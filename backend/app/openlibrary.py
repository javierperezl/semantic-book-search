import asyncio
import logging
from typing import Optional

import httpx

from app.config import get_settings
from app.trace import PipelineTrace, TraceQueryResult

logger = logging.getLogger(__name__)

SEARCH_URL = "https://openlibrary.org/search.json"
WORKS_URL = "https://openlibrary.org{key}.json"


class OpenLibraryError(Exception):
    """Error al comunicarse con Open Library (red, timeout, respuesta inválida)."""


def _headers() -> dict:
    settings = get_settings()
    return {"User-Agent": settings.openlibrary_user_agent}


def _doc_to_book(doc: dict) -> dict:
    return {
        "title": doc.get("title"),
        "author": ", ".join(doc.get("author_name", []) or []),
        "year": doc.get("first_publish_year"),
        "edition_count": doc.get("edition_count", 0),
        "subjects": doc.get("subject", []) or [],
        "description": None,  # se completa opcionalmente vía /works
        "ratings_average": doc.get("ratings_average"),
        "ratings_count": doc.get("ratings_count"),
        "readinglog_count": doc.get("readinglog_count"),
        "key": doc.get("key"),
    }


async def search_books(
    client: httpx.AsyncClient, query: str, limit: int = 10
) -> list[dict]:
    settings = get_settings()

    try:
        response = await client.get(
            SEARCH_URL,
            params={"q": query, "limit": limit, "fields": "*"},
            headers=_headers(),
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("Open Library /search falló para query=%r: %s", query, e)
        raise OpenLibraryError(f"Fallo buscando '{query}' en Open Library") from e

    try:
        docs = response.json().get("docs", [])
    except ValueError as e:
        raise OpenLibraryError("Respuesta no-JSON de Open Library /search") from e

    return [_doc_to_book(doc) for doc in docs]


async def fetch_work_details(
    client: httpx.AsyncClient, key: str
) -> Optional[dict]:
    """
    Trae /works/<id>.json para obtener descripción y subjects más completos.
    Devuelve None si falla (no es crítico: el candidato sigue funcionando
    solo con los datos de /search).
    """
    if not key:
        return None

    settings = get_settings()

    try:
        response = await client.get(
            WORKS_URL.format(key=key),
            headers=_headers(),
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.info("No se pudo enriquecer %s con /works: %s", key, e)
        return None

    description = data.get("description")
    if isinstance(description, dict):
        description = description.get("value")

    subjects = data.get("subjects", []) or []

    return {"description": description, "extra_subjects": subjects}


async def multi_search(
    queries: list[str], limit_per_query: int = 5, trace: PipelineTrace | None = None
) -> list[dict]:
    """
    Ejecuta las búsquedas EN PARALELO (antes eran secuenciales) y deduplica
    por 'key'. Si una query individual falla, se ignora esa query en vez de
    tumbar todo el request (mejor degradar que fallar por completo).
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            search_books(client, query, limit=limit_per_query) for query in queries
        ]
        results_per_query = await asyncio.gather(*tasks, return_exceptions=True)

    seen = set()
    results = []

    for query, books_or_error in zip(queries, results_per_query):
        if isinstance(books_or_error, Exception):
            logger.warning("Query '%s' descartada: %s", query, books_or_error)
            if trace is not None:
                trace.queries.append(TraceQueryResult(query=query, failed=True))
            continue

        if trace is not None:
            trace.queries.append(
                TraceQueryResult(query=query, returned=len(books_or_error))
            )

        for book in books_or_error:
            key = book.get("key")
            if key is None or key in seen:
                continue
            seen.add(key)
            results.append(book)

    return results


async def enrich_with_works(candidates: list[dict], limit: int) -> list[dict]:
    """
    Enriquece solo los primeros `limit` candidatos con /works (descripción +
    subjects adicionales). Este límite es a propósito: /works es una llamada
    por libro y no queremos N llamadas por cada request del usuario.
    """
    to_enrich = candidates[:limit]
    rest = candidates[limit:]

    async with httpx.AsyncClient() as client:
        tasks = [fetch_work_details(client, c.get("key")) for c in to_enrich]
        details = await asyncio.gather(*tasks)

    for candidate, detail in zip(to_enrich, details):
        if detail:
            candidate["description"] = detail.get("description")
            extra = detail.get("extra_subjects") or []
            # /works casi siempre repite los mismos subjects que ya vinieron
            # de /search: deduplicamos aquí (case-insensitive) para no
            # devolverle al usuario la misma lista duplicada dos veces.
            seen = set()
            merged = []
            for subject in list(candidate.get("subjects", [])) + list(extra):
                key = subject.strip().lower()
                if not subject or key in seen:
                    continue
                seen.add(key)
                merged.append(subject)
            candidate["subjects"] = merged

    return to_enrich + rest


async def search_first_book(title: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        try:
            books = await search_books(client, title, limit=1)
        except OpenLibraryError:
            return None
    return books[0] if books else None
