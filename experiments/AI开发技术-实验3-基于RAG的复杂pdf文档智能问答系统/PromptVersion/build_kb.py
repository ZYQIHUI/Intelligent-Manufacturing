#!/usr/bin/env python
"""
build_kb.py - 基于 LlamaIndex 框架构建 PDF 知识库
解析金融研报 PDF (文本/表格/图表)，向量化后存入 Milvus Lite
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import numpy as np
from dotenv import load_dotenv

# 项目根目录（用于读取 .env 和 PDF）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# PromptVersion 目录（数据隔离）
SKILL_ROOT = Path(__file__).resolve().parent

# 加载 .env 配置
load_dotenv(PROJECT_ROOT / ".env")

# ============================================
# 日志配置
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================
# 配置
# ============================================
class Config:
    PDF_PATH = os.getenv("PDF_PATH", str(PROJECT_ROOT / "金融研报.pdf"))
    MILVUS_DB_PATH = os.getenv("MILVUS_DB_PATH", str(SKILL_ROOT / "data" / "milvus.db"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # 分块参数
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50

    # 检索参数
    TOP_K = 5

    # 数据目录（PromptVersion 自带）
    DATA_DIR = SKILL_ROOT / "data"
    IMAGES_DIR = DATA_DIR / "images"
    METADATA_FILE = DATA_DIR / "kb_metadata.json"


Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
Config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# PDF 解析器
# ============================================
class PDFParser:
    """使用 PyMuPDF 解析 PDF，提取文本/表格/图片"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        self._fitz_doc = None
        self._ocr_reader = None

    @property
    def fitz_doc(self):
        if self._fitz_doc is None:
            import fitz
            self._fitz_doc = fitz.open(str(self.pdf_path))
        return self._fitz_doc

    @property
    def ocr_reader(self):
        """延迟初始化 EasyOCR（首次加载较慢）"""
        if self._ocr_reader is None:
            try:
                import easyocr
                logger.info("正在初始化 EasyOCR（首次加载需下载模型，请耐心等待）...")
                self._ocr_reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
                logger.info("EasyOCR 初始化完成")
            except ImportError:
                logger.warning("EasyOCR 未安装，图像 OCR 将被跳过")
                self._ocr_reader = False
            except Exception as e:
                logger.warning(f"EasyOCR 初始化失败: {e}，图像 OCR 将被跳过")
                self._ocr_reader = False
        return self._ocr_reader if self._ocr_reader is not False else None

    @property
    def total_pages(self) -> int:
        return self.fitz_doc.page_count

    def close(self):
        if self._fitz_doc:
            self._fitz_doc.close()

    # ---------- 文本提取 ----------
    def extract_text(self, page_num: int) -> str:
        """使用 PyMuPDF 提取页面文本，并去除重复的页眉页脚"""
        page = self.fitz_doc[page_num]
        text = page.get_text("text")
        if not text:
            return ""

        # 去除每页重复的页眉页脚（这些会稀释向量语义）
        lines = text.strip().split("\n")
        cleaned = []
        for line in lines:
            s = line.strip()
            # 跳过页眉页脚行
            if s in ("", "敬请阅读最后一页特别声明"):
                continue
            if s.startswith("证券研究报告") or s.startswith("金融工程"):
                continue
            if s.startswith("-") and s.endswith("-") and len(s) <= 5:
                continue  # 页码如 "-6-"
            if s.startswith("图") and ("：" in s or ":" in s) and "资料来源" not in s:
                # 图表标题行保留（可能含关键词）
                pass
            cleaned.append(line)

        return "\n".join(cleaned).strip()

    # ---------- 表格提取 ----------
    def extract_tables(self, page_num: int) -> List[Dict]:
        """使用 PyMuPDF find_tables 提取表格，返回结构化数据"""
        page = self.fitz_doc[page_num]
        tabs = page.find_tables()
        structured = []
        for t_idx, table in enumerate(tabs):
            try:
                data = table.extract()
                if not data or len(data) < 2:
                    continue
                headers = [str(h).strip() if h else "" for h in data[0]]
                rows = []
                for row in data[1:]:
                    cleaned = [str(c).strip() if c else "" for c in row]
                    if any(c for c in cleaned):
                        rows.append(cleaned)
                if headers and rows:
                    structured.append({
                        "headers": headers,
                        "rows": rows,
                        "page": page_num + 1,
                        "index": t_idx,
                    })
            except Exception as e:
                logger.warning(f"表格提取失败 (page={page_num + 1}, table={t_idx}): {e}")
        return structured

    @staticmethod
    def table_to_markdown(table: Dict) -> str:
        """将结构化表格转为 Markdown 格式"""
        headers = table["headers"]
        rows = table["rows"]
        if not headers:
            return ""

        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            padded = row + [""] * (len(headers) - len(row))
            lines.append("| " + " | ".join(padded[: len(headers)]) + " |")
        return "\n".join(lines)

    # ---------- 图片提取 ----------
    def extract_images_from_page(self, page_num: int) -> List[Dict]:
        """使用 PyMuPDF 提取页面中的图片"""
        page = self.fitz_doc[page_num]
        images = []

        for img_idx, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            try:
                base_image = self.fitz_doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]

                # 跳过太小的图片（可能是图标/装饰）
                w, h = base_image.get("width", 0), base_image.get("height", 0)
                if w < 100 and h < 100:
                    continue

                # 保存图片
                img_hash = hashlib.md5(image_bytes).hexdigest()[:12]
                filename = f"p{page_num + 1}_img{img_idx}_{img_hash}.{ext}"
                img_path = Config.IMAGES_DIR / filename
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                images.append({
                    "page": page_num + 1,
                    "index": img_idx,
                    "path": str(img_path),
                    "filename": filename,
                    "width": w,
                    "height": h,
                    "bytes": image_bytes,
                })
            except Exception as e:
                logger.warning(f"提取图片失败 (page={page_num + 1}, img={img_idx}): {e}")

        return images

    def ocr_image(self, image_bytes: bytes) -> str:
        """对图片运行 OCR，提取文字"""
        reader = self.ocr_reader
        if reader is None:
            return ""

        try:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            results = reader.readtext(image_np)
            texts = [r[1] for r in results if r[2] >= 0.3]
            return " ".join(texts)
        except Exception as e:
            logger.warning(f"OCR 失败: {e}")
            return ""

    # ---------- 联合解析 ----------
    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """
        解析整个 PDF（文本用 PyMuPDF get_text 保证编码正确，图片用 OCR）
        PyMuPDF 的 get_text 已将表格内容包含在文本中，无需单独提取表格。
        Returns:
            text_docs:   [{text, metadata}, ...]  整页文本（后续会分块）
            image_docs:  [{text, metadata}, ...]  图片 OCR 描述
        """
        text_docs = []
        image_docs = []

        for page_num in range(self.total_pages):
            page_no = page_num + 1
            logger.info(f"解析第 {page_no}/{self.total_pages} 页...")

            # 1) 文本 — PyMuPDF get_text，中文编码正确，且已包含表格文字
            page_text = self.extract_text(page_num)
            if page_text:
                text_docs.append({
                    "text": page_text,
                    "metadata": {
                        "page": page_no,
                        "type": "text",
                        "source": str(self.pdf_path.name),
                    },
                })

            # 2) 图片 — OCR 识别图表中的文字
            images = self.extract_images_from_page(page_num)
            for img in images:
                ocr_text = self.ocr_image(img["bytes"])

                desc_parts = [
                    f"[图片] 位于第 {img['page']} 页",
                    f"尺寸: {img['width']}x{img['height']}",
                ]
                if ocr_text:
                    desc_parts.append(f"OCR 识别文字: {ocr_text}")
                else:
                    desc_parts.append("(该图片无可识别文字，可能为纯图表)")

                img_desc = "；".join(desc_parts)

                image_docs.append({
                    "text": img_desc,
                    "metadata": {
                        "page": img["page"],
                        "type": "image",
                        "image_path": img["path"],
                        "filename": img["filename"],
                        "ocr_text": ocr_text,
                        "width": img["width"],
                        "height": img["height"],
                        "source": str(self.pdf_path.name),
                    },
                })

        logger.info(
            f"解析完成: 文本 {len(text_docs)} 页, 图片 {len(image_docs)} 张"
        )
        return text_docs, image_docs


