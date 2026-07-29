#!/usr/bin/env python3
"""Freeze all OPT-001--010 target identities before detailed source outcomes open."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_opt_001_010_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-OPT-ABSORPTION-EXTINCTION-001", "optical absorption and extinction response", ("NIST-SPECTROPHOTOMETRY",)),
    ("002", "SFT-MAT-OPT-REFLECTION-TRANSMISSION-002", "reflection, transmission and retained optical balance", ("NIST-SPECTROPHOTOMETRY", "NIST-OPTICAL-SCATTERING")),
    ("003", "SFT-MAT-OPT-LUMINESCENCE-YIELD-003", "luminescence excitation-emission and quantum-yield custody", ("NIST-FLUORESCENCE-RAMAN",)),
    ("004", "SFT-MAT-OPT-LIGHT-SCATTERING-004", "elastic and inelastic light-scattering record", ("NIST-OPTICAL-SCATTERING", "NIST-FLUORESCENCE-RAMAN")),
    ("005", "SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005", "birefringence and optical-anisotropy response", ("NIST-BIREFRINGENCE",)),
    ("006", "SFT-MAT-OPT-NONLINEAR-MIXING-006", "nonlinear optical frequency and polarization mixing", ("NIST-NONLINEAR-MIXING",)),
    ("007", "SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007", "waveguide confinement, coupling and loss ledger", ("NIST-WAVEGUIDE-LOSS",)),
    ("008", "SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008", "photonic band-gap exclusion and defect-mode confinement", ("NIST-PHOTONIC-BANDGAP",)),
    ("009", "SFT-MAT-OPT-PLASMONIC-RESPONSE-009", "collective plasmonic mode and confined optical response", ("NIST-PLASMONIC-MODES",)),
    ("010", "SFT-MAT-OPT-EXCITON-DYNAMICS-010", "exciton generation, transport and recombination history", ("NIST-EXCITON-DYNAMICS", "NIST-CARRIER-DYNAMICS")),
)

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    payload = {
        "schema": "sft-v3-materials-opt-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "optics_photonics_polarization_electromagnetic_materials",
        "selection_rule": "All ten obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [{"obligation_id": f"SFT-MAT-OBL-OPT-{number}", "claim_id": claim_id, "target_class": target, "source_identities": list(sources)} for number, claim_id, target, sources in ROWS],
        "target_count": 10,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(payload["registry_identity"])

if __name__ == "__main__":
    main()
