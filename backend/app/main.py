import logging
from contextlib import asynccontextmanager
from typing import Union

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
from app.trace import DebugSearchResponse, PipelineTrace, stage

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


@app.get("/search", response_model=Union[DebugSearchResponse, SearchResponse])
async def search(query: str, debug: bool = False):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="query no puede estar vacío")

    # Con debug=true se captura la traza del pipeline para la UI de
    # desarrollo. Con debug=false (default) trace es None y el pipeline
    # se comporta exactamente igual que siempre.
    trace = PipelineTrace() if debug else None

    try:
        with stage(trace, "intent_extraction"):
            intent = extract_intent(query)
    except IntentExtractionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # build_search_context ya devuelve los candidatos reranqueados
    # (rerank en dos etapas: preselección barata -> enrich -> rerank final)
    _query_profile, results = await build_search_context(intent, trace=trace)

    try:
        with stage(trace, "generation"):
            answer, grounded, warnings = generate_answer(query, results)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    settings = get_settings()

    response_data = dict(
        query=query,
        intent=intent,
        results=results[: settings.max_results_to_return],
        answer=answer,
        grounded=grounded,
        warnings=warnings,
    )

    if trace is not None:
        return DebugSearchResponse(**response_data, trace=trace)

    return SearchResponse(**response_data)
