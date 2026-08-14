"""Integration tests for verifier/verify.py -- every test here makes a real
z3.Solver.check() call (no mocking of Z3, per CLAUDE.md's real-infrastructure
standard applied to this checkpoint). Each of the scoping conversation's
worked examples (A, A', B, S/T) is pinned here as a named regression test,
per that conversation's own §3.5 -- each one breaks a different plausible-
but-wrong formulation of "conflict."
"""

from __future__ import annotations

import dataclasses

from obligo_brain.compiler import ast
from obligo_brain.verifier import candidates
from obligo_brain.verifier.verify import verify
from tests.verifier.helpers import (
    CUSTOMER,
    OTHER_VENDOR,
    VENDOR,
    by,
    cond,
    during,
    obligation,
    relative,
    within,
)


# -- Example A: containment -> UNSAT (the true positive) ---------------------


def test_example_a_prohibition_containing_duty_window_is_a_conflict():
    prohibition = obligation(
        modality="MUST_NOT", action="DISCLOSE", object_class="confidential_information",
        object_text="Confidential Information", temporal=during("2027-01-01", "2027-12-31"),
    )
    duty = obligation(
        modality="MUST", action="DISCLOSE", object_class="confidential_information",
        object_text="Confidential Information", temporal=during("2027-03-01", "2027-03-31"),
    )
    result = verify([prohibition, duty])

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.kind == "MODAL_CONFLICT"
    assert finding.severity == "HIGH"
    assert set(finding.obligations) == {prohibition, duty}
    assert not finding.condition_sensitive
    assert "2027-03-01" in finding.explanation
    assert "2027-01-01" in finding.explanation


# -- Example A': partial overlap -> SAT (a lawful window survives) ----------


def test_example_a_prime_partial_overlap_leaves_a_lawful_window():
    prohibition = obligation(
        modality="MUST_NOT", action="DISCLOSE", object_class="confidential_information",
        temporal=during("2027-01-01", "2027-12-31"),
    )
    duty = obligation(
        modality="MUST", action="DISCLOSE", object_class="confidential_information",
        temporal=during("2026-12-15", "2027-01-15"),
    )
    result = verify([prohibition, duty])
    assert result.findings == []


# -- Example S/T: prohibition nested inside a wider duty window -> SAT ------


def test_example_st_nested_prohibition_still_leaves_escape_room():
    duty = obligation(
        modality="MUST", action="DELIVER", object_class="quarterly_report",
        object_text="the Quarterly Report", temporal=during("2027-01-01", "2027-03-31"),
    )
    freeze = obligation(
        modality="MUST_NOT", action="DELIVER", object_class="quarterly_report",
        object_text="the Quarterly Report", temporal=during("2027-02-01", "2027-02-28"),
    )
    result = verify([duty, freeze])
    assert result.findings == []


def test_subset_vs_partial_overlap_is_the_only_variable_that_flips_the_verdict():
    # The direct A-vs-S/T contrast: same structural shape (opposed
    # modality, shared act key, overlapping windows), only the containment
    # direction differs.
    contained = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-01-10", "2027-01-20"))
    wide_prohibition = obligation(modality="MUST_NOT", action="DELIVER", object_class="x", temporal=during("2027-01-01", "2027-01-31"))
    assert len(verify([contained, wide_prohibition]).findings) == 1  # W subset of P

    wide_duty = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-01-01", "2027-01-31"))
    narrow_prohibition = obligation(modality="MUST_NOT", action="DELIVER", object_class="x", temporal=during("2027-01-10", "2027-01-20"))
    assert verify([wide_duty, narrow_prohibition]).findings == []  # P subset of W -- room outside P


# -- Example B: n-way, no pair alone is unsat --------------------------------


def test_example_b_n_way_conflict_invisible_to_pairwise_checking():
    q = obligation(modality="MUST", action="DISCLOSE", object_class="confidential_information", temporal=during("2027-01-01", "2027-12-31"))
    r1 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="confidential_information", temporal=during("2027-01-01", "2027-06-30"))
    r2 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="confidential_information", temporal=during("2027-07-01", "2027-12-31"))

    assert verify([q, r1]).findings == []
    assert verify([q, r2]).findings == []

    result = verify([q, r1, r2])
    assert len(result.findings) == 1
    assert result.findings[0].kind == "MODAL_CONFLICT"
    assert set(result.findings[0].obligations) == {q, r1, r2}


# -- MUST/MUST and MUST_NOT/MUST_NOT never conflict with each other ---------


def test_two_musts_on_same_key_never_conflict_regardless_of_windows():
    # Two duties to perform the same kind of act are two separate acts, not
    # a shared performance -- this is what makes ordinary supersession
    # (a later amendment's new deadline) not a fabricated contradiction.
    jan = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-01-01", "2027-01-31"))
    jun = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-06-01", "2027-06-30"))
    assert verify([jan, jun]).findings == []


def test_two_must_nots_never_conflict():
    a = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-06-30"))
    b = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    assert verify([a, b]).findings == []


# -- disjoint windows, no duty at all: vacuous prohibitions -----------------


