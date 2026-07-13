from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Intent(BaseModel):
    """
    Salida validada de extract_intent(). Si el LLM devuelve un JSON con
    claves faltantes o mal tipadas, esto falla aquí con un error claro,
    en vez de reventar 3 módulos después con un KeyError críptico.
    """
    intent: str
    reference_books: List[str] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    semantic_description: str

    @field_validator("search_queries")
    @classmethod
    def at_least_one_query(cls, v):
        if not v:
            raise ValueError("search_queries no puede estar vacío")
        return v


class Book(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    edition_count: int = 0
    subjects: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    ratings_average: Optional[float] = None
    ratings_count: Optional[int] = None
    readinglog_count: Optional[int] = None
    key: Optional[str] = None

    # Campos que se completan durante el pipeline (no vienen de Open Library)
    profile: Optional[str] = None
    semantic_score: Optional[float] = None

    model_config = {"extra": "allow"}


class SearchResponse(BaseModel):
    query: str
    intent: Intent
    results: List[Book]
    answer: str
    grounded: bool
    warnings: List[str] = Field(default_factory=list)
