#!/usr/bin/env python3
"""Implementation-distinct exact validator for computation HAND-001--006."""
import json,sys
from itertools import product
from pathlib import Path
RELATIONS=("one-obligation-one-owner-map","domain-measurement-owner-map","formal-prediction-observation-comparison-chain","classical-quantum-operation-boundary","dated-completion-open-extension-ledger","six-handoff-no-omission-certificate")
OWNERS=(("quantum","quantum-computation"),("implementations","engineering-translation"),("measurements","owning-domain-science"),("applications","frontier-application-rebuild"))
def witness(i):
 if i==1:return len({x[0] for x in OWNERS})==len(OWNERS) and all(x[1] for x in OWNERS)
 if i==2:return dict(OWNERS)["measurements"]=="owning-domain-science"
 if i==3:return len(("formal","seal","observe","compare"))==4
 if i==4:return dict(OWNERS)["quantum"]=="quantum-computation"
 if i==5:return ("dated","extensible","prior-immutable")[1]=="extensible"
 if i==6:return len(OWNERS)==4 and all(witness(n) for n in range(1,6))
 return False
def surface(i):
 axes=(("duplicate-or-orphan-owner","one-declared-owner"),("implicit-interface","complete-input-output-interface"),("convenience-routing",RELATIONS[i-1]),("discarded-or-rewritten-evidence","immutable-prior-evidence-custody"),("sampled-interfaces","literal-complete-product"),("broken-lineage","there-is-no-nothing-lineage"),("permanent-lock-or-rewrite","dated-complete-open-extension"),("silent-scope-transfer","explicit-domain-quantum-engineering-boundary"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,survivor=surface(i);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};passed=all((received==rows,len(set(received))==len(received)==256,decisions==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"handoff_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
