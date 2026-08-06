"""Interim shared-secret gate for apps/core -> apps/brain calls.

**What this proves, and what it deliberately does not -- read before
treating this as "auth is handled":** this dependency proves the caller
possesses BRAIN_SERVICE_TOKEN, i.e. that the request reached this endpoint
through a channel that knows the shared secret. It does NOT prove that any
specific `org_id` in the request body is a legitimate claim -- anyone who
holds the secret can still assert any org_id, and this dependency has no
way to tell the difference. It is defense-in-depth against this endpoint
being reachable from somewhere it shouldn't be (a firewall
misconfiguration, an accidental public bind during later deployment
phases), nothing more.

The real fix -- still genuinely missing, not just "TBD" -- is a
short-lived, per-request token that apps/core mints only after its own JWT
verification and RLS-scoped lookup have already established which org_id a
given request is actually allowed to touch, which apps/brain would then
verify cryptographically instead of trusting the body. Blueprint §6.1's
aspirational `core/auth (JWT verify)` module is that real fix; it doesn't
exist yet. See CLAUDE.md's debt list for the same distinction.

Fails closed, not open, if misconfigured: a request against an endpoint
that requires this dependency raises (500, not a silent pass-through) if
BRAIN_SERVICE_TOKEN itself isn't set, rather than treating "no secret
configured" as "no check needed."
"""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException


def require_internal_service_token(x_internal_service_token: str = Header(...)) -> None:
    expected = os.environ.get("BRAIN_SERVICE_TOKEN")
    if not expected:
        raise RuntimeError("BRAIN_SERVICE_TOKEN environment variable is not set")
    if not hmac.compare_digest(x_internal_service_token, expected):
        raise HTTPException(status_code=401, detail="invalid internal service token")