def test_prohibition_with_no_matching_duty_is_vacuous():
    lone_prohibition = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    unrelated_duty = obligation(modality="MUST", action="PAY", object_class="fees", temporal=during("2027-01-01", "2027-12-31"))
    assert verify([lone_prohibition, unrelated_duty]).findings == []


# -- ANTAGONISTIC_ACTION: DELETE/RETAIN, DISCLOSE/WITHHOLD -------------------


def test_delete_nested_inside_retain_window_is_antagonistic_conflict():
    retain = obligation(modality="MUST", action="RETAIN", object_class="customer_personal_data", object_text="Customer Personal Data", temporal=during("2027-01-01", "2027-12-31"))
    delete = obligation(modality="MUST", action="DELETE", object_class="customer_personal_data", object_text="Customer Personal Data", temporal=during("2027-06-01", "2027-06-02"))

    result = verify([retain, delete])
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.kind == "ANTAGONISTIC_ACTION"
    assert finding.severity == "HIGH"
    assert set(finding.obligations) == {retain, delete}


def test_delete_outside_retain_window_does_not_conflict():
    retain = obligation(modality="MUST", action="RETAIN", object_class="customer_personal_data", temporal=during("2027-01-01", "2027-12-31"))
    delete = obligation(modality="MUST", action="DELETE", object_class="customer_personal_data", temporal=during("2026-06-01", "2026-06-02"))
    assert verify([retain, delete]).findings == []


def test_withhold_disclose_antagonism():
    withhold = obligation(modality="MUST", action="WITHHOLD", object_class="trade_secret", temporal=during("2027-01-01", "2027-12-31"))
    disclose = obligation(modality="MUST", action="DISCLOSE", object_class="trade_secret", temporal=during("2027-06-01", "2027-06-02"))
    result = verify([withhold, disclose])
    assert len(result.findings) == 1
    assert result.findings[0].kind == "ANTAGONISTIC_ACTION"


