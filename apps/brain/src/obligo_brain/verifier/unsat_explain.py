"""Minimal unsat-core extraction and deterministic English rendering
(blueprint §6.7's "explanation" paragraph; scoping conversation §4).
Consumes a z3_lowering.LoweredGroup and produces Finding objects. No LLM
call anywhere in this module -- approved as proposed: "the claim comes from
the core... never let the model invent the reason" (blueprint §6.7),
Standing Principle 2.

## Minimization mechanism

z3_lowering.py builds every fact as `Implies(selector, constraint)` with the
selector *never* permanently asserted true -- each check() call here passes
a specific subset of selectors as *assumptions*
(`solver.check(*selectors)`), not permanent state. This is what makes
minimization and multi-core enumeration both possible without push/pop:
the same Solver object is reused for every check() in a group, varying only
which selectors are passed as assumptions per call.

Deletion-based minimization (`_minimize`) processes labels in a fixed order
(sorted lexicographically, which is sorted-by-SourceRef because that's how
z3_lowering.py names them) so which minimal core survives, when several
are possible, is deterministic across runs -- required both for the
conflict-symmetry property test and for reproducible eval numbers (scoping
conversation §1.3's minimality note).

## Multi-core enumeration

`_enumerate_cores` finds one minimal core, removes its labels from the pool
of labels being checked, and checks the remainder -- if that's unsat too,
it's a genuinely independent contradiction (scoping conversation §1.6,
worked example B: no single pair is unsat, only the 3-way group is).
Bounded at MAX_CORES_PER_GROUP total.

## Two passes, one severity distinction

`explain_group` runs MUST/MUST_NOT facts first (severity HIGH), then adds
SHOULD facts on top of whatever's left (severity ADVISORY) -- SPEC.md §2:
SHOULD is "non-binding... matters for risk scoring," so a SHOULD-involving
conflict is real but weaker than a MUST-involving one, and the two must
never be reported at the same severity.
"""

from __future__ import annotations

from dataclasses import dataclass

import z3

from obligo_brain.compiler import ast
from obligo_brain.verifier import actions, intervals
from obligo_brain.verifier.z3_lowering import ANTAGONISTIC, LoweredGroup

MODAL_CONFLICT = "MODAL_CONFLICT"
ANTAGONISTIC_ACTION = "ANTAGONISTIC_ACTION"
CONDITION_CONTRADICTION = "CONDITION_CONTRADICTION"
TEMPORAL_IMPOSSIBILITY = "TEMPORAL_IMPOSSIBILITY"

HIGH = "HIGH"
ADVISORY = "ADVISORY"

# scoping conversation §1.5/§1.6: bounded, not exhaustively enumerated --
# a candidate set producing more than this many independent conflicts is
# itself a signal worth a human look, not something to keep enumerating.
MAX_CORES_PER_GROUP = 5


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    obligations: tuple[ast.Obligation, ...]
    explanation: str
    condition_sensitive: bool


# --- core search --------------------------------------------------------


def _check(lowered: LoweredGroup, labels: list[str]) -> z3.CheckSatResult:
    return lowered.solver.check(*[lowered.selectors[l] for l in labels])


def _minimize(lowered: LoweredGroup, core_labels: list[str]) -> list[str]:
    core = sorted(core_labels)
    i = 0
    while i < len(core):
        candidate = core[:i] + core[i + 1 :]
        if candidate and _check(lowered, candidate) == z3.unsat:
            core = candidate
            # don't advance -- re-test whatever label shifted into position i
        else:
            i += 1
    return core


def _enumerate_cores(
    lowered: LoweredGroup, active_labels: list[str], budget: int
) -> tuple[list[list[str]], list[str], bool]:
    remaining = sorted(active_labels)
    cores: list[list[str]] = []
    timed_out = False

    for _ in range(budget):
        if not remaining:
            break
        result = _check(lowered, remaining)
        if result == z3.sat:
            break
        if result == z3.unknown:
            timed_out = True
            break
        raw_core = [str(lit).removeprefix("sel::") for lit in lowered.solver.unsat_core()]
        minimal = _minimize(lowered, raw_core)
        cores.append(minimal)
        remaining = [label for label in remaining if label not in minimal]

    return cores, remaining, timed_out


# --- classification -------------------------------------------------------


def _classify_kind(lowered: LoweredGroup, core_labels: list[str]) -> str:
    core_facts = [lowered.facts[label] for label in core_labels]
    if any(f.kind == "prohibition" and f.prohibition_source == ANTAGONISTIC for f in core_facts):
        return ANTAGONISTIC_ACTION
    if any(f.kind in ("window", "prohibition") for f in core_facts):
        return MODAL_CONFLICT
    return CONDITION_CONTRADICTION


def _condition_sensitive(lowered: LoweredGroup, core_labels: list[str]) -> bool:
    return any(lowered.facts[label].kind == "cond" for label in core_labels)


def _obligations_from_core(lowered: LoweredGroup, core_labels: list[str]) -> tuple[ast.Obligation, ...]:
    seen: set[int] = set()
    distinct: list[ast.Obligation] = []
    for label in core_labels:
        obligation = lowered.facts[label].obligation
        if id(obligation) not in seen:
            seen.add(id(obligation))
            distinct.append(obligation)
    distinct.sort(key=lambda o: (o.source.segment_id, o.source.char_start, o.source.char_end))
    return tuple(distinct)


# --- rendering ----------------------------------------------------------


def _obligor_name(obligation: ast.Obligation) -> str:
    party = obligation.obligor
    if isinstance(party, ast.ResolvedParty):
        return party.canonical_name
    return party.alias


def _object_phrase(obligation: ast.Obligation) -> str:
    return obligation.object.raw_text


