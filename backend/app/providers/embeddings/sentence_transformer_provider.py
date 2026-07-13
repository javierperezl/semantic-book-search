import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.providers.embeddings.base import EmbeddingProvider


class SentenceTransformerProvider(EmbeddingProvider):

    def __init__(self):

        settings = get_settings()

        self._model = SentenceTransformer(
            settings.embedding_model,
        )

    def encode(
        self,
        texts: str | list[str],
        normalize_embeddings: bool = True,
    ) -> np.ndarray:

        return np.array(

            self._model.encode(
                texts,
                normalize_embeddings=normalize_embeddings,
            )

        )