#!/usr/bin/env python3
"""Capture and separate the official PROP-005 molecular-dipole evidence.

The identity registry contains source and structural identities only.  Exact
measurement inscriptions are written to a distinct withheld registry consumed
only after the capability-closed prediction seal.
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
PDF_PATH = SNAPSHOT_DIR / "prop-005-nist-water-dipole-1973-v1.pdf"
HTML_PATH = SNAPSHOT_DIR / "prop-005-nist-cccbdb-experimental-dipoles-v1.html"
PRIMARY_PATH = SNAPSHOT_DIR / "prop-005-molecular-dipole-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_dipole_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_dipole_withheld_targets_v1.json"

PDF_URL = "https://tf.nist.gov/general/pdf/274.pdf"
HTML_URL = "https://cccbdb.nist.gov/diplistx.asp"
PDF_EXPECTED_SHA256 = "e3df9979865e12887c564327a3029f11c03caeb8cf6d9c90b499972a954ebb84"


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
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.lower() == "tr":
            self._row = []
        elif tag.lower() in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif lowered == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def exact_pair(value: str) -> dict[str, int]:
    part = Fraction(value)
    if part.numerator < 1 or part.denominator < 1:
        raise ValueError("positive measurement record left the exact Fold boundary")
    return {"numerator": part.numerator, "denominator": part.denominator}


def positive_record(
    target_id: str,
    species: str,
    axis: str,
    role: str,
    central: str,
    uncertainty: str,
    symmetry: str,
    component_support: int,
    raw_inscription: str,
) -> dict[str, object]:
    value = Fraction(central)
    error = Fraction(uncertainty)
    if value <= error:
        raise ValueError("dipole interval must remain exact and positive")
    return {
        "target_id": target_id,
        "source_id": "NIST-NBS-JCP-59-2254-1973",
        "source_locator": "PDF page 5; journal page 2258; displayed result equations",
        "snapshot_path": str(PDF_PATH.relative_to(ROOT)),
        "species": species,
        "molecular_state": "ground-vibrational-effective-dipole",
        "geometry": "bent-water-triatomic",
        "charge_distinction_carrier": "one-oxygen-centred-two-endpoint-electronic-charge-organization",
        "symmetry": symmetry,
        "component_support": component_support,
        "measurement_role": role,
        "axis": axis,
        "method": "microwave-Stark spectroscopy",
        "condition": "gas-phase ground vibrational state; principal-axis energy representation",
        "conventional_direction": "source-negative-axis-sign-retained-as-correspondence-only",
        "value_kind": "positive_magnitude",
        "central": exact_pair(central),
        "uncertainty": exact_pair(uncertainty),
        "lower": exact_pair(str(value - error)),
        "upper": exact_pair(str(value + error)),
        "inscription": central + " +/- " + uncertainty + " D",
        "raw_source_inscription": raw_inscription,
    }


def absence_record(target_id: str, species: str, state: str, html_hash: str) -> dict[str, object]:
    return {
        "target_id": target_id,
        "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-DIPOLES",
        "source_locator": "Experimental Dipoles table; named homonuclear isotopologue row; total column",
        "snapshot_path": str(HTML_PATH.relative_to(ROOT)),
        "snapshot_hash": html_hash,
        "species": species,
        "molecular_state": state,
        "geometry": "homonuclear-diatomic",
        "charge_distinction_carrier": "exchange-identical-two-endpoint-charge-organization",
        "symmetry": "inversion-exchange-symmetric-homonuclear-diatomic",
        "component_support": "structural-EmptyOne",
        "measurement_role": "total-magnitude",
        "axis": "all-axes-closed",
        "method": "NIST evaluated experimental dipole compilation",
        "condition": "gas phase; database experimental state row",
        "conventional_direction": "structural-EmptyOne",
        "value_kind": "source_absence_glyph",
        "inscription": "0.000 D",
        "source_glyph": "0.000",
        "native_interpretation": "EmptyOne",
    }


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = fetch_or_preserve(PDF_PATH, PDF_URL)
    html = fetch_or_preserve(HTML_PATH, HTML_URL)
    pdf_hash, html_hash = digest(pdf), digest(html)
    if pdf_hash != "sha256:" + PDF_EXPECTED_SHA256:
        raise RuntimeError("NIST 1973 water-dipole source bytes differ from the visually audited source")
    html_text = html.decode("utf-8", errors="replace")
    if "Experimental Dipoles" not in html_text or "Dipole moments in Debye" not in html_text:
        raise RuntimeError("NIST CCCBDB experimental-dipole surface is absent")
    parser = CellTableParser()
    parser.feed(html_text)
    table_rows = {row[0]: row for row in parser.rows if len(row) >= 9 and row[0] in {"H2", "D2"}}
    if set(table_rows) != {"H2", "D2"}:
        raise RuntimeError("complete H2/D2 CCCBDB identity boundary is absent")
    for species in ("H2", "D2"):
        if table_rows[species][6] != "0.000":
            raise RuntimeError(f"{species} total source absence glyph changed")

    records = [
        absence_record("NIST-CCCBDB-H2-TOTAL", "H2", "1-Sigma-g", html_hash),
        absence_record("NIST-CCCBDB-D2-TOTAL", "D2", "1-Sigma-g", html_hash),
        positive_record(
            "NIST-1973-H2O-B-COMPONENT", "H2O", "principal-b", "component-magnitude",
            "1.8546", "0.0006", "exchange-symmetric-equal-endpoint-isotopologue", 1,
            "mu_b = mu_x = -1.8546 +/- 0.0006 D",
        ),
        positive_record(
            "NIST-1973-H2O-TOTAL", "H2O", "geometric-x", "total-magnitude",
            "1.8546", "0.0006", "exchange-symmetric-equal-endpoint-isotopologue", 1,
            "mu_b = mu_x = -1.8546 +/- 0.0006 D",
        ),
        positive_record(
            "NIST-1973-D2O-B-COMPONENT", "D2O", "principal-b", "component-magnitude",
            "1.8558", "0.0021", "exchange-symmetric-equal-endpoint-isotopologue", 1,
            "mu_b = mu_x = -1.8558 +/- 0.0021 D",
        ),
        positive_record(
            "NIST-1973-D2O-TOTAL", "D2O", "geometric-x", "total-magnitude",
            "1.8558", "0.0021", "exchange-symmetric-equal-endpoint-isotopologue", 1,
            "mu_b = mu_x = -1.8558 +/- 0.0021 D",
        ),
        positive_record(
            "NIST-1973-HDO-A-COMPONENT", "HDO", "principal-a", "component-magnitude",
            "0.6567", "0.0004", "isotope-distinguished-principal-axis-carrier", 2,
            "mu_a = -0.6567 +/- 0.0004 D",
        ),
        positive_record(
            "NIST-1973-HDO-B-COMPONENT", "HDO", "principal-b", "component-magnitude",
            "1.7318", "0.0009", "isotope-distinguished-principal-axis-carrier", 2,
            "mu_b = -1.7318 +/- 0.0009 D",
        ),
        positive_record(
            "NIST-1973-HDO-TOTAL", "HDO", "geometric-x", "total-magnitude",
            "1.8521", "0.0012", "isotope-distinguished-principal-axis-carrier", 2,
            "mu_x = -(|mu_a|^2 + |mu_b|^2)^(1/2) = -1.8521 +/- 0.0012 D",
        ),
    ]
    for row in records:
        row.setdefault("snapshot_hash", pdf_hash)

    primary = {
        "schema": "sft-v3-molecular-dipole-primary-records/1",
        "provenance": "manual two-pass transcription from visually audited official pages; exact source bytes bound",
        "sources": [
            {
                "source_id": "NIST-NBS-JCP-59-2254-1973",
                "title": "Dipole moment of water from Stark measurements of H2O, HDO, and D2O",
                "publisher": "National Bureau of Standards reprint of Journal of Chemical Physics 59, 2254 (1973)",
                "url": PDF_URL,
                "snapshot_path": str(PDF_PATH.relative_to(ROOT)),
                "snapshot_hash": pdf_hash,
                "visually_verified_pages": ["PDF page 1 / journal page 2254", "PDF page 5 / journal page 2258"],
            },
            {
                "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-DIPOLES",
                "title": "CCCBDB list of experimental dipole moments",
                "publisher": "National Institute of Standards and Technology, Standard Reference Database 101",
                "url": HTML_URL,
                "snapshot_path": str(HTML_PATH.relative_to(ROOT)),
                "snapshot_hash": html_hash,
                "registered_rows": ["H2", "D2"],
            },
        ],
        "records": records,
        "all_registered_rows_preserved": True,
        "absence_policy": {
            "source_glyph": "0 or 0.000",
            "native_form": "EmptyOne",
            "numerical_zero_admitted": False,
        },
    }
    write_json(PRIMARY_PATH, primary)
    primary_hash = digest(PRIMARY_PATH.read_bytes())

    identity_rows = []
    measurement_rows = []
    value_keys = {
        "central", "uncertainty", "lower", "upper", "inscription", "raw_source_inscription", "source_glyph"
    }
    for row in records:
        identity = {key: value for key, value in row.items() if key not in value_keys}
        identity["target_value_absent"] = True
        identity_rows.append(identity)
        measurement_rows.append(dict(row))

    identity_document = {
        "schema": "sft-v3-molecular-dipole-identities/1",
        "source_primary_record_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "source_primary_record_hash": primary_hash,
        "rows": identity_rows,
        "all_measurement_values_absent": True,
        "registered_species_order": ["H2", "D2", "H2O", "D2O", "HDO"],
        "registered_measurement_row_count": len(identity_rows),
    }
    write_json(IDENTITY_PATH, identity_document)
    identity_hash = digest(IDENTITY_PATH.read_bytes())
    target_document = {
        "schema": "sft-v3-molecular-dipole-withheld-measurements/1",
        "identity_document_hash": digest(json.dumps(identity_document, sort_keys=True, separators=(",", ":")).encode()),
        "identity_file_hash": identity_hash,
        "release_requires_prediction_seal": True,
        "rows": measurement_rows,
        "all_registered_rows_preserved": True,
    }
    write_json(TARGET_PATH, target_document)
    print("captured", len(records), "PROP-005 measurement rows")
    print("primary", primary_hash)
    print("identities", digest(IDENTITY_PATH.read_bytes()))
    print("withheld", digest(TARGET_PATH.read_bytes()))


if __name__ == "__main__":
    main()
