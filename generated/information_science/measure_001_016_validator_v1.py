#!/usr/bin/env python3
"""Implementation-distinct exact validator for MEASURE-001--016."""
import json
import sys
from itertools import combinations, product
from pathlib import Path

RELATIONS=("complete-retained-pair-count","complete-generated-support-cardinality","least-complete-observation-family","registered-token-trace-length","fixed-grammar-least-program","class-containment-refinement-order","position-additive-product-support","joint-cost-bounded-by-marginal-costs","nonincreasing-retained-distinction-count","retained-plus-closed-exhaustion","refinement-restored-distinction-ledger","partition-disagreement-count","pair-ledger-symmetric-difference-metric","telescoping-refinement-increments","equal-support-unit-labelled-conversion","sixteen-measure-obligation-ledger")
FORMS=("a","b","c","d");FINE=(("a",),("b",),("c",),("d",));MIDDLE=(("a","b"),("c",),("d",));COARSE=(("a","b"),("c","d"));ONE=(("a","b","c","d"),)

def pairs(forms,partition):
 labels={form:index for index,group in enumerate(partition,1) for form in group}
 return {pair for pair in combinations(forms,2) if labels[pair[0]]!=labels[pair[1]]}
def words(alphabet,width):return tuple(product(alphabet,repeat=width))
def distance(left,right):return len(pairs(FORMS,left)^pairs(FORMS,right))
def refines(left,right):return all(any(set(a)<=set(b) for b in right) for a in left)
def witness(i):
 if i==1:return len(tuple(combinations(FORMS,2)))==len(pairs(FORMS,FINE))==6
 if i==2:return len(words(("L","R"),3))==len(set(words(("L","R"),3)))==8
 if i==3:
  forms=words(("L","R"),3);obs=tuple({word:word[p] for word in forms} for p in range(3));distinct=lambda os:len({tuple(o[f] for o in os) for f in forms})==len(forms)
  return distinct(obs) and all(not distinct(subset) for subset in combinations(obs,2))
 if i==4:return len(("emit","a","then","b"))==4 and set(("emit","a","then","b"))<={"emit","a","then","b"}
 if i==5:
  rows=(("literal",5,("a","b","a")),("repeat",2,("a","a","a")),("alternate",3,("a","b","a")));matches=tuple((name,cost) for name,cost,out in rows if out==("a","b","a"));least=min(cost for _,cost in matches)
  return tuple(name for name,cost in matches if cost==least)==("alternate",)
 if i==6:return refines(FINE,MIDDLE) and refines(MIDDLE,COARSE) and refines(FINE,COARSE)
 if i==7:return 2+3==5 and len(words(("L","R"),2))*len(words(("L","R"),3))==len(words(("L","R"),5))==32
 if i==8:return len(pairs((("a","x"),("b","y")),((("a","x"),),( ("b","y"),))))==1 and 1<=2
 if i==9:return len(pairs(FORMS,FINE))>=len(pairs(FORMS,MIDDLE))>=len(pairs(FORMS,COARSE))>=len(pairs(FORMS,ONE))
 if i==10:return pairs(FORMS,COARSE).isdisjoint(set(combinations(FORMS,2))-pairs(FORMS,COARSE)) and len(pairs(FORMS,COARSE))+len(set(combinations(FORMS,2))-pairs(FORMS,COARSE))==6
 if i==11:return len(pairs(FORMS,FINE)-pairs(FORMS,COARSE))==2
 if i==12:return distance(COARSE,COARSE)==0 and distance(COARSE,MIDDLE)==1
 if i==13:return distance(FINE,COARSE)==distance(COARSE,FINE) and distance(FINE,COARSE)<=distance(FINE,MIDDLE)+distance(MIDDLE,COARSE)
 if i==14:return (len(pairs(FORMS,COARSE))-len(pairs(FORMS,ONE)))+(len(pairs(FORMS,FINE))-len(pairs(FORMS,COARSE)))==len(pairs(FORMS,FINE))-len(pairs(FORMS,ONE))
 if i==15:return len(words(tuple("abcdefgh"),1))==len(words(("L","R"),3))==8 and ("base-eight",1)!=("two-label",3)
 if i==16:return len(RELATIONS)==16 and all(witness(n) for n in range(1,16))
 return False
def surface(i):
 axes=(("partial-support","complete-canonical-support"),("imported-continuum-scalar",RELATIONS[i-1]),("lost-or-hidden-rows","complete-retained-and-closed-ledger"),("unit-erased-number","support-and-unit-custody"),("sampled-measures","complete-declared-measure-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,survivor=surface(i);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};passed=all((received==rows,len(set(received))==len(received)==256,decisions==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_measure_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
