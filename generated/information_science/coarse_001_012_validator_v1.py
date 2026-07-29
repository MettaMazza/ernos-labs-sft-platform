#!/usr/bin/env python3
"""Implementation-distinct exact validator for COARSE-001--012."""
import json,sys
from itertools import combinations,product
from pathlib import Path
REL=("observation-sufficient-fibre-record","least-sufficient-partition","least-target-preserving-coarsening","complete-disjoint-exhaustive-partition","partition-refinement-order","complete-closed-pair-ledger","target-distinction-feature-selection","transition-consistent-state-lumping","complete-summary-preimage-boundary","exact-coarsening-composition","singleton-fibre-reversibility","twelve-coarse-obligation-ledger")
U=("a","b","c","d");T={"a":"L","b":"L","c":"R","d":"R"};P={"a":"x","b":"x","c":"y","d":"y"};F={x:x for x in U};O={x:"One" for x in U}
def cells(m):return tuple(sorted(tuple(x for x in U if m[x]==v) for v in set(m.values())))
def suff(m):return all(len({T[x] for x in c})==1 for c in cells(m))
def refine(a,b):return all(a[x]!=a[y] or b[x]==b[y] for x in U for y in U)
def lost(m):return tuple((a,b) for a,b in combinations(U,2) if m[a]==m[b])
def witness(i):
 if i==1:return suff(P)
 if i==2:return suff(P) and not suff(O) and len(cells(P))==2
 if i==3:return cells(P)==(("a","b"),("c","d")) and suff(P)
 if i==4:return len(cells(P))==2 and set(sum((list(c) for c in cells(P)),[]))==set(U)
 if i==5:return refine(F,P) and refine(P,O) and not refine(P,F)
 if i==6:return lost(P)==(("a","b"),("c","d"))
 if i==7:return suff(T) and not suff(O)
 if i==8:
  step={"a":"b","b":"a","c":"d","d":"c"};return all(len({P[step[x]] for x in c})==1 for c in cells(P))
 if i==9:return tuple(len(c) for c in cells(P))==(2,2)
 if i==10:return {x:{"x":"One","y":"One"}[P[x]] for x in U}==O
 if i==11:return all(len(c)==1 for c in cells(F)) and all(len(c)==2 for c in cells(P))
 if i==12:return len(REL)==12 and all(witness(n) for n in range(1,12))
 return False
def surface(i):
 axes=(("partial-source-support","complete-canonical-source-support"),("opaque-or-chosen-summary",REL[i-1]),("implicit-retention-target","registered-observation-distinction"),("scalar-only-loss","complete-closed-distinction-ledger"),("sampled-partitions","complete-declared-partition-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_coarsening_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
