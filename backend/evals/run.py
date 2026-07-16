import asyncio
import json
import logging
from pathlib import Path

from app.generator import generate_answer
from app.llm import extract_intent
from app.retriever import build_search_context

from evals.judges.openai_judge import OpenAIJudge
from evals.metrics.grounding import grounding_score
from evals.metrics.latency import Timer
from evals.metrics.relevance import judge_verdict
from evals.report import save_results

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def evaluate(query: str, judge: OpenAIJudge) -> dict:

    with Timer() as timer:

        intent = extract_intent(query)

        _, books = await build_search_context(intent)

        answer, grounded, warnings = generate_answer(
            query,
            books,
        )

    verdict = judge_verdict(judge, query, answer, books)

    return {
        "query": query,
        "latency": timer.elapsed,
        "grounded": grounded,
        "grounding_score": grounding_score({"grounded": grounded}),
        # None si el juez falló para esta query
        "judge_grounding": verdict["grounding"] if verdict else None,
        "judge_relevance": verdict["relevance"] if verdict else None,
        "judge_clarity": verdict["clarity"] if verdict else None,
        "judge_coverage": verdict["coverage"] if verdict else None,
        "judge_overall": verdict["overall_score"] if verdict else None,
        "judge_reasoning": verdict["reasoning"] if verdict else None,
        "warnings": warnings,
        "answer": answer,
        "books": books,
    }


async def main():

    dataset = json.loads(Path("evals/datasets/queries.json").read_text())

    # Un solo juez para todo el run: reutiliza el cliente OpenAI en vez de
    # crear uno nuevo por query.
    judge = OpenAIJudge()

    results = []

    for sample in dataset:

        print(f'Evaluating [{sample.get("id")}] ({sample.get("category")}): {sample["query"]}')

        try:
            result = await evaluate(sample["query"], judge)
        except Exception as e:
            # Una query que revienta el pipeline no debe tumbar todo el benchmark.
            logger.error("Query '%s' falló durante la evaluación: %s", sample["query"], e)
            result = {
                "query": sample["query"],
                "latency": None,
                "grounded": None,
                "grounding_score": None,
                "judge_grounding": None,
                "judge_relevance": None,
                "judge_clarity": None,
                "judge_coverage": None,
                "judge_overall": None,
                "judge_reasoning": None,
                "warnings": [f"Evaluacion fallo: {e}"],
                "answer": None,
                "books": [],
            }

        results.append(result)

    save_results(results)


if __name__ == "__main__":
    asyncio.run(main())
