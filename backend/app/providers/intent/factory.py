from app.config import get_settings
from app.providers.intent.base import IntentProvider
from app.providers.intent.openai_provider import OpenAIIntentProvider

_provider: IntentProvider | None = None


def get_intent_provider() -> IntentProvider:

    global _provider

    if _provider is not None:
        return _provider

    settings = get_settings()

    match settings.intent_provider:

        case "openai":
            _provider = OpenAIIntentProvider()

        case _:
            raise ValueError(
                f"Intent provider '{settings.intent_provider}' no soportado."
            )

    return _provider