#!/usr/bin/env python3
"""Freeze the value-free QSIMX question and source-identity registry."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
OUT = ROOT / "census/quantum_qsimx_001_024_target_registry_v1.json"

CLAIM_IDS = (
    "SFT-QUANTUM-QSIMX-MODEL-SIMULATOR-IDENTITY-001",
    "SFT-QUANTUM-QSIMX-TARGET-SUPPORT-ENCODING-002",
    "SFT-QUANTUM-QSIMX-DIGITAL-SIMULATION-003",
    "SFT-QUANTUM-QSIMX-ANALOG-BOUNDARY-004",
    "SFT-QUANTUM-QSIMX-LOCAL-UPDATE-005",
    "SFT-QUANTUM-QSIMX-HAMILTONIAN-CORRESPONDENCE-006",
    "SFT-QUANTUM-QSIMX-TIME-EVOLUTION-ENCLOSURE-007",
    "SFT-QUANTUM-QSIMX-MANY-BODY-SUPPORT-008",
    "SFT-QUANTUM-QSIMX-FERMION-BOSON-ENCODING-009",
    "SFT-QUANTUM-QSIMX-LATTICE-FIELD-HANDOFF-010",
    "SFT-QUANTUM-QSIMX-OPEN-SYSTEM-011",
    "SFT-QUANTUM-QSIMX-NOISE-CUSTODY-012",
    "SFT-QUANTUM-QSIMX-CHEMISTRY-HANDOFF-013",
    "SFT-QUANTUM-QSIMX-MATERIALS-HANDOFF-014",
    "SFT-QUANTUM-QSIMX-COMPUTATION-VERIFICATION-015",
    "SFT-QUANTUM-QSIMX-INTERACTIVE-VERIFICATION-016",
    "SFT-QUANTUM-QSIMX-BLIND-DELEGATION-017",
    "SFT-QUANTUM-QSIMX-SELF-TESTING-018",
    "SFT-QUANTUM-QSIMX-TOMOGRAPHY-019",
    "SFT-QUANTUM-QSIMX-PROCESS-CHANNEL-VERIFICATION-020",
    "SFT-QUANTUM-QSIMX-DETERMINISTIC-BENCHMARKING-021",
    "SFT-QUANTUM-QSIMX-OWNING-DOMAIN-VALIDATION-022",
    "SFT-QUANTUM-QSIMX-WORKFLOW-PROVENANCE-023",
    "SFT-QUANTUM-QSIMX-COMPLETENESS-024",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QSIMX target registry already frozen")
    frozen = json.loads(FROZEN.read_text())
    body = dict(frozen)
    census_identity = body.pop("census_identity")
    if canonical(body) != census_identity:
        raise SystemExit("Quantum Computation census identity changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QSIMX"]
    if len(obligations) != len(CLAIM_IDS) or len(set(CLAIM_IDS)) != len(CLAIM_IDS):
        raise SystemExit("QSIMX frozen obligation or claim identity count changed")
    value = {
        "schema": "sft-v3-quantum-qsimx-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "quantum_computation_census_identity": census_identity,
        "claim_ids": list(CLAIM_IDS),
        "obligation_ids": [row["obligation_id"] for row in obligations],
        "question_titles": [row["title"] for row in obligations],
        "required_external_surfaces": [row["required_external_surface"] for row in obligations],
        "pre_registered_source_identities": [
            "SFT-V3-ADMITTED-QUANTUM-SIMULATION-001",
            "SFT-V3-ADMITTED-QUANTUM-VERIFICATION-001",
            "SFT-V3-ADMITTED-QCODEX-COMPLETENESS-032",
            "SFT-V1-V2-QUANTUM-SIMULATION-VERIFICATION-COMPARISON-CORPUS",
            "OWNING-DOMAIN-PHYSICAL-MEASUREMENT-HANDOFFS",
        ],
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "prohibited_target_fields": [
            "expected simulation output",
            "selected survivor",
            "physical Hamiltonian or continuum equation",
            "device fidelity or benchmark score",
            "target-domain chemistry or materials value",
        ],
        "completion_unit": "all twenty-four QSIMX claims; no proper subset",
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(CLAIM_IDS), "identity": value["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
