"""Entry point: verify(obligations) -> VerificationResult (blueprint §7.2's
own eventual `verify_constraints` tool -- "Run Z3 over a supplied
obligation set"). Pure: no DB, no tenant_scope(), no LLM, no network --
typecheck() already resolved parties upstream, and this module needs
nothing else from the database (scoping conversation §3).

Not wired into run_pipeline() -- blueprint §3.9 places Z3 verification
after the Critic and Linker (neither built), and verification is naturally
per-org-corpus while run_pipeline() is per-segment: different granularity,
different owner. The demo path for a cross-document conflict (scoping
conversation §3) is calling run_pipeline() over segments from two different
sources in one org, unioning their PipelineResult.typechecked lists, and
calling verify() on the union -- in memory, at a green commit
(Standing Principle 1). See tests/verifier/test_verify.py's own
cross-document test for exactly this shape.

Also not written anywhere: `findings`/`verification_runs` (blueprint §8.2)
don't exist for the identical reason PipelineResult.typechecked is
returned in memory only (CLAUDE.md's obligations-persistence
investigation) -- there is no `obligations` table to hold the UUIDs a
`findings` row would need to cite, and "mark false positive" is a
human-workflow write that belongs to whatever eventually owns that table
(Phase 5), not to this module.

TEMPORAL_IMPOSSIBILITY is detected before candidate grouping, not through
it -- an obligation with its own reversed DURING bounds is broken
regardless of what else exists in the corpus, and letting it into a Z3
group would risk the finding being misattributed to whichever obligation
it happened to be paired with (unsat_explain.temporal_impossibility_finding's
own docstring). MAY obligations are dropped for the same before-grouping
reason: they assert nothing (z3_lowering.py's own docstring) and would only
inflate a candidate set's size for MAX_CANDIDATE_SET purposes without ever
being able to participate in a finding.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from obligo_brain.compiler import ast
from obligo_brain.verifier import candidates, intervals, unsat_explain, z3_lowering
from obligo_brain.verifier.unsat_explain import Finding


@dataclass(frozen=True)
class ScopeExceeded:
    obligations: tuple[ast.Obligation, ...]


@dataclass(frozen=True)
class VerificationResult:
    findings: list[Finding] = field(default_factory=list)
    scope_exceeded: list[ScopeExceeded] = field(default_factory=list)
    timed_out_groups: list[tuple[ast.Obligation, ...]] = field(default_factory=list)


def verify(obligations: "list[ast.Obligation] | tuple[ast.Obligation, ...]") -> VerificationResult:
    findings: list[Finding] = []
    scope_exceeded: list[ScopeExceeded] = []
    timed_out_groups: list[tuple[ast.Obligation, ...]] = []

    verifiable: list[ast.Obligation] = []
    for obligation in obligations:
        if obligation.modality == "MAY":
            continue
        window = intervals.temporal_window(obligation.temporal)
        if isinstance(window, intervals.Window) and intervals.is_empty(window):
            findings.append(unsat_explain.temporal_impossibility_finding(obligation))
            continue
        verifiable.append(obligation)

    for group in candidates.group_candidate_sets(verifiable):
        if len(group) > candidates.MAX_CANDIDATE_SET:
            scope_exceeded.append(ScopeExceeded(obligations=tuple(group)))
            continue
        lowered = z3_lowering.lower(group)
        group_findings, timed_out = unsat_explain.explain_group(lowered)
        findings.extend(group_findings)
        if timed_out:
            timed_out_groups.append(tuple(group))

    return VerificationResult(
        findings=findings, scope_exceeded=scope_exceeded, timed_out_groups=timed_out_groups
    )
