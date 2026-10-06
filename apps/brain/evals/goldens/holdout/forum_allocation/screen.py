"""§2.8's class measurement: forum / dispute-forum allocations in the 1,547-segment pool.

Preserved because §2.8 cites a count, and a cited count whose script is gone is an
assertion rather than a measurement.

THE SCREEN IS LOOSE ON PURPOSE AND ITS OVERRIDE RATE IS PUBLISHED, not patched away.
A marker conjunction (modal x dispute-verb x venue-noun) cannot tell a forum clause from
a severability clause that happens to mention a court of competent jurisdiction, so 16 of
25 flags are hand-rejected with a reason recorded per flag. The hand pass is load-bearing
and the raw count must never be quoted as the class size.

Standing Principle 7: the known-answer gate asserts BOTH that `C04-172` -- the segment the
screen was written for -- is flagged, AND that four named shapes are flagged-then-rejected,
so the gate proves the sweep is loose and the overrides real rather than proving the
pattern right. `load_pool()` raises below 1,547 segments, because a known-answer gate over
an empty pool passes (v0.58's own preserved screen printed "12/12 PASS" over zero items).

    uv run --project apps/brain python \
        apps/brain/evals/goldens/holdout/forum_allocation/screen.py
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

BRAIN = Path(__file__).resolve().parents[4]              # apps/brain
ROOT = BRAIN.parents[1]                                  # repo root
POOL_EXPECTED = 1547

MODAL = re.compile(r"\b(?:shall|must|will|may)\b", re.I)
DISPUTE_VERB = re.compile(
    r"\b(?:brought|commenced|filed|instituted|litigated|submitted|referred|"
    r"adjudicated|resolved|settled|heard|tried)\b",
    re.I,
)
VENUE_NOUN = re.compile(
    r"\b(?:court|courts|tribunal|arbitration|arbitral|venue|forum|jurisdiction)\b", re.I
)

# The genuine class, hand-read. Keyed by segment, valued by the shape quoted in §2.8.
GENUINE = {
    "C02-084": "court, exclusive",
    "C03-161": "arbitration, AAA Commercial Rules",
    "C04-172": "court, SDNY -- §2.8's own case",
    "C12-016": "arbitration, AAA rules",
    "C13-047": "arbitration, single arbitrator, Asheville NC",
    "C15-058": "venue, exclusive",
    "C22-043": "courts, heard and determined",
    "E05-026": "court, State Circuit or Federal",
    "E08-041": "arbitration, final and binding",
}

# Every flag the hand pass rejects, with its reason. Published, not hidden.
REJECTED = {
    "C04-007": "definition of Intellectual Property Rights; 'laws of any jurisdiction'",
    "C04-159": "termination for insolvency; 'court' incidental to the bankruptcy trigger",
    "C05-076": "severability; 'adjudicated ... by a court of competent jurisdiction'",
    "C06-006": "bankruptcy-sale notice boilerplate",
    "C06-014": "bankruptcy-sale lease assumption, no forum allocated",
    "C06-015": "bankruptcy-sale lease assumption, no forum allocated",
    "C06-021": "agent authorisation to conduct a GOB sale",
    "C06-035": "best-efforts duty to resolve a creditor dispute, no forum named",
    "C06-094": "objection window in an approval order",
    "C06-096": "exclusive right to market and sell",
    "C06-097": "conveyance of assets per an approval order",
    "C06-100": "a notice ADDRESS block plus a docket stamp",
    "E03-059": "severability; same shape as C05-076",
    # Adjacent but a DIFFERENT shape -- a party-subject MAY right to refer a dispute.
    # §2.8 deliberately does not reach these; see F35's neighbouring-shape paragraph.
    "C04-171": "party-subject MAY: 'either Party may submit such Dispute to a court'",
    "C13-046": "party-subject MAY: 'either party may refer'",
    "C14-148": "escalation mechanics; already measured under §3.5.2",
}


def load_corpus_module():
    spec = importlib.util.spec_from_file_location(
        "corpus", BRAIN / "evals/corpus.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_pool(mod):
    pool = mod.build_pool(ROOT / ".corpus", mod.load_manifest())
    if len(pool) < POOL_EXPECTED:
        raise RuntimeError(
            f"pool rebuilt to {len(pool)}, expected {POOL_EXPECTED}; a known-answer "
            "gate over a short pool proves nothing"
        )
    return pool


def flagged(mod, pool) -> dict[str, str]:
    """segment_id -> the first flagged sentence in it."""
    out = {}
    for seg in pool:
        for sent in mod.split_sentences(seg["text"]):
            if MODAL.search(sent) and DISPUTE_VERB.search(sent) and VENUE_NOUN.search(sent):
                out[seg["segment_id"]] = sent
                break
    return out


def gate(hits: dict[str, str]) -> None:
    """Both directions. A one-sided gate would only prove the pattern matches."""
    assert "C04-172" in hits, (
        "GATE FAILED: the segment this screen was written for is not flagged"
    )
    for sid, why in (
        ("C05-076", "severability"),
        ("C06-100", "a notice address block"),
        ("C04-171", "a party-subject MAY right"),
        ("C04-007", "a definition"),
    ):
        assert sid in hits, f"GATE FAILED: {sid} ({why}) is not flagged, so the "
        assert sid in REJECTED, f"GATE FAILED: {sid} is flagged but not hand-rejected"
    assert not (set(GENUINE) & set(REJECTED)), "a segment is both genuine and rejected"


def main() -> int:
    mod = load_corpus_module()
    pool = load_pool(mod)
    hits = flagged(mod, pool)
    gate(hits)

    unaccounted = set(hits) - set(GENUINE) - set(REJECTED)
    missing = (set(GENUINE) | set(REJECTED)) - set(hits)

    print(f"pool: {len(pool)} segments (gate: >= {POOL_EXPECTED})")
    print(f"GATE PASSED -- C04-172 flagged; 4 named false-positive shapes flagged AND rejected")
    print()
    print(f"RAW flags:            {len(hits)} segments  <- NOT the class size")
    print(f"hand-rejected:        {len(REJECTED)}")
    print(f"override rate:        {len(REJECTED)}/{len(hits)} = "
          f"{len(REJECTED) / len(hits) * 100:.0f}%")
    docs = sorted({s.split('-')[0] for s in GENUINE})
    print(f"GENUINE class:        {len(GENUINE)} segments across {len(docs)} documents "
          f"({' '.join(docs)})")
    print()
    for sid, shape in sorted(GENUINE.items()):
        print(f"  {sid}  {shape}")
    if unaccounted:
        print(f"\nUNACCOUNTED (neither genuine nor rejected): {sorted(unaccounted)}")
    if missing:
        print(f"\nCLASSIFIED BUT NO LONGER FLAGGED: {sorted(missing)}")
    return 1 if (unaccounted or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
