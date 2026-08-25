"""Guideline v0.33's three scoring changes, each planted individually.

  Fix 1 -- section 5 clause 5 normalizes grammatical NUMBER on both sides.
  Fix 5 -- clause 3 finally reads section 3.5.1's obligor_accept_set.
  G6    -- report.py discloses gapped numerator items inline, by DIRECTION.

The number tests LEAD WITH A KNOWN-ANSWER TABLE rather than with the gold
items they were written for. That ordering is deliberate: the first draft of
this normaliser stripped only a trailing "s", turning `taxes` into `taxe`,
and it looked entirely correct until it was run against a case whose answer
was already established (Standing Principle 7). A table of pre-agreed answers
is the detector-check; the gold-item regressions come after it.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from obligo_brain.compiler import ast

from evals.harness import registry as registry_mod, report as report_mod, score
from evals.harness.score import Outcome

GOLDENS = Path(__file__).resolve().parents[2] / "evals" / "goldens"
GOLD = GOLDENS / "batch01" / "items" / "C03-01.json"


@pytest.fixture(scope="module")
def gold() -> dict:
    return json.loads(GOLD.read_text())


@pytest.fixture(scope="module")
def reg() -> registry_mod.DocumentRegistry:
    return registry_mod.load("C03")


@pytest.fixture
def baseline(reg: registry_mod.DocumentRegistry) -> ast.Obligation:
    return ast.Obligation(
        modality="MUST", action="PROVIDE",
        obligor=ast.ResolvedParty(party_id="p1",
                                  canonical_name=reg.resolve("Vendor").canonical_name),
        obligee=ast.ResolvedParty(party_id="p2",
                                  canonical_name=reg.resolve("AT&T").canonical_name),
        object=ast.ObjectRef(class_="technical_support", raw_text="technical assistance"),
        temporal=None, conditions=(),
        source=ast.SourceRef(segment_id="seg", char_start=0, char_end=100),
        confidence=0.9, underspecified=False, missing_fields=(),
    )


# --------------------------------------------------------------------------
# Fix 1, step 1: the normaliser against answers agreed BEFORE it was written.
# --------------------------------------------------------------------------

# (a, b, do they denote the same label?) -- every pair's verdict is fixed by
# English, not by what the implementation happens to do.
KNOWN_ANSWERS = [
    # -es after a sibilant: the branch a naive trailing-"s" rule gets WRONG.
    ("taxes", "tax", True),
    ("boxes", "box", True),
    ("breaches", "breach", True),
    # plain -s
    ("retained_samples", "retained_sample", True),
    ("agreement_provisions", "agreement_provision", True),
    ("costs", "cost", True),
    # -ies -> -y
    ("warranties", "warranty", True),
    ("indemnities", "indemnity", True),
    # -ss must NOT be stripped
    ("business", "busines", False),
    ("loss_provision", "los_provision", False),
    # genuinely different labels stay different -- the over-matching guard
    ("invoice_costs", "retention_costs", False),
    ("principal_interest", "franchise_interest", False),
    ("efforts", "virus_prevention", False),
    # AND the specific conflations a stemmer would make, which this must not
    ("retention", "retain", False),
    ("provisions", "provide", False),
    ("delivery", "deliverable", False),
]


@pytest.mark.parametrize("a,b,same", KNOWN_ANSWERS)
def test_number_normaliser_against_known_answers(a: str, b: str, same: bool) -> None:
    assert (score.singularize(a) == score.singularize(b)) is same, (
        f"{a!r} vs {b!r}: expected same={same}, "
        f"got {score.singularize(a)!r} vs {score.singularize(b)!r}"
    )


def test_normaliser_is_not_a_stemmer_the_named_over_match_guard() -> None:
    """Stated as its own test because it is the failure mode that would make
    clause 5 vacuous, and a parametrized row is easy to delete."""
    assert score.singularize("retention") != score.singularize("retain")
    assert score.singularize("provisions") != score.singularize("provide")


# --------------------------------------------------------------------------
# Fix 1, step 2: clause 5 actually uses it.
# --------------------------------------------------------------------------

def test_clause5_passes_on_a_plural_of_an_accept_set_member(gold, baseline, reg) -> None:
    g = dict(gold, object_class_accept_set=["tax", "withholding_tax"])
    pred = dataclasses.replace(
        baseline, object=ast.ObjectRef(class_="taxes", raw_text="such taxes"))
    sc = score.score_item(g, pred, reg)
    assert sc.clauses["object_class"] is True
    assert "matched on number alone" in sc.detail["object_class"]


def test_clause5_detail_does_not_claim_number_matching_on_an_exact_hit(gold, baseline, reg) -> None:
    """An exact match must not be mislabelled as a number match -- otherwise the
    detail line stops distinguishing the two and the measurement is lost."""
    sc = score.score_item(gold, baseline, reg)
    assert sc.clauses["object_class"] is True
    assert "matched on number alone" not in sc.detail["object_class"]


def test_clause5_still_fails_on_a_genuinely_different_label(gold, baseline, reg) -> None:
    """The rule must not have quietly widened clause 5 into a near-match test."""
    pred = dataclasses.replace(
        baseline, object=ast.ObjectRef(class_="principal_interest", raw_text="x"))
    sc = score.score_item(dict(gold, object_class_accept_set=["franchise_interest"]), pred, reg)
    assert sc.clauses["object_class"] is False
    assert sc.outcome is Outcome.PARTIAL


def test_clause7_is_NOT_number_normalized(gold, baseline, reg) -> None:
    """Scope guard: section 5 v0.33 normalizes number for clause 5 ONLY.
    Conditions are verbatim quotes and normalizing a quotation is a different
    act from normalizing a label."""
    g = dict(gold, conditions=["upon receipt of the notices"])
    pred = dataclasses.replace(baseline, conditions=(
        ast.Condition(predicate=ast.AtomPredicate(raw="upon receipt of the notice")),))
    sc = score.score_item(g, pred, reg)
    assert sc.clauses["conditions"] is False


# --------------------------------------------------------------------------
# Fix 5: obligor_accept_set is read -- and only where it should be.
# --------------------------------------------------------------------------

def test_obligor_accept_set_admits_a_non_primary_alternative(gold, baseline, reg) -> None:
    """FAILS before v0.33: _party_matches took gold["obligor"] alone, so every
    co-obligor section 3.5.1 required an annotator to author was ignored."""
    g = dict(gold, obligor="Antares", obligor_accept_set=["Antares", "its Subcontractor"])
    pred = dataclasses.replace(baseline, obligor=ast.UnresolvedParty(alias="its Subcontractor"))
    sc = score.score_item(g, pred, reg)
    assert sc.clauses["obligor"] is True


def test_obligor_accept_set_does_not_admit_an_unlisted_alias(gold, baseline, reg) -> None:
    g = dict(gold, obligor="Antares", obligor_accept_set=["Antares", "its Subcontractor"])
    pred = dataclasses.replace(baseline, obligor=ast.UnresolvedParty(alias="AMAG"))
    sc = score.score_item(g, pred, reg)
    assert sc.clauses["obligor"] is False


def test_obligor_accept_set_does_not_leak_into_the_obligee_slot(gold, baseline, reg) -> None:
    """Section 3.5.1 deliberately has no obligee accept-set (measured: joint 0 /
    disjunctive 3 of 1,547). Reusing the obligor's for clause 4 would invent a
    rule the guideline declined to make."""
    g = dict(gold, obligee="AT&T", obligor_accept_set=["Vendor", "its Subcontractor"])
    pred = dataclasses.replace(baseline, obligee=ast.UnresolvedParty(alias="its Subcontractor"))
    sc = score.score_item(g, pred, reg)
    assert sc.clauses["obligee"] is False


def test_the_whole_coordinated_phrase_is_not_admitted_unless_listed(gold, baseline, reg) -> None:
    """C02-01's real shape, and why section 3.5.1 gained its v0.33 rider: the
    model stably emits the WHOLE disjunction, which the accept-set as authored
    never enumerated. Pinned so the rider's necessity stays visible."""
    g = dict(gold, obligor="Antares", obligor_accept_set=["Antares", "its Subcontractor"])
    pred = dataclasses.replace(
        baseline, obligor=ast.UnresolvedParty(alias="Antares or its Subcontractor"))
    assert score.score_item(g, pred, reg).clauses["obligor"] is False
    g2 = dict(g, obligor_accept_set=[*g["obligor_accept_set"], "Antares or its Subcontractor"])
    assert score.score_item(g2, pred, reg).clauses["obligor"] is True


