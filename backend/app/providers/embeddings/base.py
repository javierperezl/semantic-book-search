from abc import ABC, abstractmethod

import numpy as np


class EmbeddingProvider(ABC):

    @abstractmethod
    def encode(
        self,
        texts: str | list[str],
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        pass