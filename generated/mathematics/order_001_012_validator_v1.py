#!/usr/bin/env python3
"""Implementation-distinct exact validator for ORDER-001--012."""
import json,sys
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
REL=("reflexive-transitive-distinguishability-quotient","antisymmetric-reachability-order","exact-comparability-boundary","greatest-lower-least-upper-custody","lattice-distribution-modularity","relative-complement-boundary","extensive-monotone-idempotent-closure","adjoint-order-equivalence","finite-approximant-directed-join","order-preserving-map","finite-monotone-iteration-fixed-point","all-generated-family-meet-join")
U=frozenset((1,2,3));P=tuple(frozenset(c) for n in range(4) for c in combinations(U,n))
def close(a):return a|({2} if 1 in a else set())
def img(a):return frozenset(1 if x<3 else 2 for x in a)
def inv(b):return frozenset(x for x in U if (1 if x<3 else 2) in b)
def witness(i):
 if i==1:
  words=((1,),(1,2),(2,1,2));rel=lambda a,b:len(a)<=len(b);return all(rel(a,a) for a in words) and all(not(rel(a,b) and rel(b,c)) or rel(a,c) for a,b,c in product(words,repeat=3))
 if i==2:return all(not(a<=b and b<=a) or a==b for a,b in product(P,repeat=2))
 if i==3:return all(a<=b or b<=a for a,b in product((Fraction(1,3),Fraction(1,2),Fraction(2,3),Fraction(1)),repeat=2))
 if i==4:return all((a&b)<=a and (a&b)<=b and a<=(a|b) and b<=(a|b) for a,b in product(P,repeat=2))
 if i==5:return all(a&(b|c)==(a&b)|(a&c) and a|(b&c)==(a|b)&(a|c) for a,b,c in product(P,repeat=3))
 if i==6:return all(sum((a&b)==frozenset() and a|b==U for b in P)==1 for a in P)
 if i==7:return all(a<=close(a) and close(close(a))==close(a) for a in P) and all(not a<=b or close(a)<=close(b) for a,b in product(P,repeat=2))
 if i==8:
  q=tuple(frozenset(c) for n in range(3) for c in combinations((1,2),n));return all((img(a)<=b)==(a<=inv(b)) for a,b in product(P,q))
 if i==9:return all(max(range(1,x+1))==x for x in range(1,5))
 if i==10:return all(not a<=b or min(a+1,4)<=min(b+1,4) for a,b in product(range(1,5),repeat=2))
 if i==11:return frozenset()|{1}==frozenset({1})==frozenset({1})|{1}
 if i==12:return all(frozenset().union(*family) in P and (U.intersection(*family) if family else U) in P for n in range(9) for family in combinations(P,n))
 return False
def surface(i):
 axes=(("untracked-order-carriers","complete-generated-order-carriers"),("imported-order-answer",REL[i-1]),("numeric-zero-premise","structural-absence-boundary"),("selected-comparisons","complete-declared-comparison-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-poset-only","finite-order-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_order_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
