"""§10.3 (v0.66): F31's consolidation pass -- the stratum-artifact verdict and
the F25/F28/F29 class sizes.

Four things could go wrong silently here, and each is planted or pinned rather
than assumed away:

1. **The verdict flips because the attribution table drifts.** The whole point
   of §10.3.1 is that `NOT MEASURABLE` holds under BOTH defensible readings, so
   a test asserts both counts AND that both exceed F31(e)'s threshold -- not
   just the headline.
2. **The attribution table stops covering the queue.** A row added to §10.1
   without a classification would silently shrink the denominator, so coverage
   is an equality check against the guideline's own parsed row set.
3. **F31's own answers stop being honoured.** F31(e) names three rows
   unattributable and F31(3) counts batch 5's at seven; both are REVIEWER-SUPPLIED
   known answers and both are asserted, so a re-classification that contradicts
   the reviewer fails loudly.
4. **F27's suppression of F28's founding instance quietly goes away.** If
   `split_sentences()` is ever fixed, §10.3.4's lower-bound caveat stops being
   true -- so the interaction is pinned in BOTH directions and a fix forces that
   section to be re-read instead of silently changing a number.

The corpus-backed group is `skipif`-gated: `.corpus/` is git-ignored and absent
on the runner, so **CI verifies this ruling's effect on the committed gold set
and its arithmetic, NOT its 1,547-segment corpus measurements**. That is said
here rather than left to be inferred from a skip count -- §8.8.4's own close-out
note made the same distinction.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[4]
CONSOLIDATION = ROOT / "apps/brain/evals/goldens/holdout/consolidation"
GUIDELINE = ROOT / "docs/eval/GOLD_SET_GUIDELINE.md"
CORPUS = ROOT / ".corpus"

corpus_required = pytest.mark.skipif(
    not (CORPUS / "cuad").is_dir(),
    reason=(
        "needs the git-ignored .corpus/ working copy (fetch with "
        "`python -m evals.corpus fetch`). §10.3's corpus measurements are therefore "
        "NOT re-verified by CI -- see this module's docstring."
    ),
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, CONSOLIDATION / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def attribution():
    return _load("attribution")


# --- (1) the arithmetic that does not need the corpus ------------------------

def test_the_queue_holds_exactly_32_live_rows_not_f31s_34(attribution):
    """F31(3) says "34". §10.3.3 corrects it to 32 by COUNTING, and the count is
    pinned so the next session does not inherit a third figure."""
    rows = attribution.live_queue_rows()
    assert len(rows) == 33, (
        "§10.3.3 counts 32 live rows F1-F32 plus F33, opened at v0.66. "
        f"Got {len(rows)}: {rows}"
    )
    nums = sorted(int(r[1:]) for r in rows)
    assert nums == list(range(1, 34)), f"the queue has a gap or a duplicate: {nums}"


def test_the_struck_through_superseded_f9_duplicate_is_not_counted():
    """The queue carries one `~~**F9 (original entry...)**~~` row. Counting it
    would make the live total 34 by accident -- which is how an inherited
    figure becomes defensible-looking."""
    text = GUIDELINE.read_text()
    assert "~~**F9 (original entry, left as written)**~~" in text, (
        "the struck-through F9 duplicate is gone; §10.3.3's count of physical "
        "rows needs re-deriving"
    )


def test_attribution_table_covers_exactly_the_live_queue(attribution):
    rows = attribution.live_queue_rows()
    measured = [r for r in rows if r not in attribution.OPENED_BY_THIS_PASS]
    assert set(attribution.TABLE) == set(measured)
    assert attribution.OPENED_BY_THIS_PASS == {"F33"}


def test_f31s_own_three_named_unattributable_rows_are_unattributable(attribution):
    """F31(e) is a REVIEWER-SUPPLIED known answer, not this pass's conclusion."""
    items, strata = attribution.load_items(), attribution.doc_strata()
    for row in sorted(attribution.F31_NAMED_UNATTRIBUTABLE):
        a = attribution.TABLE[row]
        _, locus_stratum = attribution._stratum_of_locus(a.locus, items, strata)
        assert locus_stratum is None and a.opener is None, (
            f"F31(e) names {row} unattributable; the table resolves it"
        )


