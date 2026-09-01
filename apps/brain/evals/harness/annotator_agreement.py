"""Section 5.1's annotator-comparison predicate `A` -- the executable form.

Section 5 is the PIPELINE's predicate and this is not it. The two share eight
clause DEFINITIONS (which field, and what "matches" means at field level) and
share section 4.1/4.2 alignment; they differ in three comparison rules, and
each difference is forced by a structural fact rather than chosen for taste.
Read section 5.1 of docs/eval/GOLD_SET_GUIDELINE.md for the derivation; this
module is its executable form, not a re-derivation.

WHY TWO PREDICATES AT ALL. Section 5 clause 2 tests `prediction in gold's
accept_set` -- one-sided by construction. One-sidedness is COHERENT against a
predictor bound by a closed grammar (grammar/obligation.lark's ACTION terminal
is a closed set of 34 verbs, so an out-of-vocabulary emission is impossible)
and INCOHERENT against a peer annotator, for whom an out-of-vocabulary value is
not a competing reading of the sentence but a malformed annotation. The
2026-08-29 cold run measured that difference at 5 of 14 disagreements.

A1 -- THE CONFORMANCE GATE, AND IT IS SLOT-ONLY. A closed-vocabulary field
whose own value falls outside its vocabulary makes the item NON_CONFORMING:
excluded from both the numerator and the denominator of K, and reported as its
own figure. It is never counted as a "disagreement", because the two annotators
are not disagreeing about the sentence -- one of them wrote a value the field
cannot hold. Section 8.8 is what makes this a convention failure rather than a
judgment call: gold encodes an out-of-taxonomy verb as (nearest taxonomy verb +
`action_not_in_taxonomy`), so writing the true verb instead is declining a
required encoding, not proposing a rival label.

  THE GATE DOES NOT REACH ACCEPT-SET MEMBERS, and that boundary was PROVEN by
  execution rather than argued (Standing Principle 7). An off-vocabulary
  accept-set member is INERT: it can only ever be compared against a slot
  value, every legal slot value is in the vocabulary, so it can never produce a
  match in either direction. Measured on the 2026-08-29 data: stripping all 52
  of cold's off-taxonomy accept-set members from both sides changes NO clause
  outcome on ANY item. Gating on them instead would have marked 27 of 32 items
  NON_CONFORMING and left K over n=5, which supports no inference at all --
  the instrument would have been destroyed by a gate one scope too wide.

A2 -- ACCEPT-SET FIELDS ARE COMPARED SYMMETRICALLY, by MUTUAL MEMBERSHIP:
gold's slot in cold's set, OR cold's slot in gold's set. This is exactly
section 5's own test run in both directions and disjoined -- the minimal change
that removes the one-sidedness, not a new rule.

  The looser alternative -- non-empty intersection of the two accept-sets, the
  form RESULTS.md's sensitivity A measured -- is REJECTED, and the measurement
  says the rejection is free. Under the A1 gate the two rules give the
  IDENTICAL result on the 2026-08-29 data (K=7/27 either way), because the only
  item they separate (C02-03: both sets hold REPORT while neither slot is in
  the other's set) is gated out for an off-taxonomy slot. So intersection buys
  nothing measurable and would "agree" an item whose slot value the field
  cannot hold. The tighter rule is taken on principle at zero measured cost.

A3 -- PARTIES ARE COMPARED AS STRINGS, WITH NO REGISTRY BRANCH. Section 5's
lenient branch fires when the PIPELINE resolved a party; a cold annotation
carries an alias and nothing else, so the branch is not merely unused but
unavailable. Resolving both annotators' aliases through the document registry
was considered and is DEFERRED rather than adopted, on two measured grounds:
it changes nothing (of 31 matched pairs, 16 gold obligors and 10 gold obligees
resolve, and ZERO K disagreements flip), and registries exist for only 10 of
the 15 documents in the set, so adopting it would make the instrument's
strictness vary by document -- a silent coverage hazard for the sake of an
effect measured at zero. Revisit if a future cold run puts a genuine
same-party/different-alias pair in front of it.

WHAT THIS MODULE DELIBERATELY DOES NOT COMPUTE. `known_gaps` is section 5.1's
ninth clause and belongs to THIS predicate, not to section 5 -- but it is
reported as its own instrument, `evals.harness.gap_agreement`'s G/G_swing, and
is never added to or averaged with K. That separation is GAP_AGREEMENT_DESIGN
section 2's confirmed decision and is preserved here by not implementing a
ninth clause at all: clauses 1-8 produce K, clause 9 produces G, and the three
figures (K, G, conformance) are published together and never combined.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from obligo_brain.compiler.ast import ACTIONS

from evals.harness.align import iou
from evals.harness.gap_agreement import (
    DIAGNOSE_ANCHOR,
    REDESIGN_ANCHOR,
    wilson95,
)
from evals.harness.score import CLAUSES, norm, singularize

# Closed vocabularies A1 gates on. Each is closed in the IR itself, not merely
# by convention: MODALITIES and TEMPORAL_FORMS are grammar productions,
# ACTIONS is grammar/obligation.lark's ACTION terminal. `known_gaps` is closed
# by section 8 rather than by the grammar, so its vocabulary is passed in by
# the caller (see `conformance_failures`) rather than imported -- section 8
# gains tags over time and hardcoding them here would silently gate a legitimately
# new tag as a violation.
MODALITIES = frozenset({"MUST", "MUST_NOT", "SHOULD", "MAY"})
TEMPORAL_FORMS = frozenset({"BY", "WITHIN", "EVERY", "DURING", "RELATIVE_TO_TRIGGER"})

# Section 8's tag vocabulary. Supplied as a DEFAULT rather than hardcoded into
# the gate, because section 8 gains tags over time and a stale list would gate a
# legitimately new tag as a violation -- the silent-wrong-answer shape Standing
# Principle 7 is about. The guard against staleness is a test, not care:
# test_harness_annotator_agreement.py asserts every tag any locked gold item
# carries is in this set, so an added tag fails the suite instead of quietly
# marking real items NON_CONFORMING.
SECTION_8_TAGS = frozenset({
    "redacted_value", "redacted_clause", "compound_action", "mutual_obligation",
    "exception_unsupported", "unless_unsupported", "action_not_in_taxonomy",
    "within_preposition", "relative_trigger_preposition", "corpus_artifact_in_span",
    "shared_subject_split",
})


class Agreement(str, Enum):
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    NON_CONFORMING = "NON_CONFORMING"
    UNMATCHED = "UNMATCHED"


@dataclass(frozen=True)
class ItemAgreement:
    item_id: str
    outcome: Agreement
    failed_clauses: tuple[str, ...] = ()
    conformance_failures: tuple[str, ...] = ()

    @property
    def counts_in_k(self) -> bool:
        """NON_CONFORMING items leave BOTH sides of K's fraction (A1). An
        UNMATCHED gold item stays a disagreement -- it is the item-count
        decision PREREGISTRATION.md D3/channel 4 exists to test."""
        return self.outcome is not Agreement.NON_CONFORMING


def conformance_failures(item: Mapping, *, gap_vocabulary: frozenset[str] = SECTION_8_TAGS) -> tuple[str, ...]:
    """A1's gate. SLOT VALUES ONLY -- see the module docstring's inertness
    proof for why accept-set members are excluded by construction rather than
    by preference."""
    bad: list[str] = []
    if item["modality"] not in MODALITIES:
        bad.append(f"modality={item['modality']!r}")
    if item["action"] not in ACTIONS:
        bad.append(f"action={item['action']!r}")
    temporal = item.get("temporal")
    if temporal and temporal.get("form") not in TEMPORAL_FORMS:
        bad.append(f"temporal.form={temporal.get('form')!r}")
    for tag in item.get("known_gaps") or ():
        if tag not in gap_vocabulary:
            bad.append(f"known_gaps={tag!r}")
    return tuple(bad)


def _members(item: Mapping, key: str) -> set[str]:
    return {norm(x) for x in (item.get(key) or ())}


def _accept_clause(a: Mapping, b: Mapping, slot: str, accept_key: str, *,
                   symmetric: bool, number_normalize: bool = False) -> bool:
    """A2. `a` is gold, `b` is the other annotator. Symmetric mode disjoins
    section 5's own membership test with the same test run the other way."""
    def fold(s: str) -> str:
        return singularize(s) if number_normalize else norm(s)

    a_set = {fold(x) for x in _members(a, accept_key)} | {fold(a[slot])}
    b_set = {fold(x) for x in _members(b, accept_key)} | {fold(b[slot])}
    if fold(b[slot]) in a_set:
        return True
    return symmetric and fold(a[slot]) in b_set


