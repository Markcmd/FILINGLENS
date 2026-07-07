# FilingLens — Log

> Every step gets an entry: what was done, Mark's thoughts, Claude's suggestions, and the decision. Newest entry on top.

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
