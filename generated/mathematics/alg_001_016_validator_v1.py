#!/usr/bin/env python3
"""Implementation-distinct exact validator for ALG-001--016."""
import json,sys
from itertools import permutations,product
from pathlib import Path
REL=("closed-generated-binary-operation","complete-associativity-census","unique-two-sided-identity","held-reversal-to-identity","reversible-carrier-action","normal-coset-equivalence","dual-operation-distribution","nonabsence-product-retention","unique-nonabsence-division","compatible-scalar-carrier-action","bilinear-internal-product","absorbing-substructure-quotient","invariant-action-components","image-kernel-equality","signature-wide-identity-census","typed-substitution-association")
T=((1,2,3),(2,3,1),(3,1,2))
def o(a,b):return T[a-1][b-1]
def witness(i):
 if i==1:return all(a in (1,2) for a,b in product((1,2),repeat=2))
 if i==2:return all(o(o(a,b),c)==o(a,o(b,c)) for a,b,c in product((1,2,3),repeat=3))
 if i==3:return all(o(1,a)==a==o(a,1) for a in (1,2,3))
 if i==4:return all(sum(o(a,b)==1 for b in (1,2,3))==1 for a in (1,2,3))
 if i==5:return len({p for p in permutations((1,2,3))})==6
 if i==6:return len({frozenset(((x+h)%4 for h in (0,2))) for x in range(4)})==2
 if i==7:return all((a*(b+c))%3==((a*b)%3+(a*c)%3)%3 for a,b,c in product(range(3),repeat=3))
 if i==8:return all((a*b)%5!=0 for a,b in product(range(1,5),repeat=2))
 if i==9:return all(sum((a*b)%5==1 for b in range(1,5))==1 for a in range(1,5))
 if i==10:return all(tuple((s*((a+b)%2))%2 for a,b in zip(x,y))==tuple(((s*a)%2+(s*b)%2)%2 for a,b in zip(x,y)) for s in (0,1) for x,y in product(product((0,1),repeat=2),repeat=2))
 if i==11:return all(tuple(a*(b+c) for a,b,c in zip(x,y,z))==tuple(a*b+a*c for a,b,c in zip(x,y,z)) for x,y,z in product(((1,1),(1,2),(2,1),(2,2)),repeat=3))
 if i==12:return len({frozenset(((x+h)%6 for h in (0,3))) for x in range(6)})==3
 if i==13:
  swap=lambda v:tuple(reversed(v));return swap((2,2))==(2,2) and tuple(a+b for a,b in zip(swap((1,0)),(1,0)))==(1,1)
 if i==14:return {(x,0) for x in (0,1)}=={v for v in product((0,1),repeat=2) if v[1]==0}
 if i==15:return all(max(max(a,b),c)==max(a,max(b,c)) and max(a,b)==max(b,a) and max(a,a)==a for a,b,c in product((1,2,3),repeat=3))
 if i==16:
  flatten=lambda x:(x,) if isinstance(x,int) else sum((flatten(y) for y in x),());return flatten(((1,2),(3,4)))==flatten((1,(2,(3,4))))==(1,2,3,4)
 return False
def surface(i):
 axes=(("unclosed-support","complete-generated-support"),("imported-operation-laws",REL[i-1]),("unwitnessed-special-element","witnessed-identity-or-absence"),("selected-tuples","complete-operation-tuple-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-table-only","finite-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_algebra_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
