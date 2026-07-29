#!/usr/bin/env python3
"""Freeze the value-free Quantum VALID registry."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FROZEN=ROOT/"census/quantum_computation_discipline_obligations.json"; OUT=ROOT/"census/quantum_valid_001_012_target_registry_v1.json"
CLAIM_IDS=("SFT-QUANTUM-VALID-REVERSIBLE-001","SFT-QUANTUM-VALID-STATE-002","SFT-QUANTUM-VALID-GATE-CIRCUIT-003","SFT-QUANTUM-VALID-ALGORITHM-004","SFT-QUANTUM-VALID-COMPLEXITY-005","SFT-QUANTUM-VALID-COMMUNICATION-006","SFT-QUANTUM-VALID-CODING-007","SFT-QUANTUM-VALID-SIMULATION-008","SFT-QUANTUM-VALID-LEARNING-009","SFT-QUANTUM-VALID-LIMITS-010","SFT-QUANTUM-VALID-ADVERSE-OWNERSHIP-011","SFT-QUANTUM-VALID-GRAND-LOCK-012")
def canonical(v): return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists(): raise SystemExit("Quantum VALID registry already frozen")
 frozen=json.loads(FROZEN.read_text()); body=dict(frozen); identity=body.pop("census_identity")
 if canonical(body)!=identity: raise SystemExit("Quantum census identity changed")
 obligations=[r for r in frozen["obligations"] if r["family"]=="VALID"]
 if len(obligations)!=12 or len(set(CLAIM_IDS))!=12: raise SystemExit("Quantum VALID membership changed")
 value={"schema":"sft-v3-quantum-valid-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","quantum_computation_census_identity":identity,"claim_ids":list(CLAIM_IDS),"obligation_ids":[r["obligation_id"] for r in obligations],"question_titles":[r["title"] for r in obligations],"pre_registered_source_identities":["QUANTUM-RECONCILIATION-V11","ALL-CURRENT-QUANTUM-FAMILY-AUDITS","ALL-CURRENT-QUANTUM-RECEIPTS","ALL-CURRENT-QUANTUM-ADVERSE-AND-HANDOFF-ROWS"],"frozen_before_observation_access":True,"target_content_present":False,"prohibited_target_fields":["family pass count","selected receipt","suppressed adverse row","premarked Grand Lock"],"completion_unit":"all twelve VALID claims; no proper subset"}; value["registry_identity"]=canonical(value); OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); print(json.dumps({"claims":12,"identity":value["registry_identity"]},indent=2))
if __name__=="__main__": main()
