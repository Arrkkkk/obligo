"""Can the pipeline EXPRESS a both-ABSENT obligation at all? -- executed, not read.
The proof behind §8.3 of C14_076_INVESTIGATION.md.

THE QUESTION. §5 says "ABSENT matches ABSENT", but a scoring rule is only real if
the artefact it scores can exist. Before asking whether a both-ABSENT item scores
correctly, ask whether such a prediction can reach the scorer at all: three
components sit between the model and §5, and any of them could refuse an empty
alias -- the grounding gate, the Lark grammar, and the typechecker.

WHY EXECUTED. Every prior instance of this question in this repo was settled
wrongly by reading (the UNLESS carve-out, the AndPredicate/OrPredicate gap, the
trailing-period bug) -- in each case a guarantee held at the grammar/DSL layer
that the real extraction path bypassed, and in each case found by running it.
This script runs the real ground_candidates(), the real _build_dsl() and the real
parser over candidate 2's actual text.

THE TYPECHECK STEP IS NOT EXECUTED and that is stated rather than hidden: it needs
a live Neon connection. It is established instead by clause8_vacuous.py, which
proves the resolution outcome from the registry contents without a database.
"""
import sys, pathlib, inspect

HERE = pathlib.Path(__file__).resolve()
BRAIN = HERE.parents[4]                                   # apps/brain
sys.path.insert(0, str(BRAIN / "src"))

from obligo_brain.graphs.extraction import (               # noqa: E402
    LLMCandidate, SegmentRecord, ground_candidates)
from obligo_brain.compiler import ir_compile, parser, typecheck   # noqa: E402

# C14-076's second un-annotated sentence, verbatim.
SEG = ("Israel value added tax shall be added, if applicable, to all amounts "
       "payable hereunder and will be paid against submission of appropriate "
       "tax invoices.")
SPAN = ("Israel value added tax shall be added, if applicable, to all amounts "
        "payable hereunder")

# grammar/obligation.lark's SEGMENT_ID terminal is a UUID, not a corpus segment
# label -- run_pipeline() passes the segments table's own id. A literal
# "C14-076" here fails to lex, which is a fact about the DSL surface and NOT
# about the empty aliases under test; using a UUID keeps the two separate.
SEGMENT_UUID = "7d4f1a2b-0000-4000-8000-00000000c14e"


def run():
    cand = LLMCandidate(
        span_text=SPAN, modality="MUST", obligor_alias="", obligee_alias="",
        action="PAY", object_class="value_added_tax",
        object_raw_text="Israel value added tax", temporal_raw=None,
        condition_raws=["if applicable"], confidence=0.9,
    )
    grounded, rejected = ground_candidates(
        SegmentRecord(id=SEGMENT_UUID, text=SEG), [cand])
    if rejected:
        return dict(stage="ground", rejected=rejected[0])
    dsl = ir_compile._build_dsl(grounded[0])
    if not isinstance(dsl, str):
        return dict(stage="compile", rejected=dsl)
    return dict(stage="parse", dsl=dsl, obligation=parser.parse(dsl))


if __name__ == "__main__":
    print("=== EXECUTION: a both-ABSENT candidate through the real pipeline ===")
    try:
        res = run()
    except Exception as e:                                 # noqa: BLE001
        print(f"  FAILED at an unexpected stage: {type(e).__name__}: {e}")
        sys.exit(1)

    if res["stage"] != "parse":
        print(f"  REFUSED at {res['stage']}: {res['rejected']}")
        print("\nVERDICT: the pipeline CANNOT express a both-ABSENT obligation.")
        sys.exit(1)

    obl = res["obligation"]
    print(f"  1. GROUNDING : accepted "
          f"(_is_grounded_substring returns True on an empty needle, by design)")
    print(f"  2. DSL       : {res['dsl']}")
    print(f"  3. PARSE     : OK")
    print(f"       obligor = {obl.obligor!r}")
    print(f"       obligee = {obl.obligee!r}")

    checks = [
        ("obligor parsed to an UnresolvedParty with an empty alias",
         type(obl.obligor).__name__ == "UnresolvedParty" and obl.obligor.alias == ""),
        ("obligee parsed to an UnresolvedParty with an empty alias",
         type(obl.obligee).__name__ == "UnresolvedParty" and obl.obligee.alias == ""),
    ]
    print("\n=== KNOWN-ANSWER CHECK ===")
    ok = True
    for label, got in checks:
        ok &= got
        print(f"  {'ok  ' if got else 'BAD '} {label}")
    if not ok:
        print("\nDETECTOR VERDICT: FAILED")
        sys.exit(1)

    print("\n  4. TYPECHECK (source, not executed -- needs a live database):")
    for line in inspect.getsource(typecheck._resolve_party).strip().splitlines():
        print(f"       {line}")

    print("\nVERDICT: there is NO structural blocker. Grounding, the grammar and the")
    print("compiler all accept an empty alias on both slots, so a both-ABSENT")
    print("prediction can reach §5 and §5's ABSENT branch will match it. The 0/81")
    print("obligor figure in alias_census.py is therefore BEHAVIOURAL -- a prompt")
    print("convention the model was never given -- and not a capability gap.")
