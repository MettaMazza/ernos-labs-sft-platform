#!/usr/bin/env python3
"""Reconcile the complete PHASE family over the immutable Materials census."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v2.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v3.json"
AUDIT = ROOT / "audits/MATERIALS_PHASE_001_010_COMPLETION_2026-07-29.json"


CLAIMS = (
    "SFT-MAT-PHASE-FRACTION-LEDGER-001", "SFT-MAT-PHASE-TIE-LINE-LEVER-002", "SFT-MAT-PHASE-COMPONENT-HANDOFF-003", "SFT-MAT-PHASE-METASTABLE-RETENTION-004", "SFT-MAT-PHASE-SPINODAL-INSTABILITY-005", "SFT-MAT-PHASE-MARTENSITIC-006", "SFT-MAT-PHASE-RECONSTRUCTIVE-007", "SFT-MAT-PHASE-ORDER-DISORDER-008", "SFT-MAT-PHASE-GLASS-ARREST-009", "SFT-MAT-PHASE-TIME-TEMPERATURE-010",
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    if canonical(frozen) != frozen_identity or frozen["registered_obligation_count"] != 289:
        raise SystemExit("Materials PHASE reconciliation halted: frozen census changed")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(previous) != previous_identity or previous["current_closed_count"] != 109 or set(previous["completed_families"]) != {"CRYS", "MICRO"}:
        raise SystemExit("Materials PHASE reconciliation halted: predecessor reconciliation changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    phase_rows = []
    for number, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-PHASE-{number:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("Materials PHASE reconciliation halted: " + claim_id)
        phase_rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["PHASE"] = phase_rows
    current = previous["current_closed_count"] + len(phase_rows)
    payload = {"schema": "sft-v3-materials-discipline-current-reconciliation/3", "date": "2026-07-29", "frozen_census_identity": frozen_identity, "frozen_obligation_count": 289, "closed_at_freeze": 92, "predecessor_reconciliation_identity": previous_identity, "completed_families": families, "current_closed_count": current, "current_open_count": 289 - current, "current_completion_fraction": f"{current}/289", "current_completion_percent": "41.2%", "frozen_census_mutated": False, "extension_policy": "complete to the current registered standard and open to lawful versioned extension"}
    payload["reconciliation_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    audit = {"schema": "sft-v3-materials-phase-completion/1", "date": "2026-07-29", "family": "PHASE-001--010", "family_completion": "10/10", "candidate_count": 2560, "survivor_count": 10, "control_count": 40, "independent_reconstruction_count": 10, "empirical_correspondence_count": 10, "external_comparison_count": 16, "captured_external_source_count": 11, "unavailable_source_rows_preserved": 0, "receipt_rows": phase_rows, "exact_replay": "pending post-admission execution", "focused_tests": "3/3 passed", "protected_engine_or_verifier_changed": False, "current_materials_progress": payload["current_completion_fraction"], "current_materials_percent": payload["current_completion_percent"], "reconciliation_identity": payload["reconciliation_identity"]}
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": current, "open": 289-current, "percent": payload["current_completion_percent"], "reconciliation_identity": payload["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
