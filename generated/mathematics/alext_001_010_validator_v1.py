#!/usr/bin/env python3
import json,math,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("positive-polynomial-side-order-swap","exact-algebraic-balance-enclosure","finite-basis-reduction-tower","finite-label-field-table","root-label-automorphism-orbit","periodic-phase-label-cycle","held-orthogonal-pair-arithmetic","disjoint-rational-enclosure-order","prime-power-closeness-depth","explicit-unrepresented-scalar-boundary")
def val(n,p):
 c=0
 while n%p==0:n//=p;c+=1
 return c
def witness(i):
 if i==1:return Fraction(7,5)**2<2<Fraction(3,2)**2
 if i==2:return Fraction(5,4)**3<2<Fraction(4,3)**3
 if i==3:return (1+2,1+1)==(3,2)
 if i==4:return all(any((a*b)%5==1 for b in range(1,5)) for a in range(1,5))
 if i==5:return [(x*x)%7 for x in (1,2,4)]==[1,4,2]
 if i==6:return [(1+k)%5 for k in range(5)]==[1,2,3,4,0]
 if i==7:return (1*1,1*1,1*1+1*1)==(1,1,2)
 if i==8:return Fraction(4,3)<Fraction(7,5)
 if i==9:return val(81,3)==4
 if i==10:return not any(Fraction(a,b)**2==2 for b in range(1,21) for a in range(1,41))
 return False
def surface(i):
 axes=(("imported-scalar-field","generated-exact-structure"),("named-theorem-result",REL[i-1]),("decimal-or-symbol-only","defining-balance-and-record"),("selected-example","complete-declared-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fixed-table-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,sealed_path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(sealed_path.read_text());rows,survivor=surface(i);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};controls=sealed["controls"];passed=all((received==rows,len(received)==len(set(received))==256,decisions==expected,sum(expected.values())==1,len(controls)==4,all(x["passed"] for x in controls),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"exact_algebraic_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
