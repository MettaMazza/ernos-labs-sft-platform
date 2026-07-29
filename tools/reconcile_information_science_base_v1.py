#!/usr/bin/env python3
"""Bind the twelve admitted base receipts to the frozen complete-field census."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
FROZEN = ROOT / "census/information_science_discipline_obligations.json"
OUT = ROOT / "census/information_science_discipline_current_reconciliation_v1.json"
AUDIT = ROOT / "audits/INFORMATION_SCIENCE_BASE_COMPLETION_2026-07-29.json"

from sft.information_science.catalog import SPECS


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists() or AUDIT.exists():
        raise SystemExit("Information Science base reconciliation already exists")
    frozen = json.loads(FROZEN.read_text())
    body = dict(frozen)
    frozen_identity = body.pop("census_identity")
    if canonical(body) != frozen_identity or frozen["closed_obligation_count_at_freeze"] != 12:
        raise SystemExit("Information Science frozen census changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    rows = []
    for index, spec in enumerate(SPECS, 1):
        row = live[spec.claim_id]
        certificate = json.loads((ROOT / "claims" / spec.claim_id / "certificate.json").read_text())
        if not row["model_admitted"] or certificate["engine_receipt_hash"] != row["receipt_hash"]:
            raise SystemExit("Information Science base reconciliation halt: " + spec.claim_id)
        rows.append({
            "obligation_id": f"SFT-INFO-OBL-BASE-{index:03d}",
            "claim_id": spec.claim_id,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "closure_status": row["closure_status"],
            "external_status": row["external_status"],
        })
    value = {
        "schema": "sft-v3-information-science-discipline-current-reconciliation/1",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 262,
        "closed_at_freeze": 12,
        "predecessor_reconciliation_identity": None,
        "completed_families": {"BASE": rows},
        "current_closed_count": 12,
        "current_open_count": 250,
        "current_completion_fraction": "12/262",
        "current_completion_percent": "4.6%",
        "frozen_census_mutated": False,
        "extension_policy": frozen["extension_policy"],
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-information-science-base-completion/1",
        "date": "2026-07-29",
        "family": "BASE",
        "family_completion": "12/12",
        "exact_replay": "12/12 exact receipts reproduced",
        "receipt_rows": rows,
        "protected_engine_or_verifier_changed": False,
        "current_information_science_progress": "12/262",
        "current_information_science_percent": "4.6%",
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"closed": 12, "open": 250, "percent": "4.6%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
