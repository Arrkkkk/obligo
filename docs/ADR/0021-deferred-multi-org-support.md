# ADR-0021: Defer multi-org support — invitation acceptance rejects a second org membership

## Status

Accepted.

## Context

Every Google sign-in unconditionally auto-provisions a personal org
(`PersonalOrgProvisioningService`, §10.8). That means there is no "brand
new user with no org yet" state reachable through the real product: by the
time anyone is authenticated at all, they already have exactly one org
membership.

Invitations (§10.8) exist so an admin can bring someone else into their
org. But given the above, accepting an invitation always means gaining a
**second** membership for an already-provisioned user — there's no
first-time-user case to fall back on.

`OrgMembershipRepository.findByUserId` assumes exactly one row
(`queryForObject`). It's used by normal sign-in and by `/auth/refresh` to
decide which org to mint an access token for. If invitation acceptance
inserted a second `org_members` row, the user's very next ordinary
`/auth/refresh` call would throw `IncorrectResultSizeDataAccessException`
and return a 500 — not a graceful degradation, a crash in an unrelated,
already-shipped code path, triggered by a feature that hadn't even
originally been designed with that in mind.

## Options considered

**Option A — thread a "default org" concept through the token-minting path.**
Change `findByUserId` to pick the earliest-created membership (the user's
personal org, always created first) instead of requiring exactly one row;
add a narrow `findByOrgAndUser(orgId, userId)` used only by the accept
endpoint, which would mint its response token scoped to the *just-accepted*
org explicitly rather than the default. Normal sign-in/refresh would keep
landing on the user's personal org unchanged; the newly-joined org would
only be reachable via the token `/accept` itself returns, until a real
`switch-org` endpoint existed.

This was the author's original proposal. Rejected for now: it quietly
introduces a session-model concept (an "active org" distinct from "all
orgs this user belongs to") as a side effect of building invitations,
without deliberately designing the part that actually matters —
`POST /auth/switch-org` (§10.4), how the frontend would expose org
switching, and what happens to a cached/in-flight access token when the
active org changes underneath it. None of that is invitations' problem to
solve, and backing into a piece of it here means the eventual real
multi-org feature inherits undocumented assumptions from this ADR instead
of a clean-slate design.

**Option B (chosen) — invitation acceptance rejects if the user already has any org membership.**
`InvitationService.accept()` checks `OrgMembershipRepository.existsForUserId`
(new, strictly additive — `findByUserId`'s contract and every existing
caller are untouched) and returns `409 Conflict` with a clear message if
the accepting user already belongs to an org. No new membership is
created; the user's existing membership is provably untouched (see
`InvitationAcceptanceTest#acceptingWhenAlreadyBelongingToAnOrgIsRejectedWithoutTouchingExistingMembership`).

## Decision

Go with Option B. The invariant "every user has at most one org
membership" stays literally true everywhere in the system except one
narrow, explicit, tested rejection path — instead of becoming a lie that
most existing code (`MeController`, `AuthController.refresh`) silently
doesn't handle.

## Consequences

- **Real-world impact today: invitation acceptance is effectively
  unreachable through the actual product.** Because sign-in always
  auto-provisions a personal org first, there is currently no way for a
  real user to reach the authenticated `/invitations/{token}/accept`
  endpoint while eligible to accept — they will always already have their
  own org and get `409`. The endpoint is real, correct, and tested (via
  test fixtures that construct a bare `users` row without going through
  provisioning, deliberately bypassing the auto-org-creation path to
  exercise accept() in isolation), but it has no legitimate caller yet
  outside tests. It becomes usable the moment multi-org support (below)
  ships.
- Creating an org for a *new* invitee is also not solved by this ADR —
  today, signing in via Google always creates a personal org, invitation
  or not. A "join this org, don't create your own" first-sign-in path is
  part of the eventual multi-org design, not built here.
- No regression risk: every existing sign-in/refresh code path is
  unchanged, because `findByUserId` is unchanged.

## Eventual shape (when multi-org is actually built)

This is deliberately not built now, but roughly:

1. `OrgMembershipRepository.findByUserId` (or a renamed equivalent) returns
   `List<OrgMembership>` instead of assuming one row.
2. A notion of "active org" per session — likely the earliest-created
   (personal) org by default, consistent with today's only real case.
3. `POST /auth/switch-org` (§10.4): mints a new access token scoped to a
   different org the caller is already a member of; invalidates nothing
   server-side (access tokens are short-lived by design), just changes
   what the *next* one carries.
4. `InvitationService.accept()` drops the `existsForUserId` rejection,
   inserts the new membership, and mints a token scoped to the
   newly-accepted org directly (this part doesn't change — it was already
   designed this way; only the guard in front of it is removed).
5. Frontend: an org switcher, and a decision about what happens to
   in-flight requests using a token for an org the user has switched away
   from (nothing, in practice — the token remains valid for whatever it
   was scoped to until it expires, same as any other access token).
6. First-sign-in-via-invitation (no personal org, join directly): needs
   `PersonalOrgProvisioningService` to become invitation-aware, so a brand
   new user landing via an invite link joins the invited org instead of
   unconditionally getting a personal one.
