import json, glob, itertools
G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
gold = {}
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d = json.load(open(p)); gold[d["item_id"]] = d
cold = {}
for p in sorted(glob.glob(f"{G}/holdout/cold/*.json")):
    d = json.load(open(p)); cold[d["segment_id"]] = d

def iou(a0,a1,b0,b1):
    inter = max(0, min(a1,b1)-max(a0,b0)); union = max(a1,b1)-min(a0,b0)
    return inter/union if union else 0.0

byseg = {}
for it in gold.values(): byseg.setdefault(it["segment_id"], []).append(it)

EPS = 1e-9
dup_gold=[]; dup_cold=[]; tied=[]; ambig_assign=[]
for seg, gitems in sorted(byseg.items()):
    gitems = sorted(gitems, key=lambda x: x["item_id"])
    citems = cold.get(seg, {}).get("items", [])
    # 1. identical spans within an annotator
    for name, items, sink in (("gold",gitems,dup_gold),("cold",citems,dup_cold)):
        seen={}
        for i,x in enumerate(items):
            k=(x["span_char_start"],x["span_char_end"]); seen.setdefault(k,[]).append(i)
        for k,v in seen.items():
            if len(v)>1:
                ids=[items[i].get("item_id", f"cold#{i}") for i in v]
                sink.append((seg,name,k,ids))
    # 2. per-gold-item IoU ties among cold candidates >=0.5
    for g in gitems:
        cands=sorted(((iou(g["span_char_start"],g["span_char_end"],c["span_char_start"],c["span_char_end"]), ci)
                      for ci,c in enumerate(citems)), reverse=True)
        cands=[x for x in cands if x[0]>=0.5]
        if len(cands)>1 and abs(cands[0][0]-cands[1][0])<EPS:
            tied.append((seg,g["item_id"],round(cands[0][0],4),[citems[ci].get("cold_id",f"cold#{ci}") for _,ci in cands[:3]]))
    # 3. is the max-total-IoU assignment unique?
    n,m=len(gitems),len(citems)
    if n and m:
        best=None; sols=[]
        for perm in itertools.permutations(range(m), min(n,m)):
            tot=0.0; used=[]
            for gi,ci in enumerate(perm):
                v=iou(gitems[gi]["span_char_start"],gitems[gi]["span_char_end"],
                      citems[ci]["span_char_start"],citems[ci]["span_char_end"])
                if v>=0.5: tot+=v; used.append((gi,ci))
            key=round(tot,9)
            if best is None or key>best: best=key; sols=[tuple(used)]
            elif key==best and tuple(used) not in sols: sols.append(tuple(used))
        distinct={s for s in sols}
        if len(distinct)>1:
            ambig_assign.append((seg,len(gitems),len(citems),len(distinct),
                                 [[gitems[gi]["item_id"] for gi,_ in s] for s in list(distinct)[:2]]))
print("== identical spans within GOLD ==")
for r in dup_gold: print(" ", r)
print("== identical spans within COLD ==")
for r in dup_cold: print(" ", r)
print("== per-item IoU ties (top-2 equal) ==")
for r in tied: print(" ", r)
print("== segments with a non-unique max-total-IoU assignment ==")
for r in ambig_assign: print(" ", r)
print(f"\ngold items={len(gold)} segments={len(byseg)} cold items={sum(len(c['items']) for c in cold.values())}")
