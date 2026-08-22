"""Sliding-window token-rate limiter and a capturing transport, for stage 4's
one live recording run.

WHY A SLIDING WINDOW AND NOT A FLAT INTERVAL. The eval pilot proved a flat
inter-call interval unsafe by token math: 13 calls in 37.9s is a
sustained-equivalent ~25,700 tokens/min against a measured 12,000 TPM ceiling
-- 2.14x over. The pilot's clean run at that pace was unused burst capacity
absorbing a short burst, not evidence the rate was sustainable. A window keyed
on real token counts measures the thing the ceiling actually constrains.

THE CEILING IS DISCOVERED, NEVER HARDCODED. Groq returns
`x-ratelimit-limit-tokens` on EVERY response, so the limiter re-reads it from
each call and adapts. The bootstrap value is only a starting guess for the
first call; from then on the limiter tracks whatever the account's real, current
limit turns out to be -- including a limit that changes mid-run. This matters
because the pilot's own measured figures (12,000 TPM / 1,000 RPD) contradict
blueprint section 13.3's stated ~6,000 / ~14,400 in OPPOSITE directions, so
neither number deserves to be trusted as a constant.

RESERVE THEN RECONCILE. Output length is not knowable before a call, so the
limiter reserves a conservative estimate, then corrects the window entry with
the real `prompt_tokens + completion_tokens` the adapter already returns. The
reservation is what prevents a burst; the reconciliation is what keeps the
window honest over time.

Clock and sleep are injected so the tests run against a fake clock -- a limiter
whose tests really sleep is a limiter nobody runs.
"""

from __future__ import annotations

import json as jsonlib
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

import httpx

BOOTSTRAP_TPM = 12_000        # the pilot's measured figure, used only until the first response
DEFAULT_SAFETY = 0.80         # deliberate headroom: the ceiling is one account read, not a law
WINDOW_SECONDS = 60.0


@dataclass
class TokenWindow:
    """A 60-second sliding window of token spend, with a ceiling that adapts."""

    ceiling: int = BOOTSTRAP_TPM
    safety: float = DEFAULT_SAFETY
    now: Callable[[], float] = field(default=lambda: __import__("time").monotonic())
    sleep: Callable[[float], None] = field(default=lambda s: __import__("time").sleep(s))
    smooth: bool = True           # spread calls evenly instead of bursting -- see reserve()
    _entries: deque = field(default_factory=deque)   # (timestamp, tokens)
    ceiling_observations: list[int] = field(default_factory=list)
    total_slept: float = 0.0
    _last_call_at: float | None = None

    @property
    def budget(self) -> float:
        return self.ceiling * self.safety

    def _evict(self) -> None:
        cutoff = self.now() - WINDOW_SECONDS
        while self._entries and self._entries[0][0] <= cutoff:
            self._entries.popleft()

    def in_window(self) -> int:
        self._evict()
        return sum(t for _, t in self._entries)

    def observe_ceiling(self, headers: dict[str, str]) -> None:
        """Adapts to the account's real, current limit. Called for every response,
        so a limit that differs from the bootstrap -- or changes mid-run -- is
        picked up without a manual re-check."""
        raw = headers.get("x-ratelimit-limit-tokens")
        if raw is None:
            return
        try:
            observed = int(raw)
        except ValueError:
            return
        if observed > 0:
            self.ceiling_observations.append(observed)
            self.ceiling = observed

    def min_interval(self, estimate: int) -> float:
        """Even spacing implied by the budget: at `estimate` tokens per call,
        budget/estimate calls fit in a 60s window, so they belong 60/(that) apart."""
        if not self.smooth or estimate <= 0:
            return 0.0
        calls_per_window = max(1.0, self.budget / estimate)
        return WINDOW_SECONDS / calls_per_window

    def reserve(self, estimate: int) -> float:
        """Blocks until `estimate` fits under the budget AND the smoothing
        interval has elapsed. Returns seconds slept.

        SMOOTHING (approved 2026-08-22). A pure sliding window is SAFE -- it
        never exceeds the windowed budget -- but it is bursty: it admits calls
        back to back until the window fills, then stalls for a full 60s. That
        sawtooth is a smaller version of the exact pattern that earned the eval
        pilot a real 429, and nothing has ever verified whether Groq enforces a
        burst limit separately from the measured TPM ceiling. Spreading calls
        evenly costs nothing -- a TPM-bound run takes the same wall clock either
        way -- so the burst is removed rather than assumed harmless.
        """
        slept = 0.0
        if self._last_call_at is not None:
            gap = self.now() - self._last_call_at
            wait = self.min_interval(estimate) - gap
            if wait > 0:
                self.sleep(wait)
                slept += wait
        while True:
            self._evict()
            if not self._entries or self.in_window() + estimate <= self.budget:
                now = self.now()
                self._entries.append([now, estimate])
                self._last_call_at = now
                self.total_slept += slept
                return slept
            # sleep exactly until the oldest entry leaves the window
            wait = max(0.01, (self._entries[0][0] + WINDOW_SECONDS) - self.now())
            self.sleep(wait)
            slept += wait

    def reconcile(self, actual: int) -> None:
        """Replaces the most recent reservation with the real token count."""
        if self._entries:
            self._entries[-1][1] = actual

    def sustained_rate(self) -> float:
        return self.in_window() / WINDOW_SECONDS * 60.0


@dataclass
class CapturedCall:
    status_code: int
    json: Any
    headers: dict[str, str]


class CapturingTransport(httpx.BaseTransport):
    """Wraps a real transport and records each response's status, body and headers.

    groq.complete() parses a ChatCompletion and discards the raw body -- but a
    cassette must store the raw JSON to replay, and the limiter needs the
    rate-limit headers. Both are only available at the transport layer, which is
    why this exists rather than a wrapper around complete().
    """

    def __init__(self, inner: httpx.BaseTransport) -> None:
        self._inner = inner
        self.calls: list[CapturedCall] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = self._inner.handle_request(request)
        response.read()
        try:
            body = jsonlib.loads(response.content)
        except ValueError:
            body = {"_unparseable_body": response.text}
        self.calls.append(
            CapturedCall(
                status_code=response.status_code,
                json=body,
                headers={k.lower(): v for k, v in response.headers.items()},
            )
        )
        return response


def backoff_delay(attempt: int, retry_after: str | None, rng: random.Random | None = None) -> float:
    """Retry-After when the server sends one, else exponential with jitter.

    The server's own number is authoritative when present: guessing shorter
    earns another 429, and guessing longer wastes the recording window.
    """
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    rng = rng or random.Random()
    return min(60.0, (2.0 ** attempt)) * (1.0 + rng.random() * 0.25)
