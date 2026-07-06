# FilingLens — Log

> Every step gets an entry: what was done, Mark's thoughts, Claude's suggestions, and the decision. Newest entry on top.

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
