#!/usr/bin/env python3
"""Freeze the complete post-seal measurement vector for Chemistry PROP-002.

This transparent transcription tool creates source extracts, a value-free
identity registry, and one separately hashed eight-row measurement vault.  No
measured number is a derivation or prediction input.
"""

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


APS_PATH = Path("experiments/external_sources/chemistry/snapshots/aps-hydrogen-dissociation-1994.json")
APS_HASH = "sha256:9c41d01395090b18b2eb8b1223e9cb430d9309f79d1a0324b092a5ed8c1b6953"
ATOMIC_PATH = Path("experiments/external_sources/chemistry/snapshots/prop-002-atomic-1s-2s-primary-records-v1.json")
CURRENT_PATH = Path("experiments/external_sources/chemistry/snapshots/prop-002-current-dissociation-primary-records-v1.json")
IDENTITY_PATH = Path("experiments/external_sources/chemistry/bond_dissociation_energy_target_identities_v1.json")
TARGET_PATH = Path("experiments/external_sources/chemistry/bond_dissociation_energy_withheld_targets_v1.json")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def interval_record(central: Fraction, uncertainty: Fraction) -> dict[str, object]:
    if not central > uncertainty or uncertainty.numerator < 1 or uncertainty.denominator < 1:
        raise ValueError("PROP-002 source interval must be exact and strictly positive")
    return {
        "central": fraction_record(central),
        "uncertainty": fraction_record(uncertainty),
        "lower": fraction_record(central - uncertainty),
        "upper": fraction_record(central + uncertainty),
    }


def atomic_primary_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-primary-source-numeric-extract/1",
        "retrieved": "2026-07-26",
        "sources": [
            {
                "source_id": "PRL-UDEM-H-1S2S-1997",
                "body": "American Physical Society",
                "title": "Precision Measurement of the Hydrogen 1S-2S Transition Frequency",
                "doi": "10.1103/PhysRevLett.79.2646",
                "source_uri": "https://doi.org/10.1103/PhysRevLett.79.2646",
                "quantity": "hydrogen-1S1/2-to-2S1/2-transition-frequency",
                "value_inscription_kHz": "2466061413187.34",
                "standard_uncertainty_inscription_kHz": "0.84",
                "value_hz": fraction_record(Fraction(246606141318734, 100) * 1000),
                "standard_uncertainty_hz": fraction_record(Fraction(84, 100) * 1000),
            },
            {
                "source_id": "PRL-PARTHEY-HD-1S2S-SHIFT-2010",
                "body": "American Physical Society",
                "title": "Precision Measurement of the Hydrogen-Deuterium 1S-2S Isotope Shift",
                "doi": "10.1103/PhysRevLett.104.233001",
                "source_uri": "https://doi.org/10.1103/PhysRevLett.104.233001",
                "quantity": "deuterium-minus-hydrogen-1S2S-isotope-shift",
                "value_inscription_Hz": "670994334606",
                "standard_uncertainty_inscription_Hz": "15",
                "value_hz": fraction_record(Fraction(670994334606, 1)),
                "standard_uncertainty_hz": fraction_record(Fraction(15, 1)),
            },
            {
                "source_id": "SI-DEFINING-LIGHT-SPEED",
                "body": "Bureau International des Poids et Mesures",
                "title": "SI defining value of the speed of light in vacuum",
                "source_uri": "https://www.bipm.org/en/si-base-units/metre",
                "quantity": "speed-of-light-in-vacuum",
                "value_inscription_m_per_s": "299792458",
                "exact_definition": True,
            },
        ],
        "transcription_boundary": (
            "Primary atomic inscriptions and reported uncertainties only. Molecular dissociation values are absent."
        ),
    }


def current_primary_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-primary-source-numeric-extract/1",
        "retrieved": "2026-07-26",
        "sources": [
            {
                "source_id": "JCP-LIU-H2-DISSOCIATION-2009",
                "body": "American Institute of Physics",
                "title": "Determination of the ionization and dissociation energies of the hydrogen molecule",
                "doi": "10.1063/1.3120443",
                "source_uri": "https://doi.org/10.1063/1.3120443",
                "species": "H2",
                "electronic_state": "X 1Sigma_g+",
                "rotational_state": "N=0 para-H2",
                "product_channel": "H(1s)+H(1s)",
                "value_inscription_cm_inverse": "36118.06962",
                "standard_uncertainty_inscription_cm_inverse": "0.00037",
            },
            {
                "source_id": "PRA-HUSSELS-D2-DISSOCIATION-2022",
                "body": "American Physical Society",
                "title": "Improved ionization and dissociation energies of the deuterium molecule",
                "doi": "10.1103/PhysRevA.105.022820",
                "source_uri": "https://doi.org/10.1103/PhysRevA.105.022820",
                "species": "D2",
                "electronic_state": "X 1Sigma_g+",
                "rotational_state": "N=0 retained ground rotational state",
                "product_channel": "D(1s)+D(1s)",
                "value_inscription_cm_inverse": "36748.362282",
                "standard_uncertainty_inscription_cm_inverse": "0.000026",
            },
        ],
        "transcription_boundary": "Later high-resolution ground-state dissociation target rows only.",
    }


