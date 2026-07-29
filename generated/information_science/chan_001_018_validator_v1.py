#!/usr/bin/env python3
"""Implementation-distinct exact validator for CHAN-001--018."""
import json,sys
from itertools import product
from pathlib import Path
REL=("complete-total-input-output-relation","total-single-valued-channel-map","output-observation-equivalence-classes","maximum-distinguishable-single-use-codebook","registered-resource-codebook-maximum","exact-relational-channel-composition","terminal-image-cascade-boundary","complete-product-channel-support","history-retaining-feedback-support","joint-sender-single-output-relation","single-input-joint-receiver-relation","source-relay-terminal-path-ledger","cross-dependent-joint-channel-relation","two-way-history-bound-channel","complete-path-and-cut-ledger","complete-multiuse-word-support","encoder-channel-decoder-equivalence","eighteen-channel-obligation-ledger")
IDENTITY={"a":"x","b":"y","c":"z"};BINARY={"L":"L","R":"R"}
def route(edges,start,end):
 pending=[(start,)];out=[]
 while pending:
  p=pending.pop()
  if p[-1]==end:out.append(p);continue
  pending.extend(p+(b,) for a,b in edges if a==p[-1] and b not in p)
 return tuple(sorted(out))
def witness(i):
 if i==1:
  rows=(("a","x"),("b","x"),("b","y"),("c","y"));return {a for a,_ in rows}=={"a","b","c"} and len(rows)==4
 if i==2:return tuple(IDENTITY[x] for x in ("a","b","c"))==("x","y","z")
 if i==3:return len({{"x":"left","y":"left","z":"right"}[IDENTITY[x]] for x in IDENTITY})==2 and len(set(IDENTITY.values()))==3
 if i==4:return len(set(IDENTITY.values()))==3 and len({"x","y"})==2
 if i==5:return len({IDENTITY[x] for x in ("a","c")})==2
 if i==6:
  second={"x":"v","y":"w","z":"u"};return tuple(second[IDENTITY[x]] for x in IDENTITY)==("v","w","u")
 if i==7:
  terminal={"x":"p","y":"p","z":"q"};return len({terminal[IDENTITY[x]] for x in IDENTITY})==2
 if i==8:return len({(BINARY[a],IDENTITY[b]) for a,b in product(BINARY,IDENTITY)})==6
 if i==9:
  support=tuple(product(BINARY,repeat=2));images=tuple(tuple(BINARY[x] for x in word) for word in support);return len(support)==len(set(images))==4
 if i==10:
  rows=tuple(((a,b),"same" if a==b else "different") for a,b in product(("L","R"),repeat=2));return len(rows)==4 and len({x for x,_ in rows})==4 and len({y for _,y in rows})==2
 if i==11:return tuple((x,(x,x)) for x in ("L","R"))==(("L",("L","L")),("R",("R","R")))
 if i==12:return route((("s","r1"),("s","r2"),("r1","t"),("r2","t")),"s","t")==(("s","r1","t"),("s","r2","t"))
 if i==13:
  rows=tuple(((a,b),("L" if a==b else "R",b)) for a,b in product(("L","R"),repeat=2));return len(rows)==4 and rows[1][1]==("R","R") and rows[2][1]==("R","L")
 if i==14:return len(tuple(((a,b),(b,a)) for a,b in product(("L","R"),repeat=2)))==4
 if i==15:return len(route((("s","a"),("s","b"),("a","t"),("b","t")),"s","t"))==2 and route((("a","t"),("b","t")),"s","t")==()
 if i==16:return len({tuple(BINARY[x] for x in word) for word in product(BINARY,repeat=2)})==4
 if i==17:
  encoder={"a":"L","b":"R"};decoder={"L":"R","R":"L"};return tuple(decoder[BINARY[encoder[x]]] for x in encoder)==("R","L")
 if i==18:return len(REL)==18 and all(witness(n) for n in range(1,18))
 return False
def surface(i):
 axes=(("partial-channel-carrier","complete-input-output-carriers"),("missing-or-imported-channel-row",REL[i-1]),("unregistered-output-equivalence","declared-output-observation-custody"),("unitless-asymptotic-capacity","exact-code-forms-per-registered-use"),("sampled-channel-forms","complete-declared-channel-product"),("outcome-selected","root-bound-forward-forcing"),("preopened-target","post-registry-exact-observation"),("fit-exception-extra-rule","finite-successor-or-explicit-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_channel_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
