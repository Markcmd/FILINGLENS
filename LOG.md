# FilingLens — Log

> Every step gets an entry: what was done, Mark's thoughts, Claude's suggestions, and the decision. Newest entry on top.

---

## 2026-07-07 — Step 1.2: EDGAR ingest (done)
**Done:** `src/filinglens/ingest.py` — submissions index → filter latest 3 10-Ks → download primary HTML doc to `data/raw/{ticker}/{fy}_10-K.htm` with a `.meta.json` sidecar (accession, dates, URL) that later becomes the citation source. Frozen `Filing` dataclass; pure `select_10ks()` for testability; caching (skip if downloaded); User-Agent + rate-limit politeness. `requests` added as first dependency. 5 new unit tests against a fake submissions index (filtering/ordering, accession normalization, URL construction, paths, cache-skip) — 9/9 pass. Commit `9630b59`.

**Mark's thoughts:** Approved design as proposed (latest 3 fiscal years, primary document only).

**Claude's suggestions:** Keep `select_10ks` pure (no I/O) so the core logic tests need no mocking; test cache-skip by passing `session=None` — if the cache is respected no HTTP attribute is ever touched. Caught own bug pre-commit: `ingest_all` collected only the last path per ticker.

**Decision:** Committed. Claude's sandbox can't reach sec.gov, so Mark runs `python -m filinglens.ingest` locally to pull the 9 filings. Next: design step 1.3 (parse + chunk).

---

## 2026-07-07 — Phase 1 kickoff + step 1.1: scaffold (done)
**Done:** Broke Phase 1 into 7 sub-steps (scaffold → ingest → parse/chunk → embed/index → retrieve/answer → eval set → FastAPI); implemented 1.1: `pyproject.toml` (hatchling, empty deps, pytest as dev extra), `.gitignore`, README with status + roadmap, `src/filinglens/` with `config.py` (company CIKs, data paths, EDGAR User-Agent), and smoke tests. All 4 tests pass. Commit `9c2643f`.

**Mark's thoughts:** Approved sub-step breakdown and scaffold design as proposed.

**Claude's suggestions:** Start deps empty and add each at the step that needs it — clearer commit history to walk through in interviews. Use `src/` layout over flat — standard for real projects, forces installed-package imports. Ollama/embedding steps (1.4–1.5) will run on Mark's machine since Claude's sandbox can't run models.

**Decision:** Scaffold committed. Next: design step 1.2 (EDGAR ingest) before implementing.

---

## 2026-07-06 — Plan amendment: extractor + XBRL verification added as Phase 4
**Done:** Added the SEC filing extractor with XBRL verification to PLAN.md; agent → Phase 5, AWS → Phase 6.

**Mark's thoughts:** Noticed the extractor-with-verification (the original FilingLens concept) was missing from the plan.

**Claude's suggestions:** Make it a standalone phase — XBRL gives ground truth, so extracted figures can be proven right/wrong, stronger than citation-only verification. Place after storage (needs parsed filings + DB) and before the agent (which can then call the verifier as a tool). Sharpens the application pitch: maps directly to Finpilot's "verification and auditability systems for AI outputs."

**Decision:** Approved; phases renumbered.

---

## 2026-07-06 — Phase 1 design (approved)
**Done:** Designed the core RAG slice; details written into PLAN.md.

**Mark's thoughts:** Chose fully local/free AI (Ollama + sentence-transformers) over cloud APIs; Apple/Microsoft/Nvidia 10-Ks; public GitHub repo.

**Claude's suggestions:** Section-aware chunking with metadata as the citation mechanism; ChromaDB now → pgvector in Phase 2 (good migration story); provider abstraction layer so local models can be swapped for cloud APIs later without rewrites; CLI before FastAPI. Caveat noted: local models give weaker answers than cloud APIs — acceptable since the goal is learning, and the abstraction makes upgrading trivial.

**Decision:** Design approved. Next: implement Phase 1 step by step, starting with repo scaffold + EDGAR ingestion.

---

## 2026-07-06 — Plan amendment: testing included
**Done:** Added testing to every phase in PLAN.md plus a "Testing principle" section.

**Mark's thoughts:** Test setup should be included in the plan.

**Claude's suggestions:** Make tests per-phase rather than a separate phase: pytest from day one (Phase 1), DB integration tests (Phase 2), Vitest/RTL (Phase 3), CI via GitHub Actions before deploy (Phase 5). Also add a golden Q&A eval set for AI answer quality — a strong signal given Finpilot's "accuracy is non-negotiable."

**Decision:** Approved by request; PLAN.md updated.

---

## 2026-07-06 — Step 1: Scope & goals (approved)
**Done:** Defined and approved project scope; wrote phased plan into PLAN.md.

**Mark's thoughts:** Main goal is to practice unfamiliar knowledge and show capability to learn and implement real things. All four areas (RAG, agents/verification, React/TS, Postgres/AWS) are unfamiliar. Chose fuller project over small demo — continue past Jul 10 deadline, mention as in-progress with repo link. Questioned why MongoDB was missing from the proposal.

**Claude's suggestions:** FilingLens = SEC filing Q&A with exact citations, mirroring Finpilot's retrieval + verification/auditability pitch. Phase order: core RAG slice first so something real exists before the deadline. On MongoDB: initially skipped (Postgres+pgvector suffices; second DB can look like stack-padding), but a MongoDB(raw docs)/Postgres(relational+vectors) split is a legitimate pattern for semi-structured filings and covers the full Finpilot stack.

**Decision:** Scope approved with MongoDB folded into Phase 2. Next: design Phase 1 (core RAG slice) before implementing.

---

## 2026-07-05 — Project setup
**Done:** Created `FilingLens/` in the Finpilot application folder with empty `README.md`, `docs/` (design files), `PLAN.md` (step-by-step plan), and this `LOG.md`.

**Mark's thoughts:** Wants the whole project traceable — plan holds the steps we discuss; log records every step, his thinking, and Claude's suggestions.

**Claude's suggestions:** Work step-by-step (design → approve → implement); tie project scope to the Finpilot job description; next step is defining scope in PLAN step 1.

**Decision:** Structure approved by creating it. Next: discuss step 1 (scope & goals).
