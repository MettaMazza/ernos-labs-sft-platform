#!/usr/bin/env python3
"""Freeze the value-free QLEARNX question and source-identity registry."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
OUT = ROOT / "census/quantum_qlearnx_001_022_target_registry_v1.json"
CLAIM_IDS = (
    "SFT-QUANTUM-QLEARNX-PROBLEM-EXAMPLE-IDENTITY-001",
    "SFT-QUANTUM-QLEARNX-CLASSICAL-DATA-BOUNDARY-002",
    "SFT-QUANTUM-QLEARNX-QUANTUM-DATA-CUSTODY-003",
    "SFT-QUANTUM-QLEARNX-HYPOTHESIS-FAMILY-004",
    "SFT-QUANTUM-QLEARNX-FEATURE-MAP-005",
    "SFT-QUANTUM-QLEARNX-KERNEL-BOUNDARY-006",
    "SFT-QUANTUM-QLEARNX-CLASSIFICATION-007",
    "SFT-QUANTUM-QLEARNX-REGRESSION-008",
    "SFT-QUANTUM-QLEARNX-GENERATIVE-SUPPORT-009",
    "SFT-QUANTUM-QLEARNX-CLUSTERING-010",
    "SFT-QUANTUM-QLEARNX-PRINCIPAL-STRUCTURE-011",
    "SFT-QUANTUM-QLEARNX-OPTIMIZATION-012",
    "SFT-QUANTUM-QLEARNX-VARIATIONAL-BOUNDARY-013",
    "SFT-QUANTUM-QLEARNX-REINFORCEMENT-014",
    "SFT-QUANTUM-QLEARNX-ONLINE-015",
    "SFT-QUANTUM-QLEARNX-SAMPLE-COMPLEXITY-016",
    "SFT-QUANTUM-QLEARNX-QUERY-COMPLEXITY-017",
    "SFT-QUANTUM-QLEARNX-GENERALIZATION-CUSTODY-018",
    "SFT-QUANTUM-QLEARNX-ADVANTAGE-CERTIFICATE-019",
    "SFT-QUANTUM-QLEARNX-INTERPRETABILITY-020",
    "SFT-QUANTUM-QLEARNX-ROBUSTNESS-021",
    "SFT-QUANTUM-QLEARNX-COMPLETENESS-022",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QLEARNX target registry already frozen")
    frozen = json.loads(FROZEN.read_text())
    body = dict(frozen)
    census_identity = body.pop("census_identity")
    if canonical(body) != census_identity:
        raise SystemExit("Quantum Computation census identity changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QLEARNX"]
    if len(obligations) != len(CLAIM_IDS) or len(set(CLAIM_IDS)) != len(CLAIM_IDS):
        raise SystemExit("QLEARNX frozen obligation or claim identity count changed")
    value = {
        "schema": "sft-v3-quantum-qlearnx-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "quantum_computation_census_identity": census_identity,
        "claim_ids": list(CLAIM_IDS),
        "obligation_ids": [row["obligation_id"] for row in obligations],
        "question_titles": [row["title"] for row in obligations],
        "required_external_surfaces": [row["required_external_surface"] for row in obligations],
        "pre_registered_source_identities": [
            "SFT-V3-ADMITTED-QSIMX-COMPLETENESS-024",
            "SFT-V3-ADMITTED-QUANTUM-LEARNING-001",
            "SFT-V3-ADMITTED-CLASSICAL-LEARNING-COMPLETENESS-026",
            "SFT-V1-V2-QUANTUM-LEARNING-COMPARISON-CORPUS",
            "HELD-OUT-OWNING-DOMAIN-TARGET-HANDOFFS",
        ],
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "prohibited_target_fields": ["expected prediction", "selected hypothesis", "fitted parameter", "held-out target label", "claimed physical advantage"],
        "completion_unit": "all twenty-two QLEARNX claims; no proper subset",
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(CLAIM_IDS), "identity": value["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
