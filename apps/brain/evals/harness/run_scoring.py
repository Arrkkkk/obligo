"""The scoring driver: replays the recorded cassettes and produces section 9's report.

This is the module that turns evidence into a published number, so it is
committed, tested harness code rather than a run script -- section 21 R3's
"a published number without its registry is not reproducible" applies to the
code computing the number no less than to the data behind it.

WHAT IT READS. The locked gold items (goldens/*/items/*.json, each carrying its
own segment_text), the per-document scoring registries, the recorded cassettes,
and goldens/*/segments/*.json for NOT_ANNOTATABLE spans. It seeds one real
Postgres org PER SOURCE DOCUMENT (section 21 R1) and runs the real pipeline.

WHAT IT SPENDS. Nothing. Every model response is replayed from a cassette
through StrictPlayer, so a scoring run is repeatable and offline apart from the
database.

FIVE THINGS ARE WIRED EXPLICITLY HERE BECAUSE EACH IS A WAY THIS COULD QUIETLY
LIE:

W1 -- ONLY `typechecked` OBLIGATIONS ARE PREDICTIONS. `quarantined` and
`rejected` candidates never become an ast.Obligation, so a gold item with no
aligned typechecked obligation is MISSED, never UNEXPECTED and never silently
dropped from the denominator. Counting a quarantined candidate as a prediction
would invent a false positive; dropping the gold item would inflate the rate.

W2 -- SPAN OFFSETS ARE SEGMENT-RELATIVE ON BOTH SIDES. graphs/extraction.py
guarantees the stored span is always segment.text[char_start:char_end], and gold
stores span_char_start/end into the same segment text. Verified before this
module was written rather than assumed; a coordinate mismatch here would silently
zero every IoU and read as total extraction failure.

W3 -- SHORT RUNS CARRY THEIR REASON (section 6.1). An item whose segment has
fewer than the set's maximum recorded runs is scored over the runs that exist and
its reason is threaded into the report, which refuses to render an unexplained
short run at all.

W4 -- CRITERION 2's DUAL DENOMINATOR PASSES THROUGH UNTOUCHED. report.py's G3
owns that labelling. This module computes neither figure itself and must never
"helpfully" pick one.

W5 -- COMPILE SUCCESS HERE IS *NOT* CRITERION 1b. 1b is defined over the
28-document dev corpus; this runs over the 12 gold segments. The figure is
computed because it is free and diagnostic, and is labelled at every point of
use so it cannot be quoted as 1b.
"""

from __future__ import annotations

import glob
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence
from uuid import UUID

from evals.harness import cassette as cassette_mod
from evals.harness import align as align_mod
from evals.harness import conditions as conditions_mod
from evals.harness import fixtures as fixtures_mod
from evals.harness import registry as registry_mod
from evals.harness import report as report_mod
from evals.harness import score as score_mod
from evals.harness.score import Outcome

EVALS_DIR = Path(__file__).resolve().parent.parent
GOLDENS_DIR = EVALS_DIR / "goldens"

# Why C17-021 has two runs and not three. Threaded into the report per section 6.1
# rather than left to a reader to discover; see CLAUDE.md's named-failure-mode entry.
SHORT_RUN_REASONS = {
    "C17-021": (
        "run 3 unobtainable -- openai/gpt-oss-120b returns HTTP 400 json_validate_failed "
        "with an empty failed_generation on this segment, reproduced 3x (§6.1)"
    ),
}


@dataclass
class SegmentRun:
    segment_id: str
    run: int
    typechecked: list = field(default_factory=list)
    n_rejected: int = 0
    n_quarantined: int = 0
    # Spans of candidates that were extracted and grounded but never compiled.
    # Carried so a MISSED can distinguish "nothing was extracted here" from
    # "the right clause WAS extracted here and the compiler rejected it" -- see W6.
    quarantined_spans: list = field(default_factory=list)
    # NOTE: there is deliberately no `rejected_spans`. A candidate rejected AT
    # grounding has no char offsets at all -- grounding is the stage that assigns
    # them -- so there is no span to compare. RejectedCandidate carries
    # `llm_candidate`, not a grounded `candidate`, which is the same fact in the
    # type system.


