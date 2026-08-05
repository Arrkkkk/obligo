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
- `source_versions`/versioning (§11.3) is deliberately not built yet — `sources.storage_key` hardcodes `v1`, documented in V10's migration comment. This is the one item from the earlier deferred list still actually deferred; the rest (below) are now done.
- PDF structural checks (§11.6) beyond magic-byte sniffing, using Apache PDFBox 3.0.7 (`PdfStructuralValidator`) — confirmed Apache 2.0, zero known CVEs at this version per OSV.dev, and the only mature non-AGPL PDF-parsing library in the JVM ecosystem (iText's license ruled it out) before adding it as a dependency. Active-content rejection (embedded JavaScript, launch actions, embedded file attachments) is a flat scan of every indirect object in the file's xref table (`COSDocument.getXrefTable()`/`getObjectFromPool()`), not a walk of the high-level action tree — every action, wherever it's referenced from, ends up as an indirect object this scan sees, so it isn't fooled by an action dictionary missing the often-optional `/Type /Action` key. Decompression-bomb guard is one guard with three components (confirmed from blueprint's own wording, not two separate checks): page count ≤500 (blueprint's own number), a 200:1 decoded-bytes-to-file-size ratio cap plus an absolute 500 MB decoded-bytes ceiling — computed via bounded chunked reads that abort the instant either cap is crossed, so measuring the ratio never itself buffers a bomb to completion — and a 10 s hard timeout on the whole structural-check phase. Proven with PDFBox-generated fixtures, not hand-written ones: a `"%PDF-1.4\n..."` byte string passes magic-byte sniffing but isn't a real, structurally valid PDF PDFBox can parse, which broke the existing happy-path tests the instant structural validation was added — the fix was the test fixture, not the validator (`PdfTestFixtures`, generated via PDFBox itself). Real embedded-JS PDF, real high-ratio "bomb" PDF, and a real tampered-hash upload are all proven end to end against real Supabase Storage (`SourceUploadFlowTest`), plus a faster, more exhaustive pure-unit suite (`PdfStructuralValidatorTest`) covering the validator's own logic with no infrastructure needed.
- Server-side SHA-256 recomputation (§11.6) is a **deliberate deviation from, not an implementation of, blueprint's two-tier design** — blueprint splits this into synchronous verification under 20 MB and an async worker above that; this codebase recomputes synchronously for every file up to the full 50 MB cap instead, since no worker infrastructure exists yet and SHA-256 over 50 MB costs on the order of 100–300 ms in Java, trivial next to the download itself. Same honest-framing pattern as `TenantScopedRepository`'s precondition-not-guarantee note: said plainly so a future reader doesn't mistake "we hash everything synchronously now" for "we built the async tier and just haven't switched it on."
- **Accepted, unmitigated gap: PDF structural validation runs in-process, not sandboxed.** Blueprint §11.6 calls for PDF parsing to happen in an isolated worker with no network egress and a read-only filesystem; none of that exists yet, so `PdfStructuralValidator` runs Apache PDFBox directly against untrusted, potentially-malicious upload bytes inside the main Spring process. Its 10 s timeout is the only mitigation against a parser-level denial-of-service; there is no isolation at all against a parser-level memory-safety issue. Documented in its own bullet, not folded into a longer paragraph, because this is exactly the kind of thing a future security review needs to find in three seconds.
- `SourceUploadService.commit()` restructured from one `@Transactional` method into three phases (`SourceCommitGateway.gatekeep` → unlocked verification → `SourceCommitGateway.finalizeVerification`). **Performance-motivated:** once commit started downloading the full file and running PDFBox against it (up to the 10 s timeout) instead of just a HEAD and a 5-byte range GET, holding `findByIdForUpdate`'s row lock across that much external work risked exhausting this app's small Hikari pool (5 connections; 1 in tests) under concurrent large-file commits. Releasing the lock between phases reopens a race that the old single-transaction design closed for free — Postgres fully serialized concurrent `commit()` calls on the same source via the held lock, with no redundant work and no bug. That reopened race is a new failure mode this restructuring introduces, not a pre-existing bug it fixes; `finalizeVerification`'s `WHERE status = 'PENDING'` guard plus its zero-rows-affected reconciliation read is the new, deliberate mitigation for the window the restructuring itself opens.
- **Separate, correctness-critical finding — independent of the performance reasoning above, not a detail of it:** the three phases could not be implemented as private methods on `SourceUploadService` calling each other via `this.`. `@Transactional` is proxy-based AOP, and a proxy cannot intercept self-invocation — `this.gatekeep(...)` from inside the same class would have silently skipped the transaction entirely: no exception, `app.org_id` never set, RLS failing closed on every call (empty results, not a leak, but a completely broken feature that looks like a data problem, not a code problem). This is why `SourceCommitGateway` had to become a genuinely separate Spring bean — that requirement would hold even if the connection-pool concern above didn't exist at all. General rule worth remembering for this codebase, not just for this feature: the moment a method needing `@Transactional` is called via `this.` from within the same class, the annotation silently does nothing — the fix is always a separate bean, never a private method. Tenant isolation across all three phases was walked through explicitly as part of verifying this split, not assumed: org ownership is established exactly once (phase 1's `WHERE org_id = ?` + RLS), the unlocked middle phase runs zero SQL and operates only on an in-memory snapshot plus a storage key that already has `org_id` baked into its path, and phase 3 takes `orgId` as a plain threaded-through parameter, never re-derived. `TenantContext`'s Javadoc now carries a tripwire comment for this: the guarantee holds only because every step runs synchronously on one request thread, and breaks silently (not an exception — `TenantContext.get()` returns `null`, RLS fails closed) the moment anything in a flow like this crosses a thread pool boundary.
- **Regression caught and fixed, not a normal feature note:** `BlobStoreConfig`'s bean originally called `requireEnv("SUPABASE_URL")` unconditionally at bean-construction time, which Spring evaluates for every context load regardless of whether a given test touches storage. The first CI run after this slice landed proved it the hard way — 25 failures across unrelated test classes (`TenantIsolationTest` included), because the whole `ApplicationContext` failed to start the moment `SUPABASE_URL` was unset, before the CI secrets existed. This directly violated the pattern Phase 2 already established for exactly this situation (`GoogleOAuthClientRegistrationConfig`/`GoogleCredentialsPresentCondition` — no bean at all when credentials are absent, so the app boots fine and the feature activates once they exist) and Standing Principle 1 ("demoable at every commit"). Fixed the same way: `BlobStoreConfig`'s bean is now `@Conditional(SupabaseCredentialsPresentCondition.class)`, and `SourceUploadService` holds `ObjectProvider<BlobStore>` instead of a hard constructor dependency, throwing `BlobStoreUnavailableException` (→ `503`) only at the point an upload-intent or commit call actually needs storage. Proved both directions locally, matching how the Google-optional pattern was originally proved: full suite with `SUPABASE_*` entirely unset — app boots, all non-Supabase tests pass, `SourceUploadFlowTest`/`BucketConfigAgreementTest` skip cleanly (0 failures, 9 skipped); full suite with it set again — 0 skipped, all 127 tests pass. Worth remembering as a general rule, not just for this bean: any `@Bean` method that calls `requireEnv`/throws on missing config must be `@Conditional`, never called unconditionally, or it takes down every test in the module, not just its own.

