#!/usr/bin/env python3
"""Extract the complete NIST spectroscopic support-assignment census for ELEC-003.

Target identities are written separately from withheld state and configuration
content.  The source consists only of the already byte-sealed NIST diatomic
snapshots registered for ELEC-002; no new data source or model is introduced.
"""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/orbital_support_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/orbital_support_withheld_targets_v1.json"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025"


class DataTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.table_depth += 1
        elif self.table_depth and tag == "tr":
            self.in_row = True
            self.row = []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell = True
            self.cell = []
        elif self.in_cell and tag == "sup":
            self.cell.append("^")
        elif self.in_cell and tag == "sub":
            self.cell.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = False
        elif self.table_depth and tag == "table":
            self.table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell.append(data)


TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
ORBITAL_PATTERN = re.compile(r"(?<![A-Za-z0-9])([1-9][0-9]*)([spdfgh])\s*([σπδφ])(?:\^([1-9][0-9]*))?")
SUPPORT_RANK = {"Σ": "structural-empty-One", "Π": "first-recurrence", "Δ": "second-recurrence", "Φ": "third-recurrence"}
ORBITAL_RANK = {"σ": "structural-empty-One", "π": "first-recurrence", "δ": "second-recurrence", "φ": "third-recurrence"}


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> None:
    input_document = json.loads(INPUTS.read_text(encoding="utf-8"))
    identity_rows = []
    target_rows = []
    for species in input_document["rows"]:
        snapshot = ROOT / species["snapshot_path"]
        if file_hash(snapshot) != species["snapshot_hash"]:
            raise RuntimeError(f"{species['row_id']}: NIST source identity changed")
        parser = DataTableParser()
        parser.feed(snapshot.read_text(encoding="utf-8"))
        state_rows = tuple(
            row
            for row in parser.rows
            if len(row) == 13 and TERM_PATTERN.search(row[0]) is not None
        )
        if not state_rows:
            raise RuntimeError(f"{species['row_id']}: no NIST spectroscopic state rows")
        for ordinal, cells in enumerate(state_rows, start=1):
            target_id = f"{species['nist_id']}-state-{ordinal:03d}"
            terms = tuple(
                {
                    "measured_multiplicity": int(match.group(1)),
                    "conventional_support_symbol": match.group(2),
                    "fold_axis_support_rank": SUPPORT_RANK[match.group(2)],
                }
                for match in TERM_PATTERN.finditer(cells[0])
            )
            configurations = tuple(
                {
                    "positive_radial_recurrence": int(match.group(1)),
                    "source_family_label": match.group(2),
                    "conventional_support_symbol": match.group(3),
                    "fold_axis_support_rank": ORBITAL_RANK[match.group(3)],
                    "occupancy_record": int(match.group(4)) if match.group(4) else "implicit-single-occurrence",
                }
                for match in ORBITAL_PATTERN.finditer(cells[0])
            )
            identity_rows.append(
                {
                    "target_id": target_id,
                    "species_row_id": species["row_id"],
                    "nist_id": species["nist_id"],
                    "state_row_ordinal": ordinal,
                    "source_url": species["source_url"],
                    "snapshot_path": species["snapshot_path"],
                    "snapshot_hash": species["snapshot_hash"],
                }
            )
            target_rows.append(
                {
                    "target_id": target_id,
                    "species_row_id": species["row_id"],
                    "nist_id": species["nist_id"],
                    "state_row_ordinal": ordinal,
                    "state_record": cells[0],
                    "term_assignments": terms,
                    "configuration_assignments": configurations,
                    "spectroscopic_cells": cells,
                    "snapshot_path": species["snapshot_path"],
                    "snapshot_hash": species["snapshot_hash"],
                }
            )
    if len(identity_rows) != 360 or len(target_rows) != 360:
        raise RuntimeError("complete registered NIST state census must contain 360 rows")
    if len({row["target_id"] for row in identity_rows}) != 360:
        raise RuntimeError("NIST state target identities are duplicated")
    source = {
        "source_id": SOURCE_ID,
        "body": "National Institute of Standards and Technology",
        "database": "NIST Chemistry WebBook, Standard Reference Database 69",
        "doi": "10.18434/T4D303",
        "last_data_update": "March 2025",
        "retrieval_date": "2026-07-26",
        "species_count": 22,
    }
    IDENTITIES.write_text(
        json.dumps({"schema": "sft-v3-orbital-support-target-identities/1", "source": source, "rows": identity_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    TARGETS.write_text(
        json.dumps({"schema": "sft-v3-orbital-support-withheld-targets/1", "source": source, "rows": target_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    configuration_count = sum(len(row["configuration_assignments"]) for row in target_rows)
    term_count = sum(len(row["term_assignments"]) for row in target_rows)
    print(f"target rows: {len(target_rows)}")
    print(f"term assignments: {term_count}")
    print(f"configuration assignments: {configuration_count}")
    print(f"identity registry: {file_hash(IDENTITIES)}")
    print(f"withheld target registry: {file_hash(TARGETS)}")


if __name__ == "__main__":
    main()
