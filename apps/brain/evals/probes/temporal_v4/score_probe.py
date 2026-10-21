"""Score the F34 temporal-interaction probe against PREREGISTRATION.md's buckets.

Replay only -- ZERO spend. Cassettes are read with plain `json.loads` (no
`cassette.verify()`), which is why the control arm's `v0.66` stamp against the
targets' `v0.68` is provenance here and not a staleness fault.

THE PREDICATE IS CANDIDATE-LEVEL, AND THE REASON IS F37: `C04-14` and `C04-15`
have byte-identical gold spans `[23:363]`, and `align()` reads no item content,
so an item-level predicate at that segment would measure a pairing accident.

CONTROL IS SCORED FIRST, per the approval. It costs nothing and it is a gate on
this instrument: if the control cannot be computed correctly from committed
data, the scorer is wrong before any live result is read.
"""
from __future__ import annotations

import json
import pathlib
import sys
from uuid import UUID

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "apps/brain"))
sys.path.insert(0, str(ROOT / "apps/brain/src"))

from evals.harness import cassette as cassette_mod  # noqa: E402
from evals.harness import fixtures  # noqa: E402

GOLD = ROOT / "apps/brain/evals/cassettes/gold"
COND = ROOT / "apps/brain/evals/probes/conditions_v4"

# (label, segment, doc, cassette dir). Control first.
# CONTROL arms are scored by PREREGISTRATION.md §5's OWN criterion, not by §3's
# target buckets. A first version of this module pushed the control through the
# target bucket set and returned `OTHER` 3/3 for a candidate that had in fact
# compiled with its temporal intact -- i.e. for a CONTROL HOLDS. The
# control-first gate caught it at ZERO spend, which is what that gate is for.
CONTROL_ARMS = [
    ("CONTROL  v3 x C11-094 (baseline)", "C11-094", "C11", GOLD / "C11-094"),
    ("CONTROL  v4 x C11-094", "C11-094", "C11", COND / "v4" / "C11-094"),
]

ARMS = [
    ("baseline v3 x C17-006", "C17-006", "C17", GOLD / "C17-006"),
    ("baseline v3 x C04-017", "C04-017", "C04", GOLD / "C04-017"),
    ("TARGET   v4 x C17-006", "C17-006", "C17", HERE / "v4" / "C17-006"),
    ("TARGET   v4 x C04-017", "C04-017", "C04", HERE / "v4" / "C04-017"),
]

# Worst-first, for §6.1's tie rule: ties resolve AGAINST the flip.
ORDER = ["OTHER", "NOT_EXTRACTED", "SPAN_NOT_FOUND", "DROPPED_AND_FAILED_OTHERWISE",
         "ABSORBED", "NARROWED_STILL_UNMAPPABLE", "QUARANTINED_SAME",
         "DROPPED_AND_COMPILED"]


def gold_items(segment_id: str) -> list[dict]:
    out = []
    for f in sorted((ROOT / "apps/brain/evals/goldens").glob("batch*/items/*.json")):
        j = json.loads(f.read_text())
        if j["segment_id"] == segment_id:
            out.append(j)
    return out


def iou(a, b) -> float:
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    inter = max(0, hi - lo)
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union else 0.0


def classify(q_or_t, temporal_raw, conditions, during_phrase_seen) -> tuple[str, str]:
    """PREREGISTRATION.md §3's buckets, for ONE candidate."""
    kind, detail = q_or_t
    has_temporal = bool(temporal_raw and str(temporal_raw).strip())
    if kind == "typechecked":
        if not has_temporal:
            return "DROPPED_AND_COMPILED", f"compiled with temporal_raw={temporal_raw!r}"
        return "OTHER", f"compiled WITH a temporal: {temporal_raw!r}"
    if kind == "quarantined":
        if has_temporal:
            from obligo_brain.compiler.ir_compile import _classify_temporal
            if _classify_temporal(str(temporal_raw)) is None:
                if during_phrase_seen:
                    return "QUARANTINED_SAME", f"{detail}; temporal_raw={temporal_raw!r}"
                return "NARROWED_STILL_UNMAPPABLE", f"{detail}; temporal_raw={temporal_raw!r}"
            return "OTHER", f"{detail}; classifiable temporal {temporal_raw!r}"
        if any("during" in str(c).lower() for c in (conditions or [])):
            return "ABSORBED", f"phrase in condition_raws={conditions!r}"
        return "DROPPED_AND_FAILED_OTHERWISE", f"{detail}; no temporal_raw"
    if kind == "rejected":
        return ("SPAN_NOT_FOUND" if "SPAN_NOT_FOUND" in detail else "OTHER"), detail
    return "NOT_EXTRACTED", "no candidate at the span"


