"""
Calibración humana del juez LLM (Experimento 8, versión rápida "sanity check").

Uso: correr esto DESPUÉS de haber corrido evals/run.py al menos una vez, para
comparar cómo puntúa una persona vs. cómo puntuó el juez, sobre las MISMAS
respuestas ya generadas (no vuelve a llamar al pipeline ni al juez).

    python -m evals.human_calibration

Para cada query en evals/results/results.json te muestra la consulta, los
libros recuperados y la respuesta generada, y te pide un score 1-10 propio.
Al final compara tu score contra judge_overall y guarda todo en
evals/results/human_calibration.json.
"""

import json
import statistics
from pathlib import Path

RESULTS_PATH = Path("evals/results/results.json")
OUTPUT_PATH = Path("evals/results/human_calibration.json")


def _prompt_score(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None  # permite saltar una query
        try:
            score = int(raw)
        except ValueError:
            print("Escribe un número entero del 1 al 10, o Enter para saltar.")
            continue
        if 1 <= score <= 10:
            return score
        print("Tiene que estar entre 1 y 10.")


def main():
    if not RESULTS_PATH.exists():
        print(f"No existe {RESULTS_PATH}. Corre primero: python -m evals.run")
        return

    results = json.loads(RESULTS_PATH.read_text())
    comparisons = []

    print(
        "Vas a calificar cada respuesta con TU propio criterio (1-10), "
        "sin ver el score del juez todavía. Enter en blanco para saltar una query.\n"
    )

    for r in results:
        if r.get("judge_overall") is None:
            continue  # el juez ya había fallado para esta query, no hay con qué comparar

        print("=" * 70)
        print(f"Query: {r['query']}")
        print("\nLibros recuperados (top 5):")
        for b in (r.get("books") or [])[:5]:
            print(f"  - {b.get('title')} — {b.get('author')}")
        print(f"\nRespuesta generada:\n{r.get('answer')}\n")

        human_score = _prompt_score(
            "Tu score 1-10 para esta respuesta (relevancia + calidad general): "
        )
        if human_score is None:
            continue

        comparisons.append(
            {
                "query": r["query"],
                "human_score": human_score,
                "judge_score": r["judge_overall"],
                "diff": human_score - r["judge_overall"],
            }
        )

    if not comparisons:
        print("No se calificó ninguna query.")
        return

    diffs = [c["diff"] for c in comparisons]
    print("\n" + "=" * 70)
    print(f"Queries comparadas: {len(comparisons)}")
    print(f"Diferencia promedio (humano - juez): {round(statistics.mean(diffs), 2)}")
    print(f"Diferencia absoluta promedio: {round(statistics.mean([abs(d) for d in diffs]), 2)}")

    if statistics.mean(diffs) > 1.5:
        print("El juez parece más DURO que tú en promedio (te da menos puntos de los que tú darías).")
    elif statistics.mean(diffs) < -1.5:
        print("El juez parece más GENEROSO que tú en promedio (te da más puntos de los que tú darías).")
    else:
        print("El juez está razonablemente alineado con tu criterio.")

    OUTPUT_PATH.write_text(json.dumps(comparisons, indent=4, ensure_ascii=False))
    print(f"\nDetalle guardado en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
