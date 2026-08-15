"""Tests for the pure ir_hash canonicalization+hash function
(compiler/ir_hash.py). No DB, no LLM, no network.

Every base obligation here is built via the real parser.parse() -- either
directly from a hand-written DSL string (matching test_ir_compile.py's own
`_candidate()`-helper convention) or, for the hypothesis properties, via
`parse(unparse(drawn))` on a strategies.obligation()-drawn AST, the same
"reparse through the real parser" discipline test_properties.py's round-trip
test already established. Nothing under test here is a bare hand-constructed
AST standing in for something the parser could not itself have produced --
the one deliberate exception (ResolvedTrigger) is called out and justified
at its own test, below.

ResolvedParty (real, via typecheck() against a real registered party in
Postgres) is proven separately in test_ir_hash_db.py -- it needs a database.
ResolvedDate is reachable via parser.py directly (a literal ISO DATE token
compiles straight to ResolvedDate -- grammar/obligation.lark's own
`datetime_ref` comment) and is exercised here through parse(), no DB needed.
ResolvedTrigger has no real producer anywhere in this codebase yet
(typecheck.py's symbols.resolve_trigger() always returns None in v1, and the
grammar's trigger_ref production only ever emits UnresolvedTrigger) -- it's
exercised via direct dataclass construction, documented at its use site.
"""

from __future__ import annotations

import dataclasses
import json

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from obligo_brain.compiler import ast
from obligo_brain.compiler.ir_hash import ir_hash
from obligo_brain.compiler.parser import parse
from obligo_brain.compiler.unparse import unparse
from tests.compiler.strategies import obligation

_SEGMENT = "00000000-0000-0000-0000-000000000001"
_SEGMENT_2 = "00000000-0000-0000-0000-000000000002"


def _dsl(
    *,
    modality: str = "MUST",
    obligor: str = "Vendor",
    action: str = "DELIVER",
    obligee: str = "Customer",
    object_class: str = "deliverables",
    object_raw_text: str = "the Deliverables",
    temporal: str | None = None,
    conditions: list[str] | None = None,
    segment_id: str = _SEGMENT,
    char_start: int = 0,
    char_end: int = 10,
    confidence: str = "0.9",
) -> str:
    parts = [
        modality,
        json.dumps(obligor),
        action,
        json.dumps(obligee),
        object_class,
        json.dumps(object_raw_text),
    ]
    if temporal is not None:
        parts.append(temporal)
    for c in conditions or []:
        parts.append(f"IF {json.dumps(c)}")
    parts.extend([segment_id, str(char_start), str(char_end), confidence])
    return " ".join(parts)


def _ob(**kwargs) -> ast.Obligation:
    return parse(_dsl(**kwargs))


# --- excluded fields (provenance/evidence, not identity) -------------------


def test_confidence_excluded_from_hash():
    a = _ob(confidence="0.9")
    b = _ob(confidence="0.1")
    assert a != b
    assert ir_hash(a) == ir_hash(b)


def test_object_raw_text_excluded_from_hash():
    a = _ob(object_raw_text="the Deliverables")
    b = _ob(object_raw_text="all Deliverables under this Agreement")
    assert a != b
    assert ir_hash(a) == ir_hash(b)


def test_source_char_offsets_excluded_from_hash():
    a = _ob(char_start=0, char_end=10)
    b = _ob(char_start=5, char_end=400)
    assert a != b
    assert ir_hash(a) == ir_hash(b)


def test_source_segment_id_is_included_in_hash():
    a = _ob(segment_id=_SEGMENT)
    b = _ob(segment_id=_SEGMENT_2)
    assert ir_hash(a) != ir_hash(b)


# --- whitespace insignificance ---------------------------------------------


def test_alias_whitespace_is_insignificant():
    a = _ob(obligor="Acme Corp")
    b = _ob(obligor="  Acme   Corp  ")
    # The ASTs themselves genuinely differ -- alias text is stored verbatim,
    # per this project's span-grounding discipline. Only the hash function
    # normalizes past this.
    assert a != b
    assert ir_hash(a) == ir_hash(b)


def test_condition_atom_whitespace_is_insignificant():
    a = _ob(conditions=["the Customer has defaulted"])
    b = _ob(conditions=["the   Customer  has defaulted "])
    assert a != b
    assert ir_hash(a) == ir_hash(b)


# --- condition ordering: Case 1 (top-level tuple, canonicalized) ----------


def test_condition_order_does_not_affect_hash():
    forward = _ob(conditions=["A has occurred", "B has occurred"])
    backward = _ob(conditions=["B has occurred", "A has occurred"])
    assert forward != backward  # genuinely different ASTs -- tuple order differs
    assert ir_hash(forward) == ir_hash(backward)


# --- AND/OR internal reordering: Case 2 (documented, accepted gap) --------


def test_and_or_internal_operand_order_is_not_canonicalized_known_gap():
    """Pinned as a known, accepted gap -- not silently fixed. Canonicalizing
    AND/OR commutativity is real boolean-algebra normalization that needs
    normalize.py (not built); see ir_hash.py's module docstring. Today's
    real extraction pipeline (ir_compile.py) never constructs an
    AndPredicate/OrPredicate from LLM output in the first place -- those
    only arise from parsing DSL text that already contains a literal
    AND/OR keyword -- so this gap is real but currently dormant on the
    actual extraction path, not reachable via re-extracting a real document
    today.
    """
    a_and_b = parse(
        'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        f'IF "A" AND "B" {_SEGMENT} 0 10 0.9'
    )
    b_and_a = parse(
        'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        f'IF "B" AND "A" {_SEGMENT} 0 10 0.9'
    )
    assert ir_hash(a_and_b) != ir_hash(b_and_a)


