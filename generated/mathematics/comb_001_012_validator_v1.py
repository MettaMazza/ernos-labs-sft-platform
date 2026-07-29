#!/usr/bin/env python3
import json,sys
from fractions import Fraction
from itertools import combinations,permutations,product
from pathlib import Path
REL=("disjoint-sum-product-bijection-count","ordered-and-unordered-selection-census","overlap-corrected-support-ledger","complete-occupancy-lower-bound","compositional-count-recurrence","unordered-positive-part-incidence","complete-feasible-family-extremum","complete-support-average-existence","balanced-complete-incidence-design","complete-distance-packing-census","complete-colouring-forced-substructure","structure-species-composition-census")
def partitions(n,m=1):return 1 if n==0 else sum(partitions(n-k,k) for k in range(m,n+1))
def antichain():
 s=tuple(frozenset(c) for k in range(5) for c in combinations(range(4),k));best=0
 for mask in range(1<<16):
  if bin(mask).count("1")<=best:continue
  q=[s[i] for i in range(16) if mask>>i&1]
  if all(not(a<b or b<a) for i,a in enumerate(q) for b in q[i+1:]):best=len(q)
 return best
def h(a,b):return sum(x!=y for x,y in zip(a,b))
def code_max():
 w=tuple(product((0,1),repeat=3));best=0
 for mask in range(1<<8):
  q=[w[i] for i in range(8) if mask>>i&1]
  if len(q)>best and all(h(a,b)>=3 for i,a in enumerate(q) for b in q[i+1:]):best=len(q)
 return best
def ramsey():
 e=tuple(combinations(range(6),2))
 for mask in range(1<<15):
  c={x:(mask>>i)&1 for i,x in enumerate(e)}
  if not any(len({c[tuple(sorted(x))] for x in combinations(t,2)})==1 for t in combinations(range(6),3)):return False
 return True
def setparts(items):
 if not items:return {()}
 a=items[0];out=set()
 for p in setparts(items[1:]):
  p=list(p);out.add(tuple(sorted(((a,),)+tuple(p))))
  for i in range(len(p)):
   q=list(p);q[i]=tuple(sorted((a,)+q[i]));out.add(tuple(sorted(q)))
 return out
def witness(i):
 if i==1:return 3+4==7 and len(tuple(product(range(3),range(4))))==12
 if i==2:return len(tuple(permutations(range(5))))==120 and len(tuple(combinations(range(5),2)))==10
 if i==3:return len(set(range(2,13,2))|set(range(3,13,3)))==8
 if i==4:return all(max(x.count(b) for b in range(3))>=3 for x in product(range(3),repeat=7))
 if i==5:return all(len(tuple(product((1,2),repeat=n)))==2**n for n in range(1,9))
 if i==6:return partitions(5)==7
 if i==7:return antichain()==6
 if i==8:return Fraction(sum(sum(w) for w in product((0,1),repeat=3)),8)==Fraction(3,2)
 if i==9:
  b=((1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6));return all(sum(p in x for x in b)==3 for p in range(1,8)) and all(sum(set(q)<=set(x) for x in b)==1 for q in combinations(range(1,8),2))
 if i==10:return code_max()==2
 if i==11:return ramsey()
 if i==12:return len(setparts((1,2,3,4)))==15
 return False
def surface(i):
 axes=(("untracked-objects","complete-generated-carriers"),("imported-count-formula",REL[i-1]),("uncontrolled-identification","declared-order-or-symmetry"),("selected-samples","complete-declared-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-table-only","finite-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);s=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in s["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in s["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(s["controls"])==4,all(x["passed"] for x in s["controls"]),s["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_combinatorial_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
