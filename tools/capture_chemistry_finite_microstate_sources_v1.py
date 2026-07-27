#!/usr/bin/env python3
"""Capture complete finite calorimetric and molecular state-population records for THERMO-001."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-001-finite-microstate-v1"
WATER_PATH = SNAPSHOT_DIR / "nist-webbook-water-gas-calorimetric-table.html"
PRIMARY_PATH = SNAPSHOT_DIR / "finite-microstate-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/finite_microstate_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/finite_microstate_withheld_targets_v1.json"
POP_IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_measurement_target_identities_v1.json"
POP_TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_measurement_withheld_targets_v1.json"
WATER_URL = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=1&Table=on&Type=JANAFG&Units=SI"


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
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    request = Request(WATER_URL, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-custodian/1"})
    with urlopen(request, timeout=60) as response:
        water_source = response.read()
    text = water_source.decode("utf-8", errors="replace")
    if "Gas Phase Heat Capacity (Shomate Equation)" not in text or "Data from Shomate Coefficients" not in text:
        raise RuntimeError("NIST water calorimetric source boundary changed")
    WATER_PATH.write_bytes(water_source)
    parser = TableRows(); parser.feed(text)
    # NIST uses both ``500.`` and ``500.0`` inscriptions in this finite table.
    numeric = re.compile(r"[0-9]+(?:\.[0-9]*)?")
    calorimetric_rows = tuple(row for row in parser.rows if len(row) == 5 and all(numeric.fullmatch(cell) for cell in row))
    if len(calorimetric_rows) != 57:
        raise RuntimeError(f"expected complete 57-row NIST water table, found {len(calorimetric_rows)}")

    population_identities_document = json.loads(POP_IDENTITY_PATH.read_text(encoding="utf-8"))
    population_identities = tuple(population_identities_document.get("rows", ()))
    if population_identities_document.get("schema") != "sft-v3-molecular-measurement-identities/1" or len(population_identities) != 330:
        raise RuntimeError("complete CaH+ state-population identity boundary changed")

    identities: list[dict[str, object]] = []
    for ordinal, row in enumerate(population_identities, start=1):
        identities.append({
            "target_id": f"SFT-CHEM-THERMO-001-POPULATION-{ordinal:04d}",
            "source_class": "direct-molecular-state-population-and-transition-record",
            "source_id": "NIST-MDS2-3389-CAH-PLUS-QUANTUM-JUMP-THERMOMETRY",
            "source_target_id": row["target_id"], "source_file": row["file"],
            "source_row_ordinal": row["row_ordinal"], "column_identities": row["column_identities"],
            "snapshot_path": row["snapshot_path"], "snapshot_hash": row["snapshot_hash"],
            "target_value_and_population_absent": True,
        })
    water_hash = sha256_file(WATER_PATH)
    columns = (
        "temperature-kelvin", "heat-capacity-joule-per-mole-kelvin", "entropy-joule-per-mole-kelvin",
        "held-negative-gibbs-minus-reference-enthalpy-over-temperature-joule-per-mole-kelvin",
        "enthalpy-minus-reference-enthalpy-kilojoule-per-mole",
    )
    for ordinal in range(1, len(calorimetric_rows) + 1):
        identities.append({
            "target_id": f"SFT-CHEM-THERMO-001-CALORIMETRIC-{ordinal:04d}",
            "source_class": "evaluated-finite-calorimetric-state-row",
            "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-GAS-CALORIMETRIC-TABLE",
            "source_row_ordinal": ordinal, "species": "H2O", "phase": "gas",
            "column_identities": columns, "snapshot_path": str(WATER_PATH.relative_to(ROOT)),
            "snapshot_hash": water_hash, "source_locator": WATER_URL + f"#calorimetric-row-{ordinal}",
            "target_value_and_temperature_absent": True,
        })
    write_json(IDENTITY_PATH, {
        "schema": "sft-v3-finite-microstate-identities/1",
        "complete_state_population_row_count": 330,
        "complete_calorimetric_row_count": 57,
        "complete_target_count": len(identities),
        "all_populations_temperatures_and_calorimetric_values_absent": True,
        "rows": identities,
    })

    # Withheld target preparation occurs after the complete identity registry exists.
    population_targets_document = json.loads(POP_TARGET_PATH.read_text(encoding="utf-8"))
    population_targets = tuple(population_targets_document.get("rows", ()))
    if population_targets_document.get("schema") != "sft-v3-molecular-measurement-withheld-targets/1" or len(population_targets) != 330:
        raise RuntimeError("complete CaH+ state-population target boundary changed")
    population_by_id = {str(row["target_id"]): row for row in population_targets}
    targets: list[dict[str, object]] = []
    for identity in identities[:330]:
        original = population_by_id[str(identity["source_target_id"])]
        targets.append({
            "target_id": identity["target_id"], "source_class": identity["source_class"],
            "source_target_id": identity["source_target_id"], "cells": original["cells"],
        })
    for identity, values in zip(identities[330:], calorimetric_rows):
        targets.append({
            "target_id": identity["target_id"], "source_class": identity["source_class"],
            "temperature_inscription_kelvin": values[0], "heat_capacity_inscription": values[1],
            "entropy_inscription": values[2], "held_gibbs_reference_relation_inscription": values[3],
            "enthalpy_reference_relation_inscription": values[4],
        })
    write_json(TARGET_PATH, {
        "schema": "sft-v3-finite-microstate-withheld-targets/1",
        "release_requires_complete_identity_prediction_seal": True,
        "identity_registry_hash": sha256_file(IDENTITY_PATH),
        "complete_target_count": len(targets), "rows": targets,
    })
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-finite-microstate-primary-records/1",
        "state_population_source": {
            "source_id": "NIST-MDS2-3389-CAH-PLUS-QUANTUM-JUMP-THERMOMETRY",
            "identity_path": str(POP_IDENTITY_PATH.relative_to(ROOT)), "identity_hash": sha256_file(POP_IDENTITY_PATH),
            "target_path": str(POP_TARGET_PATH.relative_to(ROOT)), "target_hash": sha256_file(POP_TARGET_PATH),
            "complete_row_count": 330,
        },
        "calorimetric_source": {
            "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-GAS-CALORIMETRIC-TABLE",
            "source_url": WATER_URL, "snapshot_path": str(WATER_PATH.relative_to(ROOT)),
            "snapshot_hash": water_hash, "complete_row_count": 57,
            "source_classification": "evaluated finite table generated from NIST-JANAF Shomate representation; coefficients are external custody only and never proof parameters",
        },
        "complete_target_count": len(targets),
        "finite_rows_only": True,
        "completed_infinity_or_continuum_ensemble_used": False,
    })
    print(json.dumps({
        "water_hash": water_hash, "primary_hash": sha256_file(PRIMARY_PATH),
        "identity_hash": sha256_file(IDENTITY_PATH), "target_hash": sha256_file(TARGET_PATH),
        "population_rows": 330, "calorimetric_rows": 57, "targets": len(targets),
    }, indent=2, sort_keys=True))


if __name__ == "__main__": main()
