"""
Worker que corre SOLO recuperación (intent + rerank), sin generación, para
una config de embeddings dada. Se invoca en un subproceso propio (ver
evals/experiment_embeddings.py) con EMBEDDING_PROVIDER / EMBEDDING_MODEL ya
puestos en el entorno — así cada config arranca con sus propios settings y
caches (get_settings/get_embedding_provider están cacheados por proceso en
la app real, y no queremos que una config contamine la siguiente).
"""

import argparse
import asyncio
import json
from pathlib import Path

from app.llm import extract_intent
from app.retriever import build_search_context
from evals.metrics.latency import Timer


async def run(dataset_path: str, output_path: str):
    dataset = json.loads(Path(dataset_path).read_text())
    results = []

    for sample in dataset:
        query = sample["query"]

        try:
            with Timer() as timer:
                intent = extract_intent(query)
                _, books = await build_search_context(intent)

            results.append(
                {
                    "id": sample["id"],
                    "query": query,
                    "latency": timer.elapsed,
                    "books": [
                        {
                            "key": b.get("key"),
                            "title": b.get("title"),
                            "author": b.get("author"),
                            "subjects": b.get("subjects", []),
                            "description": b.get("description"),
                        }
                        for b in books
                    ],
                }
            )
        except Exception as e:
            results.append(
                {
                    "id": sample["id"],
                    "query": query,
                    "latency": None,
                    "books": [],
                    "error": str(e),
                }
            )

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="evals/datasets/queries.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    asyncio.run(run(args.dataset, args.output))
