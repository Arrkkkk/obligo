"""Decision 1's cost and benefit: what a complete per-sentence disposition would cost,
and how much of §21 R6's UNEXPECTED over-count it retires.

Produces every number in §11's ruling log. Known-answer checks are asserts, not prints,
and are run before any new figure is read:
  - counts.py's published 32 gold / 22 segments / 6 disagreeing segments
  - unexpected.py's published 46 GOLD_MATCH / 13 COLD_ONLY / 11 NEITHER / 11 UNGROUNDED
  - C03-192 modal==5 gold==3 (C03-01's own notes count THREE duties there)
  - C11-094 (5,1,3) and C17-021 (2,1,3), the two segments §8 names

TWO DETECTOR FAULTS FOUND AND FIXED HERE, per Standing Principle 7 -- both would have
produced a wrong-but-plausible total:
  (1) the arithmetic proxy `modal - gold` UNDERCOUNTS (20 vs the true 21): C14-076 carries
      TWO gold items inside ONE sentence (§8.3.1), so subtracting item counts from sentence
      counts double-credits the covered sentence. Undisposed is computed by SPAN OVERLAP.
  (2) matching an anchor phrase anywhere in an exclusions.json entry gives FALSE POSITIVES:
      `E03-005#discuss` quotes its neighbouring sentences in its own `segment_text` field,
      so two sentences appeared "disposed" by an entry that says nothing about them. Only
      the `reason`/`rule`/`segment_id` fields are searched.
"""
import collections, glob, hashlib, json, os, statistics, sys

sys.path.insert(0, "/Users/rajitagrawal/obligo/apps/brain")
from evals import corpus  # noqa: E402

G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
C = "/Users/rajitagrawal/obligo/apps/brain/evals/cassettes/gold"

GOLD, BATCH = collections.defaultdict(list), {}
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d = json.load(open(p))
    GOLD[d["segment_id"]].append(d)
    BATCH[d["segment_id"]] = p.split("/")[-3]
TEXT = {}
for p in glob.glob(f"{G}/holdout/packet/segments/*.json"):
    d = json.load(open(p)); TEXT[d["segment_id"]] = d["segment_text"]
COLD = {}
for p in glob.glob(f"{G}/holdout/cold/*.json"):
    d = json.load(open(p)); COLD[d["segment_id"]] = d
EXC = []
for b in ("batch01", "batch02", "batch03"):
    EXC += json.load(open(f"{G}/{b}/exclusions.json"))


def sentences(seg):
    """Sentence spans, with each sentence's char offsets in the segment."""
    t, pos, out = TEXT[seg], 0, []
    for x in corpus.split_sentences(t):
        i = t.find(x[:40], pos)
        if i < 0:
            continue
        pos = i + 1
        out.append((i, i + len(x), x))
    return out


def undisposed(seg):
    """Modal-bearing sentences overlapping NO gold span. Span overlap, not arithmetic."""
    spans = [(g["span_char_start"], g["span_char_end"]) for g in GOLD[seg]]
    return [(i, j, x) for i, j, x in sentences(seg)
            if corpus._MODAL_RE.search(x)
            and not any(not (j <= a or i >= b) for a, b in spans)]


rows = []
for s in sorted(TEXT):
    sn = sentences(s)
    rows.append(dict(seg=s, batch=BATCH[s], sents=len(sn),
                     modal=sum(1 for _, _, x in sn if corpus._MODAL_RE.search(x)),
                     gold=len(GOLD[s]), cold=len(COLD[s]["items"]),
                     ud=len(undisposed(s))))
by = {r["seg"]: r for r in rows}
assert sum(r["gold"] for r in rows) == 32 and len(rows) == 22, "KA: totals"
assert sum(1 for r in rows if r["cold"] != r["gold"]) == 6, "KA: disagreeing segments"
assert (by["C03-192"]["modal"], by["C03-192"]["gold"]) == (5, 3), "KA: C03-192"
assert (by["C11-094"]["modal"], by["C11-094"]["gold"], by["C11-094"]["cold"]) == (5, 1, 3)
assert (by["C17-021"]["modal"], by["C17-021"]["gold"], by["C17-021"]["cold"]) == (2, 1, 3)
print("KNOWN-ANSWER CHECK vs counts.py / RESULTS.md: PASSED\n")

print("=== 1. COST: undisposed modal-bearing sentences per segment ===")
print(f"{'segment':9} {'batch':8} {'sents':>5} {'modal':>5} {'gold':>4} {'ud':>3}  proxy")
for r in rows:
    proxy = max(0, r["modal"] - r["gold"])
    print(f"{r['seg']:9} {r['batch']:8} {r['sents']:>5} {r['modal']:>5} {r['gold']:>4} "
          f"{r['ud']:>3}" + (f"   <== arithmetic proxy says {proxy}" if proxy != r["ud"] else ""))
