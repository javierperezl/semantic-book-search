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
from app.trace import (
    PipelineTrace,
    TraceCheapCandidate,
    TraceFinalCandidate,
    TraceReferenceBook,
    stage,
)


async def get_reference_book(
    intent: Intent, trace: PipelineTrace | None = None
) -> dict | None:
    """
    Recupera el primer libro de referencia mencionado por el usuario,
    con sus datos REALES de Open Library (no lo que el LLM asume que es).
    Devuelve None si no hay referencia o no se encuentra.
    """
    if not intent.reference_books:
        return None

    requested = intent.reference_books[0]

    try:
        book = await search_first_book(requested)
    except OpenLibraryError:
        book = None

    if trace is not None:
        trace.reference_book = TraceReferenceBook(
            requested=requested,
            found=book is not None,
            title=book.get("title") if book else None,
            author=book.get("author") if book else None,
            key=book.get("key") if book else None,
        )

    return book


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


async def retrieve_candidates(
    intent: Intent,
    reference_book: dict | None,
    trace: PipelineTrace | None = None,
) -> list[dict]:
    settings = get_settings()

    queries = intent.search_queries[: settings.max_search_queries]

    try:
        candidates = await multi_search(
            queries, limit_per_query=settings.limit_per_query, trace=trace
        )
    except OpenLibraryError:
        return []

    return _exclude_reference_book(candidates, reference_book)


def _record_cheap_rerank(
    trace: PipelineTrace, preselected: list[dict], cutoff: int
) -> None:
    for i, candidate in enumerate(preselected):
        trace.cheap_rerank.append(
            TraceCheapCandidate(
                key=candidate.get("key"),
                title=candidate.get("title"),
                author=candidate.get("author"),
                rank=i + 1,
                score=candidate.get("semantic_score", 0.0),
                selected_for_enrichment=i < cutoff,
            )
        )


def _record_final_rerank(trace: PipelineTrace, final_results: list[dict]) -> None:
    # Posición y score de cada candidato en la etapa barata, para mostrar
    # cuánto lo movió el enriquecimiento en el ranking final.
    cheap_by_key = {c.key: c for c in trace.cheap_rerank if c.key}

    for i, candidate in enumerate(final_results):
        cheap = cheap_by_key.get(candidate.get("key"))
        trace.final_rerank.append(
            TraceFinalCandidate(
                key=candidate.get("key"),
                title=candidate.get("title"),
                author=candidate.get("author"),
                final_rank=i + 1,
                final_score=candidate.get("semantic_score", 0.0),
                cheap_rank=cheap.rank if cheap else None,
                cheap_score=cheap.score if cheap else None,
                description_added=candidate.get("description") is not None,
            )
        )


async def build_search_context(
    intent: Intent, trace: PipelineTrace | None = None
) -> tuple[str, list[dict]]:
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

    Con trace != None registra además el detalle de cada etapa (scores,
    timings, selección) para la UI de desarrollo. Con trace=None el
    comportamiento es idéntico al de siempre.
    """
    settings = get_settings()

    with stage(trace, "reference_book_lookup"):
        reference_book = await get_reference_book(intent, trace=trace)

    query_profile = build_query_profile(reference_book, intent.semantic_description)

    if trace is not None:
        trace.query_profile = query_profile

    with stage(trace, "openlibrary_search"):
        candidates = await retrieve_candidates(intent, reference_book, trace=trace)

    if trace is not None:
        trace.total_candidates = len(candidates)

    if not candidates:
        return query_profile, []

    for candidate in candidates:
        candidate["profile"] = build_book_profile(candidate)

    # Etapa 1: rerank barato (sin cachear, el profile es parcial)
    with stage(trace, "cheap_rerank"):
        preselected = rerank(query_profile, candidates, use_cache=False)

    top_candidates = preselected[: settings.max_candidates_to_enrich]

    if trace is not None:
        _record_cheap_rerank(trace, preselected, settings.max_candidates_to_enrich)

    # Etapa 2: enriquecer solo el top del pase barato
    with stage(trace, "enrich_works"):
        enriched = await enrich_with_works(
            top_candidates, limit=settings.max_candidates_to_enrich
        )

    for candidate in enriched:
        candidate["subjects"] = clean_subjects(candidate.get("subjects", []))
        candidate["profile"] = build_book_profile(candidate)

    # Etapa 3: rerank final con profile completo (este sí se cachea)
    with stage(trace, "final_rerank"):
        final_results = rerank(query_profile, enriched, use_cache=True)

    if trace is not None:
        _record_final_rerank(trace, final_results)

    return query_profile, final_results