def _conditions_clause(a: Mapping, b: Mapping, *, symmetric: bool) -> bool:
    """Clause 7, count-sensitive and order-insensitive (section 3.8), reading
    section 3.8.3's `conditions_accept_set` on gold's side and -- in symmetric
    mode -- on the other annotator's too."""
    a_conds, b_conds = a["conditions"], b["conditions"]
    if len(a_conds) != len(b_conds):
        return False
    a_acc = a.get("conditions_accept_set") or []
    b_acc = b.get("conditions_accept_set") or []
    used: set[int] = set()
    for j, b_text in enumerate(b_conds):
        for i, a_text in enumerate(a_conds):
            if i in used:
                continue
            options = {norm(a_text)}
            if i < len(a_acc):
                options |= {norm(x) for x in (a_acc[i] or ())}
            if symmetric and j < len(b_acc):
                options |= {norm(x) for x in (b_acc[j] or ())}
            if norm(b_text) in options:
                used.add(i)
                break
        else:
            return False
    return True


def compare_clauses(gold: Mapping, other: Mapping, *, symmetric: bool = True) -> dict[str, bool]:
    """Clauses 1-8. `symmetric=False` reproduces the one-sided section 5 form
    the 2026-08-29 run actually used -- kept so that published K stays
    re-derivable (the original script was never preserved, which is exactly
    the defect audit/README.md was written about)."""
    out: dict[str, bool] = {}
    out["modality"] = gold["modality"] == other["modality"]
    out["action"] = _accept_clause(gold, other, "action", "action_accept_set",
                                   symmetric=symmetric)
    out["obligor"] = _accept_clause(gold, other, "obligor", "obligor_accept_set",
                                    symmetric=symmetric)
    out["obligee"] = norm(gold["obligee"]) == norm(other["obligee"])
    out["object_class"] = _accept_clause(gold, other, "object_class",
                                         "object_class_accept_set",
                                         symmetric=symmetric, number_normalize=True)
    out["temporal"] = gold.get("temporal") == other.get("temporal")
    out["conditions"] = _conditions_clause(gold, other, symmetric=symmetric)
    out["underspecified"] = bool(gold["underspecified"]) == bool(other["underspecified"])
    return out


