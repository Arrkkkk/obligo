"""Mechanical proof that every packages/ir-spec/examples/not-supported/
fixture behaves exactly as its own expected_parser_behavior demands.

Same discipline as packages/ir-spec/SPEC.md section 9's own verification
("the same grammar that parses a valid IF condition was fed a string
containing UNLESS and genuinely failed to parse") -- applied here to the
real, wired-up grammar instead of the reference documentation grammar.
"""

from __future__ import annotations

import warnings

import pytest

from obligo_brain.compiler.parser import (
    ObligationCompositionWarning,
    ObligationParseError,
    parse,
)

SOURCE_TAIL = "00000000-0000-0000-0000-000000000099 0 10 0.9"


# exception-unless.json: "unless delayed by a Force Majeure Event" -- the
# grammar has no UNLESS production at all. Any occurrence must fail loudly.
def test_exception_unless_fails_to_parse():
    dsl = (
        'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        'WITHIN 30d OF "signing" '
        'UNLESS "delayed by a Force Majeure Event" '
        f"{SOURCE_TAIL}"
    )
    with pytest.raises(ObligationParseError):
        parse(dsl)


# mixed-condition-and-exception.json: a valid IF sitting right next to an
# UNLESS. Pins down that a legal IF clause does not make the sentence
# partially compilable by keeping the condition and dropping the exception.
def test_mixed_condition_and_exception_fails_to_parse():
    dsl = (
        'MUST "Vendor" DELIVER "Customer" deliverables "the Deliverables" '
        'IF "the Purchase Order is signed" '
        'UNLESS "the Purchase Order is cancelled within 5 days" '
        f"{SOURCE_TAIL}"
    )
    with pytest.raises(ObligationParseError):
        parse(dsl)


# exception-nested-condition.json: multi-level nesting of condition/
# exception. Out of scope under any reading -- it's nesting by any
# definition, not just a consequence of excluding UNLESS. Any UNLESS
# anywhere, nested or not, hits the same "no production" wall.
def test_exception_nested_condition_fails_to_parse():
    dsl = (
        'MUST "Vendor" INDEMNIFY "Customer" direct_damages "direct damages" '
        'IF "a claim arises from Vendor\'s breach" '
        'UNLESS "the claim arises solely from Customer\'s misuse of the Software" '
        f"{SOURCE_TAIL}"
    )
    with pytest.raises(ObligationParseError):
        parse(dsl)


# every-during-composition.json: NOT a parse failure -- "DURING the Term"
# is legal grammar with nowhere to attach once EVERY has claimed the
# obligation's one temporal slot. This checkpoint's own deliberate
# resolution (see grammar/obligation.lark's every_form comment): parse the
# EVERY clause, drop the DURING bound, and warn rather than silently drop.
def test_every_during_composition_parses_with_warning_and_drops_during():
    dsl = (
        'MUST "Vendor" REPORT "Customer" status_report "a status report" '
        "EVERY 30d DURING 2027-01-01 .. 2027-12-31 "
        f"{SOURCE_TAIL}"
    )
    with pytest.warns(ObligationCompositionWarning):
        ob = parse(dsl)

    assert ob.temporal.to_dict() == {"kind": "EVERY", "duration": {"amount": 30, "unit": "d"}}


def test_every_without_during_does_not_warn():
    dsl = (
        'MUST "Vendor" REPORT "Customer" status_report "a status report" '
        f"EVERY 30d {SOURCE_TAIL}"
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ObligationCompositionWarning)
        ob = parse(dsl)  # must not raise
    assert ob.temporal.to_dict() == {"kind": "EVERY", "duration": {"amount": 30, "unit": "d"}}
