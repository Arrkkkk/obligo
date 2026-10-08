"""§10.1 F38: the two drafting styles for a notice-form duty, and the recall cost
of §3.5's non-party-subject filter.

OBSERVATION ONLY. No rule change is proposed and none follows. §3.5's span-scoped
positional test and §8.8's copular excluded class are both deliberate and are not
in question here; what is measured is how often this corpus writes the SAME
substantive requirement -- notices must be in writing / in a given form -- with
the NOTICE as grammatical subject rather than the PARTY, because the IR captures
one style and not the other.

THE RAW FLAG COUNT IS NOT THE FINDING AND MUST NOT BE QUOTED AS ONE. A marker
conjunction cannot tell a form requirement from a genuine party duty that happens
to mention notices, so every flag is hand-read and the override rate is published
beside the raw count. The adjudicated figure is the one that means anything.

Standing Principle 7: the known-answer gate is TWO-SIDED and asserts BOTH poles of
the contrast before any count is read off the screen --
  * `C02-079` (the excluded thing-subject case) must be flagged as NOTICE-subject;
  * `C22-048`, the segment behind locked item `C22-01` (the party-subject
    counterpart, "Each party ... will give the notice in writing"), must be
    flagged as PARTY-subject and NOT as notice-subject.
A screen that flagged only one pole would be measuring a pattern, not a contrast.
`load_pool()` raises below 1,547 segments, because a gate over a short pool
passes (v0.58's own preserved screen printed "12/12 PASS" over zero items).

    uv run --project apps/brain python \
        apps/brain/evals/goldens/holdout/notice_subject/screen.py
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[4]              # apps/brain
ROOT = BRAIN.parents[1]                                  # repo root
POOL_EXPECTED = 1547

_CLAUSE_START = r"(?:^|(?<=[;:])|(?<=, provided, that )|(?<=, provided that )|(?<=, that ))"

# The notice/communication as grammatical SUBJECT of a modal.
#
# ANCHORED AT CLAUSE START, and that anchoring is the fix for a real defect the
# two-sided gate caught rather than a stylistic choice. The first draft was
# unanchored and matched `C22-048` -- "Each party giving ANY NOTICE required or
# permitted under this IP Agreement WILL give the notice in writing" -- where
# `any notice` is the OBJECT of `giving`, not a subject. An unanchored pattern
# cannot tell a notice in subject position from one in object position, which is
# exactly the contrast this screen exists to measure, so it would have reported a
# contrast while measuring none.
#
# CONSEQUENCE, STATED RATHER THAN HIDDEN: anchoring makes the screen CONSERVATIVE.
# A true notice-subject clause buried mid-sentence after a construction this
# anchor does not list is missed, so the notice-subject count is a LOWER BOUND.
# That is the right direction for a recall disclosure -- it cannot inflate the
# cost being disclosed -- but it is not a census.
NOTICE_SUBJECT = re.compile(
    _CLAUSE_START + r"\s*(?:all|any|each|every|such|the)\s+(?:written\s+)?"
    r"notices?(?:\s+and\s+other\s+communications?)?[^.;]{0,70}?\b(?:shall|will|must)\b",
    re.I,
)
# A party as grammatical SUBJECT, with a notice in the predicate.
#
# ANCHORED FOR THE SAME REASON, after the SAME DEFECT appeared in this mirror
# pattern and was caught by cross-checking the screen against an independently
# verified fact rather than by the gate. Unanchored, it matched `C02-079` on
# "or at such other address FOR A PARTY as SHALL be specified by like NOTICE" --
# where `a Party` is the object of `for`, proven by offset in that segment's own
# exclusion entry. The screen therefore reported a party duty in the very segment
# whose exclusion rests on there being none, i.e. it contradicted the finding it
# was built to support. The gate below now asserts that absence, so the
# contradiction cannot return silently.
PARTY_SUBJECT = re.compile(
    _CLAUSE_START + r"\s*(?:each|either|any|both|a|the)\s+part(?:y|ies)\b[^.;]{0,90}?"
    r"\b(?:shall|will|must)\b[^.;]{0,70}?\bnotice",
    re.I,
)

# --- the hand pass. Every raw flag is read; the rejections carry reasons. ----
# "FORM" = the clause states the required form/manner/effect of a notice with the
#          notice as subject, commanding no party conduct -> the F38 class.
# Anything else is rejected, with why.
# THE HAND PASS, read segment by segment from the pool text. The mechanical
# question (does a notice-subject clause exist?) is NOT the finding; the finding is
# whether the SEGMENT falls to zero obligation-bearing clauses ON F38's MECHANISM,
# which is the only configuration where §3.5's filter costs a gold item outright.
GENUINE_ZERO = {
    "C02-079": "F38's motivating case. Four modals, every one thing-subject: `All notices "
               "and other communications hereunder shall be in writing` / `shall be deemed "
               "given` / `such other address ... shall be specified` / `notices of a change "
               "of address shall be effective`. Both `Party` tokens are prepositional "
               "objects, proven by offset. ZERO party conduct.",
    "C05-077": "`Any notice ... must be in writing and delivered either in person ...` plus "
               "`Notice shall be deemed sufficiently given ...`. Both thing-subject; the "
               "second is an explicit deeming provision.",
    "C11-123": "`All notices to BKC shall be written in English and shall be sent by "
               "facsimile and hand delivered ...` -- three modals, all thing-subject.",
    "C11-124": "The mirror-image provision for the other direction (`All notices to the "
               "Franchisee or the Principals shall be written in English ...`), same shape.",
    "C13-045": "`All notices or other communications, which are required or permitted "
               "hereunder shall be in writing and sufficient if delivered personally ...` "
               "-- single sentence, thing-subject.",
    "C17-058": "`All notices, requests, claims, demands and other communications hereunder "
               "shall be in writing and shall be given by delivery in person ...`",
}

# Flagged, but NOT a clean F38 zero -- and these are published because they make the
# recall cost SMALLER than the raw count, which is the direction a disclosure must not
# round in its own favour.
NOT_A_CLEAN_ZERO = {
    "E03-052": "CARRIES AN EMBEDDED PARTY-SUBJECT MODAL: `... or at any address such PARTY "
               "MAY DESIGNATE by prior written notice to the other in accordance with this "
               "Section 11.3`. That is a party-subject `MAY` with a correlative party and a "
               "gating reference, so the segment does not fall to zero on F38's mechanism. "
               "Whether that embedded clause is itself annotatable is a separate judgment "
               "call (§3.2's main-predicate filter -- it modifies `address` rather than "
               "being the sentence's predicate) and is NOT decided here.",
    "E05-028": "ZERO IS OVER-DETERMINED BY A DIFFERENT RULE. Its first fragment is an ORPHAN "
               "with no subject at all -- `may change its address by providing written "
               "notice ...`, the subject sitting OUTSIDE the segment -- so it fails §2's "
               "self-containment test independently (§2.6, `C04-024`/`C22-025`). Its implied "
               "subject is a party, so this is NOT §3.5's thing-subject mechanism and the "
               "zero is not attributable to F38.",
}


def load_corpus_module():
    spec = importlib.util.spec_from_file_location("corpus", BRAIN / "evals/corpus.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_pool(mod):
    pool = mod.build_pool(ROOT / ".corpus", mod.load_manifest())
    if len(pool) < POOL_EXPECTED:
        raise RuntimeError(
            f"pool rebuilt to {len(pool)}, expected {POOL_EXPECTED}; a known-answer "
            "gate over a short pool proves nothing"
        )
    return pool


def classify(mod, pool):
    """segment_id -> (notice_subject_sentences, party_subject_sentences)."""
    out = {}
    for seg in pool:
        ns, ps = [], []
        for sent in mod.split_sentences(seg["text"]):
            if NOTICE_SUBJECT.search(sent):
                ns.append(sent)
            if PARTY_SUBJECT.search(sent):
                ps.append(sent)
        if ns or ps:
            out[seg["segment_id"]] = (ns, ps)
    return out


def gate(hits):
    """Two-sided, and it asserts the CONTRAST rather than the pattern."""
    c02 = hits.get("C02-079", ([], []))
    assert c02[0], "GATE FAILED: C02-079 (the excluded thing-subject case) is not flagged NOTICE-subject"
    c22 = hits.get("C22-048", ([], []))
    assert c22[1], (
        "GATE FAILED: C22-048 (locked item C22-01's segment, the party-subject "
        "counterpart) is not flagged PARTY-subject"
    )
    assert not c22[0], (
        "GATE FAILED: C22-048 is flagged NOTICE-subject too, so the two patterns do "
        "not discriminate and no contrast is being measured"
    )
    # The fourth pole, and the one an earlier draft of this screen got WRONG:
    # C02-079's exclusion rests on there being NO party conduct in it, and both of
    # its `Party` tokens were proven prepositional objects by offset. If this screen
    # reports a party duty there, the screen contradicts the finding it supports.
    assert not c02[1], (
        "GATE FAILED: C02-079 is flagged PARTY-subject, contradicting its own "
        "exclusion -- both its `Party` tokens are prepositional objects, verified "
        "by offset. The pattern is matching an object as a subject."
    )
    print("GATE PASSED (four assertions): C02-079 flags NOTICE-subject and NOT "
          "party-subject; C22-048 flags PARTY-subject and NOT notice-subject\n")


def main() -> int:
    mod = load_corpus_module()
    pool = load_pool(mod)
    hits = classify(mod, pool)
    gate(hits)

    notice = {k: v[0] for k, v in hits.items() if v[0]}
    party = {k: v[1] for k, v in hits.items() if v[1]}
    both = sorted(set(notice) & set(party))

    print(f"pool: {len(pool)} segments (gate: >= {POOL_EXPECTED})\n")
    print("RAW FLAGS -- NOT THE FINDING:")
    print(f"  notice-subject (thing) segments : {len(notice)}")
    print(f"  party-subject notice segments   : {len(party)}")
    print(f"  segments carrying BOTH          : {len(both)} -> {both}")
    print()
    print("THE HAND PASS is what the finding rests on. Every notice-subject flag is")
    print("read, and the decisive question is NOT whether the clause is thing-subject")
    print("but whether the SEGMENT falls to ZERO obligation-bearing clauses -- which is")
    print("the only configuration where §3.5's filter costs a gold item outright.")
    print()
    for sid in sorted(notice):
        ns = notice[sid]
        coexists = sid in party
        print(f"  {sid}  notice-subject x{len(ns)}  party-duty in same segment: "
              f"{'YES' if coexists else 'no'}")
        print(f"      {ns[0][:112]!r}")
    print()
    # The hand pass must cover exactly what the screen flagged, or one of the two is stale.
    covered = set(GENUINE_ZERO) | set(NOT_A_CLEAN_ZERO)
    assert covered == set(notice), (
        f"hand pass and screen disagree -- unadjudicated: {sorted(set(notice)-covered)}; "
        f"adjudicated but no longer flagged: {sorted(covered-set(notice))}"
    )
    print("ADJUDICATED BY HAND, every flag read from the pool text:")
    print(f"  RAW notice-subject flags              : {len(notice)}   <- NOT the finding")
    print(f"  GENUINELY fall to zero on F38's mech. : {len(GENUINE_ZERO)}")
    print(f"  flagged but NOT a clean F38 zero      : {len(NOT_A_CLEAN_ZERO)}  "
          f"({len(NOT_A_CLEAN_ZERO)}/{len(notice)} = "
          f"{len(NOT_A_CLEAN_ZERO)/len(notice)*100:.0f}% override rate)")
    for sid, why in sorted(NOT_A_CLEAN_ZERO.items()):
        print(f"    {sid}: {why[:104]}...")
    docs = sorted({s.split('-')[0] for s in GENUINE_ZERO})
    print(f"  THE ADJUDICATED FIGURE: {len(GENUINE_ZERO)} segments across {len(docs)} "
          f"documents ({' '.join(docs)})")
    print(f"  against {len(party)} party-subject notice duties, which the IR DOES capture")
    print()
    print("RECALL DISCLOSURE, stated as a disclosure and not as a defect: §3.5's")
    print("non-party-subject filter is deliberate, and §8.8's excluded class has always")
    print("been the copular one. What this screen records is that the corpus writes the")
    print("same substantive notice-form requirement in both styles, so the IR's coverage")
    print("of that requirement is a function of DRAFTING STYLE rather than of extraction")
    print("quality. No rule change is proposed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
