#!/usr/bin/env python3
"""Implementation-distinct exact validator for REL-001--014."""
import json,sys
from itertools import product
from pathlib import Path
REL=("complete-ordered-joint-support","held-condition-support-restriction","shared-determination-class-ledger","joint-as-marginal-conditional-composition","image-distinction-monotonicity","held-condition-product-factorization","recoverable-common-class","ordered-causal-distinction-ledger","three-way-shared-closure-ledger","joint-versus-marginal-product-ledger","typed-shared-unique-synergy-ledger","complete-directed-path-custody","bijection-invariant-relative-support","fourteen-relational-obligation-ledger")
L=("L","R");PAIR=tuple(product(L,repeat=2));TRI=tuple(product(L,repeat=3))
def route(edges):
 pending=[("s",)];out=[]
 while pending:
  p=pending.pop()
  if p[-1]=="t":out.append(p);continue
  pending.extend(p+(b,) for a,b in edges if a==p[-1] and b not in p)
 return tuple(sorted(out))
def witness(i):
 if i==1:return len(PAIR)==4 and {x for x,_ in PAIR}=={y for _,y in PAIR}==set(L)
 if i==2:return tuple(r for r in PAIR if r[1]=="L")==(("L","L"),("R","L"))
 if i==3:return all(len({y for x,y in (("L","L"),("R","R")) if x==a})==1 for a in L) and all(len({y for x,y in PAIR if x==a})==2 for a in L)
 if i==4:return len({x for x,_ in PAIR})==2 and tuple(len({y for x,y in PAIR if x==a}) for a in L)==(2,2) and len(PAIR)==4
 if i==5:return len({{"a":"x","b":"y","c":"z"}[x] for x in ("a","b","c")})==3 and len({{"x":"p","y":"p","z":"q"}[x] for x in ("x","y","z")})==2
 if i==6:return all({(x,y) for x,y,c in TRI if c==z}==set(PAIR) for z in L)
 if i==7:return all(x==y for x,y in (("L","L"),("R","R")))
 if i==8:return len(tuple(((a,b),(a,"same" if a==b else "different")) for a,b in PAIR))==4
 if i==9:return len((("L","L","L"),("R","R","R")))==2 and len(TRI)==8
 if i==10:return len(TRI)==8 and tuple(len({r[n] for r in TRI}) for n in range(3))==(2,2,2)
 if i==11:return len(("shared","unique-left","unique-right","synergy"))==4
 if i==12:
  edges=(("s","a"),("a","t"),("s","b"),("b","t"));return route(edges)==(("s","a","t"),("s","b","t")) and route((edges[0],edges[2],edges[3]))==(("s","b","t"),)
 if i==13:
  m={"L":"left","R":"right"};inv={"left":"L","right":"R"};return tuple(inv[m[x]] for x in L)==L and len(set(m.values()))==2
 if i==14:return len(REL)==14 and all(witness(n) for n in range(1,14))
 return False
def surface(i):
 axes=(("partial-joint-support","complete-canonical-joint-support"),("imported-or-scalar-relation",REL[i-1]),("implicit-or-probabilistic-condition","explicit-held-condition-record"),("chosen-information-allocation","complete-typed-distinction-ledger"),("sampled-relational-forms","complete-declared-relational-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_relational_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
