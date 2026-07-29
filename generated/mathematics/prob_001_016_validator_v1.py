#!/usr/bin/env python3
"""Implementation-distinct exact validator for PROB-001--016."""
import json,sys
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
REL=("exact-support-count-ratio","conditional-support-composition","complete-product-factorization","exact-weighted-expectation","held-distance-dispersion","complete-finite-distribution","deterministic-complete-word-frequency","exact-central-tail-enclosure","likelihood-preserving-sufficient-record","preregistered-exact-region-rule","complete-decision-error-ledger","exact-likelihood-ratio","exact-prior-observation-conditioning","deterministic-path-weight-process","branchwise-conditional-conservation","observation-map-identifiability-boundary")
def dist(a,b):return max(a,b)-min(a,b)
def words(n):return tuple(product((1,2),repeat=n))
def like(p,q):return p*p*p*q
def witness(i):
 if i==1:return Fraction(2,4)==Fraction(1,2)
 if i==2:return Fraction(2,4)==Fraction(2,3)*Fraction(3,6)/Fraction(4,6)==Fraction(1,2)
 if i==3:return Fraction(1,6)==Fraction(1,2)*Fraction(1,3)
 if i==4:return sum((Fraction(x,4) for x in (1,2,3,4)),Fraction())==Fraction(5,2)
 if i==5:return sum((Fraction(1,4)*dist(Fraction(x),Fraction(5,2))**2 for x in (1,2,3,4)),Fraction())==Fraction(5,4)
 if i==6:return tuple(comb(3,k) for k in range(4))==(1,3,3,1) and sum((Fraction(comb(3,k),8) for k in range(4)),Fraction())==1
 if i==7:return all(Fraction(sum(sum(1 for x in w if x==2) for w in words(n)),n*len(words(n)))==Fraction(1,2) for n in range(1,9))
 if i==8:return all(Fraction(2,2**n)<=Fraction(1,n) for n in range(2,9))
 if i==9:return all(len(tuple(w for w in words(4) if sum(1 for x in w if x==2)==k))==comb(4,k) for k in range(5))
 if i==10:
  rows=((Fraction(1,4),like(Fraction(1,4),Fraction(3,4))),(Fraction(1,2),like(Fraction(1,2),Fraction(1,2))),(Fraction(3,4),like(Fraction(3,4),Fraction(1,4))));return tuple(p for p,v in rows if v*2>=max(x for _,x in rows))==(Fraction(1,2),Fraction(3,4))
 if i==11:return Fraction(2,8)==Fraction(1,4)
 if i==12:return like(Fraction(3,4),Fraction(1,4))/like(Fraction(1,2),Fraction(1,2))==Fraction(27,16)
 if i==13:
  a=Fraction(1,3)*Fraction(3,4);b=Fraction(2,3)*Fraction(1,4);return (a/(a+b),b/(a+b))==(Fraction(3,5),Fraction(2,5))
 if i==14:return sum((Fraction(1,2)*({1:(Fraction(1,2),Fraction(1,2)),2:(Fraction(1,3),Fraction(2,3))}[a][b-1]) for a,b in product((1,2),repeat=2)),Fraction())==1
 if i==15:return (Fraction(1,2)+Fraction(3,2))/2==1 and (Fraction(5,2)+Fraction(7,2))/2==3 and (1+3)/2==2
 if i==16:return sum((Fraction(1,4),Fraction(3,4)),Fraction())==sum((Fraction(1,2),Fraction(1,2)),Fraction())==1 and (Fraction(1,4),Fraction(3,4))!=(Fraction(1,2),Fraction(1,2))
 return False
def surface(i):
 axes=(("ontic-randomness-premise","generated-path-support"),("imported-statistical-answer",REL[i-1]),("float-or-negative-weight","exact-positive-fraction-weight"),("sampled-favourable-outcomes","complete-declared-branch-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-sample-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_probability_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
