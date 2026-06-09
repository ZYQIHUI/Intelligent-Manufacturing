"""
app.py — PDF 智能问答系统前端 (Streamlit)
参考: frontend-design (community) + rag-implementation Phase 6 (LLM Integration)
设计方向: "暗金金融终端" — 深色背景 + 暖金点缀 + 编辑级排版
"""
import json
import logging
import os
import random
from pathlib import Path
from typing import List, Dict, Tuple

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # 项目根目录（读 .env）
SKILL_ROOT = Path(__file__).resolve().parent            # SkillVersion 目录（数据隔离）
load_dotenv(PROJECT_ROOT / ".env")

from config import Config
from embedding_engine import EmbeddingEngine
from vector_store import MilvusStore

# ============================================
# 设计系统 (frontend-design skill)
# 方向: "暗金金融终端" — Dark navy + warm gold
# ============================================

DESIGN_SYSTEM = """
<style>
/* ---- 字体注入 ---- */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

/* ---- CSS 变量 ---- */
:root {
    --bg-deep: #0d1117;
    --bg-card: #161b22;
    --bg-elevated: #1c2333;
    --gold: #d4a853;
    --gold-light: #f0d78c;
    --gold-dim: #8b6914;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #484f58;
    --border-subtle: #21262d;
    --accent-green: #3fb950;
    --accent-red: #f85149;
    --accent-blue: #58a6ff;
}

/* ---- 全局覆盖 ---- */
.stApp {
    background: var(--bg-deep);
}

/* ---- 主内容区 ---- */
.main .block-container {
    padding-top: 1.5rem;
}

/* ---- 标题 ---- */
h1 {
    font-family: 'Playfair Display', 'Noto Sans SC', serif !important;
    font-weight: 700 !important;
    color: var(--gold) !important;
    font-size: 2.2rem !important;
    letter-spacing: 0.02em;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0.6rem;
    margin-bottom: 0.3rem;
}

h3 {
    font-family: 'Playfair Display', 'Noto Sans SC', serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    font-size: 1.1rem !important;
}

/* ---- 副标题 ---- */
.main .block-container div[data-testid="stCaptionContainer"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--text-muted) !important;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ---- 侧边栏 ---- */
[data-testid="stSidebar"] {
    background: var(--bg-card);
    border-right: 1px solid var(--border-subtle);
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}
[data-testid="stSidebar"] h2 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
    font-size: 1.2rem;
}
[data-testid="stSidebar"] h3 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ---- 聊天消息 ---- */
[data-testid="stChatMessage"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 6px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem;
}
/* 用户消息左侧金色细线 */
[data-testid="stChatMessage"][data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-left: 3px solid var(--gold) !important;
}

/* ---- 输入框 ---- */
[data-testid="stChatInput"] textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold-dim) !important;
}

/* ---- 按钮 ---- */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.03em;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
    background: var(--bg-card) !important;
}

/* ---- Metric 组件 ---- */
[data-testid="stMetric"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px;
    padding: 0.6rem 0.8rem !important;
}
[data-testid="stMetric"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
    color: var(--gold-light) !important;
}

/* ---- Expander ---- */
[data-testid="stExpander"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px;
    background: var(--bg-card) !important;
}

/* ---- Divider ---- */
hr {
    border-color: var(--border-subtle) !important;
}

/* ---- Text Input ---- */
.stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold-dim) !important;
}
</style>
"""

# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="RAG | 金融研报问答",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(DESIGN_SYSTEM, unsafe_allow_html=True)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# ============================================
# 配置管理
# ============================================
class AppConfig:

    @staticmethod
    def get(key: str, default: str = "") -> str:
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            if get_script_run_ctx() is None:
                return os.getenv(key, default)
            return st.session_state.get(f"cfg_{key}", os.getenv(key, default))
        except Exception:
            return os.getenv(key, default)

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


# ============================================
# 组件初始化（带缓存）
# ============================================

@st.cache_resource
def get_embedding_engine():
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    model_name = AppConfig.get("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    engine = HuggingFaceEmbedding(
        model_name=model_name,
        max_length=512,
        trust_remote_code=True,
    )
    test_emb = engine.get_text_embedding("test")
    st.session_state["embed_dim"] = len(test_emb)
    return engine


def get_milvus_client():
    db_path = AppConfig.get("MILVUS_DB_PATH", str(SKILL_ROOT / "data" / "milvus.db"))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    store = MilvusStore(db_path=db_path)
    store.ensure_loaded()
    return store


