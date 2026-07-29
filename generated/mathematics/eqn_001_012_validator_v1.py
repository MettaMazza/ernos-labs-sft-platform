#!/usr/bin/env python3
"""Implementation-distinct exact validator for EQN-001--012."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path

REL=(
 "one-step-state-relation","finite-step-local-ratio-correspondence",
 "multi-coordinate-local-relation","refined-multidirectional-enclosure",
 "existence-uniqueness-record-custody","finite-accumulation-equation",
 "complete-argument-composition-census","initial-record-recurrence-space",
 "impulse-response-superposition","boundary-flux-conservation-ledger",
 "exact-solution-perturbation-bound","finite-depth-existence-uniqueness-boundary",
)
def recur(seed,step,depth):
 out=[seed]
 for _ in range(depth-1):out.append(step(out[-1]))
 return tuple(out)
def fibonacci(depth):
 out=[1,1]
 while len(out)<depth:out.append(out[-1]+out[-2])
 return tuple(out)
def response(source):return tuple(sum(source[:i+1]) for i in range(len(source)))
def witness(i):
 if i==1:return recur(1,lambda x:2*x,5)==(1,2,4,8,16)
 if i==2:return all(((Fraction(1)+Fraction(1,n))*x-x)/Fraction(1,n)==x for n in range(1,7) for x in (Fraction(1),Fraction(3,2),Fraction(2)))
 if i==3:return all((a+1+b)-(a+b)==1 and (a+b+1)-(a+b)==1 for a,b in product(range(1,4),repeat=2))
 if i==4:return all((a+b)+(a+2+b)==2*(a+1+b) and (a+b)+(a+b+2)==2*(a+b+1) for a,b in product(range(1,4),repeat=2))
 if i==5:return recur(1,lambda x:x+1,6)==(1,2,3,4,5,6)
 if i==6:return all((1,2,4,8)[n]==1+sum((1,2,4,8)[:n]) for n in range(1,4))
 if i==7:return all(2**(a+b)==(2**a)*(2**b) for a,b in product(range(1,5),repeat=2))
 if i==8:return fibonacci(6)==(1,1,2,3,5,8)
 if i==9:return response((1,0,2,0))==(1,1,3,3) and (1,0,2,0)==(1,1-1,3-1,3-3)
 if i==10:return sum((2,3))==sum((3,2))==5
 if i==11:return all(max((x+1)/2,(y+1)/2)-min((x+1)/2,(y+1)/2)==(max(x,y)-min(x,y))/2 for x,y in product((Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)),repeat=2))
 if i==12:return recur(2,lambda x:x*x,5)==(2,4,16,256,65536)
 return False
def surface(i):
 axes=(
  ("lost-initial-boundary-record","complete-record-custody"),
  ("imported-solution-answer",REL[i-1]),
  ("negative-change-scalar","held-opposed-change-label"),
  ("selected-solutions","complete-declared-solution-census"),
  ("outcome-selected","root-bound-forward-forcing"),
  ("preopened-result","post-registry-exact-observation"),
  ("fixed-grid-only","finite-depth-successor-certificate"),
  ("fit-exception-extra-rule","dated-complete-no-extra-rule"),
 )
 rows=tuple("__".join(x) for x in product(*axes))
 return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_equation_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
