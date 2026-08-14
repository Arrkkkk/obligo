"""Temporal -> Window lowering (verifier/intervals.py). No DB, no Z3 --
pure function tests only.
"""

from __future__ import annotations

from obligo_brain.compiler import ast
from obligo_brain.verifier import intervals
from obligo_brain.verifier.intervals import ABSTAIN, MAX_DAY, MIN_DAY, Window


def test_no_temporal_is_unbounded_not_abstain():
    # A standing duty with no stated bound genuinely holds for the whole
    # scope under consideration -- not the same as "unknown" (scoping
    # conversation §1.4).
    assert intervals.temporal_window(None) == Window(MIN_DAY, MAX_DAY)


def test_by_resolved_date_has_no_lower_bound():
    w = intervals.temporal_window(ast.ByTemporal(datetime=ast.ResolvedDate(date="2027-03-01")))
    assert isinstance(w, Window)
    assert w.start == MIN_DAY
    assert w.end == intervals._day("2027-03-01")


def test_by_unresolved_date_abstains():
    w = intervals.temporal_window(ast.ByTemporal(datetime=ast.UnresolvedDate(raw="the Delivery Date")))
    assert w is ABSTAIN


def test_during_both_resolved():
    w = intervals.temporal_window(
        ast.DuringTemporal(start=ast.ResolvedDate(date="2027-01-01"), end=ast.ResolvedDate(date="2027-12-31"))
    )
    assert isinstance(w, Window)
    assert w.start == intervals._day("2027-01-01")
    assert w.end == intervals._day("2027-12-31")


def test_during_one_unresolved_abstains():
    w = intervals.temporal_window(
        ast.DuringTemporal(start=ast.ResolvedDate(date="2027-01-01"), end=ast.UnresolvedDate(raw="the Expiration Date"))
    )
    assert w is ABSTAIN


def test_during_reversed_bounds_is_empty_not_abstain():
    # A real defect (TEMPORAL_IMPOSSIBILITY), not an unknown -- it must still
    # lower to a concrete (empty) Window, not ABSTAIN.
    w = intervals.temporal_window(
        ast.DuringTemporal(start=ast.ResolvedDate(date="2027-12-31"), end=ast.ResolvedDate(date="2027-01-01"))
    )
    assert isinstance(w, Window)
    assert intervals.is_empty(w)


def test_during_single_day_is_not_empty():
    w = intervals.temporal_window(
        ast.DuringTemporal(start=ast.ResolvedDate(date="2027-06-01"), end=ast.ResolvedDate(date="2027-06-01"))
    )
    assert not intervals.is_empty(w)


def test_within_always_abstains_trigger_never_resolves():
    w = intervals.temporal_window(ast.WithinTemporal(duration=ast.Duration(amount=5, unit="d"), of=ast.UnresolvedTrigger(raw="discovering a Security Incident")))
    assert w is ABSTAIN


def test_within_business_days_also_abstains():
    w = intervals.temporal_window(ast.WithinTemporal(duration=ast.Duration(amount=5, unit="bd"), of=ast.UnresolvedTrigger(raw="discovering a Security Incident")))
    assert w is ABSTAIN


def test_relative_to_trigger_always_abstains():
    w = intervals.temporal_window(ast.RelativeToTriggerTemporal(direction="BEFORE", trigger=ast.UnresolvedTrigger(raw="terminating this Agreement")))
    assert w is ABSTAIN


def test_every_always_abstains_no_outer_bound():
    w = intervals.temporal_window(ast.EveryTemporal(duration=ast.Duration(amount=30, unit="d")))
    assert w is ABSTAIN


def test_overlaps_disjoint_is_false():
    a = Window(0, 10)
    b = Window(20, 30)
    assert not intervals.overlaps(a, b)
    assert not intervals.overlaps(b, a)


def test_overlaps_touching_at_boundary_is_true():
    # Closed intervals -- day 10 belongs to both.
    a = Window(0, 10)
    b = Window(10, 20)
    assert intervals.overlaps(a, b)


def test_overlaps_containment_is_true():
    outer = Window(0, 100)
    inner = Window(40, 60)
    assert intervals.overlaps(outer, inner)
    assert intervals.overlaps(inner, outer)


def test_overlaps_abstain_overlaps_everything():
    assert intervals.overlaps(ABSTAIN, Window(0, 10))
    assert intervals.overlaps(Window(0, 10), ABSTAIN)
    assert intervals.overlaps(ABSTAIN, ABSTAIN)


def test_iso_date_round_trips_through_day_conversion():
    for iso in ("2027-01-01", "2027-12-31", "1970-01-01", "2000-02-29"):
        assert intervals.iso_date(intervals._day(iso)) == iso
