# FilingLens — Log

> Every step gets an entry: what was done, Mark's thoughts, Claude's suggestions, and the decision. Newest entry on top.

---

## 2026-07-16 — Stray one-pass scaffold found and deleted
**Done:** Mark noticed 1K+ untracked changes in git. Investigation: an uncommitted `backend/` (FastAPI + SQLAlchemy + OpenAI extractor/verifier), `frontend/` (React/TS Vite incl. node_modules ≈2,400 files), `docker-compose.yml`, and `docs/DESIGN.md` had appeared in the repo folder. Not created by any Claude session on this machine (transcripts checked). Timestamps indicate a one-pass prototype of the *original* FilingLens concept (extractor + XBRL verifier) dating to 2026-07-05 — before the step-by-step plan existed — that OneDrive synced onto this Mac the evening of 2026-07-14. It conflicted with the approved architecture (SQLAlchemy/OpenAI/no-RAG vs psycopg/local-models/citations) and with Phase 2.1's planned docker-compose.yml.

**Decision:** Mark chose to delete it (offered move-out-as-reference as alternative). Deleted 2026-07-16; git back to clean except the intentional PLAN.md/LOG.md edits. Nothing from Phase 1 was affected; nothing had been committed. Reminder for Phase 3: add `node_modules/` to .gitignore before any frontend work.
**Done:** Phase 2 (storage layer) design discussed and written into PLAN.md: 7 sub-steps (2.1 Docker infra → 2.2 Mongo filing store → 2.3 Postgres schema/migrations → 2.4 PgVector store → 2.5 eval parity gate → 2.6 Q&A history → 2.7 phase close with study digest). Sub-step breakdown awaiting Mark's explicit approval; implementation additionally gated on the Phase 1 retest.

**Mark's thoughts:** Studying Phase 1 in a parallel Opus 4.8 session while this session handles Phase 2 design. Chose all three recommended options on the design decisions.

**Claude's suggestions (the three decisions):** (3) Raw SQL via psycopg 3 over SQLAlchemy — quiz showed mechanics are the weak spot, so every query should be one Mark wrote and can defend; (4) Docker Compose for local DBs — standard practice and rehearses the Phase 6 deploy; (5) Mongo as source of truth (ingest writes to it, parse reads from it, `data/raw/` demoted to cache) over a decorative sidecar copy — "why is Mongo there?" must have an honest answer. Also framed the phase's engineering heart: the citation invariant now spans two stores (Postgres chunk offsets → Mongo canonical text), verified by integration tests. Eval parity (2.5) is the migration's proof: same golden set, numbers must match hit@6 87% / MRR 0.76.

**Decision:** Design recorded; decisions 3–5 in PLAN.md table. Next: Mark approves the sub-step breakdown, passes the Phase 1 retest, then 2.1 begins (Mark installs Docker Desktop as prep).

---

## 2026-07-13 — Phase 1 self-test baseline (live quiz)
**Done:** Mark took the 20-question Phase 1 self-test cold, live with Claude. Baseline: **5.5/20 (27.5%)**, four Tier-1 zeros (Q3 citation invariant, Q4 grounding, Q5 retrieval-vs-answer diagnosis, Q6 MRR). Score recorded in `Phase1_Study_Guide.md` (outside repo). Strongest answer: Q9 shared embedding space (full credit); solid instincts on chunking rationale and gitignore-as-build-artifact.

**Mark's thoughts:** Chose the live quiz over self-study when the untaken test was flagged before Phase 2.

**Claude's suggestions:** Study priority = the four Tier-1 zeros first — they are the verifiability + eval story, i.e. the project's pitch — then Tier-2 mechanics (upsert/idempotency, fakes in tests, overlap-doubling bug, FastAPI declarations). Use the study guide's methods: trace `AAPL_2025_item1A_003` end to end, Feynman the Tier-1 concepts, retell the Q14 bug story from chunk.py.

