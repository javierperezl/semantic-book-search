import logging

from app.config import get_settings
from app.providers.generation.exceptions import GenerationError
from app.providers.generation.factory import get_generation_provider

logger = logging.getLogger(__name__)


def _has_evidence(book: dict) -> bool:
    """
    Un candidato con score alto pero sin subjects ni descripción no tiene
    nada verificable detrás — probablemente el embedding lo empujó arriba
    por matching literal de palabras en el título, no por contenido real.
    """
    return bool(book.get("subjects")) or bool(book.get("description"))


def _select_for_context(results: list[dict], limit: int) -> list[dict]:
    with_evidence = [b for b in results if _has_evidence(b)]
    without_evidence = [b for b in results if not _has_evidence(b)]

    selected = with_evidence[:limit]

    if len(selected) < limit:
        selected += without_evidence[: limit - len(selected)]

    return selected


def _build_context(results: list[dict], limit: int) -> str:
    selected = _select_for_context(results, limit)

    context = ""

    for i, book in enumerate(selected, start=1):

        subjects = ", ".join(book.get("subjects", [])[:8]) or "none available"

        score = book.get("semantic_score")

        score_str = (
            f"{score:.3f}"
            if isinstance(score, float)
            else "n/a"
        )

        context += f"""
Book {i}
Title: {book.get("title")}
Author: {book.get("author")}
Subjects: {subjects}
Semantic score: {score_str}
"""

    return context


def _check_grounding(
    answer: str,
    selected: list[dict],
) -> tuple[bool, list[str]]:

    warnings = []

    known_titles = [
        (book.get("title") or "").lower()
        for book in selected
        if book.get("title")
    ]

    if not known_titles:
        return True, warnings

    any_title_mentioned = any(
        title[:15] in answer.lower()
        for title in known_titles
        if title
    )

    if not any_title_mentioned:

        warnings.append(
            "No se detectó ninguno de los títulos recuperados en la respuesta generada; "
            "revisar manualmente si el modelo alucinó libros."
        )

        return False, warnings

    return True, warnings


def generate_answer(
    query: str,
    results: list[dict],
) -> tuple[str, bool, list[str]]:

    settings = get_settings()

    limit = settings.max_results_to_generate

    if not results:

        return (
            "No encontré libros que coincidan con tu búsqueda en Open Library. "
            "Intenta reformular la consulta con otros temas o autores.",
            True,
            [],
        )

    selected = _select_for_context(
        results,
        limit,
    )

    context = _build_context(
        results,
        limit,
    )

    provider = get_generation_provider()

    answer = provider.generate(
        query=query,
        context=context,
    )

    grounded, warnings = _check_grounding(
        answer,
        selected,
    )

    return (
        answer,
        grounded,
        warnings,
    )