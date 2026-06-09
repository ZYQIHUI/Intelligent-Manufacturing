#!/usr/bin/env python
"""
app.py - PDF 智能问答系统前端 (Streamlit)
基于 LlamaIndex + Milvus Lite + DeepSeek 的 RAG 问答界面
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

# 项目根目录（用于读取 .env 和 PDF）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# PromptVersion 目录（数据隔离）
SKILL_ROOT = Path(__file__).resolve().parent

# 加载 .env 配置
load_dotenv(PROJECT_ROOT / ".env")

# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="PDF 智能问答系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# 日志配置
# ============================================
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# ============================================
# 配置管理
# ============================================
class AppConfig:
    """运行时配置（支持动态更新）"""

    @staticmethod
    def get(key: str, default: str = "") -> str:
        # 优先从 session_state 读取，其次从 os.environ
        return st.session_state.get(f"cfg_{key}", os.getenv(key, default))

    @staticmethod
    def set(key: str, value: str):
        st.session_state[f"cfg_{key}"] = value
        os.environ[key] = value

    @staticmethod
    def init_defaults():
        defaults = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
            "DEEPSEEK_BASE_URL": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            "DEEPSEEK_MODEL": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"),
            "PDF_PATH": os.getenv("PDF_PATH", str(PROJECT_ROOT / "金融研报.pdf")),
            "MILVUS_DB_PATH": os.getenv("MILVUS_DB_PATH", str(SKILL_ROOT / "data" / "milvus.db")),
        }
        for k, v in defaults.items():
            if f"cfg_{k}" not in st.session_state:
                st.session_state[f"cfg_{k}"] = v


AppConfig.init_defaults()

# ============================================
# 组件初始化（带缓存）
# ============================================

@st.cache_resource
def get_embedding_engine():
    """加载 Embedding 模型（缓存，只加载一次）"""
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    model_name = AppConfig.get("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    logger.info(f"加载 Embedding 模型: {model_name}")
    engine = HuggingFaceEmbedding(
        model_name=model_name,
        max_length=512,
        trust_remote_code=True,
    )
    # 缓存维度
    test_emb = engine.get_text_embedding("test")
    st.session_state["embed_dim"] = len(test_emb)
    return engine


def get_milvus_client():
    """获取 Milvus Lite 客户端（自动加载集合到内存）"""
    from pymilvus import MilvusClient

    db_path = AppConfig.get("MILVUS_DB_PATH", "./data/milvus.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    client = MilvusClient(str(db_path))

    # 确保集合已加载到内存（Milvus Lite 重启后需要重新 load）
    for col in ["text_collection", "image_collection"]:
        if client.has_collection(col):
            try:
                client.load_collection(col)
            except Exception:
                pass  # 可能已经加载

    return client


def get_deepseek_llm():
    """获取 DeepSeek LLM（LlamaIndex OpenAILike）"""
    from llama_index.llms.openai_like import OpenAILike

    api_key = AppConfig.get("DEEPSEEK_API_KEY", "")
    base_url = AppConfig.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = AppConfig.get("DEEPSEEK_MODEL", "deepseek-chat")

    if not api_key:
        return None

    return OpenAILike(
        model=model,
        api_base=base_url,
        api_key=api_key,
        is_chat_model=True,
        max_tokens=2048,
        temperature=0.3,
    )


# ============================================
# 连接检查
# ============================================

def check_api_connection() -> Tuple[bool, str]:
    """检查 DeepSeek API 是否可用"""
    api_key = AppConfig.get("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "your_deepseek_api_key_here":
        return False, "请先设置 DeepSeek API Key"

    try:
        from openai import OpenAI

        base_url = AppConfig.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client = OpenAI(api_key=api_key, base_url=base_url)
        # 简单测试调用
        resp = client.chat.completions.create(
            model=AppConfig.get("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )
        return True, f"DeepSeek API 已连接 (模型: {AppConfig.get('DEEPSEEK_MODEL', 'deepseek-chat')})"
    except Exception as e:
        return False, f"API 连接失败: {str(e)[:100]}"


def check_db_connection() -> Tuple[bool, str, Dict]:
    """检查 Milvus 数据库是否就绪"""
    try:
        client = get_milvus_client()
        stats = {}

        for key, col_name in [
            ("text", "text_collection"),
            ("image", "image_collection"),
        ]:
            if client.has_collection(col_name):
                try:
                    s = client.get_collection_stats(col_name)
                    stats[key] = s.get("row_count", 0)
                except Exception:
                    stats[key] = -1
            else:
                stats[key] = 0

        total = sum(v for v in stats.values() if v > 0)
        if total > 0:
            return True, f"数据库已就绪 ({total} 条向量)", stats
        else:
            return False, "数据库为空，请先运行 build_kb.py 构建知识库", stats
    except Exception as e:
        return False, f"数据库连接失败: {str(e)[:100]}", {}


# ============================================
# RAG 检索与问答
# ============================================

def search_all_collections(
    client, embed_engine, query: str, top_k: int = 8
) -> List[Dict]:
    """跨集合检索：文本为主，图片为辅（图片向量易偏高分，需控制比例）"""
    query_emb = embed_engine.get_text_embedding(query)

    def search_col(col_name: str, limit: int) -> List[Dict]:
        if not client.has_collection(col_name):
            return []
        try:
            results = client.search(
                collection_name=col_name,
                data=[query_emb],
                limit=limit,
                output_fields=["text", "page", "type", "metadata_json"],
            )
        except Exception:
            return []
        if not results or not results[0]:
            return []
        hits = []
        for r in results[0]:
            entity = r.get("entity", {})
            hits.append({
                "score": r.get("distance", 0),
                "text": entity.get("text", ""),
                "page": entity.get("page", 0),
                "type": entity.get("type", ""),
                "metadata": json.loads(entity.get("metadata_json", "{}")),
            })
        return hits

    # 文本为主，图片为辅（图片 OCR 向量易偏高分）
    text_results = search_col("text_collection", limit=top_k)
    image_results = search_col("image_collection", limit=max(2, top_k // 2))

    # 合并：文本全部保留，图片去重后追加
    seen = set()
    merged = []
    for r in text_results:
        key = r["text"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(r)

    for r in image_results:
        key = r["text"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(r)

    # 文本在前，图片在后（不按分数排序，确保文本优先给 LLM）
    return merged


def build_prompt(query: str, context_items: List[Dict]) -> str:
    """构建带上下文的 Prompt"""
    context_parts = []
    for i, item in enumerate(context_items):
        src_type = {"text": "文本", "table": "表格", "image": "图片"}.get(
            item["type"], item["type"]
        )
        context_parts.append(
            f"[来源 {i + 1}] 类型: {src_type} | 页码: {item['page']}\n"
            f"{item['text']}"
        )

    context_str = "\n\n---\n\n".join(context_parts)

    return f"""你是一个专业的金融研报分析助手。请根据以下从 PDF 文档中检索到的信息，准确回答用户的问题。

