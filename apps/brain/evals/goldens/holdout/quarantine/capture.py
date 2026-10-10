"""What rejects C04-03, C04-15, C17-03 -- the three EXTRACTED_THEN_QUARANTINED
in-force items (README.md in this directory). Replay only; ZERO SPEND.

Preserved rather than described, so the 9-of-9 UNMAPPABLE_TEMPORAL /
REPAIR_MADE_NO_PROGRESS result can be reproduced instead of taken on trust.
Run from the repo root with DATABASE_URL set:

    uv run --project apps/brain python \
      apps/brain/evals/goldens/holdout/quarantine/capture.py out.json


GATE: the quarantined-span count per (segment, run) must reproduce the
quarantined_spans the scorer itself already derives, or nothing below is read.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, "apps/brain"); sys.path.insert(0, "apps/brain/evals")
from evals.harness import run_scoring

TARGETS = {"C04-087": "C04-03", "C04-017": "C04-15", "C17-006": "C17-03"}
CAP = []
_orig = run_scoring.replay_segment

def wrapped(segment_id, segment_text, run, **k):
    from obligo_brain.graphs.pipeline import run_pipeline
    from obligo_brain.platform.tenancy.context import TenantContext
    from evals.harness import cassette as cassette_mod
    from uuid import UUID
    if segment_id not in TARGETS:
        return _orig(segment_id, segment_text, run, **k)
    cas = cassette_mod.load(segment_id, run, root=k.get("root"))
    player = cassette_mod.StrictPlayer(cas)
    chat = cassette_mod.chat_model_for(player)
    TenantContext.set(UUID(k["org_id"]))
    try:
        res = run_pipeline(k["segment_uuid"], k["org_id"], chat_model=chat)
    finally:
        TenantContext.clear()
    player.assert_fully_consumed()
    CAP.append(dict(
        segment=segment_id, item=TARGETS[segment_id], run=run,
        n_typechecked=len(res.typechecked),
        quarantined=[dict(
            span=[q.candidate.source.char_start, q.candidate.source.char_end],
            cause=q.cause.value, failure_reason=q.failure_reason,
            failure_detail=q.failure_detail, attempts=q.attempts,
            repair_calls=list(q.repair_calls),
            temporal_raw=q.candidate.llm_candidate.temporal_raw,
            action=q.candidate.llm_candidate.action,
            modality=q.candidate.llm_candidate.modality,
            object_raw=getattr(q.candidate.llm_candidate, "object_raw_text", None),
            conditions=list(getattr(q.candidate.llm_candidate, "condition_raws", []) or []),
            tier=q.candidate.grounding_tier.value,
            span_text=q.candidate.llm_candidate.span_text[:220],
        ) for q in res.quarantined],
        rejected=[dict(reason=r.reason.value, detail=r.detail[:300]) for r in res.rejected],
    ))
    return run_scoring.SegmentRun(
        segment_id=segment_id, run=run, typechecked=list(res.typechecked),
        n_rejected=len(res.rejected), n_quarantined=len(res.quarantined),
        quarantined_spans=[(q.candidate.source.char_start, q.candidate.source.char_end)
                           for q in res.quarantined])

run_scoring.replay_segment = wrapped
rep, _c, _co = run_scoring.run(model_id="openai/gpt-oss-120b", verbose=False)
assert list(rep.criterion2_no_known_gaps) == [6, 18], f"GATE FAILED {rep.criterion2_no_known_gaps}"
print("GATE PASS: in-force still 6/18 under instrumentation")
Path(sys.argv[1]).write_text(json.dumps(CAP, indent=1))
print("WROTE", sys.argv[1], "rows", len(CAP))
