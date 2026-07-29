#!/usr/bin/env python3
"""Freeze all COMP target identities before source capture or outcome extraction."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_comp_001_012_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-COMP-DATA-REPRESENTATION-001", "exact material-structure data representation", ("NIST-RELIABLE-MATERIALS-DATA",)),
    ("002", "SFT-MAT-COMP-STRUCTURE-PROPERTY-002", "structure-property computation boundary", ("NIST-STRUCTURE-PROPERTY-MAPPING",)),
    ("003", "SFT-MAT-COMP-FINITE-SIMULATION-003", "finite numerical material simulation", ("NIST-OOF3D",)),
    ("004", "SFT-MAT-COMP-MULTISCALE-COMPOSITION-004", "multiscale model composition", ("NIST-MULTISCALE-GREENS",)),
    ("005", "SFT-MAT-COMP-ERROR-PROPAGATION-005", "numerical stability and error propagation in materials", ("NIST-UNCERTAINTY-PROPAGATION",)),
    ("006", "SFT-MAT-COMP-INVERSE-PROBLEM-006", "inverse materials problem", ("NIST-INVERSE-HEAT-PLACEMENT",)),
    ("007", "SFT-MAT-COMP-LEARNING-BOUNDARY-007", "machine-learning materials inference boundary", ("NIST-ML-MATERIALS-ROBUSTNESS",)),
    ("008", "SFT-MAT-COMP-DATABASE-PROVENANCE-008", "materials database identity and provenance", ("NIST-MATERIALS-DATABASES",)),
    ("009", "SFT-MAT-COMP-PHASE-FIELD-009", "phase-field computational correspondence", ("NIST-PHASE-FIELD-BENCHMARK",)),
    ("010", "SFT-MAT-COMP-MOLECULAR-DYNAMICS-010", "molecular-dynamics computational correspondence", ("NIST-MOLECULAR-DYNAMICS",)),
    ("011", "SFT-MAT-COMP-ELECTRONIC-STRUCTURE-011", "electronic-structure computational correspondence", ("NIST-COMPUTATIONAL-MATERIALS",)),
    ("012", "SFT-MAT-COMP-SIMULATION-EXPERIMENT-012", "simulation-to-experiment validation ledger", ("NIST-SIMULATION-VALIDATION",)),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    value = {
        "schema": "sft-v3-materials-comp-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "computational_materials_structure_property_exact_uncertainty",
        "selection_rule": "All twelve obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-COMP-{number}", "claim_id": claim_id, "target_class": target_class, "source_identities": list(source_ids)}
            for number, claim_id, target_class, source_ids in ROWS
        ],
        "target_count": 12,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(value["registry_identity"])


if __name__ == "__main__":
    main()