def modal(verdicts: list[str]) -> tuple[str, str]:
    if not verdicts:
        return "NO RUNS", "nothing recorded"
    counts = {v: verdicts.count(v) for v in set(verdicts)}
    top = max(counts.values())
    winners = [v for v, n in counts.items() if n == top]
    if len(winners) > 1:
        worst = min(winners, key=lambda v: ORDER.index(v) if v in ORDER else 0)
        return worst, f"TIE {counts} -> worst/least-favourable (§6.1), UNSTABLE"
    unstable = "" if top == len(verdicts) else f" UNSTABLE {counts}"
    return winners[0], f"{top}/{len(verdicts)}{unstable}"


def score_arm(label, segment_id, doc, cdir, fx) -> dict:
    print(f"\n{'='*78}\n{label}   ({cdir})\n{'='*78}")
    if not cdir.is_dir():
        print("  no cassettes"); return {"label": label, "modal": "NO RUNS", "runs": []}
    items = gold_items(segment_id)
    gold_spans = [(i["item_id"], i["span_char_start"], i["span_char_end"]) for i in items]
    print(f"  gold items: {[(i, s, e) for i, s, e in gold_spans]}")

    from obligo_brain.graphs.pipeline import run_pipeline
    from obligo_brain.platform.tenancy.context import TenantContext

    verdicts, rows = [], []
    for run in (1, 2, 3):
        p = cdir / f"run{run}.json"
        if not p.exists():
            print(f"  run{run}: NO CASSETTE"); continue
        # cassette_mod.load() does NOT verify -- verify() is a separate method -- so
        # the control arm's v0.66 stamp is read without a staleness check, by design.
        cas = cassette_mod.load(segment_id, run, root=cdir.parent)
        player = cassette_mod.StrictPlayer(cas)
        chat = cassette_mod.chat_model_for(player)
        TenantContext.set(UUID(str(fx[doc].org_id)))
        try:
            res = run_pipeline(str(fx[doc].segment_uuids[segment_id]),
                               str(fx[doc].org_id), chat_model=chat)
        finally:
            TenantContext.clear()

        cands = []
        for t in res.typechecked:
            cands.append(("typechecked", "", t.source.char_start, t.source.char_end, t))
        for q in res.quarantined:
            cands.append(("quarantined", f"{q.cause.value}/{q.failure_reason}",
                          q.candidate.source.char_start, q.candidate.source.char_end, q))
        for r in res.rejected:
            cands.append(("rejected", f"{r.reason.value}", None, None, r))

        # best candidate per gold span; candidate-level, F37-proof
        best = None
        for kind, detail, cs, ce, obj in cands:
            if cs is None:
                score = -1.0
            else:
                score = max(iou((cs, ce), (s, e)) for _, s, e in gold_spans)
            if best is None or score > best[0]:
                best = (score, kind, detail, obj)
        if best is None:
            v, why, traw, conds = "NOT_EXTRACTED", "no candidates at all", None, None
        else:
            score, kind, detail, obj = best
            if kind == "typechecked":
                llm = None
                traw = None
                conds = None
                # the compiled obligation carries no raw text; read the cassette
                traw, conds = raw_fields_for(cas, (obj.source.char_start, obj.source.char_end))
            elif kind == "quarantined":
                llm = obj.candidate.llm_candidate
                traw, conds = llm.temporal_raw, list(llm.condition_raws or [])
            else:
                llm = obj.llm_candidate
                traw = getattr(llm, "temporal_raw", None) if llm else None
                conds = list(getattr(llm, "condition_raws", []) or []) if llm else []
            during = bool(traw) and "during" in str(traw).lower()
            v, why = classify((kind, detail), traw, conds, during)
        verdicts.append(v)
        rows.append({"run": run, "bucket": v, "why": why, "temporal_raw": traw,
                     "conditions": conds, "iou": None if best is None else round(best[0], 3),
                     "n_typechecked": len(res.typechecked),
                     "n_quarantined": len(res.quarantined),
                     "n_rejected": len(res.rejected)})
        print(f"  run{run}: {v:28} temporal_raw={traw!r}")
        print(f"          {why[:150]}")
    m, note = modal(verdicts)
    print(f"  --> MODAL: {m}   ({note})")
    return {"label": label, "segment": segment_id, "modal": m, "note": note, "runs": rows}


