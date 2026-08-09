"""Obligation IR v1 AST.

Structurally mirrors packages/ir-spec/schema/obligation-ir.schema.json
exactly -- every dataclass here has a `to_dict()` that produces a payload
shaped to validate against that schema. This is the AST the real grammar
(grammar/obligation.lark) parses into; nothing here decides typecheck
questions (party/date/trigger resolution, underspecification) -- those are
the next checkpoint's job (typecheck.py, symbols.py), not this one's.

All dataclasses are frozen + eq so `parse(unparse(ast)) == ast` (the
round-trip property test) is a plain equality check, not a structural diff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from obligo_brain.compiler.version import GRAMMAR_VERSION

Modality = str  # one of MUST, MUST_NOT, SHOULD, MAY -- see MODALITIES below

MODALITIES = ("MUST", "MUST_NOT", "SHOULD", "MAY")

# The closed action taxonomy (34 verbs). Derived from real obligation
# sentences in three SEC EDGAR contract exhibits -- see grammar/
# obligation.lark's header comment for the full citation-by-citation
# derivation. This tuple and the grammar's ACTION terminal alternation must
# be kept in sync by hand; a mismatch would let the grammar accept an
# action the AST layer doesn't recognize as closed-taxonomy, or vice versa
# -- test_action_taxonomy_matches_grammar in tests/compiler covers this.
ACTIONS = (
    "NOTIFY", "DELIVER", "PAY", "DELETE", "RETAIN", "MAINTAIN",
    "INDEMNIFY", "REPORT", "PROVIDE", "CURE",
    "COOPERATE", "COMPLY", "DISCLOSE", "TERMINATE", "ASSIGN",
    "TRANSFER", "WAIVE", "EXECUTE", "REPRESENT", "ENSURE",
    "PROCURE", "WITHHOLD", "REIMBURSE", "RETURN", "GRANT",
    "USE", "ESTABLISH", "FINALIZE", "CONSULT", "NEGOTIATE",
    "PROCESS", "RECOVER", "REPAIR", "APPOINT",
)


# --- PartyRef ---------------------------------------------------------

@dataclass(frozen=True)
class UnresolvedParty:
    alias: str

    def to_dict(self) -> dict:
        return {"status": "UNRESOLVED", "alias": self.alias}


@dataclass(frozen=True)
class ResolvedParty:
    party_id: str
    canonical_name: str

    def to_dict(self) -> dict:
        return {
            "status": "RESOLVED",
            "party_id": self.party_id,
            "canonical_name": self.canonical_name,
        }


PartyRef = Union[UnresolvedParty, ResolvedParty]


# --- ObjectRef ----------------------------------------------------------

@dataclass(frozen=True)
class ObjectRef:
    class_: str
    raw_text: str

    def to_dict(self) -> dict:
        return {"class": self.class_, "raw_text": self.raw_text}


# --- Duration -------------------------------------------------------------

@dataclass(frozen=True)
class Duration:
    amount: float
    unit: str  # one of h, d, bd, w, mo, y

    def to_dict(self) -> dict:
        return {"amount": self.amount, "unit": self.unit}


# --- DateRef ---------------------------------------------------------------

@dataclass(frozen=True)
class ResolvedDate:
    date: str  # ISO YYYY-MM-DD

    def to_dict(self) -> dict:
        return {"status": "RESOLVED", "date": self.date}


@dataclass(frozen=True)
class UnresolvedDate:
    raw: str

    def to_dict(self) -> dict:
        return {"status": "UNRESOLVED", "raw": self.raw}


DateRef = Union[ResolvedDate, UnresolvedDate]


# --- TriggerRef --------------------------------------------------------

@dataclass(frozen=True)
class UnresolvedTrigger:
    raw: str

    def to_dict(self) -> dict:
        return {"status": "UNRESOLVED", "raw": self.raw}


@dataclass(frozen=True)
class ResolvedTrigger:
    ref_type: str  # EVENT | DEFINED_TERM
    ref_id: str
    raw: str

    def to_dict(self) -> dict:
        return {
            "status": "RESOLVED",
            "ref_type": self.ref_type,
            "ref_id": self.ref_id,
            "raw": self.raw,
        }


TriggerRef = Union[UnresolvedTrigger, ResolvedTrigger]


# --- Temporal ------------------------------------------------------------

@dataclass(frozen=True)
class ByTemporal:
    datetime: DateRef

    def to_dict(self) -> dict:
        return {"kind": "BY", "datetime": self.datetime.to_dict()}


@dataclass(frozen=True)
class WithinTemporal:
    duration: Duration
    of: TriggerRef

    def to_dict(self) -> dict:
        return {
            "kind": "WITHIN",
            "duration": self.duration.to_dict(),
            "of": self.of.to_dict(),
        }


@dataclass(frozen=True)
class EveryTemporal:
    duration: Duration

    def to_dict(self) -> dict:
        return {"kind": "EVERY", "duration": self.duration.to_dict()}


@dataclass(frozen=True)
class DuringTemporal:
    start: DateRef
    end: DateRef

    def to_dict(self) -> dict:
        return {
            "kind": "DURING",
            "interval": {
                "start": self.start.to_dict(),
                "end": self.end.to_dict(),
            },
        }


@dataclass(frozen=True)
class RelativeToTriggerTemporal:
    direction: str  # BEFORE | AFTER
    trigger: TriggerRef

    def to_dict(self) -> dict:
        return {
            "kind": "RELATIVE_TO_TRIGGER",
            "direction": self.direction,
            "trigger": self.trigger.to_dict(),
        }


Temporal = Union[
    ByTemporal, WithinTemporal, EveryTemporal, DuringTemporal, RelativeToTriggerTemporal
]


# --- Predicate (boolean recursion within a single IF condition) -----------

@dataclass(frozen=True)
class AtomPredicate:
    raw: str

    def to_dict(self) -> dict:
        return {"type": "atom", "raw": self.raw}


@dataclass(frozen=True)
class AndPredicate:
    left: "Predicate"
    right: "Predicate"

    def to_dict(self) -> dict:
        return {"type": "and", "left": self.left.to_dict(), "right": self.right.to_dict()}


@dataclass(frozen=True)
class OrPredicate:
    left: "Predicate"
    right: "Predicate"

    def to_dict(self) -> dict:
        return {"type": "or", "left": self.left.to_dict(), "right": self.right.to_dict()}


@dataclass(frozen=True)
class NotPredicate:
    operand: "Predicate"

    def to_dict(self) -> dict:
        return {"type": "not", "operand": self.operand.to_dict()}


Predicate = Union[AtomPredicate, AndPredicate, OrPredicate, NotPredicate]


@dataclass(frozen=True)
class Condition:
    predicate: Predicate

    def to_dict(self) -> dict:
        return {"predicate": self.predicate.to_dict()}


# --- SourceRef --------------------------------------------------------

@dataclass(frozen=True)
class SourceRef:
    segment_id: str
    char_start: int
    char_end: int

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "char_start": self.char_start,
            "char_end": self.char_end,
        }


# --- Obligation (top level) ------------------------------------------------

@dataclass(frozen=True)
class Obligation:
    modality: Modality
    obligor: PartyRef
    action: str
    obligee: PartyRef
    object: ObjectRef
    temporal: Temporal | None
    conditions: tuple[Condition, ...]
    source: SourceRef
    confidence: float
    # The parser alone never sets these True -- underspecification detection
    # is the typechecker's job (packages/ir-spec/SPEC.md section 8: type
    # rules like "BY requires a resolvable absolute date -> else
    # UNDERSPECIFIED[missing:anchor]" are typecheck rules, not parse rules).
    # Always False/() out of this checkpoint's parser, by construction.
    underspecified: bool = False
    missing_fields: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "grammar_version": GRAMMAR_VERSION,
            "modality": self.modality,
            "obligor": self.obligor.to_dict(),
            "obligee": self.obligee.to_dict(),
            "action": self.action,
            "object": self.object.to_dict(),
            "temporal": self.temporal.to_dict() if self.temporal is not None else None,
            "conditions": [c.to_dict() for c in self.conditions],
            "source": self.source.to_dict(),
            "confidence": self.confidence,
            "underspecified": self.underspecified,
            "missing_fields": list(self.missing_fields),
        }
