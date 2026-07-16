"""
Experimento 1 — Comparación de modelos de embeddings.

Uso:
    export OPENAI_API_KEY=tu-key
    python -m evals.experiment_embeddings

Corre cada config de evals/embedding_configs.py en un subproceso separado
(para que EMBEDDING_PROVIDER/EMBEDDING_MODEL de una config no contaminen la
siguiente, ya que get_settings()/get_embedding_provider() se cachean por
proceso en la app real). Luego construye el ground truth compartido por
pooling + LLM, calcula P@5, P@10, R@10 y NDCG@10 por config, y guarda una
tabla comparativa.

Nota sobre costo: no se calculan cifras en dólares (los precios de las APIs
cambian y una cifra vieja hardcodeada sería peor que no tener ninguna).
En su lugar se reporta algo que no cambia con el tiempo: cuántas llamadas de
red hace cada config (0 para las locales de sentence-transformers, 1 por
query+candidato para las de OpenAI) — con eso más el precio vigente del
momento en que corras el experimento, puedes sacar el costo real.
"""

import json
import os
import statistics
import subprocess
from pathlib import Path

from evals.embedding_configs import EMBEDDING_CONFIGS
from evals.metrics.ranking import ndcg_at_k, precision_at_k, recall_at_k
from evals.relevance_judgments import load_or_build_judgments

RESULTS_DIR = Path("evals/results/embeddings")


def run_config(config: dict) -> Path:
    output_path = RESULTS_DIR / f"{config['name']}.json"

    env = os.environ.copy()
    env["EMBEDDING_PROVIDER"] = config["EMBEDDING_PROVIDER"]
    env["EMBEDDING_MODEL"] = config["EMBEDDING_MODEL"]

    print(f"\n>>> Config '{config['name']}' ({config['EMBEDDING_PROVIDER']} / {config['EMBEDDING_MODEL']})")

    subprocess.run(
        ["python", "-m", "evals._retrieve_worker", "--output", str(output_path)],
        env=env,
        check=True,
    )

    return output_path


def evaluate_config(output_path: Path, judgments: dict) -> dict:
    data = json.loads(output_path.read_text())

    p5, p10, r10, ndcg10, latencies = [], [], [], [], []

    for entry in data:
        query = entry["query"]
        query_judgments = judgments.get(query, {})
        relevant_keys = {k for k, g in query_judgments.items() if g > 0}
        grades = {k: float(g) for k, g in query_judgments.items()}

        ranked_keys = [b["key"] for b in entry.get("books", []) if b.get("key")]

        p5.append(precision_at_k(ranked_keys, relevant_keys, 5))
        p10.append(precision_at_k(ranked_keys, relevant_keys, 10))
        r10.append(recall_at_k(ranked_keys, relevant_keys, 10))
        ndcg10.append(ndcg_at_k(ranked_keys, grades, 10))

        if entry.get("latency") is not None:
            latencies.append(entry["latency"])

    def avg(values):
        return round(statistics.mean(values), 3) if values else None

    return {
        "precision_at_5": avg(p5),
        "precision_at_10": avg(p10),
        "recall_at_10": avg(r10),
        "ndcg_at_10": avg(ndcg10),
        "avg_latency_sec": avg(latencies),
    }


def _print_table(rows: list[dict]):
    header = f"{'config':<16} {'P@5':>6} {'P@10':>6} {'R@10':>6} {'NDCG@10':>8} {'latencia(s)':>12}"
    print("\n" + header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['config']:<16} {r['precision_at_5']:>6} {r['precision_at_10']:>6} "
            f"{r['recall_at_10']:>6} {r['ndcg_at_10']:>8} {r['avg_latency_sec']:>12}"
        )


def _save_report(rows: list[dict]):
    path = Path("evals/results/experiment1_embeddings.md")

    lines = [
        "# Experimento 1 — Comparación de modelos de embeddings",
        "",
        "| Config | P@5 | P@10 | R@10 | NDCG@10 | Latencia (s) |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['config']} | {r['precision_at_5']} | {r['precision_at_10']} | "
            f"{r['recall_at_10']} | {r['ndcg_at_10']} | {r['avg_latency_sec']} |"
        )

    path.write_text("\n".join(lines) + "\n")
    print(f"\nReporte guardado en {path}")


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_paths = [run_config(config) for config in EMBEDDING_CONFIGS]

    print("\n>>> Construyendo/actualizando juicios de relevancia compartidos...")
    judgments = load_or_build_judgments(output_paths)

    rows = [
        {"config": config["name"], **evaluate_config(output_path, judgments)}
        for config, output_path in zip(EMBEDDING_CONFIGS, output_paths)
    ]

    _print_table(rows)
    _save_report(rows)


if __name__ == "__main__":
    main()
