#!/usr/bin/env python3
"""Capture the complete orderable NIST molecular-state energy vector."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/state_energy_order_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/state_energy_order_withheld_targets_v1.json"
TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
VALUE_PATTERN = re.compile(r"^[\[\(]?\s*~?\s*([0-9]+(?:\.[0-9_]*)?)")


class EnergyTableParser(HTMLParser):
    """Parse data cells while excluding linked NIST note numbers."""

    def __init__(self) -> None:
        super().__init__()
        self.depth = self.in_row = self.in_cell = self.in_note_anchor = 0
        self.cell: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.depth += 1
        elif self.depth and tag == "tr":
            self.in_row, self.row = 1, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell = 1, []
        elif self.in_cell and tag == "a" and (attributes.get("href") or "").startswith("#Dia"):
            self.in_note_anchor += 1
        elif self.in_cell and not self.in_note_anchor and tag == "sup":
            self.cell.append("^")
        elif self.in_cell and not self.in_note_anchor and tag == "sub":
            self.cell.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.in_note_anchor:
            self.in_note_anchor -= 1
        elif self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = 0
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = 0
        elif self.depth and tag == "table":
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell and not self.in_note_anchor:
            self.cell.append(data)


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def quality(energy: str) -> str:
    if energy.lstrip().startswith("["):
        return "bracketed-source-estimate"
    if energy.lstrip().startswith("("):
        return "parenthesized-source-estimate"
    if energy.lstrip().startswith("~"):
        return "approximate-source-inscription"
    return "source-tabulated-value"


def main() -> None:
    inputs = json.loads(INPUTS.read_text(encoding="utf-8"))["rows"]
    identities = []
    targets = []
    for species in inputs:
        snapshot = ROOT / species["snapshot_path"]
        if file_hash(snapshot) != species["snapshot_hash"]:
            raise RuntimeError("NIST energy source identity changed")
        parser = EnergyTableParser()
        parser.feed(snapshot.read_text(encoding="utf-8"))
        state_rows = tuple(row for row in parser.rows if len(row) == 13 and TERM_PATTERN.search(row[0]))
        orderable = []
        for state_ordinal, row in enumerate(state_rows, start=1):
            if "eV" in row[1]:
                continue
            match = VALUE_PATTERN.search(row[1])
            if match is None:
                continue
            exact = Fraction(match.group(1).replace("_", ""))
            orderable.append((state_ordinal, row, exact))
        ground_rows = tuple(item for item in orderable if item[1][0].startswith("X"))
        if len(ground_rows) != 1:
            raise RuntimeError(f"{species['row_id']}: NIST X-state energy is not unique")
        ground_value = ground_rows[0][2]
        if any(value < ground_value for _, _, value in orderable):
            raise RuntimeError(f"{species['row_id']}: an orderable state lies below the NIST X state")
        if sum(value == ground_value for _, _, value in orderable) != 1:
            raise RuntimeError(f"{species['row_id']}: least measured state is not unique")
        for orderable_ordinal, (state_ordinal, row, exact) in enumerate(orderable, start=1):
            target_id = f"{species['nist_id']}-energy-{orderable_ordinal:03d}"
            identities.append(
                {
                    "target_id": target_id,
                    "species_row_id": species["row_id"],
                    "nist_id": species["nist_id"],
                    "state_row_ordinal": state_ordinal,
                    "orderable_row_ordinal": orderable_ordinal,
                    "snapshot_path": species["snapshot_path"],
                    "snapshot_hash": species["snapshot_hash"],
                    "source_url": species["source_url"],
                }
            )
            targets.append(
                {
                    "target_id": target_id,
                    "species_row_id": species["row_id"],
                    "state_record": row[0],
                    "energy_inscription": row[1],
                    "exact_value_numerator": exact.numerator,
                    "exact_value_denominator": exact.denominator,
                    "unit": "inverse-centimetre",
                    "source_quality": quality(row[1]),
                    "is_source_designated_ground_state": row[0].startswith("X"),
                    "exact_gap_from_species_ground_numerator": (exact - ground_value).numerator,
                    "exact_gap_from_species_ground_denominator": (exact - ground_value).denominator,
                    "snapshot_path": species["snapshot_path"],
                    "snapshot_hash": species["snapshot_hash"],
                }
            )
    if len(targets) != 306 or len({row["target_id"] for row in targets}) != 306:
        raise RuntimeError("complete orderable NIST energy census must contain 306 unique rows")
    if sum(row["is_source_designated_ground_state"] for row in targets) != 22:
        raise RuntimeError("energy census must retain one ground state per species")
    source = {"source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025", "body": "National Institute of Standards and Technology", "database": "NIST Chemistry WebBook SRD 69", "doi": "10.18434/T4D303", "retrieval_date": "2026-07-26", "species_count": 22}
    IDENTITIES.write_text(json.dumps({"schema": "sft-v3-state-energy-order-identities/1", "source": source, "rows": identities}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGETS.write_text(json.dumps({"schema": "sft-v3-state-energy-order-withheld-targets/1", "source": source, "rows": targets}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"orderable energy rows: {len(targets)}")
    print(f"ground rows: {sum(row['is_source_designated_ground_state'] for row in targets)}")
    print(f"excited rows: {sum(not row['is_source_designated_ground_state'] for row in targets)}")
    print(f"identity registry: {file_hash(IDENTITIES)}")
    print(f"withheld target registry: {file_hash(TARGETS)}")


if __name__ == "__main__":
    main()
