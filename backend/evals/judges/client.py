import json
import logging

from openai import OpenAI, OpenAIError

from app.config import get_settings

logger = logging.getLogger(__name__)


class JudgeError(Exception):
    """El juez no pudo producir un veredicto (llamada fallida, JSON inválido, campos faltantes)."""


def get_judge_client(model: str | None = None) -> tuple[OpenAI, str]:
    settings = get_settings()

    if not settings.openai_api_key:
        raise JudgeError("OPENAI_API_KEY no está configurada")

    client = OpenAI(api_key=settings.openai_api_key)
    return client, (model or settings.generation_model)


def call_json_judge(client: OpenAI, model: str, prompt: str) -> dict:
    """
    Llama al modelo pidiendo JSON estructurado y devuelve el dict ya parseado.
    Centraliza el manejo de errores para que todos los jueces (recomendación,
    pares, pooling de relevancia) se comporten igual ante fallos de red o
    respuestas mal formadas.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
    except OpenAIError as e:
        raise JudgeError(f"Fallo llamando al juez: {e}") from e

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise JudgeError(f"Veredicto no parseable como JSON: {e} | raw={raw!r}") from e
