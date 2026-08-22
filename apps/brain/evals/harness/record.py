"""The recorder: turns live model calls into cassettes, once, under a budget.

This is the only part of the harness that spends non-recoverable resources, so
every mechanism here exists to make a failed run cheap rather than to make a
successful one fast.

FOUR GUARANTEES, each from a specific lesson:

1. THE BUDGET HALTS, IT DOES NOT OVERRUN. `max_calls` is mandatory and is
   decremented per ACTUAL call. When it is exhausted the run stops cleanly and
   everything already recorded stays on disk. The eval pilot approved 30 calls,
   used 13, and stopped only because a 429 crashed it.

2. EACH CASSETTE IS WRITTEN THE MOMENT ITS RUN COMPLETES. The pilot scored and
   wrote only after its whole loop finished, so a mid-run crash discarded eight
   already-successful segments. Nothing here is held in memory for later.

3. A 429 MID-SEGMENT DISCARDS THAT WHOLE RUN -- never a partial resume. A
   cassette is an ordered recording of ONE contiguous execution; if the
   extraction call succeeded and the repair call was rate-limited, the partial
   `responses` list is not a recording of anything. Resuming into it would
   produce a cassette whose replay diverges from any real execution, which is
   exactly what stage 3's strict under-consumption rule refuses.

4. RESUME IS IDEMPOTENT AT (SEGMENT, RUN) GRANULARITY. On restart, a cassette
   that exists AND verifies against the current segment text, model, prompt and
   guideline version is skipped. A stale one is re-recorded, because replaying it
   would answer a question that was never asked.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol, Sequence

import httpx

from evals.harness import cassette as cassette_mod
from evals.harness.ratelimit import CapturingTransport, TokenWindow, backoff_delay

MAX_ATTEMPTS_PER_RUN = 3
DEFAULT_TOKEN_ESTIMATE = 2_200


class BudgetExhausted(RuntimeError):
    """Raised to stop the run cleanly; everything already written stays on disk."""


class RateLimited(RuntimeError):
    def __init__(self, retry_after: str | None) -> None:
        super().__init__("the provider returned 429")
        self.retry_after = retry_after


@dataclass
class Budget:
    max_calls: int
    used: int = 0

    def __post_init__(self) -> None:
        if self.max_calls <= 0:
            raise ValueError(
                "recording requires an explicit positive --max-calls; a run with no cap "
                "cannot halt cleanly, which is how the pilot hit a 429 at call 12"
            )

    @property
    def remaining(self) -> int:
        return self.max_calls - self.used

    @property
    def exhausted(self) -> bool:
        return self.used >= self.max_calls

    def charge(self, calls: int) -> None:
        """Records spend. DELIBERATELY DOES NOT RAISE.

        An earlier version raised here, from inside _record_once's `finally` --
        which fired BEFORE record_run wrote the cassette, so the last run, already
        completed and already paid for, was discarded. That is precisely the loss
        guarantee 2 exists to prevent, reintroduced by the guarantee-1 mechanism.
        Exhaustion is now checked at the START of the next run instead: finish and
        keep what has been paid for, then stop.
        """
        self.used += calls


class Invoke(Protocol):
    """Runs the pipeline for one segment with the supplied chat model. The
    recorder does not care what it returns -- only what calls it provoked."""

    def __call__(self, segment_id: str, chat_model: Callable) -> object: ...


@dataclass
class RunOutcome:
    segment_id: str
    run: int
    status: str                      # RECORDED | SKIPPED | FAILED
    calls: int = 0
    attempts: int = 1
    detail: str = ""


@dataclass
class RecordingSession:
    budget: Budget
    window: TokenWindow
    invoke: Invoke
    transport_factory: Callable[[], httpx.BaseTransport]
    model_id: str
    prompt_version: str
    guideline_version: str
    root: Path | None = None
    rng: random.Random = field(default_factory=random.Random)
    outcomes: list[RunOutcome] = field(default_factory=list)

    # -- one (segment, run) ------------------------------------------------
    def _record_once(self, segment_id: str, segment_text: str, run: int) -> cassette_mod.Cassette:
        capturing = CapturingTransport(self.transport_factory())

        def chat_model(*, system: str, user: str, model_id: str, temperature: float = 0.0):
            from obligo_brain.models.providers import groq as groq_provider

            self.window.reserve(DEFAULT_TOKEN_ESTIMATE)
            result = groq_provider.complete(
                system=system, user=user, model_id=model_id,
                temperature=temperature, transport=capturing,
            )
            if capturing.calls:
                last = capturing.calls[-1]
                self.window.observe_ceiling(last.headers)
            self.window.reconcile(int(result.input_tokens) + int(result.output_tokens))
            return result

        try:
            self.invoke(segment_id=segment_id, chat_model=chat_model)
        except httpx.HTTPStatusError as exc:
            # groq.complete() calls raise_for_status(), so a 429 arrives HERE as an
            # HTTPStatusError -- it never reaches a status check further down. An
            # earlier version only inspected captured calls after the try block,
            # which made the whole 429 contingency dead code: backoff, retry and
            # discard-partial could never have fired against a real rate limit.
            if exc.response.status_code == 429:
                raise RateLimited(exc.response.headers.get("retry-after")) from exc
            raise
        finally:
            # Charged even on failure: a 429'd call still consumed budget and,
            # more importantly, still counted against the provider's rate limit.
            if capturing.calls:
                self.budget.charge(len(capturing.calls))

        # Belt and braces: a 429 that somehow did not raise (a provider adapter
        # that stops calling raise_for_status, say) still must not become a cassette.
        for call in capturing.calls:
            if call.status_code == 429:
                raise RateLimited(call.headers.get("retry-after"))

        return cassette_mod.Cassette(
            segment_id=segment_id, run=run, model_id=self.model_id,
            prompt_version=self.prompt_version,
            segment_sha256=hashlib.sha256(segment_text.encode()).hexdigest(),
            guideline_version=self.guideline_version,
            recorded_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            responses=tuple({"status_code": c.status_code, "json": c.json} for c in capturing.calls),
        )

    def _already_good(self, segment_id: str, segment_text: str, run: int) -> bool:
        try:
            existing = cassette_mod.load(segment_id, run, root=self.root)
            existing.verify(segment_text=segment_text, model_id=self.model_id,
                            prompt_version=self.prompt_version,
                            guideline_version=self.guideline_version)
            return True
        except (cassette_mod.CassetteMissing, cassette_mod.StaleCassette):
            return False

    def record_run(self, segment_id: str, segment_text: str, run: int) -> RunOutcome:
        if self.budget.exhausted:
            raise BudgetExhausted(
                f"call budget exhausted: {self.budget.used}/{self.budget.max_calls} used. "
                "Cassettes already written are complete and will be skipped on resume."
            )
        if self._already_good(segment_id, segment_text, run):
            outcome = RunOutcome(segment_id, run, "SKIPPED", detail="cassette exists and verifies")
            self.outcomes.append(outcome)
            return outcome

        for attempt in range(1, MAX_ATTEMPTS_PER_RUN + 1):
            try:
                cassette = self._record_once(segment_id, segment_text, run)
            except RateLimited as exc:
                # Guarantee 3: the partial recording is DISCARDED, not resumed.
                if attempt == MAX_ATTEMPTS_PER_RUN:
                    outcome = RunOutcome(segment_id, run, "FAILED", attempts=attempt,
                                         detail=f"rate limited on {attempt} attempts")
                    self.outcomes.append(outcome)
                    return outcome
                self.window.sleep(backoff_delay(attempt, exc.retry_after, self.rng))
                continue
            cassette_mod.write(cassette, root=self.root)   # Guarantee 2: written now
            outcome = RunOutcome(segment_id, run, "RECORDED", calls=len(cassette.responses),
                                 attempts=attempt)
            self.outcomes.append(outcome)
            return outcome
        raise AssertionError("unreachable")

    # -- the whole set -----------------------------------------------------
    def record_all(self, segments: Sequence[tuple[str, str]], runs: int = 3) -> list[RunOutcome]:
        try:
            for run in range(1, runs + 1):
                for segment_id, segment_text in segments:
                    self.record_run(segment_id, segment_text, run)
        except BudgetExhausted as exc:
            self.outcomes.append(RunOutcome("-", 0, "FAILED", detail=str(exc)))
        return self.outcomes

    def summary(self) -> str:
        counts = {s: sum(1 for o in self.outcomes if o.status == s)
                  for s in ("RECORDED", "SKIPPED", "FAILED")}
        return (
            f"recorded={counts['RECORDED']} skipped={counts['SKIPPED']} failed={counts['FAILED']} "
            f"calls={self.budget.used}/{self.budget.max_calls} "
            f"ceiling_observed={self.window.ceiling} slept={self.window.total_slept:.0f}s"
        )
