import logging

from evals.judges.client import JudgeError
from evals.judges.openai_judge import OpenAIJudge

logger = logging.getLogger(__name__)


def judge_verdict(
    judge: OpenAIJudge,
    query: str,
    answer: str,
    books: list[dict],
) -> dict | None:
    """
    Devuelve el veredicto completo del juez (grounding, relevance, clarity,
    coverage, reasoning, overall_score, todos 1-10), o None si el juez falla.

    None en vez de un valor centinela como -1: se puede excluir del promedio
    explícitamente en el reporte, en vez de contaminarlo en silencio.
    """
    try:
        return judge.evaluate(query=query, answer=answer, books=books)
    except JudgeError as e:
        logger.warning("El juez falló para query=%r: %s", query, e)
        return None