def load_gold_items(goldens_dir: Path = GOLDENS_DIR) -> list[dict]:
    return [json.loads(Path(p).read_text())
            for p in sorted(glob.glob(str(goldens_dir / "*/items/*.json")))]


def load_not_annotatable(goldens_dir: Path = GOLDENS_DIR) -> dict[str, list[tuple[int, int]]]:
    """Section 21 R6. Present for 1 of 12 segments today; absent is not an error,
    it is the known one-directional UNEXPECTED over-count report.py already caveats."""
    out: dict[str, list[tuple[int, int]]] = {}
    for p in sorted(glob.glob(str(goldens_dir / "*/segments/*.json"))):
        d = json.loads(Path(p).read_text())
        out[d["segment_id"]] = [
            (int(s["span_char_start"]), int(s["span_char_end"]))
            for s in d.get("not_annotatable", [])
        ]
    return out


def segments_from_items(items: Sequence[dict]) -> dict[str, tuple[str, str]]:
    """segment_id -> (doc_id, segment_text), with disagreement treated as fatal."""
    out: dict[str, tuple[str, str]] = {}
    for it in items:
        sid, doc, text = it["segment_id"], it["doc_id"], it["segment_text"]
        if sid in out and out[sid][1] != text:
            raise ValueError(
                f"two gold items disagree on {sid}'s segment_text; scoring cannot "
                "proceed against an ambiguous input"
            )
        out[sid] = (doc, text)
    return out


def available_runs(segment_id: str, segment_text: str, *, model_id: str,
                   prompt_version: str, guideline_version: str,
                   max_runs: int = 3, root: Path | None = None) -> list[int]:
    """Run numbers with a cassette that EXISTS AND VERIFIES. A stale cassette is
    not silently treated as a missing run -- it propagates, because replaying it
    would answer a question that was never asked."""
    out = []
    for run in range(1, max_runs + 1):
        try:
            c = cassette_mod.load(segment_id, run, root=root)
        except cassette_mod.CassetteMissing:
            continue
        c.verify(segment_text=segment_text, model_id=model_id,
                 prompt_version=prompt_version, guideline_version=guideline_version)
        out.append(run)
    return out


def replay_segment(segment_id: str, segment_text: str, run: int, *,
                   segment_uuid: str, org_id: str, root: Path | None = None) -> SegmentRun:
    """One cassette -> one pipeline execution. Strict in both directions."""
    from obligo_brain.graphs.pipeline import run_pipeline
    from obligo_brain.platform.tenancy.context import TenantContext

    cas = cassette_mod.load(segment_id, run, root=root)
    player = cassette_mod.StrictPlayer(cas)
    chat = cassette_mod.chat_model_for(player)
    TenantContext.set(UUID(org_id))
    try:
        result = run_pipeline(segment_uuid, org_id, chat_model=chat)
    finally:
        TenantContext.clear()
    player.assert_fully_consumed()
    return SegmentRun(
        segment_id=segment_id, run=run, typechecked=list(result.typechecked),
        n_rejected=len(result.rejected), n_quarantined=len(result.quarantined),
        quarantined_spans=[(q.candidate.source.char_start, q.candidate.source.char_end)
                           for q in result.quarantined],
    )


