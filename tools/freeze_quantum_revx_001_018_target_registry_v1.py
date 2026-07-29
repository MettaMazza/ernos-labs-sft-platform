#!/usr/bin/env python3
"""Freeze REVX identities and questions before exact observation access."""

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.quantum_computation.revx_001_018_laws_v1 import IDS


OUT = ROOT / "census/quantum_revx_001_018_target_registry_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("REVX target registry already frozen")
    census = json.loads((ROOT / "census/quantum_computation_discipline_obligations.json").read_text(encoding="utf-8"))
    rows = [row for row in census["obligations"] if row["family"] == "REVX"]
    if len(rows) != len(IDS) or len(IDS) != 18:
        raise SystemExit("REVX census changed")
    payload = {
        "schema": "sft-v3-quantum-revx-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "quantum_computation_census_identity": census["census_identity"],
        "claim_ids": list(IDS),
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all eighteen REVX claims; no proper subset",
        "prohibited_target_fields": [
            "expected execution outcome",
            "selected survivor",
            "physical energy or hardware result",
            "imported reversible-machine answer",
        ],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
