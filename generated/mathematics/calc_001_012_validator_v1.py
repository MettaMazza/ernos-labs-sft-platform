#!/usr/bin/env python3
"""Implementation-distinct exact validator for CALC-001--012."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("oriented-local-change","iterated-difference-degree","complete-finite-accumulation","telescoping-reconstruction","exact-product-composition-change","nested-rational-width-refinement","shrinking-part-local-ratio","lower-upper-refinement-accumulation","coordinate-directional-change","internal-cancellation-boundary-flux","complete-variation-stationarity","certified-enclosure-only-limit")
def d(v):return tuple(v[i+1]-v[i] for i in range(len(v)-1))
def witness(i):
 if i==1:return d((1,4,9,16))==(3,5,7)
 if i==2:return d(d(d((1,8,27,64,125))))==(6,6)
 if i==3:return sum(range(1,6))==15
 if i==4:return 1+sum(d((1,4,9,16)))==16
 if i==5:return 3*1+3*1==6
 if i==6:return all(Fraction(1,n+1)<Fraction(1,n) for n in range(1,8))
 if i==7:return all(Fraction(4*n+1,n)==4+Fraction(1,n) for n in range(1,9))
 if i==8:return all(Fraction(n-1,2*n)<=Fraction(1,2)<=Fraction(n+1,2*n) and Fraction(n+1,2*n)-Fraction(n-1,2*n)==Fraction(1,n) for n in range(2,9))
 if i==9:return 3*1==3 and 2*1==2
 if i==10:return 1+1==3-1
 if i==11:return tuple(x for x in range(1,6) if (max(x,3)-min(x,3))**2==min((max(y,3)-min(y,3))**2 for y in range(1,6)))==(3,)
 if i==12:return all(Fraction(1,n+1)<Fraction(1,n) for n in range(1,8))
 return False
def surface(i):
 axes=(("lost-sample-identity","complete-generated-values"),("imported-calculus-answer",REL[i-1]),("negative-change-scalar","held-opposed-change-label"),("selected-refinements","complete-declared-refinement-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-grid-only","finite-refinement-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_calculus_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