def score_segment_run(
    sr: SegmentRun,
    gold_for_segment: Sequence[dict],
    reg: registry_mod.DocumentRegistry,
    segment_text: str,
    not_annotatable: Sequence[tuple[int, int]] = (),
) -> tuple[dict[str, score_mod.ItemScore], list[report_mod.UnscoreableCandidate]]:
    """Aligns this run's predictions to gold, then scores each aligned pair.

    W1: only sr.typechecked are predictions. A gold item left unaligned is MISSED.
    """
    gold_spans = [(int(g["span_char_start"]), int(g["span_char_end"])) for g in gold_for_segment]
    gold_ids = [g["item_id"] for g in gold_for_segment]
    preds = sr.typechecked
    pred_spans = [(p.source.char_start, p.source.char_end) for p in preds]   # W2

    alignment = align_mod.align(
        gold_spans, pred_spans, gold_ids=gold_ids, not_annotatable=not_annotatable
    )

    scores: dict[str, score_mod.ItemScore] = {}
    for pair in alignment.pairs:
        gold = gold_for_segment[pair.gold_index]
        scores[gold["item_id"]] = score_mod.score_item(gold, preds[pair.pred_index], reg)

    for gi in alignment.missed_gold:      # W1
        gold = gold_for_segment[gi]
        # W6: a MISSED must say WHICH KIND of missed it is. "No prediction at all"
        # (extraction produced nothing here) and "a prediction whose boundary fell
        # below IoU 0.5" are different failures with different fixes, and collapsing
        # them into one label hides a granularity mismatch as an extraction failure.
        # Measured on the first real run: the model emits systematically WIDER spans
        # than gold annotates (C22-01 gold [22:128] vs predicted [22:529] -- identical
        # start, 4x the length), so this distinction is load-bearing, not hypothetical.
        best_iou, best_span = 0.0, None
        for span in pred_spans:
            v = align_mod.iou((int(gold["span_char_start"]), int(gold["span_char_end"])), span)
            if v > best_iou:
                best_iou, best_span = v, span
        if best_span is None:
            # W6, refined: "nothing was extracted here" and "the clause WAS extracted
            # here, correctly, and the COMPILER rejected it" are different failures
            # pointing at different stages -- extraction quality versus a compile-stage
            # gap such as _WITHIN_RE's preposition requirement. Collapsing them reads
            # every compile failure as an extraction miss. Measured: C17-02's gold span
            # is [37:386] and the quarantined candidate's was [37:510] -- the SAME start
            # offset -- so calling that "not extracted" was actively misleading.
            q_iou, q_span = 0.0, None
            for span in sr.quarantined_spans:
                v = align_mod.iou(
                    (int(gold["span_char_start"]), int(gold["span_char_end"])), span)
                if v > q_iou:
                    q_iou, q_span = v, span
            if q_span is not None:
                kind = "EXTRACTED_THEN_QUARANTINED"
                why = (f"{kind} -- no TYPECHECKED obligation overlaps, but a grounded "
                       f"candidate at [{q_span[0]}:{q_span[1]}] (IoU {q_iou:.2f} with gold) "
                       "was quarantined. The clause was found and grounded; the COMPILER "
                       "rejected it, so this is a compile-stage failure, not an extraction miss")
                scores[gold["item_id"]] = score_mod.ItemScore(
                    item_id=gold["item_id"], outcome=Outcome.MISSED, clauses={},
                    detail={"alignment": why, "miss_kind": kind, "best_iou": f"{q_iou:.3f}"},
                )
                continue
            why = (f"NOT_EXTRACTED -- {len(preds)} typechecked obligation(s) on this segment "
                   f"and none of its {len(sr.quarantined_spans)} quarantined candidate(s) "
                   "overlaps this gold span either; nothing was extracted here at all")
        else:
            why = (f"BELOW_IOU_THRESHOLD -- best overlapping prediction "
                   f"[{best_span[0]}:{best_span[1]}] at IoU {best_iou:.2f} < 0.50 "
                   f"(gold [{gold['span_char_start']}:{gold['span_char_end']}]); the clause may "
                   "be extracted at a different granularity rather than missed")
        scores[gold["item_id"]] = score_mod.ItemScore(
            item_id=gold["item_id"], outcome=Outcome.MISSED, clauses={},
            detail={"alignment": (
                f"{why}. This run: {len(preds)} typechecked, {sr.n_quarantined} quarantined, "
                f"{sr.n_rejected} rejected at grounding"
            ), "miss_kind": "NOT_EXTRACTED" if best_span is None
               else "BELOW_IOU_THRESHOLD",
               "best_iou": f"{best_iou:.3f}"},
        )

    unexpected = [
        report_mod.UnscoreableCandidate(
            run=sr.run, segment_id=sr.segment_id,
            char_start=pred_spans[pi][0], char_end=pred_spans[pi][1],
            span_text=segment_text[pred_spans[pi][0]:pred_spans[pi][1]],
        )
        for pi in alignment.unexpected_pred
    ]
    return scores, unexpected


