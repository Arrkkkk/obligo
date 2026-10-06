"""The Tier-B `v4` conditions probe (§10.1 F31(1)).

What could go wrong silently here, each pinned rather than assumed away:

1. **`v4` gets ACTIVATED.** A `prompt_version` flip is Tier C: it stales all 35
   gold cassettes at once and `C17-021` run 3 is unobtainable (§6.1). A test
   asserts `registry.yaml` still reads `extraction: default: v3`.
2. **`v4` quietly changes the model or temperature too.** Then any behavioural
   difference is unattributable to the wording -- exactly the confound v3's own
   header refused ("changing prompt text and model_id in one bump"). Pinned.
3. **The Rule A replay finding rots.** It is the reason Rule A costs zero calls.
   If the cassettes ever stop showing `provided that` on 3 of 3, the probe's
   scope was wrong and must be re-read.
4. **The scorer's predicate drifts.** It is three-valued on purpose, because
   `v3` fails the two pairs by DIFFERENT mechanisms. A boolean predicate would
   reproduce the same PASS/FAIL while losing that, so the baseline is pinned
   mechanism-by-mechanism, not just as "FAIL".

All tests here read committed gold cassettes, the prompt files and the registry.
**None needs `.corpus/` or a database, so all of them run in CI** -- unlike the
probe's own live arm, whose cassettes are recorded under `evals/probes/`.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[4]
PROBE = ROOT / "apps/brain/evals/probes/conditions_v4"
PROMPTS = ROOT / "apps/brain/src/obligo_brain/prompts"
GOLD = ROOT / "apps/brain/evals/cassettes/gold"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, PROBE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def scorer():
    return _load("score_probe")


# --- (1) v4 must NOT be activated -------------------------------------------

def test_v4_is_not_activated_in_the_registry():
    reg = yaml.safe_load((PROMPTS / "registry.yaml").read_text())
    assert reg["extraction"]["environments"]["default"] == "v3", (
        "v4 has been activated. That is a Tier C change: prompt_version is a "
        "Cassette.verify() staleness dimension, so it stales all 35 gold "
        "cassettes at once, and C17-021 run 3 is unobtainable (§6.1). The flip "
        "belongs to the §10 freeze pass."
    )


def test_v4_exists_and_v3_is_untouched():
    v3 = yaml.safe_load((PROMPTS / "extraction/v3.yaml").read_text())
    v4 = yaml.safe_load((PROMPTS / "extraction/v4.yaml").read_text())
    assert v3["version"] == "v3" and v4["version"] == "v4"
    # Prompts are immutable: v3's own text must not have been edited in place.
    assert '"if"-type conditional phrases' in v3["system"], (
        "v3's conditions wording has changed -- prompts are versioned files, "
        "never edited in place"
    )


def test_v4_changes_wording_only_not_the_model_or_temperature():
    """Otherwise a behavioural difference is unattributable to the wording."""
    v3 = yaml.safe_load((PROMPTS / "extraction/v3.yaml").read_text())
    v4 = yaml.safe_load((PROMPTS / "extraction/v4.yaml").read_text())
    assert v4["model_constraints"] == v3["model_constraints"], (
        f"v4 changes model_constraints: {v4['model_constraints']} vs "
        f"{v3['model_constraints']}"
    )
    assert v4["system"] != v3["system"], "v4 is textually identical to v3"


def test_v4s_worked_example_imitates_neither_test_segment():
    """§3.8.2 rejected fitting the prompt to a test item ("fitting the model to
    an accident"). C11-094 pairs `If ...`/`upon ...`; the hold-out E02-010 pairs
    `if ...`/`upon ...` too, so the example must use different markers and
    different content from both."""
    v4 = yaml.safe_load((PROMPTS / "extraction/v4.yaml").read_text())
    sys_text = v4["system"]
    assert "In the event of a recall" in sys_text, "the worked example moved"
    for leaked in ("Principal", "natural person", "mental incapacity",
                   "devise or inheritance", "heir", "MedQuist", "CBay"):
        assert leaked not in sys_text, (
            f"v4's prompt leaks {leaked!r} from a test segment -- the probe would "
            "be measuring imitation rather than the rule"
        )


# --- (3) Rule A's replay finding, which is why it costs zero calls ----------

def test_rule_a_needs_no_live_call_model_already_conforms_3_of_3():
    """Rule A asks for `provided that`, not `further provided that`. At C04-117
    the committed v3 cassettes already show the conforming string on 3 of 3
    runs, so no v4 wording could improve it. If this ever fails, the probe's
    scope was wrong."""
    conforming = nonconforming = 0
    for run in sorted((GOLD / "C04-117").glob("run*.json")):
        d = json.loads(run.read_text())
        found = False
        for r in d["responses"]:
            content = r["json"]["choices"][0]["message"]["content"]
            try:
                obj = json.loads(content)
            except Exception:
                continue
            for o in obj.get("obligations", []) or []:
                for e in o.get("condition_raws") or []:
                    if e.startswith("provided that amounts owed"):
                        found = True
                    if e.startswith("further provided that"):
                        nonconforming += 1
        conforming += int(found)
    assert conforming == 3, f"expected Rule A's string on 3 of 3 runs, got {conforming}"
    assert nonconforming == 0, "the model emitted gold's `further provided that` form"


def test_gold_c04_01_is_the_non_conforming_side_of_rule_a():
    """The clause-7 failure is gold's, not the model's -- and gold is locked at
    v0.28, four versions before Rule A existed, so §10.2 does not reach it."""
    item = json.loads(
        next((ROOT / "apps/brain/evals/goldens").glob("batch0*/items/C04-01.json")).read_text())
    assert item["guideline_version"] == "v0.28"
    assert any(c.startswith("further provided that") for c in item["conditions"]), (
        "C04-01 no longer carries the `further` form -- if it was conformed, "
        "Rule A's zero-call finding needs restating"
    )


# --- (4) the predicate, and the v3 baseline mechanism by mechanism ---------

def test_predicate_is_three_valued_on_known_strings(scorer):
    a, b = "If the Principal is a natural person", "upon the death"
    assert scorer.classify([a, b], a, b)[0] == "CONFORM"
    assert scorer.classify([f"{a}, {b}"], a, b)[0] == "MERGED"
    assert scorer.classify([b], a, b)[0] == "DROPPED"
    assert scorer.classify([a], a, b)[0] == "DROPPED"
    assert scorer.classify([], a, b)[0] == "OTHER"
    assert scorer.classify(["something else"], a, b)[0] == "OTHER"
    # whitespace-insensitive, per PREREGISTRATION.md
    assert scorer.classify([f"  {a} ", b], a, b)[0] == "CONFORM"


def test_tie_resolves_to_the_worst_observed_outcome(scorer):
    """§6.1 as amended at v0.30 to match report.py's G2: never round in the
    pipeline's favour."""
    modal, note = scorer.modal(["CONFORM", "MERGED"])
    assert modal == "MERGED" and "worst observed" in note
    modal, note = scorer.modal(["CONFORM", "CONFORM", "MERGED"])
    assert modal == "CONFORM" and "UNSTABLE" in note
    modal, _ = scorer.modal(["MERGED", "MERGED", "CONFORM"])
    assert modal == "MERGED"


def test_v3_baseline_fails_the_two_pairs_by_DIFFERENT_mechanisms(scorer):
    """The reason the predicate is three-valued. §3.8.2 records the 2:1
    instability but not that pair 1 MERGES while pair 2 DROPS a phrase
    entirely -- a wording that turned a DROP into a MERGE would have changed
    behaviour without conforming, and a boolean predicate could not see it."""
    runs = sorted((GOLD / "C11-094").glob("run*.json"))
    assert len(runs) == 3
    got = {}
    for key in ((("C11-094", 1)), (("C11-094", 2))):
        a, b = scorer.PAIRS[key]
        verdicts = []
        for rp in runs:
            best = "OTHER"
            rank = ["OTHER", "DROPPED", "MERGED", "CONFORM_ARTIFACT_STRIPPED", "CONFORM"]
            for ents in scorer.entries_of(rp):
                v = scorer.classify(ents, a, b)[0]
                if rank.index(v) > rank.index(best):
                    best = v
            verdicts.append(best)
        got[key] = verdicts
    assert got[("C11-094", 1)].count("MERGED") == 2
    assert got[("C11-094", 1)].count("CONFORM") == 1
    assert got[("C11-094", 2)].count("DROPPED") == 2
    assert got[("C11-094", 2)].count("CONFORM") == 1
    for key in got:
        assert scorer.modal(got[key])[0] != "CONFORM", f"{key} baseline must FAIL"


def test_the_holdout_is_outside_the_gold_set():
    """A hold-out inside the gold set would not be held out."""
    gold_segs = set()
    for b in sorted((ROOT / "apps/brain/evals/goldens").glob("batch0*")):
        for f in (b / "items").glob("*.json"):
            gold_segs.add(json.loads(f.read_text())["segment_id"])
        for e in json.loads((b / "exclusions.json").read_text()):
            gold_segs.add(e["segment_id"].split("#")[0])
    assert "E02-010" not in gold_segs
    assert "C11-094" in gold_segs, "the known-failing case must be a gold segment"


def test_preregistration_exists_and_records_the_amendment():
    """It was committed before any v4 call. The hold-out substitution is
    recorded in it rather than applied silently."""
    text = (PROBE / "PREREGISTRATION.md").read_text()
    assert "RULE A NEEDS NO LIVE CALL" in text
    assert "AMENDMENT, made BEFORE any `v4` call was sent" in text
    assert "E02-010" in text and "C13-010" in text, (
        "the amendment must name both the chosen hold-out and the better one it "
        "replaced, with the reason"
    )
    assert "36" in text, "the cap must be stated"


# --- (5) the live results, pinned from the committed probe cassettes --------
#
# These read `evals/probes/conditions_v4/{v3,v4}/` only -- no corpus, no
# database, no model call -- so they run in CI and a future edit cannot restate
# the verdict without the cassettes agreeing.

def _verdict(scorer, base: pathlib.Path, key) -> tuple[str, list[str]]:
    a, b = scorer.PAIRS[key]
    rank = ["OTHER", "DROPPED", "MERGED", "CONFORM_ARTIFACT_STRIPPED", "CONFORM"]
    verdicts = []
    for rp in sorted(base.glob("run*.json")):
        best = "OTHER"
        for ents in scorer.entries_of(rp):
            v = scorer.classify(ents, a, b)[0]
            if rank.index(v) > rank.index(best):
                best = v
        verdicts.append(best)
    return scorer.modal(verdicts)[0], verdicts


def test_v4_conforms_3_of_3_on_every_pair(scorer):
    """THE VERDICT. Rule B is achievable by wording."""
    for key, base in (
        (("C11-094", 1), PROBE / "v4/C11-094"),
        (("C11-094", 2), PROBE / "v4/C11-094"),
        (("E02-010", 1), PROBE / "v4/E02-010"),
    ):
        modal, runs = _verdict(scorer, base, key)
        assert runs == ["CONFORM"] * 3, f"{key}: {runs}"
        assert modal == "CONFORM", f"{key}: {modal}"


def test_the_holdouts_own_v3_baseline_FAILS(scorer):
    """Without this the hold-out's v4 pass is uninterpretable -- the model might
    have conformed there under v3 anyway. It does not."""
    modal, runs = _verdict(scorer, PROBE / "v3/E02-010", ("E02-010", 1))
    assert modal == "MERGED", f"expected the baseline to FAIL by merging, got {modal} {runs}"
    assert runs.count("CONFORM") == 1, runs


def test_the_negative_control_is_not_split_by_v4(scorer):
    """C11-02's single 127-char condition CONTAINS `within the twelve (12) month
    period` and could plausibly have been split. If v4 split it, the wording
    would be making the model split everything -- which a one-sided test misses."""
    ctl = scorer.norm(scorer.CONTROL[1])
    for rp in sorted((PROBE / "v4/C11-094").glob("run*.json")):
        for ents in scorer.entries_of(rp):
            normed = [scorer.norm(e) for e in ents]
            if ctl in normed:
                continue
            fragments = [e for e in normed if e and e != ctl and e in ctl]
            assert not fragments, f"{rp.name}: control was SPLIT into {fragments}"


def test_the_ocr_artifact_was_quoted_verbatim_not_normalised(scorer):
    """E02-010's phrase B carries a stray page number mid-phrase. A CONFORM
    verdict requires it exactly, and the predicate kept a separate
    CONFORM_ARTIFACT_STRIPPED bucket for the normalising case. It must never
    have fired -- confirming the C04-117 precedent the pre-registration cited."""
    _, runs = _verdict(scorer, PROBE / "v4/E02-010", ("E02-010", 1))
    assert "CONFORM_ARTIFACT_STRIPPED" not in runs, runs
    artifact = "written 3 notice"
    assert any(artifact in e
               for rp in sorted((PROBE / "v4/E02-010").glob("run*.json"))
               for ents in scorer.entries_of(rp) for e in ents), (
        "the artifact is absent from every emitted entry -- re-read RESULTS.md §1"
    )


def test_v4_does_not_change_span_selection(scorer):
    """F34's isolation result, and the strongest part of it: the set of distinct
    spans is byte-identical between arms on both segments."""
    def spans(base: pathlib.Path) -> set[str]:
        out = set()
        for rp in sorted(base.glob("run*.json")):
            d = json.loads(rp.read_text())
            for r in d["responses"]:
                try:
                    obj = json.loads(r["json"]["choices"][0]["message"]["content"])
                except Exception:
                    continue
                for o in obj.get("obligations", []) or []:
                    if isinstance(o, dict) and "span_text" in o:
                        out.add(o["span_text"])
        return out
    assert spans(PROBE / "v3/E02-010") == spans(PROBE / "v4/E02-010")
    assert spans(GOLD / "C11-094") == spans(PROBE / "v4/C11-094")


def test_f34s_temporal_side_effect_is_real_and_bounded(scorer):
    """F34. Pinned in BOTH directions: the null rate rises, AND no target
    candidate is affected -- so a future reader cannot quote either half alone."""
    def nulls(base: pathlib.Path) -> tuple[int, int]:
        n = tot = 0
        for rp in sorted(base.glob("run*.json")):
            d = json.loads(rp.read_text())
            for r in d["responses"]:
                try:
                    obj = json.loads(r["json"]["choices"][0]["message"]["content"])
                except Exception:
                    continue
                for o in obj.get("obligations", []) or []:
                    if isinstance(o, dict) and "span_text" in o:
                        tot += 1
                        n += int(o.get("temporal_raw") is None)
        return n, tot
    v3 = tuple(sum(x) for x in zip(nulls(GOLD / "C11-094"), nulls(PROBE / "v3/E02-010")))
    v4 = tuple(sum(x) for x in zip(nulls(PROBE / "v4/C11-094"), nulls(PROBE / "v4/E02-010")))
    assert v3 == (1, 14), f"v3 baseline null rate moved: {v3}"
    assert v4 == (4, 15), f"v4 null rate moved: {v4}"
    # ...and the bound: the MUST/TRANSFER targets keep their temporal 6/6.
    kept = 0
    for base in (GOLD / "C11-094", PROBE / "v4/C11-094"):
        for rp in sorted(base.glob("run*.json")):
            d = json.loads(rp.read_text())
            for r in d["responses"]:
                try:
                    obj = json.loads(r["json"]["choices"][0]["message"]["content"])
                except Exception:
                    continue
                for o in obj.get("obligations", []) or []:
                    if (isinstance(o, dict) and o.get("modality") == "MUST"
                            and o.get("action") == "TRANSFER"):
                        kept += int(o.get("temporal_raw") is not None)
    assert kept == 12, (
        f"expected the MUST/TRANSFER targets to keep temporal_raw on all 12 "
        f"candidate-runs across both arms, got {kept}"
    )


def test_spend_stayed_within_the_approved_cap():
    """21 of 36. Nine cassettes; the call count is the recorded response count."""
    calls = 0
    for rp in sorted(PROBE.glob("v*/*/run*.json")):
        calls += len(json.loads(rp.read_text())["responses"])
    assert calls == 21, f"recorded calls = {calls}, RESULTS.md says 21"
    assert len(list(PROBE.glob("v*/*/run*.json"))) == 9