## 规则
- 如果检索信息足以回答问题，请给出准确、详细的答案。
- 如果涉及数据，必须给出具体数值。
- 如果检索信息不足以回答问题，请明确说明"根据现有文档内容无法回答该问题"，并简要说明原因。
- 用中文回答，保持专业。

## 检索信息
{context_str}

## 用户问题
{query}

## 回答"""


def generate_answer(query: str, context_items: List[Dict]) -> Tuple[str, bool]:
    """调用 LLM 生成回答"""
    if not context_items:
        return "未检索到相关内容。可能原因：\n1. 知识库未构建或为空，请先运行 build_kb.py\n2. 问题与文档内容无关\n3. 请尝试换一种问法", False

    llm = get_deepseek_llm()
    if llm is None:
        return "DeepSeek API 未配置，请在侧边栏设置 API Key", False

    prompt = build_prompt(query, context_items)

    try:
        resp = llm.complete(prompt)
        answer = resp.text.strip() if hasattr(resp, "text") else str(resp).strip()
        return answer, True
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return f"API Key 无效或已过期，请在侧边栏更新: {error_msg[:150]}", False
        elif "rate" in error_msg.lower():
            return f"API 调用频率超限，请稍后重试: {error_msg[:150]}", False
        else:
            return f"调用 LLM 失败: {error_msg[:200]}", False