def compile_success_not_criterion_1b(runs: Sequence[SegmentRun]) -> dict:
    """W5. Deliberately named so it cannot be quoted as criterion 1b by accident."""
    tc = sum(len(r.typechecked) for r in runs)
    q = sum(r.n_quarantined for r in runs)
    rej = sum(r.n_rejected for r in runs)
    grounded = tc + q
    return {
        "label": ("NOT criterion 1b -- 12 gold segments, not the 28-document dev corpus. "
                  "Criterion 1b remains Unmeasured."),
        "typechecked": tc, "quarantined": q, "rejected_at_grounding": rej,
        "compiled_over_grounded": (f"{tc}/{grounded} = {tc / grounded * 100:.1f}%"
                                   if grounded else "n/a"),
    }


def guideline_version_from_items(items: Sequence[dict]) -> str:
    """The version the ITEMS stamp -- never the guideline file's current header.

    These diverge legitimately. Cassettes record the guideline version in force when
    they were recorded (v0.28, the version all 18 conformed items stamp), while the
    document has since moved to v0.30. Both v0.29 and v0.30 changed NO annotation
    rule -- v0.29 added section 6.1's reporting exception, v0.30 reconciled its tie
    clause with G2 -- so no recorded response answers a different question and the
    cassettes are not stale. Reading the stamp from the items is what keeps that
    true by construction: the day an amendment DOES change an annotation rule, the
    conforming pass restamps the items, this returns the new version, and every
    cassette correctly goes stale at once.
    """
    stamps = {it["guideline_version"] for it in items}
    if len(stamps) != 1:
        raise ValueError(
            f"gold items stamp {len(stamps)} different guideline versions ({sorted(stamps)}); "
            "section 10's conforming pass must run before they can be scored as one set"
        )
    return stamps.pop()


def active_prompt_version() -> str:
    """Whatever registry.yaml currently points `extraction` at.

    Read through obligo_brain's own loader rather than by re-parsing the YAML at a
    hand-built path: a second reader of the same file is exactly the bypassable
    indirection CLAUDE.md's debt list records three instances of, and the first
    draft of this function did get the relative path wrong.
    """
    from obligo_brain.prompts import registry as prompt_registry
    return prompt_registry.load("extraction").version


