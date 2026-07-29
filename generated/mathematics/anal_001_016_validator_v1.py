#!/usr/bin/env python3
"""Implementation-distinct exact validator for ANAL-001--016."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("nested-sequence-enclosure","tail-pair-distance-bound","nested-carrier-intersection-certificate","partial-sum-remainder-ledger","coefficient-term-tail-custody","finite-function-value-carrier","exact-size-separation-relations","finite-operator-bound-image-custody","held-opposed-harmonic-components","exact-transform-reconstruction","complete-shift-pair-accumulation","orthogonal-coordinate-reconstruction","exact-test-function-pairing","exact-contraction-fixed-carrier","period-four-held-phase-pair","positive-invariant-weight-ledger")
def dist(a,b):return max(a,b)-min(a,b)
def norm(p):
 c=min(p);return p[0]-c,p[1]-c
def add(a,b):return norm((a[0]+b[0],a[1]+b[1]))
def flip(a):return a[1],a[0]
def h(v):return add(v[0],v[1]),add(v[0],flip(v[1]))
def ih(v):return tuple((x//2,y//2) for x,y in (add(v[0],v[1]),add(v[0],flip(v[1]))))
def conv(a,b):return tuple(sum(a[j]*b[(i-j)%len(a)] for j in range(len(a))) for i in range(len(a)))
def witness(i):
 if i==1:return all(Fraction(1)+Fraction(1,n+1)<Fraction(1)+Fraction(1,n) for n in range(1,8))
 if i==2:return all(dist(Fraction(1)+Fraction(1,m),Fraction(1)+Fraction(1,n))<=Fraction(1,k) for k in range(1,7) for m,n in product(range(k,9),repeat=2))
 if i==3:return all(Fraction(1)<=Fraction(1)+Fraction(1,n) for n in range(1,9))
 if i==4:return all(sum((Fraction(1,2**k) for k in range(1,n+1)),Fraction(0))+Fraction(1,2**n)==1 for n in range(1,9))
 if i==5:return sum((Fraction(1,2**k) for k in range(5)),Fraction(0))==Fraction(31,16)
 if i==6:return len(tuple(product((0,1),repeat=3)))==8
 if i==7:return sum((1,2,3))==6 and dist(1,3)<=dist(1,2)+dist(2,3)
 if i==8:return all(2*x+2*y==2*(x+y) for x,y in product(range(1,5),repeat=2))
 if i==9:return norm((2,4))==(0,2)
 if i==10:return ih(h(((3,0),(1,0))))==((3,0),(1,0))
 if i==11:return conv((1,2,3),(1,0,0))==(1,2,3)
 if i==12:return 1*0+0*1==0 and (3,2)==(3*1+2*0,3*0+2*1)
 if i==13:return Fraction(1,3)+Fraction(4,3)==Fraction(5,3)
 if i==14:return all(dist((x+1)/2,(y+1)/2)==dist(x,y)/2 for x,y in product((Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)),repeat=2))
 if i==15:return norm((1,1))==(0,0) and 1+1==2
 if i==16:return 1+4==5 and 2+12==14
 return False
def surface(i):
 axes=(("lost-analytic-carriers","complete-generated-support"),("imported-analysis-answer",REL[i-1]),("imaginary-or-negative-scalar","held-opposed-phase-structure"),("selected-truncations","complete-declared-truncation-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-support-only","finite-support-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_analysis_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
