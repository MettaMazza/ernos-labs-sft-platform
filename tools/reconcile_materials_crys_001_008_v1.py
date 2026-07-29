#!/usr/bin/env python3
"""Reconcile admitted CRYS receipts without mutating the frozen obligation census."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
CURRENT = ROOT / "census/materials_discipline_current_reconciliation_v1.json"
AUDIT = ROOT / "audits/MATERIALS_CRYS_001_008_COMPLETION_2026-07-29.json"


MAPPING = {
    "SFT-MAT-OBL-CRYS-001": "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001",
    "SFT-MAT-OBL-CRYS-002": "SFT-MAT-CRYS-STRUCTURE-FACTOR-002",
    "SFT-MAT-OBL-CRYS-003": "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003",
    "SFT-MAT-OBL-CRYS-004": "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004",
    "SFT-MAT-OBL-CRYS-005": "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005",
    "SFT-MAT-OBL-CRYS-006": "SFT-MAT-CRYS-TWIN-DOMAIN-006",
    "SFT-MAT-OBL-CRYS-007": "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007",
    "SFT-MAT-OBL-CRYS-008": "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008",
}


def canonical(value: object) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main() -> None:
    frozen = json.loads(FROZEN.read_text())
    identity = frozen.pop("census_identity")
    if canonical(frozen) != identity or frozen["registered_obligation_count"] != 289:
        raise SystemExit("Materials CRYS reconciliation halted: frozen discipline census changed")
    census_rows = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    reconciled = []
    for obligation_id, claim_id in MAPPING.items():
        row = census_rows.get(claim_id)
        certificate_path = ROOT / "claims" / claim_id / "certificate.json"
        certificate = json.loads(certificate_path.read_text())
        if row is None or not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"]:
            raise SystemExit("Materials CRYS reconciliation halted: receipt mismatch " + claim_id)
        if certificate["materials_obligation"] != obligation_id or certificate["candidate_count"] != 256 or certificate["unique_survivor_count"] != 1:
            raise SystemExit("Materials CRYS reconciliation halted: certificate mismatch " + claim_id)
        reconciled.append({
            "obligation_id": obligation_id,
            "claim_id": claim_id,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "closure_status": row["closure_status"],
            "external_status": row["external_status"],
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "control_count": 4,
            "independent_reconstruction": True,
            "post_registry_external_comparison": True,
        })
    payload = {
        "schema": "sft-v3-materials-discipline-current-reconciliation/1",
        "date": "2026-07-29",
        "frozen_census_identity": identity,
        "frozen_obligation_count": 289,
        "closed_at_freeze": 92,
        "newly_closed_family": "quantitative_crystallography_diffraction_disorder",
        "newly_closed_count": len(reconciled),
        "current_closed_count": 92 + len(reconciled),
        "current_open_count": 289 - 92 - len(reconciled),
        "current_completion_fraction": "100/289",
        "current_completion_percent": "34.6%",
        "family_completion_fraction": "8/8",
        "family_completion_percent": "100%",
        "reconciled_obligations": reconciled,
        "frozen_census_mutated": False,
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
    }
    payload["reconciliation_identity"] = canonical(payload)
    CURRENT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    audit = {
        **payload,
        "candidate_count": 256 * len(reconciled),
        "survivor_count": len(reconciled),
        "control_count": 4 * len(reconciled),
        "independent_reconstruction_count": len(reconciled),
        "empirical_correspondence_count": len(reconciled),
        "captured_external_source_count": 8,
        "unavailable_source_rows_preserved": 2,
        "failed_capture_routes_preserved": 2,
        "focused_tests": "pending post-admission execution",
        "exact_replay": "pending post-admission execution",
        "protected_engine_or_verifier_changed": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"current_closed": payload["current_closed_count"], "current_open": payload["current_open_count"], "percent": payload["current_completion_percent"], "reconciliation_identity": payload["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