Carried-forward technical debt from Phase 2 (real, tracked, not blocking Phase 3):
- No public revoke endpoint for invitations — revocation is internal-only (exercised by re-invite rotation, directly testable via the repository). Add a real one if a use case needs it standalone.
- ~~The ArchUnit rule from blueprint §21/§10.9~~ — **Done.** `TenantIsolationArchitectureTest` (`apps/core/src/test/java/.../tenancy/`) enforces two structural rules on any repository implementing the new `TenantScopedRepository` marker interface: every public method must be `@Transactional` (directly or via its class), and no such repository may hold a raw `DataSource`/`Connection` field. `OrganizationRepository` and `SourceRepository` implement the marker so far — the only two tables with RLS enabled; the identity-plane repositories (`users`, `org_members`, `refresh_tokens`, `invitations`) are deliberately excluded, per their own Javadoc. Verified to actually fail the build (throwaway fixture with a non-`@Transactional` method on a `TenantScopedRepository`, caught, removed) and confirmed clean against all existing repositories. Important scope limit, spelled out in `TenantScopedRepository`'s Javadoc: this proves the *precondition* for isolation (a transaction boundary exists for the AOP to intercept, no field bypasses it) — not isolation itself, which is still only proved by real-database integration tests (`TenantIsolationTest`, `SourceUploadFlowTest`).
- The full HTTP-level cross-tenant leakage suite (§17.8) — a handful of real protected endpoints exist now (org member role assignment, invitations, sources upload/commit); worth building out properly as Phase 3 adds more (listing, delete) rather than as a standalone gate.
- Known, deliberately deferred gap: apps/web's dashboard fetches the access token once at load with no silent/scheduled refresh — not a security gap (the token is cryptographically dead at 15 min regardless) but a UX one, worth a note before Phase 6's frontend work.
- No generic Idempotency-Key/X-Request-Id mechanism exists anywhere in `apps/core`, despite both being listed as non-negotiable rules. `POST /api/v1/sources/{id}/commit` has a narrow, domain-level fix (re-calling it on an already-`UPLOADED` source re-verifies via storage but never re-writes, so a retry can't double-process) — that fix covers only that one endpoint. `invite`, `accept`, and role-update still have none, and neither does any response carry `X-Request-Id`. This is a real, systemic gap, not something to consider closed because one endpoint got a narrow workaround. Build the real cross-cutting mechanism (header, response filter, keyed store) as its own dedicated slice before Phase 4, not bundled into unrelated work.

The goal of Phase 3 is turning an uploaded file into layout-aware segments with exact character offsets — the foundation span-grounding (Phase 4) depends on. Per blueprint §21 Phase 3, the acceptance criteria are:
- 10 varied PDFs (born-digital, scanned, mixed, multi-column, table-heavy) produce segments whose offsets round-trip exactly to the source text.
- Malicious fixtures (JS-embedded PDF, zip bomb, macro DOCX, oversized file) are all rejected with correct typed errors. **Partially met** — JS-embedded PDF and an oversized/high-ratio "bomb" PDF are both proven with real fixtures against real Supabase Storage (see progress above); oversized file was already met; macro DOCX is out of scope for this phase (DOCX isn't accepted at all yet — rejected at upload-intent by the MIME allow-list, not by macro-specific detection).
- Duplicate upload (same org, same SHA-256) returns `deduplicated: true` without reprocessing. **Met** — see progress above.
- Ingest progress streams live to a client (SSE).

**Do not start Phase 4 (the compiler/verifier) until these are met.** If you (Claude Code) find yourself writing LLM extraction, grammar, or Z3 code, stop and check whether Phase 3 is actually done first.

Two things worth flagging before writing any code in this phase:
- Storage is presigned-upload-based (§11.2) — the browser uploads directly to Supabase Storage, never through Spring. Spring issues a signed URL, then verifies via a server-side `HEAD` after the client claims to have uploaded. Never trust the client's claim alone. **Done** for the upload flow itself — see progress above.
- File-security controls (§11.6) — magic-byte MIME sniffing, size/page-count caps, decompression-bomb guards, PDF active-content rejection — are not optional hardening to add later. Build them alongside the happy path, since the malicious-fixture acceptance criterion above depends on them existing from the start. **Done** — magic-byte sniffing, size cap, page-count cap, the decompression-bomb guard (ratio + absolute ceiling + timeout), PDF active-content rejection, and server-side sha256 recomputation are all in and proven with real fixtures. See progress above for the one accepted, unmitigated gap (in-process, unsandboxed PDF parsing) and the sha256 deviation-from-blueprint framing.

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
