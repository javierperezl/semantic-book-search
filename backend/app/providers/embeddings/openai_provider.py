import numpy as np
from openai import OpenAI

from app.config import get_settings
from app.providers.embeddings.base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Usa la API de embeddings de OpenAI (text-embedding-3-small / -large,
    elegido vía EMBEDDING_MODEL). A diferencia de SentenceTransformerProvider,
    esto hace una llamada de red por encode(), así que cuenta como costo/latencia
    real en los experimentos, no solo cómputo local.
    """

    def __init__(self):
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.embedding_model

    def encode(
        self,
        texts: str | list[str],
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        is_single = isinstance(texts, str)
        input_texts = [texts] if is_single else texts

        response = self._client.embeddings.create(
            model=self._model,
            input=input_texts,
        )

        vectors = np.array([item.embedding for item in response.data])

        if normalize_embeddings:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vectors = vectors / norms

        return vectors[0] if is_single else vectors
