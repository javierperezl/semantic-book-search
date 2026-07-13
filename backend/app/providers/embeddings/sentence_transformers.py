import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.providers.embeddings.base import EmbeddingProvider


class SentenceTransformerProvider(EmbeddingProvider):

    def __init__(self):
        settings = get_settings()

        self.model = SentenceTransformer(
            settings.embedding_model
        )

    def encode(
        self,
        texts,
        normalize: bool = True,
    ) -> np.ndarray:

        return self.model.encode(
            texts,
            normalize_embeddings=normalize,
        )