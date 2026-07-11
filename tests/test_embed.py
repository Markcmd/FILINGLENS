"""Indexing tests with a fake embedder + in-memory Chroma (no model needed)."""

import pytest

chromadb = pytest.importorskip("chromadb")

from filinglens.embed import METADATA_FIELDS, index_chunks


class FakeEmbedder:
    """Deterministic 8-dim vectors from byte content — similar text, similar vector."""

    def embed_texts(self, texts):
        vecs = []
        for t in texts:
            v = [1e-9] * 8
            for i, b in enumerate(t.encode()):
                v[i % 8] += b
            norm = sum(x * x for x in v) ** 0.5
            vecs.append([x / norm for x in v])
        return vecs


def make_chunk(i, text):
    return {
        "id": f"TEST_2025_item1_{i:03d}",
        "text": text,
        "ticker": "TEST",
        "fiscal_year": "2025",
        "item": "1",
        "item_title": "Business",
        "char_start": i * 100,
        "char_end": i * 100 + len(text),
        "source_url": "https://example.com/f.htm",
    }


@pytest.fixture
def collection():
    client = chromadb.EphemeralClient()
    return client.get_or_create_collection("test", metadata={"hnsw:space": "cosine"})


def test_index_stores_text_and_citation_metadata(collection):
    chunks = [make_chunk(0, "apple banana"), make_chunk(1, "cherry date")]
    assert index_chunks(chunks, FakeEmbedder(), collection) == 2
    got = collection.get(ids=["TEST_2025_item1_000"])
    assert got["documents"] == ["apple banana"]
    assert set(METADATA_FIELDS) <= set(got["metadatas"][0])
    assert got["metadatas"][0]["char_end"] == 12


def test_reindexing_is_idempotent(collection):
    chunks = [make_chunk(i, f"text number {i}") for i in range(5)]
    index_chunks(chunks, FakeEmbedder(), collection)
    index_chunks(chunks, FakeEmbedder(), collection)  # run twice
    assert collection.count() == 5


def test_query_finds_planted_nearest_chunk(collection):
    emb = FakeEmbedder()
    chunks = [
        make_chunk(0, "zzzzzzzz completely different bytes here"),
        make_chunk(1, "revenue increased due to strong product demand"),
    ]
    index_chunks(chunks, emb, collection)
    # Query with (nearly) the same text as chunk 1 -> it must rank first
    q = emb.embed_texts(["revenue increased due to strong product demand!"])
    res = collection.query(query_embeddings=q, n_results=1)
    assert res["ids"][0][0] == "TEST_2025_item1_001"
