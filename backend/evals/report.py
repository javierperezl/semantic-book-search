import json
from pathlib import Path


def save_results(results):

    output = Path("evals/results/results.json")

    output.write_text(
        json.dumps(
            results,
            indent=4,
            ensure_ascii=False,
        )
    )