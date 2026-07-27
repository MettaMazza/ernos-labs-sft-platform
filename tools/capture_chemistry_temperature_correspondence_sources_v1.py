#!/usr/bin/env python3
"""Prepare value-free identities, then open the complete thermometric equilibrium vector for THERMO-002."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-002-temperature-correspondence-v1"
PHYSICS_RECORD_PATH = ROOT / "experiments/external_sources/physics/snapshots/thermal-equilibrium-postseal-source-record.json"
CODATA_PATH = ROOT / "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
ACOUSTIC_PATH = ROOT / "experiments/external_sources/physics/snapshots/nist-acoustic-boltzmann-2017.pdf"
ELECTRONIC_PATH = ROOT / "experiments/external_sources/physics/snapshots/nist-electronic-boltzmann-2011.pdf"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/chemical_temperature_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/chemical_temperature_withheld_targets_v1.json"
PRIMARY_PATH = SNAPSHOT_DIR / "chemical-temperature-primary-records-v1.json"

EXPECTED = {
    PHYSICS_RECORD_PATH: "sha256:8048a2397c064290a0b948b4238b4133c1a2e5c76a72ecf0c47222c9a951d7b5",
    CODATA_PATH: "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    ACOUSTIC_PATH: "sha256:1cbb21f0e5817270b5e028105aa79fea22017fd84130c2c4b79d1492fb37e418",
    ELECTRONIC_PATH: "sha256:187066b5390d57a3c058e0a34f6c7803a659045ba714ca4b25eed7b84b212bbb",
}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha256_file(path) != expected:
            raise RuntimeError(f"registered thermometric source changed: {path.relative_to(ROOT)}")

    # This registry is written without reading the post-seal value record.
    identities = (
        {
            "target_id": "SFT-CHEM-THERMO-002-COMMON-CARRIER-0001",
            "source_class": "exact-si-common-temperature-energy-carrier",
            "source_id": "NIST-CODATA-2022-BOLTZMANN",
            "route_identity": "exact-si-definition",
            "chemical_composition_identity": "all-lawful-chemical-compositions-share-one-physics-temperature-carrier",
            "phase_identity": "composition-and-phase-held-separately-from-temperature-carrier",
            "source_locator": "NIST CODATA 2022 all constants - Boltzmann constant",
            "snapshot_path": str(CODATA_PATH.relative_to(ROOT)),
            "snapshot_hash": EXPECTED[CODATA_PATH],
            "all_external_values_uncertainties_and_relation_flags_absent": True,
        },
        {
            "target_id": "SFT-CHEM-THERMO-002-ACOUSTIC-ARGON-0002",
            "source_class": "chemical-composition-bound-acoustic-gas-thermometry-route",
            "source_id": "NIM-NIST-ACOUSTIC-BOLTZMANN-2017",
            "route_identity": "cylindrical-acoustic-gas-thermometry",
            "chemical_composition_identity": "argon",
            "phase_identity": "gas",
            "equilibrium_reference_identity": "triple-point-of-water",
            "source_locator": "primary paper pages 748, 751-752; pure argon cavity held at TPW",
            "snapshot_path": str(ACOUSTIC_PATH.relative_to(ROOT)),
            "snapshot_hash": EXPECTED[ACOUSTIC_PATH],
            "all_external_values_uncertainties_and_relation_flags_absent": True,
        },
        {
            "target_id": "SFT-CHEM-THERMO-002-ELECTRONIC-0003",
            "source_class": "independent-electronic-Johnson-noise-thermometry-route",
            "source_id": "NIST-JOHNSON-NOISE-BOLTZMANN-2011",
            "route_identity": "Johnson-noise-thermometry",
            "chemical_composition_identity": "electronic-resistor-material-held-by-primary-route",
            "phase_identity": "condensed-material-route",
            "source_locator": "primary paper page 142; electronic Boltzmann-constant measurement",
            "snapshot_path": str(ELECTRONIC_PATH.relative_to(ROOT)),
            "snapshot_hash": EXPECTED[ELECTRONIC_PATH],
            "all_external_values_uncertainties_and_relation_flags_absent": True,
        },
    )
    write_json(IDENTITY_PATH, {
        "schema": "sft-v3-chemical-temperature-identities/1",
        "complete_target_count": len(identities),
        "complete_physically_distinct_route_count": 2,
        "all_values_uncertainties_intervals_and_relation_flags_absent": True,
        "rows": identities,
    })
    identity_hash = sha256_file(IDENTITY_PATH)

    # Only after the value-free registry exists is the prior post-seal source record opened.
    record = json.loads(PHYSICS_RECORD_PATH.read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-thermal-equilibrium-postseal-source-record/1":
        raise RuntimeError("thermometric equilibrium record schema changed")
    target = record.get("registered_target", {})
    required = {
        "exact_si_kb_scaled", "scale_denominator", "unit",
        "acoustic_kb_scaled_center", "acoustic_kb_scaled_standard_uncertainty",
        "acoustic_relative_standard_uncertainty_parts_per_million",
        "acoustic_temperature_measures_average_kinetic_energy",
        "electronic_kb_scaled_center", "electronic_kb_scaled_standard_uncertainty",
        "electronic_relative_combined_uncertainty_parts_per_million",
        "electronic_johnson_noise_power_depends_on_resistance_and_temperature",
        "electronic_johnson_relation_accuracy_parts_per_million",
        "measurement_routes_physically_distinct", "all_registered_rows_retained",
    }
    if not required.issubset(target):
        raise RuntimeError("complete thermometric equilibrium target vector changed")
    exact = int(target["exact_si_kb_scaled"])
    acoustic_center = int(target["acoustic_kb_scaled_center"])
    acoustic_uncertainty = int(target["acoustic_kb_scaled_standard_uncertainty"])
    electronic_center = int(target["electronic_kb_scaled_center"])
    electronic_uncertainty = int(target["electronic_kb_scaled_standard_uncertainty"])
    if min(exact, acoustic_center, acoustic_uncertainty, electronic_center, electronic_uncertainty, int(target["scale_denominator"])) <= 0:
        raise RuntimeError("thermometric record requires exact positive carriers")
    targets = (
        {
            "target_id": identities[0]["target_id"], "source_class": identities[0]["source_class"],
            "exact_si_common_carrier_scaled_numerator": exact,
            "common_scale_denominator": int(target["scale_denominator"]), "unit": target["unit"],
        },
        {
            "target_id": identities[1]["target_id"], "source_class": identities[1]["source_class"],
            "measured_center_scaled_numerator": acoustic_center,
            "measured_standard_uncertainty_scaled_numerator": acoustic_uncertainty,
            "measured_interval_lower_scaled_numerator": acoustic_center - acoustic_uncertainty,
            "measured_interval_upper_scaled_numerator": acoustic_center + acoustic_uncertainty,
            "common_scale_denominator": int(target["scale_denominator"]),
            "relative_standard_uncertainty_parts_per_million": int(target["acoustic_relative_standard_uncertainty_parts_per_million"]),
            "temperature_measures_average_kinetic_energy": target["acoustic_temperature_measures_average_kinetic_energy"],
            "chemical_composition_identity": "argon", "phase_identity": "gas",
            "equilibrium_reference_identity": "triple-point-of-water",
        },
        {
            "target_id": identities[2]["target_id"], "source_class": identities[2]["source_class"],
            "measured_center_scaled_numerator": electronic_center,
            "measured_standard_uncertainty_scaled_numerator": electronic_uncertainty,
            "measured_interval_lower_scaled_numerator": electronic_center - electronic_uncertainty,
            "measured_interval_upper_scaled_numerator": electronic_center + electronic_uncertainty,
            "common_scale_denominator": int(target["scale_denominator"]),
            "relative_combined_uncertainty_parts_per_million": int(target["electronic_relative_combined_uncertainty_parts_per_million"]),
            "noise_power_depends_on_resistance_and_temperature": target["electronic_johnson_noise_power_depends_on_resistance_and_temperature"],
            "reported_relation_accuracy_parts_per_million": int(target["electronic_johnson_relation_accuracy_parts_per_million"]),
        },
    )
    write_json(TARGET_PATH, {
        "schema": "sft-v3-chemical-temperature-withheld-targets/1",
        "release_requires_complete_identity_prediction_seal": True,
        "identity_registry_hash": identity_hash,
        "complete_target_count": len(targets),
        "measurement_routes_physically_distinct": target["measurement_routes_physically_distinct"],
        "all_registered_rows_retained": target["all_registered_rows_retained"],
        "rows": targets,
    })
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-chemical-temperature-primary-records/1",
        "source_record_path": str(PHYSICS_RECORD_PATH.relative_to(ROOT)),
        "source_record_hash": EXPECTED[PHYSICS_RECORD_PATH],
        "source_snapshot_hashes": {
            str(path.relative_to(ROOT)): expected for path, expected in EXPECTED.items() if path != PHYSICS_RECORD_PATH
        },
        "identity_registry_hash_before_target_open": identity_hash,
        "complete_target_count": len(targets),
        "complete_physically_distinct_route_count": 2,
        "acoustic_composition_and_equilibrium_locator": "argon at the triple point of water, primary paper pages 751-752",
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "identity_hash": identity_hash, "target_hash": sha256_file(TARGET_PATH),
        "primary_hash": sha256_file(PRIMARY_PATH), "targets": len(targets),
        "exact_common_carrier_scaled": exact,
        "acoustic_interval": [acoustic_center - acoustic_uncertainty, acoustic_center + acoustic_uncertainty],
        "electronic_interval": [electronic_center - electronic_uncertainty, electronic_center + electronic_uncertainty],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
