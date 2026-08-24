"""The `condition_raws` prompt-versus-gold alignment check (CLAUDE.md debt list).

THE QUESTION, which is a fact about model behaviour and settleable no other way.
`prompts/extraction/v3.yaml` asks for `condition_raws` as "a list of literal
**'if'-type** conditional phrases". Across the 18 locked gold items only 2 of 8
condition entries are literally `if`-headed; the other 6 use `upon`, a bare
participial, `As requested by`, `solely to the extent`, and `further provided
that`. Either the model reads "'if'-type" as a CATEGORY (and emits these), or it
reads it NARROWLY (and returns []) -- in which case all 6 become guaranteed
section 5 clause-7 count mismatches attributable to prompt wording rather than to
extraction quality, and invisible without this check.

WHY IT READS CASSETTES AND NOT PipelineResult. By the time text reaches
ast.Obligation.conditions it has passed through ir_compile, which wraps each raw
in an AtomPredicate and can drop candidates entirely. The question is what the
MODEL emitted, so the only honest source is the recorded response itself.
Costs no live call and touches no database.

MULTI-CALL CASSETTES ARE HANDLED, NOT ASSUMED AWAY. A cassette holds one
extraction response (`{"obligations": [...]}`) followed by zero or more repair
responses (`{"repairs": [{"index": N, "<field>": ...}]}`). A repair patches a
candidate by index and CAN in principle target condition_raws, so patches are
applied in order rather than reading response 0 alone. Whether that ever happens
is itself reported (`repairs_touching_conditions`) -- if it never does, that is a
measured fact, not an assumption this module made.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

# Markers the gold set actually uses, beyond a literal leading "if".
NON_IF_MARKERS = ("upon", "as requested", "solely to the extent",
                  "further provided", "provided that", "subject to", "to the extent")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def is_if_headed(text: str) -> bool:
    """Leading token is `if`, punctuation-insensitively.

    The punctuation strip is load-bearing, not defensive: gold's
    `"If, during the Term of this Agreement, ..."` heads with `If,` and a
    naive split()[0] == "if" test reports it as NOT if-headed -- which is
    exactly the trailing/adjacent-punctuation failure class CLAUDE.md's debt
    list already records for regex-anchored classifiers over real quoted text.
    Caught here by reading the classified output rather than the totals
    (Standing Principle 7).
    """
    head = norm(text).split(" ")[0] if norm(text) else ""
    return head.strip(".,;:()\"'").lower() == "if"


@dataclass
class GoldConditionCheck:
    item_id: str
    segment_id: str
    text: str
    if_headed: bool
    exact_emitted_runs: list[int] = field(default_factory=list)
    partial_emitted_runs: list[int] = field(default_factory=list)
    total_runs: int = 0

    @property
    def status(self) -> str:
        if self.exact_emitted_runs:
            return "EMITTED_EXACT"
        if self.partial_emitted_runs:
            return "EMITTED_DIFFERENT_BOUNDARY"
        return "NEVER_EMITTED"


def _candidates_after_repairs(responses: Sequence[dict]) -> tuple[list[dict], int]:
    """Replays a cassette's response list into the candidate state the pipeline
    would have held after repair. Returns (candidates, repairs_touching_conditions)."""
    candidates: list[dict] = []
    touching = 0
    for r in responses:
        try:
            body = json.loads(r["json"]["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if "obligations" in body and isinstance(body["obligations"], list):
            candidates = [dict(c) for c in body["obligations"] if isinstance(c, dict)]
        elif "repairs" in body and isinstance(body["repairs"], list):
            for patch in body["repairs"]:
                if not isinstance(patch, dict):
                    continue
                idx = patch.get("index")
                if not isinstance(idx, int) or not (0 <= idx < len(candidates)):
                    continue
                for k, v in patch.items():
                    if k == "index":
                        continue
                    if k == "condition_raws":
                        touching += 1
                    candidates[idx][k] = v
    return candidates, touching


def emitted_conditions(responses: Sequence[dict]) -> tuple[list[str], int]:
    """Every condition_raws string a cassette's candidates ended up carrying."""
    candidates, touching = _candidates_after_repairs(responses)
    out: list[str] = []
    for c in candidates:
        raws = c.get("condition_raws") or []
        if isinstance(raws, list):
            out.extend(norm(str(x)) for x in raws if str(x).strip())
    return out, touching


