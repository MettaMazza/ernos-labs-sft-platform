#!/usr/bin/env python3
"""Capture the complete NIST CCCBDB molecular-polarizability surface.

The public identity registry contains every non-atomic table row but no alpha
value.  Exact decimal inscriptions are isolated in the withheld registry and
may be opened only after the value-free PROP-006 prediction has been sealed.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots"
HTML_PATH = SNAPSHOT_DIR / "prop-006-nist-cccbdb-experimental-polarizabilities-v1.html"
PRIMARY_PATH = SNAPSHOT_DIR / "prop-006-molecular-polarizability-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_polarizability_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_polarizability_withheld_targets_v1.json"
HTML_URL = "https://cccbdb.nist.gov/pollistx.asp"


def digest(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_or_preserve(path: Path, url: str) -> bytes:
    if path.exists():
        return path.read_bytes()
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"empty source response: {url}")
    path.write_bytes(data)
    return data


class CellTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, ...]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        lowered = tag.casefold()
        if lowered == "tr":
            self._row = []
        elif lowered in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            normalized = " ".join(data.split())
            if normalized:
                self._cell.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell))
            self._cell = None
        elif lowered == "tr" and self._row is not None:
            if self._row:
                self.rows.append(tuple(self._row))
            self._row = None
            self._cell = None


def exact_pair(value: Fraction) -> dict[str, int]:
    if value.numerator < 1 or value.denominator < 1:
        raise ValueError("polarizability record left the exact positive domain")
    return {"numerator": value.numerator, "denominator": value.denominator}


def rounding_interval(inscription: str) -> tuple[Fraction, Fraction]:
    central = Fraction(inscription)
    places = len(inscription.partition(".")[2])
    half_unit = Fraction(1, 2 * (10 ** places))
    lower, upper = central - half_unit, central + half_unit
    if lower <= 0:
        raise ValueError("display rounding interval is not wholly positive")
    return lower, upper


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    html = fetch_or_preserve(HTML_PATH, HTML_URL)
    html_hash = digest(html)
    text = html.decode("utf-8", errors="replace")
    if "Experimental Polarizabilites" not in text or "Polarizabilites in" not in text:
        raise RuntimeError("NIST CCCBDB experimental-polarizability surface is absent")
    parser = CellTableParser()
    parser.feed(text)
    source_rows = tuple(
        row for row in parser.rows
        if len(row) == 7 and row[0] != "Molecule" and row[4].replace(".", "", 1).isdigit()
    )
    if len(source_rows) != 276:
        raise RuntimeError(f"NIST complete polarizability table changed: {len(source_rows)} rows")
    atomic_rows = tuple(row for row in source_rows if row[1].casefold().endswith(" atom"))
    molecular_rows = tuple(row for row in source_rows if not row[1].casefold().endswith(" atom"))
    if len(atomic_rows) != 24 or len(molecular_rows) != 252:
        raise RuntimeError("value-free atom/molecule boundary changed")

    records = []
    for ordinal, row in enumerate(molecular_rows, start=1):
        formula, name, state, conformation, inscription, reference, comment = row
        value = Fraction(inscription)
        lower, upper = rounding_interval(inscription)
        records.append({
            "target_id": f"NIST-CCCBDB-PROP-006-MOLECULAR-{ordinal:03d}",
            "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-POLARIZABILITIES",
            "source_locator": f"Experimental Polarizabilites table; non-atomic row {ordinal}",
            "snapshot_path": str(HTML_PATH.relative_to(ROOT)),
            "snapshot_hash": html_hash,
            "source_row_ordinal": ordinal,
            "formula": formula,
            "name": name,
            "molecular_state": state,
            "conformation": conformation,
            "response_kind": "evaluated-experimental-static-dipole-polarizability-alpha",
            "component_definition": "source-reported-molecular-alpha-scalar",
            "method": "NIST-evaluated-experimental-compilation",
            "condition": "gas-phase molecular state and conformation as registered by CCCBDB",
            "units": "angstrom-cubed",
            "reference": reference,
            "comment": comment,
            "value": exact_pair(value),
            "display_rounding_lower": exact_pair(lower),
            "display_rounding_upper": exact_pair(upper),
            "inscription": inscription,
        })

    references = sorted({str(row["reference"]) for row in records})
    primary = {
        "schema": "sft-v3-molecular-polarizability-primary-records/1",
        "source": {
            "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-POLARIZABILITIES",
            "title": "CCCBDB list of experimental polarizabilities",
            "publisher": "National Institute of Standards and Technology, Standard Reference Database 101",
            "url": HTML_URL,
            "snapshot_path": str(HTML_PATH.relative_to(ROOT)),
            "snapshot_hash": html_hash,
            "source_unit": "angstrom-cubed",
        },
        "selection_rule": "retain every table row whose NIST name is not explicitly an atom; rule fixed without alpha access",
        "complete_source_rows": len(source_rows),
        "excluded_atomic_rows": len(atomic_rows),
        "complete_molecular_rows": len(records),
        "reference_cohorts": references,
        "records": records,
        "all_molecular_rows_preserved": True,
        "numerical_zero_record_present": False,
    }
    write_json(PRIMARY_PATH, primary)
    primary_hash = digest(PRIMARY_PATH.read_bytes())

    value_keys = {"value", "display_rounding_lower", "display_rounding_upper", "inscription"}
    identity_rows = []
    for record in records:
        identity = {key: value for key, value in record.items() if key not in value_keys}
        identity["target_value_absent"] = True
        identity_rows.append(identity)
    identities = {
        "schema": "sft-v3-molecular-polarizability-identities/1",
        "source_primary_record_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "source_primary_record_hash": primary_hash,
        "selection_rule": primary["selection_rule"],
        "rows": identity_rows,
        "all_polarizability_values_absent": True,
        "complete_molecular_row_count": len(identity_rows),
    }
    write_json(IDENTITY_PATH, identities)
    identity_hash = digest(IDENTITY_PATH.read_bytes())
    targets = {
        "schema": "sft-v3-molecular-polarizability-withheld-measurements/1",
        "identity_document_hash": digest(json.dumps(identities, sort_keys=True, separators=(",", ":")).encode()),
        "identity_file_hash": identity_hash,
        "release_requires_prediction_seal": True,
        "source_unit": "angstrom-cubed",
        "rows": records,
        "all_molecular_rows_preserved": True,
        "complete_molecular_row_count": len(records),
    }
    write_json(TARGET_PATH, targets)
    print("captured", len(records), "complete molecular polarizability rows")
    print("snapshot", html_hash)
    print("primary", primary_hash)
    print("identities", digest(IDENTITY_PATH.read_bytes()))
    print("withheld", digest(TARGET_PATH.read_bytes()))


if __name__ == "__main__":
    main()
