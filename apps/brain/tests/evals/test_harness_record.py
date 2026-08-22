"""The recorder, proven offline against a fault-injecting transport.

Every test here plants a failure the live run could actually hit -- a 429 on the
first call, a 429 on the SECOND call of a segment (the partial-cassette case), a
budget that runs out mid-set, a stale cassette on resume -- because the recorder
exists to make those cheap, and a suite that only records happy paths would not
show that it does.

No network, no database, no real sleeping.
"""

from __future__ import annotations

import json
import random

import httpx
import pytest

from evals.harness import cassette as cassette_mod
from evals.harness.ratelimit import TokenWindow
from evals.harness.record import Budget, BudgetExhausted, RecordingSession

SEG = ("C02-021", "Antares shall retain samples.")
CTX = dict(model_id="llama-3.3-70b-versatile", prompt_version="v2", guideline_version="v0.28")


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.slept.append(s)
        self.t += s


def ok_body(marker: str = "{}") -> dict:
    return {"id": "x", "object": "chat.completion", "created": 0,
            "model": "llama-3.3-70b-versatile",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": marker},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1500, "completion_tokens": 400, "total_tokens": 1900}}


def scripted(*responses: tuple[int, dict]) -> httpx.MockTransport:
    """A transport that returns each scripted response in turn, then repeats the last."""
    seq = list(responses)
    state = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        status, body = seq[min(state["i"], len(seq) - 1)]
        state["i"] += 1
        headers = {"x-ratelimit-limit-tokens": "12000"}
        if status == 429:
            headers["retry-after"] = "2"
        return httpx.Response(status, json=body, headers=headers)

    return httpx.MockTransport(handler)


def session(tmp_path, transport, *, max_calls=60, calls_per_invoke=1, clock=None):
    clock = clock or FakeClock()

    def invoke(*, segment_id, chat_model):
        for _ in range(calls_per_invoke):
            chat_model(system="s", user="u", model_id=CTX["model_id"])

    return RecordingSession(
        budget=Budget(max_calls=max_calls),
        window=TokenWindow(now=clock.now, sleep=clock.sleep),
        invoke=invoke,
        transport_factory=lambda: transport,
        root=tmp_path, rng=random.Random(1), **CTX,
    ), clock


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "offline-test-never-reaches-the-network")


# --- the happy path, so the failures below mean something --------------------

def test_records_a_cassette_and_writes_it_immediately(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())))
    outcome = s.record_run(*SEG, run=1)
    assert outcome.status == "RECORDED"
    assert cassette_mod.path_for(SEG[0], 1, tmp_path).exists(), "guarantee 2: written now, not at the end"
    loaded = cassette_mod.load(SEG[0], 1, root=tmp_path)
    loaded.verify(segment_text=SEG[1], **CTX)


def test_multi_call_segment_records_every_call_in_order(tmp_path):
    """A repair-loop segment: extraction plus one repair call."""
    s, _ = session(tmp_path, scripted((200, ok_body("first")), (200, ok_body("second"))),
                   calls_per_invoke=2)
    s.record_run(*SEG, run=1)
    cas = cassette_mod.load(SEG[0], 1, root=tmp_path)
    assert len(cas.responses) == 2
    contents = [r["json"]["choices"][0]["message"]["content"] for r in cas.responses]
    assert contents == ["first", "second"]


# --- guarantee 1: the budget halts -------------------------------------------

def test_budget_requires_an_explicit_positive_cap():
    with pytest.raises(ValueError, match="explicit positive --max-calls"):
        Budget(max_calls=0)


def test_budget_charges_actual_calls_not_invocations(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())), calls_per_invoke=3)
    s.record_run(*SEG, run=1)
    assert s.budget.used == 3, "a segment that made three calls costs three"