def check(
    gold_items: Iterable[dict],
    cassettes_by_segment: dict[str, list[Sequence[dict]]],
) -> tuple[list[GoldConditionCheck], dict[str, Any]]:
    """`cassettes_by_segment` maps segment_id -> [responses per run]."""
    checks: list[GoldConditionCheck] = []
    repairs_touching = 0
    emitted_total = 0
    emitted_non_if = 0

    seen_segments: set[str] = set()
    for seg, runs in cassettes_by_segment.items():
        for responses in runs:
            emitted, touching = emitted_conditions(responses)
            repairs_touching += touching
            emitted_total += len(emitted)
            emitted_non_if += sum(1 for e in emitted if not is_if_headed(e))
        seen_segments.add(seg)

    for item in gold_items:
        seg = item["segment_id"]
        runs = cassettes_by_segment.get(seg, [])
        for text in item.get("conditions", []):
            gc = GoldConditionCheck(
                item_id=item["item_id"], segment_id=seg, text=text,
                if_headed=is_if_headed(text), total_runs=len(runs),
            )
            g = norm(text)
            for run_no, responses in enumerate(runs, start=1):
                emitted, _ = emitted_conditions(responses)
                if any(e == g for e in emitted):
                    gc.exact_emitted_runs.append(run_no)
                elif any(g in e or e in g for e in emitted if e):
                    gc.partial_emitted_runs.append(run_no)
            checks.append(gc)

    summary = {
        "gold_condition_entries": len(checks),
        "gold_if_headed": sum(1 for c in checks if c.if_headed),
        "gold_non_if_headed": sum(1 for c in checks if not c.if_headed),
        "model_condition_strings_emitted": emitted_total,
        "model_emitted_non_if_headed": emitted_non_if,
        "repairs_touching_conditions": repairs_touching,
        "segments_examined": len(seen_segments),
    }
    return checks, summary


def render(checks: Sequence[GoldConditionCheck], summary: dict) -> str:
    lines = [
        "CONDITION_RAWS PROMPT-ALIGNMENT CHECK",
        "    Settles the CLAUDE.md debt item: does the extraction prompt's \"'if'-type\"",
        "    wording cause the model to omit non-'if'-headed conditions the gold set",
        "    annotates? Read from recorded cassettes; no live call, no database.",
        "",
    ]
    for k, v in summary.items():
        lines.append(f"    {k}: {v}")
    lines += ["", "Per gold condition entry:"]
    for c in sorted(checks, key=lambda c: (c.item_id, c.text)):
        head = "IF " if c.if_headed else "non-IF"
        lines.append(
            f"    {c.item_id:8s} {head:6s} {c.status:26s} "
            f"exact={c.exact_emitted_runs} partial={c.partial_emitted_runs}"
            f" /{c.total_runs} runs"
        )
        lines.append(f"             {c.text[:96]!r}")

    non_if = [c for c in checks if not c.if_headed]
    never = [c for c in non_if if c.status == "NEVER_EMITTED"]
    lines += ["", "VERDICT:"]
    if not non_if:
        lines.append("    No non-'if'-headed gold conditions in scope; the question is unasked here.")
    elif len(never) == len(non_if):
        lines.append(
            f"    NARROW READING CONFIRMED -- all {len(non_if)} non-'if'-headed gold conditions "
            "were NEVER emitted.\n"
            "    Per the debt entry the fix is a prompt version bump enumerating the markers,\n"
            "    NOT a change to gold. Not actioned here: this check measures, it does not fix."
        )
    elif not never:
        lines.append(
            f"    CATEGORY READING CONFIRMED -- every one of the {len(non_if)} non-'if'-headed "
            "gold conditions\n    was emitted in at least one run. The prompt wording is loose "
            "but not harmful; no bump needed on this evidence."
        )
    else:
        lines.append(
            f"    MIXED -- {len(never)} of {len(non_if)} non-'if'-headed gold conditions were "
            "never emitted.\n    Neither reading is clean; inspect the per-entry rows above "
            "before proposing a prompt change."
        )
    return "\n".join(lines)
