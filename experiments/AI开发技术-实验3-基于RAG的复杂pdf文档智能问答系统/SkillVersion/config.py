"""
config.py — 共享配置
参考: rag-implementation Phase 1 (Requirements Analysis) + 自定义 pdf-parser skill
"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # 项目根目录（用于读 .env）
SKILL_ROOT = Path(__file__).resolve().parent            # SkillVersion 目录（数据隔离）
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    # ---- 路径 ----
    PDF_PATH = os.getenv("PDF_PATH", str(PROJECT_ROOT / "金融研报.pdf"))
    DATA_DIR = SKILL_ROOT / "data"
    IMAGES_DIR = DATA_DIR / "images"
    MILVUS_DB_PATH = os.getenv("MILVUS_DB_PATH", str(DATA_DIR / "milvus.db"))
    METADATA_FILE = DATA_DIR / "kb_metadata.json"

    # ---- DeepSeek API (rag-implementation Phase 6: LLM Integration) ----
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # ---- Embedding (rag-implementation Phase 2: Embedding Selection) ----
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

    # ---- 分块 (rag-implementation Phase 4: Chunking Strategy) ----
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50

    # ---- 检索 (rag-implementation Phase 5: Retrieval Implementation) ----
    TOP_K = 8  # 文本检索条数
    IMAGE_TOP_K = 4  # 图片检索条数（top_k // 2）

    # ---- Milvus 集合名 (rag-implementation Phase 3: Vector DB Setup) ----
    TEXT_COLLECTION = "text_collection"
    IMAGE_COLLECTION = "image_collection"

    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
