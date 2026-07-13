from abc import ABC, abstractmethod

from app.models import Intent


class IntentProvider(ABC):

    @abstractmethod
    def extract_intent(
        self,
        query: str,
    ) -> Intent:
        pass