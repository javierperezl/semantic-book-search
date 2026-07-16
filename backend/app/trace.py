"""
Traza opcional del pipeline para la UI de desarrollo (/search?debug=true).

La captura es 100% aditiva: todas las funciones del pipeline aceptan
trace=None y con ese default se comportan exactamente igual que antes.
La traza solo se construye cuando el endpoint recibe debug=true.
"""

import time
from contextlib import contextmanager
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import SearchResponse


class StageTiming(BaseModel):
    stage: str
    duration_ms: float


class TraceQueryResult(BaseModel):
    """Resultado de una search query individual contra Open Library."""

    query: str
    returned: int = 0
    failed: bool = False


class TraceReferenceBook(BaseModel):
    """Qué libro de referencia pidió el intent y qué se encontró realmente."""

    requested: str
    found: bool = False
    title: Optional[str] = None
    author: Optional[str] = None
    key: Optional[str] = None


class TraceCheapCandidate(BaseModel):
    """Candidato tras el rerank barato (etapa 1, profile parcial)."""

    key: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    rank: int
    score: float
    selected_for_enrichment: bool


class TraceFinalCandidate(BaseModel):
    """
    Candidato tras el rerank final (etapa 3), con su posición en la etapa
    barata para poder ver cuánto movió el enriquecimiento al ranking.
    """

    key: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    final_rank: int
    final_score: float
    cheap_rank: Optional[int] = None
    cheap_score: Optional[float] = None
    description_added: bool = False


class PipelineTrace(BaseModel):
    query_profile: Optional[str] = None
    reference_book: Optional[TraceReferenceBook] = None
    queries: List[TraceQueryResult] = Field(default_factory=list)
    total_candidates: int = 0
    cheap_rerank: List[TraceCheapCandidate] = Field(default_factory=list)
    final_rerank: List[TraceFinalCandidate] = Field(default_factory=list)
    timings: List[StageTiming] = Field(default_factory=list)


class DebugSearchResponse(SearchResponse):
    """Respuesta de /search?debug=true: lo mismo que producción + la traza."""

    trace: PipelineTrace


@contextmanager
def stage(trace: Optional[PipelineTrace], name: str):
    """
    Mide la duración de una etapa y la registra en la traza.
    Con trace=None no mide nada (modo producción, costo cero).
    """
    if trace is None:
        yield
        return

    start = time.perf_counter()
    try:
        yield
    finally:
        trace.timings.append(
            StageTiming(
                stage=name,
                duration_ms=round((time.perf_counter() - start) * 1000, 1),
            )
        )