def test_budget_exhaustion_halts_the_run_and_keeps_what_was_recorded(tmp_path):
    segments = [(f"S{i:02d}", f"text {i}") for i in range(10)]
    s, _ = session(tmp_path, scripted((200, ok_body())), max_calls=4)
    s.record_all(segments, runs=1)
    written = sorted(p.parent.name for p in tmp_path.rglob("run1.json"))
    assert len(written) == 4, f"exactly the budgeted calls were recorded, got {written}"
    assert any(o.status == "FAILED" and "budget exhausted" in o.detail for o in s.outcomes)
    for seg_id in written:
        cassette_mod.load(seg_id, 1, root=tmp_path)   # each survivor is complete and loadable


# --- guarantee 3: a mid-segment 429 discards the whole run -------------------

def test_a_429_on_the_second_call_leaves_no_partial_cassette(tmp_path):
    """THE case stage 3's under-consumption rule forbids resuming into: the
    extraction call succeeded, the repair call was rate limited. The partial
    recording must not reach disk."""
    s, clock = session(tmp_path, scripted((200, ok_body("first")), (429, {"error": "rate limited"})),
                       calls_per_invoke=2)
    outcome = s.record_run(*SEG, run=1)
    assert outcome.status == "FAILED"
    assert not cassette_mod.path_for(SEG[0], 1, tmp_path).exists(), (
        "a partial cassette is not a recording of anything and must never be written"
    )
    assert outcome.attempts == 3, "retried to the cap before giving up"


def test_a_transient_429_is_retried_and_then_succeeds(tmp_path):
    responses = iter([(429, {"error": "rate limited"}), (200, ok_body())])
    last = {"v": (200, ok_body())}

    def handler(request):
        try:
            last["v"] = next(responses)
        except StopIteration:
            pass
        status, body = last["v"]
        headers = {"x-ratelimit-limit-tokens": "12000"}
        if status == 429:
            headers["retry-after"] = "2"
        return httpx.Response(status, json=body, headers=headers)

    s, clock = session(tmp_path, httpx.MockTransport(handler))
    outcome = s.record_run(*SEG, run=1)
    assert outcome.status == "RECORDED"
    assert outcome.attempts == 2
    assert clock.slept, "the retry must have backed off, not hammered"


def test_retry_after_header_drives_the_backoff(tmp_path):
    s, clock = session(tmp_path, scripted((429, {"error": "x"})))
    s.record_run(*SEG, run=1)
    assert 2.0 in clock.slept, f"Retry-After: 2 must be honoured, slept {clock.slept}"


def test_a_rate_limited_call_still_consumes_budget(tmp_path):
    """A 429'd call counted against the provider's limit, so it must count
    against ours -- otherwise a rate-limited run silently overruns."""
    s, _ = session(tmp_path, scripted((429, {"error": "x"})))
    s.record_run(*SEG, run=1)
    assert s.budget.used >= 3, "three attempts, each a real call"


# --- guarantee 4: idempotent resume ------------------------------------------

def test_resume_skips_a_cassette_that_exists_and_verifies(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())))
    s.record_run(*SEG, run=1)
    calls_after_first = s.budget.used

    s2, _ = session(tmp_path, scripted((200, ok_body())))
    outcome = s2.record_run(*SEG, run=1)
    assert outcome.status == "SKIPPED"
    assert s2.budget.used == 0, "a resumed run must spend nothing on work already done"
    assert calls_after_first > 0


def test_resume_re_records_a_stale_cassette(tmp_path):
    """A cassette recorded against different segment text answers a question
    that was never asked; replaying it would fabricate a result."""
    s, _ = session(tmp_path, scripted((200, ok_body())))
    s.record_run(*SEG, run=1)

    s2, _ = session(tmp_path, scripted((200, ok_body())))
    outcome = s2.record_run(SEG[0], "COMPLETELY DIFFERENT SEGMENT TEXT", run=1)
    assert outcome.status == "RECORDED", "a stale cassette must be re-recorded, not skipped"
    assert s2.budget.used > 0


