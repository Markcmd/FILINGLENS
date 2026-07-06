# FilingLens — Plan

> Working agreement: each step is designed → discussed → approved → implemented. No step starts before the previous one is approved. Every step gets a LOG.md entry.

## Project scope (approved 2026-07-06)
**FilingLens** — ask questions about SEC filings (10-K/10-Q), get answers with exact citations back to the filing text, so every AI output is verifiable. Mirrors Finpilot's core pitch: retrieval + verification/auditability for finance.

**Mark's goal:** practice unfamiliar knowledge (all of: RAG, agents/verification, React/TS, Postgres/AWS, MongoDB) and show he can learn and implement real things. Fuller project — continued after the Jul 10 application deadline; application mentions it as in-progress with repo link.

## Status legend
`[ ]` not started · `[~]` in discussion · `[>]` approved, in progress · `[x]` done

## Steps

- [x] 1. Define project scope & goals — approved 2026-07-06
- [ ] 2. **Phase 1 (by Jul 10) — core RAG slice (Python):** download filings from SEC EDGAR, chunk + embed, CLI or minimal API answering questions with cited passages. Mentionable in application.
- [ ] 3. **Phase 2 — storage layer:** MongoDB for raw/parsed filing documents (semi-structured), Postgres + pgvector for chunks, embeddings, citations, Q&A history.
- [ ] 4. **Phase 3 — React/TypeScript UI:** question box, answer view with clickable citations highlighting source passages.
- [ ] 5. **Phase 4 — agent + verification:** multi-step agent (e.g. compare risk factors across years) with per-step audit trail; verifier checking each claim against sources.
- [ ] 6. **Phase 5 — AWS deploy:** get it live.

## Decisions
| # | Decision | Date | Log ref |
|---|----------|------|---------|
| 1 | Project = SEC filing Q&A with verifiable citations; phased to cover all unfamiliar areas | 2026-07-06 | Log 2026-07-06 |
| 2 | Use both MongoDB (raw filing docs) and Postgres/pgvector (relational + vectors) — legitimate split, covers full Finpilot stack | 2026-07-06 | Log 2026-07-06 |
