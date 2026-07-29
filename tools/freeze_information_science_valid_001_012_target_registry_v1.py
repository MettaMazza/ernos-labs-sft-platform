#!/usr/bin/env python3
"""Freeze the value-free VALID-001--012 target registry before vector access."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.information_science.valid_001_012_laws_v1 import IDS, SPECS


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    output = ROOT / "census/information_science_valid_001_012_target_registry_v1.json"
    if output.exists():
        raise SystemExit("refusing overwrite " + str(output))
    census = json.loads((ROOT / "census/information_science_discipline_obligations.json").read_text())
    value = {
        "authority": "Maria Smith",
        "claim_ids": list(IDS),
        "completion_unit": "all twelve claims; no proper subset",
        "date": "2026-07-29",
        "frozen_before_observation_access": True,
        "information_science_census_identity": census["census_identity"],
        "obligation_ids": [f"SFT-INFO-OBL-VALID-{index:03d}" for index in range(1, 13)],
        "prohibited_target_fields": [
            "expected validation outcome",
            "selected survivor",
            "match result",
            "post-outcome exclusions, fitted tolerances or favorable-only row selection",
        ],
        "question_titles": [SPECS[claim_id].title for claim_id in IDS],
        "schema": "sft-v3-information-science-valid-value-free-registry/1",
        "target_content_present": False,
    }
    value["registry_identity"] = canonical(value)
    output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"registry": str(output.relative_to(ROOT)), "identity": value["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
