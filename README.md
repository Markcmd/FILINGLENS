# FilingLens

Ask questions about SEC filings (10-K/10-Q) and get answers with exact citations back to the filing text — so every AI output is verifiable.

**Status: in progress.** Phase 1 — the core RAG pipeline (`ingest → parse → chunk → embed → retrieve → answer with citations`) over Apple, Microsoft, and Nvidia 10-Ks — is complete and runs fully local (sentence-transformers + Ollama + ChromaDB). No API keys, no cloud.

Every answer cites exact character offsets into a specific SEC filing, so every claim is checkable against the source — retrieval *and* verification, not just generation.

## Setup

Requires Python 3.10+ and [Ollama](https://ollama.com) with a model pulled (`ollama pull llama3.2`).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                        # full suite, no network/model/Ollama needed
```

## Usage

```bash
# 1. Build the index (downloads 9 10-Ks from SEC EDGAR, ~1 min each step)
python -m filinglens.ingest
python -m filinglens.parse
python -m filinglens.chunk
python -m filinglens.embed

# 2. Ask questions
python -m filinglens.cli "What are Apple's supply chain risks?" --ticker AAPL
python -m filinglens.cli "segment revenue" --retrieve-only   # debug retrieval

# 3. Or serve the HTTP API (interactive docs at localhost:8000/docs)
uvicorn filinglens.api:app

# 4. Measure quality against the golden Q&A set
python -m filinglens.eval             # retrieval metrics
python -m filinglens.eval --with-llm  # + answer quality
```

## Evaluation

A golden Q&A set (`eval/golden_qa.jsonl`, 15 questions across the three companies) measures retrieval and answer quality separately — run `python -m filinglens.eval [--with-llm]`.

Baseline (2026-07-08, all-MiniLM-L6-v2 + llama3.2, fully local):

| Metric | Score |
|---|---|
| Retrieval hit@6 | 87% |
| Retrieval MRR | 0.76 |
| Answer pass rate (llama3.2) | 47% |

Several answer failures occur on questions where retrieval ranked the correct chunk #1 — the bottleneck is the small local model's generation (dropped citations, missed synthesis), not retrieval. The LLM sits behind a provider abstraction, so stronger models can be swapped in to move that number.

## Roadmap

1. **Core RAG slice (Python)** — EDGAR ingestion, section-aware chunking, local embeddings, cited answers via CLI/API *(current)*
2. **Storage layer** — MongoDB for raw filings, Postgres + pgvector for chunks/embeddings
3. **React/TypeScript UI** — clickable citations highlighting source passages
4. **Extractor + XBRL verification** — extracted financials checked against EDGAR ground truth
5. **Agent + audit trail** — multi-step analysis with per-step auditability
6. **AWS deploy** — live, with CI

Tests ship with every phase: pytest/Vitest for correctness plus a golden Q&A eval set for answer quality.
