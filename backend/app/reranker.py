import logging

import numpy as np
from app.providers.embeddings.factory import (
    get_embedding_provider,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

# Cache simple en memoria de proceso: key de Open Library -> embedding.
# No es persistente entre reinicios ni compartida entre workers, pero evita
# recalcular embeddings de libros populares que aparecen en muchos requests.
_embedding_cache: dict[str, np.ndarray] = {}


def _embed_candidates(candidates: list[dict], use_cache: bool) -> np.ndarray:
    provider = get_embedding_provider()

    if not use_cache:
        # Usado en el pase "barato" (pre-enriquecimiento): el profile todavía
        # no tiene descripción/subjects completos, así que NO lo guardamos
        # bajo la key del libro — si lo hiciéramos, el pase final reutilizaría
        # por error este embedding incompleto en vez de recalcularlo.
        texts = [c["profile"] for c in candidates]
        return np.array(provider.encode(texts, normalize_embeddings=True))

    to_compute_idx = []
    to_compute_texts = []

    for i, candidate in enumerate(candidates):
        key = candidate.get("key")
        if key and key in _embedding_cache:
            continue
        to_compute_idx.append(i)
        to_compute_texts.append(candidate["profile"])

    if to_compute_texts:
        new_embeddings = provider.encode(to_compute_texts, normalize_embeddings=True)
        for idx, embedding in zip(to_compute_idx, new_embeddings):
            key = candidates[idx].get("key")
            if key:
                _embedding_cache[key] = embedding

    embeddings = []
    for candidate in candidates:
        key = candidate.get("key")
        if key and key in _embedding_cache:
            embeddings.append(_embedding_cache[key])
        else:
            # Libro sin key (raro) o cache falló: calcular al vuelo sin cachear
            embeddings.append(provider.encode(candidate["profile"], normalize_embeddings=True))

    return np.array(embeddings)


def rerank(query_profile: str, candidates: list[dict], use_cache: bool = True) -> list[dict]:
    """
    use_cache=False se usa para el rerank "barato" de preselección (antes de
    enriquecer con /works), donde el profile aún es parcial y no queremos que
    ese embedding quede cacheado bajo la key del libro.
    """
    if not candidates:
        return []

    provider = get_embedding_provider()

    query_embedding = provider.encode(query_profile, normalize_embeddings=True)
    candidate_embeddings = _embed_candidates(candidates, use_cache=use_cache)

    scores = np.dot(candidate_embeddings, query_embedding)

    for candidate, score in zip(candidates, scores):
        candidate["semantic_score"] = float(score)

    candidates.sort(key=lambda x: x["semantic_score"], reverse=True)

    return candidates
