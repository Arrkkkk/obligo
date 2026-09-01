# Standing Principle 7: prove the detector FIRES on a planted instance before
# trusting its "C04-139 is the only one" verdict.
import json, glob, itertools, copy
G = "/Users/rajitagrawal/obligo/apps/brain/evals/goldens"
gold={}
for p in glob.glob(f"{G}/batch0*/items/*.json"):
    d=json.load(open(p)); gold[d["item_id"]]=d
cold={}
for p in sorted(glob.glob(f"{G}/holdout/cold/*.json")):
    d=json.load(open(p)); cold[d["segment_id"]]=d
def iou(a0,a1,b0,b1):
    inter=max(0,min(a1,b1)-max(a0,b0)); union=max(a1,b1)-min(a0,b0)
    return inter/union if union else 0.0
def audit(gold, cold):
    byseg={}
    for it in gold.values(): byseg.setdefault(it["segment_id"],[]).append(it)
    hits=[]
    for seg,gitems in sorted(byseg.items()):
        citems=cold.get(seg,{}).get("items",[])
        seen={}
        for x in gitems: seen.setdefault((x["span_char_start"],x["span_char_end"]),[]).append(x["item_id"])
        for k,v in seen.items():
            if len(v)>1: hits.append((seg,"dup_gold",v))
        for g in gitems:
            c=sorted((iou(g["span_char_start"],g["span_char_end"],x["span_char_start"],x["span_char_end"]) for x in citems),reverse=True)
            c=[v for v in c if v>=0.5]
            if len(c)>1 and abs(c[0]-c[1])<1e-9: hits.append((seg,"tie",g["item_id"]))
    return hits
print("baseline:", audit(gold, cold))
# plant a clone of C02-01 in its own segment; C02-021 cold side has >=2 items?
g2=copy.deepcopy(gold); base=g2["C02-01"]
clone=copy.deepcopy(base); clone["item_id"]="ZZ-99"; g2["ZZ-99"]=clone
seg=base["segment_id"]
print(f"planted clone of C02-01 in {seg} (cold items there: {len(cold[seg]['items'])})")
print("with plant:", audit(g2, cold))
