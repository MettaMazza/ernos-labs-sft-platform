#!/usr/bin/env python3
"""Freeze SYMREP claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/information_science_symrep_001_014_target_registry_v1.json"
IDS = (
    "SFT-INFO-SYMREP-ALPHABET-GENERATION-001",
    "SFT-INFO-SYMREP-SYMBOL-IDENTITY-DISTINCTION-002",
    "SFT-INFO-SYMREP-CODEWORD-PARSING-003",
    "SFT-INFO-SYMREP-PREFIX-UNIQUE-DECODING-004",
    "SFT-INFO-SYMREP-GRAMMAR-REPRESENTATION-005",
    "SFT-INFO-SYMREP-EQUIVALENCE-ISOMORPHISM-006",
    "SFT-INFO-SYMREP-CANONICAL-NORMALIZATION-007",
    "SFT-INFO-SYMREP-VARIABLE-LENGTH-BOUNDARY-008",
    "SFT-INFO-SYMREP-PRODUCT-ALPHABET-009",
    "SFT-INFO-SYMREP-HIERARCHICAL-TYPED-SYMBOL-010",
    "SFT-INFO-SYMREP-CONVERSION-TRANSDUCTION-011",
    "SFT-INFO-SYMREP-AMBIGUITY-ALTERNATIVES-012",
    "SFT-INFO-SYMREP-FINITE-SUCCESSOR-013",
    "SFT-INFO-SYMREP-COMPLETENESS-014",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("SYMREP registry already frozen")
    census = json.loads((ROOT / "census/information_science_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "SYMREP"]
    if len(rows) != len(IDS) or len(IDS) != 14:
        raise SystemExit("SYMREP census changed")
    payload = {
        "schema": "sft-v3-information-science-symrep-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "information_science_census_identity": census["census_identity"],
        "claim_ids": IDS,
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all fourteen claims; no proper subset",
        "prohibited_target_fields": [
            "expected representation result",
            "selected survivor",
            "match result",
            "imported coding theorem answer",
        ],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
