from app.config import get_settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.sentence_transformer_provider import (
    SentenceTransformerProvider,
)

_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:

    global _provider

    if _provider is not None:
        return _provider

    settings = get_settings()

    match settings.embedding_provider:

        case "sentence-transformers":
            _provider = SentenceTransformerProvider()

        case _:
            raise ValueError(
                f"Embedding provider '{settings.embedding_provider}' no soportado."
            )

    return _provider