#!/usr/bin/env python3
"""Capture the complete nine-species PROP-007 molecular-ionization vector."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1"
GUIDE_PATH = SNAPSHOT_DIR / "nist-webbook-gas-phase-ion-thermochemistry.html"
PRIMARY_PATH = SNAPSHOT_DIR / "molecular-ionization-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_ionization_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_ionization_withheld_targets_v1.json"
GUIDE_URL = "https://webbook.nist.gov/chemistry/ion/"


SPECIES = (
    ("D2", "Deuterium diatomic", "7782390", "1-Sigma-g", "D-infinity-h"),
    ("HD", "Deuterium hydride", "13983205", "1-Sigma-g", "D-infinity-h"),
    ("H2", "Hydrogen diatomic", "1333740", "1-Sigma-g", "D-infinity-h"),
    ("N2", "Nitrogen diatomic", "7727379", "1-Sigma-g", "D-infinity-h"),
    ("CO", "Carbon monoxide", "630080", "1-Sigma", "C-infinity-v"),
    ("NO", "Nitric oxide", "10102439", "2-Pi", "C-infinity-v"),
    ("O2", "Oxygen diatomic", "7782447", "3-Sigma-g", "D-infinity-h"),
    ("HF", "Hydrogen fluoride", "7664393", "1-Sigma", "C-infinity-v"),
    ("F2", "Fluorine diatomic", "7782414", "1-Sigma-g", "D-infinity-h"),
)


def digest(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_or_preserve(path: Path, url: str) -> bytes:
    if path.exists():
        return path.read_bytes()
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=90) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"empty source response: {url}")
    path.write_bytes(data)
    return data


def pair(value: Fraction) -> dict[str, int]:
    if value.numerator < 1 or value.denominator < 1:
        raise ValueError("ionization measurement left the exact positive domain")
    return {"numerator": value.numerator, "denominator": value.denominator}


def display_interval(value: Fraction, inscription: str) -> tuple[Fraction, Fraction]:
    places = len(inscription.partition(".")[2])
    half_unit = Fraction(1, 2 * (10 ** places))
    return value - half_unit, value + half_unit


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    guide = fetch_or_preserve(GUIDE_PATH, GUIDE_URL)
    guide_text = unescape(guide.decode("utf-8", errors="replace"))
    normalized_guide_text = " ".join(guide_text.split())
    required_fragments = (
        "is the lowest energy required",
        "Vertical Ionization Energy",
        "must always be greater than or equal to the adiabatic ionization energy",
    )
    if any(fragment.casefold() not in normalized_guide_text.casefold() for fragment in required_fragments):
        raise RuntimeError("NIST ionization definition and ordering surface changed")

    records = []
    source_manifest = []
    pattern = re.compile(
        r"Experimental Ionization Energy is\s*([0-9]+(?:\.[0-9]+)?)"
        r"(?:\s*[±]\s*([0-9]+(?:\.[0-9]+)?))?\s*eV",
        re.IGNORECASE,
    )
    for ordinal, (formula, name, casno, state, conformation) in enumerate(SPECIES, start=1):
        url = f"https://cccbdb.nist.gov/ie2x.asp?casno={casno}"
        path = SNAPSHOT_DIR / f"{ordinal:02d}-{formula.casefold()}-{casno}.html"
        data = fetch_or_preserve(path, url)
        source_text = unescape(data.decode("utf-8", errors="replace"))
        match = pattern.search(source_text)
        if match is None:
            raise RuntimeError(f"NIST experimental ionization record absent: {formula}")
        inscription, uncertainty_inscription = match.groups()
        value = Fraction(inscription)
        if uncertainty_inscription is None:
            lower, upper = display_interval(value, inscription)
            uncertainty_kind = "source-displays-no-explicit-uncertainty; exact display-rounding-enclosure-only"
            uncertainty = None
        else:
            uncertainty = Fraction(uncertainty_inscription)
            if value <= uncertainty:
                raise RuntimeError("ionization uncertainty leaves positive support")
            lower, upper = value - uncertainty, value + uncertainty
            uncertainty_kind = "source-explicit-symmetric-uncertainty"
        snapshot_hash = digest(data)
        source_manifest.append({
            "formula": formula,
            "url": url,
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_hash": snapshot_hash,
        })
        record = {
            "target_id": f"NIST-CCCBDB-PROP-007-{formula}-ADIABATIC-IE",
            "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-IONIZATION-ENERGY",
            "source_locator": f"Calculated Ionization Energy for {formula}; displayed Experimental Ionization Energy line",
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_hash": snapshot_hash,
            "source_row_ordinal": ordinal,
            "formula": formula,
            "name": name,
            "casno": casno,
            "initial_molecular_state": state,
            "initial_conformation": conformation,
            "resulting_ionic_state": formula + "-positive-ion-least-generated-state",
            "removed_carrier": "one-held-electron-distinction",
            "ionization_path": "adiabatic-least-terminal-positive-Take",
            "method": "NIST-evaluated-experimental-ionization-energy",
            "condition": "isolated-gas-phase-molecule-to-isolated-positive-ion-and-released-electron",
            "units": "electronvolt",
            "value": pair(value),
            "lower": pair(lower),
            "upper": pair(upper),
            "uncertainty": pair(uncertainty) if uncertainty is not None else None,
            "uncertainty_kind": uncertainty_kind,
            "inscription": inscription,
            "uncertainty_inscription": uncertainty_inscription,
        }
        records.append(record)

    primary = {
        "schema": "sft-v3-molecular-ionization-primary-records/1",
        "development_provenance": "observational derivation; question and source surface disclosed before value-free execution",
        "definition_source": {
            "source_id": "NIST-WEBBOOK-SRD69-GAS-PHASE-ION-THERMOCHEMISTRY",
            "url": GUIDE_URL,
            "snapshot_path": str(GUIDE_PATH.relative_to(ROOT)),
            "snapshot_hash": digest(guide),
            "required_fragments": required_fragments,
        },
        "selection_rule": "the complete first nine neutral diatomic carriers in the admitted PROP-006 source order, excluding the already ionic H2+ row without reading ionization values",
        "source_manifest": source_manifest,
        "records": records,
        "complete_registered_rows": len(records),
        "all_rows_preserved": True,
    }
    write_json(PRIMARY_PATH, primary)
    primary_hash = digest(PRIMARY_PATH.read_bytes())
    value_keys = {"value", "lower", "upper", "uncertainty", "inscription", "uncertainty_inscription"}
    identity_rows = []
    for record in records:
        identity = {key: value for key, value in record.items() if key not in value_keys}
        identity["target_value_absent"] = True
        identity_rows.append(identity)
    identities = {
        "schema": "sft-v3-molecular-ionization-identities/1",
        "source_primary_record_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "source_primary_record_hash": primary_hash,
        "definition_source_path": str(GUIDE_PATH.relative_to(ROOT)),
        "definition_source_hash": digest(guide),
        "selection_rule": primary["selection_rule"],
        "rows": identity_rows,
        "all_ionization_values_absent": True,
        "complete_row_count": len(identity_rows),
    }
    write_json(IDENTITY_PATH, identities)
    targets = {
        "schema": "sft-v3-molecular-ionization-withheld-measurements/1",
        "identity_document_hash": digest(json.dumps(identities, sort_keys=True, separators=(",", ":")).encode()),
        "identity_file_hash": digest(IDENTITY_PATH.read_bytes()),
        "release_requires_prediction_seal": True,
        "rows": records,
        "all_rows_preserved": True,
        "complete_row_count": len(records),
    }
    write_json(TARGET_PATH, targets)
    print("captured", len(records), "molecular ionization rows")
    print("guide", digest(guide))
    print("primary", primary_hash)
    print("identities", digest(IDENTITY_PATH.read_bytes()))
    print("withheld", digest(TARGET_PATH.read_bytes()))


if __name__ == "__main__":
    main()
