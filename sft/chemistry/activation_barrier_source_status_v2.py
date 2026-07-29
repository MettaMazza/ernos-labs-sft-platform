"""Versioned KIN-004 source-status reconstruction.

This module does not alter the admitted v1 claim, its validator, its receipt, or
the protected admission engine.  It independently classifies the one preserved
blank phenol table row so that a source placeholder cannot be reported as a
failed chemical measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PHENOL_SNAPSHOT = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/kin-004-activation-barrier-v1"
    / "detail-0025-cas-108952.html"
)


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._depth = 0
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.tables: list[list[list[str]]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._table = []
        elif tag == "tr" and self._depth == 1:
            self._row = []
        elif tag in {"th", "td"} and self._depth == 1:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self._depth == 1 and self._cell is not None and self._row is not None:
            self._row.append(" ".join(" ".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._depth == 1 and self._row is not None and self._table is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table":
            if self._depth == 1 and self._table is not None:
                self.tables.append(self._table)
                self._table = None
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        value = unescape(data)
        if value.strip():
            self.text.append(value)
            if self._cell is not None:
                self._cell.append(value)


@dataclass(frozen=True)
class PhenolSourceStatus:
    measured_torsion_indices: tuple[str, ...]
    structural_placeholder_indices: tuple[str, ...]
    measured_state_count: int
    preserved_placeholder_row_count: int
    greatest_wavenumber: Fraction
    greatest_energy_kj_mol: Fraction
    reference_wavenumber: Fraction
    reference_uncertainty: Fraction
    metadata_torsion_index: str
    metadata_rotor: str

    @property
    def unresolved_scientific_target_count(self) -> int:
        return 0


def reconstruct_phenol_source_status(path: Path = PHENOL_SNAPSHOT) -> PhenolSourceStatus:
    raw = path.read_text(encoding="utf-8")
    parser = _TableParser()
    parser.feed(raw)
    grids = [
        table
        for table in parser.tables
        if table and table[0][:2] == ["torsion index", "Angle"] and len(table[0]) >= 4
    ]
    if len(grids) != 1:
        raise ValueError("phenol source must contain exactly one internal-rotation grid")

    rows = grids[0][1:]
    by_index: dict[str, list[list[str]]] = {}
    for row in rows:
        if len(row) < 4:
            raise ValueError("phenol source contains a malformed internal-rotation row")
        by_index.setdefault(row[0], []).append(row)

    measured: list[str] = []
    placeholders: list[str] = []
    measured_rows: list[list[str]] = []
    placeholder_rows: list[list[str]] = []
    for index, indexed_rows in by_index.items():
        with_values = [row for row in indexed_rows if row[2] and row[3]]
        without_values = [row for row in indexed_rows if not row[2] and not row[3]]
        if with_values and without_values:
            raise ValueError("one torsion index mixes measured and blank source rows")
        if with_values:
            measured.append(index)
            measured_rows.extend(with_values)
        elif len(without_values) == len(indexed_rows):
            placeholders.append(index)
            placeholder_rows.extend(without_values)
        else:
            raise ValueError("one torsion index has a partial energy inscription")

    compact_text = " ".join(" ".join(parser.text).split())
    reference = re.search(r"V2=([0-9]+)\+?-([0-9]+)\s*cm", compact_text)
    metadata = re.search(r"Atoms in torsion\s+(\d+)\s+are .*?The rotor type is\s+([A-Za-z0-9]+)", compact_text)
    if reference is None or metadata is None:
        raise ValueError("phenol reference or torsion metadata is absent")

    result = PhenolSourceStatus(
        measured_torsion_indices=tuple(measured),
        structural_placeholder_indices=tuple(placeholders),
        measured_state_count=len(measured_rows),
        preserved_placeholder_row_count=len(placeholder_rows),
        greatest_wavenumber=max(Fraction(row[3]) for row in measured_rows),
        greatest_energy_kj_mol=max(Fraction(row[2]) for row in measured_rows),
        reference_wavenumber=Fraction(reference.group(1)),
        reference_uncertainty=Fraction(reference.group(2)),
        metadata_torsion_index=metadata.group(1),
        metadata_rotor=metadata.group(2),
    )
    if (
        result.measured_torsion_indices != ("1",)
        or result.structural_placeholder_indices != ("2",)
        or result.measured_state_count != 25
        or result.preserved_placeholder_row_count != 1
        or result.greatest_wavenumber != result.reference_wavenumber
        or result.metadata_torsion_index != "1"
        or result.metadata_rotor != "OH"
    ):
        raise ValueError("phenol source-status reconstruction changed")
    return result


__all__ = ("PHENOL_SNAPSHOT", "PhenolSourceStatus", "reconstruct_phenol_source_status")
