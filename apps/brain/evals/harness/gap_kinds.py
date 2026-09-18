"""Section 8's `known_gaps` tag vocabulary, on TWO axes (guideline section 8.10, F9).

Until v0.59 this vocabulary was one flat set and `report.py` classified it by
DIRECTION alone (OVERSTATING / INCOMPLETENESS), leaving five live tags
UNCLASSIFIED. F9's finding is that direction was never the first axis: the five
tags that DO carry a direction are exactly the five where IR v1 has no form for
what the document says, and the five that resisted classification are the ones
where the IR is not the thing at fault. A `kind` filter had been operating
unnamed, as the precondition for direction being answerable at all.

So: `kind` first, `direction` second -- and v0.60 (F18) SHARPENS what the second
axis is asked of. v0.59 tied direction to REPRESENTATIONAL alone, which was a
proxy for the real test rather than the test itself. The real test is:

    DIRECTION IS ASSIGNABLE WHEREVER GOLD DEPARTS FROM THE DOCUMENT.

REPRESENTATIONAL departs because the IR has no form for the clause.
WITHHELD_VALUE departs for a different reason and departs all the same: the IR
HAS the form, and section 8.1 rules the field `null` anyway. The remaining three
kinds carry no direction because gold does not depart at all -- which is F10's
resolution, restated on the ground that actually does the work.

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
# WITHHELD_VALUE        The operative VALUE was withheld in the filing (section
#                       8.1). Not a representational gap -- no IR change helps --
#                       and not a corpus defect, since nothing is wrong with the
#                       text. v0.60 (F18) corrects the gloss this line used to
#                       carry, "does not exist to ANY party": the redaction
#                       removes the value from the FILING, and what the pipeline
#                       reads is the filing. That distinction is the whole
#                       ruling, because the redaction removes the VALUE and
#                       leaves the CONSTRUCTION standing -- measured on E03-005,
#                       where the model quotes "At least ** before the ** of each
#                       Calendar Quarter ..." on 3 of 3 runs and the repaired
#                       narrowing classifies as BEFORE "the ** of each Calendar
#                       Quarter". So gold's `null` is not a faithful record of an
#                       absent constraint; it discards a constraint the document
#                       plainly states. Hence a direction, below.
GAP_KIND = {
    "exception_unsupported": "REPRESENTATIONAL",
    "unless_unsupported": "REPRESENTATIONAL",
    "compound_action": "REPRESENTATIONAL",
    "mutual_obligation": "REPRESENTATIONAL",
    "action_not_in_taxonomy": "REPRESENTATIONAL",
    # v0.61 (F19): no v1 temporal form carries a DURATION and a DIRECTION
    # together, so a lead-time deadline ("at least 30 days before X") has no
    # form at all. REPRESENTATIONAL rather than REACHABILITY on section 8.6.1's
    # own test: this is not a surface pattern rejecting input the IR could hold
    # -- the IR cannot hold it. Verified mechanically over all five forms, not
    # read off the regexes (see GOLD_SET_GUIDELINE.md section 8.11).
    "lead_time_unrepresentable": "REPRESENTATIONAL",
    "within_preposition": "REACHABILITY",
    "relative_trigger_preposition": "REACHABILITY",
    "corpus_artifact_in_span": "CORPUS_DEFECT",
    "shared_subject_split": "ANNOTATION_CONVENTION",
    "redacted_value": "WITHHELD_VALUE",
}

UNCLASSIFIED_KIND = "UNCLASSIFIED"

# --- axis 2: direction, for the kinds where GOLD DEPARTS FROM THE DOCUMENT --
#
# Direction of the IR's departure from the contract, NOT severity. OVERSTATING
# claims more than the document does (a monitor flags a breach the contract
# exempts); INCOMPLETENESS claims less (a monitor misses a real breach).
#
# A direction-bearing tag absent from this map is UNCLASSIFIED and must force a
# decision. A tag of a kind NOT in DIRECTION_BEARING_KINDS has no entry here BY
# DESIGN, and that is the substance of F10's resolution: for those kinds gold is
# faithful, so nothing departs from the contract and there is no direction to
# assign. Their former UNCLASSIFIED status was never a missing decision -- it was
# the wrong question.
DIRECTION_BEARING_KINDS = frozenset({"REPRESENTATIONAL", "WITHHELD_VALUE"})
GAP_DIRECTION = {
    "exception_unsupported": "OVERSTATING",
    "unless_unsupported": "OVERSTATING",
    "compound_action": "INCOMPLETENESS",
    "mutual_obligation": "INCOMPLETENESS",
    # v0.48 (F10, scoped): INCOMPLETENESS on the identical ground as
    # compound_action -- section 8.8 puts the NEAREST taxonomy verb in `action`
    # and the real verb is lost, so the IR claims less than the document says.
    "action_not_in_taxonomy": "INCOMPLETENESS",
    # v0.61 (F19, RULED): INCOMPLETENESS, and reached INDEPENDENTLY rather than
    # inherited from E03-01's own annotator note. The IR drops the lead-time
    # DURATION and keeps at most the bare direction (the repaired narrowing on
    # E03-005 runs 2-3 classifies as BEFORE "the ** of each Calendar Quarter"),
    # so a monitor built on it never checks the advance-notice period and
    # misses a real breach -- the IR claims LESS than the document. The
    # OVERSTATING alternative was considered and rejected on the semantics: the
    # nearest composable v1 approximation, WITHIN 30d OF X, denotes X-30d <= t
    # < X, which is the COMPLEMENT of "at least 30 days before X" (t <= X-30d)
    # -- so it would be a misstatement rather than an overstatement, and v1
    # cannot build it anyway (no form pairs duration with direction).
    "lead_time_unrepresentable": "INCOMPLETENESS",
    # v0.60 (F18, RULED): INCOMPLETENESS. Section 8.1 sets the affected field to
    # `null` for a clause the document states IS constrained, so the IR claims
    # LESS than the document -- a monitor built on E03-01 never checks the
    # forecast lead time at all and misses a real breach. Section 8.1 concedes
    # the hazard in its own words ("that conflates 'the contract states no
    # deadline' with 'a deadline exists and was withheld'") and answers it with
    # `missing_fields` + `redacted_phrase`, "the channel that keeps the
    # withheld-versus-absent distinction recoverable". THAT CHANNEL IS INVISIBLE
    # AT THE POINT OF CERTIFICATION: section 5 excludes `missing_fields` from the
    # predicate and `redacted_phrase` is non-scored. So what a FULLY_CORRECT
    # verdict would certify is the bare `null`, and the bare `null` misstates the
    # document. Recoverability from the ITEM is not recoverability from the
    # PREDICATE, and section 9.1 ground 2 reads the predicate.
    "redacted_value": "INCOMPLETENESS",
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
#   WITHHELD_VALUE    RULED EXCLUDED v0.60 (F18), no longer held. Ground 2 DOES
#                     bite, on the direction assigned above: gold's `null`
#                     discards a constraint the document states, and section 5
#                     cannot see the channel section 8.1 makes it recoverable
#                     through. A SECOND, independent ground is recorded because
#                     the two fail differently -- the item is not winnable in
#                     practice: across E03-005's 3 runs the model quotes the
#                     redacted timing phrase every time, and on the 2 runs that
#                     survive compile the repaired narrowing classifies, so
#                     clause 6 fails and drags clause 8 with it through an
#                     unresolvable trigger. STATED PRECISELY RATHER THAN
#                     OVERCLAIMED: this is 3-of-3 MEASURED model behaviour, not
#                     REACHABILITY's grammatical guarantee, and it is the weaker
#                     of the two grounds. Ground 2 alone is sufficient.
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
    if kind_of(tag) not in DIRECTION_BEARING_KINDS:
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
