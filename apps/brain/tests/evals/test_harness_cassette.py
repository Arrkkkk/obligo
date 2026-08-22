"""Strict cassette replay: overflow, under-consumption, and every staleness
dimension, each proven by a planted defect rather than by a clean happy path.

A cassette layer that only ever gets well-formed input will pass while silently
reusing responses, replaying a diverged code path, or answering a question the
recording was never asked. Each of those is a way to produce a number the
evidence does not back, so each gets its own failing case.
"""

from __future__ import annotations

import hashlib
import json

import httpx
import pytest

from evals.harness import cassette as C

SEGMENT = "Vendor shall provide technical assistance to AT&T."
SHA = hashlib.sha256(SEGMENT.encode()).hexdigest()


def _resp(marker: str) -> dict:
    return {"status_code": 200, "json": {"choices": [{"message": {"content": marker}}]}}


def make(tmp_path, *, responses=2, segment_sha=SHA, model_id="llama-3.3-70b-versatile",
         prompt_version="v2", guideline_version="v0.28") -> C.Cassette:
    cas = C.Cassette(
        segment_id="C02-021", run=1, model_id=model_id, prompt_version=prompt_version,
        segment_sha256=segment_sha, guideline_version=guideline_version,
        recorded_at="2026-08-22T00:00:00Z",
        responses=tuple(_resp(f"call-{i}") for i in range(responses)),
    )
    C.write(cas, root=tmp_path)
    return cas


def _fire(player: C.StrictPlayer, n: int) -> list[str]:
    client = httpx.Client(transport=player.transport())
    seen = []
    for _ in range(n):
        r = client.post("https://api.groq.com/openai/v1/chat/completions", json={})
        seen.append(r.json()["choices"][0]["message"]["content"])
    return seen


# --- round trip -------------------------------------------------------------

def test_write_then_load_round_trips(tmp_path):
    original = make(tmp_path)
    assert C.load("C02-021", 1, root=tmp_path) == original


def test_responses_are_served_in_recorded_order_once_each(tmp_path):
    player = C.StrictPlayer(make(tmp_path, responses=3))
    assert _fire(player, 3) == ["call-0", "call-1", "call-2"]
    player.assert_fully_consumed()


# --- overflow ---------------------------------------------------------------

def test_overflow_raises_rather_than_reusing_a_response(tmp_path):
    """The repair loop making an unrecorded third call must fail loudly. Reusing
    the last response would feed the extraction answer to a repair call."""
    player = C.StrictPlayer(make(tmp_path, responses=2))
    _fire(player, 2)
    with pytest.raises(C.CassetteOverflow) as exc:
        _fire(player, 1)
    assert "recorded 2 model call(s)" in str(exc.value)
    assert "made 3" in str(exc.value)


# --- under-consumption ------------------------------------------------------

def test_under_consumption_raises(tmp_path):
    """Fewer calls than recorded means the replayed path diverged from the
    recorded one -- a clean-looking run that is not a replay of it."""
    player = C.StrictPlayer(make(tmp_path, responses=3))
    _fire(player, 2)
    with pytest.raises(C.CassetteUnderflow) as exc:
        player.assert_fully_consumed()
    assert "made only 2" in str(exc.value)


def test_zero_calls_against_a_recorded_cassette_is_under_consumption(tmp_path):
    player = C.StrictPlayer(make(tmp_path, responses=1))
    with pytest.raises(C.CassetteUnderflow):
        player.assert_fully_consumed()


# --- staleness, one dimension at a time -------------------------------------

def _verify(cas, **over):
    kwargs = dict(segment_text=SEGMENT, model_id="llama-3.3-70b-versatile",
                  prompt_version="v2", guideline_version="v0.28")
    kwargs.update(over)
    cas.verify(**kwargs)


def test_verify_passes_when_nothing_changed(tmp_path):
    _verify(make(tmp_path))