def test_batch_5_opened_exactly_seven_rows_f24_through_f30(attribution):
    """F31(3) says 7 while F31(d) says "F24-F31", which is 8 and includes a
    reviewer sequencing decision no segment opened. §10.3.3 rules that (3) is
    correct; this pins which seven."""
    assert attribution.F31_BATCH5_OPENED == {
        "F24", "F25", "F26", "F27", "F28", "F29", "F30"
    }
    assert "F31" not in attribution.F31_BATCH5_OPENED
    assert "F32" not in attribution.F31_BATCH5_OPENED


def test_the_two_attribution_rules_are_not_nested(attribution):
    """If STRICT were simply a subset of LOCUS, the "both readings agree" claim
    would be one reading stated twice. F13 is the witness: attributable under
    STRICT, unattributable under LOCUS."""
    items, strata = attribution.load_items(), attribution.doc_strata()
    f13 = attribution.TABLE["F13"]
    _, locus = attribution._stratum_of_locus(f13.locus, items, strata)
    assert locus is None and f13.opener is not None, (
        "F13 no longer witnesses that the two rules are not nested; §10.3.1's "
        "independence claim needs re-deriving"
    )


# --- (2) the verdict, which needs the corpus only for its gates -------------

@corpus_required
def test_both_readings_exceed_f31s_pre_fixed_threshold(attribution):
    """THE VERDICT. F31(e) fixed `> 10 -> NOT MEASURABLE` before any row was
    looked at; §10.3.1 reports 14 and 22. Both are asserted, because the claim
    is that the verdict does not depend on which reading is taken."""
    state = attribution.run()
    res, rows = state["res"], state["rows"]
    counts = {
        rule: len([r for r in rows if res[r][rule] is None])
        for rule in ("LOCUS", "STRICT")
    }
    assert counts["LOCUS"] == 14, counts
    assert counts["STRICT"] == 22, counts
    assert all(n > 10 for n in counts.values()), (
        f"§10.3.1's verdict no longer holds under both readings: {counts}"
    )


@corpus_required
def test_the_two_readings_disagree_on_the_sign_of_the_deviation(attribution):
    """§10.3.1's SECOND and stronger ground. Under LOCUS the batches-1-4 hard
    share is above H0; under STRICT it is below. A measurement whose sign flips
    with a defensible re-reading is not measuring what it was built to."""
    state = attribution.run()
    res, rows = state["res"], state["rows"]
    shares = {}
    for rule in ("LOCUS", "STRICT"):
        keep = [
            r for r in rows
            if res[r][rule] and res[r]["batches"]
            and set(res[r]["batches"]) <= set(attribution.BATCH_14)
        ]
        hard = len([r for r in keep if res[r][rule] == "hard"])
        shares[rule] = hard / len(keep)
    assert shares["LOCUS"] > attribution.F31_H0_14, shares
    assert shares["STRICT"] < attribution.F31_H0_14, shares
    for rule, share in shares.items():
        assert abs(share - attribution.F31_H0_14) > attribution.BAND_SUGGESTIVE, (
            f"{rule} now falls inside F31(c)'s band: {share}"
        )


@corpus_required
def test_f31s_denominators_and_h0_shares_reproduce_exactly(attribution):
    """F31(b)/(c)'s figures are the GATE, not an output -- so if they ever stop
    reproducing, the pass is measuring a different population than F31 designed."""
    state = attribution.run()
    assert state["denoms"]["batches 1-4"] == attribution.F31_DENOM_14 == (33, 40)
    assert state["denoms"]["all five"] == attribution.F31_DENOM_ALL == (42, 40)


# --- (3) F32's composite-id defect, two-sided -------------------------------

