#!/usr/bin/env python3
"""Freeze value-free authoritative targets for the complete THERM family."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_therm_001_007_target_registry_v1.json"

ROWS = (
    ("001", "SFT-MAT-THERM-DIFFUSIVITY-001", "thermal conductivity, volumetric heat capacity and diffusivity relation", ("NIST-MATERIALS-DATA-GUIDE", "NIST-THERMAL-DIFFUSIVITY-AM")),
    ("002", "SFT-MAT-THERM-BOUNDARY-RESISTANCE-002", "thermal interface resistance and multilayer transport record", ("NIST-FDTR-TRANSPORT",)),
    ("003", "SFT-MAT-THERM-PHONON-MEAN-PATH-003", "phonon scattering and mean-free-path thermal-transport record", ("NIST-PHONON-THERMAL-LIMITS", "NIST-INTERFACE-SCATTERING")),
    ("004", "SFT-MAT-THERM-RADIATIVE-TRANSPORT-004", "spectral reflectance, transmittance, emittance and radiative-transfer record", ("NIST-INFRARED-OPTICAL-PROPERTIES",)),
    ("005", "SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005", "Seebeck, resistivity, temperature and thermal-conductivity coupled-response record", ("NIST-THERMOELECTRIC-MEASUREMENTS", "NIST-TRANSPORT-THERMOELECTRIC")),
    ("006", "SFT-MAT-THERM-PHASE-STORAGE-006", "phase-change latent and sensible thermal-storage record", ("NIST-PHASE-CHANGE-STORAGE", "NIST-NANOCALORIMETRY")),
    ("007", "SFT-MAT-THERM-SHOCK-FATIGUE-007", "temperature-step, thermal-strain, crack-initiation and repeated-cycle record", ("NIST-FRACTOGRAPHY-THERMAL-SHOCK", "NIST-THERMAL-SHOCK-SILICON-NITRIDE")),
)

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    if OUT.exists():
        raise SystemExit("refusing to overwrite frozen THERM registry")
    payload = {
        "schema": "sft-v3-materials-therm-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "thermal_transport_storage_expansion_thermoelectric",
        "selection_rule": "All seven obligations, comparison classes and authoritative source identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "The registry contains source identities and target classes only; it contains no measured value, detailed source fragment, candidate, survivor or comparison outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-THERM-{number}", "claim_id": claim_id, "target_class": target, "source_identities": list(sources)}
            for number, claim_id, target, sources in ROWS
        ],
        "target_count": 7,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"target_count": 7, "registry_identity": payload["registry_identity"]}, indent=2))

if __name__ == "__main__":
    main()
