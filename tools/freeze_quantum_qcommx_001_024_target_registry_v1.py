#!/usr/bin/env python3
"""Freeze value-free QCOMMX questions and source identities before outcome access."""
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from sft.quantum_computation.qcommx_001_024_laws_v1 import IDS, SPECS
OUT = ROOT / "census/quantum_qcommx_001_024_target_registry_v1.json"
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"


def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("QCOMMX target registry already frozen")
    frozen = json.loads(FROZEN.read_text()); body = dict(frozen); identity = body.pop("census_identity")
    if canonical(body) != identity: raise SystemExit("Quantum census identity changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QCOMMX"]
    if len(obligations) != 24 or tuple(row["title"] for row in obligations) != tuple(SPECS[cid].title for cid in IDS): raise SystemExit("QCOMMX frozen obligation membership changed")
    value = {"schema": "sft-v3-quantum-qcommx-value-free-registry/1", "date": "2026-07-29", "authority": "Maria Smith", "quantum_computation_census_identity": identity, "claim_ids": list(IDS), "obligation_ids": [row["obligation_id"] for row in obligations], "question_titles": [row["title"] for row in obligations], "frozen_before_observation_access": True, "target_content_present": False, "prohibited_target_fields": ["expected communication outcome", "selected survivor", "physical link, rate or loophole result", "imported protocol or security answer"], "completion_unit": "all twenty-four QCOMMX claims; no proper subset"}
    value["registry_identity"] = canonical(value); OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n"); print(json.dumps({"claims": len(IDS), "identity": value["registry_identity"]}, indent=2))


if __name__ == "__main__": main()
