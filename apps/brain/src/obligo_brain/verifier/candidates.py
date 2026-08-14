"""The conflict-candidate set (blueprint §6.7, §0.2 gap 5; scoping
conversation §1-§2). Pure, no I/O -- same discipline as ground_candidates()/
compile_candidates().

Two entry points:

- select_candidates(target, pool): blueprint's own framing -- "given a
  newly-typechecked Obligation, what determines which other obligations it
  needs to be checked against." Returns the admitted candidates (each
  tagged with how its party match was established) and the excluded
  obligations (each tagged with which clause excluded it), so a missed
  conflict is diagnosable from the run record rather than invisible
  (scoping conversation §1.2).

- group_candidate_sets(obligations): the connected components of the
  candidate graph over a whole corpus -- the actual sets verify.py hands to
  z3_lowering.py. This operationalizes §1.6's "solve the set, not the
  pairs": an edge is select_candidates admitting each obligation as a
  candidate of the other (the relation is symmetric -- see
  tests/verifier/test_candidates.py), and a connected component is exactly
  the transitive closure needed to catch an n-way conflict where every pair
  is individually satisfiable but the group together is not (scoping
  conversation §1.4, worked example B: Q pairs with R1 and with R2, but R1
  and R2 don't pair with each other directly -- yet all three belong in one
  solve because they're connected through Q).

Four clauses, all must hold for an edge to exist:

  (a) object class  -- exact match on the normalized class string
  (b) party          -- at least one of {obligor, obligee} overlaps, in
                        either role (scoping conversation §1.3: this is
                        deliberately *not* obligor-identity; that
                        requirement lives in z3_lowering.py's act key, not
                        here)
  (c) temporal        -- windows overlap; an ABSTAINing obligation overlaps
                        everything (intervals.py's own module docstring)
  (d) verifiability    -- not both sides ABSTAIN (a pair of two abstentions
                        can never produce a finding, so it's excluded
                        before Z3 rather than after)

The candidate set never decides a conflict -- it only decides what gets
solved. Deleting clause (a) entirely was checked concretely (scoping
conversation §2.2) to cost only throughput, never a wrong verdict, because
object class is *also* part of z3_lowering.py's act key -- the real
discriminator lives there, at the layer that actually determines
correctness (Standing Principle 2).
"""

from __future__ import annotations

from dataclasses import dataclass

from obligo_brain.compiler import ast
from obligo_brain.verifier import intervals

# A connected component larger than this is reported as
# VERIFIER_SCOPE_EXCEEDED rather than solved -- a set this large is itself a
# signal (candidate-set explosion, most likely from an over-broad object
# class), not a case to push through Z3 regardless of cost. See scoping
# conversation §1.5.
MAX_CANDIDATE_SET = 50

_PARTY_ID = "PARTY_ID"
_ALIAS = "ALIAS"

ExclusionReason = str  # one of the four below
OBJECT_CLASS_MISMATCH: ExclusionReason = "OBJECT_CLASS_MISMATCH"
NO_PARTY_OVERLAP: ExclusionReason = "NO_PARTY_OVERLAP"
NO_TEMPORAL_OVERLAP: ExclusionReason = "NO_TEMPORAL_OVERLAP"
BOTH_ABSTAIN: ExclusionReason = "BOTH_ABSTAIN"


@dataclass(frozen=True)
class Candidate:
    obligation: ast.Obligation
    party_match_basis: str  # PARTY_ID | ALIAS -- scoping conversation §1.3


@dataclass(frozen=True)
class Exclusion:
    obligation: ast.Obligation
    reason: ExclusionReason


@dataclass(frozen=True)
class CandidateSelection:
    target: ast.Obligation
    candidates: tuple[Candidate, ...]
    excluded: tuple[Exclusion, ...]


def norm_object_class(class_: str) -> str:
    """Public: z3_lowering.py's act key reuses this exact function, so the
    prefilter's clause (a) and the solver's own identity notion can never
    silently drift apart from each other.
    """
    return class_.strip().casefold()


def _object_class_matches(a: ast.ObjectRef, b: ast.ObjectRef) -> bool:
    return norm_object_class(a.class_) == norm_object_class(b.class_)


def party_key(party: ast.PartyRef) -> tuple[str, str]:
    """RESOLVED and UNRESOLVED keys are never equal to each other by
    construction (different first element) -- an UnresolvedParty alias is
    never matched against a ResolvedParty's canonical_name here; that's
    symbols.resolve_party()'s job, upstream of the verifier entirely.

    Public: z3_lowering.py's act key reuses this exact function, for the
    same drift-prevention reason as norm_object_class() above.
    """
    if isinstance(party, ast.ResolvedParty):
        return (_PARTY_ID, party.party_id)
    return (_ALIAS, party.alias.casefold())


def _party_overlap_basis(a: ast.Obligation, b: ast.Obligation) -> str | None:
    a_keys = [(party_key(a.obligor)), (party_key(a.obligee))]
    b_keys = {party_key(b.obligor), party_key(b.obligee)}
    for key in a_keys:
        if key in b_keys:
            return key[0]
    return None


def _temporal_overlaps(a: ast.Obligation, b: ast.Obligation) -> bool:
    return intervals.overlaps(intervals.temporal_window(a.temporal), intervals.temporal_window(b.temporal))


def _both_abstain(a: ast.Obligation, b: ast.Obligation) -> bool:
    return isinstance(intervals.temporal_window(a.temporal), intervals.Abstain) and isinstance(
        intervals.temporal_window(b.temporal), intervals.Abstain
    )


def _classify(target: ast.Obligation, other: ast.Obligation) -> tuple[str | None, ExclusionReason | None]:
    """Returns (party_match_basis, exclusion_reason) -- exactly one of the
    two is None. Clauses are checked in a fixed order (a, b, c, d) so a
    pair failing multiple clauses always reports the same single reason.
    """
    if not _object_class_matches(target.object, other.object):
        return None, OBJECT_CLASS_MISMATCH

    basis = _party_overlap_basis(target, other)
    if basis is None:
        return None, NO_PARTY_OVERLAP

    if not _temporal_overlaps(target, other):
        return None, NO_TEMPORAL_OVERLAP

    if _both_abstain(target, other):
        return None, BOTH_ABSTAIN

    return basis, None


def select_candidates(
    target: ast.Obligation, pool: "list[ast.Obligation] | tuple[ast.Obligation, ...]"
) -> CandidateSelection:
    candidates: list[Candidate] = []
    excluded: list[Exclusion] = []

    for other in pool:
        if other is target:
            continue
        basis, reason = _classify(target, other)
        if reason is not None:
            excluded.append(Exclusion(obligation=other, reason=reason))
        else:
            assert basis is not None
            candidates.append(Candidate(obligation=other, party_match_basis=basis))

    return CandidateSelection(target=target, candidates=tuple(candidates), excluded=tuple(excluded))


def group_candidate_sets(
    obligations: "list[ast.Obligation] | tuple[ast.Obligation, ...]",
) -> list[list[ast.Obligation]]:
    """Connected components of the candidate graph, in deterministic order
    (component membership order matches `obligations`' own order; components
    are returned in order of their earliest member). Singleton components
    (no edges to anything) are omitted -- nothing to solve.
    """
    n = len(obligations)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    for i in range(n):
        for j in range(i + 1, n):
            basis, reason = _classify(obligations[i], obligations[j])
            if reason is None:
                assert basis is not None
                union(i, j)

    groups: dict[int, list[ast.Obligation]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(obligations[i])

    return [members for members in groups.values() if len(members) > 1]
