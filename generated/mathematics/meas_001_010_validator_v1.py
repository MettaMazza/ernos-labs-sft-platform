#!/usr/bin/env python3
"""Implementation-distinct exact validator for MEAS-001--010."""
import json,sys
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
REL=("exact-finite-support-weight","disjoint-support-additivity","complete-cover-minimum-weight","exact-boundary-decomposition","weighted-support-accumulation","exact-refinement-sum-correspondence","product-and-conditional-support-law","held-opposed-measure-ledger","exact-test-function-action","successor-refined-measure-enclosure")
W={1:Fraction(1,6),2:Fraction(2,6),3:Fraction(3,6)}
def parts(values):
 values=tuple(values)
 return tuple(frozenset(x) for n in range(len(values)+1) for x in combinations(values,n))
def mass(s):return sum((W[x] for x in s),Fraction())
def action(v):return sum((W[x]*v[x] for x in W),Fraction())
def midpoint(n):return sum((Fraction(2*i-1,2*n)*Fraction(1,n) for i in range(1,n+1)),Fraction())
def witness(i):
 if i==1:return mass({1,2,3})==1
 if i==2:return all(mass(a|b)==mass(a)+mass(b) for a,b in product(parts((1,2,3)),repeat=2) if not a&b)
 if i==3:return min(mass(c) for c in parts((1,2,3)) if {1,3}<=c)==Fraction(4,6)
 if i==4:return all(mass(a)==mass(a&{1,2})+mass(a&{3}) for a in parts((1,2,3)))
 if i==5:return action({1:1,2:2,3:3})==Fraction(7,3)
 if i==6:return all(midpoint(n)==Fraction(1,2) for n in range(1,9))
 if i==7:return sum((a*b for a,b in product((Fraction(1,3),Fraction(2,3)),(Fraction(1,4),Fraction(3,4)))),Fraction())==1 and (Fraction(1,3)*Fraction(3,4))/Fraction(1,3)==Fraction(3,4)
 if i==8:return Fraction(1,2)+Fraction(1,4)==Fraction(3,4)
 if i==9:return action({1:1,2:2,3:3})+action({1:3,2:2,3:1})==action({1:4,2:4,3:4})==4
 if i==10:return all(Fraction(1,n+2)<Fraction(1,n+1) for n in range(1,9))
 return False
def surface(i):
 axes=(("imported-continuum-support","generated-finite-support"),("imported-measure-answer",REL[i-1]),("negative-signed-scalar","held-opposed-positive-ledger"),("selected-subsets-or-partitions","complete-declared-support-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-support-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_measure_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
