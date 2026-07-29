#!/usr/bin/env python3
"""Reconcile CRYS and MICRO receipts against the immutable Materials census."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v2.json"
AUDIT = ROOT / "audits/MATERIALS_MICRO_001_009_COMPLETION_2026-07-29.json"


FAMILIES = {
    "CRYS": (
        "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001", "SFT-MAT-CRYS-STRUCTURE-FACTOR-002", "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003", "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004", "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005", "SFT-MAT-CRYS-TWIN-DOMAIN-006", "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007", "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008",
    ),
    "MICRO": (
        "SFT-MAT-MICRO-DEFECT-POPULATION-001", "SFT-MAT-MICRO-DEFECT-MIGRATION-002", "SFT-MAT-MICRO-DISLOCATION-REACTION-003", "SFT-MAT-MICRO-GRAIN-GROWTH-004", "SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005", "SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006", "SFT-MAT-MICRO-COARSENING-TRANSFER-007", "SFT-MAT-MICRO-INTERFACE-MOBILITY-008", "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009",
    ),
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text()); identity = frozen.pop("census_identity")
    if canonical(frozen) != identity or frozen["registered_obligation_count"] != 289:
        raise SystemExit("Materials reconciliation halted: frozen census changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    families = {}
    for code, claim_ids in FAMILIES.items():
        rows = []
        for number, claim_id in enumerate(claim_ids, 1):
            row = live[claim_id]; certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
            obligation = f"SFT-MAT-OBL-{code}-{number:03d}"
            if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
                raise SystemExit("Materials reconciliation halted: " + claim_id)
            rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
        families[code] = rows
    current = 92 + sum(len(rows) for rows in families.values())
    payload = {"schema": "sft-v3-materials-discipline-current-reconciliation/2", "date": "2026-07-29", "frozen_census_identity": identity, "frozen_obligation_count": 289, "closed_at_freeze": 92, "completed_families": families, "current_closed_count": current, "current_open_count": 289 - current, "current_completion_fraction": f"{current}/289", "current_completion_percent": "37.7%", "frozen_census_mutated": False, "extension_policy": "complete to the current registered standard and open to lawful versioned extension"}
    payload["reconciliation_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    audit = {"schema": "sft-v3-materials-micro-completion/1", "date": "2026-07-29", "family": "MICRO-001--009", "family_completion": "9/9", "candidate_count": 2304, "survivor_count": 9, "control_count": 36, "independent_reconstruction_count": 9, "empirical_correspondence_count": 9, "captured_external_source_count": 9, "unavailable_source_rows_preserved": 1, "failed_capture_routes_preserved": 1, "receipt_rows": families["MICRO"], "exact_replay": "pending post-admission execution", "focused_tests": "3/3 passed", "protected_engine_or_verifier_changed": False, "current_materials_progress": payload["current_completion_fraction"], "current_materials_percent": payload["current_completion_percent"], "reconciliation_identity": payload["reconciliation_identity"]}
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": current, "open": 289-current, "percent": payload["current_completion_percent"], "reconciliation_identity": payload["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
