from evals.judges.client import JudgeError, call_json_judge, get_judge_client

# Alineado con el Experimento 7 del plan del equipo: el juez nunca participa
# en la generación, solo evalúa, y devuelve un JSON con estas dimensiones.
JUDGE_PROMPT = """
You are an independent evaluator for a book recommendation system. Judge as
an outside reviewer would — do not assume the recommendation is correct just
because it sounds fluent, and do not reward it for using evidence it doesn't
actually have.

User query:
{query}

Books retrieved by the system (the only evidence it had access to):
{books}

Recommendation the system generated for the user:
{answer}

Rate each dimension on a 1-10 scale:
- grounding: does the recommendation rely ONLY on the retrieved evidence,
  with no invented facts about books or authors?
- relevance: are the retrieved books actually relevant to the query?
- clarity: is the recommendation clear and easy to follow?
- coverage: does the recommendation address what the user actually asked for?
- overall_score: your own holistic judgment, not necessarily the average of
  the above (e.g. perfect grounding with irrelevant books should NOT score high overall)

Return ONLY a JSON object, no other text:
{{"grounding": <1-10>, "relevance": <1-10>, "clarity": <1-10>, "coverage": <1-10>, "reasoning": "<one sentence, in Spanish>", "overall_score": <1-10>}}
"""

_REQUIRED_FIELDS = ("grounding", "relevance", "clarity", "coverage", "overall_score")


def _format_books(books: list[dict], limit: int = 5) -> str:
    lines = []
    for b in books[:limit]:
        subjects = ", ".join(b.get("subjects", [])[:5]) or "none available"
        lines.append(f'- "{b.get("title")}" by {b.get("author")} | subjects: {subjects}')
    return "\n".join(lines) or "(no se recuperó ningún libro)"


class OpenAIJudge:
    """
    Juez LLM independiente del proveedor de generación de producción.
    Por defecto usa GENERATION_MODEL; se puede pasar otro modelo al
    construirlo para reducir el sesgo de "el modelo se autoevalúa".
    """

    def __init__(self, model: str | None = None):
        self._client, self._model = get_judge_client(model)

    def evaluate(self, query: str, answer: str, books: list[dict]) -> dict:
        prompt = JUDGE_PROMPT.format(
            query=query,
            books=_format_books(books),
            answer=answer,
        )

        verdict = call_json_judge(self._client, self._model, prompt)

        try:
            for field in _REQUIRED_FIELDS:
                value = float(verdict[field])
                if not (1 <= value <= 10):
                    raise ValueError(f"{field} fuera de rango 1-10: {value}")
                verdict[field] = value
            verdict.setdefault("reasoning", "")
        except (KeyError, TypeError, ValueError) as e:
            raise JudgeError(f"Veredicto incompleto o inválido: {e} | verdict={verdict!r}") from e

        return verdict