def raw_fields_for(cas, span) -> tuple:
    """temporal_raw / condition_raws from the cassette for the candidate at `span`."""
    for r in cas.responses:
        content = r["json"]["choices"][0]["message"]["content"]
        try:
            obj = json.loads(content)
        except Exception:
            continue
        for o in obj.get("obligations", []) or []:
            if isinstance(o, dict):
                return o.get("temporal_raw"), list(o.get("condition_raws") or [])
    return None, []


def score_control(label, segment_id, doc, cdir, fx) -> dict:
    """PREREGISTRATION.md §5: retains a non-empty `temporal_raw` AND its clause-6
    outcome matches the `v3` arm's, on >=2 of 3 runs.

    Clause 6 is computed with the HARNESS's own canonicalisers rather than
    re-implemented, so "clause 6" here means exactly what it means in scoring.
    """
    from evals.harness.score import _canonical_gold_temporal, _canonical_temporal
    from obligo_brain.graphs.pipeline import run_pipeline
    from obligo_brain.platform.tenancy.context import TenantContext

    print(f"\n{'='*78}\n{label}   ({cdir})\n{'='*78}")
    if not cdir.is_dir():
        print("  no cassettes"); return {"label": label, "runs": []}
    gold = [i for i in gold_items(segment_id) if i["item_id"] == "C11-01"]
    assert len(gold) == 1, "control expects exactly one C11-01 gold item"
    g = gold[0]
    gspan = (g["span_char_start"], g["span_char_end"])
    g_t = _canonical_gold_temporal(g.get("temporal"))
    print(f"  control item C11-01 span={gspan} gold temporal={g_t}")

    rows = []
    for run in (1, 2, 3):
        p = cdir / f"run{run}.json"
        if not p.exists():
            print(f"  run{run}: NO CASSETTE"); continue
        cas = cassette_mod.load(segment_id, run, root=cdir.parent)
        player = cassette_mod.StrictPlayer(cas)
        chat = cassette_mod.chat_model_for(player)
        TenantContext.set(UUID(str(fx[doc].org_id)))
        try:
            res = run_pipeline(str(fx[doc].segment_uuids[segment_id]),
                               str(fx[doc].org_id), chat_model=chat)
        finally:
            TenantContext.clear()
        best, best_iou = None, -1.0
        for t in res.typechecked:
            v = iou((t.source.char_start, t.source.char_end), gspan)
            if v > best_iou:
                best, best_iou = t, v
        if best is None:
            rows.append({"run": run, "compiled": False, "retained": False,
                         "clause6": None, "iou": None})
            print(f"  run{run}: NOT COMPILED at the control span")
            continue
        traw, _ = raw_fields_for(cas, (best.source.char_start, best.source.char_end))
        p_t = _canonical_temporal(best.temporal)
        clause6 = (g_t == p_t)
        retained = bool(traw and str(traw).strip())
        rows.append({"run": run, "compiled": True, "retained": retained,
                     "clause6": clause6, "iou": round(best_iou, 3),
                     "temporal_raw": traw, "pred_temporal": p_t})
        print(f"  run{run}: compiled iou={best_iou:.3f} retained={retained} "
              f"clause6={clause6}")
        print(f"          temporal_raw={traw!r}")
    return {"label": label, "segment": segment_id, "runs": rows}


