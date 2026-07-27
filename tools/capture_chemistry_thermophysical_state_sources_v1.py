#!/usr/bin/env python3
"""Freeze the shared NIST water thermophysical state vector for Chemistry THERMO laws."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-shared-water-isobar-v1"
SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-webbook-water-isobar-1bar-300-400K.html"
PRIMARY_PATH = SNAPSHOT_DIR / "thermophysical-state-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/thermophysical_state_withheld_targets_v1.json"
QUERY = {
    "Action": "Load", "ID": "C7732185", "Type": "IsoBar", "P": "1",
    "TLow": "300", "THigh": "400", "TInc": "10", "Digits": "8",
    "TUnit": "K", "PUnit": "bar", "DUnit": "mol/l", "HUnit": "kJ/mol",
    "WUnit": "m/s", "VisUnit": "uPa*s", "STUnit": "N/m", "RefState": "DEF",
}
SOURCE_URL = "https://webbook.nist.gov/cgi/fluid.cgi?" + urlencode(QUERY)
COLUMNS = (
    "temperature-kelvin", "pressure-bar", "density-mole-per-litre", "volume-litre-per-mole",
    "internal-energy-kilojoule-per-mole", "enthalpy-kilojoule-per-mole",
    "entropy-joule-per-mole-kelvin", "isochoric-heat-capacity-joule-per-mole-kelvin",
    "isobaric-heat-capacity-joule-per-mole-kelvin", "sound-speed-metre-per-second",
    "joule-thomson-kelvin-per-bar", "viscosity-micropascal-second",
    "thermal-conductivity-watt-per-metre-kelvin", "phase-identity",
)


class TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.parts: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"td", "th"}:
            self.in_cell = True
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.in_cell:
            self.row.append(" ".join("".join(self.parts).split()))
            self.in_cell = False
        elif tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.row = []


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    # The complete query boundary and row identities are committed before any response values are fetched.
    identities = tuple({
        "target_id": f"SFT-CHEM-THERMO-SHARED-WATER-ISOBAR-{ordinal:04d}",
        "source_class": "NIST-WebBook-finite-isobaric-thermophysical-state-row",
        "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-FLUID-PROPERTIES",
        "source_row_ordinal": ordinal,
        "chemical_composition_identity": "H2O",
        "query_identity": "one-bar; 300-to-400-kelvin; ten-kelvin-requested-increment; returned-phase-boundary-rows-retained",
        "column_identities": COLUMNS,
        "source_url": SOURCE_URL,
        "all_returned_temperatures_phases_and_property_values_absent": True,
    } for ordinal in range(1, 14))
    write_json(IDENTITY_PATH, {
        "schema": "sft-v3-thermophysical-state-identities/1",
        "complete_query_identity_count": 13,
        "all_returned_temperatures_phases_and_property_values_absent": True,
        "rows": identities,
    })
    identity_hash = sha256_file(IDENTITY_PATH)

    request = Request(SOURCE_URL, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-custodian/1"})
    with urlopen(request, timeout=60) as response:
        source = response.read()
    text = source.decode("utf-8", errors="replace")
    if "Isobaric Properties for Water" not in text or "Internal Energy" not in text:
        raise RuntimeError("NIST internal-energy table boundary changed")
    parser = TableRows()
    parser.feed(text)
    data_rows = tuple(
        row for row in parser.rows
        if len(row) == 14 and row[0] != "Temperature (K)" and row[-1] in {"liquid", "vapor", "supercritical"}
    )
    if len(data_rows) != 13:
        raise RuntimeError(f"expected complete 13-row NIST isobaric surface, found {len(data_rows)}")
    if sum(row[0] == "372.75593" for row in data_rows) != 2 or {row[-1] for row in data_rows if row[0] == "372.75593"} != {"liquid", "vapor"}:
        raise RuntimeError("NIST one-bar phase-boundary pair changed")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_bytes(source)
    snapshot_hash = sha256_file(SNAPSHOT_PATH)

    targets = tuple({
        "target_id": identity["target_id"],
        "source_class": identity["source_class"],
        "source_row_ordinal": identity["source_row_ordinal"],
        "snapshot_hash": snapshot_hash,
        **{column: value for column, value in zip(COLUMNS, row)},
    } for identity, row in zip(identities, data_rows))
    write_json(TARGET_PATH, {
        "schema": "sft-v3-thermophysical-state-withheld-targets/1",
        "release_requires_complete_identity_prediction_seal": True,
        "identity_registry_hash": identity_hash,
        "complete_target_count": len(targets),
        "rows": targets,
    })
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-thermophysical-state-primary-records/1",
        "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-FLUID-PROPERTIES",
        "source_url": SOURCE_URL,
        "query": QUERY,
        "snapshot_path": str(SNAPSHOT_PATH.relative_to(ROOT)),
        "snapshot_hash": snapshot_hash,
        "identity_registry_hash_before_source_response_open": identity_hash,
        "complete_returned_row_count": len(targets),
        "liquid_row_count": sum(row[-1] == "liquid" for row in data_rows),
        "vapor_row_count": sum(row[-1] == "vapor" for row in data_rows),
        "phase_boundary_temperature_inscription": "372.75593",
        "phase_boundary_row_count": 2,
        "all_fourteen_returned_columns_preserved": True,
        "external_signed_glyphs_are_source_inscriptions_not_SFT_proof_values": True,
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "identity_hash": identity_hash, "snapshot_hash": snapshot_hash,
        "target_hash": sha256_file(TARGET_PATH), "primary_hash": sha256_file(PRIMARY_PATH),
        "rows": len(targets), "liquid": sum(row[-1] == "liquid" for row in data_rows),
        "vapor": sum(row[-1] == "vapor" for row in data_rows),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