def test_a_resolved_party_ignores_the_accept_set(gold, baseline, reg) -> None:
    """The registry IS the accept-set on the resolved path; a second one there
    could only loosen an identity check."""
    g = dict(gold, obligor_accept_set=["anything at all"])
    sc = score.score_item(g, baseline, reg)
    assert sc.clauses["obligor"] is True


# --------------------------------------------------------------------------
# Fix 4 / G6: the in-force denominator and inline gap disclosure.
# --------------------------------------------------------------------------

def _report(items: list[tuple[str, Outcome, list[str]]]) -> report_mod.Report:
    per_item = {i: [o, o, o] for i, o, _ in items}
    gold_by_id = {
        i: {"item_id": i, "known_gaps": g, "vague_temporal_phrase": None}
        for i, _, g in items
    }
    return report_mod.build(per_item, gold_by_id)


def test_the_in_force_criterion_is_the_no_known_gaps_denominator() -> None:
    rep = _report([
        ("A-01", Outcome.FULLY_CORRECT, []),
        ("A-02", Outcome.PARTIAL, []),
        ("A-03", Outcome.FULLY_CORRECT, ["mutual_obligation"]),
    ])
    out = rep.render()
    assert rep.criterion2_no_known_gaps == (1, 2)
    assert rep.criterion2_all_items == (2, 3)
    assert "CRITERION 2 (IN FORCE" in out and "len(known_gaps)==0" in out
    # The all-items figure must still be published, and must NOT be the criterion.
    assert "Reported alongside, over ALL items" in out
    assert "NOT the criterion" in out


