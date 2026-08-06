"""Pure-unit coverage of the interim shared-secret gate (no infra needed --
tests/api/test_segment_source.py's
test_segment_source_rejects_requests_without_a_valid_internal_service_token
covers the same behavior through the real HTTP route, but that one only
runs with real Neon/Supabase credentials set; this always runs).
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from obligo_brain.platform.security.internal_auth import require_internal_service_token


def test_correct_token_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAIN_SERVICE_TOKEN", "correct-secret")
    require_internal_service_token(x_internal_service_token="correct-secret")


def test_wrong_token_is_rejected_with_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAIN_SERVICE_TOKEN", "correct-secret")
    with pytest.raises(HTTPException) as exc_info:
        require_internal_service_token(x_internal_service_token="wrong-secret")
    assert exc_info.value.status_code == 401


def test_missing_configured_token_fails_closed_not_open(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRAIN_SERVICE_TOKEN", raising=False)
    with pytest.raises(RuntimeError):
        require_internal_service_token(x_internal_service_token="anything")
