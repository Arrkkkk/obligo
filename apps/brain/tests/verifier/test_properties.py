"""Property-based tests for the verifier (blueprint §19.3) -- these unblock
two of test_properties.py's (compiler) six deferred properties: conflict
symmetry and typecheck soundness (see CLAUDE.md's Phase 4 acceptance-
criteria table).

Every check() call here is real Z3 -- no mocking.

A note on what was actually asked for versus what's actually true, kept
here rather than only in chat: the literal property "any two intervals
with a nonempty intersection are always flagged" is FALSE -- Example S/T
(test_verify.py) is exactly a nonempty-intersection pair that is SAT. The
TRUE, provable relationship for a MUST/MUST_NOT pair is residual-emptiness,
which reduces to set containment: unsat iff the duty's window is a subset
of the prohibition's window (scoping conversation §1.2). "Empty
intersection implies never flagged" IS true and is tested explicitly below
as a named corollary of the subset property, since it's a real, useful,
narrower claim -- but its converse is not, and is not tested as if it were.
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from obligo_brain.verifier import intervals, z3_lowering
from obligo_brain.verifier.verify import verify
from tests.compiler.strategies import obligation as compiler_obligation
from tests.verifier.helpers import during, obligation

_DAY_BOUND = 3650  # +-10 years around the epoch -- ample range, keeps date arithmetic cheap


@st.composite
def window(draw):
    a = draw(st.integers(min_value=-_DAY_BOUND, max_value=_DAY_BOUND))
    b = draw(st.integers(min_value=-_DAY_BOUND, max_value=_DAY_BOUND))
    start, end = (a, b) if a <= b else (b, a)
    return intervals.Window(start=start, end=end)


def _obligation_with_window(modality: str, w: intervals.Window):
    return obligation(
        modality=modality,
        action="DISCLOSE",
        object_class="confidential_information",
        temporal=during(intervals.iso_date(w.start), intervals.iso_date(w.end)),
    )


def _is_subset(inner: intervals.Window, outer: intervals.Window) -> bool:
    return outer.start <= inner.start and inner.end <= outer.end


@given(window(), window())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=150)
def test_must_must_never_conflicts_regardless_of_windows(w1, w2):
    a = _obligation_with_window("MUST", w1)
    b = _obligation_with_window("MUST", w2)
    assert verify([a, b]).findings == []


@given(window(), window())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=150)
def test_must_not_must_not_never_conflicts_regardless_of_windows(w1, w2):
    a = _obligation_with_window("MUST_NOT", w1)
    b = _obligation_with_window("MUST_NOT", w2)
    assert verify([a, b]).findings == []


@given(window(), window())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=200)
def test_must_must_not_unsat_iff_duty_window_is_subset_of_prohibition(w_duty, w_prohibit):
    duty = _obligation_with_window("MUST", w_duty)
    prohibition = _obligation_with_window("MUST_NOT", w_prohibit)
    result = verify([duty, prohibition])

    if _is_subset(w_duty, w_prohibit):
        assert len(result.findings) == 1
        assert result.findings[0].kind == "MODAL_CONFLICT"
    else:
        assert result.findings == []


@given(window(), window())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=150)
def test_empty_intersection_implies_never_flagged(w_duty, w_prohibit):
    # The TRUE direction of what was asked for -- a real corollary of the
    # subset property above (a nonempty window can never be a subset of a
    # window it doesn't intersect), pinned as its own explicit test.
    disjoint = w_duty.end < w_prohibit.start or w_prohibit.end < w_duty.start
    if not disjoint:
        return
    duty = _obligation_with_window("MUST", w_duty)
    prohibition = _obligation_with_window("MUST_NOT", w_prohibit)
    assert verify([duty, prohibition]).findings == []


@given(window(), window())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=100)
def test_conflict_symmetry(w1, w2):
    a = _obligation_with_window("MUST", w1)
    b = _obligation_with_window("MUST_NOT", w2)

    forward = verify([a, b])
    backward = verify([b, a])

    assert len(forward.findings) == len(backward.findings)
    if forward.findings:
        assert forward.findings[0].kind == backward.findings[0].kind
        assert forward.findings[0].explanation == backward.findings[0].explanation


@given(compiler_obligation())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=200)
def test_typecheck_soundness_any_parser_producible_ast_lowers_without_error(ob):
    # "Any AST accepted by the typechecker lowers to Z3 without error"
    # (blueprint §19.3). Reuses the compiler's own hypothesis strategy
    # (tests/compiler/strategies.py) -- the same shape of AST typecheck()
    # accepts and returns (typecheck only resolves values in place; it
    # never changes the AST's shape). A single-obligation "group" is
    # sufficient: lower() must not raise regardless of modality, temporal
    # form, or condition structure.
    lowered = z3_lowering.lower([ob])
    assert lowered is not None
