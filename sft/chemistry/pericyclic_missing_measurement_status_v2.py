"""Versioned ORG-012 source-status reconstruction for four blank table rows.

Blank primary-table rows are not adverse measurements.  They are preserved as
measurement obligations whose outcomes were not reported by that source.  The
distinction prevents an absent experiment from being retired as a failed law.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1"
    / "complete-postseal-analysis-v1.json"
)


@dataclass(frozen=True)
class MissingPericyclicMeasurement:
    ordinal: int
    adduct_pair: str
    diene: str
    absent_fields: tuple[str, ...]
    source_status: str = "measurement-not-reported-in-primary-table"
    scientific_result_retired: bool = False


def reconstruct_missing_measurements(path: Path = ANALYSIS) -> tuple[MissingPericyclicMeasurement, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = document["primary_table_rows_in_source_order"]
    if len(rows) != 32:
        raise ValueError("ORG-012 primary table census changed")
    fields = (
        "temperature_conventional",
        "time_conventional",
        "isolated_yield_conventional",
        "endo_exo_experimental_conventional",
    )
    result = tuple(
        MissingPericyclicMeasurement(
            ordinal=row["ordinal"],
            adduct_pair=row["adducts"],
            diene=row["diene"],
            absent_fields=tuple(field for field in fields if row[field] == "—"),
        )
        for row in rows
        if row["experimental_ratio_status"] == "unresolved_absent_in_primary_table"
    )
    expected = (
        (6, "5CPD-n, 5CPD-x", "2"),
        (19, "12BD-n, 12BD-x", "1"),
        (27, "17BD-n, 17BD-x", "1"),
        (30, "18CPD-n, 18CPD-x", "2"),
    )
    if tuple((row.ordinal, row.adduct_pair, row.diene) for row in result) != expected:
        raise ValueError("ORG-012 missing-measurement identity vector changed")
    if any("endo_exo_experimental_conventional" not in row.absent_fields for row in result):
        raise ValueError("ORG-012 blank ratio was incorrectly classified as measured")
    return result


__all__ = ("ANALYSIS", "MissingPericyclicMeasurement", "reconstruct_missing_measurements")