def control_verdict(v3: dict, v4: dict) -> tuple[str, str]:
    """§5's two-sided criterion, evaluated across the two control arms."""
    c6_v3 = [r["clause6"] for r in v3["runs"] if r.get("compiled")]
    base = (sum(1 for x in c6_v3 if x) >= 2) if c6_v3 else None
    ok = 0
    for r in v4["runs"]:
        if r.get("compiled") and r.get("retained") and r.get("clause6") == base:
            ok += 1
    n = len([r for r in v4["runs"] if True])
    verdict = "CONTROL HOLDS" if ok >= 2 else "CONTROL FAILS"
    return verdict, (f"{ok}/{n} v4 runs retain temporal_raw AND match the v3 clause-6 "
                     f"outcome (v3 clause6 passes on >=2 of 3: {base})")


def main() -> int:
    per_doc: dict[str, list] = {}
    import importlib.util
    spec = importlib.util.spec_from_file_location("corpus", ROOT / "apps/brain/evals/corpus.py")
    c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    man = json.loads((ROOT / "docs/eval/corpus_manifest.json").read_text())
    pool = c.build_pool(ROOT / ".corpus", man)
    assert len(pool) == 1547, f"POOL GATE FAILED: {len(pool)}"
    texts = {s["segment_id"]: s["text"] for s in pool}
    for _, seg, doc, _ in CONTROL_ARMS + ARMS:
        per_doc.setdefault(doc, [])
        if seg not in [s for s, _ in per_doc[doc]]:
            per_doc[doc].append((seg, texts[seg]))

    out, ctrl = [], []
    with fixtures.document_fixtures(per_doc) as fx:
        # CONTROL FIRST, per the approval: it costs nothing and it gates the
        # instrument before any live result is read.
        for label, seg, doc, cdir in CONTROL_ARMS:
            ctrl.append(score_control(label, seg, doc, cdir, fx))
        cverdict, cnote = control_verdict(ctrl[0], ctrl[1])
        print(f"\n  ==> {cverdict}   ({cnote})")
        for label, seg, doc, cdir in ARMS:
            out.append(score_arm(label, seg, doc, cdir, fx))

    # §4's threshold, applied to the arms just scored. The verdict is WRITTEN TO
    # THE ARTIFACT and not merely printed: the first version of this scorer
    # persisted `control_verdict` and left the hazard verdict on stdout, so
    # verifying the headline result from the committed file meant re-deriving it
    # by hand. An artifact that omits its own conclusion is not a record of it.
    tgt = [r["modal"] for r in out if r["label"].startswith("TARGET")]
    if tgt and all(m != "NO RUNS" for m in tgt):
        if any(m == "DROPPED_AND_COMPILED" for m in tgt):
            v = "CONFIRMED"
        elif all(m == "QUARANTINED_SAME" for m in tgt):
            v = "REFUTED"
        else:
            v = "INDETERMINATE"
    else:
        v = "NOT YET MEASURED (targets unrecorded)"

    (HERE / "_scored.json").write_text(json.dumps(
        {"control": ctrl, "control_verdict": [cverdict, cnote],
         "arms": out, "hazard_verdict": v,
         "hazard_verdict_basis": {r["segment"]: r["modal"] for r in out
                                  if r["label"].startswith("TARGET")}},
        indent=1, default=str))
    print(f"\n{'='*78}\nSUMMARY\n{'='*78}")
    print(f"  {'CONTROL (§5)':26} -> {cverdict}  ({cnote})")
    for r in out:
        print(f"  {r['label']:26} -> {r['modal']}  ({r.get('note','')})")
    print(f"  {'HAZARD VERDICT (§4)':26} -> {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
