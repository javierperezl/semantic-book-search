import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Configuración centralizada. Todo viene de variables de entorno para poder
    ajustar comportamiento (modelos, límites, timeouts) sin tocar código,
    y para poder correr tests/CI con valores distintos a producción.
    """

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    intent_model: str = os.getenv("INTENT_MODEL", "gpt-4.1-mini")
    generation_model: str = os.getenv("GENERATION_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    intent_provider: str = os.getenv(
        "INTENT_PROVIDER",
        "openai",
    )

    generation_provider: str = os.getenv(
        "GENERATION_PROVIDER",
        "openai",
    )

    embedding_provider: str = os.getenv(
        "EMBEDDING_PROVIDER",
        "sentence-transformers",
    )

    # Cuántas queries de búsqueda genera el LLM de intención (tope de seguridad)
    max_search_queries: int = int(os.getenv("MAX_SEARCH_QUERIES", 5))

    # Resultados por query a Open Library /search
    limit_per_query: int = int(os.getenv("LIMIT_PER_QUERY", 8))

    # De todos los candidatos deduplicados, cuántos se enriquecen con /works
    # (evita golpear la API decenas de veces por request)
    max_candidates_to_enrich: int = int(os.getenv("MAX_CANDIDATES_TO_ENRICH", 15))

    # Cuántos resultados finales entran al prompt de generación
    max_results_to_generate: int = int(os.getenv("MAX_RESULTS_TO_GENERATE", 5))

    # Cuántos resultados se devuelven en la respuesta de la API (puede ser
    # mayor a max_results_to_generate: el frontend puede querer mostrar más
    # de lo que el LLM usa para redactar la recomendación)
    max_results_to_return: int = int(os.getenv("MAX_RESULTS_TO_RETURN", 15))

    # Open Library pide identificar la app en el User-Agent
    openlibrary_user_agent: str = os.getenv(
        "OPENLIBRARY_USER_AGENT",
        "Portafolio-BookSearch/0.1 (contact: set-your-email@example.com)",
    )

    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", 10.0))


@lru_cache
def get_settings() -> Settings:
    return Settings()
