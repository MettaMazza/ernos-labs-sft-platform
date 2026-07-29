"""Versioned ANAL-008 reconstruction of deposited zero-rate inscriptions.

In native SFT arithmetic the glyph ``0`` denotes absence; it is not a numerical
rate.  This implementation independently reads the NMR-STAR source and binds
each deposited zero to the absence of a reported positive fitted magnitude.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex


ROOT = Path(__file__).resolve().parents[2]
BMRB_ENTRY = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1"
    / "bmr27257_3.str"
)


@dataclass(frozen=True)
class ExchangeAbsence:
    saveframe: str
    row_id: str
    residue: str
    sequence_id: str
    raw_value_glyph: str
    value_min: str
    value_max: str
    value_error: str
    native_status: str = "structural-absence-of-reported-positive-fitted-rate"


def _exchange_rows(path: Path) -> tuple[dict[str, str], ...]:
    lines = path.read_text(encoding="utf-8").splitlines()
    saveframe = ""
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("save_H_exch_rate_list_"):
            saveframe = stripped.removeprefix("save_")
        if stripped != "loop_":
            index += 1
            continue
        index += 1
        headers: list[str] = []
        while index < len(lines) and lines[index].strip().startswith("_"):
            headers.append(lines[index].strip())
            index += 1
        if not headers or not all(header.startswith("_H_exch_rate.") for header in headers):
            while index < len(lines) and lines[index].strip() != "stop_":
                index += 1
            index += 1
            continue
        while index < len(lines) and lines[index].strip() != "stop_":
            stripped = lines[index].strip()
            if stripped:
                values = shlex.split(stripped, posix=True)
                if len(values) != len(headers):
                    raise ValueError("ANAL-008 NMR-STAR exchange row width changed")
                rows.append({"saveframe": saveframe, **dict(zip(headers, values))})
            index += 1
        index += 1
    if len(rows) != 138:
        raise ValueError("ANAL-008 complete exchange-row census changed")
    return tuple(rows)


def reconstruct_exchange_absences(path: Path = BMRB_ENTRY) -> tuple[ExchangeAbsence, ...]:
    rows = _exchange_rows(path)
    result = tuple(
        ExchangeAbsence(
            saveframe=row["saveframe"],
            row_id=row["_H_exch_rate.ID"],
            residue=row["_H_exch_rate.Comp_ID"],
            sequence_id=row["_H_exch_rate.Seq_ID"],
            raw_value_glyph=row["_H_exch_rate.Val"],
            value_min=row["_H_exch_rate.Val_min"],
            value_max=row["_H_exch_rate.Val_max"],
            value_error=row["_H_exch_rate.Val_err"],
        )
        for row in rows
        if row["_H_exch_rate.Val"] == "0"
    )
    expected = (
        ("H_exch_rate_list_1", "ILE", "105"),
        ("H_exch_rate_list_1", "ASP", "112"),
        ("H_exch_rate_list_1", "THR", "137"),
        ("H_exch_rate_list_1", "GLY", "139"),
        ("H_exch_rate_list_2", "PHE", "64"),
        ("H_exch_rate_list_2", "PHE", "66"),
        ("H_exch_rate_list_2", "ILE", "105"),
        ("H_exch_rate_list_2", "MET", "108"),
        ("H_exch_rate_list_2", "THR", "137"),
        ("H_exch_rate_list_2", "LEU", "138"),
        ("H_exch_rate_list_2", "ILE", "140"),
    )
    observed = tuple((row.saveframe, row.residue, row.sequence_id) for row in result)
    if observed != expected:
        raise ValueError("ANAL-008 exact deposited-zero identity vector changed")
    if any(
        row.raw_value_glyph != "0"
        or row.value_min != "."
        or row.value_max != "."
        or row.value_error != "."
        for row in result
    ):
        raise ValueError("ANAL-008 zero-rate boundary metadata changed")
    return result


__all__ = ("BMRB_ENTRY", "ExchangeAbsence", "reconstruct_exchange_absences")
