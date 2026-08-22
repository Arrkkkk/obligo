"""R5 -- the startup self-check that makes registry-fixture defects fail
loudly instead of surfacing as clause-8 losses attributed to extraction.

Guideline section 21 R5: before scoring any item, the harness MUST assert,
for every locked gold item in scope, that each of its obligor/obligee values
resolves iff the item's annotated `underspecified` value requires it. A
mismatch is a hard startup failure naming the item and the alias, never a
scored result.

Why this is load-bearing rather than defensive. `underspecified` is scored
(section 5 clause 8) and, per section 3.9 as restated at v0.28, its first
trigger is "a party reference symbols.resolve_party() cannot match" -- which
is a fact about the REGISTRY, not about the document. So every fixture
defect in R1-R3 (wrong org grouping, an alias in the wrong case, a party
left unregistered) lands on exactly the same field a genuine extraction
error lands on, and is indistinguishable from it in the report. Without R5
the harness would measure its own setup and publish it as model quality.

The check recomputes what section 3.9 says `underspecified` MUST be, from
the registry plus the item's own annotated temporal, and compares that with
what the annotator wrote. It therefore also cross-checks the conforming
pass: if a locked item's `underspecified` was conformed wrongly, this fails
on the first run rather than quietly costing a point.

Temporal contribution reflects v1 reality, not the spec's eventual shape:
symbols.resolve_date() and resolve_trigger() unconditionally return None
(see their module docstring), so ANY date- or trigger-bearing temporal makes
an obligation underspecified in v1. `temporal: null` is deliberately NOT a
trigger (section 15.3, and typecheck.py returns None without appending to
missing_fields).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from evals.harness import registry as registry_mod

GOLDENS_DIR = Path(__file__).resolve().parent.parent / "goldens"

# Which of the five frozen temporal forms carry a constituent that
# section 3.9 triggers 2/3 flag as unresolvable in v1.
_DATE_BEARING = {"BY", "DURING"}
_TRIGGER_BEARING = {"WITHIN", "RELATIVE_TO_TRIGGER"}


@dataclass(frozen=True)
class Failure:
    item_id: str
    kind: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.item_id}] {self.kind}: {self.detail}"


def _temporal_forces_underspecified(temporal: dict | None) -> tuple[bool, str]:
    if temporal is None:
        return False, "temporal is null -- deliberately not a trigger (section 15.3)"
    form = temporal.get("form")
    if form in _TRIGGER_BEARING:
        return True, f"{form} carries a TriggerRef; resolve_trigger() returns None in v1"
    if form in _DATE_BEARING:
        return True, f"{form} carries a DateRef; resolve_date() returns None in v1"
    if form == "EVERY":
        if str(temporal.get("unit")) == "bd":
            return True, "EVERY with a business-day duration (rule 6)"
        return False, "EVERY with no date, trigger, or bd duration"
    return False, f"unrecognised temporal form {form!r}"


def check_item(item: dict, reg: registry_mod.DocumentRegistry) -> list[Failure]:
    """Recomputes section 3.9 for one item and reports every disagreement."""
    failures: list[Failure] = []
    unresolved_parties: list[str] = []

    for role in ("obligor", "obligee"):
        alias = item[role]
        if alias == "ABSENT":
            unresolved_parties.append(f"{role}=ABSENT")
            continue
        if reg.resolve(alias) is None:
            unresolved_parties.append(f"{role}={alias!r} does not resolve")

    temporal_flag, temporal_why = _temporal_forces_underspecified(item.get("temporal"))
    predicted = bool(unresolved_parties or temporal_flag)
    annotated = item["underspecified"]

    if predicted != annotated:
        reasons = "; ".join(unresolved_parties) or "all parties resolve"
        failures.append(
            Failure(
                item["item_id"],
                "UNDERSPECIFIED MISMATCH",
                f"annotated {annotated}, but section 3.9 over registry {reg.doc_id} "
                f"computes {predicted}. Parties: {reasons}. Temporal: {temporal_why}. "
                "Either the registry is wrong (section 21 R1-R3) or the item is.",
            )
        )

    # A resolvable party that the annotator also listed in missing_fields is a
    # weaker signal -- missing_fields is not scored (section 5) -- but it means the
    # two artifacts disagree about the same fact, so it is surfaced, not enforced.
    for role in ("obligor", "obligee"):
        alias = item[role]
        listed = role in item.get("missing_fields", [])
        resolves = alias != "ABSENT" and reg.resolve(alias) is not None
        if resolves and listed:
            failures.append(
                Failure(
                    item["item_id"],
                    "MISSING_FIELDS DISAGREEMENT (non-blocking)",
                    f"{role}={alias!r} resolves against registry {reg.doc_id}, "
                    f"but the item lists {role!r} in missing_fields",
                )
            )
    return failures


def run(items_dir: Path = GOLDENS_DIR) -> list[Failure]:
    failures: list[Failure] = []
    registries: dict[str, registry_mod.DocumentRegistry] = {}
    for path in sorted(items_dir.rglob("items/*.json")):
        item = json.loads(path.read_text())
        doc_id = item["doc_id"]
        if doc_id not in registries:
            registries[doc_id] = registry_mod.load(doc_id)
        failures.extend(check_item(item, registries[doc_id]))
    return failures


def main() -> int:
    failures = run()
    blocking = [f for f in failures if "non-blocking" not in f.kind]
    for f in failures:
        print(f"  {f}")
    n_items = len(list(GOLDENS_DIR.rglob("items/*.json")))
    print(
        f"\nR5 self-check over {n_items} items: "
        f"{len(blocking)} blocking, {len(failures) - len(blocking)} non-blocking."
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
