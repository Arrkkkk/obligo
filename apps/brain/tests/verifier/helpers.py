"""Shared obligation builders for the verifier test suite. Every obligation
built here is already RESOLVED (both parties) by default, matching what the
verifier actually receives in practice -- it runs after typecheck(), never
before (verify.py's own module docstring).
"""

from __future__ import annotations

import itertools

from obligo_brain.compiler import ast

_counter = itertools.count(1)


def source_ref() -> ast.SourceRef:
    n = next(_counter)
    return ast.SourceRef(segment_id=f"00000000-0000-0000-0000-{n:012d}", char_start=0, char_end=50)


VENDOR = ast.ResolvedParty(party_id="11111111-1111-1111-1111-111111111111", canonical_name="Acme Vendor Corp.")
CUSTOMER = ast.ResolvedParty(party_id="22222222-2222-2222-2222-222222222222", canonical_name="Beta Customer Inc.")
OTHER_VENDOR = ast.ResolvedParty(party_id="33333333-3333-3333-3333-333333333333", canonical_name="Zeta Supplier LLC")


def during(start: str, end: str) -> ast.DuringTemporal:
    return ast.DuringTemporal(start=ast.ResolvedDate(date=start), end=ast.ResolvedDate(date=end))


def by(deadline: str) -> ast.ByTemporal:
    return ast.ByTemporal(datetime=ast.ResolvedDate(date=deadline))


def within(amount: float, unit: str, trigger_raw: str) -> ast.WithinTemporal:
    return ast.WithinTemporal(duration=ast.Duration(amount=amount, unit=unit), of=ast.UnresolvedTrigger(raw=trigger_raw))


def relative(direction: str, trigger_raw: str) -> ast.RelativeToTriggerTemporal:
    return ast.RelativeToTriggerTemporal(direction=direction, trigger=ast.UnresolvedTrigger(raw=trigger_raw))


def every(amount: float, unit: str) -> ast.EveryTemporal:
    return ast.EveryTemporal(duration=ast.Duration(amount=amount, unit=unit))


def cond(raw: str, *, negate: bool = False) -> ast.Condition:
    predicate: ast.Predicate = ast.AtomPredicate(raw=raw)
    if negate:
        predicate = ast.NotPredicate(operand=predicate)
    return ast.Condition(predicate=predicate)


def obligation(
    *,
    modality: str,
    action: str,
    object_class: str,
    object_text: str | None = None,
    obligor: ast.PartyRef = VENDOR,
    obligee: ast.PartyRef = CUSTOMER,
    temporal: ast.Temporal | None = None,
    conditions: tuple[ast.Condition, ...] = (),
    confidence: float = 0.9,
) -> ast.Obligation:
    return ast.Obligation(
        modality=modality,
        obligor=obligor,
        action=action,
        obligee=obligee,
        object=ast.ObjectRef(class_=object_class, raw_text=object_text or object_class.replace("_", " ")),
        temporal=temporal,
        conditions=conditions,
        source=source_ref(),
        confidence=confidence,
    )
