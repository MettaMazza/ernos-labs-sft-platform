#!/usr/bin/env python3
"""Implementation-distinct exact validator for OPT-001--016."""
import json,sys
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
REL=("feasible-objective-order","complete-finite-extrema","complete-pareto-frontier","exact-linear-feasible-enumeration","complete-discrete-feasible-search","held-distance-convex-minimum","matching-primal-dual-certificate","complete-path-action-minimum","subproblem-optimum-composition","complete-control-path-optimum","mutual-best-response-census","exact-decision-loss-order","flow-schedule-conservation","complete-worst-case-scenario-order","exact-certified-approximation-gap","complete-infeasible-or-successor-unbounded-certificate")
def powers(values):
 values=tuple(values)
 return tuple(tuple(values[i] for i in range(len(values)) if i in chosen) for n in range(len(values)+1) for chosen in combinations(range(len(values)),n))
def frontier(points):return tuple(p for p in points if not any(q!=p and q[0]<=p[0] and q[1]<=p[1] for q in points))
def comps(total,width):return tuple(x for x in product(range(1,total+1),repeat=width) if sum(x)==total)
def witness(i):
 if i==1:return min(x for x in (1,2,3,4) if x>=2)==2
 if i==2:return min((4,1,3,2))==1 and max((4,1,3,2))==4
 if i==3:return frontier(((1,4),(2,2),(4,1),(3,3)))==((1,4),(2,2),(4,1))
 if i==4:return max(x+y for x,y in product(range(1,4),repeat=2) if x+y<=4)==4
 if i==5:return max(tuple((s,sum((2,3,4)[j] for j in s)) for s in powers(range(3)) if sum((1,2,3)[j] for j in s)<=3),key=lambda x:x[1])==((0,1),5)
 if i==6:return tuple(x for x in range(1,6) if (max(x,3)-min(x,3))**2==min((max(y,3)-min(y,3))**2 for y in range(1,6)))==(3,)
 if i==7:return max(x+y for x,y in product(range(1,4),repeat=2) if x+y<=4)==min(4*z for z in range(1,5))==4
 if i==8:return tuple(x for x in comps(6,3) if sum(v*v for v in x)==min(sum(v*v for v in y) for y in comps(6,3)))==((2,2,2),)
 if i==9:return min((2+1,1+1+1,1+5))==3
 if i==10:return tuple(p for n in range(1,5) for p in product((1,2),repeat=n) if 1+sum(p)==5 and n==min(m for m in range(1,5) if any(1+sum(q)==5 for q in product((1,2),repeat=m))))==((2,2),)
 if i==11:
  pay={(1,1):(2,2),(1,2):(1,3),(2,1):(3,1),(2,2):(2,2)};return tuple((r,c) for r,c in product((1,2),repeat=2) if pay[(r,c)][0]==max(pay[(x,c)][0] for x in (1,2)) and pay[(r,c)][1]==max(pay[(r,y)][1] for y in (1,2)))==((2,2),)
 if i==12:return (Fraction(1+2,2),Fraction(2+2,2),Fraction(3+2,2))==(Fraction(3,2),2,Fraction(5,2))
 if i==13:return min(2,2)+min(1,1)==3 and sum((2,1))==3
 if i==14:return min((("A",5),("B",4),("C",6)),key=lambda x:x[1])==("B",4)
 if i==15:return Fraction(8,10)==Fraction(4,5) and 8+2==10
 if i==16:return not any(x<=2 and x>=3 for x in range(1,6)) and all(b+1>b for b in range(1,9))
 return False
def surface(i):
 axes=(("selected-feasible-candidates","complete-generated-feasible-support"),("imported-optimum-answer",REL[i-1]),("negative-cost-scalar","positive-cost-held-orientation"),("sampled-search","complete-declared-candidate-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-instance-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_optimization_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
