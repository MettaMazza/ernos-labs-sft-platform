#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from sft.quantum_computation.qcodex_001_032_laws_v1 import IDS, SPECS
OUT = ROOT / "census/quantum_qcodex_001_032_target_registry_v1.json"; FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("QCODEX target registry already frozen")
    frozen = json.loads(FROZEN.read_text()); body = dict(frozen); identity = body.pop("census_identity")
    if canonical(body) != identity: raise SystemExit("Quantum census identity changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QCODEX"]
    if len(obligations) != 32 or tuple(row["title"] for row in obligations) != tuple(SPECS[cid].title for cid in IDS): raise SystemExit("QCODEX frozen obligation membership changed")
    value = {"schema": "sft-v3-quantum-qcodex-value-free-registry/1", "date": "2026-07-29", "authority": "Maria Smith", "quantum_computation_census_identity": identity, "claim_ids": list(IDS), "obligation_ids": [row["obligation_id"] for row in obligations], "question_titles": [row["title"] for row in obligations], "frozen_before_observation_access": True, "target_content_present": False, "prohibited_target_fields": ["expected recovery outcome", "selected survivor", "physical error rate or threshold", "imported code or fault model"], "completion_unit": "all thirty-two QCODEX claims; no proper subset"}; value["registry_identity"] = canonical(value); OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n"); print(json.dumps({"claims": len(IDS), "identity": value["registry_identity"]}, indent=2))
if __name__ == "__main__": main()