def test_antagonism_is_not_symmetric_must_not_retain_does_not_imply_prohibition_on_delete():
    # Only a MUST on the continuous side generates an implied prohibition --
    # a MUST_NOT RETAIN just forbids retaining, it says nothing about DELETE.
    must_not_retain = obligation(modality="MUST_NOT", action="RETAIN", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    delete = obligation(modality="MUST", action="DELETE", object_class="x", temporal=during("2027-06-01", "2027-06-02"))
    assert verify([must_not_retain, delete]).findings == []


def test_delete_must_never_implies_a_prohibition_on_retain():
    # The reverse direction of the asymmetry: a point-in-time DELETE duty
    # does not forbid retaining beforehand.
    delete = obligation(modality="MUST", action="DELETE", object_class="x", temporal=by("2027-03-01"))
    retain = obligation(modality="MUST", action="RETAIN", object_class="x", temporal=during("2027-01-01", "2027-02-01"))
    assert verify([delete, retain]).findings == []


# -- CONDITION_CONTRADICTION -------------------------------------------------


def test_condition_contradiction_isolated_no_temporal_overlap_at_all():
    # Disjoint windows so there is no modal conflict at all -- isolates the
    # condition-only contradiction cleanly.
    a = obligation(
        modality="MUST", action="TERMINATE", object_class="agreement", object_text="this Agreement",
        temporal=during("2027-01-01", "2027-01-31"),
        conditions=(cond("the Company terminates for cause"),),
    )
    b = obligation(
        modality="MUST_NOT", action="TERMINATE", object_class="agreement", object_text="this Agreement",
        temporal=during("2027-06-01", "2027-06-30"),
        conditions=(cond("the Company terminates for cause", negate=True),),
    )
    # NOTE: disjoint temporal windows means clause (c) would normally
    # exclude this pair from candidate grouping entirely -- but a condition
    # contradiction has nothing to do with timing. Construct instead with
    # temporal=None on both (unbounded, so clause (c) passes) and rely on
    # the *conditions* being the only thing that can make this unsat, which
    # is exactly what CONDITION_CONTRADICTION classification requires.
    a = dataclasses.replace(a, temporal=None)
    b = dataclasses.replace(b, temporal=None)

    result = verify([a, b])
    # Both a condition contradiction AND (since temporal is None on both,
    # i.e. unbounded on both sides) a real modal conflict are present --
    # multi-core enumeration must find both, independently.
    kinds = {f.kind for f in result.findings}
    assert "CONDITION_CONTRADICTION" in kinds
    condition_finding = next(f for f in result.findings if f.kind == "CONDITION_CONTRADICTION")
    assert condition_finding.condition_sensitive
    assert "terminates for cause" in condition_finding.explanation


def test_condition_contradiction_without_any_modal_conflict():
    # A clean isolation: different actions (no shared act key at all, no
    # antagonism relation either), so the *only* possible source of unsat
    # is the opposed conditions.
    a = obligation(
        modality="MUST", action="NOTIFY", object_class="incident", temporal=None,
        conditions=(cond("a Security Incident occurs"),),
    )
    b = obligation(
        modality="MUST", action="REPORT", object_class="incident", temporal=None,
        conditions=(cond("a Security Incident occurs", negate=True),),
    )
    result = verify([a, b])
    assert len(result.findings) == 1
    assert result.findings[0].kind == "CONDITION_CONTRADICTION"
    assert result.findings[0].condition_sensitive


def test_non_contradictory_conditions_never_manufacture_a_finding():
    a = obligation(modality="MUST", action="NOTIFY", object_class="x", temporal=None, conditions=(cond("event A"),))
    b = obligation(modality="MUST", action="REPORT", object_class="x", temporal=None, conditions=(cond("event B"),))
    assert verify([a, b]).findings == []


# -- SHOULD: advisory pass, weaker severity ----------------------------------


def test_should_conflict_is_advisory_not_high():
    should_disclose = obligation(modality="SHOULD", action="DISCLOSE", object_class="x", temporal=during("2027-03-01", "2027-03-31"))
    must_not_disclose = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    result = verify([should_disclose, must_not_disclose])
    assert len(result.findings) == 1
    assert result.findings[0].severity == "ADVISORY"


def test_should_never_conflicts_with_should():
    a = obligation(modality="SHOULD", action="DELIVER", object_class="x", temporal=during("2027-01-01", "2027-01-31"))
    b = obligation(modality="SHOULD", action="DELIVER", object_class="x", temporal=during("2027-06-01", "2027-06-30"))
    assert verify([a, b]).findings == []


def test_must_conflict_stays_high_even_when_should_present():
    prohibition = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    must_duty = obligation(modality="MUST", action="DISCLOSE", object_class="x", temporal=during("2027-03-01", "2027-03-31"))
    should_duty = obligation(modality="SHOULD", action="DISCLOSE", object_class="x", temporal=during("2027-04-01", "2027-04-30"))

    result = verify([prohibition, must_duty, should_duty])
    severities = {f.severity for f in result.findings}
    assert "HIGH" in severities


# -- MAY is inert -------------------------------------------------------


def test_may_never_participates_in_any_finding():
    may_disclose = obligation(modality="MAY", action="DISCLOSE", object_class="x", temporal=during("2027-03-01", "2027-03-31"))
    must_not_disclose = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    assert verify([may_disclose, must_not_disclose]).findings == []


# -- TEMPORAL_IMPOSSIBILITY --------------------------------------------------


def test_temporal_impossibility_reversed_during_bounds():
    broken = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-12-31", "2027-01-01"))
    result = verify([broken])
    assert len(result.findings) == 1
    assert result.findings[0].kind == "TEMPORAL_IMPOSSIBILITY"
    assert result.findings[0].obligations == (broken,)


def test_temporal_impossibility_does_not_contaminate_other_obligations():
    broken = obligation(modality="MUST", action="DELIVER", object_class="reports", temporal=during("2027-12-31", "2027-01-01"))
    unrelated_duty = obligation(modality="MUST", action="PAY", object_class="fees", temporal=during("2027-01-01", "2027-12-31"))
    unrelated_prohibition = obligation(modality="MUST_NOT", action="PAY", object_class="fees", temporal=during("2027-01-01", "2027-12-31"))

    result = verify([broken, unrelated_duty, unrelated_prohibition])
    kinds = [f.kind for f in result.findings]
    assert kinds.count("TEMPORAL_IMPOSSIBILITY") == 1
    assert kinds.count("MODAL_CONFLICT") == 1


# -- cross-document: object equality doesn't care about source segment ------


def test_conflict_detected_across_different_source_segments():
    # The whole point of org-wide (not same-document) scoping: two
    # obligations from different segment_ids still conflict.
    a = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    b = obligation(modality="MUST", action="DISCLOSE", object_class="x", temporal=during("2027-03-01", "2027-03-31"))
    assert a.source.segment_id != b.source.segment_id
    result = verify([a, b])
    assert len(result.findings) == 1


# -- scale bound --------------------------------------------------------


def test_scope_exceeded_when_candidate_group_too_large():
    group = [
        obligation(modality="MUST" if i % 2 == 0 else "MUST_NOT", action="DELETE", object_class="x", temporal=None)
        for i in range(candidates.MAX_CANDIDATE_SET + 1)
    ]
    result = verify(group)
    assert result.findings == []
    assert len(result.scope_exceeded) == 1
    assert len(result.scope_exceeded[0].obligations) == candidates.MAX_CANDIDATE_SET + 1


# -- determinism / conflict symmetry (concrete regression, complementing
# the hypothesis property in test_properties.py) ----------------------------


def test_verify_result_is_order_independent():
    q = obligation(modality="MUST", action="DISCLOSE", object_class="ci", temporal=during("2027-01-01", "2027-12-31"))
    r1 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="ci", temporal=during("2027-01-01", "2027-06-30"))
    r2 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="ci", temporal=during("2027-07-01", "2027-12-31"))

    forward = verify([q, r1, r2])
    backward = verify([r2, r1, q])

    assert len(forward.findings) == len(backward.findings) == 1
    assert forward.findings[0].kind == backward.findings[0].kind
    assert forward.findings[0].explanation == backward.findings[0].explanation
    assert set(forward.findings[0].obligations) == set(backward.findings[0].obligations)
