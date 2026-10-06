"""Pool-wide sizing for §10.1 F25, F28 and F29 -- SEPARATELY, as F31(2) requires.

F25/F28/F29 each state, in their own words, that they must not be folded
together: F25 is a temporal FORM gap in `DuringTemporal`'s `{start: DateRef,
end: DateRef}` shape, F28 is an action SLOT gap in `Obligation.action`, F29 is
a missing FIELD TYPE with no slot at all. Three mechanisms, three sweeps,
three numbers. This file reports them as three sections and never sums them.

Standing Principle 7 throughout: each detector is gated on named known answers
-- the real locked segments each row cites -- BEFORE any count is read off it,
and the pool rebuild to 1,547 is its own gate. `_sentences()` raises below a
floor, because a known-answer gate over an empty corpus passes.

A FINDING ABOUT THE METHOD, STATED UP FRONT BECAUSE IT CONSTRAINS F25's SWEEP:
`_DURING_RE` requires `during YYYY-MM-DD..YYYY-MM-DD`, so NO natural-language
`during` phrase matches it -- date-bounded or event-bounded alike. Verified by
execution below. So `_classify_temporal() is None` CANNOT discriminate F25's
representational gap from `_DURING_RE`'s reachability pattern, and the
discrimination has to come from the AST's shape, which is what F25's row
actually did. The sweep is therefore a MARKER census with a stated hand pass,
not a classifier-output census.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "apps/brain/src"))

from obligo_brain.compiler.ast import ACTIONS  # noqa: E402
from obligo_brain.compiler.ir_compile import (  # noqa: E402
    _DURING_RE,
    _classify_temporal,
)


def _corpus():
    spec = importlib.util.spec_from_file_location(
        "corpus", ROOT / "apps/brain/evals/corpus.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sentences(with_segments: bool = False):
    """Two granularities, both returned, because they measure different things.

    SENTENCE granularity is the natural unit for a construction that lives
    inside one sentence -- and it SYSTEMATICALLY UNDER-COUNTS, because §10.1
    F27's `split_sentences()` defect fragments 32 of the 35 redaction-bearing
    pool segments, ALL in `C04`. SEGMENT granularity recovers those and can in
    exchange pair limbs across a sentence boundary. Neither is "the" number;
    both are reported.
    """
    c = _corpus()
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = c.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)}, expected 1547"
    sents = [
        (s["segment_id"], s["doc_id"], snt)
        for s in pool
        for snt in c.split_sentences(s["text"])
        if c._MODAL_RE.search(snt)
    ]
    segs = [(s["segment_id"], s["doc_id"], s["text"])
            for s in pool if c._MODAL_RE.search(s["text"])]
    if len(sents) < 3000 or len(segs) < 800:
        raise RuntimeError(f"_sentences() loaded {len(sents)}/{len(segs)}; floors not met")
    print(f"pool-rebuild gate: {len(pool)} segments, {len(sents)} modal-bearing sentences, "
          f"{len(segs)} modal-bearing segments  PASS")
    return (sents, segs) if with_segments else sents


def _tally(hits):
    return len(hits), len({h[0] for h in hits}), len({h[1] for h in hits})


def _fmt(label, hits, total_sents):
    n, segs, docs = _tally(hits)
    return (f"  {label:46} {n:4} sentences  {segs:4} segments  {docs:2} documents"
            f"  ({n/total_sents:.1%} of modal sentences)")


# ===========================================================================
# F25 -- THE EVENT-BOUNDED INTERVAL (a temporal FORM gap)
# ===========================================================================
# An interval whose bound is an EVENT or STATE rather than a date. `until <X>`
# is deliberately NOT in this core set: an end-only bound is a DIFFERENT gap
# (no end-only slot) which happens to share the symptom, so it is reported
# separately rather than folded in -- F25's own "different mechanism" rule
# applied one level down.
F25_CORE = re.compile(
    r"(during the (?:continuance|continuation|pendency) of"
    r"|for the duration of"
    r"|for (?:so|as) long as"
    r"|during (?:any|the|such) period (?:in which|during which|that|when|of)"
    r"|at all times (?:while|during which))",
    re.IGNORECASE,
)
F25_ADJACENT_UNTIL = re.compile(r"\buntil\b", re.IGNORECASE)
# The five v1-classifying heads, used only to flag a sentence that carries a
# SECOND temporal element -- i.e. §8.12 composition territory, not F25.
V1_TEMPORAL_HEAD = re.compile(
    r"\b(within\s+\w+\s+(?:day|days|month|months|year|years|week|weeks|hour|hours|"
    r"business day|business days|calendar day|calendar days)"
    r"|every\s+\d|by\s+(?:\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},\s*\d{4})"
    r"|(?:before|after)\s+the\s+\w+)\b",
    re.IGNORECASE,
)


# A hand reading override, PUBLISHED rather than patched away (§8.8.4's
# discipline). `for the duration of the Warranty Period` names a DEFINED
# PERIOD, not an event or a state -- a date pair could hold it once its
# termini resolved -- so it is §8.12's `during the Term` family, not F25's.
F25_READING_OVERRIDES = {
    "C14-133": "`for the duration of the Warranty Period` bounds the interval by a "
               "DEFINED PERIOD, not an event or state; a resolved date pair could hold "
               "it, so this is §8.12's `during the Term` family rather than F25's",
}


def size_f25(sents, segs):
    print("\n" + "=" * 78)
    print("F25 -- EVENT-BOUNDED INTERVAL  (temporal FORM gap in DuringTemporal)")
    print("=" * 78)

    # --- GATE: the AST claim, and the method finding ------------------------
    assert not _DURING_RE.match("during the pendency of such challenge")
    assert not _DURING_RE.match("during the period from January 1, 2020 to December 31, 2020")
    assert _DURING_RE.match("during 2020-01-01..2020-12-31"), "DURING gate: ISO form must match"
    print("  method gate: `_DURING_RE` accepts ONLY `during <ISO>..<ISO>`; it rejects an")
    print("    event-bounded AND a date-bounded natural-language `during` alike, so")
    print("    classifier output cannot discriminate the two.  PASS")
    for phrase in ("during the pendency of such challenge",
                   "for the duration of such force majeure",
                   "until Bellicum has secured an alternate source of supply"):
        assert _classify_temporal(phrase) is None, phrase
    assert _classify_temporal("within 30 days of the Effective Date") is not None
    print("  classifier gate: 3 event-bounded phrases -> None; a WITHIN deadline -> a form.  PASS")

    core = [h for h in sents if F25_CORE.search(h[2])]
    # --- GATE: two-sided, on the row's own named instance -------------------
    assert any(s == "C10-025" for s, _, _ in core), "F25 GATE: C10-025 not flagged"
    assert not any(F25_CORE.search(t) for s, _, t in sents if s == "C04-072"), \
        "F25 GATE: C04-072 (a WITHIN-deadline segment) was flagged"
    assert not any(s == "C04-051" for s, _, _ in core), \
        "F25 GATE: C04-051's `until` clause leaked into the CORE set"
    assert any(s == "C04-051" for s, _, t in sents if F25_ADJACENT_UNTIL.search(t)), \
        "F25 GATE: C04-051's `until` clause is not in the adjacent set"
    print("  known-answer gate: C10-025 IN core; C04-072 OUT; C04-051 OUT of core and IN")
    print("    the adjacent `until` set -- so core and adjacent discriminate.  PASS")

    n = len(sents)
    print()
    print(_fmt("CORE: event/state-bounded interval", core, n))
    single = [h for h in core if not V1_TEMPORAL_HEAD.search(h[2])]
    comp = [h for h in core if V1_TEMPORAL_HEAD.search(h[2])]
    print(_fmt("  of which SINGLE-element (F25 proper)", single, n))
    print(_fmt("  of which carry a 2nd v1 head (-> §8.12)", comp, n))
    print("\n  core marker breakdown:")
    for marker, cnt in collections.Counter(
        F25_CORE.search(h[2]).group(1).lower() for h in core
    ).most_common():
        print(f"    {marker:52} {cnt}")
    print("\n  core instances:")
    for sid, did, s in sorted(core):
        m = F25_CORE.search(s)
        print(f"    {sid}: ...{s[max(0, m.start()-45):m.end()+55].strip()}...")

    until = [h for h in sents if F25_ADJACENT_UNTIL.search(h[2])]
    print()
    print(_fmt("ADJACENT, REPORTED SEPARATELY: `until <terminus>`", until, n))
    until_segs = [h for h in segs if F25_ADJACENT_UNTIL.search(h[2])]
    print(_fmt("  same sweep at SEGMENT granularity", until_segs, len(segs)))
    print("    ALREADY RULED BY §8.9, NOT A SIBLING OF THIS SECTION'S CLASS -- and this")
    print("    script's first draft had it the other way round, as an end-only")
    print("    `DuringTemporal` gap. The governing slot is `RelativeToTriggerTemporal`:")
    print("    §8.9 annotates `until <X>` as RELATIVE_TO_TRIGGER(before, X) with")
    print("    `relative_trigger_preposition`, so the IR CAN hold the form and the")
    print("    failure is REACHABILITY (`_RELATIVE_RE` wants a literal before/after),")
    print("    not expressiveness. Gated by execution just below.")
    print("    The SEGMENT figure independently reproduces §8.9's own v0.34 correction")
    print("    (72 segments, 4.7%) -- off by one, identical percentage.")
    print("    ITS EVENT/DATE SPLIT IS DELIBERATELY NOT MEASURED HERE: phrases like")
    print("    `until the expiration or earlier termination of X` are genuinely both,")
    print("    so any split would be one hand pass's opinion offered as a census.")
    # Two-sided gate on §8.9's ruling, and on the locked item that falsified the
    # draft's "no locked item carries one" claim.
    assert _classify_temporal("until the Parties have reached agreement on this matter") is None
    assert _classify_temporal("before the Parties have reached agreement on this matter") \
        is not None, "§8.9 gate: the `before` reading must classify"
    # Located by glob, NOT by a hardcoded batch: a first draft guessed batch05
    # and C04-06 lives in batch02, which is also how this section's wrong
    # cassette claim was found (§10.1's own rule -- re-derive an artifact
    # property at execution time, never trust it from the row).
    c04_06 = json.loads(
        next((ROOT / "apps/brain/evals/goldens").glob("batch0*/items/C04-06.json")).read_text())
    assert "until" in c04_06["span_text"].lower(), "§8.9 gate: C04-06's span lost its `until`"
    assert c04_06["temporal"]["form"] == "RELATIVE_TO_TRIGGER" and \
        c04_06["temporal"]["direction"] == "before", \
        "§8.9 gate: C04-06 no longer annotates the `before` reading"
    assert "relative_trigger_preposition" in c04_06["known_gaps"], \
        "§8.9 gate: C04-06 no longer carries §8.9's own tag"
    print("    §8.9 gate: `until X` -> None, `before X` -> a form, and LOCKED `C04-06`")
    print("      annotates RELATIVE_TO_TRIGGER(before, ...) over an `until` span and")
    print("      already carries §8.9's own `relative_trigger_preposition` tag.  PASS")

    adjudicated = [h for h in core if h[0] not in F25_READING_OVERRIDES]
    print(f"\n  HAND READING OVERRIDES, published not patched: "
          f"{len(F25_READING_OVERRIDES)} of {len(core)} = "
          f"{len(F25_READING_OVERRIDES)/len(core):.1%} detector error rate")
    for sid, why in F25_READING_OVERRIDES.items():
        assert any(h[0] == sid for h in core), f"override {sid} has gone INERT"
        print(f"    {sid}: {why}")
    print(_fmt("ADJUDICATED event/state-bounded interval", adjudicated, n))

    seg_core = [h for h in segs if F25_CORE.search(h[2])]
    print(_fmt("same sweep at SEGMENT granularity", seg_core, len(segs)))
    extras = sorted({h[0] for h in seg_core} - {h[0] for h in core})
    print(f"    segment-only extras: {extras} -- CHECKED, and they are NOT F27's")
    print("    splitter defect: both sit in clauses with no modal at all (`is excused`,")
    print("    `represents and warrants`), so the modal filter excludes them correctly.")
    print("    F27's interaction is specific to F28; see that section.")
    return {"core": core, "adjudicated": adjudicated, "single": single,
            "composition": comp, "until": until, "seg_core": seg_core}


# ===========================================================================
# F28 -- THE DISJUNCTIVE OBLIGATION (an action SLOT gap)
# ===========================================================================
# Three anchors, not one. The third exists because the first two MISS F28's own
# second instance: `C04-033` reads "the right to transfer ..., or to request",
# with no `either` and no `at its option` anywhere. The known-answer gate below
# is what surfaced that, and it is kept.
# Each anchor yields the text (or, for the third, the word) that LEADS each
# limb. The third's shape is different on purpose: there the verbs sit
# immediately after `to`, so the pattern captures them rather than capturing
# limb text for `_limb_head` to scan. A first draft used one uniform shape and
# the known-answer gate below FAILED on `C04-033`, because a single
# `...or to \w+` anchor CONSUMES the very `or` the limb split needs; that
# failure is why the per-anchor shape exists.
F28_ANCHORS = {
    "either_or": (re.compile(r"\beither\b(.{0,250}?)\bor\b(.{0,80})", re.IGNORECASE | re.S), False),
    "at_its_option": (re.compile(
        r"at its (?:sole )?(?:option|election|discretion)(.{0,250}?)\bor\b(.{0,80})",
        re.IGNORECASE | re.S), False),
    "to_V_or_to_V": (re.compile(r"\bto\s+(\w+)\b[^.;]{0,200}?\bor\s+to\s+(\w+)",
                                re.IGNORECASE), True),
}
# Base-form verbs that can head a performance limb. Seeded from the closed
# taxonomy and extended by hand with the contract verbs this corpus actually
# uses as limb heads; every rejected limb head is PRINTED, so a vocabulary
# miss is visible rather than a silent false negative.
LIMB_VERBS = {a.lower() for a in ACTIONS} | {
    "accept", "acquire", "add", "adjust", "amend", "arrange", "assume", "buy",
    "cancel", "cause", "charge", "collect", "commence", "complete", "conduct",
    "continue", "correct", "credit", "defend", "defer", "delegate", "destroy",
    "disapprove", "discontinue", "dispose", "elect", "engage", "exercise",
    "extend", "furnish", "give", "hold", "increase", "initiate", "install",
    "invoice", "issue", "keep", "make", "modify", "obtain", "offer", "order",
    "perform", "permit", "prepare", "purchase", "reduce", "refund", "reject",
    "release", "remove", "renew", "repay", "replace", "request", "require",
    "reschedule", "resume", "revise", "secure", "sell", "send", "ship",
    "submit", "supply", "suspend", "take", "treat", "withdraw",
}
# Tokens a limb may begin with before its verb: enumerators and adverbs.
SKIP = re.compile(
    r"^(?:[\s:,;]|\(?(?:[ivx]+|[a-z]|\d+)\)|to\b|not\b|then\b|also\b|promptly\b"
    r"|diligently\b|immediately\b|reasonably\b|and\b|otherwise\b|at once\b)+",
    re.IGNORECASE,
)


def _limb_head(text: str) -> str | None:
    stripped = SKIP.sub("", text, count=1).lstrip()
    m = re.match(r"([A-Za-z][A-Za-z-]*)", stripped)
    return m.group(1).lower() if m else None


def _is_performance_disjunction(sentence: str):
    """Returns (anchor_name, left_head, right_head). A disjunction counts only
    when BOTH limbs are headed by a base-form verb -- which is what separates
    two alternative PERFORMANCES from `either Party`, `either case`, or a
    coordinated object/adjective."""
    for name, (pattern, verbs_captured) in F28_ANCHORS.items():
        for m in pattern.finditer(sentence):
            if verbs_captured:
                left, right = m.group(1).lower(), m.group(2).lower()
            else:
                left, right = _limb_head(m.group(1)), _limb_head(m.group(2))
            if left in LIMB_VERBS and right in LIMB_VERBS and left != right:
                return name, left, right
    return None, None, None


# Hand adjudication of every flagged instance, PUBLISHED with its error rate
# rather than patched into the pattern (§8.8.4's discipline). F28's class is
# ONE duty with TWO alternative performances and the obligor choosing; each
# entry below is flagged by the detector and is NOT that.
F28_READING_OVERRIDES = {
    "C02-048": "the disjunction sits inside the OBJECT noun phrase (`the decision to "
               "initiate a Recall or to take some other corrective action`); the duty is "
               "to make and implement a decision, so the alternation is the decision's "
               "CONTENT, not the duty's performance",
    "C04-057": "a disjunction of FAILURE MODES inside an indemnity TRIGGER (`arising out "
               "of Bellicum's failure to obtain ... or to comply`), not alternative "
               "performances of the indemnity duty",
    "C14-138": "`transfer and/or assign` is §8.3's COMPOUND ACTION, not an alternation "
               "the obligor chooses between",
    "C17-023": "NEGATED (`No Provider shall be required to purchase ... or to provide`): "
               "under negation the limbs are a CONJUNCTION -- neither is required -- so "
               "nothing is being chosen between. Polarity, the axis §8.8.1/§8.8.4 "
               "already made load-bearing, reached from the disjunction side",
    "C17-044": "the disjunction is inside a CONDITION (the scope of a third party's "
               "consent); the duty is `each Party shall ... execute any such form`",
    # Reached only at SEGMENT granularity.
    "C12-003": "NEGATED, the same shape as C17-023 (`not to disclose it ... or to use it "
               "except as necessary`): neither limb is permitted, so nothing is chosen "
               "between",
}


def size_f28(sents, segs):
    print("\n" + "=" * 78)
    print("F28 -- DISJUNCTIVE OBLIGATION  (action SLOT gap in Obligation.action)")
    print("=" * 78)

    # --- GATE: both of F28's own real instances, plus two known negatives ---
    KNOWN_POS = {
        "C04-144": "to either promptly and diligently negotiate a license with such Third "
                   "Party or modify the relevant Miltenyi Product(s)",
        "C04-033": "Bellicum shall have the right to transfer Miltenyi Product(s) to a "
                   "Subcontractor, or to request from Miltenyi that Miltenyi Deliver any "
                   "Miltenyi Product(s)",
    }
    KNOWN_NEG = {
        "party_disjunction": "Antares or its Subcontractor shall retain sufficient quantities "
                             "of shipped Products",
        "either_party_right": "either Party may terminate this Agreement upon notice",
        "coordinated_object": "Vendor shall provide technical support and field service or "
                              "assistance to AT&T",
    }
    for name, text in KNOWN_POS.items():
        v, l, r = _is_performance_disjunction(text)
        assert v, f"F28 GATE FAILED: known positive {name} not flagged ({l!r}/{r!r})"
        print(f"  known positive {name}: flagged via {v} ({l} | {r})")
    for name, text in KNOWN_NEG.items():
        v, l, r = _is_performance_disjunction(text)
        assert not v, f"F28 GATE FAILED: known negative {name} flagged ({l!r}/{r!r})"
        print(f"  known negative {name}: not flagged")
    print("  F28 known-answer gate: 2/2 positives, 3/3 negatives  PASS")

    n = len(sents)
    raw = {}
    for name, (pattern, _) in F28_ANCHORS.items():
        raw[name] = [h for h in sents if pattern.search(h[2])]
    print()
    for name in F28_ANCHORS:
        print(_fmt(f"raw anchor hits: {name}", raw[name], n))
    anchored = [h for h in sents if any(p.search(h[2]) for p, _ in F28_ANCHORS.values())]
    print(_fmt("raw anchor hits: ANY anchor", anchored, n))

    flagged, by_anchor, heads = [], collections.Counter(), collections.Counter()
    for h in sents:
        v, l, r = _is_performance_disjunction(h[2])
        if v:
            flagged.append(h)
            by_anchor[v] += 1
            heads[f"{l}/{r}"] += 1
    print()
    print(_fmt("NARROWED: both limbs verb-headed (F28's class)", flagged, n))
    print(f"    by anchor: {dict(by_anchor)}")
    print(f"    precision of the anchor alone: {len(flagged)}/{len(anchored)} "
          f"= {len(flagged)/len(anchored):.1%} -- so the ANCHOR IS NOT THE MEASUREMENT")
    print("\n  instances:")
    for sid, did, s in sorted(flagged):
        v, l, r = _is_performance_disjunction(s)
        print(f"    {sid:9} [{l} | {r}]  {s[:150].strip()}...")
    print("\n  rejected limb-head pairs, PRINTED so a vocabulary miss is visible"
          "\n  rather than a silent false negative:")
    rejected = collections.Counter()
    for sid, did, s in sents:
        if _is_performance_disjunction(s)[0]:
            continue
        for name, (pattern, verbs_captured) in F28_ANCHORS.items():
            m = pattern.search(s)
            if not m:
                continue
            if verbs_captured:
                rejected[(m.group(1).lower(), m.group(2).lower())] += 1
            else:
                rejected[(_limb_head(m.group(1)), _limb_head(m.group(2)))] += 1
            break
    for (l, r), cnt in rejected.most_common(18):
        print(f"    {str(l):22} / {str(r):22} x{cnt}")

    seg_flagged = [h for h in segs if _is_performance_disjunction(h[2])[0]]
    adjudicated = [h for h in flagged if h[0] not in F28_READING_OVERRIDES]
    sent_ovr = {k for k in F28_READING_OVERRIDES if any(h[0] == k for h in flagged)}
    print(f"\n  HAND READING OVERRIDES, published not patched: {len(sent_ovr)} of "
          f"{len(flagged)} flagged at sentence granularity = "
          f"{len(sent_ovr)/len(flagged):.1%} detector error rate "
          f"({len(F28_READING_OVERRIDES)} overrides in all, one reached only at "
          f"segment granularity)")
    for sid, why in sorted(F28_READING_OVERRIDES.items()):
        # An override must be reached at SOME granularity, or it has gone inert
        # and is silently protecting nothing -- v0.62's PRE_RESTAMP lesson.
        assert any(h[0] == sid for h in flagged) or any(h[0] == sid for h in seg_flagged), \
            f"override {sid} has gone INERT at both granularities"
        where = "sentence" if sid in sent_ovr else "segment-only"
        print(f"    {sid} [{where}]: {why}")
    print()
    print(_fmt("ADJUDICATED disjunctive obligations", adjudicated, n))

    # --- THE F27 INTERACTION, PINNED SO IT CANNOT SILENTLY RETURN ---------
    assert not any(h[0] == "C04-144" for h in flagged), \
        "F27-interaction gate: C04-144 is now found at SENTENCE granularity -- " \
        "re-read this section, the splitter defect it documents may be fixed"
    assert any(h[0] == "C04-144" for h in seg_flagged), \
        "F27-interaction gate: C04-144 not found at SEGMENT granularity either"
    print("\n  *** F27 INTERACTION, MEASURED: F28's OWN FOUNDING INSTANCE IS INVISIBLE")
    print("      TO THE SENTENCE-SCOPED SWEEP. `split_sentences()` breaks C04-144 at its")
    print("      `[...***...]` redaction, so the fragment carrying `shall at its option`")
    print("      has NO disjunction and the fragment carrying `either ... negotiate ... or")
    print("      modify` has NO MODAL -- and is therefore filtered out before any")
    print("      detector sees it. Verified by execution, and gated above in BOTH")
    print("      directions. Every sentence-scoped figure here is a LOWER BOUND, and")
    print("      systematically so in C04, the largest hard-stratum document.")
    print(_fmt("  same sweep at SEGMENT granularity", seg_flagged, len(segs)))
    seg_adj = [h for h in seg_flagged if h[0] not in F28_READING_OVERRIDES]
    print(_fmt("  ADJUDICATED at SEGMENT granularity", seg_adj, len(segs)))
    print("    adjudicated instances: " + ", ".join(sorted({h[0] for h in seg_adj})))
    print("    overridden here: "
          + ", ".join(sorted({h[0] for h in seg_flagged} & set(F28_READING_OVERRIDES))))
    return {"flagged": flagged, "adjudicated": adjudicated, "anchored": anchored,
            "seg_flagged": seg_flagged, "seg_adjudicated": seg_adj}


# ===========================================================================
# F29 -- AN EFFORTS / PERFORMANCE STANDARD WITH NO IR FIELD AT ALL
# ===========================================================================
F29_RE = re.compile(
    r"\b((?:best|reasonable|commercially reasonable|reasonable commercial|diligent|"
    r"good faith|commercial|all reasonable|every reasonable|its reasonable)\s+"
    r"(?:efforts|endeavors|endeavours))\b",
    re.IGNORECASE,
)
F29_WIDE_RE = re.compile(r"\b(?:efforts|endeavors|endeavours)\b", re.IGNORECASE)


def size_f29(sents, segs, locked):
    print("\n" + "=" * 78)
    print("F29 -- EFFORTS / PERFORMANCE STANDARD  (a missing FIELD TYPE)")
    print("=" * 78)

    # --- GATE: the locked item that already carries one, plus a negative ----
    assert any(s == "C11-094" for s, _, t in sents if F29_RE.search(t)), \
        "F29 GATE: C11-094 (locked C11-03, 'shall use best efforts') not flagged"
    assert not F29_RE.search("Antares shall invoice AMAG for the costs associated with "
                             "performing these activities"), "F29 GATE: negative flagged"
    assert not F29_RE.search("the Parties will discuss in good faith"), \
        "F29 GATE: a bare good-faith standard (no efforts noun) must not be flagged"
    print("  known-answer gate: C11-094 IN (locked C11-03 carries `best efforts`);")
    print("    a plain invoice duty OUT; a bare `in good faith` OUT.  PASS")

    n = len(sents)
    hits = [h for h in sents if F29_RE.search(h[2])]
    wide = [h for h in sents if F29_WIDE_RE.search(h[2])]
    print()
    print(_fmt("QUALIFIED efforts/endeavours standard", hits, n))
    print(_fmt("  wider: any efforts/endeavours noun", wide, n))
    print("\n  standard breakdown:")
    for std, cnt in collections.Counter(
        re.sub(r"\s+", " ", F29_RE.search(h[2]).group(1).lower()) for h in hits
    ).most_common():
        print(f"    {std:40} {cnt}")

    # --- exposure against the gold set -------------------------------------
    hit_segs = {s for s, _, _ in hits}
    on_locked = sorted(
        (i["item_id"], i["segment_id"], i["stratum"])
        for i in locked.values()
        if i["segment_id"] in hit_segs
    )
    in_span = [(iid, seg, st) for iid, seg, st in on_locked
               if F29_RE.search(locked[iid]["span_text"])]
    print(f"\n  EXPOSURE AGAINST THE GOLD SET:")
    print(f"    locked items whose SEGMENT carries a standard : {len(on_locked)}")
    print(f"    locked items whose OWN SPAN carries one       : {len(in_span)}")
    for iid, seg, st in in_span:
        print(f"      {iid} ({seg}, {st}): "
              f"{F29_RE.search(locked[iid]['span_text']).group(1)!r}")
    seg_hits = [h for h in segs if F29_RE.search(h[2])]
    print()
    print(_fmt("same sweep at SEGMENT granularity", seg_hits, len(segs)))
    print(f"    segment-only extras: "
          f"{sorted({h[0] for h in seg_hits} - {h[0] for h in hits})} (modal filter, not F27)")
    return {"hits": hits, "wide": wide, "on_locked": on_locked, "in_span": in_span,
            "seg_hits": seg_hits}


def main():
    sents, segs = _sentences(with_segments=True)
    from attribution import load_items  # same directory
    locked = load_items()
    f25 = size_f25(sents, segs)
    f28 = size_f28(sents, segs)
    f29 = size_f29(sents, segs, locked)
    print("\n" + "=" * 78)
    print("THE THREE SIZES, STATED SEPARATELY AND NEVER SUMMED (F31(2))")
    print("=" * 78)
    for label, key, extra in [
        ("F25 event-bounded interval (temporal FORM)", f25["adjudicated"],
         f"raw {_tally(f25['core'])[0]}; adjacent `until` family {_tally(f25['until'])[0]}, "
         f"NOT folded in; segment-granularity {_tally(f25['seg_core'])[0]}"),
        ("F28 disjunctive obligation (action SLOT)", f28["seg_adjudicated"],
         f"SEGMENT granularity, which is the load-bearing unit here: the sentence-scoped "
         f"figure is {_tally(f28['adjudicated'])[0]} and MISSES F28's OWN founding "
         f"instance C04-144 to F27's splitter defect. Raw flags "
         f"{_tally(f28['seg_flagged'])[0]} at "
         f"{len([h for h in f28['seg_flagged'] if h[0] in F28_READING_OVERRIDES])}"
         f"/{_tally(f28['seg_flagged'])[0]} hand-override rate"),
        ("F29 efforts standard (missing FIELD TYPE)", f29["hits"],
         f"{len(f29['in_span'])} LOCKED items already carry one in their own span; "
         f"segment-granularity {_tally(f29['seg_hits'])[0]}"),
    ]:
        n, sg, dc = _tally(key)
        print(f"  {label}")
        print(f"      {n:4} sentences  {sg:4} segments  {dc:2} documents")
        print(f"      ({extra})")
    print("\n  THEY ARE NOT SUMMED. F25's class is a temporal FORM gap, F28's an action")
    print("  SLOT gap, F29's a missing FIELD TYPE -- three mechanisms, three populations.")
    print("  The classes are NOT disjoint at the segment level, and that is DISCLOSED")
    print("  rather than asserted away: one segment can carry more than one gap.")
    a25 = {h[0] for h in f25["adjudicated"]}
    a28 = {h[0] for h in f28["seg_adjudicated"]}
    a29 = {h[0] for h in f29["hits"]}
    for la, a, lb, b in [("F25", a25, "F28", a28), ("F25", a25, "F29", a29),
                         ("F28", a28, "F29", a29)]:
        ov = sorted(a & b)
        print(f"    {la} n {lb}: {ov if ov else 'none'}")


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    main()
