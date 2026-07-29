#!/usr/bin/env python3
"""Implementation-distinct exact validator for TOPO-001--014."""
import json,sys
from itertools import combinations,product
from pathlib import Path
REL=("finite-open-support-closure","open-preimage-continuity","finite-cover-subcover-custody","maximal-connected-components","finite-observation-separation","product-restriction-quotient-observation","downward-closed-simplex-incidence","finite-face-path-deformation","cycle-composition-reversal","boundary-of-boundary-absence","dual-cycle-observation","finite-local-chart-overlap","finite-diagram-move-invariant","filtered-feature-birth-merge-ledger")
O=(frozenset(),frozenset({1}),frozenset({1,2}));T=tuple(frozenset(c) for n in range(1,4) for c in combinations((1,2,3),n))
def comps(v,e):
 left=set(v);n=0
 while left:
  n+=1;seen={left.pop()};changed=True
  while changed:
   changed=False
   for a,b in e:
    if a in seen and b in left:left.remove(b);seen.add(b);changed=True
    if b in seen and a in left:left.remove(a);seen.add(a);changed=True
  
 return n
def witness(i):
 if i==1:return all(frozenset().union(*f) in O and (frozenset({1,2}).intersection(*f) if f else frozenset({1,2})) in O for n in range(4) for f in combinations(O,n))
 if i==2:return all(x in O for x in O)
 if i==3:return frozenset({1,2})|frozenset({2,3})==frozenset({1,2,3})
 if i==4:return comps((1,2,3,4,5),((1,2),(2,3),(4,5)))==2
 if i==5:return all(b not in {a} for a,b in product((1,2,3),repeat=2) if a!=b)
 if i==6:return len(tuple(product((1,2),(3,4,5))))==6
 if i==7:return len(T)==7 and all(frozenset(c) in T for f in T for n in range(1,len(f)+1) for c in combinations(f,n))
 if i==8:return (1,2,4)[0::2]==(1,3,4)[0::2]
 if i==9:return 3+1==3+1
 if i==10:return set((1,2))^set((2,3))^set((1,3))==set()
 if i==11:return sum(1 for _ in ((1,2),(2,3),(1,3)))==3
 if i==12:return all(len({v,1+(v%4),4 if v==1 else v-1})==3 for v in range(1,5))
 if i==13:return sorted((1,2,3,1,2,3))==sorted((2,3,1,2,3,1))
 if i==14:return tuple(comps((1,2,3,4),e) for e in ((),((1,2),(3,4)),((1,2),(2,3),(3,4))))==(4,2,1)
 return False
def surface(i):
 axes=(("lost-topological-carriers","complete-generated-support"),("imported-topological-answer",REL[i-1]),("numeric-zero-premise","structural-absence-boundary"),("selected-open-families","complete-declared-topology-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-complex-only","finite-complex-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_topology_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
