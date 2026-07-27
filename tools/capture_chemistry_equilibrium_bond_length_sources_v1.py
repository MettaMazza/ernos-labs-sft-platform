#!/usr/bin/env python3
"""Freeze the existing authoritative H2/D2 and CODATA source surfaces for PROP-001."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402
from sft.physics.measured_value import MeasuredQuantity, load_codata_interval  # noqa: E402
from sft.physics.measured_value import CODATA_SOURCE_HASH, CODATA_SOURCE_PATH  # type: ignore[attr-defined] # noqa: E402


MOLECULAR_RECORD_PATH = Path(
    "experiments/external_sources/physics/snapshots/molecular-spectroscopy-successor-source-record.json"
)
MOLECULAR_RECORD_HASH = "sha256:211fb30414204bcc61f9fb4a69a451db24cb5d5aaaacb2bb3b85fc83429388a9"
IDENTITY_PATH = Path(
    "experiments/external_sources/chemistry/equilibrium_bond_length_target_identities_v1.json"
)
SCALE_PATH = Path(
    "experiments/external_sources/chemistry/equilibrium_bond_length_scale_input_v1.json"
)
TARGET_PATH = Path(
    "experiments/external_sources/chemistry/equilibrium_bond_length_withheld_targets_v1.json"
)


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def main() -> None:
    molecular_path = ROOT / MOLECULAR_RECORD_PATH
    codata_path = ROOT / CODATA_SOURCE_PATH
    if hash_file(molecular_path) != MOLECULAR_RECORD_HASH:
        raise SystemExit("molecular spectroscopy authority changed")
    if hash_file(codata_path) != CODATA_SOURCE_HASH:
        raise SystemExit("CODATA authority changed")

    molecular = json.loads(molecular_path.read_text(encoding="utf-8"))
    atomic_length = load_codata_interval(
        codata_path,
        MeasuredQuantity("atomic_length", "atomic unit of length", "m"),
    )
    metre_to_angstrom = Fraction(10**10, 1)
    atomic_angstrom = {
        "quantity": "CODATA atomic unit of length",
        "unit": "angstrom",
        "central": fraction_record(atomic_length.central * metre_to_angstrom),
        "lower": fraction_record(atomic_length.lower * metre_to_angstrom),
        "upper": fraction_record(atomic_length.upper * metre_to_angstrom),
        "uncertainty_record": atomic_length.uncertainty_record,
        "source_path": CODATA_SOURCE_PATH,
        "source_hash": CODATA_SOURCE_HASH,
    }

    identities = []
    targets = []
    for isotope, species in (("hydrogen", "H2"), ("deuterium", "D2")):
        source = molecular["sources"][isotope]
        distance = source["rows"]["equilibrium_internuclear_distance_angstrom"]
        centre = Fraction(distance["inscription"])
        half_width = Fraction(distance["last_inscribed_digit_half_width"])
        target_id = f"NIST-{species}-X1SIGMA-G-EQUILIBRIUM-DISTANCE"
        identities.append(
            {
                "target_id": target_id,
                "species": species,
                "isotopologue": species,
                "electronic_state": "X 1Sigma_g+ 1s-sigma-squared ground state",
                "measurement_condition": "gas-phase constants of diatomic molecules",
                "source_id": source["source_id"],
                "source_uri": source["source_uri"],
                "source_locator": source["locator"] + " :: equilibrium internuclear distance",
                "snapshot_path": source["snapshot_path"],
                "snapshot_hash": source["snapshot_hash"],
                "target_value_absent": True,
            }
        )
        targets.append(
            {
                "target_id": target_id,
                "species": species,
                "inscription": distance["inscription"],
                "last_inscribed_digit_half_width": distance["last_inscribed_digit_half_width"],
                "unit": "angstrom",
                "central": fraction_record(centre),
                "lower": fraction_record(centre - half_width),
                "upper": fraction_record(centre + half_width),
                "source_snapshot_hash": source["snapshot_hash"],
            }
        )

    identity_document = {
        "schema": "sft-v3-equilibrium-bond-length-identities/1",
        "provenance": "observational_derivation",
        "development_targets_already_known": True,
        "not_claimed_as_unknown_target_forward_prediction": True,
        "molecular_authority": {
            "path": str(MOLECULAR_RECORD_PATH),
            "hash": MOLECULAR_RECORD_HASH,
        },
        "atomic_length_authority": {
            "path": CODATA_SOURCE_PATH,
            "hash": CODATA_SOURCE_HASH,
        },
        "registered_scale_input": {
            "path": str(SCALE_PATH),
            "hash": sha256_identity(atomic_angstrom),
        },
        "rows": identities,
    }
    scale_document = {
        "schema": "sft-v3-equilibrium-bond-length-scale-input/1",
        "target_values_absent": True,
        "registered_scale_input": atomic_angstrom,
    }
    target_document = {
        "schema": "sft-v3-equilibrium-bond-length-withheld-targets/1",
        "identity_document_hash": sha256_identity(identity_document),
        "scale_input_values_absent": True,
        "rows": targets,
    }

    for relative, document in (
        (IDENTITY_PATH, identity_document),
        (SCALE_PATH, scale_document),
        (TARGET_PATH, target_document),
    ):
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(relative, hash_file(path))


if __name__ == "__main__":
    main()
