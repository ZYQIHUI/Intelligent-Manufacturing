"""
build_kb.py — 知识库构建器 (编排脚本)
参考: rag-implementation Phase 4 (Chunking) + Phase 5 (Retrieval)
流程: PDF解析 → 文本分块 → 向量化 → Milvus存储
"""
import json
import logging
import sys
from pathlib import Path

from config import Config
from pdf_parser import PDFParser
from embedding_engine import EmbeddingEngine
from vector_store import MilvusStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_knowledge_base():
    logger.info("=" * 50)
    logger.info("   PDF 知识库构建工具 (SkillVersion)")
    logger.info("   社区 Skill: rag-implementation + frontend-design")
    logger.info("=" * 50)

    Config.ensure_dirs()

    # 1. 检查 PDF
    pdf_path = Config.PDF_PATH
    if not Path(pdf_path).exists():
        logger.error(f"PDF 文件不存在: {pdf_path}")
        sys.exit(1)

    # 2. 初始化组件
    embed_engine = EmbeddingEngine()
    store = MilvusStore(dim=embed_engine.dim)

    # 3. 解析 PDF (pdf-parser skill)
    parser = PDFParser(pdf_path)
    total_pages = parser.total_pages
    try:
        text_docs, image_docs = parser.parse()
    finally:
        parser.close()

    if not text_docs and not image_docs:
        logger.error("PDF 未提取到任何内容！")
        sys.exit(1)

    # 4. 文本分块 (rag-implementation Phase 4: Chunking Strategy)
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core import Document as LDocument

    splitter = SentenceSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )
    chunked_text_docs = []
    for d in text_docs:
        nodes = splitter.get_nodes_from_documents([
            LDocument(text=d["text"], metadata=d["metadata"])
        ])
        for node in nodes:
            chunked_text_docs.append({
                "text": node.text,
                "metadata": {**d["metadata"], "chunk_size": len(node.text)},
            })

    logger.info(f"文本分块: {len(text_docs)} 页 → {len(chunked_text_docs)} 段")

    # 5. 向量化 & 存储 (rag-implementation Phase 5: Retrieval Implementation)
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
        "skill_version": "SkillVersion",
        "skills_used": ["pdf-parser (custom)", "rag-implementation (community)", "frontend-design (community)"],
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
