"""AST -> DSL printer: the inverse of parser.parse().

Exists specifically for the round-trip property test (blueprint SS19.3):
`parse(unparse(ast)) == ast` for arbitrary generated ASTs. Not named in
blueprint SS6.1's compiler/ file list (grammar/obligation.lark ·
lexer_hints.py · ast.py · parser.py · typecheck.py · symbols.py ·
normalize.py · repair.py · version.py) -- added because the round-trip
property is meaningless without a printer to round-trip through, and no
listed file's stated purpose (typecheck, symbols, normalize, repair,
versioning) covers it.
"""

from __future__ import annotations

import json
from decimal import Decimal

from obligo_brain.compiler import ast


def _q(s: str) -> str:
    return json.dumps(s)


def _party(p: ast.PartyRef) -> str:
    if isinstance(p, ast.UnresolvedParty):
        return _q(p.alias)
    raise ValueError(f"parser never emits RESOLVED party refs, cannot unparse: {p!r}")


def _date_ref(d: ast.DateRef) -> str:
    if isinstance(d, ast.ResolvedDate):
        return d.date
    if isinstance(d, ast.UnresolvedDate):
        return _q(d.raw)
    raise TypeError(d)


def _trigger_ref(t: ast.TriggerRef) -> str:
    if isinstance(t, ast.UnresolvedTrigger):
        return _q(t.raw)
    raise ValueError(f"parser never emits RESOLVED trigger refs, cannot unparse: {t!r}")


def _duration(d: ast.Duration) -> str:
    amount = int(d.amount) if float(d.amount).is_integer() else d.amount
    return f"{amount}{d.unit}"


def _temporal(t: ast.Temporal) -> str:
    if isinstance(t, ast.ByTemporal):
        return f"BY {_date_ref(t.datetime)}"
    if isinstance(t, ast.WithinTemporal):
        return f"WITHIN {_duration(t.duration)} OF {_trigger_ref(t.of)}"
    if isinstance(t, ast.EveryTemporal):
        return f"EVERY {_duration(t.duration)}"
    if isinstance(t, ast.DuringTemporal):
        return f"DURING {_date_ref(t.start)} .. {_date_ref(t.end)}"
    if isinstance(t, ast.RelativeToTriggerTemporal):
        return f"{t.direction} {_trigger_ref(t.trigger)}"
    raise TypeError(t)


def _predicate_grouped(p: ast.Predicate) -> str:
    # AND/OR/NOT chains are ambiguous in the surface syntax without
    # grouping (see grammar/obligation.lark's predicate rule comment) --
    # always wrap a compound operand in parens so the printed DSL's nesting
    # is explicit and doesn't depend on the grammar's own default
    # associativity when reparsed. Atoms never need grouping.
    text = _predicate(p)
    return text if isinstance(p, ast.AtomPredicate) else f"({text})"


def _predicate(p: ast.Predicate) -> str:
    if isinstance(p, ast.AtomPredicate):
        return _q(p.raw)
    if isinstance(p, ast.AndPredicate):
        return f"{_predicate_grouped(p.left)} AND {_predicate_grouped(p.right)}"
    if isinstance(p, ast.OrPredicate):
        return f"{_predicate_grouped(p.left)} OR {_predicate_grouped(p.right)}"
    if isinstance(p, ast.NotPredicate):
        return f"NOT {_predicate_grouped(p.operand)}"
    raise TypeError(p)


def unparse(ob: ast.Obligation) -> str:
    modality_literal = "MUST_NOT" if ob.modality == "MUST_NOT" else ob.modality
    parts = [
        modality_literal,
        _party(ob.obligor),
        ob.action,
        _party(ob.obligee),
        ob.object.class_,
        _q(ob.object.raw_text),
    ]
    if ob.temporal is not None:
        parts.append(_temporal(ob.temporal))
    for condition in ob.conditions:
        parts.append(f"IF {_predicate(condition.predicate)}")
    parts.append(ob.source.segment_id)
    parts.append(str(ob.source.char_start))
    parts.append(str(ob.source.char_end))
    parts.append(format_confidence(ob.confidence))
    return " ".join(parts)


def format_confidence(confidence: float) -> str:
    # FLOAT terminal: /0(\.\d+)?|1(\.0+)?/ -- fixed-point only, no exponent
    # support. repr() is the shortest string that round-trips exactly back
    # to the same float, but for very small values (e.g. a low-confidence
    # extraction near 1e-137) it uses scientific notation, which this
    # terminal can't parse. Decimal(repr(x)) reparses those exact digits
    # and reformats them in fixed-point -- same digits, no precision lost,
    # just no "e" in the output.
    if confidence == 0:
        return "0"
    if confidence == 1:
        return "1"
    text = repr(float(confidence))
    if "e" in text or "E" in text:
        text = format(Decimal(text), "f")
    return text