def test_a_gapped_numerator_item_is_disclosed_by_direction() -> None:
    rep = _report([
        ("A-01", Outcome.FULLY_CORRECT, ["exception_unsupported"]),
        ("A-02", Outcome.FULLY_CORRECT, ["compound_action"]),
    ])
    out = rep.render()
    assert "OVERSTATING: A-01 (exception_unsupported)" in out
    assert "INCOMPLETENESS: A-02 (compound_action)" in out


def test_a_gapped_item_that_is_NOT_in_the_numerator_is_not_disclosed() -> None:
    """G6 discloses what the numerator CERTIFIES. A tagged item scoring PARTIAL
    is already reported as a failure and needs no numerator caveat."""
    rep = _report([("A-01", Outcome.PARTIAL, ["exception_unsupported"])])
    out = rep.render()
    assert "OVERSTATING" not in out
    assert "None -- every item in either numerator" in out


def test_an_unmapped_gap_tag_surfaces_as_UNCLASSIFIED_rather_than_defaulting() -> None:
    """A tag added later must force a direction decision, never be absorbed
    silently into whichever bucket a default happened to pick."""
    rep = _report([("A-01", Outcome.FULLY_CORRECT, ["some_future_tag"])])
    assert "UNCLASSIFIED: A-01 (some_future_tag)" in rep.render()


def test_c14_01s_real_shape_an_overstating_item_entering_the_numerator() -> None:
    """The concrete case grounding section 9.1's validity argument: C14-01 is
    scored FULLY_CORRECT once clause 5's number rule lands, and its IR is
    STRONGER than the contract (section 8.2). It must be excluded from the
    in-force criterion AND named inline in the all-items figure."""
    rep = _report([
        ("C14-01", Outcome.FULLY_CORRECT, ["mutual_obligation", "exception_unsupported"]),
        ("C03-01", Outcome.FULLY_CORRECT, []),
    ])
    assert rep.criterion2_no_known_gaps == (1, 1)
    assert rep.criterion2_all_items == (2, 2)
    out = rep.render()
    assert "OVERSTATING: C14-01 (exception_unsupported)" in out
    assert "INCOMPLETENESS: C14-01 (mutual_obligation)" in out
