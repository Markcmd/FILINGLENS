"""Embed chunks and index them in ChromaDB.

Embeddings map text to vectors where similar meaning lands nearby, so a
question can find relevant chunks even without shared keywords. ChromaDB
stores the vectors (persisted in .chroma/) and answers nearest-neighbor
queries; every hit carries the chunk's citation metadata.

The Embedder protocol keeps the model swappable: local sentence-transformers
today, a cloud embedding API later, without touching the indexing code.

Run: python -m filinglens.embed
"""

from __future__ import annotations

import json
from typing import Protocol

from filinglens.config import CHUNKS_DIR, ROOT_DIR

CHROMA_DIR = ROOT_DIR / ".chroma"
COLLECTION_NAME = "filings"
EMBED_MODEL = "all-MiniLM-L6-v2"  # 384-dim, ~80MB, fast on CPU
BATCH_SIZE = 64

# Chunk fields stored as Chroma metadata — everything a citation needs.
METADATA_FIELDS = (
    "ticker",
    "fiscal_year",
    "item",
    "item_title",
    "char_start",
    "char_end",
    "source_url",
)


class Embedder(Protocol):
    """Anything that can turn texts into vectors."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class LocalEmbedder:
    """sentence-transformers embedder (lazy import: tests don't need it)."""

    def __init__(self, model_name: str = EMBED_MODEL):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).tolist()


def get_collection(client=None):
    """The 'filings' collection, cosine-similarity space."""
    import chromadb

    if client is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(CHUNKS_DIR.glob("*/*.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def index_chunks(chunks: list[dict], embedder: Embedder, collection) -> int:
    """Embed and upsert chunks in batches; returns collection size.

    upsert (insert-or-overwrite by id) makes re-indexing idempotent.
    """
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        collection.upsert(
            ids=[c["id"] for c in batch],
            embeddings=embedder.embed_texts(texts),
            documents=texts,
            metadatas=[{k: c[k] for k in METADATA_FIELDS} for c in batch],
        )
    return collection.count()


def main():
    chunks = load_chunks()
    print(f"loaded {len(chunks)} chunks from {CHUNKS_DIR}")
    total = index_chunks(chunks, LocalEmbedder(), get_collection())
    print(f"indexed into {CHROMA_DIR / COLLECTION_NAME!s}: {total} vectors")


if __name__ == "__main__":
    main()
