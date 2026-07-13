import json
import logging

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.config import get_settings
from app.models import Intent
from app.prompts.intent.default import PROMPT_TEMPLATE
from app.providers.intent.base import IntentProvider
from app.providers.intent.exceptions import IntentExtractionError

logger = logging.getLogger(__name__)


class OpenAIIntentProvider(IntentProvider):
    def __init__(self):
        settings = get_settings()

        if not settings.openai_api_key:
            raise IntentExtractionError(
                "OPENAI_API_KEY no está configurada"
            )

        self._client = OpenAI(
            api_key=settings.openai_api_key,
        )

        self._model = settings.intent_model

    def extract_intent(
        self,
        query: str,
        _retry: bool = True,
    ) -> Intent:

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "user",
                        "content": PROMPT_TEMPLATE.format(query=query),
                    }
                ],
            )

        except OpenAIError as e:
            raise IntentExtractionError(
                f"Fallo llamando al LLM: {e}"
            ) from e

        raw = response.choices[0].message.content

        try:
            data = json.loads(raw)
            return Intent(**data)

        except (json.JSONDecodeError, ValidationError) as e:

            logger.warning(
                "Intent inválido: %s | raw=%r",
                e,
                raw,
            )

            if _retry:
                return self.extract_intent(
                    query,
                    _retry=False,
                )

            raise IntentExtractionError(
                "El LLM no devolvió un intent válido."
            ) from e