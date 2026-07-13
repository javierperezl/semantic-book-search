import asyncio

from app.config import get_settings
from app.models import Intent
from app.openlibrary import (
    OpenLibraryError,
    enrich_with_works,
    multi_search,
    search_first_book,
)
from app.reranker import rerank
from app.semantic_profile import build_book_profile, build_query_profile, clean_subjects


async def get_reference_book(intent: Intent) -> dict | None:
    """
    Recupera el primer libro de referencia mencionado por el usuario,
    con sus datos REALES de Open Library (no lo que el LLM asume que es).
    Devuelve None si no hay referencia o no se encuentra.
    """
    if not intent.reference_books:
        return None

    try:
        return await search_first_book(intent.reference_books[0])
    except OpenLibraryError:
        return None


def _exclude_reference_book(candidates: list[dict], reference_book: dict | None) -> list[dict]:
    """
    El usuario ya conoce el libro de referencia (lo usó como ejemplo) —
    recomendárselo de vuelta no aporta nada, y como el query_profile se
    construye a partir de sus propios metadatos, el reranker lo puntúa
    artificialmente alto (matchea consigo mismo). Se filtra antes de rerankear.
    """
    if not reference_book or not reference_book.get("key"):
        return candidates

    ref_key = reference_book["key"]
    return [c for c in candidates if c.get("key") != ref_key]


async def retrieve_candidates(intent: Intent, reference_book: dict | None) -> list[dict]:
    settings = get_settings()

    queries = intent.search_queries[: settings.max_search_queries]

    try:
        candidates = await multi_search(queries, limit_per_query=settings.limit_per_query)
    except OpenLibraryError:
        return []

    return _exclude_reference_book(candidates, reference_book)


async def build_search_context(intent: Intent) -> tuple[str, list[dict]]:
    """
    Devuelve (query_profile, candidatos_finales_con_profile_completo).

    Estrategia en dos etapas para no desperdiciar llamadas a /works en
    candidatos irrelevantes, ni perjudicar a candidatos relevantes que
    Open Library devolvió tarde en el orden de resultados:

      1) Rerank "barato" con lo que ya trae /search (título, autor,
         subjects crudos, sin descripción) sobre TODOS los candidatos.
      2) Se enriquecen con /works solo los mejores N de ese pase barato.
      3) Rerank final con el profile completo (descripción + subjects
         combinados y deduplicados) sobre esos N.

    Esto evita que un candidato genuinamente relevante quede sin
    enriquecer solo por el orden en que Open Library lo devolvió, y evita
    gastar llamadas a /works en candidatos que el pase barato ya descarta.
    """
    settings = get_settings()

    reference_book = await get_reference_book(intent)
    query_profile = build_query_profile(reference_book, intent.semantic_description)

    candidates = await retrieve_candidates(intent, reference_book)

    if not candidates:
        return query_profile, []

    for candidate in candidates:
        candidate["profile"] = build_book_profile(candidate)

    # Etapa 1: rerank barato (sin cachear, el profile es parcial)
    preselected = rerank(query_profile, candidates, use_cache=False)
    top_candidates = preselected[: settings.max_candidates_to_enrich]

    # Etapa 2: enriquecer solo el top del pase barato
    enriched = await enrich_with_works(top_candidates, limit=settings.max_candidates_to_enrich)

    for candidate in enriched:
        candidate["subjects"] = clean_subjects(candidate.get("subjects", []))
        candidate["profile"] = build_book_profile(candidate)

    # Etapa 3: rerank final con profile completo (este sí se cachea)
    final_results = rerank(query_profile, enriched, use_cache=True)

    return query_profile, final_results