# ============================================
# Embedding 模型
# ============================================
class EmbeddingEngine:
    """基于 LlamaIndex HuggingFaceEmbedding 的向量化引擎"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self._model = None
        self._dim = None

    @property
    def model(self):
        if self._model is None:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            logger.info(f"加载 Embedding 模型: {self.model_name}")
            self._model = HuggingFaceEmbedding(
                model_name=self.model_name,
                max_length=512,
                trust_remote_code=True,
            )
        return self._model

    @property
    def dim(self) -> int:
        """自动检测向量维度"""
        if self._dim is None:
            test_emb = self.model.get_text_embedding("test")
            self._dim = len(test_emb)
            logger.info(f"向量维度: {self._dim}")
        return self._dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量文本转向量"""
        return [self.model.get_text_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """单条查询转向量"""
        return self.model.get_text_embedding(text)


# ============================================
# Milvus Lite 向量存储
# ============================================
class MilvusStore:
    """基于 Milvus Lite 的向量存储（文本/表格/图片分离索引）"""

    COLLECTIONS = {
        "text": "text_collection",
        "image": "image_collection",
    }

    def __init__(self, db_path: str = None, dim: int = 512):
        self.db_path = db_path or Config.MILVUS_DB_PATH
        self.dim = dim
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from pymilvus import MilvusClient
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._client = MilvusClient(str(self.db_path))
            logger.info(f"Milvus Lite 已连接: {self.db_path}")
        return self._client

    def reset_collections(self):
        """删除旧集合后重新创建"""
        for name in self.COLLECTIONS.values():
            if self.client.has_collection(name):
                self.client.drop_collection(name)
                logger.info(f"已删除旧集合: {name}")

            self.client.create_collection(
                collection_name=name,
                dimension=self.dim,
                metric_type="COSINE",
            )
            logger.info(f"已创建集合: {name} (dim={self.dim})")

    def insert(self, collection_key: str, docs: List[Dict], embeddings: List[List[float]]):
        """批量插入向量及元数据"""
        if not docs:
            logger.info(f"集合 '{collection_key}' 无数据，跳过")
            return

        collection_name = self.COLLECTIONS[collection_key]
        data = []
        for i, (doc, emb) in enumerate(zip(docs, embeddings)):
            data.append({
                "id": i,
                "vector": emb,
                "text": doc["text"],
                "page": doc["metadata"].get("page", 0),
                "type": doc["metadata"].get("type", ""),
                "metadata_json": json.dumps(doc["metadata"], ensure_ascii=False),
            })

        self.client.insert(collection_name=collection_name, data=data)
        # 加载集合到内存，否则搜索时报 released 状态错误
        self.client.load_collection(collection_name)
        logger.info(f"集合 '{collection_key}' 已插入 {len(data)} 条向量并加载到内存")

    def search(
        self, collection_key: str, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict]:
        """向量相似度搜索"""
        collection_name = self.COLLECTIONS[collection_key]
        results = self.client.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=["text", "page", "type", "metadata_json"],
        )
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

    def get_stats(self) -> Dict:
        """获取各集合的统计信息"""
        stats = {}
        for key, name in self.COLLECTIONS.items():
            if self.client.has_collection(name):
                try:
                    s = self.client.get_collection_stats(name)
                    stats[key] = s.get("row_count", 0)
                except Exception:
                    stats[key] = "?"
            else:
                stats[key] = 0
        return stats

    def has_data(self) -> bool:
        """检查是否已有数据"""
        stats = self.get_stats()
        return any(v and v != "?" and v > 0 for v in stats.values())


