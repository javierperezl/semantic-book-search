import asyncio
import json
from pathlib import Path

from app.generator import generate_answer
from app.llm import extract_intent
from app.retriever import build_search_context

from evals.metrics.grounding import grounding_score
from evals.metrics.latency import Timer
from evals.report import save_results


async def evaluate(query: str):

    with Timer() as timer:

        intent = extract_intent(query)

        _, books = await build_search_context(intent)

        answer, grounded, warnings = generate_answer(
            query,
            books,
        )

    return {

        "query": query,

        "latency": timer.elapsed,

        "grounded": grounded,

        "grounding_score": grounding_score(
            {
                "grounded": grounded,
            }
        ),

        "warnings": warnings,

        "answer": answer,

        "books": books,
    }


async def main():

    dataset = json.loads(

        Path(
            "evals/datasets/queries.json"
        ).read_text()

    )

    results = []

    for sample in dataset:

        print(
            f'Evaluating: {sample["query"]}'
        )

        result = await evaluate(
            sample["query"]
        )

        results.append(result)

    save_results(results)


if __name__ == "__main__":

    asyncio.run(main())