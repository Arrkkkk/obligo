"""§3.6.1 / §3.6.2's restatement screen -- does an `object_class` label restate a
verb the item's `action_accept_set` holds, rather than only its `action` SLOT value?

This is the screen behind guideline §10.1 **F12** (ruled v0.58). It is preserved
here, gate and all, rather than living only in a session record -- the same
discipline `band_risk/` is kept under.

WHY IT IS A HAND-AUTHORED TABLE AND DELIBERATELY NOT A STEMMER
--------------------------------------------------------------
Every recorded miss by the predecessor of this screen was a stemmer artifact at a
`y`/`e` boundary -- `deliver`->`delivery`, `indemnify`->`indemnification`, and
`comply`->`compliance` (that last one reported a ZERO, which reads more
reassuringly than a wrong positive; §3.6.1 records it as the third miss in one
session). The answer to three stemmer misses is to stop stemming, not to stem more
carefully, so the mapping below is written out.

It would not have helped with the fourth. `notify`->`notice` is SUPPLETIVE: no
stemmer of any kind relates those strings, which is why `C22-01`'s slot sat
unscreened through both the v0.44 sweep and its v0.48 re-run. That case is now a
known answer below.

THE 2x2 THE RECORD ONLY EVER FILLED THREE CELLS OF
--------------------------------------------------
                         label = slot        label = accept-set member
    verb = action slot   v0.44 scope         v0.44 scope
    verb = accept member  F12: C04-04         NEVER MEASURED until v0.58

Scope B below is F12's own scope; scope A is the v0.44 scope, re-run because a
screen that missed `C22-01` once can miss it again.

Reads only committed gold JSON -- no corpus, no database, no network.
"""

from __future__ import annotations

import json
import pathlib

GOLDENS = pathlib.Path(__file__).resolve().parents[2]

# The gate below checks the MATCHER. It does not check that anything was LOADED --
# a distinct failure surface, and the first draft of this file tripped it: the path
# was one level short, every glob returned empty, and the screen printed "12/12
# PASS" over ZERO items and "no offenders". A passing gate above an empty corpus is
# the Standing Principle 7 shape one layer out, so the load asserts its own floor.
MIN_EXPECTED_ITEMS = 36

# Taxonomy verb -> the nominal/adjectival surface forms that RESTATE it.
# One entry per `compiler/ast.py` ACTIONS member; verbs whose nominal is the bare
# verb carry just that.
FORMS: dict[str, list[str]] = {
    "APPOINT": ["appoint", "appointment"],
    "ASSIGN": ["assign", "assignment", "assignee"],
    "COMPLY": ["comply", "compliance", "compliant"],
    "CONSULT": ["consult", "consultation"],
    "COOPERATE": ["cooperate", "cooperation"],
    "CURE": ["cure"],
    "DELETE": ["delete", "deletion"],
    "DELIVER": ["deliver", "delivery", "deliverable"],
    "DISCLOSE": ["disclose", "disclosure"],
    "ENSURE": ["ensure", "assurance"],
    "ESTABLISH": ["establish", "establishment"],
    "EXECUTE": ["execute", "execution"],
    "FINALIZE": ["finalize", "finalization"],
    "GRANT": ["grant"],
    "INDEMNIFY": ["indemnify", "indemnification", "indemnity"],
    "MAINTAIN": ["maintain", "maintenance"],
    "NEGOTIATE": ["negotiate", "negotiation"],
    # notify -> notice is SUPPLETIVE, and is the whole reason this is a table.
    "NOTIFY": ["notify", "notification", "notice"],
    "PAY": ["pay", "payment", "payable"],
    "PROCESS": ["process", "processing"],
    "PROCURE": ["procure", "procurement"],
    "PROVIDE": ["provide", "provision"],
    "RECOVER": ["recover", "recovery"],
    "REIMBURSE": ["reimburse", "reimbursement"],
    "REPAIR": ["repair"],
    "REPORT": ["report", "reporting"],
    "REPRESENT": ["represent", "representation"],
    "RETAIN": ["retain", "retention", "retained"],
    "RETURN": ["return"],
    "TERMINATE": ["terminate", "termination"],
    "TRANSFER": ["transfer"],
    "USE": ["use", "usage"],
    "WAIVE": ["waive", "waiver"],
    "WITHHOLD": ["withhold", "withholding"],
}


def restates(label: str, verb: str) -> list[str]:
    """Which snake_case tokens of `label` restate `verb`. Number-tolerant only."""
    forms = set(FORMS[verb])
    hits = []
    for token in (t for t in label.split("_") if t):
        base = token[:-1] if token.endswith("s") and token[:-1] in forms else token
        if base in forms:
            hits.append(token)
    return hits


