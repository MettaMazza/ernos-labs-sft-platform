#!/usr/bin/env python3
"""Freeze all EXT target identities before source capture or outcome extraction."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_ext_001_008_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-EXT-HIGH-PRESSURE-STATE-001", "high-pressure material state", ("NIST-HIGH-PRESSURE-MATERIAL-TESTING",)),
    ("002", "SFT-MAT-EXT-HIGH-TEMPERATURE-STATE-002", "high-temperature material state", ("NIST-HIGH-TEMPERATURE-THERMOELECTRIC",)),
    ("003", "SFT-MAT-EXT-CRYOGENIC-RESPONSE-003", "cryogenic material response", ("NIST-CRYOGENIC-MATERIAL-PROPERTIES",)),
    ("004", "SFT-MAT-EXT-ELECTRIC-FIELD-RESPONSE-004", "high-electric-field material response", ("NIST-ELECTRIC-FIELD-RESPONSE",)),
    ("005", "SFT-MAT-EXT-MAGNETIC-FIELD-RESPONSE-005", "high-magnetic-field material response", ("NIST-HIGH-MAGNETIC-FIELD",)),
    ("006", "SFT-MAT-EXT-SHOCK-RESPONSE-006", "high-strain-rate and shock response", ("NIST-SHOCKWAVE-MATERIAL-RESPONSE",)),
    ("007", "SFT-MAT-EXT-RADIATION-RESPONSE-007", "extreme-radiation material response", ("NIST-RADIATION-DAMAGE-MEASUREMENT",)),
    ("008", "SFT-MAT-EXT-COMBINED-PATH-CUSTODY-008", "combined-extreme condition and path custody", ("NIST-COMBINED-EXTREME-KOLSKY",)),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    value = {
        "schema": "sft-v3-materials-ext-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "materials_under_extreme_conditions_complete_path_custody",
        "selection_rule": "All eight obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-EXT-{number}", "claim_id": claim_id, "target_class": target_class, "source_identities": list(source_ids)}
            for number, claim_id, target_class, source_ids in ROWS
        ],
        "target_count": 8,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(value["registry_identity"])


if __name__ == "__main__":
    main()
