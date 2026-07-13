from openai import OpenAI, OpenAIError

from app.config import get_settings
from app.prompts.generation.default import PROMPT_TEMPLATE
from app.providers.generation.base import GenerationProvider
from app.providers.generation.exceptions import GenerationError


class OpenAIGenerationProvider(GenerationProvider):

    def __init__(self):

        settings = get_settings()

        if not settings.openai_api_key:
            raise GenerationError(
                "OPENAI_API_KEY no está configurada"
            )

        self._client = OpenAI(
            api_key=settings.openai_api_key,
        )

        self._model = settings.generation_model

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:

        prompt = PROMPT_TEMPLATE.format(
            query=query,
            context=context,
        )

        try:

            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

        except OpenAIError as e:

            raise GenerationError(
                f"Fallo generando respuesta: {e}"
            ) from e

        return response.choices[0].message.content