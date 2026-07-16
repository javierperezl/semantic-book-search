# Experimento 1 del plan del equipo. Las primeras 3 configs NO requieren
# código nuevo (sentence-transformers ya carga cualquier modelo de
# HuggingFace por nombre) — solo cambian EMBEDDING_MODEL. Las últimas 2 usan
# el OpenAIEmbeddingProvider agregado en app/providers/embeddings/openai_provider.py.
EMBEDDING_CONFIGS = [
    {
        "name": "minilm",
        "EMBEDDING_PROVIDER": "sentence-transformers",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    },
    {
        "name": "bge-small",
        "EMBEDDING_PROVIDER": "sentence-transformers",
        "EMBEDDING_MODEL": "BAAI/bge-small-en-v1.5",
    },
    {
        "name": "bge-base",
        "EMBEDDING_PROVIDER": "sentence-transformers",
        "EMBEDDING_MODEL": "BAAI/bge-base-en-v1.5",
    },
    {
        "name": "openai-3-small",
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_MODEL": "text-embedding-3-small",
    },
    {
        "name": "openai-3-large",
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_MODEL": "text-embedding-3-large",
    },
]