def main() -> None:
    if hash_file(ROOT / APS_PATH) != APS_HASH:
        raise SystemExit("PROP-002 APS authority changed")
    aps = json.loads((ROOT / APS_PATH).read_text(encoding="utf-8"))
    atomic = atomic_primary_record()
    current = current_primary_record()
    write_json(ROOT / ATOMIC_PATH, atomic)
    write_json(ROOT / CURRENT_PATH, current)
    atomic_hash = hash_file(ROOT / ATOMIC_PATH)
    current_hash = hash_file(ROOT / CURRENT_PATH)

    aps_rows = {(row["species"], row["kind"]): row for row in aps["records"]}
    atomic_sources = {row["source_id"]: row for row in atomic["sources"]}
    current_rows = {row["species"]: row for row in current["sources"]}
    c_cm_per_second = Fraction(29979245800, 1)
    h_record = atomic_sources["PRL-UDEM-H-1S2S-1997"]
    isotope_record = atomic_sources["PRL-PARTHEY-HD-1S2S-SHIFT-2010"]
    h_frequency = Fraction(h_record["value_hz"]["numerator"], h_record["value_hz"]["denominator"])
    h_uncertainty = Fraction(h_record["standard_uncertainty_hz"]["numerator"], h_record["standard_uncertainty_hz"]["denominator"])
    isotope_shift = Fraction(isotope_record["value_hz"]["numerator"], isotope_record["value_hz"]["denominator"])
    isotope_uncertainty = Fraction(isotope_record["standard_uncertainty_hz"]["numerator"], isotope_record["standard_uncertainty_hz"]["denominator"])
    atomic_rows = {
        "H2": (h_frequency / c_cm_per_second, h_uncertainty / c_cm_per_second),
        "D2": ((h_frequency + isotope_shift) / c_cm_per_second, (h_uncertainty + isotope_uncertainty) / c_cm_per_second),
    }

    identities: list[dict[str, object]] = []
    measurements: list[dict[str, object]] = []
    for species, atom in (("H2", "H"), ("D2", "D")):
        threshold = aps_rows[(species, "measured_dissociation_threshold")]
        historical = aps_rows[(species, "measured_ground_state_dissociation_energy")]
        threshold_central = Fraction(threshold["value_numerator"], threshold["value_denominator"])
        threshold_uncertainty = Fraction(threshold["uncertainty_numerator"], threshold["uncertainty_denominator"])
        atomic_central, atomic_uncertainty = atomic_rows[species]
        current_row = current_rows[species]
        current_central = Fraction(current_row["value_inscription_cm_inverse"])
        current_uncertainty = Fraction(current_row["standard_uncertainty_inscription_cm_inverse"])
        historical_central = Fraction(historical["value_numerator"], historical["value_denominator"])
        historical_uncertainty = Fraction(historical["uncertainty_numerator"], historical["uncertainty_denominator"])

        rows = (
            (
                f"PATH-{species}-BPRIME-THRESHOLD",
                "path-threshold",
                "B-prime 1Sigma_u+",
                f"{atom}(1s)+{atom}(2s)",
                "APS-PRA-49-2460-1994",
                APS_PATH,
                APS_HASH,
                threshold["value_inscription"],
                threshold_central,
                threshold_uncertainty,
            ),
            (
                f"PATH-{atom}-ATOMIC-1S2S",
                "atomic-path-segment",
                f"{atom} atomic 1s-to-2s",
                f"{atom}(1s)->{atom}(2s)",
                "PRL-UDEM-H-1S2S-1997" if species == "H2" else "PRL-UDEM-H-1S2S-1997+PRL-PARTHEY-HD-1S2S-SHIFT-2010",
                ATOMIC_PATH,
                atomic_hash,
                "exact-frequency-interval-translated-by-SI-c",
                atomic_central,
                atomic_uncertainty,
            ),
            (
                f"APS-1994-{species}-X-GROUND-D0",
                "historical-ground-dissociation",
                "X 1Sigma_g+ ground electronic state",
                f"{atom}(1s)+{atom}(1s)",
                "APS-PRA-49-2460-1994",
                APS_PATH,
                APS_HASH,
                historical["value_inscription"],
                historical_central,
                historical_uncertainty,
            ),
            (
                f"CURRENT-{species}-X-GROUND-D0",
                "later-ground-dissociation",
                "X 1Sigma_g+ ground electronic state",
                f"{atom}(1s)+{atom}(1s)",
                current_row["source_id"],
                CURRENT_PATH,
                current_hash,
                current_row["value_inscription_cm_inverse"],
                current_central,
                current_uncertainty,
            ),
        )
        for target_id, role, state, channel, source_id, snapshot_path, snapshot_hash, inscription, central, uncertainty in rows:
            identities.append({
                "target_id": target_id,
                "species": species,
                "measurement_role": role,
                "state": state,
                "channel": channel,
                "source_id": source_id,
                "source_locator": "registered primary measurement row",
                "snapshot_path": str(snapshot_path),
                "snapshot_hash": snapshot_hash,
                "target_value_absent": True,
            })
            measurements.append({
                "target_id": target_id,
                "species": species,
                "measurement_role": role,
                "inscription": inscription,
                "unit": "inverse-centimetre",
                **interval_record(central, uncertainty),
                "source_snapshot_hash": snapshot_hash,
            })

    identity_document = {
        "schema": "sft-v3-bond-dissociation-energy-identities/1",
        "provenance": "observational_derivation",
        "development_measurements_already_known": True,
        "not_claimed_as_unknown-target-forward-prediction": True,
        "all_measurement_values_absent": True,
        "rows": identities,
    }
    target_document = {
        "schema": "sft-v3-bond-dissociation-energy-withheld-measurements/1",
        "identity_document_hash": sha256_identity(identity_document),
        "release_requires_prediction_seal": True,
        "rows": measurements,
    }
    write_json(ROOT / IDENTITY_PATH, identity_document)
    write_json(ROOT / TARGET_PATH, target_document)
    for path in (ATOMIC_PATH, CURRENT_PATH, IDENTITY_PATH, TARGET_PATH):
        print(path, hash_file(ROOT / path))


if __name__ == "__main__":
    main()