def test_f32s_five_composite_segment_ids_are_still_exactly_five(attribution):
    """F32 records a hand-maintained field-convention drift. If a sixth appears,
    or one is normalised away, F32's "five entries affected" stops being true and
    every consumer joining `segment_id` is affected differently."""
    composites = [
        e["segment_id"]
        for b in attribution.BATCHES
        for e in json.loads(
            (attribution.GOLDENS / b / "exclusions.json").read_text()
        )
        if "#" in e["segment_id"]
    ]
    assert sorted(composites) == [
        "C14-044#S1", "E03-005#discuss", "E03-005#itemize",
        "E07-010#sentence2", "E07-010#sentence3",
    ], composites


# --- (4) the class sizes, and F27's suppression of F28's own instance -------

@corpus_required
def test_f25_f28_f29_sizes_reproduce():
    cs = _load("class_sizes")
    sents, segs = cs._sentences(with_segments=True)
    f25 = cs.size_f25(sents, segs)
    assert cs._tally(f25["adjudicated"]) == (16, 16, 11), cs._tally(f25["adjudicated"])
    f28 = cs.size_f28(sents, segs)
    assert cs._tally(f28["seg_adjudicated"])[1:] == (5, 4), cs._tally(f28["seg_adjudicated"])
    f29 = cs.size_f29(sents, segs, _load("attribution").load_items())
    assert cs._tally(f29["hits"]) == (71, 66, 16), cs._tally(f29["hits"])


@corpus_required
def test_f27_still_suppresses_f28s_founding_instance_from_a_sentence_sweep():
    """§10.3.4's lower-bound caveat depends on this. If `split_sentences()` is
    fixed, this test fails and that section must be re-read -- which is the
    point: the caveat must not outlive the defect that justifies it."""
    cs = _load("class_sizes")
    sents, segs = cs._sentences(with_segments=True)
    sentence_hits = {h[0] for h in sents if cs._is_performance_disjunction(h[2])[0]}
    segment_hits = {h[0] for h in segs if cs._is_performance_disjunction(h[2])[0]}
    assert "C04-144" not in sentence_hits, (
        "C04-144 is now reachable at sentence granularity -- F27's defect may be "
        "fixed, and §10.3.4's lower-bound caveat needs re-deriving"
    )
    assert "C04-144" in segment_hits


@corpus_required
def test_no_f28_reading_override_has_gone_inert():
    """An override that matches nothing is silently protecting nothing -- the
    v0.62 `PRE_RESTAMP` lesson. `size_f28` asserts this internally; this makes
    the guarantee visible as a test rather than only as a side effect."""
    cs = _load("class_sizes")
    sents, segs = cs._sentences(with_segments=True)
    flagged = {h[0] for h in sents if cs._is_performance_disjunction(h[2])[0]}
    flagged |= {h[0] for h in segs if cs._is_performance_disjunction(h[2])[0]}
    inert = sorted(set(cs.F28_READING_OVERRIDES) - flagged)
    assert not inert, f"overrides matching nothing: {inert}"


# --- (5) the two findings about already-answered questions -------------------

def test_f29s_forcing_function_is_met_by_four_locked_items():
    """§10.3.4's against-interest finding. F29 asked for a LEGIBLE instance;
    four locked items carry one in their own span, and `C11-03` predates the row.
    Reads the committed gold set only, so it runs in CI."""
    cs_src = (CONSOLIDATION / "class_sizes.py").read_text()
    pattern = re.search(r"F29_RE = re\.compile\(\s*\n(.*?)\n\)", cs_src, re.S)
    assert pattern, "F29_RE moved; this test's regex extraction needs updating"
    efforts = re.compile(
        r"\b((?:best|reasonable|commercially reasonable|reasonable commercial|diligent|"
        r"good faith|commercial|all reasonable|every reasonable|its reasonable)\s+"
        r"(?:efforts|endeavors|endeavours))\b",
        re.IGNORECASE,
    )
    items = _load("attribution").load_items()
    in_span = sorted(
        i["item_id"] for i in items.values() if efforts.search(i["span_text"])
    )
    assert in_span == ["C11-03", "C14-04", "C17-01", "C17-02"], in_span
    assert items["C11-03"]["guideline_version"] == "v0.55", (
        "C11-03's stamp is what makes the 'already met when the row was filed' "
        "claim checkable"
    )
    # None of the four is tagged for it -- which is what leaves F29 open.
    for iid in in_span:
        assert "efforts_standard_unrepresentable" not in items[iid]["known_gaps"]