def test_stale_on_changed_segment_text(tmp_path):
    with pytest.raises(C.StaleCassette, match="segment text changed"):
        _verify(make(tmp_path), segment_text=SEGMENT + " Amended.")


def test_stale_on_changed_model_id(tmp_path):
    with pytest.raises(C.StaleCassette, match="model_id"):
        _verify(make(tmp_path), model_id="some-other-model")


def test_stale_on_changed_prompt_version(tmp_path):
    with pytest.raises(C.StaleCassette, match="prompt_version"):
        _verify(make(tmp_path), prompt_version="v3")


def test_stale_on_changed_guideline_version(tmp_path):
    with pytest.raises(C.StaleCassette, match="guideline_version"):
        _verify(make(tmp_path), guideline_version="v0.29")


def test_all_staleness_problems_are_reported_together(tmp_path):
    """One error per re-record, not one error per attempt."""
    with pytest.raises(C.StaleCassette) as exc:
        _verify(make(tmp_path), segment_text="different", model_id="x",
                prompt_version="v9", guideline_version="v9")
    message = str(exc.value)
    for dimension in ("segment text changed", "model_id", "prompt_version", "guideline_version"):
        assert dimension in message


# --- missing cassettes ------------------------------------------------------

def test_missing_cassette_names_the_3x_requirement(tmp_path):
    make(tmp_path)  # run 1 only
    with pytest.raises(C.CassetteMissing, match="all 3 recorded runs"):
        C.load("C02-021", 2, root=tmp_path)


def test_three_runs_can_hold_genuinely_different_responses(tmp_path):
    """The whole point of 3x: replay must be able to reproduce real recorded
    non-determinism, not three byte-identical copies."""
    for run, marker in ((1, "alpha"), (2, "beta"), (3, "alpha")):
        C.write(C.Cassette(segment_id="C14-076", run=run, model_id="m", prompt_version="v2",
                           segment_sha256=SHA, guideline_version="v0.28",
                           recorded_at="t", responses=(_resp(marker),)), root=tmp_path)
    seen = []
    for run in (1, 2, 3):
        player = C.StrictPlayer(C.load("C14-076", run, root=tmp_path))
        seen.extend(_fire(player, 1))
        player.assert_fully_consumed()
    assert seen == ["alpha", "beta", "alpha"]
    assert len(set(seen)) == 2, "replay must preserve run-to-run variation"


def test_chat_model_closure_drives_the_real_provider_through_the_strict_transport(tmp_path):
    """Exercises chat_model_for() end to end against the REAL provider adapter.

    Added after an earlier draft imported `obligo_brain.models.groq_provider`,
    which does not exist -- the module is `models.providers.groq`. Thirteen
    passing tests missed it because none of them called this closure, so the
    ImportError would first have surfaced during live recording. A seam that is
    never exercised is not covered by the tests that surround it.
    """
    import os
    os.environ.setdefault("GROQ_API_KEY", "cassette-replay-does-not-use-this-value")
    payload = {"id": "x", "object": "chat.completion", "created": 0,
               "model": "llama-3.3-70b-versatile",
               "choices": [{"index": 0, "message": {"role": "assistant", "content": "{}"},
                            "finish_reason": "stop"}],
               "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}
    cas = C.Cassette(segment_id="C02-021", run=1, model_id="llama-3.3-70b-versatile",
                     prompt_version="v2", segment_sha256=SHA, guideline_version="v0.28",
                     recorded_at="t", responses=({"status_code": 200, "json": payload},))
    player = C.StrictPlayer(cas)
    chat = C.chat_model_for(player)
    result = chat(system="s", user="u", model_id="llama-3.3-70b-versatile", temperature=0.0)
    assert result is not None
    player.assert_fully_consumed()

    with pytest.raises(C.CassetteOverflow):
        chat(system="s", user="u", model_id="llama-3.3-70b-versatile", temperature=0.0)