ud = [r["ud"] for r in rows]
assert sum(ud) == 21, f"KA: undisposed total {sum(ud)}"
print(f"\ntotal={sum(ud)} (arithmetic proxy {sum(max(0, r['modal']-r['gold']) for r in rows)} "
      f"-- UNDERCOUNTS, fault (1) above)")
print(f"distribution {sorted(ud)}  mean={statistics.mean(ud):.2f}  "
      f"zero-extra {sum(1 for x in ud if x == 0)}/22")

print("\n=== 2. COST conditioned on density, and pool-weighted forward cost ===")
cond = {}
for m in sorted({r["modal"] for r in rows}):
    rr = [r for r in rows if r["modal"] == m]
    cond[m] = statistics.mean([r["ud"] for r in rr])
    print(f"  {m} modal sentence(s): n={len(rr)}  mean undisposed {cond[m]:.2f}  {[r['ud'] for r in rr]}")
POOL = {1: 782, 2: 376, 3: 194}; P4 = 195           # guideline §2.6.1, 1,547 pool segments
c4 = statistics.mean([r["ud"] for r in rows if r["modal"] >= 4])
lo = sum(POOL[m] * cond[m] for m in POOL) / sum(POOL.values())
hi = (sum(POOL[m] * cond[m] for m in POOL) + P4 * c4) / (sum(POOL.values()) + P4)
print(f"  4+ modal: mean {c4:.2f} (n={sum(1 for r in rows if r['modal'] >= 4)})")
print(f"  §2.6.1 pool: 1-modal is {100*POOL[1]/sum(POOL.values()):.1f}% of band-eligible segments")
print(f"  POOL-WEIGHTED FORWARD COST: {lo:.2f} (4+ all band-excluded) .. {hi:.2f} (4+ all admitted)")
segs = 68 / (32 / 22)
print(f"  over the ~{segs:.0f} further segments for 68 more items: ~{segs*lo:.0f}..{segs*hi:.0f} "
      f"dispositions = {segs*lo/68:.2f}x..{segs*hi/68:.2f}x the item count")
for b in ("batch01", "batch02", "batch03"):
    rr = [r for r in rows if r["batch"] == b]
    print(f"  observed {b}: mean modal {statistics.mean([r['modal'] for r in rr]):.2f}, "
          f"mean undisposed {statistics.mean([r['ud'] for r in rr]):.2f}")

print("\n=== 3. How much is ALREADY recorded (the §6.3 denominator correction) ===")
print("Only `reason`/`rule`/`segment_id` are searched -- `segment_text` quotes NEIGHBOURING")
print("sentences and matching it gives false positives (fault (2) above).")
ANCH = {  # a distinctive phrase per undisposed sentence; 'non-binding' is E03-01's own wording
    "C02-021": ["available for inspection"],
    "C03-192": ["not be construed as altering", "available on call"],
    "C04-117": ["acknowledges that the potential volume"],
    "C11-094": ["not be subject to BKC", "All other transfers",
                "use best efforts to transfer", "shall have the option"],
    "C14-044": ["reschedule delivery"],
    "C14-076": ["solely responsible for any and all taxes", "value added tax"],
    "C17-021": ["reducing the effects of the virus"],
    "C17-066": ["separated portion", "indemnify and hold harmless"],
    "E03-005": ["itemize", "non-binding", "discuss and review", "substantially the form"],
    "E07-010": ["On-site personnel", "These personnel"],
    "E08-005": ["ensure that the DC is clean"],
}
# C17-066's 'indemnify' hit is a CLASSIFICATION ('a section 8.4 mutual case') that states no
# disposition -- adjudicated by reading, per §3, and counted separately.
CLASSIFICATION_ONLY = {("C17-066", "indemnify and hold harmless")}
n = collections.Counter()
assert sum(len(v) for v in ANCH.values()) == 21, "KA: anchor count must match the 21"
for seg, ans in ANCH.items():
    notes = " || ".join((g.get("annotator_notes") or "") for g in GOLD[seg])
    for a in ans:
        e = [x for x in EXC if x["segment_id"].startswith(seg) and a.lower() in
             (x.get("reason", "") + " " + x.get("rule", "") + " " + x["segment_id"]).lower()]
        if (seg, a) in CLASSIFICATION_ONLY:  tag = "CLASSIFICATION_ONLY"
        elif e:                              tag = "EXCLUSION_LOG"
        elif a.lower() in notes.lower():     tag = "ANNOTATOR_NOTES"
        else:                                tag = "NONE"
        n[tag] += 1
        print(f"  {seg:9} {tag:19} {a!r}")
