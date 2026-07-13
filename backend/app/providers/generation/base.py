from abc import ABC, abstractmethod


class GenerationProvider(ABC):

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        pass