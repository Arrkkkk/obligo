"""Round-trip proof: the real parser against packages/ir-spec/'s own frozen
worked examples.

packages/ir-spec/examples/*.json pairs a source_text with its compiled IR.
This checkpoint's grammar (grammar/obligation.lark) does not parse English
source_text -- it parses the structured DSL an upstream IR Compiler stage
would build from an already-extracted candidate (see parser.py's module
docstring). So for each example we hand-construct DSL input matching that
example's *IR shape* (as the task explicitly allows), parse it, and prove
the result validates against the schema.

Two real, deliberate divergences from bit-for-bit fixture equality, both
documented at the point they occur rather than silently glossed over:

1. must-not-no-temporal.json has RESOLVED parties (post-typecheck state).
   The parser only ever emits UNRESOLVED party refs (packages/ir-spec/
   SPEC.md section 4) -- symbol resolution is the typechecker's job, not
   built yet. We construct the UNRESOLVED-party equivalent instead of
   claiming to reproduce the fixture's RESOLVED state.

2. underspecified-missing-unit.json and underspecified-missing-anchor.json
   have underspecified=true with populated missing_fields. Detecting
   underspecification is a typecheck-rule concern (SPEC.md section 8:
   "BY requires a resolvable absolute date -> else
   UNDERSPECIFIED[missing:anchor]" is a *type* rule), not something the
   grammar alone can decide -- so the parser always emits
   underspecified=False, missing_fields=() by construction. We assert that
   explicitly, and assert everything else about the shape matches.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from obligo_brain.compiler.parser import parse

IR_SPEC_DIR = Path(__file__).resolve().parents[4] / "packages" / "ir-spec"
SCHEMA_PATH = IR_SPEC_DIR / "schema" / "obligation-ir.schema.json"
EXAMPLES_DIR = IR_SPEC_DIR / "examples"

_schema = json.loads(SCHEMA_PATH.read_text())
jsonschema.Draft202012Validator.check_schema(_schema)
_validator = jsonschema.Draft202012Validator(_schema)


def _fixture(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text())


def _assert_valid(ir: dict) -> None:
    errors = list(_validator.iter_errors(ir))
    assert errors == [], f"schema violations: {errors}"


# Each entry: (fixture filename, hand-constructed DSL matching its IR shape)
# source/confidence tails are pulled from the fixture itself at test time,
# not hand-copied, so there's no transcription risk on those fields.
EXACT_MATCH_CASES = [
    (
        "must-by.json",
        'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" BY 2027-03-01',
    ),
    (
        "should-within.json",
        'SHOULD "Vendor" NOTIFY "Customer" security_incident "a Security Incident" '
        'WITHIN 5bd OF "discovering a Security Incident"',
    ),
    (
        "may-relative-to-trigger.json",
        'MAY "Vendor" PROVIDE "Customer" refund "a refund" '
        'AFTER "receipt of the returned Product"',
    ),
    (
        "must-every.json",
        'MUST "Vendor" REPORT "Customer" status_report "a status report" EVERY 30d',
    ),
    (
        "must-during.json",
        'MUST "Vendor" MAINTAIN "Customer" software "the Software" '
        "DURING 2027-01-01 .. 2027-12-31",
    ),
    (
        "must-if-condition.json",
        'MUST "Vendor" INDEMNIFY "Customer" direct_damages "direct damages" '
        'IF "a claim arises from Vendor\'s breach" AND "the claim is finally adjudicated"',
    ),
]


@pytest.mark.parametrize("fixture_name,dsl_body", EXACT_MATCH_CASES)
def test_parses_to_exact_fixture_ir(fixture_name, dsl_body):
    fixture = _fixture(fixture_name)
    src = fixture["ir"]["source"]
    dsl = f'{dsl_body} {src["segment_id"]} {src["char_start"]} {src["char_end"]} {fixture["ir"]["confidence"]}'
    ob = parse(dsl)
    result = ob.to_dict()
    _assert_valid(result)
    assert result == fixture["ir"]


def test_must_not_no_temporal_unresolved_party_equivalent():
    fixture = _fixture("must-not-no-temporal.json")
    src = fixture["ir"]["source"]
    dsl = (
        f'MUST NOT "Vendor" DISCLOSE "Any Third Party" '
        f'confidential_information "Confidential Information" '
        f'{src["segment_id"]} {src["char_start"]} {src["char_end"]} {fixture["ir"]["confidence"]}'
    )
    ob = parse(dsl)
    result = ob.to_dict()
    _assert_valid(result)

    expected_parser_shape = dict(fixture["ir"])
    expected_parser_shape["obligor"] = {"status": "UNRESOLVED", "alias": "Vendor"}
    expected_parser_shape["obligee"] = {"status": "UNRESOLVED", "alias": "Any Third Party"}
    assert result == expected_parser_shape
    assert fixture["ir"]["obligor"]["status"] == "RESOLVED", (
        "sanity check: the fixture really does carry post-typecheck RESOLVED "
        "parties, confirming this is a real divergence, not a stale assumption"
    )


def test_underspecified_missing_unit_temporal_null():
    fixture = _fixture("underspecified-missing-unit.json")
    src = fixture["ir"]["source"]
    dsl = (
        f'SHOULD "Vendor" NOTIFY "Customer" security_incident "any security incident" '
        f'{src["segment_id"]} {src["char_start"]} {src["char_end"]} {fixture["ir"]["confidence"]}'
    )
    ob = parse(dsl)
    result = ob.to_dict()
    _assert_valid(result)

    assert result["temporal"] is None
    assert ob.underspecified is False, (
        "parser never sets underspecified=True -- detecting a vague temporal "
        "phrase like 'promptly' as an underspecification candidate (vs. no "
        "temporal at all) is a typechecker-stage decision not yet built"
    )
    expected_parser_shape = dict(fixture["ir"])
    expected_parser_shape["underspecified"] = False
    expected_parser_shape["missing_fields"] = []
    assert result == expected_parser_shape


def test_underspecified_missing_anchor_by_shape_unresolved_date():
    fixture = _fixture("underspecified-missing-anchor.json")
    src = fixture["ir"]["source"]
    dsl = (
        f'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        f'BY "the Delivery Date" '
        f'{src["segment_id"]} {src["char_start"]} {src["char_end"]} {fixture["ir"]["confidence"]}'
    )
    ob = parse(dsl)
    result = ob.to_dict()
    _assert_valid(result)

    # The BY-shape-with-UNRESOLVED-datetime IS grammar-producible (a literal
    # ALIAS instead of a DATE token) -- this part matches the fixture exactly.
    assert result["temporal"] == fixture["ir"]["temporal"]
    assert ob.underspecified is False
    expected_parser_shape = dict(fixture["ir"])
    expected_parser_shape["underspecified"] = False
    expected_parser_shape["missing_fields"] = []
    assert result == expected_parser_shape