print(f"\n  exclusions.json {n['EXCLUSION_LOG']} + annotator_notes {n['ANNOTATOR_NOTES']} "
      f"= {n['EXCLUSION_LOG']+n['ANNOTATOR_NOTES']}/21 genuinely disposed "
      f"({100*(n['EXCLUSION_LOG']+n['ANNOTATOR_NOTES'])/21:.0f}%)")
print(f"  classification without a disposition: {n['CLASSIFICATION_ONLY']}   "
      f"nothing anywhere: {n['NONE']}")
print(f"  §6.3 measured ~11% over the 9 SURPLUS clauses -- a subsample selected FOR")
print(f"  disagreement. Over the 21 sentences §2.7 reaches, it is ~half.")

print("\n=== 4. The modal-keyed trigger is UNSAFE: non-modal sentences ===")
nm = [(s, x) for s in sorted(TEXT) for i, j, x in sentences(s)
      if not corpus._MODAL_RE.search(x)]
for s, x in nm:
    print(f"  {s:9} | {x[:110]}")
assert any("reserves the right to defer" in x for _, x in nm), \
    "KA: C04-117's §2.5 rights clause MUST be non-modal -- it is why §2.7's unit is the sentence"
print(f"\n  {len(nm)} non-modal sentences. C04-117's 'reserves the right to defer' -- SURPLUS")
print( "  CLAUSE #1, the §2.5 case -- is among them, so a modal-keyed trigger drops it silently.")

print("\n=== 5. BENEFIT: UNEXPECTED over-count retired ===")
UD = {s: [(i, j) for i, j, _ in undisposed(s)] for s in TEXT}
GS = {s: [(g["span_char_start"], g["span_char_end"]) for g in GOLD[s]] for s in TEXT}
CS = {s: [(it["span_char_start"], it["span_char_end"]) for it in COLD[s]["items"]] for s in TEXT}


def iou(a, b):
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    u = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / u if u else 0.0


cls = collections.Counter(); retired = collections.Counter(); residual = set()
for seg in sorted(os.listdir(C)):
    t = TEXT[seg]
    for run in (1, 2, 3):
        p = f"{C}/{seg}/run{run}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        assert hashlib.sha256(t.encode()).hexdigest() == d["segment_sha256"], f"{seg} run{run}"
        for r in d["responses"]:
            try:
                obj = json.loads(r["json"]["choices"][0]["message"]["content"])
            except Exception:
                continue
            for o in obj.get("obligations", []):
                st = o.get("span_text", ""); i = t.find(st)
                if i < 0:
                    cls["UNGROUNDED"] += 1; continue
                sp = (i, i + len(st))
                g = max((iou(sp, x) for x in GS[seg]), default=0.0)
                c = max((iou(sp, x) for x in CS[seg]), default=0.0)
                k = "GOLD_MATCH" if g >= 0.5 else ("COLD_ONLY" if c >= 0.5 else "NEITHER")
                cls[k] += 1
                if k == "GOLD_MATCH":
                    continue
                # a disposition covers a candidate that sits inside it, or aligns to it
                cov = any(sp[0] >= a - 2 and sp[1] <= b + 2 for a, b in UD[seg]) \
                    or any(iou(sp, x) >= 0.5 for x in UD[seg])
                retired[k] += bool(cov)
                if not cov:
                    residual.add((seg, k, st[:70]))
assert (cls["GOLD_MATCH"], cls["COLD_ONLY"], cls["NEITHER"], cls["UNGROUNDED"]) == \
    (46, 13, 11, 11), f"KNOWN-ANSWER CHECK vs unexpected.py FAILED: {cls}"
print("  KNOWN-ANSWER CHECK vs unexpected.py (46/13/11/11): PASSED")
unexp = cls["COLD_ONLY"] + cls["NEITHER"]; ret = retired["COLD_ONLY"] + retired["NEITHER"]
print(f"\n  currently UNEXPECTED: {unexp}")
print(f"  RETIRED by populating §4.4 from these dispositions: {ret} ({100*ret/unexp:.0f}%)")
print(f"    COLD_ONLY {retired['COLD_ONLY']}/{cls['COLD_ONLY']}   "
      f"NEITHER {retired['NEITHER']}/{cls['NEITHER']}")
print(f"  RESIDUAL {unexp-ret} -- sub-sentence spans inside already-covered sentences, which")
print( "  §2.7 does NOT reach. R6's caveat is NARROWED, not retired:")
for seg, k, st in sorted(residual):
    print(f"    {seg}  {k:10} | {st}")
