"""Property-based tests (blueprint SS19.3) for the real parser.

Of blueprint's 8 named properties, exactly two are buildable at this
checkpoint -- the rest genuinely require components this checkpoint was
explicitly told not to build:

| Property               | Status | Why |
| ----------------------- | ------ | --- |
| Round-trip               | BUILT  | parse(unparse(ast)) == ast -- pure grammar+AST, no other component needed |
| Termination               | BUILT  | parser must not hang/crash on adversarial input -- pure grammar+parser concern |
| Idempotence               | deferred | needs normalize.py (the normalizer), not built yet |
| Hash stability             | deferred | needs ir_hash's canonicalization function (typecheck-adjacent, not built) |
| Typecheck soundness       | deferred | needs typecheck.py + Z3 lowering, neither built |
| Temporal totality          | deferred | "resolves to a concrete interval or is UNDERSPECIFIED" is a typecheck-rule question (SPEC.md section 8); the parser alone has no notion of underspecification (see test_ir_spec_examples.py's underspecified-* tests) |
| Grounding invariant        | deferred here | needs real segment text to check a span against; this DSL-level parser never receives segment text as input (see grammar/obligation.lark's header: it parses an already-extracted candidate, not raw source text). Proven instead at tests/graphs/test_ground.py (the Extractor -> Span Grounder checkpoint, §21), the layer that actually has segment text to check against |
| Conflict symmetry           | deferred | needs the verifier (Z3), not built |
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import jsonschema
from hypothesis import HealthCheck, given, settings

from obligo_brain.compiler.parser import ObligationParseError, parse
from obligo_brain.compiler.unparse import unparse
from tests.compiler.strategies import obligation

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[4]
    / "packages"
    / "ir-spec"
    / "schema"
    / "obligation-ir.schema.json"
)
_VALIDATOR = jsonschema.Draft202012Validator(json.loads(_SCHEMA_PATH.read_text()))


@given(obligation())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=300)
def test_round_trip(ob):
    dsl = unparse(ob)
    reparsed = parse(dsl)
    assert reparsed == ob


@given(obligation())
@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_round_trip_output_validates_against_schema(ob):
    reparsed = parse(unparse(ob))
    errors = list(_VALIDATOR.iter_errors(reparsed.to_dict()))
    assert errors == []


def _time_bounded_parse(dsl: str, bound_seconds: float = 3.0):
    start = time.monotonic()
    try:
        result = parse(dsl)
    except ObligationParseError:
        result = None
    elapsed = time.monotonic() - start
    assert elapsed < bound_seconds, f"parse took {elapsed:.2f}s, exceeding {bound_seconds}s bound"
    return result


def test_termination_deeply_nested_predicate():
    # 300-deep left-nested AND chain: "a0" AND ("a1" AND ("a2" AND ...))
    depth = 300
    predicate_src = '"leaf"'
    for i in range(depth):
        predicate_src = f'"a{i}" AND {predicate_src}'
    dsl = (
        'MUST "Vendor" INDEMNIFY "Customer" direct_damages "damages" '
        f"IF {predicate_src} "
        "00000000-0000-0000-0000-000000000001 0 10 0.9"
    )
    ob = _time_bounded_parse(dsl)
    assert ob is not None
    # depth+1 atoms total (depth "aN" leaves plus the innermost "leaf")
    def count_atoms(p):
        from obligo_brain.compiler import ast as _ast

        if isinstance(p, _ast.AtomPredicate):
            return 1
        if isinstance(p, _ast.AndPredicate):
            return count_atoms(p.left) + count_atoms(p.right)
        if isinstance(p, _ast.OrPredicate):
            return count_atoms(p.left) + count_atoms(p.right)
        if isinstance(p, _ast.NotPredicate):
            return count_atoms(p.operand)
        raise TypeError(p)

    assert count_atoms(ob.conditions[0].predicate) == depth + 1


def test_termination_very_long_alias():
    huge_alias = "x" * 100_000
    dsl = (
        f'MUST "{huge_alias}" DELIVER "Customer" deliverables "the Deliverables" '
        "00000000-0000-0000-0000-000000000001 0 10 0.9"
    )
    ob = _time_bounded_parse(dsl)
    assert ob is not None
    assert ob.obligor.alias == huge_alias


def test_termination_adversarial_garbage_fails_fast_not_hangs():
    # A long run of characters that never forms a valid token at all --
    # must fail cleanly (ObligationParseError), not hang or stack-overflow.
    garbage = "!@#$%^&*()" * 5000
    start = time.monotonic()
    try:
        parse(garbage)
        raised = False
    except ObligationParseError:
        raised = True
    elapsed = time.monotonic() - start
    assert raised
    assert elapsed < 3.0
