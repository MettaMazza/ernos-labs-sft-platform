#!/usr/bin/env python3
"""Freeze RECORD claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/information_science_record_001_012_target_registry_v1.json"
IDS = (
    "SFT-INFO-RECORD-DATA-IDENTITY-001",
    "SFT-INFO-RECORD-TUPLE-RELATION-002",
    "SFT-INFO-RECORD-METADATA-003",
    "SFT-INFO-RECORD-SCHEMA-TYPE-004",
    "SFT-INFO-RECORD-PROVENANCE-005",
    "SFT-INFO-RECORD-INTEGRITY-006",
    "SFT-INFO-RECORD-VERSION-REVISION-007",
    "SFT-INFO-RECORD-ABSENT-MISSING-UNKNOWN-008",
    "SFT-INFO-RECORD-DUPLICATE-ALIAS-009",
    "SFT-INFO-RECORD-LINKAGE-IDENTITY-010",
    "SFT-INFO-RECORD-DATASET-COMPLETENESS-011",
    "SFT-INFO-RECORD-CUSTODY-REPRODUCIBILITY-012",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("RECORD registry already frozen")
    census = json.loads((ROOT / "census/information_science_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "RECORD"]
    if len(rows) != len(IDS) or len(IDS) != 12:
        raise SystemExit("RECORD census changed")
    payload = {
        "schema": "sft-v3-information-science-record-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "information_science_census_identity": census["census_identity"],
        "claim_ids": IDS,
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all twelve claims; no proper subset",
        "prohibited_target_fields": ["expected record result", "selected survivor", "match result", "imported data-model answer"],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
