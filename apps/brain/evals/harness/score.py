"""Section 5's conjunctive predicate, clause by clause.

Pure: takes (gold item, ast.Obligation, DocumentRegistry) and returns a
per-clause verdict. No database, no network, no pipeline import beyond
compiler.ast. Every clause is independently checkable, which is what makes a
PARTIAL diagnosable rather than merely a failure.

Three comparison rules were decided at v0.28 and are implemented here
literally rather than softened:

  Clauses 3 and 4 (parties) compare by IDENTITY, not by string, whenever the
  pipeline resolved the party -- gold's alias must resolve, through the
  registry's own canonical_name/aliases matching, to the SAME party_id.
  The model's own alias is not available to compare against: ResolvedParty
  discards it and PipelineResult retains no candidate for a successfully
  typechecked obligation.

  Clause 7 (conditions) is an order-insensitive, count-sensitive multiset of
  WHITESPACE-NORMALIZED strings. Case is NOT folded: section 3.8 requires
  verbatim quotes and "NOT" versus "not" is exactly the distinction section
  17 exists to keep.

  Clause 6 (temporal) requires exact, whitespace-normalized equality on the
  constituents, trigger text included. That is deliberately strict. If it
  proves too strict, that is a MEASUREMENT worth having before section 5 is
  amended -- the posture section 11 took on _WITHIN_RE, and the reason a
  scored field is not softened ahead of evidence it needs softening.

Direction (BEFORE/AFTER) is case-normalized because it is a closed enum, not
free text -- the one place normalization is safe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from obligo_brain.compiler import ast

from evals.harness.registry import DocumentRegistry


class Outcome(str, Enum):
    FULLY_CORRECT = "FULLY_CORRECT"
    PARTIAL = "PARTIAL"
    MISSED = "MISSED"
    UNEXPECTED = "UNEXPECTED"


CLAUSES = (
    "modality", "action", "obligor", "obligee",
    "object_class", "temporal", "conditions", "underspecified",
)


def norm(s: str) -> str:
    """Whitespace normalization only -- never case-folding (see module docstring)."""
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class ItemScore:
    item_id: str
    outcome: Outcome
    clauses: dict[str, bool]
    detail: dict[str, str]

    @property
    def failed(self) -> list[str]:
        return [c for c in CLAUSES if c in self.clauses and not self.clauses[c]]


def _party_matches(gold_alias: str, pred: ast.PartyRef, reg: DocumentRegistry) -> tuple[bool, str]:
    if gold_alias == "ABSENT":
        # ABSENT matches ABSENT. The pipeline expresses "absent" as an
        # UnresolvedParty carrying an empty-ish alias; anything that resolved
        # is by definition not absent.
        if isinstance(pred, ast.ResolvedParty):
            return False, f"gold ABSENT, predicted resolved to {pred.canonical_name!r}"
        return (norm(pred.alias) == "", f"gold ABSENT, predicted alias {pred.alias!r}")

    if isinstance(pred, ast.ResolvedParty):
        gold_party = reg.resolve(gold_alias)
        if gold_party is None:
            return False, (
                f"predicted resolved to party_id {pred.party_id}, but gold alias "
                f"{gold_alias!r} does not resolve in registry {reg.doc_id}"
            )
        ok = gold_party.canonical_name == pred.canonical_name
        return ok, (
            f"gold {gold_alias!r} -> {gold_party.canonical_name!r}; "
            f"predicted -> {pred.canonical_name!r}"
        )
    return (
        norm(pred.alias) == norm(gold_alias),
        f"both UNRESOLVED: gold {gold_alias!r} vs predicted {pred.alias!r}",
    )


def _date_text(ref: ast.DateRef) -> str:
    return ref.date if isinstance(ref, ast.ResolvedDate) else ref.raw


def _trigger_text(ref: ast.TriggerRef) -> str:
    return ref.raw


def _canonical_temporal(pred: ast.Temporal | None) -> dict[str, Any] | None:
    if pred is None:
        return None
    if isinstance(pred, ast.ByTemporal):
        return {"form": "BY", "date": norm(_date_text(pred.datetime))}
    if isinstance(pred, ast.WithinTemporal):
        return {"form": "WITHIN", "amount": float(pred.duration.amount),
                "unit": pred.duration.unit, "trigger": norm(_trigger_text(pred.of))}
    if isinstance(pred, ast.EveryTemporal):
        return {"form": "EVERY", "amount": float(pred.duration.amount), "unit": pred.duration.unit}
    if isinstance(pred, ast.DuringTemporal):
        return {"form": "DURING", "start": norm(_date_text(pred.start)),
                "end": norm(_date_text(pred.end))}
    if isinstance(pred, ast.RelativeToTriggerTemporal):
        return {"form": "RELATIVE_TO_TRIGGER", "direction": pred.direction.upper(),
                "trigger": norm(_trigger_text(pred.trigger))}
    raise TypeError(f"unhandled Temporal variant {pred!r}")


def _canonical_gold_temporal(gold: dict | None) -> dict[str, Any] | None:
    """Gold stores a form plus variant-specific keys; `alias` and `date` are
    two spellings of the same BY constituent (an unresolved alias or an ISO
    date), so both collapse to one comparable field."""
    if gold is None:
        return None
    form = gold["form"]
    if form == "BY":
        return {"form": "BY", "date": norm(str(gold.get("date") or gold.get("alias") or ""))}
    if form == "WITHIN":
        return {"form": "WITHIN", "amount": float(gold["amount"]), "unit": gold["unit"],
                "trigger": norm(str(gold.get("trigger", "")))}
    if form == "EVERY":
        return {"form": "EVERY", "amount": float(gold["amount"]), "unit": gold["unit"]}
    if form == "DURING":
        return {"form": "DURING", "start": norm(str(gold["start"])), "end": norm(str(gold["end"]))}
    if form == "RELATIVE_TO_TRIGGER":
        return {"form": "RELATIVE_TO_TRIGGER", "direction": str(gold["direction"]).upper(),
                "trigger": norm(str(gold.get("trigger", "")))}
    raise ValueError(f"unrecognised gold temporal form {form!r}")


def _condition_multiset(conds) -> list[str]:
    out = []
    for c in conds:
        raw = c.predicate.raw if isinstance(c.predicate, ast.AtomPredicate) else str(c.predicate)
        out.append(norm(raw))
    return sorted(out)


def score_item(gold: dict, pred: ast.Obligation, reg: DocumentRegistry) -> ItemScore:
    clauses: dict[str, bool] = {}
    detail: dict[str, str] = {}

    clauses["modality"] = pred.modality == gold["modality"]
    detail["modality"] = f"gold {gold['modality']!r} vs predicted {pred.modality!r}"

    clauses["action"] = pred.action in gold["action_accept_set"]
    detail["action"] = f"predicted {pred.action!r} vs accept-set {gold['action_accept_set']}"

    clauses["obligor"], detail["obligor"] = _party_matches(gold["obligor"], pred.obligor, reg)
    clauses["obligee"], detail["obligee"] = _party_matches(gold["obligee"], pred.obligee, reg)

    clauses["object_class"] = pred.object.class_ in gold["object_class_accept_set"]
    detail["object_class"] = (
        f"predicted {pred.object.class_!r} vs accept-set {gold['object_class_accept_set']}"
    )

    g_t = _canonical_gold_temporal(gold.get("temporal"))
    p_t = _canonical_temporal(pred.temporal)
    clauses["temporal"] = g_t == p_t
    detail["temporal"] = f"gold {g_t} vs predicted {p_t}"

    g_c = sorted(norm(c) for c in gold["conditions"])
    p_c = _condition_multiset(pred.conditions)
    clauses["conditions"] = g_c == p_c
    detail["conditions"] = f"gold {g_c} vs predicted {p_c}"

    clauses["underspecified"] = bool(pred.underspecified) == bool(gold["underspecified"])
    detail["underspecified"] = (
        f"gold {gold['underspecified']} vs predicted {pred.underspecified}"
    )

    outcome = Outcome.FULLY_CORRECT if all(clauses.values()) else Outcome.PARTIAL
    return ItemScore(item_id=gold["item_id"], outcome=outcome, clauses=clauses, detail=detail)
