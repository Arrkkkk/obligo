"""Temporal -> integer-day Window lowering (blueprint §6.7's interval-algebra
half of Z3 lowering; the scoping conversation's §1.4/§1.5).

This module answers exactly one question: given an ast.Temporal | None, what
window of days does it constrain an obligation's performance to? It does not
decide conflicts -- that's z3_lowering.py's job, working from the windows
this module produces.

Coverage is deliberately partial, and that partiality is load-bearing, not a
gap to silently paper over (CLAUDE.md §0's own framing, applied to this
checkpoint). Only BY and DURING carry a usable window in v1, because they're
the only two temporal forms whose DateRef can ever be RESOLVED --
symbols.resolve_trigger() unconditionally returns None (compiler/symbols.py),
so WITHIN and RELATIVE_TO_TRIGGER's TriggerRef is always UNRESOLVED, and
EVERY has no outer bound to lower against (packages/ir-spec/SPEC.md §7 --
the bound is left implicit to a `sources.effective_date` that was never
migrated). Every one of those cases ABSTAINs rather than guessing a window.

ABSTAIN is treated as "overlaps everything" by overlaps() below -- unknown
must not collapse to "no overlap," which would silently shrink the
candidate-selection set (scoping conversation §1.4). It's also excluded from
ever reaching the solver on its own by candidates.py's clause (d): a pair of
two abstaining obligations can never produce a finding, so it's filtered
before Z3 sees it, not after.

Day arithmetic is integer days since the Unix epoch (1970-01-01), via
date.toordinal() rather than string comparison, so window arithmetic in
z3_lowering.py is plain integer arithmetic. Range is bounded by Python's own
date.min/date.max (proleptic Gregorian, year 1-9999) -- IR v1's DateRef only
ever holds an ISO date within that range (ast.ResolvedDate.date), so no wider
bound is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from obligo_brain.compiler import ast

_EPOCH_ORDINAL = date(1970, 1, 1).toordinal()


def _day(iso: str) -> int:
    return date.fromisoformat(iso).toordinal() - _EPOCH_ORDINAL


MIN_DAY = date.min.toordinal() - _EPOCH_ORDINAL
MAX_DAY = date.max.toordinal() - _EPOCH_ORDINAL


def iso_date(day: int) -> str:
    """Inverse of the internal ISO -> day conversion, for rendering a Window
    bound back into a human-readable date (unsat_explain.py's own use)."""
    return date.fromordinal(day + _EPOCH_ORDINAL).isoformat()


@dataclass(frozen=True)
class Window:
    """A closed interval [start, end] in integer days since epoch, both
    bounds inclusive. start > end is a legal value -- it represents an
    obligation whose own DURING bounds are reversed (end date before start
    date), which is empty by construction (is_empty()); this is a real,
    named conflict class (TEMPORAL_IMPOSSIBILITY) and not filtered out here,
    since detecting it is z3_lowering.py's job.
    """

    start: int
    end: int


class Abstain:
    """Sentinel: this obligation's temporal scope cannot be lowered to a
    concrete window in IR v1. See module docstring for exactly which
    temporal forms this covers and why.
    """

    def __repr__(self) -> str:
        return "ABSTAIN"


ABSTAIN = Abstain()


def is_empty(window: Window) -> bool:
    return window.end < window.start


def temporal_window(temporal: ast.Temporal | None) -> Window | Abstain:
    """No temporal element at all is not the same as an unresolved one: a
    standing duty with no stated bound genuinely holds for the whole scope
    under consideration (scoping conversation §1.4), so `None` lowers to the
    unbounded window [MIN_DAY, MAX_DAY], not ABSTAIN.
    """
    if temporal is None:
        return Window(MIN_DAY, MAX_DAY)

    if isinstance(temporal, ast.ByTemporal):
        if isinstance(temporal.datetime, ast.ResolvedDate):
            return Window(MIN_DAY, _day(temporal.datetime.date))
        return ABSTAIN

    if isinstance(temporal, ast.DuringTemporal):
        if isinstance(temporal.start, ast.ResolvedDate) and isinstance(
            temporal.end, ast.ResolvedDate
        ):
            return Window(_day(temporal.start.date), _day(temporal.end.date))
        return ABSTAIN

    if isinstance(
        temporal, (ast.WithinTemporal, ast.RelativeToTriggerTemporal, ast.EveryTemporal)
    ):
        return ABSTAIN

    raise TypeError(f"unhandled Temporal variant: {temporal!r}")


def overlaps(a: Window | Abstain, b: Window | Abstain) -> bool:
    """Used by candidates.py's clause (c) only -- a cheap prefilter, not a
    conflict verdict. An ABSTAIN on either side overlaps everything (see
    module docstring). This is deliberately permissive: correctness of the
    eventual verdict rests on z3_lowering.py's residual-emptiness computation
    (scoping conversation §1.2), not on this predicate, so erring toward
    "overlaps" here costs throughput, never correctness -- confirmed
    concretely in the scoping conversation's §2.2 (deleting clause (a)
    entirely still produces the right verdict, because the solver's own
    act-key identity is the actual gate).
    """
    if isinstance(a, Abstain) or isinstance(b, Abstain):
        return True
    return a.start <= b.end and b.start <= a.end
