"""Token limiter and capturing transport, proven offline against a fake clock
and fault-injected responses. No real sleeping, no network.

The load-bearing test is test_the_pilots_actual_failure_is_now_prevented: it
replays the exact burst the eval pilot ran (13 calls at ~2,000 tokens in 37.9s,
a sustained-equivalent ~25,700 tokens/min against a 12,000 ceiling) and asserts
the limiter now paces it under budget. A limiter that only passes synthetic
cases would not tell us it fixed the thing it was built for.
"""

from __future__ import annotations

import random

import httpx
import pytest

from evals.harness.ratelimit import (
    BOOTSTRAP_TPM, CapturingTransport, TokenWindow, backoff_delay,
)


class FakeClock:
    def __init__(self) -> None:
        self.t = 1000.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.t += seconds

    def advance(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def window(clock: FakeClock) -> TokenWindow:
    return TokenWindow(now=clock.now, sleep=clock.sleep)


# --- the window ------------------------------------------------------------

def test_calls_under_budget_never_sleep(window, clock):
    for _ in range(4):
        assert window.reserve(2_000) == 0.0
    assert clock.slept == []
    assert window.in_window() == 8_000


def test_a_call_that_would_exceed_budget_sleeps_until_the_window_frees(window, clock):
    """Budget is 80% of 12,000 = 9,600. Four 2,000-token calls fit; the fifth
    must wait for the first to age out of the 60s window."""
    for _ in range(4):
        window.reserve(2_000)
    slept = window.reserve(2_000)
    assert slept > 0, "the fifth call must be paced, not admitted"
    assert window.in_window() <= window.budget


def test_entries_age_out_after_sixty_seconds(window, clock):
    window.reserve(9_000)
    assert window.in_window() == 9_000
    clock.advance(61)
    assert window.in_window() == 0
    assert window.reserve(9_000) == 0.0, "a fresh window admits immediately"


def test_reconcile_replaces_the_estimate_with_the_real_count(window):
    window.reserve(2_200)
    assert window.in_window() == 2_200
    window.reconcile(1_310)          # the call was smaller than reserved
    assert window.in_window() == 1_310, "the window must track real spend, not guesses"


def test_reconcile_upward_is_also_honoured(window):
    window.reserve(2_200)
    window.reconcile(5_000)          # the model returned far more than estimated
    assert window.in_window() == 5_000


# --- the ceiling adapts (D2's question) -------------------------------------

def test_ceiling_is_discovered_from_response_headers_not_hardcoded(window):
    assert window.ceiling == BOOTSTRAP_TPM
    window.observe_ceiling({"x-ratelimit-limit-tokens": "6000"})
    assert window.ceiling == 6_000
    assert window.budget == pytest.approx(4_800), "80% of the OBSERVED ceiling, not the bootstrap"


def test_a_ceiling_change_mid_run_is_picked_up(window):
    window.observe_ceiling({"x-ratelimit-limit-tokens": "30000"})
    assert window.budget == pytest.approx(24_000)
    window.observe_ceiling({"x-ratelimit-limit-tokens": "12000"})
    assert window.budget == pytest.approx(9_600)
    assert window.ceiling_observations == [30_000, 12_000]


@pytest.mark.parametrize("headers", [{}, {"x-ratelimit-limit-tokens": "not-a-number"},
                                     {"x-ratelimit-limit-tokens": "0"}])
def test_a_missing_or_malformed_header_leaves_the_ceiling_untouched(window, headers):
    window.observe_ceiling(headers)
    assert window.ceiling == BOOTSTRAP_TPM


def test_a_lower_discovered_ceiling_immediately_tightens_pacing(window, clock):
    """If the real limit turns out to be half the bootstrap, calls that were
    admitted freely must start being paced."""
    window.observe_ceiling({"x-ratelimit-limit-tokens": "6000"})
    window.reserve(2_000)
    window.reserve(2_000)
    assert window.reserve(2_000) > 0, "budget is now 4,800; the third call must wait"


# --- the pilot's real failure ------------------------------------------------

def test_the_pilots_actual_failure_is_now_prevented(window, clock):
    """The eval pilot made 13 calls in 37.9s with no pacing and hit a real 429.
    At ~2,000 tokens each that is ~26,000 tokens in 37.9s -- a sustained rate of
    ~41,000/min, far over the 12,000 ceiling. Replayed here, the limiter must
    pace it so the window never exceeds budget."""
    peak = 0
    for _ in range(13):
        window.reserve(2_000)
        window.reconcile(2_000)
        peak = max(peak, window.in_window())
    assert peak <= window.budget, f"window peaked at {peak}, over budget {window.budget}"
    assert window.sustained_rate() <= window.ceiling
    assert clock.slept, "an unpaced 13-call burst must have been slowed"


def test_a_full_recording_run_stays_under_the_ceiling(window, clock):
    """46 calls -- the pilot-rate estimate for 12 segments x 3 runs."""
    for _ in range(46):
        window.reserve(2_200)
        window.reconcile(1_900)
        assert window.in_window() <= window.budget


# --- capturing transport (D4) ------------------------------------------------

def _mock(status: int, body: dict, headers: dict | None = None) -> httpx.MockTransport:
    return httpx.MockTransport(
        lambda request: httpx.Response(status_code=status, json=body, headers=headers or {})
    )


def test_capturing_transport_records_status_body_and_headers():
    inner = _mock(200, {"choices": [{"message": {"content": "hi"}}]},
                  {"x-ratelimit-limit-tokens": "12000", "x-ratelimit-remaining-tokens": "9500"})
    transport = CapturingTransport(inner)
    client = httpx.Client(transport=transport)
    response = client.post("https://api.groq.com/openai/v1/chat/completions", json={})

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "hi", (
        "the caller must still receive a fully readable response"
    )
    assert len(transport.calls) == 1
    captured = transport.calls[0]
    assert captured.status_code == 200
    assert captured.json["choices"][0]["message"]["content"] == "hi"
    assert captured.headers["x-ratelimit-limit-tokens"] == "12000"


def test_capturing_transport_records_each_call_in_order():
    bodies = iter([{"n": 1}, {"n": 2}, {"n": 3}])
    inner = httpx.MockTransport(lambda r: httpx.Response(200, json=next(bodies)))
    transport = CapturingTransport(inner)
    client = httpx.Client(transport=transport)
    for _ in range(3):
        client.post("https://x/y", json={})
    assert [c.json["n"] for c in transport.calls] == [1, 2, 3]


def test_capturing_transport_records_a_429_rather_than_swallowing_it():
    """The recorder needs to SEE the 429 to back off; the transport must not
    hide it or raise on its own."""
    transport = CapturingTransport(_mock(429, {"error": "rate limited"}, {"retry-after": "8"}))
    client = httpx.Client(transport=transport)
    response = client.post("https://x/y", json={})
    assert response.status_code == 429
    assert transport.calls[0].status_code == 429
    assert transport.calls[0].headers["retry-after"] == "8"


def test_capturing_transport_survives_a_non_json_body():
    inner = httpx.MockTransport(lambda r: httpx.Response(502, text="<html>bad gateway</html>"))
    transport = CapturingTransport(inner)
    httpx.Client(transport=transport).post("https://x/y", json={})
    assert "_unparseable_body" in transport.calls[0].json


# --- backoff (D3) -------------------------------------------------------------

def test_retry_after_header_is_authoritative_when_present():
    assert backoff_delay(attempt=0, retry_after="12") == 12.0
    assert backoff_delay(attempt=5, retry_after="3") == 3.0, (
        "the server's own number wins over our exponential guess"
    )


def test_backoff_is_exponential_with_jitter_when_no_header():
    rng = random.Random(7)
    delays = [backoff_delay(attempt=i, retry_after=None, rng=rng) for i in range(5)]
    assert delays == sorted(delays), "must increase with attempt"
    assert all(2.0 ** i <= d <= 2.0 ** i * 1.25 for i, d in enumerate(delays))


def test_backoff_is_capped():
    assert backoff_delay(attempt=20, retry_after=None) <= 60.0 * 1.25


def test_a_malformed_retry_after_falls_back_to_exponential():
    assert backoff_delay(attempt=2, retry_after="soon") >= 4.0