def test_c04_06_falsifies_f33s_first_draft_and_annotates_section_8_9s_reading():
    """F33's draft claimed no locked item carries an `until` temporal. `C04-06`
    does, annotates §8.9's `before` reading, and already carries §8.9's tag --
    which is what reduced F33 from a new class to a fidelity question. Committed
    gold only, so it runs in CI."""
    items = _load("attribution").load_items()
    c04_06 = items["C04-06"]
    assert "until" in c04_06["span_text"].lower()
    assert c04_06["temporal"]["form"] == "RELATIVE_TO_TRIGGER"
    assert c04_06["temporal"]["direction"] == "before"
    assert "relative_trigger_preposition" in c04_06["known_gaps"]
    # And the artifact facts F33's draft got wrong, pinned so they stay right.
    assert c04_06["segment_id"] == "C04-117"
    assert c04_06["batch"] == "batch02"


def test_no_new_tag_was_minted_by_this_pass():
    """§10.3 sizes three classes and mints none. A tag appearing in either
    vocabulary without a §8.10 kind ruling is exactly what F10's forcing
    function exists to prevent."""
    from evals.harness.annotator_agreement import SECTION_8_TAGS
    from evals.harness.gap_kinds import GAP_KIND

    for minted in (
        "event_bounded_interval", "disjunctive_obligation",
        "efforts_standard_unrepresentable", "end_only_bound",
    ):
        assert minted not in GAP_KIND, minted
        assert minted not in SECTION_8_TAGS, minted


# --- (6) the queue parser's scoping, which was right only by document order --

def test_the_queue_parser_is_scoped_and_not_merely_order_lucky(attribution):
    """§10.3.4's own size table carries rows labelled `**F25**`/`**F28**`/`**F29**`,
    and the 5-column audit sub-table repeats four more. An unscoped scan that
    deduplicates by first occurrence returns the right answer ONLY because §10.1
    precedes both. This asserts the scoping is doing real work: the labels occur
    more than once in the document, and the parser still returns each once."""
    text = GUIDELINE.read_text()
    rows = attribution.live_queue_rows()
    assert len(rows) == len(set(rows)), f"parser returned duplicates: {rows}"
    for label in ("F25", "F28", "F29", "F3", "F7"):
        assert text.count(f"| **{label}** | ") > 1, (
            f"{label} no longer appears outside §10.1's table, so this test has "
            "gone vacuous and the scoping is no longer being exercised"
        )
        assert rows.count(label) == 1


def test_the_queue_parser_refuses_a_duplicate_row_instead_of_deduplicating(attribution):
    """Silently deduplicating is how an unscoped parse hid the problem above. A
    genuine duplicate in §10.1 is a document defect and must fail loudly."""
    import re as _re

    original = attribution.GUIDELINE
    text = original.read_text()
    marker = "| **F32** | "
    i = text.index(marker)
    end = text.index("\n", i) + 1
    planted = text[:end] + text[i:end] + text[end:]  # F32 twice, in §10.1
    tmp = original.parent / "_planted_duplicate_guideline.md"
    try:
        tmp.write_text(planted)
        attribution.GUIDELINE = tmp
        with pytest.raises(RuntimeError, match="duplicate rows"):
            attribution.live_queue_rows()
    finally:
        attribution.GUIDELINE = original
        tmp.unlink(missing_ok=True)