def test_resume_after_a_budget_halt_completes_the_set(tmp_path):
    """The realistic recovery path: halt on budget, re-invoke with more, finish."""
    segments = [(f"S{i:02d}", f"text {i}") for i in range(6)]
    first, _ = session(tmp_path, scripted((200, ok_body())), max_calls=3)
    first.record_all(segments, runs=1)
    assert len(list(tmp_path.rglob("run1.json"))) == 3

    second, _ = session(tmp_path, scripted((200, ok_body())), max_calls=60)
    second.record_all(segments, runs=1)
    assert len(list(tmp_path.rglob("run1.json"))) == 6
    assert second.budget.used == 3, "only the three unrecorded segments cost anything"


# --- pacing and provenance ---------------------------------------------------

def test_the_limiter_learns_the_ceiling_from_recorded_headers(tmp_path):
    def handler(request):
        return httpx.Response(200, json=ok_body(), headers={"x-ratelimit-limit-tokens": "6000"})

    s, _ = session(tmp_path, httpx.MockTransport(handler))
    s.record_run(*SEG, run=1)
    assert s.window.ceiling == 6000, "the recorder must feed real headers to the limiter"
    assert s.window.budget == pytest.approx(4800)


def test_reconciliation_uses_the_real_returned_token_count(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())))
    s.record_run(*SEG, run=1)
    assert s.window.in_window() == 1900, "1500 prompt + 400 completion, not the 2,200 estimate"


def test_summary_reports_budget_and_pacing(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())))
    s.record_run(*SEG, run=1)
    text = s.summary()
    assert "recorded=1" in text and "calls=1/60" in text and "ceiling_observed=12000" in text


def test_three_runs_produce_three_separate_cassettes(tmp_path):
    s, _ = session(tmp_path, scripted((200, ok_body())))
    s.record_all([SEG], runs=3)
    for run in (1, 2, 3):
        cassette_mod.load(SEG[0], run, root=tmp_path)
    assert s.budget.used == 3


# --- regressions for the two bugs the fault-injection tests exposed ----------

def test_a_real_429_reaches_the_retry_path_not_an_uncaught_httpstatuserror(tmp_path):
    """REGRESSION. groq.complete() calls raise_for_status(), so a 429 arrives as
    an httpx.HTTPStatusError -- it never reaches a status-code check placed after
    the invoke() call. The first version of the recorder inspected captured calls
    only after the try block, which made the ENTIRE 429 contingency dead code:
    backoff, retry and discard-partial could not have fired against a real rate
    limit. Caught offline by fault injection; it would otherwise have surfaced
    mid-recording, after budget was spent."""
    s, clock = session(tmp_path, scripted((429, {"error": "rate limited"})))
    outcome = s.record_run(*SEG, run=1)
    assert outcome.status == "FAILED", "must be a handled failure, not an escaped exception"
    assert outcome.attempts == 3
    assert clock.slept, "the retry path must have run"


def test_a_non_429_http_error_is_not_swallowed_by_the_retry_path(tmp_path):
    """The 429 conversion must not turn every HTTP error into a rate-limit retry."""
    s, _ = session(tmp_path, scripted((500, {"error": "server exploded"})))
    with pytest.raises(httpx.HTTPStatusError):
        s.record_run(*SEG, run=1)


def test_the_final_paid_for_run_is_written_before_the_budget_halts(tmp_path):
    """REGRESSION. charge() used to raise from inside _record_once's `finally`,
    which fired BEFORE record_run wrote the cassette -- so the last run, already
    completed and already paid for, was discarded. Guarantee 1 was destroying
    guarantee 2. Exhaustion is now checked at the start of the NEXT run."""
    segments = [(f"S{i:02d}", f"text {i}") for i in range(5)]
    s, _ = session(tmp_path, scripted((200, ok_body())), max_calls=3)
    s.record_all(segments, runs=1)
    written = sorted(p.parent.name for p in tmp_path.rglob("run1.json"))
    assert written == ["S00", "S01", "S02"], (
        f"every call paid for must have produced a cassette, got {written}"
    )
    assert s.budget.used == 3
