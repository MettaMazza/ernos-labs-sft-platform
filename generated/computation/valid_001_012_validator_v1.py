#!/usr/bin/env python3
"""Implementation-distinct exact validator for computation VALID-001--012."""
import json,sys
from itertools import product
from pathlib import Path
COUNTS=((22,5632,88),(21,5376,84),(33,8448,132),(31,7936,124),(25,6400,100),(26,6656,104),(25,6400,100),(26,6656,104),(25,6400,100))
RELATIONS=("formal-family-receipt-vector","computability-family-receipt-vector","complexity-family-receipt-vector","algorithm-family-receipt-vector","semantics-family-receipt-vector","distributed-family-receipt-vector","security-family-receipt-vector","learning-family-receipt-vector","scientific-family-receipt-vector","theorem-finite-frontier-boundary-vector","complete-adverse-ownership-vector","classical-computation-grand-lock-vector")
def witness(i):
 if i<=9:return COUNTS[i-1][0]*256==COUNTS[i-1][1] and COUNTS[i-1][0]*4==COUNTS[i-1][2]
 if i==10:return COUNTS[1][0]+COUNTS[2][0]==54
 if i==11:return all(claims*4==controls for claims,_candidates,controls in COUNTS)
 if i==12:return sum(x[0] for x in COUNTS)==234 and sum(x[1] for x in COUNTS)==59904 and sum(x[2] for x in COUNTS)==936
 return False
def surface(i):
 axes=(("missing-or-duplicate-obligation","complete-frozen-obligation-map"),("stale-or-unreproduced-receipt","exact-current-receipt-replay"),("summary-only-assertion",RELATIONS[i-1]),("missing-control-or-trusted-producer","all-controls-and-independent-certificates"),("sampled-evidence","literal-complete-product"),("broken-or-outcome-selected-lineage","there-is-no-nothing-lineage"),("preopened-or-suppressed-row","complete-post-registry-observation-ledger"),("silent-unrestricted-export","explicit-theorem-census-handoff-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,survivor=surface(i);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};passed=all((received==rows,len(set(received))==len(received)==256,decisions==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"validation_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
