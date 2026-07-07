# FilingLens — Plan

> Working agreement: each step is designed → discussed → approved → implemented. No step starts before the previous one is approved. Every step gets a LOG.md entry.

## Project scope (approved 2026-07-06)
**FilingLens** — ask questions about SEC filings (10-K/10-Q), get answers with exact citations back to the filing text, so every AI output is verifiable. Mirrors Finpilot's core pitch: retrieval + verification/auditability for finance.

**Mark's goal:** practice unfamiliar knowledge (all of: RAG, agents/verification, React/TS, Postgres/AWS, MongoDB) and show he can learn and implement real things. Fuller project — continued after the Jul 10 application deadline; application mentions it as in-progress with repo link.

## Status legend
`[ ]` not started · `[~]` in discussion · `[>]` approved, in progress · `[x]` done

## Steps

- [x] 1. Define project scope & goals — approved 2026-07-06
- [>] 2. **Phase 1 (by Jul 10) — core RAG slice (Python):** download filings from SEC EDGAR, chunk + embed, CLI or minimal API answering questions with cited passages. Includes test setup: pytest from day one, unit tests for chunking/parsing, plus a small golden Q&A eval set to measure retrieval quality. Mentionable in application.
- [ ] 3. **Phase 2 — storage layer:** MongoDB for raw/parsed filing documents (semi-structured), Postgres + pgvector for chunks, embeddings, citations, Q&A history. Tests: integration tests against real local DBs.
- [ ] 4. **Phase 3 — React/TypeScript UI:** question box, answer view with clickable citations highlighting source passages. Tests: Vitest + React Testing Library for components.
- [ ] 5. **Phase 4 — extractor + XBRL verification:** LLM extracts key financials (revenue, net income, EPS…) from filing text → verify against XBRL ground truth (EDGAR companyfacts API) → per-figure verdict (match / mismatch / not found) + accuracy scorecard. Q&A answers auto-verify numeric claims. Tests: extraction accuracy measured against XBRL across all ingested filings.
- [ ] 6. **Phase 5 — agent + audit trail:** multi-step agent (e.g. compare risk factors across years) with per-step audit trail; agent can call the Phase 4 verifier as a tool. Tests: extend golden eval set to agent tasks.
- [ ] 7. **Phase 6 — AWS deploy:** get it live, with tests running in CI (GitHub Actions) before deploy.

## Phase 1 sub-steps (approved 2026-07-07)

- [x] 1.1 Scaffold — pyproject, src/ layout, config.py, pytest smoke tests (2026-07-07)
- [x] 1.2 Ingest — EDGAR client downloading AAPL/MSFT/NVDA 10-Ks, cached to `data/raw/` (2026-07-07; Mark to run `python -m filinglens.ingest` locally)
- [ ] 1.3 Parse + chunk — section-aware item splitting, ~600-token chunks with citation metadata
- [ ] 1.4 Embed + index — sentence-transformers → ChromaDB
- [ ] 1.5 Retrieve + answer — provider abstraction, Ollama answers with citations, CLI
- [ ] 1.6 Golden Q&A eval set — `eval/golden_qa.jsonl` + retrieval scoring
- [ ] 1.7 FastAPI wrapper — minimal `/ask` endpoint

## Phase 1 design (approved 2026-07-06)
Pipeline: `ingest → parse → chunk → embed → retrieve → answer with citations`

- **Data:** 10-Ks for Apple, Microsoft, Nvidia from SEC EDGAR free API (User-Agent header required)
- **Chunking:** section-aware (10-K items), ~600-token chunks with overlap; metadata per chunk (company, year, item, char offsets) = the citation
- **AI:** fully local/free — sentence-transformers for embeddings, Ollama for answers; provider behind an abstraction layer so cloud APIs can be swapped in later
- **Vector store:** ChromaDB locally; migrates to Postgres/pgvector in Phase 2
- **Layout:** `src/filinglens/` (ingest, chunk, embed, retrieve, answer), `tests/`, `eval/golden_qa.jsonl`
- **Interface:** CLI first, FastAPI at end of Phase 1
- **Repo:** GitHub, public, meaningful commit history

## Testing principle
Tests are not a separate phase — every phase ships with its own tests. Two kinds throughout: conventional tests (pytest/Vitest) for code correctness, and a golden Q&A eval set for AI answer quality — the latter mirrors Finpilot's "accuracy is non-negotiable."

## Decisions
| # | Decision | Date | Log ref |
|---|----------|------|---------|
| 1 | Project = SEC filing Q&A with verifiable citations; phased to cover all unfamiliar areas | 2026-07-06 | Log 2026-07-06 |
| 2 | Use both MongoDB (raw filing docs) and Postgres/pgvector (relational + vectors) — legitimate split, covers full Finpilot stack | 2026-07-06 | Log 2026-07-06 |
