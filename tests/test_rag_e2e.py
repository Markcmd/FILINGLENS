"""End-to-end RAG pipeline test: index -> retrieve -> answer, all fakes.

Needs chromadb but no embedding model and no Ollama, so it runs on any
machine with the project installed (and in CI later).
"""

import pytest

chromadb = pytest.importorskip("chromadb")

from filinglens.answer import NOT_FOUND, answer_question
from filinglens.embed import index_chunks
from filinglens.retrieve import retrieve
from test_embed import FakeEmbedder, make_chunk


class FakeLLM:
    """Returns a canned cited answer; records the prompt it was given."""

    def __init__(self, response="Revenue increased due to product demand [1]."):
        self.response = response
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.response


@pytest.fixture
def collection():
    client = chromadb.EphemeralClient()
    col = client.get_or_create_collection("e2e", metadata={"hnsw:space": "cosine"})
    chunks = [
        make_chunk(0, "revenue increased due to strong product demand this year"),
        make_chunk(1, "litigation risks include patent disputes in many regions"),
    ]
    other = dict(make_chunk(2, "totally unrelated other company text"), ticker="OTHR")
    index_chunks(chunks + [other], FakeEmbedder(), col)
    return col


def test_retrieve_ranks_relevant_chunk_first(collection):
    hits = retrieve(
        "revenue increased due to strong product demand this year!",
        k=2,
        embedder=FakeEmbedder(),
        collection=collection,
    )
    assert hits[0].id == "TEST_2025_item1_000"
    assert hits[0].score >= hits[1].score
    assert hits[0].source_url  # citation metadata came back with the hit


def test_retrieve_ticker_filter_excludes_other_companies(collection):
    hits = retrieve(
        "anything at all",
        k=5,
        ticker="TEST",
        embedder=FakeEmbedder(),
        collection=collection,
    )
    assert hits and all(h.ticker == "TEST" for h in hits)


def test_answer_resolves_citations_to_chunks(collection):
    llm = FakeLLM("Revenue increased due to product demand [1].")
    result = answer_question(
        "why did revenue increase",
        k=2,
        llm=llm,
        embedder=FakeEmbedder(),
        collection=collection,
    )
    # The prompt the LLM saw contained the excerpts and grounding rules
    assert "ONLY the numbered excerpts" in llm.prompts[0]
    # [1] resolved to the first retrieved chunk, with offsets and URL intact
    assert len(result.citations) == 1
    c = result.citations[0]
    assert c.marker == 1 and c.chunk_id == result.hits[0].id
    assert c.source_url == "https://example.com/f.htm"


def test_no_hits_returns_not_found_without_calling_llm(collection):
    llm = FakeLLM()
    result = answer_question(
        "anything",
        ticker="NOSUCH",  # filter matches nothing -> no hits
        llm=llm,
        embedder=FakeEmbedder(),
        collection=collection,
    )
    assert result.text == NOT_FOUND
    assert result.citations == [] and llm.prompts == []
