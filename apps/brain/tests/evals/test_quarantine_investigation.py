"""The 2026-10-10 quarantine investigation, pinned against committed artifacts.

Scope, stated so a green CI is not over-read: these tests cover what can be
checked from the COMMITTED gold set and the PRODUCTION classifier -- no corpus,
no database, no cassette replay -- so they all run in CI. The 9-of-9
UNMAPPABLE_TEMPORAL / REPAIR_MADE_NO_PROGRESS result itself needs a real
database and the cassettes, and is reproduced by
`evals/goldens/holdout/quarantine/capture.py` rather than by a test here.

See `evals/goldens/holdout/quarantine/README.md`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obligo_brain.compiler.ir_compile import _classify_temporal

GOLDENS = Path(__file__).resolve().parents[2] / "evals" / "goldens"

# The phrases the three items' candidates actually carried, read off the real
# PipelineResult.quarantined records. Verbatim: every one grounded at tier EXACT.
QUARANTINED_VERBATIM = {
    "C04-03": ['on the Delivery Date ("Delivery")', "on the Delivery Date"],
    "C04-15": ["During the Term of this Agreement"],
    "C17-03": [
        "During the applicable Term of any Service",
        "During the applicable Term",   # run 3, AFTER two repair calls narrowed it
    ],
}


def _item(item_id: str) -> dict:
    hits = sorted(GOLDENS.glob(f"batch*/items/{item_id}.json"))
    assert len(hits) == 1, f"{item_id}: expected exactly one gold file, got {hits}"
    return json.loads(hits[0].read_text())


def test_the_classifier_gate_behaves_before_any_phrase_is_read():
    """Standing Principle 7: a known accept and a known reject first.

    Without this, every assertion below could be passing because
    _classify_temporal returns None for everything.
    """
    assert _classify_temporal("by 2026-01-01") is not None
    assert _classify_temporal("the parties agree") is None


@pytest.mark.parametrize(
    "phrase",
    [p for ps in QUARANTINED_VERBATIM.values() for p in ps],
)
def test_every_quarantined_phrase_classifies_to_none(phrase: str):
    """One cause, measured: UNMAPPABLE_TEMPORAL on all three items."""
    assert _classify_temporal(phrase) is None, phrase


def test_c04_03s_gold_form_IS_reachable_and_only_the_preposition_blocks_it():
    """2a -- REACHABILITY, not representability, and this is the discriminator.

    Swapping the contract's `on` for the `by` that gold annotates makes the
    identical phrase classify. That is what separates C04-03 from C04-15/C17-03.
    """
    assert _classify_temporal("on the Delivery Date") is None
    got = _classify_temporal("by the Delivery Date")
    assert got is not None
    assert "the Delivery Date" in str(got)


def test_c04_03s_contract_writes_on_and_gold_annotates_by():
    """The conformance question of README §4, pinned so it cannot drift silently."""
    it = _item("C04-03")
    assert it["temporal"]["form"] == "BY"
    assert it["temporal"]["alias"] == "the Delivery Date"
    assert 'on the Delivery Date ("Delivery")' in it["segment_text"]
    assert "by the Delivery Date" not in it["segment_text"]


def test_c04_03_is_untagged_for_its_temporal():
    """It carries only a CORPUS_DEFECT tag, which ENTERS the in-force denominator.

    If a future session rules F41 and tags it, this test fails loudly -- which is
    the point: the reading change is an acknowledgement, not a silent edit.
    """
    from evals.harness.gap_kinds import in_force_scope

    gaps = tuple(_item("C04-03")["known_gaps"])
    assert gaps == ("corpus_artifact_in_span",)
    assert in_force_scope(gaps) is True


def test_no_DURING_narrowing_is_a_path_but_the_legal_shape_classifies():
    """2b -- REPRESENTATIONAL. C17-03 run 3 spent two repair calls narrowing.

    The two-sided form is what makes this a statement about the GRAMMAR's slot
    arity rather than about the regex rejecting long strings.
    """
    for phrase in QUARANTINED_VERBATIM["C17-03"]:
        assert _classify_temporal(phrase) is None, phrase
    assert _classify_temporal("during 2026-01-01..2026-12-31") is not None


def test_the_defined_term_pair_carries_gold_temporal_null_and_no_tag():
    """Why §10.4.4's interaction is live: gold says null, so a dropped phrase
    would make clause 6 compare None to None."""
    for item_id in ("C04-15", "C17-03"):
        it = _item(item_id)
        assert it["temporal"] is None, item_id
        assert it["known_gaps"] == [], item_id


def test_clause_six_passes_on_null_equals_null():
    """The mechanism behind §10.4.4, asserted against the real scorer helpers
    rather than read off score.py's source."""
    from evals.harness.score import _canonical_gold_temporal, _canonical_temporal

    assert _canonical_gold_temporal(None) is None
    assert _canonical_temporal(None) is None
    assert _canonical_gold_temporal(None) == _canonical_temporal(None)
