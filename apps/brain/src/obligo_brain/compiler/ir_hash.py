"""Canonical hashing for the Obligation IR -- blueprint SS8.2/SS8.3's
`obligations(org_id, ir_hash)` unique index, SS8.4's exclusion constraint,
SS6.7's `hash(sorted(ir_hashes))` verdict-cache key, and SS19.3's "Hash
stability" property (packages/ir-spec/SPEC.md section 10).

Scoped narrowly, per the CLAUDE.md ir_hash checkpoint's own scoping
conversation: this module is the *pure* half only -- canonicalize an
ast.Obligation deterministically, then hash it. "Same real-world obligation,
re-extracted, always hashes the same" and "different obligations never
collide" are both provable here, with no I/O. The *dedup-against-storage*
half -- the unique index, the exclusion constraint, and the actual
reconciliation/upsert decision when a hash is already present -- needs the
`obligations` table, which doesn't exist yet and is explicitly Phase 5's
deliverable (see CLAUDE.md's "Obligations-persistence investigation" entry;
same scope boundary, same reasoning, applied here). Acceptance criterion 5
("re-extracting the same document twice produces zero duplicate
obligations") is therefore NOT closed by this module alone -- see CLAUDE.md's
acceptance-criteria table, row 5 vs. the new row 5a.

Field-by-field canonicalization (the full per-field rationale lives in the
CLAUDE.md checkpoint entry; this is the short version):

- `object.raw_text`, `confidence`, `source.char_start`/`char_end` are
  excluded entirely. They're provenance/evidence about *how* an obligation
  was extracted (the exact quoted span, the model's confidence, the exact
  span boundary), not part of *what* the obligation is. Including any of
  them would make two genuinely identical re-extractions hash differently
  whenever the model's confidence drifts or grounding lands on a
  slightly different but overlapping span -- exactly the false-negative
  dedup failure this function exists to prevent.
- `grammar_version` is never an instance field on ast.Obligation (it's
  injected into `to_dict()` from the module-level GRAMMAR_VERSION
  constant, not stored on self) -- there is nothing to exclude here. Noted
  so a future reader doesn't mistake the absence for an oversight.
- `PartyRef`/`DateRef`/`TriggerRef` (all two-state UNRESOLVED/RESOLVED
  unions, packages/ir-spec/SPEC.md section 4's convention) hash their
  RESOLVED value (party_id; the ISO date; ref_type+ref_id) when resolved,
  or normalized raw text when not. SPEC.md section 10 states this
  explicitly for PartyRef ("canonicalization must hash the resolved form
  of a PartyRef... not the raw alias"); applied uniformly to all three
  here rather than inventing a second rule for DateRef/TriggerRef.
- `conditions` (the top-level tuple) is order-insensitive: multiple
  entries are an implicit conjunction (ir_compile.py's own docstring:
  "multiple entries become multiple separate IF clauses"), which is
  commutative. Sorted by canonical form before hashing, so `(X, Y)` and
  `(Y, X)` always produce the same hash.
- AND/OR/NOT structure *within* one condition's Predicate tree is
  deliberately NOT reordered. Canonicalizing boolean-algebra
  commutativity/associativity is a real, separate normalization problem
  that needs normalize.py (not built) -- see test_ir_hash.py's own
  regression test pinning this as a known, accepted gap rather than a
  silently "solved" one. Today's real extraction->compile bridge
  (ir_compile.py) never constructs an AndPredicate/OrPredicate from LLM
  output in the first place -- those only arise from parsing DSL text
  that already contains literal AND/OR keywords -- so this gap is real but
  currently dormant on the actual extraction path.
"""

from __future__ import annotations

import hashlib
import json
import re

from obligo_brain.compiler import ast

_WHITESPACE_RUN = re.compile(r"\s+")


def _normalize_text(raw: str) -> str:
    return _WHITESPACE_RUN.sub(" ", raw.strip())


def _canon_party(party: ast.PartyRef) -> tuple:
    if isinstance(party, ast.ResolvedParty):
        return ("RESOLVED", party.party_id)
    return ("UNRESOLVED", _normalize_text(party.alias))


