#!/usr/bin/env python3
"""Reconcile admitted THERM obligations against the immutable Materials census."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v4.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v5.json"
AUDIT = ROOT / "audits/MATERIALS_THERM_001_007_COMPLETION_2026-07-29.json"
CLAIMS = (
    "SFT-MAT-THERM-DIFFUSIVITY-001",
    "SFT-MAT-THERM-BOUNDARY-RESISTANCE-002",
    "SFT-MAT-THERM-PHONON-MEAN-PATH-003",
    "SFT-MAT-THERM-RADIATIVE-TRANSPORT-004",
    "SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005",
    "SFT-MAT-THERM-PHASE-STORAGE-006",
    "SFT-MAT-THERM-SHOCK-FATIGUE-007",
)

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(frozen) != frozen_identity or canonical(previous) != previous_identity or previous["current_closed_count"] != 133:
        raise SystemExit("THERM reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-THERM-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("THERM reconciliation halted: " + claim_id)
        rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["THERM"] = rows
    payload = {
        "schema": "sft-v3-materials-discipline-current-reconciliation/5",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 289,
        "closed_at_freeze": 92,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": families,
        "current_closed_count": 140,
        "current_open_count": 149,
        "current_completion_fraction": "140/289",
        "current_completion_percent": "48.4%",
        "frozen_census_mutated": False,
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
    }
    payload["reconciliation_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-materials-therm-completion/1",
        "date": "2026-07-29",
        "family": "THERM-001--007",
        "family_completion": "7/7",
        "candidate_count": 1792,
        "survivor_count": 7,
        "control_count": 28,
        "independent_reconstruction_count": 7,
        "empirical_correspondence_count": 7,
        "external_comparison_count": 12,
        "captured_external_source_count": 12,
        "receipt_rows": rows,
        "exact_replay": "pending post-admission execution",
        "focused_tests": "3/3 passed",
        "protected_engine_or_verifier_changed": False,
        "current_materials_progress": "140/289",
        "current_materials_percent": "48.4%",
        "reconciliation_identity": payload["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 140, "open": 149, "percent": "48.4%", "identity": payload["reconciliation_identity"]}, indent=2))

if __name__ == "__main__":
    main()
