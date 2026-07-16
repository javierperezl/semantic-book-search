import json
import statistics
from pathlib import Path

RESULTS_DIR = Path("evals/results")

_JUDGE_FIELDS = [
    "judge_grounding",
    "judge_relevance",
    "judge_clarity",
    "judge_coverage",
    "judge_overall",
]


def _average(values: list) -> float | None:
    clean = [v for v in values if v is not None]
    return round(statistics.mean(clean), 3) if clean else None


def _summarize(results: list[dict]) -> dict:
    summary = {
        "num_queries": len(results),
        "avg_latency_sec": _average([r.get("latency") for r in results]),
        "avg_grounding_score": _average([r.get("grounding_score") for r in results]),
        "ungrounded_queries": [r["query"] for r in results if r.get("grounded") is False],
        "unjudged_queries": [r["query"] for r in results if r.get("judge_overall") is None],
    }

    for field in _JUDGE_FIELDS:
        summary[f"avg_{field}"] = _average([r.get(field) for r in results])

    return summary


def _to_markdown(summary: dict) -> str:
    lines = [
        "# Reporte de evaluación",
        "",
        f"- Queries evaluadas: {summary['num_queries']}",
        f"- Latencia promedio: {summary['avg_latency_sec']} s",
        f"- Grounding (heurístico, 0-1): {summary['avg_grounding_score']}",
        "",
        "## Juez LLM (1-10 cada dimensión)",
        f"- Grounding: {summary['avg_judge_grounding']}",
        f"- Relevance: {summary['avg_judge_relevance']}",
        f"- Clarity: {summary['avg_judge_clarity']}",
        f"- Coverage: {summary['avg_judge_coverage']}",
        f"- Overall: {summary['avg_judge_overall']}",
    ]

    if summary["ungrounded_queries"]:
        lines.append("")
        lines.append("## Queries sin grounding heurístico (revisar posible alucinación)")
        lines += [f"- {q}" for q in summary["ungrounded_queries"]]

    if summary["unjudged_queries"]:
        lines.append("")
        lines.append("## Queries sin veredicto del juez (fallo al evaluar)")
        lines += [f"- {q}" for q in summary["unjudged_queries"]]

    return "\n".join(lines) + "\n"


def save_results(results: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    (RESULTS_DIR / "results.json").write_text(
        json.dumps(results, indent=4, ensure_ascii=False)
    )

    summary = _summarize(results)

    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, indent=4, ensure_ascii=False)
    )

    report_md = _to_markdown(summary)
    (RESULTS_DIR / "report.md").write_text(report_md)

    print(f"\nResultados guardados en {RESULTS_DIR}/")
    print(report_md)
