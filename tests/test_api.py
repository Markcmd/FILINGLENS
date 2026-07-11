"""API tests: TestClient + fakes; no model, no Ollama, in-memory Chroma."""

import pytest

pytest.importorskip("fastapi")
chromadb = pytest.importorskip("chromadb")

from fastapi.testclient import TestClient

from filinglens.api import app, get_chroma, get_embedder, get_llm
from filinglens.embed import index_chunks
from test_embed import FakeEmbedder, make_chunk
from test_rag_e2e import FakeLLM


@pytest.fixture
def client():
    col = chromadb.EphemeralClient().get_or_create_collection(
        "api", metadata={"hnsw:space": "cosine"}
    )
    index_chunks(
        [
            make_chunk(0, "revenue increased due to strong product demand this year"),
            make_chunk(1, "litigation risks include patent disputes in many regions"),
        ],
        FakeEmbedder(),
        col,
    )
    app.dependency_overrides[get_embedder] = lambda: FakeEmbedder()
    app.dependency_overrides[get_chroma] = lambda: col
    app.dependency_overrides[get_llm] = lambda: FakeLLM(
        "Revenue increased due to product demand [1]."
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_reports_chunk_count(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "chunks": 2}


def test_ask_returns_answer_with_resolved_citations(client):
    r = client.post("/ask", json={"question": "why did revenue increase", "k": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"].endswith("[1].")
    assert len(body["citations"]) == 1
    c = body["citations"][0]
    assert c["marker"] == 1
    assert c["chunk_id"].startswith("TEST_2025_item1_")
    assert c["source_url"] == "https://example.com/f.htm"


def test_search_returns_scored_hits(client):
    r = client.get("/search", params={"q": "patent disputes litigation", "k": 2})
    assert r.status_code == 200
    hits = r.json()
    assert len(hits) == 2
    assert hits[0]["id"] == "TEST_2025_item1_001"  # litigation chunk ranks first
    assert hits[0]["score"] >= hits[1]["score"]


def test_validation_rejects_bad_requests(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "ok?", "k": 0}).status_code == 422
    assert client.get("/search", params={"q": "hi", "k": 99}).status_code == 422