# ============================================
# 主流程
# ============================================
def build_knowledge_base():
    """主入口：解析 PDF -> 向量化 -> 存入 Milvus"""
    logger.info("=" * 50)
    logger.info("   PDF 知识库构建工具 (LlamaIndex + Milvus Lite)")
    logger.info("=" * 50)

    # 1. 检查 PDF
    pdf_path = Config.PDF_PATH
    if not Path(pdf_path).exists():
        logger.error(f"PDF 文件不存在: {pdf_path}")
        logger.error("请在 .env 中设置 PDF_PATH 或确保文件存在")
        sys.exit(1)

    # 2. 初始化组件
    embed_engine = EmbeddingEngine()
    store = MilvusStore(dim=embed_engine.dim)

    # 3. 解析 PDF
    parser = PDFParser(pdf_path)
    total_pages = parser.total_pages  # 在 close 前保存
    try:
        text_docs, image_docs = parser.parse()
    finally:
        parser.close()

    if not text_docs and not image_docs:
        logger.error("PDF 未提取到任何内容！请检查文件是否可读")
        sys.exit(1)

    # 4. 文本分块 — 整页文本太长，需要切成小段提升检索精度
    from llama_index.core.node_parser import SentenceSplitter
    splitter = SentenceSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )
    from llama_index.core import Document as LDocument
    chunked_text_docs = []
    for d in text_docs:
        nodes = splitter.get_nodes_from_documents([
            LDocument(text=d["text"], metadata=d["metadata"])
        ])
        for node in nodes:
            chunked_text_docs.append({
                "text": node.text,
                "metadata": {
                    **d["metadata"],
                    "chunk_size": len(node.text),
                },
            })
    logger.info(f"文本分块: {len(text_docs)} 页 -> {len(chunked_text_docs)} 段")

    # 5. 向量化 & 存储
    store.reset_collections()

    for key, docs in [("text", chunked_text_docs), ("image", image_docs)]:
        if not docs:
            continue
        texts = [d["text"] for d in docs]
        logger.info(f"向量化 {key} ({len(texts)} 条)...")
        embeddings = embed_engine.embed(texts)
        store.insert(key, docs, embeddings)

    # 6. 保存元数据
    metadata = {
        "pdf_path": str(Path(pdf_path).absolute()),
        "pdf_name": Path(pdf_path).name,
        "total_pages": total_pages,
        "text_segments": len(chunked_text_docs),
        "image_count": len(image_docs),
        "embedding_model": embed_engine.model_name,
        "vector_dim": embed_engine.dim,
        "chunk_size": Config.CHUNK_SIZE,
    }
    with open(Config.METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info("=" * 50)
    logger.info("   知识库构建完成!")
    logger.info(f"   文本块: {metadata['text_segments']}")
    logger.info(f"   图片数: {metadata['image_count']}")
    logger.info(f"   向量维度: {metadata['vector_dim']}")
    logger.info(f"   存储路径: {store.db_path}")
    logger.info("=" * 50)


if __name__ == "__main__":
    build_knowledge_base()