**Decision:** Per working agreement (pass ≥70%, no Tier-1 zeros, before next phase), Phase 2 implementation waits for a passing retest. Mark studies in a **separate session (Opus 4.8)** using `Phase1_Study_Guide.md`; **this session proceeds with Phase 2 design discussion only**. Retest scores go into the study guide's table.

---

## 2026-07-11 — Mark's Phase 1 reflection (recorded at his request)
**Mark's thoughts (verbatim spirit):** Claude is amazing, but he barely understands the code and logic, which feels bad — the desire to know everything collides with anxiety. Line-by-line study is too slow at his current level; picking key points to understand deeply feels reasonable. Wants interview questions covering only those points, and a measurable understanding metric (target: ~70%).

**Response:** Created `Phase1_Study_Guide.md` (outside the repo, next to FilingLens/): 10 concepts in 3 tiers, study methods (trace one chunk end-to-end, Feynman technique, modify-to-learn experiments), a 20-question self-test with 0/0.5/1 scoring → percentage, pass = ≥70% with no Tier-1 zeros, and a score-tracking table.

**Process change from Phase 2 onward:** each step's design discussion includes a plain-language "what you need to understand here" note; each phase ends with a study digest + self-test before the next phase starts. Understanding is a deliverable, same as tests.

---

## 2026-07-11 — Phase 1 COMPLETE: API verified end-to-end
**Done:** Mark verified the full stack on his machine: 37 tests pass (after fixing a test that assumed the non-semantic FakeEmbedder would rank like a real one — caught by Mark's run), `httpx`→`httpx2` dev-dep swap silenced the starlette deprecation, and `/ask` via Swagger `/docs` returned a synthesized, multi-citation answer ([3][4][5][6] across FY2023–2025 Apple 10-Ks) for the supply-chain question.

**Debugging lessons along the way (good interview material):**
- `uvicorn` resolved to system Python 3.12 instead of the venv despite `(.venv)` in the prompt — fixed with `python -m uvicorn`; lesson: `python -m` pins the interpreter.
- Swagger's placeholder values (`"ticker": "string"`) silently became real filters → zero hits → the API correctly refused with "Not found in the provided filings" instead of hallucinating. Accidental production test of the unanswerable path; it behaved as designed.

**Application status:** Finpilot deadline missed (window closed 2026-07-10 before submission); tracker updated. FilingLens continues as the flagship portfolio project — next target: FilmTools application (due 2026-07-29, wants GitHub/portfolio link).

**Decision:** Phase 1 closed. Phase 2 (MongoDB + Postgres/pgvector) design discussion starts in a new session.

---

## 2026-07-08 — Step 1.7: FastAPI wrapper (code done) + Phase 1 retrospective
**Done:** `api.py` — `POST /ask` (the future React UI's endpoint), `GET /search` (raw scored hits), `GET /health` (status + chunk count); Pydantic request/response models give validation (422s) and auto-generated interactive docs at `/docs`; embedder/collection/LLM are lru_cached singletons so the model loads once, not per request; tests override the dependency functions with fakes — 4 new tests via TestClient, no Ollama/model/disk needed. Deps: fastapi, uvicorn (+httpx dev). README rewritten with full usage. Expect 37 tests locally.

**Phase 1 retrospective (for the interview):**
- Built: EDGAR ingestion → canonical-text parsing with ToC-proof section detection → offset-exact chunking → local embeddings in ChromaDB → grounded Q&A with citations resolvable to exact characters of a specific filing → CLI + HTTP API → measured baseline (hit@6 87%, MRR 0.76, answers 47%).
- Core invariant everything hangs on: `text[char_start:char_end] == chunk.text` — verified across all 973 chunks.
- Bugs the tests caught pre-commit: ingest path collection bug; chunk overlap doubling on hard-split paragraphs.
- Honest limitations, by design: llama3.2 paraphrases excerpts rather than synthesizing (measured, swappable); HTML tables embed poorly (Phase 4 XBRL is the numbers story); two retrieval misses analyzed (table flattening, cross-company confusion).
- Every step: designed → discussed → approved → implemented → tested → logged.

**Decision:** Phase 1 code complete pending Mark's local verification of the API. Mark: `pip install -e ".[dev]"` → `pytest` (expect 37) → `uvicorn filinglens.api:app` → try `/docs` in browser → push to GitHub. Then Phase 2 (MongoDB + Postgres/pgvector) design when ready.

---

## 2026-07-08 — Step 1.6 results: baseline measured
**Done:** Mark ran both eval modes. Retrieval: hit@6 = 87% (13/15), MRR = 0.76, 11 questions ranked #1. Answers (llama3.2): 47% pass. Baseline recorded in README.

**Analysis:** Retrieval misses: `aapl_greater_china` (phrase partly in flattened segment tables — embeddings of number-soup are weak) and `aapl_climate` (likely outranked by MSFT/NVDA climate chunks — cross-company confusion in unfiltered search). Answer failures include 5 questions where retrieval was rank 1 but generation failed the check (dropped [n] markers / missing keyword) — bottleneck is the small model, not retrieval. Measuring the two separately is what makes that diagnosis possible.

**Improvement backlog (later phases):** better table handling (Phase 2 storage / Phase 4 XBRL for numbers), metadata-aware ranking boosts, stronger LLM via the provider abstraction.

**Decision:** Baseline accepted; numbers in README. Next: 1.7 FastAPI wrapper to close Phase 1.

---

## 2026-07-08 — Step 1.5 verified by Mark + step 1.6: golden eval set (code done)
**Done (1.5 verification):** Mark ran the CLI on his machine — Apple supply-chain question returned a grounded answer citing AAPL FY2025 Item 1A chars 45464–48905 with the sec.gov URL; `--retrieve-only` showed sensible hits. 29 tests pass locally (Claude's earlier "31" was a miscount). Observations logged: llama3.2 answers near-verbatim rather than synthesizing (small-model behavior; eval will quantify, provider abstraction makes upgrades one-line); MSFT "Item 8 (FINANCIAL STATE)" title clipped by a mid-word line wrap (cosmetic); financial tables retrieve as flattened number-soup (expected; Phase 4 XBRL is the real fix for numbers).

**Done (1.6):** `eval/golden_qa.jsonl` — 15 questions across all 3 companies; expectations are (ticker, acceptable items, must-contain phrase), never chunk ids, so the set survives re-chunking. Every phrase verified to exist in the real chunks (15/15). `eval.py` — hit@k + MRR for retrieval; `--with-llm` answer check (not a refusal + expected keywords + >=1 citation pointing at a matching chunk). 4 new pure tests incl. golden-file validation. 26 pass in sandbox / 33 expected locally.

**Mark's thoughts:** Asked what HF Hub was (answer: model download source only — everything runs locally) and how the code reaches Ollama (answer: background service on localhost:11434, spoken to over HTTP). Approved 1.6 design.

**Claude's suggestions:** Draft golden questions from phrases grep-verified in the actual filings so expectations are guaranteed satisfiable; keep eval expectations chunk-id-free.

**Decision:** Committed. Mark runs `python -m filinglens.eval` (retrieval-only, fast) and `python -m filinglens.eval --with-llm` (slow, ~15 Ollama calls); numbers go into README. Then 1.7 (FastAPI) closes Phase 1.

---

## 2026-07-08 — Step 1.5: retrieve + answer + CLI (code done; awaiting Mark's local run)
**Done:** `retrieve.py` — question embedded with the same MiniLM model, Chroma query with optional ticker/year metadata filters, `Hit` carries text + full citation metadata + cosine score. `answer.py` — `LLM` protocol + `OllamaLLM` (local HTTP API, temperature 0, no new deps); grounding prompt (answer ONLY from numbered excerpts, cite [n], refuse rather than guess); `[n]` markers parsed and resolved back to exact chunks. `cli.py` — question + `--ticker/--year/-k/--model`, `--retrieve-only` debug mode, prints Sources with char offsets + URLs. 9 new tests: 5 pure (prompt rules, citation parsing, where-clauses) + 4 e2e with FakeEmbedder/FakeLLM/in-memory Chroma (ranking, filter isolation, citation resolution, not-found short-circuits without calling the LLM). 22 pass in sandbox; chroma-dependent ones run on Mark's machine.

**Mark's thoughts:** Confirmed 1.4 local run (973 vectors, .chroma synced); pulled llama3.2; approved 1.5 design.

**Claude's suggestions:** `--retrieve-only` to tell retrieval failures from generation failures when answers are bad; temperature 0 for factual mode; resolve citations only for markers the answer actually used.

**Decision:** Committed. Mark runs: `pytest` (expect 31 passed) then first real question via CLI. Next: 1.6 golden Q&A eval set.

---

## 2026-07-07 — Step 1.4: embed + index (code done; awaiting Mark's local run)
**Done:** `embed.py` — `Embedder` protocol (provider abstraction), `LocalEmbedder` wrapping sentence-transformers `all-MiniLM-L6-v2` (normalized vectors, batches of 64), ChromaDB `filings` collection (cosine space, persisted in `.chroma/`), `upsert` for idempotent re-indexing, chunk metadata (ticker/fy/item/offsets/URL) stored on every vector so search hits carry their citations. Deps: sentence-transformers, chromadb. 3 new tests using a `FakeEmbedder` + in-memory Chroma: metadata storage, idempotency, nearest-neighbor retrieval of a planted chunk; `importorskip` since Claude's sandbox lacks chromadb. Prior 17 tests still pass.

**Mark's thoughts:** Approved; noted he didn't fully understand embeddings/vector DBs yet — Claude explained (embeddings = meaning→vectors, Chroma = nearest-neighbor store, upsert = no duplicates). Revisit before interviews.

**Claude's suggestions:** Lazy-import the heavy libs inside `LocalEmbedder`/`get_collection` so the rest of the package imports without them; test the pipeline through the abstraction with a deterministic fake instead of the real model — fast and no downloads.

**Decision:** Committed. Mark to run locally: `pip install -e ".[dev]"` → `pytest` (expect 20 passed) → `python -m filinglens.embed` (expect "973 vectors"). Then design 1.5 (retrieve + answer).

---

## 2026-07-07 — Step 1.3: parse + chunk (done)
**Done:** `parse.py` — BeautifulSoup(+lxml) → normalized *canonical text* (the string all citation offsets point into) + section map via item-heading regex; ToC false positives handled by keeping the last occurrence of each item code, out-of-order stragglers dropped, whole-doc fallback if detection fails. `chunk.py` — paragraph packing into ≤500-word chunks (small-paragraph overlap), never crossing sections; each chunk = id + exact char offsets + filing metadata = the citation. Deps: beautifulsoup4, lxml. 8 new tests (17 total, all pass). Ran on all 9 real filings: 22–23 sections each, 973 chunks, **0 offset round-trip failures**.

**Mark's thoughts:** Ran the EDGAR ingest locally (all 9 filings downloaded); read through the full ingest code; approved 1.3 design as proposed, including word-count budget over a real tokenizer.

**Claude's suggestions:** Make `text[char_start:char_end] == chunk.text` the invariant the whole verification story rests on — tested per-chunk across all filings. Bug found by the tests before commit: chunk overlap doubled sizes when the carried paragraph was itself a hard-split 500-word piece; fixed by capping overlap paragraphs at 120 words.

**Decision:** Committed. Next: design step 1.4 (embed + index into ChromaDB) — runs on Mark's machine.

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
