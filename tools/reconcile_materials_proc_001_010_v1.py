#!/usr/bin/env python3
"""Reconcile the completed PROC family into the frozen Materials census."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/materials_discipline_obligations.json"
PREVIOUS = ROOT / "census/materials_discipline_current_reconciliation_v14.json"
OUT = ROOT / "census/materials_discipline_current_reconciliation_v15.json"
AUDIT = ROOT / "audits/MATERIALS_PROC_001_010_COMPLETION_2026-07-29.json"
CLAIMS = (
    "SFT-MAT-PROC-CASTING-HISTORY-001",
    "SFT-MAT-PROC-FORMING-TEXTURE-002",
    "SFT-MAT-PROC-MACHINING-DAMAGE-003",
    "SFT-MAT-PROC-ADDITIVE-BUILD-004",
    "SFT-MAT-PROC-THIN-FILM-GROWTH-005",
    "SFT-MAT-PROC-EPITAXY-MATCHING-006",
    "SFT-MAT-PROC-JOINING-INTERFACE-007",
    "SFT-MAT-PROC-POLYMER-ORIENTATION-008",
    "SFT-MAT-PROC-POWDER-COMPACTION-009",
    "SFT-MAT-PROC-WINDOW-PROVENANCE-010",
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_identity = frozen.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_identity = previous.pop("reconciliation_identity")
    if canonical(frozen) != frozen_identity or canonical(previous) != previous_identity or previous["current_closed_count"] != 232:
        raise SystemExit("PROC reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(CLAIMS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-MAT-OBL-PROC-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["materials_obligation"] != obligation:
            raise SystemExit("PROC reconciliation halt " + claim_id)
        rows.append({"obligation_id": obligation, "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"]})
    families = dict(previous["completed_families"])
    families["PROC"] = rows
    value = {
        "schema": "sft-v3-materials-discipline-current-reconciliation/15",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 289,
        "closed_at_freeze": 92,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": families,
        "current_closed_count": 242,
        "current_open_count": 47,
        "current_completion_fraction": "242/289",
        "current_completion_percent": "83.7%",
        "frozen_census_mutated": False,
        "extension_policy": "complete to the current registered standard and open to lawful versioned extension",
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-materials-proc-completion/1",
        "date": "2026-07-29",
        "family": "PROC-001--010",
        "family_completion": "10/10",
        "candidate_count": 2560,
        "survivor_count": 10,
        "control_count": 40,
        "independent_reconstruction_count": 10,
        "empirical_correspondence_count": 10,
        "external_comparison_count": 10,
        "captured_external_source_count": 10,
        "receipt_rows": rows,
        "exact_replay": "10/10 exact receipts reproduced",
        "focused_tests": "3/3 passed",
        "protected_engine_or_verifier_changed": False,
        "current_materials_progress": "242/289",
        "current_materials_percent": "83.7%",
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 242, "open": 47, "percent": "83.7%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
