"""Obligation set -> Z3 assertions (blueprint §6.7; scoping conversation
§1-§3). Builds the Z3 problem for one candidate group; does not solve it or
decide what a resulting core means -- that's unsat_explain.py's job. Pure:
no I/O, no DB, no LLM (Standing Principle 2 -- this determines a finding's
correctness, so it must be deterministic code, not a model call).

## The conflict condition (scoping conversation §1.2, the corrected rule)

A conflict is an empty *residual* feasible set for some single act, not an
empty pairwise intersection and not a subset check in either direction --
both of those collapse in configurations that are actually satisfiable (see
the module docstring's worked-example citations in
tests/verifier/test_z3_lowering.py). For each performance variable t_i
belonging to a MUST/SHOULD obligation on act key k:

    required window:   W_i
    forbidden windows:  P_1, P_2, ...   (every MUST_NOT and every implied
                                        antagonism-prohibition sharing k)
    feasible set:       F_i = W_i \\ (P_1 u P_2 u ...)
    CONFLICT  iff  F_i = empty

Z3 computes this directly via `t_i in W_i` conjoined with `t_i not in P_j`
for each P_j -- residual-emptiness falls out of ordinary conjunction/
disjunction, it is never computed as a separate set operation in Python.

## Act keys and why MUSTs never share a performance variable

`act_key(obligation) = (candidates.party_key(obligor), action,
candidates.norm_object_class(object.class_))` -- the *same* two functions
candidates.py's clause (a)/(b) use, imported rather than reimplemented, so
the prefilter and the solver's own notion of "same act" can never silently
drift apart (see candidates.py's own public-function docstrings).

Every MUST/SHOULD obligation gets its own fresh Z3 Int, even when several
share an act key -- two duties to perform the same kind of act are two
separate acts, not one shared performance. Unifying them would turn ordinary
supersession (a later amendment's new deadline) into a fabricated
contradiction; this is the single largest false-positive source named in the
scoping conversation and it's closed by construction, not by a runtime
check.

## Conditions

Condition predicates lower to plain Z3 Bools, keyed by normalized raw atom
text so the *same* atom text used in two different obligations' conditions
is the *same* Z3 variable -- this is what makes `IF "X"` in one obligation
and `IF NOT "X"` in another actually able to contradict each other. They are
asserted as bare literals (not used to guard the modal/window facts): this
directly implements "condition literals are assumed true"
(scoping conversation §2.1) with no extra machinery -- if two conditions are
genuinely opposed, that alone is already unsat, independent of any temporal
fact; deletion-based minimization (unsat_explain.py) is what tells the
difference between a condition-only core and a modal one.

## MAY and abstaining obligations

A MAY obligation asserts nothing (§2.1: "a right you needn't exercise cannot
be breached") and is never lowered here at all -- filtering it out is
verify.py's job, upstream of this module, so this module never has to check
modality against MAY.

An obligation whose temporal_window() is ABSTAIN (intervals.py) cannot be
lowered into a concrete window at all -- WITHIN/RELATIVE_TO_TRIGGER/EVERY,
or an unresolved BY/DURING date. Its `.window`/`.prohibition` contribution
is silently omitted (there is nothing sound to assert), but its `.cond`
contribution (if it has conditions) is still included -- a condition
contradiction needs no temporal information at all to be real.
"""

from __future__ import annotations

from dataclasses import dataclass

import z3

from obligo_brain.compiler import ast
from obligo_brain.verifier import actions, candidates, intervals

MUST_ISH = ("MUST", "SHOULD")

# scoping conversation §4.2: 120s, matching blueprint §4.2's own
# Z3_TIMEOUT_MS=120000 constant.
Z3_TIMEOUT_MS = 120_000

MODAL = "MODAL"
ANTAGONISTIC = "ANTAGONISTIC"


def _norm_atom(raw: str) -> str:
    return raw.strip().casefold()


def _lower_predicate(predicate: ast.Predicate, atom_vars: dict[str, z3.BoolRef]) -> z3.BoolRef:
    if isinstance(predicate, ast.AtomPredicate):
        key = _norm_atom(predicate.raw)
        if key not in atom_vars:
            atom_vars[key] = z3.Bool(f"atom::{key}")
        return atom_vars[key]
    if isinstance(predicate, ast.AndPredicate):
        return z3.And(
            _lower_predicate(predicate.left, atom_vars), _lower_predicate(predicate.right, atom_vars)
        )
    if isinstance(predicate, ast.OrPredicate):
        return z3.Or(
            _lower_predicate(predicate.left, atom_vars), _lower_predicate(predicate.right, atom_vars)
        )
    if isinstance(predicate, ast.NotPredicate):
        return z3.Not(_lower_predicate(predicate.operand, atom_vars))
    raise TypeError(f"unhandled Predicate variant: {predicate!r}")


def _obligation_condition(obligation: ast.Obligation, atom_vars: dict[str, z3.BoolRef]) -> z3.BoolRef:
    return z3.And(*[_lower_predicate(c.predicate, atom_vars) for c in obligation.conditions])


def _act_key(obligation: ast.Obligation) -> tuple:
    return (
        candidates.party_key(obligation.obligor),
        obligation.action,
        candidates.norm_object_class(obligation.object.class_),
    )


