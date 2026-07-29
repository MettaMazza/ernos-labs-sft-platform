#!/usr/bin/env python3
"""Freeze SOURCE claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/information_science_source_001_014_target_registry_v1.json"
IDS = (
    "SFT-INFO-SOURCE-SUPPORT-001",
    "SFT-INFO-SOURCE-SEQUENCE-ORDER-002",
    "SFT-INFO-SOURCE-PROCESS-TRANSITION-003",
    "SFT-INFO-SOURCE-SPATIAL-ADJACENCY-004",
    "SFT-INFO-SOURCE-NETWORK-PATH-005",
    "SFT-INFO-SOURCE-REFINEMENT-COARSENING-006",
    "SFT-INFO-SOURCE-STATIONARY-SUPPORT-007",
    "SFT-INFO-SOURCE-NONSTATIONARY-SUPPORT-008",
    "SFT-INFO-SOURCE-MEMORYLESS-009",
    "SFT-INFO-SOURCE-FINITE-MEMORY-010",
    "SFT-INFO-SOURCE-JOINT-COMPOSITION-011",
    "SFT-INFO-SOURCE-DEPENDENCE-COMMON-SUPPORT-012",
    "SFT-INFO-SOURCE-SUCCESSOR-013",
    "SFT-INFO-SOURCE-COMPLETENESS-014",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("SOURCE registry already frozen")
    census = json.loads((ROOT / "census/information_science_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "SOURCE"]
    if len(rows) != len(IDS) or len(IDS) != 14:
        raise SystemExit("SOURCE census changed")
    payload = {
        "schema": "sft-v3-information-science-source-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "information_science_census_identity": census["census_identity"],
        "claim_ids": IDS,
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all fourteen claims; no proper subset",
        "prohibited_target_fields": ["expected source result", "selected survivor", "match result", "imported stochastic-source answer"],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