# --- distinctness: flipping a real field always changes the hash ----------


def test_modality_flip_changes_hash():
    assert ir_hash(_ob(modality="MUST")) != ir_hash(_ob(modality="MUST_NOT"))


def test_action_flip_changes_hash():
    assert ir_hash(_ob(action="DELIVER")) != ir_hash(_ob(action="NOTIFY"))


def test_object_class_flip_changes_hash():
    assert ir_hash(_ob(object_class="deliverables")) != ir_hash(_ob(object_class="personal_data"))


def test_obligor_alias_real_change_changes_hash():
    assert ir_hash(_ob(obligor="Acme Corp")) != ir_hash(_ob(obligor="Widget Inc"))


def test_temporal_presence_changes_hash():
    assert ir_hash(_ob(temporal=None)) != ir_hash(_ob(temporal="BY 2026-01-01"))


def test_temporal_shape_flip_changes_hash():
    assert ir_hash(_ob(temporal="BY 2026-01-01")) != ir_hash(_ob(temporal="EVERY 30d"))


# --- ResolvedDate: real, via parser.py's literal DATE token ----------------


def test_resolved_date_hashes_by_date_value_not_dsl_form():
    ob = _ob(temporal="BY 2026-01-01")
    assert isinstance(ob.temporal, ast.ByTemporal)
    assert isinstance(ob.temporal.datetime, ast.ResolvedDate)
    # Sanity: this genuinely differs from an unresolved BY (a defined-term alias).
    unresolved = _ob(temporal='BY "the Delivery Date"')
    assert ir_hash(ob) != ir_hash(unresolved)


# --- ResolvedTrigger: no real producer exists yet -- direct construction --


def test_resolved_trigger_hashes_by_ref_not_raw_text_direct_construction():
    """ResolvedTrigger has no real producer anywhere in this codebase yet:
    grammar/obligation.lark's trigger_ref production only ever emits
    UnresolvedTrigger, and typecheck.py's symbols.resolve_trigger() always
    returns None in v1 (see that module's own docstring -- no declared-
    event-type/defined-terms registry exists). Constructed directly here:
    a valid, spec-legal TriggerRef state (packages/ir-spec/SPEC.md section
    4's two-state convention) that just isn't reachable via today's
    pipeline yet -- the same "real function, honestly unreachable in v1"
    status symbols.py's own docstring already gives resolve_trigger().
    """
    base = _ob(temporal='WITHIN 5d OF "a Security Incident"')
    assert isinstance(base.temporal, ast.WithinTemporal)
    assert isinstance(base.temporal.of, ast.UnresolvedTrigger)

    resolved_a = dataclasses.replace(
        base,
        temporal=dataclasses.replace(
            base.temporal,
            of=ast.ResolvedTrigger(ref_type="EVENT", ref_id="evt-123", raw="a Security Incident"),
        ),
    )
    # Different raw text, same ref -- must hash the same once resolved.
    resolved_b = dataclasses.replace(
        base,
        temporal=dataclasses.replace(
            base.temporal,
            of=ast.ResolvedTrigger(ref_type="EVENT", ref_id="evt-123", raw="the Incident"),
        ),
    )
    assert ir_hash(resolved_a) == ir_hash(resolved_b)
    # And genuinely differs from the unresolved base.
    assert ir_hash(resolved_a) != ir_hash(base)


# --- property tests (blueprint SS19.3's "Hash stability", made real) ------


@given(obligation())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=200)
def test_ir_hash_is_deterministic(ob):
    real = parse(unparse(ob))
    assert ir_hash(real) == ir_hash(real)
    assert ir_hash(real) == ir_hash(parse(unparse(real)))


@given(
    obligation(),
    st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    st.randoms(),
)
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=200)
def test_ir_hash_stable_under_insignificant_perturbation(ob, new_confidence, rng):
    """Hypothesis form of blueprint SS19.3's "Hash stability" property:
    semantically identical IR differing only in confidence or condition
    order must produce the same ir_hash. `real` is built via
    parse(unparse(drawn)) -- a genuine parser-constructed instance -- and
    the perturbation below isolates exactly the two fields this checkpoint
    claims are insignificant (confidence, condition order), rather than
    standing in as a shortcut for "a real obligation".
    """
    real = parse(unparse(ob))
    shuffled_conditions = list(real.conditions)
    rng.shuffle(shuffled_conditions)
    perturbed = dataclasses.replace(
        real, confidence=new_confidence, conditions=tuple(shuffled_conditions)
    )
    assert ir_hash(real) == ir_hash(perturbed)


@given(obligation(), st.sampled_from(ast.MODALITIES))
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=100)
def test_modality_change_always_changes_hash(ob, new_modality):
    real = parse(unparse(ob))
    assume(new_modality != real.modality)
    changed = dataclasses.replace(real, modality=new_modality)
    assert ir_hash(real) != ir_hash(changed)