def pair_items(gold_items: Sequence[Mapping], other_items: Sequence[Mapping],
               *, threshold: float = 0.5) -> tuple[list[tuple[int, int, float]], list[int], list[int]]:
    """Section 4.1 greedy-descending-IoU, PLUS section 4.2's v0.36 content
    tie-break, which `align.align` does not implement.

    That tie-break is not optional here. C04-139's two gold items carry
    BYTE-IDENTICAL spans, so IoU is uninformative between them and plain greedy
    pairing is decided by iteration order -- it happened to land correctly for
    this data, which is luck rather than a rule, and OBJECT_CLASS_INVESTIGATION
    section 0's struck reproduction is what mispairing them costs.
    """
    spans_g = [(g["span_char_start"], g["span_char_end"]) for g in gold_items]
    spans_o = [(o["span_char_start"], o["span_char_end"]) for o in other_items]
    identical: dict[tuple[int, int], list[int]] = {}
    for gi, s in enumerate(spans_g):
        identical.setdefault(s, []).append(gi)
    tied = {gi for group in identical.values() if len(group) > 1 for gi in group}

    scored = []
    for gi, gs in enumerate(spans_g):
        for oi, os_ in enumerate(spans_o):
            v = iou(gs, os_)
            if v >= threshold:
                scored.append((v, gi, oi))

    def sort_key(row):
        v, gi, oi = row
        preferred = 0
        if gi in tied:
            group = identical[spans_g[gi]]
            hits = [j for j in group
                    if other_items[oi]["action"] in (gold_items[j]["action_accept_set"] or ())]
            if len(hits) == 1 and hits[0] == gi:
                preferred = -1          # section 4.2: exactly one accept-set covers it
        return (preferred, -v, gold_items[gi]["item_id"], spans_o[oi][0])

    scored.sort(key=sort_key)
    used_g: set[int] = set()
    used_o: set[int] = set()
    pairs: list[tuple[int, int, float]] = []
    for v, gi, oi in scored:
        if gi in used_g or oi in used_o:
            continue
        used_g.add(gi)
        used_o.add(oi)
        pairs.append((gi, oi, v))
    return (pairs,
            [i for i in range(len(gold_items)) if i not in used_g],
            [i for i in range(len(other_items)) if i not in used_o])


