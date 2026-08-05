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

**Phase 3 — Ingestion, Storage & Segmentation** (see blueprint §21 / §11 / §3 Phase 3 deliverables).

Phase 2 (Identity, Tenancy & Authorization) is complete and verified, locally and in CI, against real databases (no mocks):
- Tenant isolation (§10.9) — proven under adversarial connection-pooling conditions (identical `pg_backend_pid` across two tenant contexts). Two real findings fixed along the way: Neon's owner role has `rolbypassrls=true` (RLS silently no-ops for it — the app now connects as a dedicated `obligo_app` role with `NOBYPASSRLS`), and a touched-then-reset custom GUC reverts to `''` not `NULL` (fixed via `NULLIF` in the RLS policy).
- Google OAuth2 + PKCE sign-in, RS256 JWT issuance with a real JWKS endpoint (hand-rolled, not a JWT library — the mechanics are the point per §10.2).
- Refresh token rotation with reuse detection — replaying a used token kills the entire family and audits it, tested to the same rigor as tenant isolation.
- Full 5-role RBAC (§10.7) — capability-based, not role-name checks. `RoleCapabilities` is the single source of truth for the role→capability matrix; capabilities are baked into the JWT's `scopes` claim at mint time. Deliberate, stated decision: a role change doesn't take effect until the access token naturally expires (≤15 min) — consistent with §10.10's failure-mode table, not a `token_epoch` mechanism, since that's explicitly `[PROD]` scope.
- Invitations (§10.8) — email-matched (rejected mismatches are a security check, not UX), single-use, 7-day expiry, re-invite rotates the token rather than resending it. Deliberate scope decision: accepting an invitation while already belonging to an org is rejected with 409 by design, not a bug — multi-org support is deferred, see ADR-0021.