def _join_and(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _describe_window(window: intervals.Window) -> str:
    if window.start == intervals.MIN_DAY and window.end == intervals.MAX_DAY:
        return "at any time"
    if window.start == intervals.MIN_DAY:
        return f"by {intervals.iso_date(window.end)}"
    if window.end == intervals.MAX_DAY:
        return f"on or after {intervals.iso_date(window.start)}"
    return f"during {intervals.iso_date(window.start)} to {intervals.iso_date(window.end)}"


def _predicate_text(predicate: ast.Predicate) -> str:
    if isinstance(predicate, ast.AtomPredicate):
        return f'"{predicate.raw}"'
    if isinstance(predicate, ast.AndPredicate):
        return f"({_predicate_text(predicate.left)} AND {_predicate_text(predicate.right)})"
    if isinstance(predicate, ast.OrPredicate):
        return f"({_predicate_text(predicate.left)} OR {_predicate_text(predicate.right)})"
    if isinstance(predicate, ast.NotPredicate):
        return f"NOT {_predicate_text(predicate.operand)}"
    raise TypeError(f"unhandled Predicate variant: {predicate!r}")


def _condition_text(obligation: ast.Obligation) -> str:
    return " AND ".join(_predicate_text(c.predicate) for c in obligation.conditions)


def _render_modal_or_antagonistic(duty_facts: list, prohibition_facts: list) -> str:
    anchor = duty_facts[0].obligation
    obligor_name = _obligor_name(anchor)

    duty_descs = [
        f"{actions.gloss(f.obligation.action)} {_object_phrase(f.obligation)} "
        f"{_describe_window(intervals.temporal_window(f.obligation.temporal))}"
        for f in duty_facts
    ]

    prohibition_descs = []
    for f in prohibition_facts:
        window = intervals.temporal_window(f.obligation.temporal)
        if f.prohibition_source == ANTAGONISTIC:
            prohibition_descs.append(
                f"a duty to {actions.gloss(f.obligation.action)} the same "
                f"{_object_phrase(f.obligation)} {_describe_window(window)} makes that impossible"
            )
        else:
            prohibition_descs.append(f"another clause prohibits it {_describe_window(window)}")

    return f"{obligor_name} must {_join_and(duty_descs)}, but {_join_and(prohibition_descs)}."


def _render_condition_contradiction(cond_facts: list) -> str:
    obligor_name = _obligor_name(cond_facts[0].obligation)
    conditions = _join_and([_condition_text(f.obligation) for f in cond_facts])
    return f"{obligor_name}'s obligations rely on conditions that cannot all hold at once: {conditions}."


def _render(lowered: LoweredGroup, core_labels: list[str], kind: str) -> str:
    core_facts = [lowered.facts[label] for label in core_labels]
    if kind == CONDITION_CONTRADICTION:
        return _render_condition_contradiction([f for f in core_facts if f.kind == "cond"])
    duty_facts = [f for f in core_facts if f.kind == "window"]
    prohibition_facts = [f for f in core_facts if f.kind == "prohibition"]
    return _render_modal_or_antagonistic(duty_facts, prohibition_facts)


def _finding_from_core(lowered: LoweredGroup, core_labels: list[str], severity: str) -> Finding:
    kind = _classify_kind(lowered, core_labels)
    return Finding(
        kind=kind,
        severity=severity,
        obligations=_obligations_from_core(lowered, core_labels),
        explanation=_render(lowered, core_labels, kind),
        condition_sensitive=_condition_sensitive(lowered, core_labels),
    )


# --- top-level entry points ------------------------------------------------


def explain_group(lowered: LoweredGroup) -> tuple[list[Finding], bool]:
    """Runs both passes over one lowered candidate group. Returns
    (findings, timed_out); timed_out mirrors blueprint §4.2's Z3-timeout
    failure mode -- the caller (verify.py) surfaces it as its own signal,
    never folding an UNKNOWN verdict into a Finding that would read as a
    confirmed conflict.
    """
    findings: list[Finding] = []

    pass1_cores, remaining, timed_out = _enumerate_cores(
        lowered, list(lowered.must_ish_labels), MAX_CORES_PER_GROUP
    )
    findings.extend(_finding_from_core(lowered, core, HIGH) for core in pass1_cores)

    if not timed_out and lowered.should_labels:
        budget_left = MAX_CORES_PER_GROUP - len(pass1_cores)
        if budget_left > 0:
            pass2_active = remaining + list(lowered.should_labels)
            pass2_cores, _remaining2, timed_out2 = _enumerate_cores(lowered, pass2_active, budget_left)
            findings.extend(_finding_from_core(lowered, core, ADVISORY) for core in pass2_cores)
            timed_out = timed_out or timed_out2

    return findings, timed_out


def temporal_impossibility_finding(obligation: ast.Obligation) -> Finding:
    """TEMPORAL_IMPOSSIBILITY is detected in pure Python (intervals.is_empty),
    not through Z3 -- an obligation's own reversed DURING bounds need no
    solver call, and routing it through Z3 would risk misattributing the
    defect to whatever it happened to be grouped with (see verify.py's own
    docstring for why this is excluded from candidate grouping entirely).
    """
    window = intervals.temporal_window(obligation.temporal)
    assert isinstance(window, intervals.Window) and intervals.is_empty(window)
    obligor_name = _obligor_name(obligation)
    return Finding(
        kind=TEMPORAL_IMPOSSIBILITY,
        severity=HIGH,
        obligations=(obligation,),
        explanation=(
            f"{obligor_name}'s obligation to {actions.gloss(obligation.action)} "
            f"{_object_phrase(obligation)} has a temporal window that ends "
            f"({intervals.iso_date(window.end)}) before it starts "
            f"({intervals.iso_date(window.start)}) -- it can never be performed."
        ),
        condition_sensitive=False,
    )
