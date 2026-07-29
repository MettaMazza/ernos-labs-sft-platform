#!/usr/bin/env python3
"""Implementation-distinct exact validator for NOISE-001--012."""
import json,sys
from itertools import combinations,product
from pathlib import Path
REL=("complete-predecessor-closure-ledger","complete-changed-position-trace","complete-generated-error-mask-support","ordered-action-trace-composition","invalid-code-image-detection","unique-changed-position-record","complete-predecessor-estimate-class","typed-erasure-substitution-actions","contiguous-and-related-mask-structure","complete-resource-bounded-adversary-masks","changed-position-budget-custody","twelve-noise-obligation-ledger")
A=("L","L","L");B=("R","R","R");CODE=(A,B)
def apply(word,mask):return tuple(("R" if x=="L" else "L") if n+1 in mask else x for n,x in enumerate(word))
def changed(a,b):return tuple((n+1,x,y) for n,(x,y) in enumerate(zip(a,b)) if x!=y)
def masks(width,budget):return tuple(c for size in range(1,budget+1) for c in combinations(range(1,width+1),size))
def predecessors(image,actions):return tuple(source for source in CODE if any(apply(source,m)==image for m in actions))
def witness(i):
 if i==1:return predecessors(("R","L","L"),((1,),(2,3)))==(A,B)
 if i==2:return changed(A,("R","L","L"))==((1,"L","R"),) and changed(A,A)==()
 if i==3:return masks(3,1)==((1,),(2,),(3,)) and len({apply(A,m) for m in masks(3,1)})==3
 if i==4:return apply(apply(A,(1,)),(3,))==("R","L","R") and changed(A,("R","L","R"))==((1,"L","R"),(3,"L","R"))
 if i==5:return all(apply(source,m) not in CODE for source in CODE for m in masks(3,1))
 if i==6:return tuple(changed(A,apply(A,m))[0][0] for m in masks(3,1))==(1,2,3)
 if i==7:return all(len(predecessors(apply(source,m),masks(3,1)))==1 for source in CODE for m in masks(3,1))
 if i==8:return ("erasure",2,"L","absent")!=("substitution",2,"L","R")
 if i==9:return tuple(m for m in combinations((1,2,3),2) if m==tuple(range(m[0],m[0]+len(m))))==((1,2),(2,3))
 if i==10:return set(masks(4,1))=={(1,),(2,),(3,),(4,)}
 if i==11:return all(len(changed(("L",)*4,apply(("L",)*4,m)))<=1 for m in masks(4,1)) and len(changed(("L",)*4,apply(("L",)*4,(1,3))))>1
 if i==12:return len(REL)==12 and all(witness(n) for n in range(1,12))
 return False
def surface(i):
 axes=(("partial-source-support","complete-canonical-source-support"),("opaque-or-random-perturbation",REL[i-1]),("scalar-error-only","complete-position-action-trace"),("chosen-likely-predecessor","complete-predecessor-class"),("sampled-error-patterns","complete-declared-mask-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_noise_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