# (label, verb, expect_hit, why this answer is already established)
KNOWN_ANSWERS: list[tuple[str, str, bool, str]] = [
    ("self_regulatory_compliance", "COMPLY", True, "F12's one recorded instance (C04-04)"),
    ("self_compliant_use", "COMPLY", True, "C04-04's pre-F3 slot -- exposure was 1 before and after"),
    ("product_delivery", "DELIVER", True, "C04-03's retained member, a v0.44 known answer"),
    ("product_liability_indemnification", "INDEMNIFY", True, "C10-01's pre-v0.44 slot"),
    ("retained_sample", "RETAIN", True, "C02-01: MUST flag, then CLEARS under carve-out 1"),
    ("withholding_tax", "WITHHOLD", True, "C14-01: MUST flag, then CLEARS under carve-out 1"),
    ("notice", "NOTIFY", True, "C22-01 -- the suppletive case both prior sweeps missed"),
    ("insurance_certificate_listing", "ESTABLISH", False,
     "C10-02: the screen is STRUCTURALLY BLIND here -- action is ESTABLISH, the real verb is 'add'"),
    ("product_shipment", "DELIVER", False, "C04-03's slot is clean"),
    ("trademark_license_grant", "ENSURE", False, "C22-02: _grant restates nothing; action is ENSURE"),
    ("third_party_royalties", "REIMBURSE", False, "C04-01's slot is clean"),
    ("retention_costs", "PROVIDE", False, "C02-03 is clean against its own action"),
]


class GateFailure(AssertionError):
    """The screen disagreed with an answer already on the record."""


def check_gate() -> None:
    """Standing Principle 7. Counts are not evidence until this passes.

    A ZERO is exactly as much a detector output as a positive count, and reads
    more reassuringly -- which is how `comply`->`compliance` survived a pass.
    """
    bad = [
        (label, verb, expected, why)
        for label, verb, expected, why in KNOWN_ANSWERS
        if bool(restates(label, verb)) is not expected
    ]
    if bad:
        raise GateFailure(f"restatement screen failed {len(bad)} of {len(KNOWN_ANSWERS)}: {bad}")


def load_items() -> list[dict]:
    items = sorted(
        (json.loads(p.read_text()) for p in GOLDENS.glob("batch0*/items/*.json")),
        key=lambda d: d["item_id"],
    )
    if len(items) < MIN_EXPECTED_ITEMS:
        raise GateFailure(
            f"loaded {len(items)} gold items from {GOLDENS}, expected at least "
            f"{MIN_EXPECTED_ITEMS} -- an empty or short load makes every count below "
            f"meaningless, and a zero reads like a clean result"
        )
    return items


def screen(items: list[dict]) -> dict[str, list[tuple]]:
    """Returns {"slot_verb": [...], "accept_set_verb": [...]}.

    `slot_verb` is the v0.44 scope (the label restates the item's own `action`);
    `accept_set_verb` is F12's scope (it restates some OTHER accept-set member).
    Each hit is (item_id, "SLOT"|"member", label, verb, token).
    """
    out: dict[str, list[tuple]] = {"slot_verb": [], "accept_set_verb": []}
    for item in items:
        slot_action = item["action"]
        labels = [("SLOT", item["object_class"])] + [
            ("member", m) for m in item["object_class_accept_set"] if m != item["object_class"]
        ]
        for kind, label in labels:
            for verb in item["action_accept_set"]:
                hits = restates(label, verb)
                if not hits:
                    continue
                bucket = "slot_verb" if verb == slot_action else "accept_set_verb"
                out[bucket].append((item["item_id"], kind, label, verb, hits[0]))
    return out


def items_without_a_clean_member(items: list[dict]) -> list[str]:
    """§3.6.2's set rule, read accept-set-wide: at least one member restating no
    accept-set verb and neither party.

    The one item this returns is `C22-01`, whose hit is against its own SLOT verb
    -- v0.44 scope, not F12's -- and which CLEARS under carve-out 1 because the
    span names the thing "notice". See §3.6.2.
    """
    offenders = []
    for item in items:
        parties = [p for p in (item.get("obligor"), item.get("obligee")) if p and p != "ABSENT"]
        party_tokens = {t.lower() for p in parties for t in p.replace("_", " ").split()}
        clean = [
            m
            for m in item["object_class_accept_set"]
            if not any(restates(m, v) for v in item["action_accept_set"])
            and not (party_tokens & {t for t in m.split("_") if t})
        ]
        if not clean:
            offenders.append(item["item_id"])
    return offenders


def main() -> None:
    check_gate()
    print(f"known-answer gate: {len(KNOWN_ANSWERS)}/{len(KNOWN_ANSWERS)} PASS\n")
    items = load_items()
    hits = screen(items)
    for bucket, title in (
        ("slot_verb", "A. label restates the item's own `action` SLOT (v0.44 scope)"),
        ("accept_set_verb", "B. label restates a NON-SLOT accept-set verb (F12's scope)"),
    ):
        print(f"=== {title} ===")
        for item_id, kind, label, verb, token in hits[bucket]:
            print(f"  {item_id:8} {kind:6} {label:42} restates {verb:10} via {token!r}")
        print(f"  -> {len(hits[bucket])} hits over {len({h[0] for h in hits[bucket]})} items\n")
    offenders = items_without_a_clean_member(items)
    print(f"items with NO clean member under §3.6.2's accept-set-wide set rule: {offenders or 'none'}")
    print(f"(screened {len(items)} committed items)")


if __name__ == "__main__":
    main()
