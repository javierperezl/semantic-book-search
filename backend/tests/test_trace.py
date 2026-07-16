"""
Tests del modo debug (?debug=true) y de que el modo normal queda intacto.
"""

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.models import Intent
from app.openlibrary import multi_search
from app.trace import PipelineTrace
from app.retriever import build_search_context


FAKE_INTENT = Intent(
    intent="recommendation",
    reference_books=[],
    search_queries=["mystery venice"],
    semantic_description="a mystery novel set in venice",
)


def _fake_rerank(query_profile: str, candidates: list[dict], use_cache: bool = True):
    """Asigna scores decrecientes deterministas, sin cargar embeddings."""
    for i, candidate in enumerate(candidates):
        candidate["semantic_score"] = 1.0 - i * 0.1
    return candidates


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main_module, "extract_intent", lambda q: FAKE_INTENT)
    monkeypatch.setattr(
        main_module, "generate_answer", lambda q, r: ("an answer", True, [])
    )
    return TestClient(app)


def _mock_openlibrary():
    respx.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "docs": [
                    {
                        "title": "Book A",
                        "author_name": ["Author A"],
                        "key": "/works/OL1W",
                        "subject": ["Mystery"],
                    },
                    {
                        "title": "Book B",
                        "author_name": ["Author B"],
                        "key": "/works/OL2W",
                        "subject": ["Crime"],
                    },
                ]
            },
        )
    )
    respx.get(url__regex=r"https://openlibrary\.org/works/.*\.json").mock(
        return_value=httpx.Response(
            200, json={"description": "A great mystery.", "subjects": ["Venice"]}
        )
    )


@respx.mock
def test_search_normal_no_incluye_trace(client, monkeypatch):
    monkeypatch.setattr("app.retriever.rerank", _fake_rerank)
    _mock_openlibrary()

    response = client.get("/search", params={"query": "a mystery in venice"})

    assert response.status_code == 200
    body = response.json()
    assert "trace" not in body
    assert body["answer"] == "an answer"


@respx.mock
def test_search_debug_incluye_trace_poblada(client, monkeypatch):
    monkeypatch.setattr("app.retriever.rerank", _fake_rerank)
    _mock_openlibrary()

    response = client.get(
        "/search", params={"query": "a mystery in venice", "debug": "true"}
    )

    assert response.status_code == 200
    trace = response.json()["trace"]

    # Etapas cronometradas (las del retriever + intent y generation)
    stage_names = {t["stage"] for t in trace["timings"]}
    assert "intent_extraction" in stage_names
    assert "openlibrary_search" in stage_names
    assert "cheap_rerank" in stage_names
    assert "final_rerank" in stage_names
    assert "generation" in stage_names

    # Retrieval por query
    assert trace["queries"] == [
        {"query": "mystery venice", "returned": 2, "failed": False}
    ]
    assert trace["total_candidates"] == 2

    # Rerank barato: todos los candidatos con rank y flag de selección
    assert len(trace["cheap_rerank"]) == 2
    assert trace["cheap_rerank"][0]["rank"] == 1
    assert trace["cheap_rerank"][0]["selected_for_enrichment"] is True

    # Rerank final: cruza con la etapa barata
    assert len(trace["final_rerank"]) == 2
    first = trace["final_rerank"][0]
    assert first["final_rank"] == 1
    assert first["cheap_rank"] is not None
    assert first["description_added"] is True

    assert trace["query_profile"]


@pytest.mark.asyncio
@respx.mock
async def test_multi_search_registra_stats_por_query():
    respx.get(
        "https://openlibrary.org/search.json", params={"q": "ok query"}
    ).mock(
        return_value=httpx.Response(
            200, json={"docs": [{"title": "Book A", "key": "/works/OL1W"}]}
        )
    )
    respx.get(
        "https://openlibrary.org/search.json", params={"q": "bad query"}
    ).mock(return_value=httpx.Response(500))

    trace = PipelineTrace()
    results = await multi_search(["ok query", "bad query"], trace=trace)

    assert len(results) == 1
    assert len(trace.queries) == 2
    assert trace.queries[0].returned == 1
    assert trace.queries[0].failed is False
    assert trace.queries[1].failed is True


@pytest.mark.asyncio
@respx.mock
async def test_build_search_context_sin_trace_no_cambia(monkeypatch):
    """El modo producción (trace=None) devuelve lo mismo de siempre."""
    monkeypatch.setattr("app.retriever.rerank", _fake_rerank)
    _mock_openlibrary()

    query_profile, results = await build_search_context(FAKE_INTENT)

    assert query_profile
    assert len(results) == 2
    assert all("semantic_score" in r for r in results)
