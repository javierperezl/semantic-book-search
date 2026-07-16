"""
Ground truth compartido para el Experimento 1 (y cualquier otro que necesite
P@k/Recall/NDCG). Método: pooling (estilo TREC) + graduación por LLM.

Por qué pooling: ninguna config individual recuperó "todos los libros
relevantes que existen" — cada una trae su propio top-N. Pooling junta la
UNIÓN de lo que cualquier config recuperó para una query, y ESO es lo que se
gradúa. Así el ground truth no favorece a la config que generó el pool.

Por qué se cachea en disco (evals/results/relevance_judgments.json): el
juicio de un par (query, libro) no depende de qué config lo recuperó, así
que se computa una sola vez y se reutiliza para las 5 configs — y para
cualquier config nueva que se agregue después, sin volver a gastar llamadas
en pares ya juzgados.
"""

import json
import logging
from pathlib import Path

from evals.judges.client import JudgeError, call_json_judge, get_judge_client

logger = logging.getLogger(__name__)

JUDGMENTS_PATH = Path("evals/results/relevance_judgments.json")

GRADE_PROMPT = """
You are building ground-truth relevance judgments for an information
retrieval evaluation. This judgment will be reused for EVERY retrieval
system being compared, so judge the book strictly on its own merits against
the query — ignore which system retrieved it.

Query: {query}

Book:
- Title: {title}
- Author: {author}
- Subjects: {subjects}
- Description: {description}

Grade relevance:
2 = highly relevant, a strong match for the query
1 = somewhat relevant, a plausible but weaker match
0 = not relevant

Return ONLY a JSON object: {{"grade": <0, 1, or 2>}}
"""


def _grade(client, model: str, query: str, book: dict) -> int:
    prompt = GRADE_PROMPT.format(
        query=query,
        title=book.get("title"),
        author=book.get("author"),
        subjects=", ".join((book.get("subjects") or [])[:8]) or "none",
        description=(book.get("description") or "none")[:500],
    )

    verdict = call_json_judge(client, model, prompt)

    try:
        grade = int(verdict["grade"])
    except (KeyError, TypeError, ValueError) as e:
        raise JudgeError(f"grade inválido: {e} | verdict={verdict!r}") from e

    if grade not in (0, 1, 2):
        raise JudgeError(f"grade fuera de rango 0-2: {grade}")

    return grade


def build_pool(config_result_files: list[Path]) -> dict[str, dict[str, dict]]:
    """query -> {book_key: metadata}, unión de todo lo recuperado por cualquier config."""
    pool: dict[str, dict[str, dict]] = {}

    for path in config_result_files:
        data = json.loads(path.read_text())
        for entry in data:
            query = entry["query"]
            pool.setdefault(query, {})
            for book in entry.get("books", []):
                key = book.get("key")
                if key and key not in pool[query]:
                    pool[query][key] = book

    return pool


def load_or_build_judgments(config_result_files: list[Path]) -> dict[str, dict[str, int]]:
    """query -> {book_key: grade}. Persistido en disco, solo gradúa pares nuevos."""
    judgments: dict[str, dict[str, int]] = {}
    if JUDGMENTS_PATH.exists():
        judgments = json.loads(JUDGMENTS_PATH.read_text())

    pool = build_pool(config_result_files)
    client, model = get_judge_client()

    pending = sum(
        1
        for query, books_by_key in pool.items()
        for key in books_by_key
        if key not in judgments.get(query, {})
    )
    print(f"Pares (query, libro) nuevos por graduar: {pending}")

    for query, books_by_key in pool.items():
        judgments.setdefault(query, {})

        for key, book in books_by_key.items():
            if key in judgments[query]:
                continue

            try:
                judgments[query][key] = _grade(client, model, query, book)
            except JudgeError as e:
                logger.warning("No se pudo graduar %r para query=%r: %s", key, query, e)

    JUDGMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JUDGMENTS_PATH.write_text(json.dumps(judgments, indent=2, ensure_ascii=False))

    return judgments