def _canon_date(date_ref: ast.DateRef) -> tuple:
    if isinstance(date_ref, ast.ResolvedDate):
        return ("RESOLVED", date_ref.date)
    return ("UNRESOLVED", _normalize_text(date_ref.raw))


def _canon_trigger(trigger_ref: ast.TriggerRef) -> tuple:
    if isinstance(trigger_ref, ast.ResolvedTrigger):
        return ("RESOLVED", trigger_ref.ref_type, trigger_ref.ref_id)
    return ("UNRESOLVED", _normalize_text(trigger_ref.raw))


def _canon_duration(duration: ast.Duration) -> tuple:
    return (duration.amount, duration.unit)


def _canon_temporal(temporal: ast.Temporal | None) -> tuple | None:
    if temporal is None:
        return None
    if isinstance(temporal, ast.ByTemporal):
        return ("BY", _canon_date(temporal.datetime))
    if isinstance(temporal, ast.WithinTemporal):
        return ("WITHIN", _canon_duration(temporal.duration), _canon_trigger(temporal.of))
    if isinstance(temporal, ast.EveryTemporal):
        return ("EVERY", _canon_duration(temporal.duration))
    if isinstance(temporal, ast.DuringTemporal):
        return ("DURING", _canon_date(temporal.start), _canon_date(temporal.end))
    if isinstance(temporal, ast.RelativeToTriggerTemporal):
        return ("RELATIVE_TO_TRIGGER", temporal.direction, _canon_trigger(temporal.trigger))
    raise TypeError(f"unhandled Temporal variant: {temporal!r}")


def _canon_predicate(predicate: ast.Predicate) -> tuple:
    # Structural fidelity only -- AND/OR/NOT nesting is preserved exactly
    # as given, never reordered. See module docstring's condition-ordering
    # paragraph (the "Case 2" gap).
    if isinstance(predicate, ast.AtomPredicate):
        return ("ATOM", _normalize_text(predicate.raw))
    if isinstance(predicate, ast.AndPredicate):
        return ("AND", _canon_predicate(predicate.left), _canon_predicate(predicate.right))
    if isinstance(predicate, ast.OrPredicate):
        return ("OR", _canon_predicate(predicate.left), _canon_predicate(predicate.right))
    if isinstance(predicate, ast.NotPredicate):
        return ("NOT", _canon_predicate(predicate.operand))
    raise TypeError(f"unhandled Predicate variant: {predicate!r}")


def _canon_condition(condition: ast.Condition) -> tuple:
    return _canon_predicate(condition.predicate)


def canonicalize(obligation: ast.Obligation) -> tuple:
    """A deterministic, order- and provenance-insensitive structural form of
    `obligation`. Two obligations that are the same real-world obligation --
    modulo whitespace, alias choice (once resolved), condition order,
    confidence, and exact span boundary -- canonicalize identically. See the
    module docstring for the full field-by-field rationale.
    """
    conditions = tuple(sorted(_canon_condition(c) for c in obligation.conditions))
    return (
        obligation.modality,
        _canon_party(obligation.obligor),
        obligation.action,
        _canon_party(obligation.obligee),
        obligation.object.class_,
        _canon_temporal(obligation.temporal),
        conditions,
        obligation.source.segment_id,
    )


def ir_hash(obligation: ast.Obligation) -> str:
    """The obligation's dedup/idempotency key (blueprint SS8.2's
    `obligations(org_id, ir_hash)` unique index; packages/ir-spec/SPEC.md
    section 10). SHA-256 hex digest of `canonicalize(obligation)`, matching
    the hashing primitive already used for `agent_runs.input_hash`/
    `prompt_hash` (graphs/extraction.py, graphs/repair.py) -- no new
    dependency, stdlib hashlib throughout.

    Pure and deterministic: proves the "same obligation always hashes the
    same, different obligations never collide" half only. Using this to
    actually dedupe against persisted rows needs the `obligations` table,
    which is Phase 5's deliverable -- see this module's own docstring and
    CLAUDE.md's ir_hash checkpoint entry for the drawn scope boundary.
    """
    canonical_json = json.dumps(canonicalize(obligation), separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode()).hexdigest()
