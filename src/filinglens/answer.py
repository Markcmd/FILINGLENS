"""Generate cited answers from retrieved chunks.

Grounding rules in the prompt are the anti-hallucination stance: the model
may ONLY use the numbered excerpts, must cite [n] for every claim, and must
say it can't find an answer rather than guess. Every [n] marker in the
output is resolved back to the exact chunk (filing, item, char offsets), so
any claim can be checked against the source text.

The LLM protocol mirrors Embedder: local Ollama today, any API later.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

import requests

from filinglens.retrieve import Hit, retrieve

NOT_FOUND = "Not found in the provided filings."

PROMPT_TEMPLATE = """You are FilingLens, an assistant that answers questions about SEC filings.

Rules:
- Use ONLY the numbered excerpts below. No outside knowledge.
- Cite the excerpt number in square brackets, like [1] or [2], after every claim.
- If the excerpts do not contain the answer, reply exactly: {not_found}
- Be concise and factual.

Excerpts:
{excerpts}

Question: {question}

Answer:"""


class LLM(Protocol):
    """Anything that can complete a prompt."""

    def generate(self, prompt: str) -> str: ...


class OllamaLLM:
    """Local Ollama server (https://ollama.com), default model llama3.2."""

    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt: str) -> str:
        resp = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},  # deterministic, factual mode
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()


@dataclass(frozen=True)
class Citation:
    marker: int  # the [n] used in the answer text
    chunk_id: str
    ticker: str
    fiscal_year: str
    item: str
    item_title: str
    char_start: int
    char_end: int
    source_url: str


@dataclass(frozen=True)
class Answer:
    question: str
    text: str
    citations: list[Citation]  # only the excerpts the answer actually cited
    hits: list[Hit]  # everything that was retrieved (for debugging)


def format_excerpt(n: int, hit: Hit) -> str:
    return (
        f"[{n}] {hit.ticker} FY{hit.fiscal_year} 10-K, "
        f"Item {hit.item} ({hit.item_title}):\n{hit.text}"
    )


def build_prompt(question: str, hits: list[Hit]) -> str:
    excerpts = "\n\n".join(format_excerpt(i + 1, h) for i, h in enumerate(hits))
    return PROMPT_TEMPLATE.format(
        not_found=NOT_FOUND, excerpts=excerpts, question=question
    )


def cited_markers(text: str, n_hits: int) -> list[int]:
    """Distinct [n] markers in the answer that map to a real excerpt."""
    seen = []
    for m in re.findall(r"\[(\d+)\]", text):
        n = int(m)
        if 1 <= n <= n_hits and n not in seen:
            seen.append(n)
    return seen


def answer_question(
    question: str,
    k: int = 6,
    ticker: str | None = None,
    year: str | int | None = None,
    llm: LLM | None = None,
    embedder=None,
    collection=None,
) -> Answer:
    hits = retrieve(
        question, k=k, ticker=ticker, year=year, embedder=embedder, collection=collection
    )
    if not hits:
        return Answer(question, NOT_FOUND, [], [])

    text = (llm or OllamaLLM()).generate(build_prompt(question, hits))

    citations = []
    for n in cited_markers(text, len(hits)):
        h = hits[n - 1]
        citations.append(
            Citation(
                marker=n,
                chunk_id=h.id,
                ticker=h.ticker,
                fiscal_year=h.fiscal_year,
                item=h.item,
                item_title=h.item_title,
                char_start=h.char_start,
                char_end=h.char_end,
                source_url=h.source_url,
            )
        )
    return Answer(question, text, citations, hits)
