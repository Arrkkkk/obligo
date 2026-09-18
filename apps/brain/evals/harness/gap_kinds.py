"""Section 8's `known_gaps` tag vocabulary, on TWO axes (guideline section 8.10, F9).

Until v0.59 this vocabulary was one flat set and `report.py` classified it by
DIRECTION alone (OVERSTATING / INCOMPLETENESS), leaving five live tags
UNCLASSIFIED. F9's finding is that direction was never the first axis: the five
tags that DO carry a direction are exactly the five where IR v1 has no form for
what the document says, and the five that resisted classification are the ones
where the IR is not the thing at fault. A `kind` filter had been operating
unnamed, as the precondition for direction being answerable at all.

So: `kind` first, `direction` only where kind is REPRESENTATIONAL.

The line between the first two kinds is NOT invented here -- it is guideline
section 8.6.1's own principle promoted into the vocabulary: "`temporal: null`
marks what the IR cannot REPRESENT, never what the classifier cannot REACH."

Two consumers share `in_force_scope()` deliberately rather than each testing
`known_gaps` themselves: section 9.1's denominator and G6's disclosure must move
together by construction. CLAUDE.md's debt list records three instances of an
indirection that was only as real as the tests that didn't bypass it; a second
call site spelling this predicate out by hand would be a fourth.
"""

from __future__ import annotations

from typing import Iterable

# --- axis 1: WHAT KIND OF THING the tag records ---------------------------
#
# REPRESENTATIONAL      IR v1 has NO FORM for what the document says. The loss
#                       is baked into the gold item itself, so gold is knowingly
#                       unfaithful and a DIRECTION is both answerable and
#                       required (axis 2 below).
# REACHABILITY          The IR CAN express the form; a production surface
#                       pattern rejects the input (section 8.6/8.9 --
#                       `_WITHIN_RE`, `_RELATIVE_RE`). Gold is faithful and
#                       complete; the loss is downstream and LOUD
#                       (UNMAPPABLE_TEMPORAL, visible in criterion 1b).
# CORPUS_DEFECT         The source TEXT is defective. Section 8's own table:
#                       "not a v1 compiler gap ... no grammar change fixes it."
#                       Gold carries the defect verbatim, by rule (section 8.7).
# ANNOTATION_CONVENTION Neither the IR nor the corpus is at fault -- the gold
#                       set's OWN span/alignment rules force an exception. The
#                       tag records a departure from a guideline rule, not from
#                       the contract (section 8.3.1 v0.31: what is tagged is
#                       "spans are nested").
# WITHHELD_VALUE        The operative value does not exist to ANY party: it was
#                       withheld in the filing (section 8.1). Not a
#                       representational gap -- no IR change helps -- and not a
#                       corpus defect, since nothing is wrong with the text.
GAP_KIND = {
    "exception_unsupported": "REPRESENTATIONAL",
    "unless_unsupported": "REPRESENTATIONAL",
    "compound_action": "REPRESENTATIONAL",
    "mutual_obligation": "REPRESENTATIONAL",
    "action_not_in_taxonomy": "REPRESENTATIONAL",
    "within_preposition": "REACHABILITY",
    "relative_trigger_preposition": "REACHABILITY",
    "corpus_artifact_in_span": "CORPUS_DEFECT",
    "shared_subject_split": "ANNOTATION_CONVENTION",
    "redacted_value": "WITHHELD_VALUE",
}

UNCLASSIFIED_KIND = "UNCLASSIFIED"

