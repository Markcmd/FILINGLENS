"""Split parsed filings into citation-ready chunks.

Each chunk is a contiguous span of the canonical text: `text[char_start:
char_end]` reproduces it exactly, which is what makes citations verifiable.
Paragraphs are packed into ~MAX_WORDS chunks with a one-paragraph overlap;
chunks never cross section boundaries.

Run: python -m filinglens.chunk
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from filinglens.config import CHUNKS_DIR, PARSED_DIR

MAX_WORDS = 500  # ~650 tokens for typical English text
MIN_WORDS = 20  # drop degenerate chunks (page numbers, stray headers)
OVERLAP_MAX_WORDS = 120  # only carry a paragraph into the next chunk if small


@dataclass(frozen=True)
class Chunk:
    id: str  # e.g. "AAPL_2025_item7A_002"
    text: str
    ticker: str
    fiscal_year: str
    item: str
    item_title: str
    char_start: int  # offsets into the filing's canonical text
    char_end: int
    source_url: str


def _paragraph_spans(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """(start, end) spans of non-empty paragraphs within text[start:end]."""
    spans = []
    for m in re.finditer(r"[^\n]+(?:\n[^\n]+)*", text[start:end]):
        spans.append((start + m.start(), start + m.end()))
    return spans


def _split_oversized(text: str, span: tuple[int, int]) -> list[tuple[int, int]]:
    """Hard-split a single paragraph longer than MAX_WORDS at word boundaries."""
    words = list(re.finditer(r"\S+", text[span[0] : span[1]]))
    pieces = []
    for i in range(0, len(words), MAX_WORDS):
        group = words[i : i + MAX_WORDS]
        pieces.append((span[0] + group[0].start(), span[0] + group[-1].end()))
    return pieces


def chunk_section(
    text: str, section: dict, ticker: str, fy: str, source_url: str
) -> list[Chunk]:
    spans: list[tuple[int, int]] = []
    for span in _paragraph_spans(text, section["char_start"], section["char_end"]):
        n_words = len(text[span[0] : span[1]].split())
        spans.extend(_split_oversized(text, span) if n_words > MAX_WORDS else [span])

    chunks: list[list[tuple[int, int]]] = []
    current: list[tuple[int, int]] = []
    count = 0
    for span in spans:
        n = len(text[span[0] : span[1]].split())
        if current and count + n > MAX_WORDS:
            chunks.append(current)
            # One-paragraph overlap, but only if that paragraph is small —
            # carrying a hard-split 500-word piece would double chunk sizes.
            last_words = len(text[current[-1][0] : current[-1][1]].split())
            if last_words <= OVERLAP_MAX_WORDS:
                current, count = [current[-1]], last_words
            else:
                current, count = [], 0
        current.append(span)
        count += n
    if current:
        chunks.append(current)

    out = []
    for seq, group in enumerate(chunks):
        start, end = group[0][0], group[-1][1]
        chunk_text = text[start:end]
        if len(chunk_text.split()) < MIN_WORDS:
            continue
        out.append(
            Chunk(
                id=f"{ticker}_{fy}_item{section['item']}_{seq:03d}",
                text=chunk_text,
                ticker=ticker,
                fiscal_year=fy,
                item=section["item"],
                item_title=section["title"],
                char_start=start,
                char_end=end,
                source_url=source_url,
            )
        )
    return out


def chunk_filing(parsed: dict) -> list[Chunk]:
    chunks = []
    for section in parsed["sections"]:
        chunks.extend(
            chunk_section(
                parsed["text"],
                section,
                parsed["ticker"],
                parsed["fiscal_year"],
                parsed["source_url"],
            )
        )
    return chunks


def chunk_all() -> int:
    """Chunk every parsed filing; write data/chunks/{ticker}/{fy}.jsonl."""
    total = 0
    for parsed_path in sorted(PARSED_DIR.glob("*/*.json")):
        parsed = json.loads(parsed_path.read_text())
        chunks = chunk_filing(parsed)
        out_path = CHUNKS_DIR / parsed["ticker"] / f"{parsed['fiscal_year']}.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            "\n".join(json.dumps(asdict(c)) for c in chunks) + "\n"
        )
        total += len(chunks)
        print(f"{parsed['ticker']} FY{parsed['fiscal_year']}: {len(chunks)} chunks")
    print(f"total: {total} chunks")
    return total


if __name__ == "__main__":
    chunk_all()