def run(*, model_id: str, guideline_version: str | None = None,
        prompt_version: str | None = None,
        goldens_dir: Path = GOLDENS_DIR, cassette_root: Path | None = None,
        verbose: bool = True) -> tuple[report_mod.Report, str, dict]:
    """The whole scoring pass. Returns (report, condition-check rendering, compile stats)."""
    prompt_version = prompt_version or active_prompt_version()
    items = load_gold_items(goldens_dir)
    guideline_version = guideline_version or guideline_version_from_items(items)
    segments = segments_from_items(items)
    not_annotatable = load_not_annotatable(goldens_dir)

    by_segment: dict[str, list[dict]] = {}
    for it in items:
        by_segment.setdefault(it["segment_id"], []).append(it)

    per_doc: dict[str, list[tuple[str, str]]] = {}
    for sid, (doc, text) in sorted(segments.items()):
        per_doc.setdefault(doc, []).append((sid, text))

    # R5 first: a registry-fixture defect must fail loudly, never as a clause-8 loss.
    from evals.harness import selfcheck
    blocking = [f for f in selfcheck.run(goldens_dir) if "non-blocking" not in f.kind]
    if blocking:
        raise RuntimeError(
            "R5 self-check failed; refusing to score. "
            + "; ".join(str(f) for f in blocking)
        )

    per_item_runs: dict[str, list[Outcome]] = {}
    failed_clauses: dict[str, list[str]] = {}
    miss_kinds: dict[str, list[str]] = {}
    unexpected: list[report_mod.UnscoreableCandidate] = []
    all_runs: list[SegmentRun] = []
    short_run_reasons: dict[str, str] = {}
    runs_by_segment: dict[str, list[int]] = {}

    with fixtures_mod.document_fixtures(per_doc) as fx_by_doc:
        seg_to: dict[str, tuple[str, str]] = {}
        for doc, fx in fx_by_doc.items():
            for cid, u in fx.segment_uuids.items():
                seg_to[cid] = (u, fx.org_id)

        for sid in sorted(segments):
            doc, text = segments[sid]
            runs = available_runs(sid, text, model_id=model_id, prompt_version=prompt_version,
                                  guideline_version=guideline_version, root=cassette_root)
            runs_by_segment[sid] = runs
            if not runs:
                raise RuntimeError(f"segment {sid} has no usable cassette; cannot score it")
            reg = registry_mod.load(doc)
            seg_uuid, org_id = seg_to[sid]
            for run_no in runs:
                sr = replay_segment(sid, text, run_no, segment_uuid=seg_uuid,
                                    org_id=org_id, root=cassette_root)
                all_runs.append(sr)
                scores, unx = score_segment_run(
                    sr, by_segment[sid], reg, text, not_annotatable.get(sid, ())
                )
                unexpected.extend(unx)
                for item_id, sc in scores.items():
                    per_item_runs.setdefault(item_id, []).append(sc.outcome)
                    if sc.outcome is Outcome.MISSED and "miss_kind" in sc.detail:
                        miss_kinds.setdefault(item_id, []).append(
                            f"run{sr.run}:{sc.detail['miss_kind']}@IoU{sc.detail['best_iou']}")
                    if sc.failed:
                        failed_clauses.setdefault(item_id, [])
                        for c in sc.failed:
                            if c not in failed_clauses[item_id]:
                                failed_clauses[item_id].append(c)
            if verbose:
                print(f"  {sid}: runs={runs} "
                      f"items={[g['item_id'] for g in by_segment[sid]]}", flush=True)

    # W3: thread section 6.1's reason onto every item backed by a short segment.
    top = max((len(v) for v in runs_by_segment.values()), default=0)
    for sid, runs in runs_by_segment.items():
        if len(runs) < top:
            reason = SHORT_RUN_REASONS.get(sid, "")
            if not reason:
                raise RuntimeError(
                    f"segment {sid} has {len(runs)} runs against a set maximum of {top} "
                    "and no recorded reason. Section 6.1 admits a short run only with its "
                    "reason stated; add it to SHORT_RUN_REASONS or re-record."
                )
            for g in by_segment[sid]:
                short_run_reasons[g["item_id"]] = reason

    gold_by_id = {it["item_id"]: it for it in items}
    rep = report_mod.build(
        per_item_runs, gold_by_id,
        unscoreable_candidates=unexpected,
        short_run_reasons=short_run_reasons,
        failed_clauses=failed_clauses,
        provenance={
            "model_id": model_id, "prompt_version": prompt_version,
            "guideline_version": guideline_version,
            "cassettes": sum(len(v) for v in runs_by_segment.values()),
            "segments": len(segments), "items": len(items),
        },
    )
    rep.miss_kinds = miss_kinds

    cassettes_by_segment = {
        sid: [cassette_mod.load(sid, r, root=cassette_root).responses for r in runs]
        for sid, runs in runs_by_segment.items()
    }
    checks, summary = conditions_mod.check(items, cassettes_by_segment)
    return rep, conditions_mod.render(checks, summary), compile_success_not_criterion_1b(all_runs)


def main() -> int:
    import os
    model_id = os.environ.get("EVAL_MODEL_ID", "openai/gpt-oss-120b")
    rep, cond, compile_stats = run(model_id=model_id)
    print("\n" + rep.render())
    print("\n" + "=" * 78 + "\n")
    print(cond)
    print("\n" + "=" * 78 + "\n")
    print("COMPILE SUCCESS OVER THE GOLD SEGMENTS")
    for k, v in compile_stats.items():
        print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