def _in_window(t: z3.ArithRef, window: intervals.Window) -> z3.BoolRef:
    return z3.And(t >= window.start, t <= window.end)


@dataclass(frozen=True)
class Fact:
    """One tracked assumption in the lowered problem. `obligation` is
    whichever obligation is responsible for this fact -- for a
    `prohibition` fact, that's the MUST_NOT (MODAL) or the antagonistic
    MUST (ANTAGONISTIC) that contributed it, not the obligation(s) it
    constrains.
    """

    label: str
    kind: str  # "window" | "prohibition" | "cond"
    obligation: ast.Obligation
    prohibition_source: str | None = None  # MODAL | ANTAGONISTIC, kind == "prohibition" only


@dataclass(frozen=True)
class LoweredGroup:
    solver: z3.Solver
    facts: dict[str, Fact]
    selectors: dict[str, z3.BoolRef]
    must_ish_labels: tuple[str, ...]  # window/cond facts owned by MUST/MUST_NOT obligations
    should_labels: tuple[str, ...]  # window/cond facts owned by SHOULD obligations


def lower(obligations: "list[ast.Obligation] | tuple[ast.Obligation, ...]") -> LoweredGroup:
    """Builds one Z3 problem for a candidate group (candidates.py's
    group_candidate_sets() output). Obligations are processed in a fixed,
    deterministic order (by SourceRef, then original position) so label
    naming -- and therefore minimization order in unsat_explain.py -- never
    depends on input ordering (scoping conversation §2.4's minimality note).
    """
    ordered = sorted(
        enumerate(obligations),
        key=lambda pair: (pair[1].source.segment_id, pair[1].source.char_start, pair[1].source.char_end, pair[0]),
    )

    solver = z3.Solver()
    solver.set(timeout=Z3_TIMEOUT_MS)

    atom_vars: dict[str, z3.BoolRef] = {}
    facts: dict[str, Fact] = {}
    selectors: dict[str, z3.BoolRef] = {}
    must_ish_labels: list[str] = []
    should_labels: list[str] = []

    # First pass: performance variables for MUST/SHOULD, condition facts for
    # everyone, and the raw (obligation, window) pairs that will become
    # prohibition facts once we know which act keys actually have a
    # MUST/SHOULD var to constrain.
    perf_vars: dict[tuple, list[z3.ArithRef]] = {}
    raw_prohibitions: list[tuple[ast.Obligation, tuple, intervals.Window, str]] = []

    def _add(label: str, kind: str, obligation: ast.Obligation, constraint: z3.BoolRef, *, prohibition_source=None):
        sel = z3.Bool(f"sel::{label}")
        solver.add(z3.Implies(sel, constraint))
        selectors[label] = sel
        facts[label] = Fact(label=label, kind=kind, obligation=obligation, prohibition_source=prohibition_source)
        target = should_labels if obligation.modality == "SHOULD" else must_ish_labels
        target.append(label)

    for idx, obligation in ordered:
        if obligation.modality == "MAY":
            # A right you needn't exercise cannot be breached -- asserts
            # nothing at all, not even its own conditions (module
            # docstring). verify.py also filters MAY before grouping so it
            # never inflates a candidate set's size; this is defense in
            # depth for any caller that hands lower() a group directly.
            continue

        label_base = f"{obligation.source.segment_id}:{obligation.source.char_start}:{obligation.source.char_end}:{idx}"

        if obligation.conditions:
            cond_expr = _obligation_condition(obligation, atom_vars)
            _add(f"{label_base}.cond", "cond", obligation, cond_expr)

        window = intervals.temporal_window(obligation.temporal)
        if isinstance(window, intervals.Abstain):
            continue

        if obligation.modality in MUST_ISH:
            key = _act_key(obligation)
            t = z3.Int(f"t::{label_base}")
            perf_vars.setdefault(key, []).append(t)
            _add(f"{label_base}.window", "window", obligation, _in_window(t, window))

            implied = actions.implied_prohibition(obligation.action)
            if implied is not None:
                target_key = (candidates.party_key(obligation.obligor), implied, candidates.norm_object_class(obligation.object.class_))
                raw_prohibitions.append((obligation, target_key, window, ANTAGONISTIC))

        elif obligation.modality == "MUST_NOT":
            key = _act_key(obligation)
            raw_prohibitions.append((obligation, key, window, MODAL))

    # Second pass: materialize prohibition facts, but only for act keys that
    # actually have a MUST/SHOULD performance variable to constrain --
    # a prohibition with no matching duty is vacuous and contributes
    # nothing, per §2.1.
    for obligation, target_key, window, source in raw_prohibitions:
        must_vars = perf_vars.get(target_key)
        if not must_vars:
            continue
        label = f"{obligation.source.segment_id}:{obligation.source.char_start}:{obligation.source.char_end}.prohibition:{source}:{target_key[1]}"
        constraint = z3.And(*[z3.Not(_in_window(t, window)) for t in must_vars])
        _add(label, "prohibition", obligation, constraint, prohibition_source=source)

    return LoweredGroup(
        solver=solver,
        facts=facts,
        selectors=selectors,
        must_ish_labels=tuple(must_ish_labels),
        should_labels=tuple(should_labels),
    )
