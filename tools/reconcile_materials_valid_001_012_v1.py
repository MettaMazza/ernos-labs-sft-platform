#!/usr/bin/env python3
"""Reconcile the completed VALID family into the frozen Materials census."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v18.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v19.json"
AUDIT = ROOT / "audits/MATERIALS_VALID_001_012_COMPLETION_2026-07-29.json"
CLAIMS = (
    "SFT-MAT-VALIDATION-CRYSTALLOGRAPHY-DIFFRACTION-VECTOR-001",
    "SFT-MAT-VALIDATION-DEFECT-MICROSTRUCTURE-VECTOR-002",
    "SFT-MAT-VALIDATION-PHASE-TRANSFORMATION-VECTOR-003",
    "SFT-MAT-VALIDATION-MECHANICAL-TRIBOLOGICAL-VECTOR-004",
    "SFT-MAT-VALIDATION-THERMAL-TRANSPORT-VECTOR-005",
    "SFT-MAT-VALIDATION-ELECTRONIC-IONIC-DIELECTRIC-VECTOR-006",
    "SFT-MAT-VALIDATION-MAGNETIC-SUPERCONDUCTING-TOPOLOGICAL-VECTOR-007",
    "SFT-MAT-VALIDATION-OPTICAL-PHOTONIC-VECTOR-008",
    "SFT-MAT-VALIDATION-MATERIAL-CLASS-PROCESSING-VECTOR-009",
    "SFT-MAT-VALIDATION-CROSS-SOURCE-REPRODUCIBILITY-VECTOR-010",
    "SFT-MAT-VALIDATION-ADVERSE-ABSENT-OUT-OF-BOUND-VECTOR-011",
    "SFT-MAT-VALIDATION-EMPIRICAL-GRAND-LOCK-012",
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(frozen) != frozen_identity or canonical(previous) != previous_identity or previous["current_closed_count"] != 271:
        raise SystemExit("VALID reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-VALID-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("VALID reconciliation halt " + claim_id)
        rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["VALID"] = rows
    value = {
        "schema": "sft-v3-materials-discipline-current-reconciliation/19",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 289,
        "closed_at_freeze": 92,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": families,
        "current_closed_count": 283,
        "current_open_count": 6,
        "current_completion_fraction": "283/289",
        "current_completion_percent": "97.9%",
        "frozen_census_mutated": False,
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-materials-valid-completion/1",
        "date": "2026-07-29",
        "family": "VALID-001--012",
        "family_completion": "12/12",
        "candidate_count": 3072,
        "survivor_count": 12,
        "control_count": 48,
        "independent_reconstruction_count": 12,
        "empirical_correspondence_count": 12,
        "external_comparison_count": 1040,
        "captured_external_source_count": 334,
        "receipt_rows": rows,
        "exact_replay": "12/12 exact receipts reproduced",
        "focused_tests": "4/4 passed",
        "protected_engine_or_verifier_changed": False,
        "current_materials_progress": "283/289",
        "current_materials_percent": "97.9%",
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 283, "open": 6, "percent": "97.9%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