# --- axis 2: direction, and ONLY for REPRESENTATIONAL ---------------------
#
# Direction of the IR's departure from the contract, NOT severity. OVERSTATING
# claims more than the document does (a monitor flags a breach the contract
# exempts); INCOMPLETENESS claims less (a monitor misses a real breach).
#
# A REPRESENTATIONAL tag absent from this map is UNCLASSIFIED and must force a
# decision. A tag of any OTHER kind has no entry here BY DESIGN, and that is the
# substance of F10's resolution: for those kinds gold is faithful, so nothing
# departs from the contract and there is no direction to assign. Their former
# UNCLASSIFIED status was never a missing decision -- it was the wrong question.
GAP_DIRECTION = {
    "exception_unsupported": "OVERSTATING",
    "unless_unsupported": "OVERSTATING",
    "compound_action": "INCOMPLETENESS",
    "mutual_obligation": "INCOMPLETENESS",
    # v0.48 (F10, scoped): INCOMPLETENESS on the identical ground as
    # compound_action -- section 8.8 puts the NEAREST taxonomy verb in `action`
    # and the real verb is lost, so the IR claims less than the document says.
    "action_not_in_taxonomy": "INCOMPLETENESS",
}

# --- the denominator, per kind (guideline section 9.1, amended v0.59) -----
#
# EXCLUDED, each on its own ground rather than by one blanket rule:
#   REPRESENTATIONAL  section 9.1 ground 2 (validity) -- the item is a KNOWING
#                     unfaithfulness, so certifying it FULLY_CORRECT would
#                     certify an IR that misstates the contract.
#   REACHABILITY      NOT ground 2 (gold is faithful) but a structurally
#                     guaranteed failure: the compile stage rejects it on every
#                     run, so admitting it would put unwinnable items in the
#                     headline denominator and corrupt the figure's meaning.
#   WITHHELD_VALUE    Held excluded pending its own DIRECTION ruling. Ground 2
#                     bites only if the item is a knowing unfaithfulness, and
#                     that is precisely the contested question for this kind
#                     (gold asserts null for a field the contract does populate).
#                     Membership cannot be settled on a ground whose own input is
#                     open, so the status quo stands and the question is queued.
#   UNCLASSIFIED      A tag whose kind was never decided must never enter the
#                     headline denominator silently. Excluding is the loud,
#                     conservative default -- and G6 names it.
#
# ADMITTED:
#   CORPUS_DEFECT, ANNOTATION_CONVENTION -- section 9.1 ground 1's own text is
#   "items IR v1 can represent faithfully", and for both kinds it can: neither
#   the IR nor the annotation departs from the contract. Ground 2 does not bite
#   either, because gold is faithful.
DENOMINATOR_EXCLUDING_KINDS = frozenset({
    "REPRESENTATIONAL",
    "REACHABILITY",
    "WITHHELD_VALUE",
    UNCLASSIFIED_KIND,
})


def kind_of(tag: str) -> str:
    """The tag's kind, or UNCLASSIFIED for a tag this vocabulary has not ruled on."""
    return GAP_KIND.get(tag, UNCLASSIFIED_KIND)


def direction_of(tag: str) -> str | None:
    """The tag's direction, or None when direction does not apply to its kind.

    None and UNCLASSIFIED are DIFFERENT answers and the caller must not collapse
    them: None means "this kind has no direction to assign" (F10's resolution),
    UNCLASSIFIED means "a decision is owed". Returning None for both would let a
    new, unruled tag hide in the bucket F10 exists to keep visible.
    """
    if kind_of(tag) != "REPRESENTATIONAL":
        return None
    return GAP_DIRECTION.get(tag, UNCLASSIFIED_KIND)


def excluding_tags(known_gaps: Iterable[str]) -> list[str]:
    """The tags on this item that keep it OUT of the in-force denominator."""
    return [t for t in known_gaps if kind_of(t) in DENOMINATOR_EXCLUDING_KINDS]


def in_force_scope(known_gaps: Iterable[str]) -> bool:
    """Is this item in criterion 2's IN-FORCE denominator (section 9.1)?

    Membership is by KIND, never by count -- section 9's v0.22 rule is unchanged,
    only the predicate it applies. An item carrying several tags is excluded if
    ANY of them is of an excluding kind, which is what keeps a mixed item like
    C14-02 (`mutual_obligation` + `shared_subject_split`) out on the strength of
    the representational tag alone.
    """
    return not excluding_tags(known_gaps)
