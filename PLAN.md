# FilingLens — Plan

> Working agreement: each step is designed → discussed → approved → implemented. No step starts before the previous one is approved. Every step gets a LOG.md entry.

## Project scope (approved 2026-07-06)
**FilingLens** — ask questions about SEC filings (10-K/10-Q), get answers with exact citations back to the filing text, so every AI output is verifiable. Mirrors Finpilot's core pitch: retrieval + verification/auditability for finance.

**Mark's goal:** practice unfamiliar knowledge (all of: RAG, agents/verification, React/TS, Postgres/AWS, MongoDB) and show he can learn and implement real things. Fuller project — continued after the Jul 10 application deadline; application mentions it as in-progress with repo link.

## Status legend
`[ ]` not started · `[~]` in discussion · `[>]` approved, in progress · `[x]` done

## Steps

- [x] 1. Define project scope & goals — approved 2026-07-06
- [x] 2. **Phase 1 — core RAG slice (Python), complete 2026-07-11:** download filings from SEC EDGAR, chunk + embed, CLI or minimal API answering questions with cited passages. Includes test setup: pytest from day one, unit tests for chunking/parsing, plus a small golden Q&A eval set to measure retrieval quality. Mentionable in application.
- [~] 3. **Phase 2 — storage layer:** MongoDB for raw/parsed filing documents (semi-structured), Postgres + pgvector for chunks, embeddings, citations, Q&A history. Tests: integration tests against real local DBs. *Design discussed 2026-07-13; implementation gated on Phase 1 self-test retest ≥70% with no Tier-1 zeros (baseline 27.5%, 2026-07-13).*
- [ ] 4. **Phase 3 — React/TypeScript UI:** question box, answer view with clickable citations highlighting source passages. Tests: Vitest + React Testing Library for components.
- [ ] 5. **Phase 4 — extractor + XBRL verification:** LLM extracts key financials (revenue, net income, EPS…) from filing text → verify against XBRL ground truth (EDGAR companyfacts API) → per-figure verdict (match / mismatch / not found) + accuracy scorecard. Q&A answers auto-verify numeric claims. Tests: extraction accuracy measured against XBRL across all ingested filings.
- [ ] 6. **Phase 5 — agent + audit trail:** multi-step agent (e.g. compare risk factors across years) with per-step audit trail; agent can call the Phase 4 verifier as a tool. Tests: extend golden eval set to agent tasks.
- [ ] 7. **Phase 6 — AWS deploy:** get it live, with tests running in CI (GitHub Actions) before deploy.

## Phase 1 sub-steps (approved 2026-07-07)

- [x] 1.1 Scaffold — pyproject, src/ layout, config.py, pytest smoke tests (2026-07-07)
- [x] 1.2 Ingest — EDGAR client downloading AAPL/MSFT/NVDA 10-Ks, cached to `data/raw/` (2026-07-07; Mark to run `python -m filinglens.ingest` locally)
- [x] 1.3 Parse + chunk — section-aware item splitting, ~600-token chunks with citation metadata (2026-07-07; 973 chunks across 9 filings, offsets verified)
- [x] 1.4 Embed + index — sentence-transformers → ChromaDB (2026-07-07; Mark ran locally, 973 vectors indexed)
- [x] 1.5 Retrieve + answer — provider abstraction, Ollama answers with citations, CLI (2026-07-08; Mark ran CLI, cited answer verified; 29 tests pass locally)
- [x] 1.6 Golden Q&A eval set (2026-07-08; baseline: hit@6 87%, MRR 0.76, answers 47% — see README)
- [x] 1.7 FastAPI wrapper — `/ask`, `/search`, `/health` (2026-07-11; Mark verified via /docs — cited answer returned end-to-end)

## Phase 2 sub-steps (proposed 2026-07-13, pending approval)

- [ ] 2.1 Infra + config — docker-compose.yml (MongoDB + pgvector Postgres), connection settings in config.py, DB smoke tests
- [ ] 2.2 Mongo filing store — `FilingStore` protocol; ingest/parse write raw HTML + canonical text + EDGAR metadata to Mongo; upsert by accession number (idempotent); integration tests
- [ ] 2.3 Postgres schema + migrations — `filings`, `chunks` (with `vector(384)` column + citation metadata), `qa_history` tables; hand-written SQL migrations with a tiny runner
- [ ] 2.4 PgVector store — vector-store operations (upsert, cosine top-k via `<=>`, metadata filters) on Postgres; index all chunks
- [ ] 2.5 Eval parity gate — golden eval vs pgvector must match Chroma baseline (hit@6 87% / MRR 0.76) before Chroma is retired
- [ ] 2.6 Q&A history — persist every /ask (question, answer, citations, model, latency); `GET /history`
- [ ] 2.7 Phase close — README/docs update; Phase 2 study digest + 20-question self-test (outside repo)

## Phase 2 design (discussed 2026-07-13; decisions 3–5 made)

- **Data split:** MongoDB = source of truth for filings (raw HTML, parsed canonical text, submission metadata; document-shaped). Postgres = chunks, embeddings (pgvector), citations, Q&A history (relational + vectors). `data/raw/` demoted to download cache.
- **Cross-store invariant:** `text[char_start:char_end] == chunk.text` now spans stores — Postgres chunk rows point into Mongo canonical texts; integration tests verify it end-to-end.
- **DB access:** raw SQL via psycopg 3 (no ORM) — maximum transparency, every query defensible in interviews; ORM can be layered later.
- **Local runtime:** Docker Compose (reused in Phase 6 AWS story).
- **Testing:** unit tests keep fakes; integration tests are pytest-marked and skip cleanly when DBs aren't running.
- **Understanding checkpoints (per step, plain-language):** why two DBs; idempotent upsert-by-accession; DDL/keys/migrations; what HNSW and the `<=>` operator do; why eval parity proves the migration.

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
| 3 | Postgres access via raw SQL (psycopg 3), no ORM — understanding over buzzwords; ORM can come later | 2026-07-13 | Log 2026-07-13 |
| 4 | Local DBs via Docker Compose — standard practice, rehearses Phase 6 deploy | 2026-07-13 | Log 2026-07-13 |
| 5 | Mongo is source of truth for filings; `data/raw/` becomes a download cache — honest architecture, defensible in interviews | 2026-07-13 | Log 2026-07-13 |
