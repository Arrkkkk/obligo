"""hypothesis strategies generating arbitrary ast.Obligation instances --
restricted to exactly the subset a real parse() call can itself produce
(UnresolvedParty only, never ResolvedParty; UnresolvedTrigger only, never
ResolvedTrigger; underspecified=False, missing_fields=()), since the
round-trip property (parse(unparse(x)) == x) is only meaningful over ASTs
the parser could have produced in the first place -- unparse() intentionally
raises on a ResolvedParty/ResolvedTrigger it could never have emitted.
"""

from __future__ import annotations

import string
from datetime import date

from hypothesis import strategies as st

from obligo_brain.compiler import ast

_TEXT_ALPHABET = string.ascii_letters + string.digits + " .,'-"

text_field = st.text(alphabet=_TEXT_ALPHABET, min_size=1, max_size=30)

object_class = st.builds(
    lambda first, rest: first + rest,
    st.sampled_from(string.ascii_lowercase),
    st.text(alphabet=string.ascii_lowercase + "_", max_size=15),
)

segment_id = st.uuids().map(str)

iso_date = st.dates(min_value=date(1000, 1, 1), max_value=date(9999, 12, 31)).map(
    lambda d: d.isoformat()
)

duration_amount = st.floats(min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False)
duration_unit = st.sampled_from(["h", "d", "bd", "w", "mo", "y"])

confidence = st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)

action = st.sampled_from(ast.ACTIONS)


@st.composite
def unresolved_party(draw):
    return ast.UnresolvedParty(alias=draw(text_field))


@st.composite
def object_ref(draw):
    return ast.ObjectRef(class_=draw(object_class), raw_text=draw(text_field))


@st.composite
def duration(draw):
    return ast.Duration(amount=draw(duration_amount), unit=draw(duration_unit))


@st.composite
def date_ref(draw):
    return draw(
        st.one_of(
            iso_date.map(ast.ResolvedDate),
            text_field.map(ast.UnresolvedDate),
        )
    )


@st.composite
def trigger_ref(draw):
    return ast.UnresolvedTrigger(raw=draw(text_field))


@st.composite
def temporal(draw):
    return draw(
        st.one_of(
            date_ref().map(ast.ByTemporal),
            st.builds(ast.WithinTemporal, duration=duration(), of=trigger_ref()),
            duration().map(ast.EveryTemporal),
            st.builds(ast.DuringTemporal, start=date_ref(), end=date_ref()),
            st.builds(
                ast.RelativeToTriggerTemporal,
                direction=st.sampled_from(["BEFORE", "AFTER"]),
                trigger=trigger_ref(),
            ),
        )
    )


def predicate(max_leaves: int = 4):
    atom = text_field.map(ast.AtomPredicate)
    return st.recursive(
        atom,
        lambda children: st.one_of(
            st.builds(ast.AndPredicate, left=children, right=children),
            st.builds(ast.OrPredicate, left=children, right=children),
            children.map(ast.NotPredicate),
        ),
        max_leaves=max_leaves,
    )


@st.composite
def condition(draw, max_leaves: int = 4):
    return ast.Condition(predicate=draw(predicate(max_leaves)))


@st.composite
def source_ref(draw):
    start = draw(st.integers(min_value=0, max_value=10_000))
    end = start + draw(st.integers(min_value=1, max_value=1000))
    return ast.SourceRef(segment_id=draw(segment_id), char_start=start, char_end=end)


@st.composite
def obligation(draw, max_conditions: int = 3, max_predicate_leaves: int = 4):
    return ast.Obligation(
        modality=draw(st.sampled_from(ast.MODALITIES)),
        obligor=draw(unresolved_party()),
        action=draw(action),
        obligee=draw(unresolved_party()),
        object=draw(object_ref()),
        temporal=draw(st.one_of(st.none(), temporal())),
        conditions=tuple(
            draw(st.lists(condition(max_predicate_leaves), max_size=max_conditions))
        ),
        source=draw(source_ref()),
        confidence=draw(confidence),
    )
