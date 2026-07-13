import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.generator import GenerationError, generate_answer
from app.llm import IntentExtractionError, extract_intent
from app.models import SearchResponse
from app.providers.embeddings.factory import (
    get_embedding_provider,
)
from app.retriever import build_search_context

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Precarga el modelo de embeddings al iniciar el servidor
    get_embedding_provider()
    yield


app = FastAPI(
    title="Portafolio - Semantic Book Search",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Semantic Book Search"}


@app.get("/search", response_model=SearchResponse)
async def search(query: str):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="query no puede estar vacío")

    try:
        intent = extract_intent(query)
    except IntentExtractionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # build_search_context ya devuelve los candidatos reranqueados
    # (rerank en dos etapas: preselección barata -> enrich -> rerank final)
    _query_profile, results = await build_search_context(intent)

    try:
        answer, grounded, warnings = generate_answer(query, results)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    settings = get_settings()

    return SearchResponse(
        query=query,
        intent=intent,
        results=results[: settings.max_results_to_return],
        answer=answer,
        grounded=grounded,
        warnings=warnings,
    )
