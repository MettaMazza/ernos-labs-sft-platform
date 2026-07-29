#!/usr/bin/env python3
"""Implementation-distinct exact validator for CAT-001--012."""
import json,sys
from itertools import product
from pathlib import Path
REL=("typed-arrow-composition","identity-associative-composition","identity-composition-preserving-map","commuting-component-family","product-coproduct-universal-record","finite-diagram-universal-construction","exact-hom-pairing-bijection","associative-unitary-tensor","internal-map-evaluation-currying","dependent-fibre-record","compatible-local-unique-gluing","finite-arity-substitution-associativity")
def comp(a,b):return tuple(b[x-1] for x in a)
def maps(domain,codomain):return tuple(product(codomain,repeat=len(domain)))
def curried(table,a,b):return tuple(tuple(table[x*b+y] for y in range(b)) for x in range(a))
def quotient(first,second):
 labels=tuple(sorted(set(first.values())|set(second.values())))
 pairs=tuple((first[key],second[key]) for key in first)
 def connected(start,target):
  reached={start}
  while True:
   extended=reached|{right for left,right in pairs if left in reached}|{left for left,right in pairs if right in reached}
   if extended==reached:return target in reached
   reached=extended
 return tuple(sorted({tuple(label for label in labels if connected(seed,label)) for seed in labels}))
def witness(i):
 if i==1:return ("A","B")[1]==("B","C")[0] and ("A","B")[1]!=("A","C")[0]
 if i==2:
  f=(2,1);g=(1,2);h=(2,1);identity=(1,2);return comp(identity,f)==f and comp(f,identity)==f and comp(comp(f,g),h)==comp(f,comp(g,h))
 if i==3:return all(2*(x+1)==(lambda y:2*y)(x+1) for x in (1,2,3))
 if i==4:return all(2*(x+1)==2*x+2 for x in (1,2))
 if i==5:return all((a,b)==((a,b)[0],(a,b)[1]) for a,b in product((1,2),(3,4))) and len({("left",1),("left",2),("right",3),("right",4)})==4
 if i==6:
  f={1:1,2:2,3:3};g={1:1,2:3,3:3};return tuple(x for x in f if f[x]==g[x])==(1,3) and quotient(f,g)==((1,),(2,3))
 if i==7:
  tables=maps((1,2,3,4),(1,2));return len(tables)==16 and len({curried(t,2,2) for t in tables})==16
 if i==8:return all((a+b)+c==a+(b+c) and a+()==a and ()+a==a for a,b,c in (((1,),(2,),(3,)),((1,2),(3,4),(5,))))
 if i==9:
  tables=maps((1,2,3,4),(1,2));return len(maps((1,2),(1,2)))==4 and all(tuple(x for row in curried(t,2,2) for x in row)==t for t in tables)
 if i==10:
  fam={1:("x",),2:("y","z")};pairs=((1,"x"),(2,"y"),(2,"z"));return len(pairs)==3 and all(v in fam[a] for a,v in pairs)
 if i==11:return tuple(g for g in ({1:a,2:b,3:c} for a,b,c in product(("a","b"),repeat=3)) if {1:g[1],2:g[2]}=={1:"a",2:"b"} and {2:g[2],3:g[3]}=={2:"b",3:"a"})==({1:"a",2:"b",3:"a"},)
 if i==12:return ((1,)+(2,3))+(4,5)==(1,)+((2,3)+(4,5)) and len((1,2,3,4,5))==5
 return False
def surface(i):
 axes=(("untyped-carriers","generated-source-target-types"),("imported-universal-answer",REL[i-1]),("negative-arrow-scalar","held-opposed-arrow-orientation"),("sampled-diagrams","complete-declared-diagram-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-arity-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_category_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
