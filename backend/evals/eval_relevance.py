"""
Eval mínima para la métrica de éxito del reto: "resultados más pertinentes
que una búsqueda por keyword".

Idea: por cada query de prueba, comparamos
  A) los top-N resultados de nuestro pipeline (intent + rerank semántico)
  B) un baseline ingenuo: primeros N resultados de /search.json sin rerank

y le pedimos a un LLM (distinto del que generó la respuesta, o el mismo con
un prompt de juez neutral) que diga cuál lista es más pertinente para la
query original, sin saber cuál es cuál (ciego).

Esto es un punto de partida, no una suite completa: correr manualmente con
un puñado de queries representativas y revisar los veredictos, no asumir
que un solo run es concluyente.
"""

import asyncio
import json
import random

from openai import OpenAI

from app.config import get_settings
from app.llm import extract_intent
from app.openlibrary import search_books
from app.retriever import build_search_context

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
    # build_search_context ya devuelve los resultados reranqueados
    _query_profile, results = await build_search_context(intent)
    return results


async def get_keyword_baseline(query: str) -> list[dict]:
    import httpx

    async with httpx.AsyncClient() as client:
        return await search_books(client, query, limit=5)


async def run_eval():
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

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

        response = client.chat.completions.create(
            model=settings.generation_model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        verdict = json.loads(response.choices[0].message.content)
        winner_label = label_map.get(verdict.get("winner"), verdict.get("winner"))

        print(f"\nQuery: {query}")
        print(f"Ganador: {winner_label} | Razón: {verdict.get('reason')}")


if __name__ == "__main__":
    asyncio.run(run_eval())
