from app.config import get_settings
from app.providers.generation.base import GenerationProvider
from app.providers.generation.openai_provider import (
    OpenAIGenerationProvider,
)

_provider: GenerationProvider | None = None


def get_generation_provider() -> GenerationProvider:

    global _provider

    if _provider is not None:
        return _provider

    settings = get_settings()

    match settings.generation_provider:

        case "openai":
            _provider = OpenAIGenerationProvider()

        case _:
            raise ValueError(
                f"Generation provider '{settings.generation_provider}' no soportado."
            )

    return _provider