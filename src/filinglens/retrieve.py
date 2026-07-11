"""Semantic retrieval: question -> most relevant chunks with citations.

The question is embedded with the SAME model used to index the chunks
(vectors from different models live in different spaces and can't be
compared), then ChromaDB returns the nearest chunks. Optional ticker/year
filters use metadata so e.g. an Apple question never retrieves MSFT text.
"""

from __future__ import annotations

from dataclasses import dataclass

from filinglens.embed import Embedder, LocalEmbedder, get_collection


@dataclass(frozen=True)
class Hit:
    """One retrieved chunk plus everything needed to cite it."""

    id: str
    text: str
    ticker: str
    fiscal_year: str
    item: str
    item_title: str
    char_start: int
    char_end: int
    source_url: str
    score: float  # cosine similarity, 1.0 = identical direction


def build_where(ticker: str | None = None, year: str | int | None = None):
    """Chroma metadata filter; None when unfiltered."""
    clauses = []
    if ticker:
        clauses.append({"ticker": ticker.upper()})
    if year:
        clauses.append({"fiscal_year": str(year)})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def retrieve(
    question: str,
    k: int = 6,
    ticker: str | None = None,
    year: str | int | None = None,
    embedder: Embedder | None = None,
    collection=None,
) -> list[Hit]:
    embedder = embedder or LocalEmbedder()
    if collection is None:
        collection = get_collection()

    res = collection.query(
        query_embeddings=embedder.embed_texts([question]),
        n_results=k,
        where=build_where(ticker, year),
    )

    hits = []
    for i, chunk_id in enumerate(res["ids"][0]):
        meta = res["metadatas"][0][i]
        hits.append(
            Hit(
                id=chunk_id,
                text=res["documents"][0][i],
                ticker=meta["ticker"],
                fiscal_year=meta["fiscal_year"],
                item=meta["item"],
                item_title=meta["item_title"],
                char_start=meta["char_start"],
                char_end=meta["char_end"],
                source_url=meta["source_url"],
                score=1.0 - res["distances"][0][i],
            )
        )
    return hits
