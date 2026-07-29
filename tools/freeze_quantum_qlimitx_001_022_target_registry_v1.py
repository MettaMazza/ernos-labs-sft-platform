#!/usr/bin/env python3
"""Freeze the value-free QLIMITX question and source-identity registry."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
OUT = ROOT / "census/quantum_qlimitx_001_022_target_registry_v1.json"
CLAIM_IDS = (
    "SFT-QUANTUM-QLIMITX-CLASSICAL-STATE-EMBEDDING-001",
    "SFT-QUANTUM-QLIMITX-REVERSIBLE-SUBMODEL-002",
    "SFT-QUANTUM-QLIMITX-PROBABILISTIC-SUPPORT-003",
    "SFT-QUANTUM-QLIMITX-MEASUREMENT-DECODER-004",
    "SFT-QUANTUM-QLIMITX-BIDIRECTIONAL-SIMULATION-005",
    "SFT-QUANTUM-QLIMITX-EFFICIENT-REGION-006",
    "SFT-QUANTUM-QLIMITX-PHASE-SEPARATION-007",
    "SFT-QUANTUM-QLIMITX-ENTANGLEMENT-SEPARATION-008",
    "SFT-QUANTUM-QLIMITX-NO-CLONING-009",
    "SFT-QUANTUM-QLIMITX-MEASUREMENT-DISTURBANCE-010",
    "SFT-QUANTUM-QLIMITX-HALTING-SELF-REFERENCE-011",
    "SFT-QUANTUM-QLIMITX-UNDECIDABILITY-012",
    "SFT-QUANTUM-QLIMITX-INCOMPLETENESS-013",
    "SFT-QUANTUM-QLIMITX-NO-HYPERCOMPUTATION-014",
    "SFT-QUANTUM-QLIMITX-FINITE-SUPPORT-015",
    "SFT-QUANTUM-QLIMITX-NO-UNRESTRICTED-ADVANTAGE-016",
    "SFT-QUANTUM-QLIMITX-NO-UNMEASURED-SPEEDUP-017",
    "SFT-QUANTUM-QLIMITX-NO-FORMAL-HARDWARE-THRESHOLD-018",
    "SFT-QUANTUM-QLIMITX-IMPLEMENTATION-HANDOFF-019",
    "SFT-QUANTUM-QLIMITX-PHYSICS-MEASUREMENT-BOUNDARY-020",
    "SFT-QUANTUM-QLIMITX-OPEN-FALSIFICATION-021",
    "SFT-QUANTUM-QLIMITX-COMPLETENESS-022",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QLIMITX target registry already frozen")
    frozen = json.loads(FROZEN.read_text())
    body = dict(frozen)
    census_identity = body.pop("census_identity")
    if canonical(body) != census_identity:
        raise SystemExit("Quantum Computation census identity changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QLIMITX"]
    if len(obligations) != len(CLAIM_IDS) or len(set(CLAIM_IDS)) != len(CLAIM_IDS):
        raise SystemExit("QLIMITX frozen obligation or claim identity count changed")
    value = {
        "schema": "sft-v3-quantum-qlimitx-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "quantum_computation_census_identity": census_identity,
        "claim_ids": list(CLAIM_IDS),
        "obligation_ids": [row["obligation_id"] for row in obligations],
        "question_titles": [row["title"] for row in obligations],
        "required_external_surfaces": [row["required_external_surface"] for row in obligations],
        "pre_registered_source_identities": [
            "SFT-V3-ADMITTED-QLEARNX-COMPLETENESS-022",
            "SFT-V3-ADMITTED-QUANTUM-LIMITS-001",
            "SFT-V3-ADMITTED-COMPUTABILITY-AND-INCOMPLETENESS-FAMILIES",
            "SFT-V1-V2-CLASSICAL-QUANTUM-LIMITS-COMPARISON-CORPUS",
            "PHYSICS-DEVICE-ENERGY-TIMING-THRESHOLD-MEASUREMENT-HANDOFFS",
        ],
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "prohibited_target_fields": ["claimed speedup", "hardware threshold", "device timing", "energy value", "hypercomputation answer"],
        "completion_unit": "all twenty-two QLIMITX claims; no proper subset",
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(CLAIM_IDS), "identity": value["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
