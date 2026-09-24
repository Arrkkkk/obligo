"""Section 8.13 (v0.65): `within_parenthetical` is minted, kind REACHABILITY.

Three things could go wrong silently here and each is planted rather than
assumed away:

1. The tag lands in ONE vocabulary copy. That is v0.61's own trap -- adding a
   tag to `gap_kinds.GAP_KIND` alone left `annotator_agreement.SECTION_8_TAGS`
   stale and silently marked its item NON_CONFORMING in a DIFFERENT instrument.
2. The tag acquires a DIRECTION. REACHABILITY means gold is faithful, so there
   is nothing to assign; a plausible-looking lookup would be wrong in the same
   way F10's five tags were wrong.
3. The tag ADMITS its item to section 9.1's in-force denominator. REACHABILITY
   excludes on the third ground (a structurally guaranteed compile failure), so
   an admitting predicate would seat an unwinnable item in this phase's headline
   figure.

THE CALENDAR-DAYS GAP IS DELIBERATELY NOT A TAG, and that is pinned too: a test
asserts it stays out of both vocabularies, so minting it later is a visible
decision rather than a quiet one.
"""

from __future__ import annotations

import json
import re

import pytest

from evals.harness.annotator_agreement import SECTION_8_TAGS
from evals.harness.gap_kinds import (
    DIRECTION_BEARING_KINDS,
    DIRECTION_DEFERRED,
    GAP_DIRECTION,
    GAP_KIND,
    UNCLASSIFIED_KIND,
    direction_of,
    excluding_tags,
    in_force_scope,
    kind_of,
)
from evals.harness.run_scoring import GOLDENS_DIR, load_gold_items

from obligo_brain.compiler.ir_compile import _UNIT_ALTERNATION, _WITHIN_RE, _classify_temporal


@pytest.fixture(scope="module")
def gold_items():
    items = load_gold_items(GOLDENS_DIR)
    # Standing Principle 7: a short or empty load would make every population
    # assertion below pass vacuously. A FLOOR, not an equality -- pinning an
    # exact count would make each future batch look like a defect.
    assert len(items) >= 48, f"expected at least the 48 locked items, loaded {len(items)}"
    return items


# --- the tag itself ---------------------------------------------------------

def test_the_tag_is_minted_in_BOTH_vocabulary_copies():
    """v0.61's trap, pinned for this tag specifically rather than left to the
    general subset invariant: that invariant would catch a GAP_KIND-only
    addition, but only once some item used it."""
    assert GAP_KIND.get("within_parenthetical") == "REACHABILITY"
    assert "within_parenthetical" in SECTION_8_TAGS


def test_the_tag_carries_NO_direction_because_gold_is_faithful():
    """REACHABILITY is not in DIRECTION_BEARING_KINDS: gold annotates the
    WITHIN form exactly as the document writes it, so nothing departs from the
    contract and there is no direction to assign. Distinct from UNCLASSIFIED,
    which means a decision is owed -- F10's own distinction, one level down."""
    assert "REACHABILITY" not in DIRECTION_BEARING_KINDS
    assert "within_parenthetical" not in GAP_DIRECTION
    assert "within_parenthetical" not in DIRECTION_DEFERRED
    assert direction_of("within_parenthetical") is None
    assert direction_of("within_parenthetical") != UNCLASSIFIED_KIND


def test_it_gets_the_IDENTICAL_treatment_to_its_sibling_within_preposition():
    """Both are `_WITHIN_RE` reachability defects; the ruling is that they are
    two gaps with two tags, not one gap. What must NOT differ is how the
    denominator and the direction axis treat them."""
    assert kind_of("within_parenthetical") == kind_of("within_preposition")
    assert direction_of("within_parenthetical") == direction_of("within_preposition")


def test_it_EXCLUDES_from_the_in_force_denominator():
    """§9.1's third ground: a structurally guaranteed compile failure, so
    admitting it would seat an unwinnable item in the headline figure."""
    assert in_force_scope(["within_parenthetical"]) is False
    assert excluding_tags(["within_parenthetical"]) == ["within_parenthetical"]


def test_membership_is_by_KIND_and_by_ANY_excluding_tag_not_by_count():
    """§9's v0.22 rule is unchanged, only the predicate it applies. One
    excluding tag is enough, and a CORPUS_DEFECT/ANNOTATION_CONVENTION tag
    alongside it changes nothing."""
    assert in_force_scope([]) is True
    assert in_force_scope(["corpus_artifact_in_span"]) is True
    assert in_force_scope(["within_parenthetical", "corpus_artifact_in_span"]) is False


# --- the mechanism, by execution rather than read off the regex -------------

def test_the_IR_HAS_the_form_which_is_what_makes_it_REACHABILITY():
    """§8.6.1's test, applied by execution. If the repaired phrase did not
    classify, this would be REPRESENTATIONAL and the whole ruling changes."""
    assert _classify_temporal("within 3 days of receipt of the billing data") is not None
    assert _classify_temporal("within 30 days of the Effective Date") is not None


