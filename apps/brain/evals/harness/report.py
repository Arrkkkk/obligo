"""Aggregates scored runs into the figures section 9 requires, with the
caveats that make them honest.

Five decisions are implemented literally here rather than left to the caller,
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

G5 -- A SHORT RUN STATES ITS RUN COUNT INLINE. Section 6.1 (v0.29) admits
items scored over fewer than 3 runs when the provider reproducibly refuses a
request, and requires the run count and reason stated ON THE SPOT wherever the
item's figure appears -- not in a footnote. ItemReport therefore carries
run_count, and render() annotates any item whose count differs from the set's
maximum. The n=2 tie resolves via G2's worst-outcome rule, which section 6.1
defers to as of v0.30; there is no separate "no modal outcome" status.

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
    short_run_reason: str = ""      # G5: why this item has fewer runs than the set

    @property
    def run_count(self) -> int:
        return len(self.outcomes)


@dataclass
class Report:
    items: list[ItemReport] = field(default_factory=list)
    unscoreable_candidates: list[UnscoreableCandidate] = field(default_factory=list)
    vague_temporal_items: int = 0
    unscoreable_items: int = 0
    provenance: dict = field(default_factory=dict)
    miss_kinds: dict = field(default_factory=dict)   # item_id -> per-run miss diagnosis

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
    def max_runs(self) -> int:
        return max((i.run_count for i in self.items), default=0)

    @property
    def short_run_items(self) -> list[ItemReport]:
        """Items scored over fewer runs than the rest of the set (G5/section 6.1)."""
        top = self.max_runs
        return [i for i in self.items if i.run_count < top]

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
        short = self.short_run_items
        lines += ["", f"Runs per item: {self.max_runs} (§6)."]
        if short:
            lines.append(
                f"    {len(short)} item(s) scored over FEWER runs -- §6.1, stated here and "
                "again on each item's own line below:"
            )
            for i in short:
                lines.append(
                    f"    {i.item_id}: {i.run_count} runs, not {self.max_runs}"
                    + (f" -- {i.short_run_reason}" if i.short_run_reason else "")
                )
        else:
            lines.append("    Every item scored over the full number of runs.")

        lines += ["", "Per item (modal outcome; run count stated inline per §6.1):"]
        for i in self.items:
            note = "" if i.run_count == self.max_runs else (
                f"  [{i.run_count} RUNS, not {self.max_runs}"
                + (f": {i.short_run_reason}" if i.short_run_reason else "") + "]"
            )
            flag = " UNSTABLE" if i.unstable else ""
            gaps = f" gaps={list(i.known_gaps)}" if i.known_gaps else ""
            failed = f" failed={list(i.failed_clauses)}" if i.failed_clauses else ""
            lines.append(
                f"    {i.item_id:8s} {i.modal.value:14s}"
                f" runs={[o.value for o in i.outcomes]}{flag}{gaps}{failed}{note}"
            )

        if self.miss_kinds:
            lines += ["", "MISSED items, diagnosed (a boundary miss is not an extraction miss):"]
            for item_id, kinds in sorted(self.miss_kinds.items()):
                lines.append(f"    {item_id}: {kinds}")

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
    short_run_reasons: dict[str, str] | None = None,
    failed_clauses: dict[str, Sequence[str]] | None = None,
) -> Report:
    """`short_run_reasons` maps item_id -> why that item has fewer runs (G5).
    An item scored over fewer runs than the set's maximum WITHOUT a reason is a
    programming error, not a reportable state: section 6.1 admits a short run only
    when the provider refused the request, and an unexplained one means the driver
    silently dropped a run. It raises rather than rendering an unexplained gap."""
    reasons = dict(short_run_reasons or {})
    failed = dict(failed_clauses or {})
    report = Report(provenance=dict(provenance or {}))
    top = max((len(o) for o in per_item_runs.values()), default=0)
    for item_id, outcomes in sorted(per_item_runs.items()):
        if len(outcomes) < top and not reasons.get(item_id):
            raise ValueError(
                f"item {item_id} was scored over {len(outcomes)} run(s) against a set maximum "
                f"of {top}, with no reason given. Section 6.1 requires the reason stated "
                "inline wherever the figure appears; an unexplained short run means a run was "
                "dropped, which is a bug rather than a caveat."
            )
        modal, unstable = modal_outcome(outcomes)
        gold = gold_by_id[item_id]
        report.items.append(
            ItemReport(
                item_id=item_id,
                known_gaps=tuple(gold.get("known_gaps", ())),
                outcomes=tuple(outcomes),
                modal=modal,
                unstable=unstable,
                failed_clauses=tuple(failed.get(item_id, ())),
                short_run_reason=reasons.get(item_id, ""),
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
