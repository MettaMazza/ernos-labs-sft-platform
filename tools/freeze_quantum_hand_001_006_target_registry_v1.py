#!/usr/bin/env python3
"""Freeze the value-free Quantum HAND registry."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FROZEN=ROOT/"census/quantum_computation_discipline_obligations.json";OUT=ROOT/"census/quantum_hand_001_006_target_registry_v1.json"
CLAIM_IDS=("SFT-QUANTUM-HAND-DOWNSTREAM-OWNERSHIP-001","SFT-QUANTUM-HAND-PHYSICS-MEASUREMENT-002","SFT-QUANTUM-HAND-CHEMISTRY-MATERIALS-003","SFT-QUANTUM-HAND-SOFTWARE-HARDWARE-004","SFT-QUANTUM-HAND-OPEN-EXTENSION-005","SFT-QUANTUM-HAND-CROSS-BRANCH-COMPLETENESS-006")
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("Quantum HAND registry already frozen")
 frozen=json.loads(FROZEN.read_text());body=dict(frozen);identity=body.pop("census_identity")
 if canonical(body)!=identity:raise SystemExit("Quantum census identity changed")
 obligations=[r for r in frozen["obligations"] if r["family"]=="HAND"]
 if len(obligations)!=6:raise SystemExit("Quantum HAND membership changed")
 value={"schema":"sft-v3-quantum-hand-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","quantum_computation_census_identity":identity,"claim_ids":list(CLAIM_IDS),"obligation_ids":[r["obligation_id"] for r in obligations],"question_titles":[r["title"] for r in obligations],"pre_registered_source_identities":["QUANTUM-RECONCILIATION-V12","QUANTUM-GRAND-LOCK-012","CROSS-BRANCH-OWNERSHIP-MAP","PHYSICS-CHEMISTRY-MATERIALS-ENGINEERING-EXTENSION-HANDOFFS"],"frozen_before_observation_access":True,"target_content_present":False,"prohibited_target_fields":["duplicated owner","invented downstream value","closed extension gate","premarked branch completion"],"completion_unit":"all six HAND claims; no proper subset"};value["registry_identity"]=canonical(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":6,"identity":value["registry_identity"]},indent=2))
if __name__=="__main__":main()
