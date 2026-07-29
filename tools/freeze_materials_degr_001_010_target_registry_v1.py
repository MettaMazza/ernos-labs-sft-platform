#!/usr/bin/env python3
"""Freeze all DEGR target identities before source capture or outcome extraction."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_degr_001_010_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-DEGR-OXIDATION-SCALE-001", "oxidation scale growth and transport", ("NIST-OXIDE-GROWTH",)),
    ("002", "SFT-MAT-DEGR-CORROSION-PATH-002", "corrosion-rate and electrochemical-path ledger", ("NIST-ELECTROCHEMICAL-CORROSION",)),
    ("003", "SFT-MAT-DEGR-PASSIVATION-BREAKDOWN-003", "passivation and film-breakdown boundary", ("NIST-LOCALIZED-CORROSION-RESISTANCE",)),
    ("004", "SFT-MAT-DEGR-STRESS-CORROSION-004", "stress-corrosion cracking", ("NIST-STRESS-CORROSION-CRACK",)),
    ("005", "SFT-MAT-DEGR-HYDROGEN-EMBRITTLEMENT-005", "hydrogen uptake and embrittlement", ("NIST-HYDROGEN-UPTAKE-EMBRITTLEMENT",)),
    ("006", "SFT-MAT-DEGR-WEAR-MODE-DISTINCTION-006", "abrasive adhesive and erosive wear distinction", ("NIST-MULTIAXIAL-WEAR",)),
    ("007", "SFT-MAT-DEGR-RADIATION-DEFECT-RECOVERY-007", "radiation-defect accumulation and recovery", ("NIST-UV-RADIATION-DAMAGE",)),
    ("008", "SFT-MAT-DEGR-PHYSICAL-AGEING-008", "physical ageing and property drift", ("NIST-PHYSICAL-AGEING-RECOVERY",)),
    ("009", "SFT-MAT-DEGR-WEATHERING-009", "environmental attack and weathering", ("NIST-WEATHER-MATERIAL-RESPONSE",)),
    ("010", "SFT-MAT-DEGR-SERVICE-LIFE-EVIDENCE-010", "service-life and failure-time evidence boundary", ("NIST-SERVICE-LIFE-BOUNDARY",)),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    value = {
        "schema": "sft-v3-materials-degr-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "degradation_corrosion_oxidation_radiation_ageing",
        "selection_rule": "All ten obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-DEGR-{number}", "claim_id": claim_id, "target_class": target_class, "source_identities": list(source_ids)}
            for number, claim_id, target_class, source_ids in ROWS
        ],
        "target_count": 10,
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
