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

**Phase 2 — Identity, Tenancy & Authorization** (see blueprint §21 / §10). In progress, most of it done and verified.

Done and verified, locally and in CI, against real databases (no mocks):
- Tenant isolation (§10.9) — proven under adversarial connection-pooling conditions (identical pg_backend_pid across two tenant contexts), including two real findings fixed: Neon's owner role has rolbypassrls=true (RLS silently no-ops for it — the app now connects as a dedicated obligo_app role with NOBYPASSRLS), and a touched-then-reset custom GUC reverts to '' not NULL (fixed via NULLIF in the RLS policy).
- Google OAuth2 + PKCE sign-in, RS256 JWT issuance with a real JWKS endpoint (hand-rolled, not a JWT library — the mechanics are the point per §10.2).
- Refresh token rotation with reuse detection — replaying a used token kills the entire family and audits it, tested to the same rigor as tenant isolation.
- Full 5-role RBAC (§10.7) — capability-based, not role-name checks. RoleCapabilities is the single source of truth for the role→capability matrix; capabilities are baked into the JWT's scopes claim at mint time. Deliberate, stated decision: a role change doesn't take effect until the access token naturally expires (≤15 min) — consistent with §10.10's failure-mode table, not a token_epoch mechanism, since that's explicitly [PROD] scope.
- Invitations (§10.8) — email-matched (rejected mismatches are a security check, not UX), single-use, 7-day expiry, re-invite rotates the token rather than resending it. Deliberate scope decision worth knowing about: accepting an invitation while already belonging to an org is rejected with 409 by design, not a bug — multi-org support is deferred, see ADR-0021.

Remaining for Phase 2 sign-off:
- No public revoke endpoint for invitations — revocation is internal-only (exercised by re-invite rotation, and directly testable via the repository). Deliberate: only three endpoints were asked for. Add a real one if a use case needs it standalone.
- The full HTTP-level cross-tenant leakage suite (§17.8) — only one real protected endpoint exists so far (org member role assignment); the suite is worth building out as more endpoints exist, not necessarily as a blocking gate.
- The ArchUnit rule from blueprint §21/§10.9 — "removing the tenant predicate from any repository method fails the build." Not started; every repository built so far scopes correctly by hand, but nothing yet fails the build if a future one doesn't.
- Known, deliberately deferred gap: apps/web's dashboard fetches the access token once at load with no silent/scheduled refresh — not a security gap (the token is cryptographically dead at 15 min regardless) but a UX one, worth a note in docs/TROUBLESHOOTING.md before Phase 6's frontend work.

**Do not start Phase 3 (ingestion/storage) until the remaining acceptance criteria in blueprint §21 are met.**

When this phase is completed and I confirm it, update this section to reflect Phase 3 before continuing work.

---

## Standing principles (do not violate these without asking)

1. **The system must be demoable at every commit.** Don't leave the stack in a broken state overnight.
2. **Deterministic core, probabilistic edge.** Anything a parser, typechecker, or solver can decide must not be decided by an LLM. If you're about to have a model output something that determines correctness (not just a draft/candidate), stop and ask.
3. **One trust boundary, three enforcement layers** for tenant isolation: gateway → application (Hibernate filter + `@PreAuthorize`) → database (RLS). All three, always, once we reach Phase 2.
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
- **Tenant isolation:** every tenant-scoped table has `org_id` and an RLS policy from the moment it's created — not retrofitted later. Every new repository method needs a tenant predicate; there's an ArchUnit rule for this once Phase 2 lands, but don't wait for the rule to write it correctly.
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