# ============================================
# UI 组件
# ============================================

def render_sidebar():
    """渲染侧边栏：设置、上传、状态"""
    with st.sidebar:
        st.header("⚙️ 系统设置")

        # ---- API 设置 ----
        st.subheader("🔑 DeepSeek API")
        api_key = st.text_input(
            "API Key",
            value=AppConfig.get("DEEPSEEK_API_KEY", ""),
            type="password",
            placeholder="sk-...",
            help="输入 DeepSeek API Key",
        )
        base_url = st.text_input(
            "Base URL",
            value=AppConfig.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            help="API 地址",
        )
        model = st.selectbox(
            "模型",
            ["deepseek-chat", "deepseek-reasoner"],
            index=0 if AppConfig.get("DEEPSEEK_MODEL") == "deepseek-chat" else 1,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 更新 API", use_container_width=True):
                AppConfig.set("DEEPSEEK_API_KEY", api_key)
                AppConfig.set("DEEPSEEK_BASE_URL", base_url)
                AppConfig.set("DEEPSEEK_MODEL", model)
                # 清除 LLM 缓存
                st.cache_resource.clear()
                get_deepseek_llm.clear()
                st.success("API 配置已更新")
                st.rerun()
        with col2:
            if st.button("🔁 恢复默认", use_container_width=True):
                for k in ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"]:
                    st.session_state.pop(f"cfg_{k}", None)
                st.cache_resource.clear()
                get_deepseek_llm.clear()
                st.success("已恢复默认配置")
                st.rerun()

        st.divider()

        # ---- PDF 上传 ----
        st.subheader("📄 PDF 文档")
        uploaded_file = st.file_uploader(
            "上传 PDF",
            type=["pdf"],
            help="上传新的 PDF 文档（需要重新构建知识库）",
        )
        if uploaded_file is not None:
            pdf_path = SKILL_ROOT / "data" / uploaded_file.name
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            AppConfig.set("PDF_PATH", str(pdf_path))
            st.success(f"已上传: {uploaded_file.name}")
            st.info("请在终端运行 `python build_kb.py` 重新构建知识库")

        st.divider()

        # ---- 数据库状态 ----
        st.subheader("📦 数据库状态")
        db_ok, db_msg, db_stats = check_db_connection()

        if db_ok:
            st.success(db_msg)
        else:
            st.error(db_msg)

        if db_stats:
            cols = st.columns(2)
            cols[0].metric("文本", db_stats.get("text", 0))
            cols[1].metric("图片", db_stats.get("image", 0))

        st.divider()

        # ---- 系统信息 ----
        st.subheader("ℹ️ 系统信息")
        st.caption(f"Embedding: {AppConfig.get('EMBEDDING_MODEL')}")
        st.caption(f"PDF: {Path(AppConfig.get('PDF_PATH')).name}")

        # 检查 metadata
        meta_path = SKILL_ROOT / "data" / "kb_metadata.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            st.caption(f"总页数: {meta.get('total_pages', '?')}")
            st.caption(f"向量维度: {meta.get('vector_dim', '?')}")


def render_chat():
    """渲染主聊天区域"""
    st.title("📊 PDF 智能问答系统")
    st.caption("基于 RAG 的金融研报问答 — LlamaIndex + Milvus + DeepSeek")

    # ---- 连接状态栏 ----
    api_ok, api_msg = check_api_connection()
    db_ok, db_msg, _ = check_db_connection()

    col_api, col_db = st.columns(2)
    with col_api:
        if api_ok:
            st.success(f"✅ {api_msg}")
        else:
            st.error(f"❌ {api_msg}")
    with col_db:
        if db_ok:
            st.success(f"✅ {db_msg}")
        else:
            st.warning(f"⚠️ {db_msg}")

    st.divider()

    # ---- 初始化聊天历史 ----
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "你好！我是金融研报智能问答助手。\n\n"
                    "我可以回答关于已上传 PDF 文档的各种问题，包括：\n"
                    "- 📈 市场指数与估值分析\n"
                    "- 📊 表格数据查询\n"
                    "- 📉 图表信息解读\n\n"
                    "请在下方向我提问吧！"
                ),
            }
        ]

    # ---- 显示聊天历史 ----
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # 如果有来源信息，显示
            if "sources" in msg and msg["sources"]:
                with st.expander("📎 参考来源"):
                    for src in msg["sources"]:
                        st.caption(
                            f"[{src['type']}] 第 {src['page']} 页 (相似度: {src['score']:.3f})"
                        )
                        st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))

    # ---- 输入框 ----
    if prompt := st.chat_input("请输入您的问题...", key="chat_input"):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成回答
        if not api_ok:
            bot_msg = f"⚠️ {api_msg}\n\n请在左侧边栏设置有效的 API Key 后再提问。"
            sources = []
        elif not db_ok:
            bot_msg = f"⚠️ {db_msg}\n\n请先在终端运行 `python build_kb.py` 构建知识库。"
            sources = []
        else:
            with st.spinner("🔍 正在检索相关文档内容..."):
                try:
                    client = get_milvus_client()
                    embed_engine = get_embedding_engine()
                    context_items = search_all_collections(client, embed_engine, prompt)
                except Exception as e:
                    context_items = []
                    st.error(f"检索失败: {e}")

            if context_items:
                with st.spinner("🤔 正在分析并生成回答..."):
                    answer, ok = generate_answer(prompt, context_items)
                bot_msg = answer
                sources = context_items[:5] if ok else []
            else:
                bot_msg = (
                    "❌ **未检索到相关内容**\n\n"
                    "可能的原因：\n"
                    "1. 知识库尚未构建——请运行 `python build_kb.py`\n"
                    "2. 该问题与文档内容无关——请尝试询问文档相关的问题\n"
                    "3. Embedding 模型未正确加载——请检查控制台日志"
                )
                sources = []

        # 添加助手消息
        msg_entry = {"role": "assistant", "content": bot_msg}
        if sources:
            msg_entry["sources"] = [
                {
                    "type": s["type"],
                    "page": s["page"],
                    "score": s["score"],
                    "text": s["text"],
                }
                for s in sources
            ]
        st.session_state.messages.append(msg_entry)

        with st.chat_message("assistant"):
            st.markdown(bot_msg)
            if sources:
                with st.expander("📎 参考来源"):
                    for src in sources:
                        st.caption(
                            f"[{src['type']}] 第 {src['page']} 页 (相似度: {src['score']:.3f})"
                        )
                        st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))

    # ---- 底部操作 ----
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🔄 刷新状态", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    with col3:
        if st.button("ℹ️ 使用帮助", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "**使用帮助**\n\n"
                    "**1. 首次使用：**\n"
                    "- 在侧边栏设置 DeepSeek API Key\n"
                    "- 确保 PDF 文件存在于项目目录\n"
                    "- 运行 `python build_kb.py` 构建知识库\n"
                    "- 刷新页面后即可提问\n\n"
                    "**2. 更新 PDF：**\n"
                    "- 在侧边栏上传新 PDF\n"
                    "- 重新运行 `python build_kb.py`\n\n"
                    "**3. 提问技巧：**\n"
                    "- 问题尽量具体，涉及数据的提问效果更好\n"
                    "- 可以询问表格数据、图表信息、文本分析\n"
                    "- 如果答案不理想，换一种问法试试"
                ),
            })
            st.rerun()


# ============================================
# 主入口
# ============================================
def main():
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
