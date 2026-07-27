#!/usr/bin/env python3
"""Capture one complete official NIST paired fundamental-frequency surface for PROP-009."""

from __future__ import annotations

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1"
SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-paired-fundamental-frequency-surface.html"
PRIMARY_PATH = SNAPSHOT_DIR / "vibrational-frequency-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/vibrational_frequency_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/vibrational_frequency_withheld_targets_v1.json"
SOURCE_URL = "https://cccbdb.nist.gov/vibscale2x.asp?basis=27&method=16"


class TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.cell_span = 1
        self.cell_parts: list[str] = []
        self.current: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "td":
            self.in_cell = True
            self.cell_parts = []
            attributes = dict(attrs)
            declared = attributes.get("colspan", "1")
            self.cell_span = int(declared) if str(declared).isdigit() else 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == "td" and self.in_cell:
            self.current.append(" ".join("".join(self.cell_parts).split()))
            self.current.extend("" for _ in range(self.cell_span - 1))
            self.in_cell = False
            self.cell_span = 1
        elif lowered == "tr":
            if len(self.current) == 9:
                self.rows.append(tuple(self.current))
            self.current = []


def fetch() -> bytes:
    request = Request(SOURCE_URL, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-custodian/1"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def pair(inscription: str) -> dict[str, int]:
    value = Fraction(inscription)
    return {"numerator": value.numerator, "denominator": value.denominator}


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    source = fetch()
    SNAPSHOT_PATH.write_bytes(source)
    text = source.decode("utf-8", errors="replace")
    if (
        "Calculated vibrational frequencies" not in text
        or ">164<" not in text
        or ">2452<" not in text
        or "Frequency" not in text
        or "Experiment" not in text
    ):
        raise RuntimeError("NIST paired fundamental-frequency boundary changed")
    parser = TableRows()
    parser.feed(text)
    records = []
    current_formula = ""
    current_name = ""
    for cells in parser.rows:
        formula, name, mode, symmetry, theory, experiment, ratio, molecule_count, vibration_count = cells
        if formula:
            current_formula = formula
        if name:
            current_name = name
        if not (current_formula and current_name and mode and molecule_count and vibration_count):
            continue
        if not re.fullmatch(r"[0-9]+", mode):
            raise RuntimeError(f"non-exact mode count row: {cells}")
        if experiment and not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", experiment):
            raise RuntimeError(f"non-exact experimental frequency row: {cells}")
        if experiment and Fraction(experiment) <= 0:
            raise RuntimeError("fundamental-frequency surface contains a numerical-null or negative record")
        ordinal = len(records) + 1
        if int(vibration_count) != ordinal:
            raise RuntimeError("NIST vibration count is not complete and ordered")
        target_id = f"NIST-CCCBDB-PROP-009-MODE-{ordinal:04d}"
        records.append({
            "target_id": target_id,
            "source_id": "NIST-CCCBDB-COMPLETE-PAIRED-FUNDAMENTAL-FREQUENCY-SURFACE",
            "source_locator": f"vibscale2x basis=27 method=16, vibration count {vibration_count}",
            "formula": current_formula,
            "name": current_name,
            "mode_count": int(mode),
            "symmetry_label": symmetry if symmetry else "source-absent-symmetry-label",
            "symmetry_present": bool(symmetry),
            "molecule_count": int(molecule_count),
            "vibration_count": int(vibration_count),
            "measurement_kind": "experimental-fundamental-vibrational-wavenumber",
            "measurement_unit": "recurrence-count-per-centimeter",
            "measurement_present": bool(experiment),
            "frequency_inscription_cm_inverse": experiment if experiment else None,
            "exact_positive_recurrence_ratio_per_centimeter": pair(experiment) if experiment else None,
            "external_measurement_absence": None if experiment else "structural-EmptyOne",
            "source_row_uncertainty": None,
            "source_row_uncertainty_absent": True,
        })
    if len(records) != 2009 or len({row["target_id"] for row in records}) != 2009:
        raise RuntimeError(f"NIST complete displayed frequency count changed: {len(records)}")
    if len({row["molecule_count"] for row in records}) != 145 or records[-1]["molecule_count"] != 145:
        raise RuntimeError("NIST complete displayed molecule count changed")
    identities = []
    for row in records:
        identities.append({
            key: row[key]
            for key in (
                "target_id", "source_id", "source_locator", "formula", "name", "mode_count",
                "symmetry_label", "symmetry_present", "molecule_count", "vibration_count",
                "measurement_kind", "measurement_unit", "source_row_uncertainty_absent",
            )
        })
        identities[-1]["target_value_absent"] = True
    primary = {
        "schema": "sft-v3-nist-cccbdb-vibrational-frequency-primary-records/1",
        "source_url": SOURCE_URL,
        "source_advertised_molecule_count": 164,
        "source_advertised_vibration_count": 2452,
        "complete_displayed_molecule_count": 145,
        "complete_displayed_vibration_count": 2009,
        "source_advertised_but_undisplayed_molecule_count": 19,
        "source_advertised_but_undisplayed_vibration_count": 443,
        "all_rows_preserved": True,
        "selection_boundary": "all rows actually displayed on the official basis=27 method=16 NIST CCCBDB comparison surface, in source count order; the page-advertised 164/2452 counts and displayed 145/2009 counts are both preserved",
        "experimental_measurement_present_count": sum(row["measurement_present"] for row in records),
        "experimental_measurement_absent_count": sum(not row["measurement_present"] for row in records),
        "calculated_frequency_ratio_and_fitted_scale_columns_excluded_from_derivation_and_measurement_vector": True,
        "rows": records,
    }
    identity = {
        "schema": "sft-v3-vibrational-frequency-identities/1",
        "complete_displayed_molecule_count": 145,
        "complete_row_count": 2009,
        "all_frequency_values_absent": True,
        "selection_boundary": primary["selection_boundary"],
        "rows": identities,
    }
    targets = {
        "schema": "sft-v3-vibrational-frequency-withheld-measurements/1",
        "complete_displayed_molecule_count": 145,
        "complete_row_count": 2009,
        "source_advertised_molecule_count": 164,
        "source_advertised_vibration_count": 2452,
        "source_advertised_but_undisplayed_rows_preserved_as_source_boundary": True,
        "release_requires_prediction_seal": True,
        "all_rows_preserved": True,
        "all_values_are_exact_positive_recurrence_ratios_or_structural_absence": True,
        "rows": records,
    }
    PRIMARY_PATH.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    IDENTITY_PATH.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGET_PATH.write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_advertised_molecules": 164,
        "source_advertised_vibrations": 2452,
        "displayed_molecules": 145,
        "fundamental_frequency_rows": len(records),
        "measurement_present_rows": sum(row["measurement_present"] for row in records),
        "measurement_absent_rows": sum(not row["measurement_present"] for row in records),
        "symmetry_present_rows": sum(row["symmetry_present"] for row in records),
        "symmetry_absent_rows": sum(not row["symmetry_present"] for row in records),
        "minimum_inscription": min(Fraction(row["frequency_inscription_cm_inverse"]) for row in records if row["measurement_present"]).__str__(),
        "maximum_inscription": max(Fraction(row["frequency_inscription_cm_inverse"]) for row in records if row["measurement_present"]).__str__(),
        "snapshot_path": SNAPSHOT_PATH.relative_to(ROOT).as_posix(),
        "primary_path": PRIMARY_PATH.relative_to(ROOT).as_posix(),
        "identity_path": IDENTITY_PATH.relative_to(ROOT).as_posix(),
        "target_path": TARGET_PATH.relative_to(ROOT).as_posix(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PROP-009 source capture halted: {exc}", file=sys.stderr)
        raise
