"""The condition_raws prompt-alignment check.

Every test plants ONE defect and asserts the check reports exactly that,
including the multi-call repair path -- a cassette's later responses patch
candidates by index, and reading only response 0 would silently answer a
different question than the one asked.

Pure: no database, no network, no cassette files on disk.
"""

from __future__ import annotations

import json

import pytest

from evals.harness import conditions


def _resp(body: dict) -> dict:
    return {"status_code": 200,
            "json": {"choices": [{"message": {"content": json.dumps(body)}}]}}


def _extraction(*condition_lists) -> dict:
    return _resp({"obligations": [
        {"span_text": f"span {i}", "condition_raws": list(c)}
        for i, c in enumerate(condition_lists)
    ]})


def _item(item_id="X-01", segment_id="S-001", conditions=()):
    return {"item_id": item_id, "segment_id": segment_id, "conditions": list(conditions)}


# --- is_if_headed: the punctuation trap ------------------------------------

def test_if_headed_accepts_a_comma_immediately_after_if():
    """PLANTED REGRESSION for a bug this module's author actually shipped in a
    throwaway script: `"If, during the Term..."` splits to the token `"If,"`,
    which != "if". Gold really contains this string, so the naive test
    misclassifies a genuine if-headed condition as non-if and would have
    corrupted the very count this check exists to produce."""
    assert conditions.is_if_headed("If, during the Term of this Agreement, the Parties agree")


@pytest.mark.parametrize("text", ["If the Principal is a natural person", "  if x happens"])
def test_if_headed_true_cases(text):
    assert conditions.is_if_headed(text)


@pytest.mark.parametrize("text", [
    "upon the death or mental incapacity of a Principal",
    "As requested by Client",
    "solely to the extent X",
    "notifying the other party",          # a bare participial, not if-headed
    "",
])
def test_if_headed_false_cases(text):
    assert not conditions.is_if_headed(text)


def test_if_headed_does_not_match_a_word_merely_starting_with_if():
    assert not conditions.is_if_headed("ifthe Principal is a natural person")


# --- multi-call cassettes ---------------------------------------------------

def test_a_repair_patching_condition_raws_is_applied_and_counted():
    """A repair response patches a candidate BY INDEX. Reading response 0 alone
    would report the pre-repair conditions, which no execution ever held."""
    responses = [
        _extraction(["before repair"]),
        _resp({"repairs": [{"index": 0, "condition_raws": ["after repair"]}]}),
    ]
    emitted, touching = conditions.emitted_conditions(responses)
    assert emitted == ["after repair"]
    assert touching == 1


def test_a_repair_patching_another_field_leaves_conditions_alone_and_is_not_counted():
    responses = [
        _extraction(["kept"]),
        _resp({"repairs": [{"index": 0, "temporal_raw": "within 5 days of X"}]}),
    ]
    emitted, touching = conditions.emitted_conditions(responses)
    assert emitted == ["kept"]
    assert touching == 0, "only condition_raws patches may be counted as touching conditions"


def test_an_out_of_range_repair_index_is_ignored_rather_than_crashing():
    responses = [_extraction(["a"]), _resp({"repairs": [{"index": 7, "condition_raws": ["z"]}]})]
    emitted, _ = conditions.emitted_conditions(responses)
    assert emitted == ["a"]


def test_an_unparseable_response_is_skipped_not_fatal():
    bad = {"status_code": 200, "json": {"choices": [{"message": {"content": "not json"}}]}}
    emitted, _ = conditions.emitted_conditions([_extraction(["a"]), bad])
    assert emitted == ["a"]


def test_conditions_are_whitespace_normalised_before_comparison():
    emitted, _ = conditions.emitted_conditions([_extraction(["  upon   the   death  "])])
    assert emitted == ["upon the death"]


# --- verdicts ---------------------------------------------------------------

def test_narrow_reading_when_no_non_if_condition_is_ever_emitted():
    items = [_item(conditions=["upon the death of X", "As requested by Y"])]
    cass = {"S-001": [[_extraction([])], [_extraction([])], [_extraction([])]]}
    checks, summary = conditions.check(items, cass)
    assert summary["gold_non_if_headed"] == 2
    assert all(c.status == "NEVER_EMITTED" for c in checks)
    assert "NARROW READING CONFIRMED" in conditions.render(checks, summary)


def test_category_reading_when_every_non_if_condition_is_emitted():
    items = [_item(conditions=["upon the death of X"])]
    cass = {"S-001": [[_extraction(["upon the death of X"])]]}
    checks, summary = conditions.check(items, cass)
    assert checks[0].status == "EMITTED_EXACT"
    assert "CATEGORY READING CONFIRMED" in conditions.render(checks, summary)


def test_mixed_verdict_when_some_are_emitted_and_some_are_not():
    items = [_item(conditions=["upon the death of X", "As requested by Y"])]
    cass = {"S-001": [[_extraction(["upon the death of X"])]]}
    checks, summary = conditions.check(items, cass)
    assert "MIXED" in conditions.render(checks, summary)


def test_a_different_boundary_is_reported_separately_from_never_emitted():
    """Emitting a SUPERSET of the gold phrase is not the same failure as
    emitting nothing -- one is a boundary question, the other a recall question."""
    items = [_item(conditions=["upon the death of X"])]
    cass = {"S-001": [[_extraction(["upon the death of X or any successor"])]]}
    checks, _ = conditions.check(items, cass)
    assert checks[0].status == "EMITTED_DIFFERENT_BOUNDARY"
    assert checks[0].partial_emitted_runs == [1]
    assert checks[0].exact_emitted_runs == []


def test_per_run_attribution_is_recorded_not_collapsed():
    items = [_item(conditions=["upon the death of X"])]
    cass = {"S-001": [[_extraction([])], [_extraction(["upon the death of X"])]]}
    checks, _ = conditions.check(items, cass)
    assert checks[0].exact_emitted_runs == [2], "which run emitted it must survive aggregation"
    assert checks[0].total_runs == 2
