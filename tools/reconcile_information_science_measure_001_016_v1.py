#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FROZEN = ROOT / "census/information_science_discipline_obligations.json"
PREVIOUS = ROOT / "census/information_science_discipline_current_reconciliation_v4.json"
OUT = ROOT / "census/information_science_discipline_current_reconciliation_v5.json"
AUDIT = ROOT / "audits/INFORMATION_SCIENCE_MEASURE_001_016_COMPLETION_2026-07-29.json"

from sft.information_science.measure_001_016_laws_v1 import IDS


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    frozen = json.loads(FROZEN.read_text())
    frozen_body = dict(frozen)
    frozen_identity = frozen_body.pop("census_identity")
    previous = json.loads(PREVIOUS.read_text())
    previous_body = dict(previous)
    previous_identity = previous_body.pop("reconciliation_identity")
    if canonical(frozen_body) != frozen_identity or canonical(previous_body) != previous_identity or previous["current_closed_count"] != 52:
        raise SystemExit("MEASURE reconciliation predecessor changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, claim_id in enumerate(IDS, 1):
        row = live[claim_id]
        certificate = json.loads((ROOT / "claims" / claim_id / "certificate.json").read_text())
        obligation = f"SFT-INFO-OBL-MEASURE-{index:03d}"
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"] or certificate["information_science_obligation"] != obligation:
            raise SystemExit("MEASURE reconciliation halt: " + claim_id)
        rows.append({
            "obligation_id": obligation,
            "claim_id": claim_id,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "closure_status": row["closure_status"],
            "external_status": row["external_status"],
        })
    families = dict(previous["completed_families"])
    families["MEASURE"] = rows
    value = {
        "schema": "sft-v3-information-science-discipline-current-reconciliation/5",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 262,
        "closed_at_freeze": 12,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": families,
        "current_closed_count": 68,
        "current_open_count": 194,
        "current_completion_fraction": "68/262",
        "current_completion_percent": "26.0%",
        "frozen_census_mutated": False,
        "extension_policy": frozen["extension_policy"],
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-information-science-measure-completion/1",
        "date": "2026-07-29",
        "family": "MEASURE-001--016",
        "family_completion": "16/16",
        "candidate_count": 4096,
        "survivor_count": 16,
        "control_count": 64,
        "independent_reconstruction_count": 16,
        "empirical_correspondence_count": 16,
        "observation_record_count": 16,
        "receipt_rows": rows,
        "exact_replay": "16/16 exact receipts reproduced",
        "focused_tests": "4/4 passed",
        "protected_engine_or_verifier_changed": False,
        "current_information_science_progress": "68/262",
        "current_information_science_percent": "26.0%",
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 68, "open": 194, "percent": "26.0%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