def test_the_parenthetical_numeral_alone_is_sufficient_to_reject():
    """Isolated: unit accepted, preposition accepted, only the numeral wrong."""
    assert _WITHIN_RE.match("within 30 days of X")
    assert not _WITHIN_RE.match("within thirty (30) days of X")
    assert _classify_temporal("within thirty (30) days of X") is None


def test_E02_006s_phrase_trips_the_numeral_and_the_UNIT_independently():
    """Two gaps, and each alone rejects. This is the measurement the ruling
    rests on, so it is pinned rather than described."""
    assert _classify_temporal("within three (3) calendar days of receipt") is None
    # numeral repaired, unit still wrong
    assert _classify_temporal("within 3 calendar days of receipt") is None
    # unit repaired, numeral still wrong
    assert _classify_temporal("within three (3) days of receipt") is None
    # both repaired
    assert _classify_temporal("within 3 days of receipt") is not None


def test_the_unit_alternation_has_no_entry_for_calendar_days():
    """The second gap's mechanism, stated where a reader will find it: it is a
    different sub-pattern of the same regex, not the numeral one."""
    assert not re.match(f"^(?:{_UNIT_ALTERNATION})$", "calendar days", re.IGNORECASE)
    assert re.match(f"^(?:{_UNIT_ALTERNATION})$", "days", re.IGNORECASE)


def test_the_calendar_days_gap_is_NOT_a_tag_and_that_is_deliberate():
    """§8.13's forcing function. Zero independent instances in 179 real WITHIN
    deadlines; minting a tag that can never fire alone buys nothing. Pinned so
    that minting one later is a visible decision."""
    for vocabulary in (GAP_KIND, SECTION_8_TAGS):
        assert not any("calendar" in t or "unit" in t for t in vocabulary), (
            "a unit-modifier tag was minted without §8.13's forcing function "
            "being met -- see the F23 queue row"
        )


# --- the committed gold set -------------------------------------------------

def test_E02_02_is_the_sets_first_and_only_carrier_of_the_tag(gold_items):
    carriers = sorted(i["item_id"] for i in gold_items if "within_parenthetical" in i["known_gaps"])
    assert carriers == ["E02-02"]


def test_C11_03_is_NOT_restamped_and_keeps_within_preposition_alone(gold_items):
    """§8.6's "two gaps, one tag" practice is reconciled with §11 in prose, not
    changed. C11-03 trips BOTH gaps and keeps the single tag it was locked
    with, so this ruling restamps no item."""
    c11_03 = next(i for i in gold_items if i["item_id"] == "C11-03")
    assert c11_03["known_gaps"] == ["within_preposition"]
    assert c11_03["guideline_version"] == "v0.55"
    # and the premise: its phrase really does trip the numeral gap too
    assert _classify_temporal("within twelve (12) months of the date") is None


def test_no_locked_item_other_than_E02_02_gains_or_loses_a_tag(gold_items):
    """The §10 re-check, asserted over data rather than argued. Exposure across
    the set is ONE item, and it is the new one."""
    tagged = {i["item_id"]: sorted(i["known_gaps"]) for i in gold_items if i["known_gaps"]}
    assert tagged["C17-02"] == ["within_preposition"]
    assert tagged["C11-03"] == ["within_preposition"]
    # C11-02's span carries a parenthetical WITHIN inside its `if`-clause, but
    # its own temporal is null, so no gap tag is owed. The screen over spans
    # over-fires here on purpose; this pins the adjudicated answer.
    c11_02 = next(i for i in gold_items if i["item_id"] == "C11-02")
    assert c11_02["known_gaps"] == []
    assert c11_02["temporal"] is None
    assert "within the twelve (12) month period" in c11_02["span_text"]


def test_E08_03_remains_the_sets_only_COMPILABLE_within(gold_items):
    """A known answer from E08-03's own notes, re-derived here rather than
    trusted: it must NOT acquire this tag."""
    e08_03 = next(i for i in gold_items if i["item_id"] == "E08-03")
    assert "within_parenthetical" not in e08_03["known_gaps"]
    assert _classify_temporal("within 30 days of KIRKLAND'S's receipt of NFI's invoice") is not None


def test_E02_02s_temporal_canonicalises_IDENTICALLY_through_both_functions(gold_items):
    """§8.6.1's own confirmation step, and the reason `unit` is the AST's "d"
    rather than the document's "calendar days": clause 6 compares canonical
    forms, so a "calendar days" stamp would fail against every correct
    prediction."""
    from evals.harness import score
    from obligo_brain.compiler.parser import parse

    e02_02 = next(i for i in gold_items if i["item_id"] == "E02-02")
    dsl = (
        'MUST "CBay" PROVIDE "Client Facility" invoice "an invoice" '
        'WITHIN 3d OF "receipt of the billing data from MedQuist" '
        "00000000-0000-0000-0000-000000000000 0 10 1.0"
    )
    parsed = score._canonical_temporal(parse(dsl).temporal)
    gold = score._canonical_gold_temporal(e02_02["temporal"])
    assert gold == parsed
    assert gold["unit"] == "d"