def get_deepseek_llm():
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
    api_key = AppConfig.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return False, "请先设置 DeepSeek API Key"

    try:
        from openai import OpenAI

        base_url = AppConfig.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client = OpenAI(api_key=api_key, base_url=base_url)
        client.chat.completions.create(
            model=AppConfig.get("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )
        return True, f"DeepSeek API 已连接"
    except Exception as e:
        return False, f"API 连接失败: {str(e)[:100]}"


def check_db_connection() -> Tuple[bool, str, Dict]:
    try:
        store = get_milvus_client()
        stats = store.get_stats()
        total = sum(v for v in stats.values() if v > 0)
        if total > 0:
            return True, f"数据库已就绪", stats
        else:
            return False, "数据库为空，请先运行 build_kb.py 构建知识库", stats
    except Exception as e:
        return False, f"数据库连接失败: {str(e)[:100]}", {}


# ============================================
# RAG 检索与问答 (rag-implementation Phase 5 + 6)
# ============================================

def search_all_collections(store: MilvusStore, embed_engine, query: str, top_k: int = 8) -> List[Dict]:
    """跨集合均衡检索：文本为主(8条)，图片为辅(4条)，文本在前"""
    query_emb = embed_engine.get_text_embedding(query)

    text_results = store.search("text", query_emb, top_k=top_k)
    image_results = store.search("image", query_emb, top_k=max(2, top_k // 2))

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

    return merged


def build_prompt(query: str, context_items: List[Dict]) -> str:
    """构建结构化 Prompt (rag-implementation Phase 6: Prompt Template)"""
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
    if not context_items:
        return (
            "未检索到相关内容。可能原因：\n"
            "1. 知识库未构建或为空，请先运行 build_kb.py\n"
            "2. 问题与文档内容无关\n"
            "3. 请尝试换一种问法"
        ), False

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
    with st.sidebar:
        st.header("◆ 系统设置")

        # ---- API 设置 ----
        st.subheader("API 配置")
        api_key = st.text_input(
            "DeepSeek API Key",
            value=AppConfig.get("DEEPSEEK_API_KEY", ""),
            type="password",
            placeholder="sk-...",
        )
        base_url = st.text_input(
            "Base URL",
            value=AppConfig.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        model = st.selectbox(
            "模型",
            ["deepseek-chat", "deepseek-reasoner"],
            index=0 if AppConfig.get("DEEPSEEK_MODEL") == "deepseek-chat" else 1,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("更新 API", use_container_width=True):
                AppConfig.set("DEEPSEEK_API_KEY", api_key)
                AppConfig.set("DEEPSEEK_BASE_URL", base_url)
                AppConfig.set("DEEPSEEK_MODEL", model)
                st.cache_resource.clear()
                st.rerun()
        with col2:
            if st.button("恢复默认", use_container_width=True):
                for k in ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"]:
                    st.session_state.pop(f"cfg_{k}", None)
                st.cache_resource.clear()
                st.rerun()

        st.divider()

        # ---- PDF 上传 ----
        st.subheader("文档管理")
        uploaded_file = st.file_uploader("上传 PDF", type=["pdf"])
        if uploaded_file is not None:
            pdf_path = SKILL_ROOT / "data" / uploaded_file.name
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            AppConfig.set("PDF_PATH", str(pdf_path))
            st.success(f"已上传: {uploaded_file.name}")
            st.info("请在终端运行 `python SkillVersion/build_kb.py` 重新构建知识库")

        st.divider()

        # ---- 数据库状态 ----
        st.subheader("向量库状态")
        db_ok, db_msg, db_stats = check_db_connection()

        if db_ok:
            st.success(db_msg)
        else:
            st.error(db_msg)

        if db_stats:
            cols = st.columns(2)
            cols[0].metric("文本块", db_stats.get("text", 0))
            cols[1].metric("图片", db_stats.get("image", 0))

        st.divider()

        # ---- 技能信息 ----
        st.subheader("已加载技能")
        st.caption("pdf-parser（自定义）")
        st.caption("rag-implementation（社区）")
        st.caption("frontend-design（社区）")

        st.divider()

        # ---- 系统信息 ----
        st.subheader("系统信息")
        st.caption(f"Embedding: {AppConfig.get('EMBEDDING_MODEL')}")
        st.caption(f"PDF: {Path(AppConfig.get('PDF_PATH')).name}")

        meta_path = SKILL_ROOT / "data" / "kb_metadata.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            st.caption(f"总页数: {meta.get('total_pages', '?')}")
            st.caption(f"向量维度: {meta.get('vector_dim', '?')}")


def render_chat():
    st.title("金融研报 · 智能问答")
    st.caption("RAG System — LlamaIndex + Milvus + DeepSeek")

    # ---- 连接状态栏 ----
    api_ok, api_msg = check_api_connection()
    db_ok, db_msg, _ = check_db_connection()

    col_api, col_db = st.columns(2)
    with col_api:
        if api_ok:
            st.success(f"◆ {api_msg}")
        else:
            st.error(f"◆ {api_msg}")
    with col_db:
        if db_ok:
            st.success(f"◆ {db_msg}")
        else:
            st.warning(f"◆ {db_msg}")

    st.divider()

    # ---- 初始化聊天历史 ----
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "欢迎使用金融研报智能问答系统。\n\n"
                    "本系统基于 RAG 架构，可回答文档中的以下内容：\n"
                    "◆ 市场指数与估值分析\n"
                    "◆ 行业数据与表格查询\n"
                    "◆ 图表信息解读\n\n"
                    "请在下方输入您的问题。"
                ),
            }
        ]

    # ---- 显示聊天历史 ----
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("◆ 参考来源"):
                    for src in msg["sources"]:
                        st.caption(
                            f"[{src['type']}] 第 {src['page']} 页 · 相似度 {src['score']:.3f}"
                        )
                        st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))

    # ---- 输入框 ----
    if prompt := st.chat_input("输入问题...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not api_ok:
            bot_msg = f"◆ {api_msg}\n\n请在左侧边栏设置有效的 API Key 后再提问。"
            sources = []
        elif not db_ok:
            bot_msg = f"◆ {db_msg}\n\n请先在终端运行 `python SkillVersion/build_kb.py` 构建知识库。"
            sources = []
        else:
            with st.spinner("检索相关文档内容..."):
                try:
                    store = get_milvus_client()
                    embed_engine = get_embedding_engine()
                    context_items = search_all_collections(store, embed_engine, prompt)
                except Exception as e:
                    context_items = []
                    st.error(f"检索失败: {e}")

            if context_items:
                with st.spinner("分析并生成回答..."):
                    answer, ok = generate_answer(prompt, context_items)
                bot_msg = answer
                sources = context_items[:5] if ok else []
            else:
                bot_msg = (
                    "◆ 未检索到相关内容\n\n"
                    "可能的原因：\n"
                    "1. 知识库尚未构建 — 请运行 `python SkillVersion/build_kb.py`\n"
                    "2. 该问题与文档内容无关 — 请尝试询问文档相关的问题\n"
                    "3. Embedding 模型未正确加载 — 请检查控制台日志"
                )
                sources = []

        msg_entry = {"role": "assistant", "content": bot_msg}
        if sources:
            msg_entry["sources"] = [
                {"type": s["type"], "page": s["page"], "score": s["score"], "text": s["text"]}
                for s in sources
            ]
        st.session_state.messages.append(msg_entry)

        with st.chat_message("assistant"):
            st.markdown(bot_msg)
            if sources:
                with st.expander("◆ 参考来源"):
                    for src in sources:
                        st.caption(
                            f"[{src['type']}] 第 {src['page']} 页 · 相似度 {src['score']:.3f}"
                        )
                        st.text(src["text"][:300] + ("..." if len(src["text"]) > 300 else ""))

    # ---- 底部操作 ----
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("刷新状态", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    with col3:
        if st.button("使用帮助", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "**使用帮助**\n\n"
                    "**首次使用：**\n"
                    "◆ 在侧边栏设置 DeepSeek API Key\n"
                    "◆ 确保 PDF 文件存在于项目目录\n"
                    "◆ 运行 `python SkillVersion/build_kb.py` 构建知识库\n"
                    "◆ 刷新页面后即可提问\n\n"
                    "**提问技巧：**\n"
                    "◆ 问题尽量具体，涉及数据的提问效果更好\n"
                    "◆ 可以询问表格数据、图表信息、文本分析\n"
                    "◆ 如果答案不理想，换一种问法试试"
                ),
            })
            st.rerun()


# ============================================
# 主入口
# ============================================
def main():
    AppConfig.init_defaults()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        import sys
        sys.exit(1)
