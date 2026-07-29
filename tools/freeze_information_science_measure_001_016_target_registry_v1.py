#!/usr/bin/env python3
"""Freeze MEASURE claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/information_science_measure_001_016_target_registry_v1.json"
IDS = (
    "SFT-INFO-MEASURE-DISTINCTION-COUNT-001",
    "SFT-INFO-MEASURE-COMBINATORIAL-QUANTITY-002",
    "SFT-INFO-MEASURE-OPERATIONAL-COST-003",
    "SFT-INFO-MEASURE-DESCRIPTION-LENGTH-004",
    "SFT-INFO-MEASURE-ALGORITHMIC-BOUNDARY-005",
    "SFT-INFO-MEASURE-PARTITION-REFINEMENT-006",
    "SFT-INFO-MEASURE-PRODUCT-ADDITIVITY-007",
    "SFT-INFO-MEASURE-SHARED-SUBADDITIVITY-008",
    "SFT-INFO-MEASURE-COARSENING-MONOTONICITY-009",
    "SFT-INFO-MEASURE-BALANCE-LEDGER-010",
    "SFT-INFO-MEASURE-RELATIVE-011",
    "SFT-INFO-MEASURE-DIVERGENCE-012",
    "SFT-INFO-MEASURE-GEOMETRY-013",
    "SFT-INFO-MEASURE-MULTISCALE-014",
    "SFT-INFO-MEASURE-UNIT-CUSTODY-015",
    "SFT-INFO-MEASURE-COMPLETENESS-016",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("MEASURE registry already frozen")
    census = json.loads((ROOT / "census/information_science_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "MEASURE"]
    if len(rows) != len(IDS) or len(IDS) != 16:
        raise SystemExit("MEASURE census changed")
    payload = {
        "schema": "sft-v3-information-science-measure-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "information_science_census_identity": census["census_identity"],
        "claim_ids": IDS,
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all sixteen claims; no proper subset",
        "prohibited_target_fields": ["expected information value", "selected survivor", "match result", "imported logarithmic or algorithmic-information answer"],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__": main()
