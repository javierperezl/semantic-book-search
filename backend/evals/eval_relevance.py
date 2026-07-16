"""
Comparación ciega: pipeline semántico vs. baseline de keyword search puro.

Por cada query, comparamos
  A) los top-N resultados del pipeline completo (intent + rerank semántico)
  B) un baseline ingenuo: primeros N resultados de /search.json sin rerank

y le pedimos a un LLM juez (sin saber cuál lista es cuál) cuál es más
pertinente para la query original.

Punto de partida rápido para chequear a ojo, no un reemplazo de los
experimentos formales del Experimento 1 (que usan métricas de IR con
ground truth fijo, ver evals/experiment_embeddings.py).
"""

import asyncio
import random

from app.llm import extract_intent
from app.openlibrary import search_books
from app.retriever import build_search_context

from evals.judges.client import JudgeError, call_json_judge, get_judge_client

TEST_QUERIES = [
    "quiero un libro como Sapiens pero sobre economia",
    "novelas de ciencia ficcion con temas de inteligencia artificial",
    "libros de autoayuda sobre habitos como Atomic Habits",
]

JUDGE_PROMPT = """
You are judging two lists of book search results (List 1 and List 2) for
the same user query. Decide which list is more relevant to the query.

Query: {query}

List 1:
{list_1}

List 2:
{list_2}

Answer with a JSON object: {{"winner": "list_1" | "list_2" | "tie", "reason": "..."}}
"""


def format_list(books: list[dict]) -> str:
    return "\n".join(
        f"- {b.get('title')} by {b.get('author')} | subjects: {', '.join(b.get('subjects', [])[:5])}"
        for b in books[:5]
    )


async def get_semantic_results(query: str) -> list[dict]:
    intent = extract_intent(query)
    _query_profile, results = await build_search_context(intent)
    return results


async def get_keyword_baseline(query: str) -> list[dict]:
    import httpx

    async with httpx.AsyncClient() as client:
        return await search_books(client, query, limit=5)


async def run_eval():
    client, model = get_judge_client()

    for query in TEST_QUERIES:
        semantic = await get_semantic_results(query)
        baseline = await get_keyword_baseline(query)

        # Orden aleatorio para que el juez no infiera cuál es cuál
        lists = [("semantic", semantic), ("baseline", baseline)]
        random.shuffle(lists)
        label_map = {"list_1": lists[0][0], "list_2": lists[1][0]}

        prompt = JUDGE_PROMPT.format(
            query=query,
            list_1=format_list(lists[0][1]),
            list_2=format_list(lists[1][1]),
        )

        try:
            verdict = call_json_judge(client, model, prompt)
        except JudgeError as e:
            print(f"\nQuery: {query}\nEl juez falló: {e}")
            continue

        winner_label = label_map.get(verdict.get("winner"), verdict.get("winner"))

        print(f"\nQuery: {query}")
        print(f"Ganador: {winner_label} | Razón: {verdict.get('reason')}")


if __name__ == "__main__":
    asyncio.run(run_eval())
