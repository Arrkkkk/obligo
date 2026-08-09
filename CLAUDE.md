# CLAUDE.md — Obligo

This file is read automatically by Claude Code at the start of every session in this repo. It is the operating contract for how work gets done here. If anything below conflicts with a request in chat, **flag the conflict and ask before proceeding** — don't silently override this file, and don't silently override the request either.

The full design authority is `OBLIGO_ENGINEERING_BLUEPRINT.md` at the repo root. This file is a summary and a set of guardrails, not a replacement — when in doubt, go read the relevant section of the blueprint rather than guessing.

---

## What this project is

Obligo compiles natural-language obligations (from contracts, email, transcripts) into a typed, formally verifiable intermediate representation, detects contradictions between obligations using an SMT solver (Z3), and monitors each obligation against real-world evidence until it's fulfilled or breached.

The differentiator is the compiler (LLM candidate extraction → Lark grammar parse → semantic typecheck) and the verifier (Z3 lowering + unsat-core explanation). Everything else in the stack exists to support those two things. If a proposed change doesn't serve the compiler, the verifier, or making them demoable, treat it with suspicion.

---

## Local dev environment — DEVIATION FROM BLUEPRINT, READ THIS FIRST

**No Docker on the local machine**, by deliberate choice (not a temporary gap — don't try to "fix" this by installing Docker). This changes how Phase 1 and beyond are executed locally:

- **Postgres:** not run locally. Use a **Neon free-tier branch** (with the `pgvector` extension enabled) as the dev database. Connection string goes in `.env` (git-ignored), never committed.
- **Redis:** not run locally. Use **Upstash's free-tier Redis** (HTTPS/REST-based, no local process needed).
- **The three services run natively**, not in containers: Spring via `./gradlew bootRun`, FastAPI via `uvicorn` in a venv, Next.js via `npm run dev`.
- **Dockerfiles and `compose.yml` still get written** per the blueprint — they're needed for CI image builds (§20.4) and eventual deployment (§20.5) — but they are **not exercised locally** and are not a dependency for local development to work. Do not block any Phase 1 task on "the Compose stack running locally," because it won't be, by design.
- **`make dev` in this project means:** start Spring, start FastAPI, start Next.js natively, pointed at the cloud Postgres/Redis — not `docker compose up`. Write the Makefile target accordingly.
- Docker becomes actually relevant again around Phase 9 (deployment) or whenever CI needs to build and push real images — not before.

---

## Current phase

**Phase 4 — The Compiler & Verifier ★** (see blueprint §21 / §3 Phase 4 deliverables). Blueprint's own words: this is the differentiator phase the entire project exists to contain — "do not compress this phase, compress Phase 8 instead."

Phase 3 (Ingestion, Storage & Segmentation) is complete and verified, locally and in CI, against real infrastructure (no mocks) — all four blueprint §21 acceptance criteria Met or explicitly, permanently deferred:
- **Presigned upload flow (§11.2)** — `sources` table with RLS from creation, upload-intent/commit against real Supabase Storage, SHA-256 dedup-on-reupload. Real finding: Supabase's signed-upload token ignores a caller-supplied expiry (always ~2h, not blueprint's 5 min target) — verified live that a leaked/replayed URL still can't do anything once the legitimate upload lands (`upsert:false`, no read scope, path-bound signature), so the real exposure is narrower than it first looked (a pre-upload race on an abandoned intent); bounded server-side to a 30 min staleness cap, not "solved."
- **File-security hardening (§11.6)** — magic-byte sniffing, size cap, PDF active-content rejection (JS/launch actions/embedded files), a three-part decompression-bomb guard (page count ≤500, 200:1 expansion ratio, 10s timeout), and server-side SHA-256 recomputation (a deliberate deviation from blueprint's sync/async two-tier split — done synchronously up to the full 50MB cap instead, since no async-worker infra exists yet). All proven with real PDFBox-generated and downloaded malicious/benign fixtures — including a real page-count-cap gap (blueprint's own literal "600-page file" case) found completely untested and closed during the Phase 3 sign-off pass, not assumed covered by the byte-size cap it was previously conflated with.
- **Tenant isolation ported to apps/brain (§10.9)** — the first Python-side Postgres access, proven with the same rigor as the Java-side suite (identical `pg_backend_pid` across tenant contexts, zero leakage) plus one write-path case Java's own test doesn't cover. `contextvars.ContextVar`, not `threading.local` — FastAPI's asyncio concurrency model means a naive port would leak one request's `org_id` into another's.
- **PyMuPDF text/layout extraction, offsets derived by construction, not post-hoc matching** — `page_text[char_start:char_end] == text` holds by construction for every segment, because the persisted text is literally what produced the offsets. Real, documented, not-fully-solved limitation: round-trip correctness is guaranteed; reading-order correctness on genuinely multi-column layouts is not (PyMuPDF's block order is a position heuristic, demonstrated on a real two-column fixture and asserted so a future fix changes the test loudly).
- **PyMuPDF is AGPL-3.0-or-commercial, not permissive** — confirmed against PyPI/GitHub, no permissive alternative exists with comparable layout fidelity. Accepted for the *current* deployment shape only (local/personal use — AGPL's network-copyleft clause is deployment-triggered, not distribution-triggered): **revisit at Phase 9 deployment**, not before, either confirming the AGPL obligation is acceptable or acquiring a commercial license.
- **OCR via Tesseract 5 (local dev, Apple Silicon) / PaddleOCR PP-OCRv4 (x86 Hetzner prod target)** — a deliberate dev/prod split, not a preference: PaddlePaddle ships arm64 wheels now, but current PaddleOCR still segfaults on M1-M3 Macs (a stability class wheel availability doesn't fix). Per-page (not per-document) scanned-page detection, MIN-aggregated block confidence (a deliberate choice over averaging — one badly-misread date/party-name/dollar-figure is a real correctness failure, not noise to smooth over), `LOW_OCR_CONFIDENCE_THRESHOLD` flagging proven against real degraded scans. **Revisit at Phase 9 deployment**, same footing as the PyMuPDF/AGPL decision.
- **Async segmentation via Celery on Redis** — job state lives in Postgres (`segmentation_jobs`), not a second broker, per blueprint's own stated design intent. `acks_late=True` plus a real macOS fork-safety finding (opening a network connection inside a forked child segfaults — CPython's documented limitation, not a bug here — fixed via `--pool=solo` on this machine, `--pool=prefork` on Linux CI/prod where the hazard doesn't exist) plus a Postgres-based staleness-reconciliation net for the real, verified gaps in how promptly `acks_late` redelivery actually happens under concurrent access.
- **SSE ingest-progress streaming** — apps/core polls apps/brain's existing job-status endpoint on an interval (not Postgres LISTEN/NOTIFY, which Neon's pooled connections don't support, and not a new Redis pub/sub channel), reusing the existing shared-secret-gated core→brain boundary rather than reopening it. Two real async-dispatch bugs found and fixed: this was the first async (`SseEmitter`-returning) endpoint the codebase has ever had, and `TenantJwtAuthenticationFilter` needed `shouldNotFilterAsyncDispatch()`/`shouldNotFilterErrorDispatch()` explicitly overridden to `false`, or Spring Security's own `AuthorizationFilter` failed closed on the container's internal completion/error dispatch.
- **10 varied, genuinely distinct PDF fixtures** (not padding — two new born-digital layouts and one mechanically-distinct OCR degradation, each checked for real structural variety before being added) prove offset-exactness end to end. The one permanent, explicit scope exclusion: **macro DOCX** — DOCX is rejected at upload-intent by the MIME allow-list (`{"application/pdf"}` only) before any macro-specific detection could ever run against it; revisit only if DOCX ingestion is ever added to the allow-list.

Carried-forward technical debt (real, tracked, not blocking Phase 4):
- No public revoke endpoint for invitations — revocation is internal-only (exercised by re-invite rotation). Add a real one if a use case needs it standalone.
- The full HTTP-level cross-tenant leakage suite (§17.8) is still not built out as its own standalone gate — more protected endpoints now exist (sources upload/commit/segment/stream) than when this was first deferred in Phase 2, which makes this more overdue, not less.
- **No generic Idempotency-Key/X-Request-Id mechanism exists anywhere in `apps/core`**, despite both being listed as non-negotiable rules. This was explicitly flagged during Phase 3 as "build as its own dedicated slice before Phase 4, not bundled into unrelated work" — it wasn't built. Carrying forward as overdue debt, not a newly-discovered gap: `invite`, `accept`, `role-update`, and every new Phase 3 endpoint still have none, and no response carries `X-Request-Id`.
- **Interim shared-secret gate between apps/core and apps/brain; real per-request org authentication still doesn't exist.** `BRAIN_SERVICE_TOKEN` proves "a caller that knows the secret reached this endpoint," not "this `org_id` claim is trustworthy" — anyone holding the secret (including a buggy or compromised apps/core) can still assert any `org_id`. The real fix (a short-lived, per-request token apps/core mints only after its own JWT verification has established which `org_id` a request may actually touch, cryptographically verified by apps/brain instead of trusted from the body) still doesn't exist. **More relevant entering Phase 4, not less** — the compiler/extraction pipeline will add more apps/brain-side operations touching org-scoped data across this exact boundary.
- Genuine Neon branch-per-PR CI isn't built — CI runs against one persistent branch instead. Real future work if per-PR isolation ever becomes worth the added complexity; apps/brain's Flyway-CLI self-migration step was deliberately written to be correct under either setup already.
- `source_versions`/versioning (§11.3) is still deliberately not built — `sources.storage_key` still hardcodes `v1`.
- **Accepted, unmitigated gap: PDF structural validation runs in-process, not sandboxed.** `PdfStructuralValidator` runs Apache PDFBox directly against untrusted upload bytes inside the main Spring process; its 10s timeout is the only mitigation against a parser-level DoS, with no isolation against a parser-level memory-safety issue.
- No ArchUnit-equivalent static check yet proves every DB access in apps/brain actually goes through `tenant_scope()` rather than a raw `engine.connect()` — the Python-side analog of the Java `TenantIsolationArchitectureTest` gap that already exists on the Java side, left as follow-up there too.
- Reprocessing/supersession semantics for re-segmenting an already-segmented source are still undecided — currently a safe, loud `409`, not real idempotency. Named as an open question in three places (`V12`'s migration comment, `segmentation_jobs`' `UNIQUE` constraint comment, the segment-trigger endpoint) without being resolved in any of them.
- Upstash's actual max-concurrent-connections ceiling for the free tier is still unverified — `worker_concurrency=2` is a deliberately conservative fallback, not a confirmed-safe number.
- A periodic Celery Beat sweep calling `restore_visible()` proactively (rather than relying on worker idle-polling, which has real, verified rough edges under concurrent access) is valid future hardening, not built — the Postgres staleness-reconciliation check is the actual load-bearing safety net today.
- apps/web's dashboard fetches the access token once at load with no silent/scheduled refresh — not a security gap (the token is cryptographically dead at 15 min regardless) but a UX one, worth a note before Phase 6's frontend work.

**Phase 4 scope, per blueprint §21.** Objective: build the differentiator — LLM candidate extraction → Lark grammar parse → semantic typecheck (the compiler), then Z3 lowering + unsat-core explanation (the verifier). Deliverables: Obligation IR v1 spec (`packages/ir-spec/`) · Lark grammar · AST · typechecker (party-alias symbol resolution, temporal unit validation, underspecification detection, amendment scope/precedence) · LangGraph extraction graph (Router → Loader → Segmenter → Extractor → **Span Grounder** → IR Compiler → Normalizer → Critic → Linker) · parse-error repair loop (≤3 retries, parser message fed back) · model router with budget enforcement, provider failover, content-hash caching · versioned prompt registry · Z3 lowering (interval algebra + modal constraints) · conflict-candidate set definition · unsat-core → plain-English explanation · `ir_hash` reconciliation for idempotent re-extraction · embeddings + hybrid search · the two-tier eval harness and the 100-obligation gold set · property-based compiler test suite. Acceptance criteria: compile success ≥90% on the dev corpus with span-grounding rate exactly 100% (zero ungrounded obligations reach the database, by construction); Tier-2 fully-correct-IR rate ≥80% on the gold set; a planted cross-document conflict detected with a minimal unsat core rendered as one readable sentence; all property tests pass including round-trip and hash stability; re-extracting the same document twice produces zero duplicate obligations.

Named risk worth flagging before writing any Phase 4 code, per blueprint's own risk list: **the IR is the single largest schedule risk if it's allowed to stay open-ended.** Blueprint's own mitigation is to freeze IR v1 at four modalities, five temporal forms, and conditions only (no nested exceptions in v1) — everything else is v2. This is a blueprint-level constraint, not a suggestion to relitigate once Phase 4 work actually starts.

**Obligation IR v1 spec checkpoint (§21 Phase 4) — `packages/ir-spec/` written and frozen. No parser, no typechecker, no extraction pipeline code exists yet — this checkpoint is the IR's shape only.**
- **Real discrepancy found and resolved, not guessed past:** blueprint §6.2's grammar sketch lists six temporal alternatives (`BY`, `WITHIN...OF`, `EVERY`, `DURING`, `AFTER`, `BEFORE`) against §21's stated freeze of five. Resolved by merging `AFTER`/`BEFORE` into one directional `RELATIVE_TO_TRIGGER(direction, trigger)` form — keeps all six alternatives' expressive power, lands on exactly five named forms as §21 requires.
- **"Conditions only, no nested exceptions" read deliberately as "no `UNLESS`/exception construct exists in v1's grammar at all,"** not "flat exceptions are allowed, just not nested ones." The safer reading for a tool whose whole purpose is catching what a human reader would otherwise miss — a silent drop of a legal carve-out is worse than a loud refusal to compile it. **Verified mechanically, not just documented:** `grammar.lark`'s own `IF` production parses correctly while a string containing `UNLESS` genuinely fails to parse (`UnexpectedCharacters`) — there is no accidental path by which an exception clause sneaks through this grammar's own rules.
- **A real compositional gap named and given its own worked "not representable" fixture:** an obligation's `temporal?` slot is singular, so `EVERY` (recurrence) and `DURING` (its outer bound) can't compose on one obligation even though each exists individually. v1's answer: `EVERY` alone, with the outer bound left implicit to the source document's own `effective_date`/expiration — real compositional temporal expressions are v2 scope, the same footing as nested exceptions.
- **Obligor/obligee reconciled from the grammar sketch's single abstract `party` slot against the ER schema's two distinct FK columns** (`obligor_party_id`, `obligee_party_id`, a CHECK that they differ) — `PartyRef` is a two-state (`UNRESOLVED` alias / `RESOLVED` party_id) tagged union, applied as a consistent convention everywhere the typechecker, not the parser, is responsible for resolving a reference (`DateRef`, `TriggerRef` use the identical shape).
- **`packages/ir-spec/` built per §22.4's own description** ("documentation-as-artifact... the grammar, the type rules, worked examples, and the shared test fixtures both runtimes validate against") — mirrors `packages/contracts/`'s existing JSON-Schema-as-source-of-truth precedent, not a Python-only Pydantic model set Java would have no way to check itself against: `SPEC.md` (12-section narrative spec) + `grammar.lark` (frozen Lark-syntax reference, not wired to any parser) + `schema/obligation-ir.schema.json` (the canonical both-runtimes artifact) + `examples/*.json` (9 worked examples covering all 4 modalities, all 5 temporal forms, both `PartyRef` states, both underspecification mechanisms) + `examples/not-supported/*.json` (4 boundary fixtures: bare `UNLESS`, `IF`+`UNLESS` mixed, multi-level nesting, the `EVERY`+`DURING` gap).
- **Verified for real, twice** — once while drafting, once fresh from a clean directory state per this file's own standing discipline: the schema checks as well-formed JSON Schema 2020-12; `grammar.lark` loads and parses a real sample obligation with no grammar/lexer conflicts; every example's `ir` key validates against the schema with every `alias`/`raw`/`raw_text` string confirmed a literal substring of its own `source_text` (the same span-grounding discipline the real pipeline will enforce, applied to the fixtures too, not assumed). **Two real classes of self-authored bugs caught by this discipline, not by eyeballing:** four `char_end` arithmetic mistakes (hand-computed offsets that went stale after editing the sentence they were computed against), and four internal section cross-references in `SPEC.md`/the schema that pointed at the wrong section number after the document was drafted out of the order it now reads in — caught by grepping every `section N` reference and mapping each one against the real header list, not by rereading and trusting.
- **Open item, explicitly carried, not silently invented:** the closed action taxonomy (~40 verbs; blueprint names 10 examples and no more) is validated in the schema only for lexical shape, not a closed enum. Finalizing the full list is deferred to writing `apps/brain/compiler/grammar/obligation.lark` (the next checkpoint) — decide it there, against real extraction candidates, don't invent it now. The object-class taxonomy carries the identical open-item status.

When this phase is completed and I confirm it, update this section to reflect Phase 5 before continuing work.

---

## Standing principles (do not violate these without asking)

1. **The system must be demoable at every commit.** Don't leave the stack in a broken state overnight.
2. **Deterministic core, probabilistic edge.** Anything a parser, typechecker, or solver can decide must not be decided by an LLM. If you're about to have a model output something that determines correctness (not just a draft/candidate), stop and ask.
3. **One trust boundary, three enforcement layers** for tenant isolation: gateway → application (`TenantConnectionPreparer` AOP setting the RLS GUC per-transaction + `@PreAuthorize`) → database (RLS, `FORCE`d, fail-closed). All three, always. Note: there is no JPA/Hibernate anywhere in `apps/core` — it's `JdbcTemplate` throughout, so "Hibernate `@Filter`" (as blueprint §10.9's diagram depicts for Layer 2) does not apply to this codebase; Layer 2 is the AOP described above, not a Hibernate filter.
4. **Every LLM output is untrusted input** — including, especially, when it originates from a document the user uploaded. Never concatenate document text into a system prompt.
5. **Prefer deleting a technology over adding one.** If a task seems to need a new piece of infrastructure, check the "explicitly deferred" list below first — it's probably already been considered and rejected for now.

---

## Tech choices that are LOCKED IN — do not re-litigate these

| Layer | Choice | Do not suggest instead |
| :--- | :--- | :--- |
| Core service | Java 21 + Spring Boot 3.3 | Quarkus, Micronaut |
| AI/compute service | Python 3.12 + FastAPI | Django, Flask |
| Frontend | Next.js 15 (App Router) + shadcn/ui + Tailwind | Vite SPA, Remix |
| Database | Postgres 16 + pgvector | A separate vector DB |
| Managed DB (demo) | Supabase Free | — |
| Managed DB (CI) | Neon, single persistent branch (see note below) | — |
| Cache / lock / broker | Redis 7, self-hosted | Memcached |
| Task queue | Celery on Redis only | Celery + RabbitMQ (explicitly rejected — see below) |
| Grammar/parser | Lark | ANTLR |
| Solver | Z3 | cvc5 (noted as fallback only) |
| Object storage | Supabase Storage → R2 later | — |
| Orchestration | Docker Compose | Kubernetes/Helm (deferred, see below) |
| MCP server language | Python (FastMCP), separate process | TypeScript (explicitly rejected — see ADR-0011) |
| Identity | Spring owns it entirely | Supabase Auth (explicitly rejected — two identity systems is a security anti-pattern) |
| PDF text/layout extraction | PyMuPDF (`fitz`), Python side | `pdfplumber`/`pypdf` (insufficient layout/block fidelity) — **see the PyMuPDF/AGPL bullet in this file's Phase 3 summary (under "Current phase") before assuming this choice is licensing-neutral** |
| OCR engine | **Tesseract 5, local dev only** (Apple Silicon) / **PaddleOCR PP-OCRv4, x86 Hetzner prod target** (blueprint §13.3's own default) | Do not treat this as one locked choice — it's a deliberate, documented dev/prod split, not a preference. **See the OCR bullet in this file's Phase 3 summary (under "Current phase") for why**, in short: PaddlePaddle now ships official macOS arm64 wheels, but current (2025-2026) GitHub issues still show it segfaulting/freezing on M1-M3 Macs specifically — a stability class wheel availability doesn't fix. Matches blueprint's own stated fallback ("on non-x86 dev hardware, expect to fall back to Tesseract... on x86 Hetzner, PaddleOCR is fine"). **Revisit at Phase 9 deployment** — same "decided for the current deployment shape only" framing as the PyMuPDF/AGPL note, not a permanent choice for either environment. |

**If you think one of these should change, say so explicitly and ask — don't just start using a different library because it seemed convenient.**

**Correction (found during Phase 3, apps/brain tenancy checkpoint):** this table previously claimed "Neon (branch per PR)" for CI, which was never actually implemented — what exists is a single, persistent CI Neon branch that both `ci-core.yml` and `ci-brain.yml` point at via `secrets.DATABASE_URL` (see each workflow's own comments). The row above now states what's actually true. Genuine branch-per-PR (an ephemeral branch created and migrated per PR, torn down after) is real, not-yet-done future work — see the carried-forward debt list in "Current phase" above — not something to assume already exists when reasoning about CI behavior.

---

## Explicitly deferred — do NOT introduce these yet

These were considered in the blueprint and deliberately cut from MVP. Reintroducing any of them before the stated phase is scope creep, even if it seems like the "more correct" choice in the moment.

| Thing | Deferred to | Why |
| :--- | :--- | :--- |
| Kafka / Redpanda | Phase 8, and only if ≥3 independent event consumers actually exist | Postgres outbox + polling relay is sufficient until then |
| RabbitMQ | Never (cut entirely) | One broker (Redis) for Celery; durability handled via Postgres job-state reconciliation, not a second broker |
| Kubernetes / KEDA / Helm | Phase 9, authored but not operated | Docker Compose on one host is correct at this scale |
| Terraform | Not planned | Negative value for one VPS and one DNS record |
| Stripe / billing | Cut entirely | No product benefit for a portfolio project |
| Sanity CMS | Deferred (YAML playbooks in repo for now) | Standing up a CMS for one author who is also the developer is premature |
| ML risk model (LightGBM) | Phase 9+, only once ≥500 resolved obligations exist | Cold-start: a trained model on no data is worse than a transparent heuristic. Use the deterministic hazard score until then. |
| n8n | Phase 8 | Notifications at MVP = one Spring `NotificationOrchestrator` sending email via SMTP |
| Autonomous evidence agent / MCP writes | Phase 7 | Read-only MCP tools only, until the human-approval flow exists |

---

## Non-negotiable engineering rules

- **Idempotency:** every mutating endpoint accepts `Idempotency-Key`. Every response carries `X-Request-Id`.
- **Tenant isolation:** every tenant-scoped table has `org_id` and an RLS policy from the moment it's created — not retrofitted later. Its repository must implement `TenantScopedRepository` (`apps/core/.../platform/tenancy/`), which `TenantIsolationArchitectureTest` enforces at build time: every public method must be `@Transactional`, and no raw `DataSource`/`Connection` field is allowed. This proves the precondition for isolation, not isolation itself — the actual guarantee is still the RLS policy + `TenantConnectionPreparer`, so write and test each new repository's isolation behavior for real, the ArchUnit rule alone isn't sufficient.
- **No `localStorage`/`sessionStorage` for tokens.** Access tokens live in JS memory only. Refresh tokens are `HttpOnly` cookies.
- **Migrations are immutable once merged.** Corrections are new migrations, never edits to old ones. Use expand/contract for anything destructive.
- **No raw SQL string concatenation, ever.** Parameterized queries only, in both Java and Python.
- **Extraction/compiler output must cite a verbatim source span.** If a candidate obligation's span text doesn't literally appear in the source segment, discard it — don't try to "fix" or reinterpret it.
- **Prompts are versioned files, not inline strings.** Once Phase 4 starts, every prompt lives in `brain/prompts/` with a version and is never edited in place — bump the version.
- **Every LLM call records `model_id`, `prompt_version`, cost, and latency.** Without this, nothing about the AI pipeline is reproducible or debuggable later.

---

## When you're unsure

- If a requested change conflicts with something in this file or the blueprint: **say so and ask**, don't silently comply or silently refuse.
- If you're about to add a new dependency, new service, or new piece of infrastructure not listed in the "locked in" table above: **ask first.**
- If a task seems to require skipping ahead to a later phase to "do it properly": **flag it, propose the minimal Phase-1-appropriate version instead**, and note what's being deferred.
- If tests are failing and the fix isn't obvious: **stop and explain what you found**, rather than working around the test or weakening an assertion to make it pass.

---

## Reference

Full detail for everything above lives in `OBLIGO_ENGINEERING_BLUEPRINT.md`:
- §0 — Critical review and the reasoning behind every deferral above
- §7 — MCP server design (read this before touching `apps/mcp`)
- §10 — Auth (read this before touching `apps/core/identity` or `apps/core/authz`)
- §19.7 — The eval harness and gold-set design (read this before Phase 4)
- §21 — Canonical phase plan, deliverables, and acceptance criteria per phase
- §22 — Repository structure (the exact folder layout to follow)
