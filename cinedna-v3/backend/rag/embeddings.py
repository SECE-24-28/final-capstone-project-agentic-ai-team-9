from typing import List
from sentence_transformers import SentenceTransformer
from core.config import settings


class EmbeddingManager:
    """Singleton sentence-transformer embedding manager with caching."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        if self._model is None:
            print(f"[Embeddings] Loading {settings.EMBEDDING_MODEL}...")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("[Embeddings] Model loaded.")

    def embed(self, text: str) -> List[float]:
        self.load()
        return self._model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self.load()
        return self._model.encode(texts, normalize_embeddings=True).tolist()


embeddings = EmbeddingManager()