@dataclass
class AgreementResult:
    items: tuple[ItemAgreement, ...]

    @property
    def scoreable(self) -> tuple[ItemAgreement, ...]:
        return tuple(i for i in self.items if i.counts_in_k)

    @property
    def n(self) -> int:
        return len(self.scoreable)

    @property
    def k(self) -> int:
        return sum(1 for i in self.scoreable if i.outcome is not Agreement.AGREE)

    @property
    def non_conforming(self) -> tuple[ItemAgreement, ...]:
        return tuple(i for i in self.items if i.outcome is Agreement.NON_CONFORMING)

    @property
    def k_rate(self) -> float:
        return self.k / self.n if self.n else 0.0

    @property
    def k_wilson(self) -> tuple[float, float]:
        return wilson95(self.k, self.n)

    @property
    def conformance_rate(self) -> float:
        return len(self.non_conforming) / len(self.items) if self.items else 0.0

    @property
    def bands(self) -> tuple[int, int]:
        """PREREGISTRATION.md section 4's OWN derivation method -- preserve
        section 7's evidential strength (the Wilson95 LOWER bound at each
        trigger) rather than its raw counts -- recomputed at THIS n instead of
        transcribing the n=32 counts. Returns (smallest k that is DIAGNOSE,
        smallest k that is REDESIGN).

        Deriving rather than transcribing is load-bearing: A's gate changes n,
        and reusing counts fixed for n=32 would silently change the band's
        evidential strength. Checked against the published n=32 bands (3, 6) as
        a known-answer case in the tests."""
        diagnose = redesign = None
        for k in range(self.n + 1):
            lower = wilson95(k, self.n)[0]
            if diagnose is None and lower >= DIAGNOSE_ANCHOR:
                diagnose = k
            if redesign is None and lower >= REDESIGN_ANCHOR:
                redesign = k
                break
        if diagnose is None or redesign is None:      # pragma: no cover - n too small
            raise ValueError(f"no band clears the anchors at n={self.n}")
        return (diagnose, redesign)

    @property
    def verdict(self) -> str:
        diagnose, redesign = self.bands
        if self.k >= redesign:
            return "REDESIGN"
        if self.k >= diagnose:
            return "DIAGNOSE"
        return "PROCEED"


def compute(gold_by_segment: Mapping[str, Sequence[Mapping]],
            other_by_segment: Mapping[str, Sequence[Mapping]],
            *, gap_vocabulary: frozenset[str] = SECTION_8_TAGS, symmetric: bool = True,
            gate: bool = True) -> AgreementResult:
    """`symmetric=False, gate=False` is the 2026-08-29 form, kept re-derivable."""
    out: list[ItemAgreement] = []
    for segment_id, gold_items in sorted(gold_by_segment.items()):
        others = list(other_by_segment.get(segment_id, ()))
        gold_items = sorted(gold_items, key=lambda d: (d["span_char_start"], d["item_id"]))
        pairs, missed, _surplus = pair_items(gold_items, others)
        for gi, oi, _v in pairs:
            gold, other = gold_items[gi], others[oi]
            failures = ()
            if gate:
                failures = (conformance_failures(gold, gap_vocabulary=gap_vocabulary)
                            + conformance_failures(other, gap_vocabulary=gap_vocabulary))
            if failures:
                out.append(ItemAgreement(gold["item_id"], Agreement.NON_CONFORMING,
                                         conformance_failures=failures))
                continue
            clauses = compare_clauses(gold, other, symmetric=symmetric)
            failed = tuple(c for c in CLAUSES if not clauses[c])
            out.append(ItemAgreement(
                gold["item_id"],
                Agreement.DISAGREE if failed else Agreement.AGREE,
                failed_clauses=failed))
        for gi in missed:
            out.append(ItemAgreement(gold_items[gi]["item_id"], Agreement.UNMATCHED,
                                     failed_clauses=("UNMATCHED",)))
    return AgreementResult(items=tuple(sorted(out, key=lambda i: i.item_id)))
