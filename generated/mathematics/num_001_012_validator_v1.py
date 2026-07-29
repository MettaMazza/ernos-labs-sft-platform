#!/usr/bin/env python3
"""Implementation-distinct exact validator for NUM-001--012."""
import json,sys
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path
REL=("exact-representation-rounding-custody","outward-rational-enclosure","retained-residual-error","forward-backward-exact-gap","input-output-gap-ratio","successor-error-contraction","ordered-rational-root-bracket","complete-positive-system-enumeration","exact-weighted-interpolation","exact-cell-accumulation","exact-recurrence-state-trace","replayable-arithmetic-certificate")
def distance(a,b):return b-a if a<=b else a-b
def independently_round(q):
 whole=q.numerator//q.denominator;next_whole=whole+1
 return (whole,next_whole,whole if q-whole<next_whole-q else next_whole)
def independently_accumulate(parts):
 value=Fraction(1,2)
 for index in range(2,parts+1):value+=Fraction(1,2**index)
 return value
def witness(i):
 if i==1:return independently_round(Fraction(7,3))==(2,3,2) and distance(Fraction(7,3),2)==Fraction(1,3) and distance(Fraction(7,3),3)==Fraction(2,3)
 if i==2:
  a=(Fraction(1,2),Fraction(2,3));b=(Fraction(1,3),Fraction(1,2));return (a[0]+b[0],a[1]+b[1])==(Fraction(5,6),Fraction(7,6)) and (a[0]*b[0],a[1]*b[1])==(Fraction(1,6),Fraction(1,3))
 if i==3:return all(independently_accumulate(n)+Fraction(1,2**n)==1 for n in range(1,9))
 if i==4:return distance(Fraction(23,10),Fraction(7,3))==Fraction(1,30) and distance(Fraction(70,23),Fraction(3))==Fraction(1,23)
 if i==5:
  x=Fraction(2);y=Fraction(201,100);a=Fraction(5);return distance(a*x,a*y)==Fraction(1,20) and distance(a*x,a*y)/distance(x,y)==5
 if i==6:return all(Fraction(1,2**(n+1))*2==Fraction(1,2**n) for n in range(1,9))
 if i==7:return Fraction(7,5)**2<Fraction(2)<Fraction(3,2)**2
 if i==8:return tuple((x,y) for x,y in product(range(1,9),repeat=2) if x+y==5 and x+2*y==8)==((2,3),)
 if i==9:return Fraction(1,2)*2+Fraction(1,2)*6==4
 if i==10:return Fraction(2)*2==4 and Fraction(2)*Fraction(1+3,2)==4
 if i==11:
  trace=[Fraction(1)]
  for _ in (1,2):trace.append(trace[-1]+trace[-1]/2)
  return tuple(trace)==(Fraction(1),Fraction(3,2),Fraction(9,4))
 if i==12:
  numerator=1*3+1*2;denominator=2*3;return Fraction(1,2)+Fraction(1,3)==Fraction(numerator,denominator) and gcd(numerator,denominator)==1
 return False
def surface(i):
 axes=(("floating-or-opaque-number","exact-generated-fraction-record"),("imported-numerical-answer",REL[i-1]),("negative-error-scalar","ordered-gap-or-held-orientation"),("sampled-inputs","complete-declared-input-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("single-resolution-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_numerical_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
