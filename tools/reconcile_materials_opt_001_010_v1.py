#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v7.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v8.json"
AUDIT = ROOT / "audits/MATERIALS_OPT_001_010_COMPLETION_2026-07-29.json"
CLAIMS = (
    "SFT-MAT-OPT-ABSORPTION-EXTINCTION-001",
    "SFT-MAT-OPT-REFLECTION-TRANSMISSION-002",
    "SFT-MAT-OPT-LUMINESCENCE-YIELD-003",
    "SFT-MAT-OPT-LIGHT-SCATTERING-004",
    "SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005",
    "SFT-MAT-OPT-NONLINEAR-MIXING-006",
    "SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007",
    "SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008",
    "SFT-MAT-OPT-PLASMONIC-RESPONSE-009",
    "SFT-MAT-OPT-EXCITON-DYNAMICS-010",
)

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(frozen) != frozen_identity or canonical(previous) != previous_identity or previous["current_closed_count"] != 164:
        raise SystemExit("OPT reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-OPT-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("OPT reconciliation halt " + claim_id)
        rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["OPT"] = rows
    payload = {"schema": "sft-v3-materials-discipline-current-reconciliation/8", "date": "2026-07-29", "frozen_census_identity": frozen_identity, "frozen_obligation_count": 289, "closed_at_freeze": 92, "predecessor_reconciliation_identity": previous_identity, "completed_families": families, "current_closed_count": 174, "current_open_count": 115, "current_completion_fraction": "174/289", "current_completion_percent": "60.2%", "frozen_census_mutated": False, "extension_policy": "complete to the current registered standard and open to lawful versioned extension"}
    payload["reconciliation_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    audit = {"schema": "sft-v3-materials-opt-completion/1", "date": "2026-07-29", "family": "OPT-001--010", "family_completion": "10/10", "candidate_count": 2560, "survivor_count": 10, "control_count": 40, "independent_reconstruction_count": 10, "empirical_correspondence_count": 10, "external_comparison_count": 14, "captured_external_source_count": 11, "initial_source_limitation_preserved": True, "receipt_rows": rows, "exact_replay": "pending post-admission execution", "focused_tests": "3/3 passed", "protected_engine_or_verifier_changed": False, "current_materials_progress": "174/289", "current_materials_percent": "60.2%", "reconciliation_identity": payload["reconciliation_identity"]}
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 174, "open": 115, "percent": "60.2%", "identity": payload["reconciliation_identity"]}, indent=2))

if __name__ == "__main__":
    main()
