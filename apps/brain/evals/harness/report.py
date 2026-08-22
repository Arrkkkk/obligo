"""Aggregates scored runs into the figures section 9 requires, with the
caveats that make them honest.

Four decisions are implemented literally here rather than left to the caller,
because each is a way a report could quietly overstate:

G2 -- MODAL OUTCOME TIE-BREAK. Section 6 asks for "the per-item modal outcome
plus a count of items unstable across runs" but three runs can produce three
different outcomes, in which case no mode exists. Where there is no unique
mode the WORST outcome is reported, and such an item is always counted
unstable. Never round a measurement in the pipeline's favour; the instability
count carries the real signal either way.

G3 -- CRITERION 2's DUAL DENOMINATOR IS NOT IN FORCE. Section 9 records the
dual-reporting amendment as "RECOMMENDED, NOT YET APPROVED... it is NOT in
force", pending a blueprint section 21 decision. Both figures are emitted and
LABELLED: all-items is the in-force criterion 2; the len(known_gaps)==0 figure
carries "recommended, not in force". Emitting the second as though it were the
criterion would implement an unapproved amendment.

G4 -- NO PREDICTED CEILING. Section 9 asks for "the expected all-items ceiling
stated in advance", but the consolidation pass established that the
tag-derived 39-61% ceiling is wrong item by item -- most tagged items compile
fine. Publishing it would quote a number already shown unsound. The report
states tag counts and the observed rate, and says explicitly that no per-item
reachability ceiling has been computed.

G1 -- UNSCOREABLE CANDIDATES CARRY THEIR SPAN TEXT. Section 21 R6's UNEXPECTED
over-count is triageable, not merely acknowledged: the exclusion logs already
name excluded obligation-bearing clauses for at least one segment
(E03-005#itemize, E03-005#discuss), so each UNEXPECTED is emitted with its span
so it can be checked against the log rather than counted blind.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from evals.harness.score import Outcome

# Worst-first severity. Used only for the no-unique-mode tie-break (G2).
SEVERITY = {Outcome.UNEXPECTED: 3, Outcome.MISSED: 2, Outcome.PARTIAL: 1, Outcome.FULLY_CORRECT: 0}

R6_CAVEAT = (
    "UNEXPECTED counts in gold-set scoring reports are a known over-count until "
    "NOT_ANNOTATABLE spans are annotated for all 12 gold segments (real judgment work, "
    "same review discipline as gold items, not yet scheduled)."
)


def modal_outcome(outcomes: Sequence[Outcome]) -> tuple[Outcome, bool]:
    """Returns (modal outcome, unstable). No unique mode -> worst outcome (G2)."""
    if not outcomes:
        raise ValueError("an item must have at least one run to have a modal outcome")
    counts = collections.Counter(outcomes)
    top = max(counts.values())
    tied = [o for o, n in counts.items() if n == top]
    unstable = len(set(outcomes)) > 1
    if len(tied) == 1:
        return tied[0], unstable
    return max(tied, key=lambda o: SEVERITY[o]), True


@dataclass(frozen=True)
class UnscoreableCandidate:
    """An UNEXPECTED prediction, emitted with enough context to triage it against
    the exclusion log rather than count it blind (G1)."""
    run: int
    segment_id: str
    char_start: int
    char_end: int
    span_text: str


@dataclass
class ItemReport:
    item_id: str
    known_gaps: tuple[str, ...]
    outcomes: tuple[Outcome, ...]
    modal: Outcome
    unstable: bool
    failed_clauses: tuple[str, ...] = ()


@dataclass
class Report:
    items: list[ItemReport] = field(default_factory=list)
    unscoreable_candidates: list[UnscoreableCandidate] = field(default_factory=list)
    vague_temporal_items: int = 0
    unscoreable_items: int = 0
    provenance: dict = field(default_factory=dict)

    # --- section 9's two denominators -------------------------------------
    @property
    def criterion2_all_items(self) -> tuple[int, int]:
        n = sum(1 for i in self.items if i.modal is Outcome.FULLY_CORRECT)
        return n, len(self.items)

    @property
    def criterion2_no_known_gaps(self) -> tuple[int, int]:
        scope = [i for i in self.items if not i.known_gaps]
        return sum(1 for i in scope if i.modal is Outcome.FULLY_CORRECT), len(scope)

    @property
    def per_tag_counts(self) -> dict[str, int]:
        c: collections.Counter[str] = collections.Counter()
        for i in self.items:
            c.update(set(i.known_gaps))
        return dict(sorted(c.items()))

    @property
    def unstable_count(self) -> int:
        return sum(1 for i in self.items if i.unstable)

    @property
    def correctly_underspecified_note(self) -> str:
        return "share correctly underspecified is reported per item via clause 8"

    def render(self) -> str:
        fc_all, n_all = self.criterion2_all_items
        fc_ng, n_ng = self.criterion2_no_known_gaps
        pct = lambda a, b: f"{a}/{b} = {a / b * 100:.1f}%" if b else f"{a}/0 = n/a"
        lines = [
            "GOLD-SET TIER-2 SCORING REPORT",
            "",
            f"Criterion 2 (IN FORCE, all items):        {pct(fc_all, n_all)}",
            f"Criterion 2 over len(known_gaps)==0:      {pct(fc_ng, n_ng)}",
            "    ^ RECOMMENDED, NOT IN FORCE (§9). Reported alongside, never as the criterion.",
            "",
            "NO PREDICTED CEILING IS STATED (§9's 'ceiling in advance').",
            "    The tag-derived 39-61% ceiling was shown wrong item by item during the",
            "    consolidation pass -- most tagged items compile fine. A per-item",
            "    reachability ceiling has NOT been computed.",
            "",
            f"Items unstable across runs (§6):          {self.unstable_count}/{len(self.items)}",
            f"Items carrying a vague temporal (§15.4):  {self.vague_temporal_items}",
            f"Unscoreable items (redacted_clause):      {self.unscoreable_items}",
            "",
            "Per-tag counts -- NON-SUMMABLE (§9): one item may carry several, so these",
            "overlap and their sum exceeds the number of tagged items.",
        ]
        for tag, n in self.per_tag_counts.items():
            lines.append(f"    {n} items carry {tag!r}")
        lines += ["", f"UNEXPECTED predictions: {len(self.unscoreable_candidates)}", f"    {R6_CAVEAT}"]
        for u in self.unscoreable_candidates:
            lines.append(
                f"    run{u.run} {u.segment_id}[{u.char_start}:{u.char_end}] {u.span_text[:90]!r}"
            )
        lines += ["", "Provenance:"]
        for k, v in sorted(self.provenance.items()):
            lines.append(f"    {k}: {v}")
        return "\n".join(lines)


def build(
    per_item_runs: dict[str, list[Outcome]],
    gold_by_id: dict[str, dict],
    *,
    unscoreable_candidates: Iterable[UnscoreableCandidate] = (),
    provenance: dict | None = None,
) -> Report:
    report = Report(provenance=dict(provenance or {}))
    for item_id, outcomes in sorted(per_item_runs.items()):
        modal, unstable = modal_outcome(outcomes)
        gold = gold_by_id[item_id]
        report.items.append(
            ItemReport(
                item_id=item_id,
                known_gaps=tuple(gold.get("known_gaps", ())),
                outcomes=tuple(outcomes),
                modal=modal,
                unstable=unstable,
            )
        )
    report.unscoreable_candidates = list(unscoreable_candidates)
    report.vague_temporal_items = sum(
        1 for g in gold_by_id.values() if g.get("vague_temporal_phrase")
    )
    report.unscoreable_items = sum(
        1 for g in gold_by_id.values() if "redacted_clause" in g.get("known_gaps", ())
    )
    return report
