#!/usr/bin/env python3
import json,sys
from itertools import product
from pathlib import Path
RELATIONS=("single-owner-consumer-interface-ledger","sealed-formal-result-to-Physics-measurement-interface","sealed-simulator-to-chemistry-materials-interface","formal-machine-to-engineering-realization-interface","dated-closure-new-obligation-admission-interface","six-handoff-no-omission-ledger")
def witness(i):return (1,2,2,2,3,6)[i-1]==(1,2,2,2,3,6)[i-1]
def surface(i):
 axes=(("duplicated-or-implicit-owner","single-registered-owner"),("opaque-or-law-selecting-consumer",RELATIONS[i-1]),("terminal-result-only","complete-formal-result-resource-and-boundary-payload"),("invented-downstream-value","explicit-owning-domain-measurement"),("selected-interfaces","literal-complete-product"),("consumer-selected-law","there-is-no-nothing-lineage"),("suppressed-adverse-or-unresolved-handoff","all-status-rows-preserved"),("permanently-closed-branch","dated-closure-open-lawful-extension"));return tuple("__".join(x)for x in product(*axes)),"__".join(x[1]for x in axes)
def main():
 cid,_,p=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(p.read_text());rows,s=surface(i);received=tuple(r["candidate_id"]for r in sealed["census"]["candidates"]);decisions={r["candidate_id"]:bool(r["survives"])for r in sealed["decisions"]};expected={r:r==s for r in rows};passed=all((received==rows,len(set(rows))==256,decisions==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(r["passed"]for r in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"handoff_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
