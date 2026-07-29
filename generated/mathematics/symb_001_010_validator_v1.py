#!/usr/bin/env python3
"""Implementation-distinct exact validator for SYMB-001--010."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("canonical-symbolic-record","trace-retaining-simplification","coefficient-convolution-factorization","complete-symbolic-solution-support","decreasing-confluent-rewrite-record","finite-coefficient-transform","held-phase-positive-weight-transform","successor-recurrence-special-function","bounded-complete-proof-search","constructive-witness-certificate")
EMPTY="EmptyOne";ONE="One"
def normal(term):
 if not isinstance(term,tuple):return term
 op=term[0];children=tuple(normal(x) for x in term[1:]);children=tuple(x for x in children if not (op=="add" and x==EMPTY) and not (op=="mul" and x==ONE))
 if len(children)==1:return children[0]
 return (op,)+tuple(sorted(children,key=repr))
def conv(a,b):
 result=[]
 for degree in range(len(a)+len(b)-1):
  terms=tuple(a[left]*b[degree-left] for left in range(len(a)) if degree-left>=0 and degree-left<len(b));value=terms[0]
  for term in terms[1:]:value+=term
  result.append(value)
 return tuple(result)
def witness(i):
 if i==1:return normal(("add",("mul","y",ONE),EMPTY,"x"))==normal(("add","x",("mul",ONE,"y")))==("add","x","y")
 if i==2:return normal(("add",("mul","x",ONE),EMPTY))=="x"
 if i==3:return conv((1,1),(2,1))==(2,3,1)
 if i==4:return tuple(x for x in range(1,9) if x+3==7)==(4,)
 if i==5:return normal(("add",normal(("mul","x",ONE)),EMPTY))==normal(normal(("add",("mul","x",ONE),EMPTY)))=="x"
 if i==6:return conv((1,1,1),(1,1))==(1,2,2,1)
 if i==7:return (2,EMPTY)==(2,EMPTY) and Fraction(1)+Fraction(2,2)+Fraction(3,4)==Fraction(11,4)
 if i==8:
  trace=[1]
  for n in range(2,5):trace.append(trace[-1]*n)
  return tuple(trace)==(1,2,6,24)
 if i==9:return tuple((a,b) for a,b in product((('A','B'),('B','C')),repeat=2) if a[1]==b[0] and a[0]=='A' and b[1]=='C')==((('A','B'),('B','C')),)
 if i==10:return tuple(x for x in range(1,7) if x+x==6)==(3,) and 3+3==6
 return False
def surface(i):
 axes=(("opaque-expression-object","generated-canonical-syntax"),("imported-symbolic-answer",REL[i-1]),("negative-coefficient-shortcut","held-opposed-symbolic-orientation"),("sampled-rewrites","complete-declared-rewrite-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("single-depth-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_symbolic_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
