from app.models import Intent
from app.providers.intent.exceptions import IntentExtractionError
from app.providers.intent.factory import get_intent_provider


def extract_intent(query: str) -> Intent:
    provider = get_intent_provider()
    return provider.extract_intent(query)