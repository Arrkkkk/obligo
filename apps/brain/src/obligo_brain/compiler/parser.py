"""Wires grammar/obligation.lark to a real Lark parser and transforms its
parse tree into the AST defined in ast.py.

Entry point: parse(text) -> ast.Obligation, raising ObligationParseError on
any grammar-level rejection (including, deliberately, any UNLESS clause --
packages/ir-spec/SPEC.md section 6's frozen "no exception construct in v1"
boundary). Callers upstream (the eventual repair loop, blueprint SS6.3
stage 3) are responsible for retrying with a fed-back parser message; this
module's only job is to parse or fail loudly, never to guess or repair.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import lark
from lark import Lark, Token, Transformer

from obligo_brain.compiler import ast

_GRAMMAR_PATH = Path(__file__).parent / "grammar" / "obligation.lark"


class ObligationCompositionWarning(UserWarning):
    """A grammatically legal temporal composition v1's IR can't represent.

    Currently raised only for EVERY+DURING (packages/ir-spec/examples/
    not-supported/every-during-composition.json) -- distinct from
    ObligationParseError, which is for genuinely illegal grammar (e.g. an
    UNLESS clause, which has no production at all).
    """


class ObligationParseError(Exception):
    """Raised when source text does not conform to grammar/obligation.lark.

    Wraps the underlying lark.exceptions.LarkError so a caller can inspect
    `.lark_error` for the parser's own diagnostic (line/column, expected
    tokens) -- exactly what the repair loop feeds back on retry.
    """

    def __init__(self, message: str, lark_error: lark.exceptions.LarkError):
        super().__init__(message)
        self.lark_error = lark_error


def _unescape(token: Token) -> str:
    """common.ESCAPED_STRING is JSON-string-compatible; decode it as one."""
    return json.loads(str(token))


class _ObligationTransformer(Transformer):
    # -- modality --------------------------------------------------------
    def modality(self, children):
        (token,) = children
        # token.type is the terminal name (MUST/MUST_NOT/SHOULD/MAY)
        # regardless of which literal alternative matched ("MUST NOT" vs
        # "MUST_NOT"), so this also normalizes surface spelling for free.
        return token.type

    # -- parties -----------------------------------------------------------
    def obligor(self, children):
        (token,) = children
        return ast.UnresolvedParty(alias=_unescape(token))

    def obligee(self, children):
        (token,) = children
        return ast.UnresolvedParty(alias=_unescape(token))

    # -- object --------------------------------------------------------
    def raw_text(self, children):
        (token,) = children
        return _unescape(token)

    def object(self, children):
        class_token, raw_text_value = children
        return ast.ObjectRef(class_=str(class_token), raw_text=raw_text_value)

    # -- temporal ---------------------------------------------------------
    def datetime_ref(self, children):
        (token,) = children
        if token.type == "DATE":
            return ast.ResolvedDate(date=str(token))
        return ast.UnresolvedDate(raw=_unescape(token))

    def trigger_ref(self, children):
        (token,) = children
        return ast.UnresolvedTrigger(raw=_unescape(token))

    def duration(self, children):
        number_token, unit_token = children
        return ast.Duration(amount=float(number_token), unit=str(unit_token))

    def interval(self, children):
        start, end = children
        return (start, end)

    def by_form(self, children):
        (datetime_ref_value,) = children
        return ast.ByTemporal(datetime=datetime_ref_value)

    def within_form(self, children):
        duration_value, trigger_value = children
        return ast.WithinTemporal(duration=duration_value, of=trigger_value)

    def during_bound(self, children):
        (interval_value,) = children
        return interval_value

    def every_form(self, children):
        duration_value = children[0]
        if len(children) == 2:
            # EVERY + a trailing DURING bound: legal grammar (unlike an
            # UNLESS clause), but the schema's Temporal has no variant that
            # can hold both. Compiled as EVERY alone, per packages/ir-spec/
            # SPEC.md section 7 -- the outer bound is dropped, loudly, not
            # silently absorbed or silently discarded.
            warnings.warn(
                "EVERY temporal has a trailing DURING bound that v1's IR "
                "cannot represent (Temporal carries one variant, not a "
                "composition); compiling as EVERY alone and dropping the "
                "DURING bound. See packages/ir-spec/SPEC.md section 7.",
                ObligationCompositionWarning,
                stacklevel=2,
            )
        return ast.EveryTemporal(duration=duration_value)

    def during_form(self, children):
        (interval_value,) = children
        start, end = interval_value
        return ast.DuringTemporal(start=start, end=end)

    def relative_form(self, children):
        direction_token, trigger_value = children
        return ast.RelativeToTriggerTemporal(direction=str(direction_token), trigger=trigger_value)

    def temporal(self, children):
        (form,) = children
        return form

    # -- predicate / condition ---------------------------------------------
    def atom(self, children):
        (token,) = children
        return ast.AtomPredicate(raw=_unescape(token))

    def and_predicate(self, children):
        left, right = children
        return ast.AndPredicate(left=left, right=right)

    def or_predicate(self, children):
        left, right = children
        return ast.OrPredicate(left=left, right=right)

    def not_predicate(self, children):
        (operand,) = children
        return ast.NotPredicate(operand=operand)

    def condition(self, children):
        (predicate_value,) = children
        return ast.Condition(predicate=predicate_value)

    # -- source / confidence ---------------------------------------------
    def source(self, children):
        segment_id_token, char_start_token, char_end_token = children
        return ast.SourceRef(
            segment_id=str(segment_id_token),
            char_start=int(char_start_token),
            char_end=int(char_end_token),
        )

    def confidence(self, children):
        (token,) = children
        return float(token)

    # -- top level -----------------------------------------------------
    def obligation(self, children):
        modality_value = children[0]
        obligor_value = children[1]
        action_token = children[2]
        obligee_value = children[3]
        object_value = children[4]

        rest = children[5:]
        temporal_value = None
        conditions: list[ast.Condition] = []
        idx = 0
        if rest and isinstance(rest[idx], (
            ast.ByTemporal, ast.WithinTemporal, ast.EveryTemporal,
            ast.DuringTemporal, ast.RelativeToTriggerTemporal,
        )):
            temporal_value = rest[idx]
            idx += 1
        while idx < len(rest) and isinstance(rest[idx], ast.Condition):
            conditions.append(rest[idx])
            idx += 1
        source_value = rest[idx]
        confidence_value = rest[idx + 1]

        return ast.Obligation(
            modality=modality_value,
            obligor=obligor_value,
            action=str(action_token),
            obligee=obligee_value,
            object=object_value,
            temporal=temporal_value,
            conditions=tuple(conditions),
            source=source_value,
            confidence=confidence_value,
        )

    def start(self, children):
        (obligation_value,) = children
        return obligation_value


_transformer = _ObligationTransformer()
_parser: Lark | None = None


def _get_parser() -> Lark:
    global _parser
    if _parser is None:
        _parser = Lark.open(str(_GRAMMAR_PATH), parser="lalr")
    return _parser


def parse(text: str) -> ast.Obligation:
    """Parse a DSL obligation string into an ast.Obligation.

    Raises ObligationParseError on any grammar-level rejection -- including
    an UNLESS clause, which has no production in this grammar at all and so
    always fails here, never silently absorbed as a condition.
    """
    try:
        tree = _get_parser().parse(text)
    except lark.exceptions.LarkError as e:
        raise ObligationParseError(str(e), e) from e
    return _transformer.transform(tree)
