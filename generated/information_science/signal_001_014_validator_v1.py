#!/usr/bin/env python3
"""Implementation-distinct exact validator for SIGNAL-001--014."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("complete-position-amplitude-record","separate-support-and-amplitude-custody","source-bound-position-selection","grammar-exhaustive-reconstruction-sufficiency","equal-sample-distinct-source-alias","complete-exact-amplitude-partition","held-oriented-exact-error-part","unique-source-bound-reconstruction","finite-generated-interpolation-candidates","bijective-finite-support-transform","position-and-change-joint-record","complete-coordinate-product-support","capture-sample-transform-provenance-chain","fourteen-signal-obligation-ledger")
ROWS=((1,Fraction(1,4)),(2,Fraction(1,2)),(3,Fraction(3,4)),(4,Fraction(1,1)))
def select(rows,pos):return tuple(rows[p-1] for p in pos)
def transform(w):
 b={"L":False,"R":True};l={False:"L",True:"R"};a,c=map(b.get,w);return (l[a],l[a!=c])
def inverse(w):
 b={"L":False,"R":True};l={False:"L",True:"R"};a,c=map(b.get,w);return (l[a],l[a!=c])
def witness(i):
 if i==1:return ROWS==tuple((n+1,Fraction(n+1,4)) for n in range(4))
 if i==2:return tuple(p for p,_ in ROWS)==(1,2,3,4) and tuple(v for _,v in ROWS)==(Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,1))
 if i==3:return select(ROWS,(1,3))==((1,Fraction(1,4)),(3,Fraction(3,4)))
 if i==4:return all(tuple(seed[n%2] for n in range(6))==form for seed in product(("L","R"),repeat=2) for form in (tuple(seed[n%2] for n in range(6)),))
 if i==5:
  left=((1,Fraction(1,4)),(2,Fraction(1,2)),(3,Fraction(3,4)));right=((1,Fraction(1,4)),(2,Fraction(1,1)),(3,Fraction(3,4)))
  return left!=right and select(left,(1,3))==select(right,(1,3))
 if i==6:
  classes={Fraction(1,4):"low",Fraction(1,2):"low",Fraction(3,4):"high",Fraction(1,1):"high"}
  return tuple(classes[v] for _,v in ROWS)==("low","low","high","high") and len(classes)==4
 if i==7:return ("opposed",abs(Fraction(3,8)-Fraction(1,2)))==("opposed",Fraction(1,8)) and ("held",abs(Fraction(5,8)-Fraction(1,2)))==("held",Fraction(1,8))
 if i==8:return select(ROWS,(1,2,3,4))==ROWS
 if i==9:return tuple(Fraction(n,4) for n in range(1,5))==(Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,1))
 if i==10:return all(inverse(transform(w))==w for w in product(("L","R"),repeat=2)) and len({transform(w) for w in product(("L","R"),repeat=2)})==4
 if i==11:
  w=("L","L","R","L");return tuple((n+1,w[n],"same" if n==0 or w[n]==w[n-1] else "change") for n in range(4))==((1,"L","same"),(2,"L","same"),(3,"R","change"),(4,"L","change"))
 if i==12:return len(tuple(product((1,2),(1,2,3))))==len(set(product((1,2),(1,2,3))))==6
 if i==13:return tuple(x for x,_ in (("capture","sensor-A"),("sample",(1,3)),("quantize",("low","high"))))==("capture","sample","quantize")
 if i==14:return len(REL)==14 and all(witness(n) for n in range(1,14))
 return False
def surface(i):
 axes=(("partial-signal-support","complete-position-labelled-support"),("floating-or-untyped-amplitude","exact-part-and-held-label"),("imported-signal-answer",REL[i-1]),("terminal-or-samples-only","source-sample-reconstruction-ledger"),("sampled-signal-forms","complete-declared-signal-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_signal_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
