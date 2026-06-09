"""
embedding_engine.py — 向量化引擎
参考: rag-implementation Phase 2 (Embedding Selection)
选用 BAAI/bge-small-zh-v1.5: 512维, 中文金融文本优化, 本地运行
"""
import logging
from typing import List

from config import Config

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """基于 BGE 模型的向量化引擎"""

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
        if self._dim is None:
            test_emb = self.model.get_text_embedding("test")
            self._dim = len(test_emb)
            logger.info(f"向量维度: {self._dim}")
        return self._dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        """批量转向量 (rag-implementation Phase 2: batch embedding)"""
        return [self.model.get_text_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """单条查询转向量"""
        return self.model.get_text_embedding(text)
