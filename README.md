# FilingLens

Ask questions about SEC filings (10-K/10-Q) and get answers with exact citations back to the filing text — so every AI output is verifiable.

**Status: in progress.** Currently building Phase 1: the core RAG pipeline (`ingest → parse → chunk → embed → retrieve → answer with citations`) over Apple, Microsoft, and Nvidia 10-Ks, running fully local (sentence-transformers + Ollama + ChromaDB).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Roadmap

1. **Core RAG slice (Python)** — EDGAR ingestion, section-aware chunking, local embeddings, cited answers via CLI/API *(current)*
2. **Storage layer** — MongoDB for raw filings, Postgres + pgvector for chunks/embeddings
3. **React/TypeScript UI** — clickable citations highlighting source passages
4. **Extractor + XBRL verification** — extracted financials checked against EDGAR ground truth
5. **Agent + audit trail** — multi-step analysis with per-step auditability
6. **AWS deploy** — live, with CI

Tests ship with every phase: pytest/Vitest for correctness plus a golden Q&A eval set for answer quality.
