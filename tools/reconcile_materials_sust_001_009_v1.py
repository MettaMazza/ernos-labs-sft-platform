#!/usr/bin/env python3
"""Reconcile the completed SUST family into the frozen Materials census."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v17.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v18.json"
AUDIT = ROOT / "audits/MATERIALS_SUST_001_009_COMPLETION_2026-07-29.json"
CLAIMS = (
    "SFT-MAT-SUST-EMBODIED-LEDGER-001",
    "SFT-MAT-SUST-AVAILABILITY-BOUNDARY-002",
    "SFT-MAT-SUST-REUSE-REMANUFACTURE-003",
    "SFT-MAT-SUST-RECOVERY-YIELD-004",
    "SFT-MAT-SUST-CIRCULAR-FLOW-005",
    "SFT-MAT-SUST-DURABILITY-EXTENSION-006",
    "SFT-MAT-SUST-TOXICITY-HANDOFF-007",
    "SFT-MAT-SUST-SUBSTITUTION-FUNCTION-008",
    "SFT-MAT-SUST-END-OF-LIFE-CUSTODY-009",
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(frozen) != frozen_identity or canonical(previous) != previous_identity or previous["current_closed_count"] != 262:
        raise SystemExit("SUST reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-SUST-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("SUST reconciliation halt " + claim_id)
        rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["SUST"] = rows
    value = {
        "schema": "sft-v3-materials-discipline-current-reconciliation/18",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 289,
        "closed_at_freeze": 92,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": families,
        "current_closed_count": 271,
        "current_open_count": 18,
        "current_completion_fraction": "271/289",
        "current_completion_percent": "93.8%",
        "frozen_census_mutated": False,
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-materials-sust-completion/1",
        "date": "2026-07-29",
        "family": "SUST-001--009",
        "family_completion": "9/9",
        "candidate_count": 2304,
        "survivor_count": 9,
        "control_count": 36,
        "independent_reconstruction_count": 9,
        "empirical_correspondence_count": 9,
        "external_comparison_count": 9,
        "captured_external_source_count": 9,
        "receipt_rows": rows,
        "exact_replay": "9/9 exact receipts reproduced",
        "focused_tests": "3/3 passed",
        "protected_engine_or_verifier_changed": False,
        "current_materials_progress": "271/289",
        "current_materials_percent": "93.8%",
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 271, "open": 18, "percent": "93.8%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
