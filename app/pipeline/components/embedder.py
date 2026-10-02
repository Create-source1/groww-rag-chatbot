"""Embedding generation using sentence-transformers."""
import numpy as np
from app.config import settings


class Embedder:
    """Generates embeddings using a sentence-transformers model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None

    def _load_model(self):
        """Lazy-load the embedding model from Hugging Face."""
        if self._model is None:
            import os
            if settings.hf_token:
                os.environ["HF_TOKEN"] = settings.hf_token
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Encode a list of texts into embedding vectors."""
        model = self._load_model()
        return model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True
        )

    def encode_query(self, query: str) -> list[float]:
        """Encode a single query string."""
        embedding = self.encode([query])
        return embedding[0].tolist()
