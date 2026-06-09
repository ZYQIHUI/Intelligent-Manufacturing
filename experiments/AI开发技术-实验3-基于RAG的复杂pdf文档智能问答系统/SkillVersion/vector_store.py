"""
vector_store.py — Milvus Lite 向量存储
参考: rag-implementation Phase 3 (Vector Database Setup)
双集合设计: text_collection (67段) + image_collection (59张)
COSINE 相似度, FLAT 索引 (小规模暴力搜索精度最高)
"""
import json
import logging
from pathlib import Path
from typing import List, Dict

from config import Config

logger = logging.getLogger(__name__)


class MilvusStore:
    """Milvus Lite 向量存储，管理 text_collection 和 image_collection"""

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
        """删除旧集合并重建 (rag-implementation Phase 3: Schema Design)"""
        for name in [Config.TEXT_COLLECTION, Config.IMAGE_COLLECTION]:
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
        """批量插入向量并加载到内存"""
        if not docs:
            logger.info(f"集合 '{collection_key}' 无数据，跳过")
            return

        collection_name = Config.TEXT_COLLECTION if collection_key == "text" else Config.IMAGE_COLLECTION
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
        self.client.load_collection(collection_name)
        logger.info(f"集合 '{collection_key}' 已插入 {len(data)} 条向量并加载到内存")

    def search(self, collection_key: str, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """向量相似度搜索 (rag-implementation Phase 5: Vector Search)"""
        collection_name = Config.TEXT_COLLECTION if collection_key == "text" else Config.IMAGE_COLLECTION

        try:
            results = self.client.search(
                collection_name=collection_name,
                data=[query_embedding],
                limit=top_k,
                output_fields=["text", "page", "type", "metadata_json"],
            )
        except Exception as e:
            logger.warning(f"搜索失败 ({collection_name}): {e}")
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

    def get_stats(self) -> Dict:
        """获取各集合统计信息"""
        stats = {}
        for key, name in [("text", Config.TEXT_COLLECTION), ("image", Config.IMAGE_COLLECTION)]:
            if self.client.has_collection(name):
                try:
                    s = self.client.get_collection_stats(name)
                    stats[key] = s.get("row_count", 0)
                except Exception:
                    stats[key] = -1
            else:
                stats[key] = 0
        return stats

    def has_data(self) -> bool:
        stats = self.get_stats()
        return any(v and v > 0 for v in stats.values())

    def ensure_loaded(self):
        """确保所有集合已加载到内存 (Milvus Lite 连接后必须 load)"""
        for name in [Config.TEXT_COLLECTION, Config.IMAGE_COLLECTION]:
            if self.client.has_collection(name):
                try:
                    self.client.load_collection(name)
                except Exception:
                    pass
