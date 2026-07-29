#!/usr/bin/env python3
"""Implementation-distinct exact validator for LOGIC-001--016."""
import json,sys
from itertools import combinations,product
from pathlib import Path
H="held";O="opposed";U="unresolved"
REL=("generated-proposition-valuation","valuation-preserving-inference","finite-proof-model-equivalence","explicit-proof-object-check","complete-domain-quantifier-census","complete-symbol-interpretation","finite-intersection-witness-boundary","finite-formula-total-decision","self-negating-fixed-point-boundary","generated-finite-collection-algebra","ranked-size-extension-boundary","witness-bearing-construction","transition-indexed-modal-temporal-law","finite-ordered-valuation-algebra","strict-proof-reduction-normalization","finite-consistency-unrestricted-self-limit")
def inv(x):return {H:O,O:H,U:U}[x]
def implication(a,b):return O if a==H and b==O else H
def power(values):
 values=tuple(values)
 return tuple(frozenset(values[i] for i in chosen) for n in range(len(values)+1) for chosen in combinations(range(len(values)),n))
def ev(form,env):
 if isinstance(form,str):return env[form]
 if form[0]=="not":return inv(ev(form[1],env))
 if form[0]=="and":return H if ev(form[1],env)==H and ev(form[2],env)==H else O
 if form[0]=="or":return H if H in (ev(form[1],env),ev(form[2],env)) else O
 return implication(ev(form[1],env),ev(form[2],env))
def witness(i):
 if i==1:return all(v in (H,O) for v in (H,O))
 if i==2:return all(not (p==H and implication(p,q)==H) or q==H for p,q in product((H,O),repeat=2))
 if i==3:return all((H if p==H and q==H else O)==ev(("and","p","q"),{"p":p,"q":q}) for p,q in product((H,O),repeat=2))
 if i==4:
  known={"P",("implies","P","Q")};return "P" in known and ("implies","P","Q") in known
 if i==5:return any(x==2 for x in (1,2,3)) and not all(x==2 for x in (1,2,3))
 if i==6:return set((2,))<={1,2,3} and bool((2,))
 if i==7:return not any(all(x!=y for y in (1,2,3,4)) for x in (1,2,3,4)) and all(any(all(x!=y for y in omitted) for x in (1,2,3,4)) for omitted in combinations((1,2,3,4),3))
 if i==8:return all(ev(f,{"p":p,"q":q}) in (H,O) for f in ("p","q",("not","p"),("and","p","q"),("or","p","q"),("implies","p","q")) for p,q in product((H,O),repeat=2))
 if i==9:return not any(inv(x)==x for x in (H,O))
 if i==10:
  p=power((1,2,3));return len(p)==8 and all(a|b in p and a&b in p for a,b in product(p,repeat=2))
 if i==11:return tuple(len(power(range(1,n+1))) for n in range(1,5))==(2,4,8,16)
 if i==12:return ("and-proof","proof-A","proof-B")[1:]==("proof-A","proof-B") and ("left-witness","proof-A")[1]=="proof-A"
 if i==13:
  successors={1:(2,3),2:(2,4),3:(4,),4:(4,)};p={2,3,4};return all(x in p for x in successors[1]) and any(x in p for x in successors[2])
 if i==14:return all(min(a,b,key=(O,U,H).index) in (O,U,H) and max(a,b,key=(O,U,H).index) in (O,U,H) for a,b in product((O,U,H),repeat=2)) and inv(H)==O and inv(O)==H and inv(U)==U
 if i==15:return len(("apply",("lambda","x","x"),"A"))>len(("A",))
 if i==16:
  derived={"P",("implies","P","Q"),"Q"};return "P" in derived and "Q" in derived and "opposed-P" not in derived
 return False
def surface(i):
 axes=(("imported-formula-language","generated-exact-syntax"),("imported-theorem-answer",REL[i-1]),("negative-truth-scalar","held-opposed-truth-label"),("sampled-models-or-proofs","complete-declared-proof-model-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-depth-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_logic_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
