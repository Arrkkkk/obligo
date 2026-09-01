import json, glob
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
byseg={}
for it in gold.values(): byseg.setdefault(it["segment_id"],[]).append(it)
rows=[]
for seg,gitems in sorted(byseg.items()):
    citems=cold.get(seg,{}).get("items",[])
    for g in sorted(gitems,key=lambda x:x["item_id"]):
        c=sorted((iou(g["span_char_start"],g["span_char_end"],x["span_char_start"],x["span_char_end"])
                  for x in citems),reverse=True)
        above=[v for v in c if v>=0.5]
        top=c[0] if c else 0.0
        second=c[1] if len(c)>1 else 0.0
        rows.append((g["item_id"],len(above),round(top,3),round(second,3),round(top-second,3)))
rows.sort(key=lambda r:r[4])
print(f'{"item":9} {"n>=.5":5} {"top":>6} {"2nd":>6} {"margin":>7}')
for r in rows: print(f'{r[0]:9} {r[1]:5} {r[2]:6.3f} {r[3]:6.3f} {r[4]:7.3f}')
n_multi=sum(1 for r in rows if r[1]>1)
print(f"\nitems with >1 candidate above IoU 0.5: {n_multi} of {len(rows)}")
print("smallest nonzero margin among those:",
      min([r[4] for r in rows if r[1]>1 and r[4]>0], default=None))