Phase 3 progress so far:
- Presigned upload flow (§11.2) — `sources` table (V10, RLS from creation, `SourceRepository implements TenantScopedRepository`), `POST /api/v1/sources/upload-intent`, `POST /api/v1/sources/{id}/commit`. `BlobStore` port + `SupabaseStorageBlobStore` adapter (§11.1's stated escape hatch to R2 later). Verified against real Neon + real Supabase Storage, no mocks — full upload → real PUT to the signed URL → commit → dedup-on-reupload flow, plus cross-tenant and capability-gating checks.
- File-security controls (§11.6) for this slice specifically: magic-byte MIME sniffing (`%PDF-` signature, via a ranged GET, not the client's declared Content-Type), a size cap, PDF-only rejection. `FileSecurityLimits`'s app-level cap/allow-list is checked against the Supabase bucket's own server-side config (`BucketConfigAgreementTest`, real API call) so the two independent layers can't silently drift apart.
- Real finding, not guessed from docs: Supabase's upload-sign endpoint does not honor a caller-supplied expiry — confirmed by passing `expiresIn` and decoding the returned token, which always carries a fixed ~2h lifetime. Blueprint §11.2 targets 5 min; nothing on our side can tighten a TTL Supabase itself fixes. Three follow-up properties verified live (not assumed) before deciding this was acceptable to document rather than something requiring an app-side mitigation: (1) `upsert:false` makes a second PUT to an already-uploaded key fail with `409 KeyAlreadyExists` and leaves the original content untouched — a leaked URL is dead the instant the legitimate upload lands, regardless of remaining token life; (2) the upload-signing token carries no read scope — the same token fails to `GET` the object it can write; (3) the token's signature is bound to its exact path — it fails with `InvalidSignature` against any other key. So the actual exposure isn't "a leaked URL is live for 2h" — it's narrower: a **pre-upload race on an abandoned intent** (client crashes, tab closes, upload never happens), for as long as that specific token stays valid. `SourceUploadService.commit` now caps that window at 30 min server-side (`MAX_PENDING_AGE`) — a `PENDING` source older than that is rejected with a typed `410 Gone` rather than falling through to storage verification, tested both ways (`commitRejectsAPendingSourceOlderThanTheStalenessThreshold`, `commitStillSucceedsForAPendingSourceUnderTheStalenessThreshold`). This shrinks the abandoned-intent race window to 30 min instead of Supabase's full 2h, but doesn't touch the live case: an attacker who wins the race within that 30 min window can still plant content that satisfies commit's own structural checks (size equality, magic-byte signature) — those checks validate shape, not provenance, and the visible failure this causes on the legitimate client's own PUT (also a `409 KeyAlreadyExists`, same mechanism) is a detection signal, not a prevention. **Final state: bounded, not solved.** No cross-tenant leakage, no standing access, no post-upload risk, and a materially narrower window than the raw 2h token — but a determined attacker who wins a sub-30-minute race on an abandoned intent can still get content past commit's checks. Acceptable for this phase; revisit if content provenance (e.g., a client-side signature Spring could verify) becomes a real requirement.
- Deliberately deferred within this slice, not yet meeting §21 Phase 3's acceptance criteria below: PDF active-content rejection (embedded JS/launch actions), decompression-bomb guard, page-count cap, and server-side sha256 recomputation (blueprint assigns this to an async worker for files under 20 MB — no worker exists yet, see below). `source_versions`/versioning (§11.3) is also not built — `sources.storage_key` hardcodes `v1`, documented in V10's migration comment.

Carried-forward technical debt from Phase 2 (real, tracked, not blocking Phase 3):
- No public revoke endpoint for invitations — revocation is internal-only (exercised by re-invite rotation, directly testable via the repository). Add a real one if a use case needs it standalone.
- ~~The ArchUnit rule from blueprint §21/§10.9~~ — **Done.** `TenantIsolationArchitectureTest` (`apps/core/src/test/java/.../tenancy/`) enforces two structural rules on any repository implementing the new `TenantScopedRepository` marker interface: every public method must be `@Transactional` (directly or via its class), and no such repository may hold a raw `DataSource`/`Connection` field. `OrganizationRepository` and `SourceRepository` implement the marker so far — the only two tables with RLS enabled; the identity-plane repositories (`users`, `org_members`, `refresh_tokens`, `invitations`) are deliberately excluded, per their own Javadoc. Verified to actually fail the build (throwaway fixture with a non-`@Transactional` method on a `TenantScopedRepository`, caught, removed) and confirmed clean against all existing repositories. Important scope limit, spelled out in `TenantScopedRepository`'s Javadoc: this proves the *precondition* for isolation (a transaction boundary exists for the AOP to intercept, no field bypasses it) — not isolation itself, which is still only proved by real-database integration tests (`TenantIsolationTest`, `SourceUploadFlowTest`).
- The full HTTP-level cross-tenant leakage suite (§17.8) — a handful of real protected endpoints exist now (org member role assignment, invitations, sources upload/commit); worth building out properly as Phase 3 adds more (listing, delete) rather than as a standalone gate.
- Known, deliberately deferred gap: apps/web's dashboard fetches the access token once at load with no silent/scheduled refresh — not a security gap (the token is cryptographically dead at 15 min regardless) but a UX one, worth a note before Phase 6's frontend work.
- No generic Idempotency-Key/X-Request-Id mechanism exists anywhere in `apps/core`, despite both being listed as non-negotiable rules. `POST /api/v1/sources/{id}/commit` has a narrow, domain-level fix (re-calling it on an already-`UPLOADED` source re-verifies via storage but never re-writes, so a retry can't double-process) — that fix covers only that one endpoint. `invite`, `accept`, and role-update still have none, and neither does any response carry `X-Request-Id`. This is a real, systemic gap, not something to consider closed because one endpoint got a narrow workaround. Build the real cross-cutting mechanism (header, response filter, keyed store) as its own dedicated slice before Phase 4, not bundled into unrelated work.

The goal of Phase 3 is turning an uploaded file into layout-aware segments with exact character offsets — the foundation span-grounding (Phase 4) depends on. Per blueprint §21 Phase 3, the acceptance criteria are:
- 10 varied PDFs (born-digital, scanned, mixed, multi-column, table-heavy) produce segments whose offsets round-trip exactly to the source text.
- Malicious fixtures (JS-embedded PDF, zip bomb, macro DOCX, oversized file) are all rejected with correct typed errors.
- Duplicate upload (same org, same SHA-256) returns `deduplicated: true` without reprocessing. **Met** — see progress above.
- Ingest progress streams live to a client (SSE).

**Do not start Phase 4 (the compiler/verifier) until these are met.** If you (Claude Code) find yourself writing LLM extraction, grammar, or Z3 code, stop and check whether Phase 3 is actually done first.

Two things worth flagging before writing any code in this phase:
- Storage is presigned-upload-based (§11.2) — the browser uploads directly to Supabase Storage, never through Spring. Spring issues a signed URL, then verifies via a server-side `HEAD` after the client claims to have uploaded. Never trust the client's claim alone. **Done** for the upload flow itself — see progress above.
- File-security controls (§11.6) — magic-byte MIME sniffing, size/page-count caps, decompression-bomb guards, PDF active-content rejection — are not optional hardening to add later. Build them alongside the happy path, since the malicious-fixture acceptance criterion above depends on them existing from the start. **Partially done** — magic-byte sniffing and size cap are in; page-count caps, decompression-bomb guards, and active-content rejection are the deferred items noted above and still need to land before this phase's acceptance criteria are fully met.

When this phase is completed and I confirm it, update this section to reflect Phase 4 before continuing work.

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
| Managed DB (CI) | Neon (branch per PR) | — |
| Cache / lock / broker | Redis 7, self-hosted | Memcached |
| Task queue | Celery on Redis only | Celery + RabbitMQ (explicitly rejected — see below) |
| Grammar/parser | Lark | ANTLR |
| Solver | Z3 | cvc5 (noted as fallback only) |
| Object storage | Supabase Storage → R2 later | — |
| Orchestration | Docker Compose | Kubernetes/Helm (deferred, see below) |
| MCP server language | Python (FastMCP), separate process | TypeScript (explicitly rejected — see ADR-0011) |
| Identity | Spring owns it entirely | Supabase Auth (explicitly rejected — two identity systems is a security anti-pattern) |

**If you think one of these should change, say so explicitly and ask — don't just start using a different library because it seemed convenient.**

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
