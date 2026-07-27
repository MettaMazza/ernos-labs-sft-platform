#!/usr/bin/env python3
"""Freeze the complete authoritative external surface for Chemistry PROP-011.

The value-free identity document is written separately from the withheld value
vault.  The complete CCCBDB hydrogen-bonded-dimer catalogue is traversed: all
listed dimers and every linked method/basis value are retained, including
signed adverse inscriptions.  NIST-hosted water-cluster dissociation values
and the complete NIST ion-cluster thermochemistry compendium are preserved as
separate empirical and scope records.  No source number is a derivation input.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1"
INDEX_URL = "https://cccbdb.nist.gov/dimer_bond1x.asp"
INDEX_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-hydrogen-bonded-dimer-list.html"
WATER_CLUSTER_URL = "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=925773"
WATER_CLUSTER_PATH = SNAPSHOT_DIR / "nist-water-cluster-dissociation-values-2018.pdf"
ION_CLUSTER_URL = "https://srd.nist.gov/jpcrdreprint/1.555757.pdf"
ION_CLUSTER_PATH = SNAPSHOT_DIR / "nist-ion-cluster-thermochemistry-complete-1986.pdf"
PRIMARY_PATH = SNAPSHOT_DIR / "intermolecular-binding-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/intermolecular_binding_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/intermolecular_binding_withheld_targets_v1.json"


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + sha256(payload).hexdigest()


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fetch_or_preserve(path: Path, url: str) -> bytes:
    if path.exists():
        return path.read_bytes()
    request = Request(url, headers={"User-Agent": "SFT-v3-source-capture/1"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    if not payload:
        raise RuntimeError(f"empty authoritative response: {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


class _TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_row: list[dict[str, object]] | None = None
        self.current_cell: dict[str, object] | None = None
        self.rows: list[list[dict[str, object]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.current_row = []
        elif tag in {"td", "th"} and self.current_row is not None:
            self.current_cell = {"parts": [], "hrefs": []}
            self.current_row.append(self.current_cell)
        elif tag == "a" and self.current_cell is not None:
            href = dict(attrs).get("href")
            if href:
                self.current_cell["hrefs"].append(href)

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            self.rows.append(self.current_row)
            self.current_row = None


def _clean_cell(cell: dict[str, object]) -> str:
    return " ".join("".join(str(part) for part in cell["parts"]).split())


def _listed_dimers(index: bytes) -> tuple[dict[str, str], ...]:
    parser = _TableRows()
    parser.feed(index.decode("utf-8", errors="replace"))
    records: list[dict[str, str]] = []
    for row in parser.rows:
        hrefs = [str(href) for cell in row for href in cell["hrefs"]]
        link = next((href for href in hrefs if "dimer_bond2x.asp?di=" in href), None)
        if link is None:
            continue
        cells = [_clean_cell(cell) for cell in row]
        if len(cells) < 7:
            raise RuntimeError("CCCBDB dimer list row lost its constituent fields")
        match = re.search(r"[?&]di=([0-9]+)", link)
        if match is None:
            raise RuntimeError("CCCBDB dimer list link lost its identifier")
        records.append({
            "dimer_id": match.group(1),
            "dimer_formula": cells[1],
            "dimer_name": cells[2],
            "donor_formula": cells[3],
            "donor_name": cells[4],
            "acceptor_formula": cells[5],
            "acceptor_name": cells[6],
            "comment": cells[7] if len(cells) > 7 else "",
        })
    if len(records) != 11 or len({row["dimer_id"] for row in records}) != 11:
        raise RuntimeError("the complete CCCBDB dimer catalogue is not eleven unique entries")
    return tuple(records)


_VALUE_LINK = re.compile(
    r'<a\s+href="dimer_bond3x\.asp\?casno=([0-9]+)&(?:amp;)?method=([0-9]+)&(?:amp;)?basis=([0-9]+)">\s*([^<]+?)\s*</a>',
    re.IGNORECASE,
)


def _calculation_rows(dimer: dict[str, str], page: bytes, page_path: Path) -> tuple[dict[str, object], ...]:
    text = page.decode("utf-8", errors="replace")
    records: list[dict[str, object]] = []
    for casno, method_id, basis_id, inscription in _VALUE_LINK.findall(text):
        value = Fraction(inscription.strip())
        target_id = f"CCCBDB-DIMER-{dimer['dimer_id']}-METHOD-{method_id}-BASIS-{basis_id}"
        records.append({
            "target_id": target_id,
            **dimer,
            "casno": casno,
            "method_id": method_id,
            "basis_id": basis_id,
            "source_id": "NIST-CCCBDB-SRD-101-DIMER-BINDING",
            "source_class": "authoritative-calculated-benchmark",
            "source_locator": f"dimer_bond2x.asp?di={dimer['dimer_id']}; method={method_id}; basis={basis_id}",
            "snapshot_path": str(page_path.relative_to(ROOT)),
            "value_inscription_kJ_per_mol": inscription.strip(),
            "external_orientation": "positive-bound-record" if value > 0 else "signed-adverse-or-unbound-record",
            "absolute_inscribed_magnitude_kJ_per_mol": _fraction_record(abs(value)),
        })
    if len(records) != len({row["target_id"] for row in records}):
        raise RuntimeError(f"duplicate CCCBDB method/basis row for dimer {dimer['dimer_id']}")
    return tuple(records)


def main() -> None:
    index = _fetch_or_preserve(INDEX_PATH, INDEX_URL)
    dimers = _listed_dimers(index)
    calculated: list[dict[str, object]] = []
    dimer_pages: list[dict[str, object]] = []
    unavailable_dnf = 0
    for dimer in dimers:
        url = urljoin(INDEX_URL, f"dimer_bond2x.asp?di={dimer['dimer_id']}")
        path = SNAPSHOT_DIR / f"nist-cccbdb-dimer-{dimer['dimer_id']}-complete-method-basis-surface.html"
        payload = _fetch_or_preserve(path, url)
        rows = _calculation_rows(dimer, payload, path)
        calculated.extend(rows)
        unavailable_dnf += len(re.findall(r">\s*dnf\s*<", payload.decode("utf-8", errors="replace"), re.IGNORECASE))
        dimer_pages.append({
            "dimer_id": dimer["dimer_id"], "url": url,
            "snapshot_path": str(path.relative_to(ROOT)), "snapshot_hash": _hash_bytes(payload),
            "linked_numeric_row_count": len(rows),
        })
    if len(calculated) != 1297 or len({row["target_id"] for row in calculated}) != 1297:
        raise RuntimeError("complete CCCBDB linked dimer surface changed from 1,297 unique rows")

    water_pdf = _fetch_or_preserve(WATER_CLUSTER_PATH, WATER_CLUSTER_URL)
    ion_pdf = _fetch_or_preserve(ION_CLUSTER_PATH, ION_CLUSTER_URL)
    experimental = (
        {
            "target_id": "NIST-WATER-CLUSTER-H2O-DIMER-D0-2018",
            "dimer_id": "25655838", "dimer_formula": "(H2O)2", "dimer_name": "water dimer",
            "donor_formula": "H2O", "donor_name": "Water", "acceptor_formula": "H2O", "acceptor_name": "Water",
            "separation_organization": "reported ground cluster dissociation boundary",
            "source_id": "NIST-FARADAY-C8FD00092A-H2O-DIMER-D0",
            "source_class": "reported-experimental-cluster-dissociation-value",
            "source_locator": "PDF page 13; article page 13; lines reporting (H2O)2 dissociation energy; original Ref. 87",
            "snapshot_path": str(WATER_CLUSTER_PATH.relative_to(ROOT)),
            "value_inscription_cm_inverse": "1105", "uncertainty_inscription_cm_inverse": "10",
            "central_cm_inverse": _fraction_record(Fraction(1105, 1)),
            "uncertainty_cm_inverse": _fraction_record(Fraction(10, 1)),
            "lower_cm_inverse": _fraction_record(Fraction(1095, 1)),
            "upper_cm_inverse": _fraction_record(Fraction(1115, 1)),
            "external_orientation": "positive-bound-record",
        },
        {
            "target_id": "NIST-WATER-CLUSTER-D2O-DIMER-D0-2018",
            "dimer_id": "D2O-DIMER", "dimer_formula": "(D2O)2", "dimer_name": "heavy-water dimer",
            "donor_formula": "D2O", "donor_name": "Heavy water", "acceptor_formula": "D2O", "acceptor_name": "Heavy water",
            "separation_organization": "reported ground cluster dissociation boundary",
            "source_id": "NIST-FARADAY-C8FD00092A-D2O-DIMER-D0",
            "source_class": "reported-experimental-cluster-dissociation-value",
            "source_locator": "PDF page 13; article page 13; lines reporting (D2O)2 dissociation energy; original Ref. 88",
            "snapshot_path": str(WATER_CLUSTER_PATH.relative_to(ROOT)),
            "value_inscription_cm_inverse": "1244", "uncertainty_inscription_cm_inverse": "10",
            "central_cm_inverse": _fraction_record(Fraction(1244, 1)),
            "uncertainty_cm_inverse": _fraction_record(Fraction(10, 1)),
            "lower_cm_inverse": _fraction_record(Fraction(1234, 1)),
            "upper_cm_inverse": _fraction_record(Fraction(1254, 1)),
            "external_orientation": "positive-bound-record",
        },
    )

    all_rows = tuple(calculated) + experimental
    identities = []
    measurements = []
    for row in all_rows:
        identity = {
            key: row[key] for key in (
                "target_id", "dimer_id", "dimer_formula", "dimer_name", "donor_formula", "donor_name",
                "acceptor_formula", "acceptor_name", "source_id", "source_class", "source_locator", "snapshot_path",
            )
        }
        identity.update({
            "separated_constituent_identities_retained": True,
            "bound_composite_identity_retained": True,
            "separation_organization_retained": True,
            "target_value_absent": True,
        })
        if "method_id" in row:
            identity.update({"method_id": row["method_id"], "basis_id": row["basis_id"], "casno": row["casno"]})
        identities.append(identity)
        measurements.append(row)

    primary = {
        "schema": "sft-v3-intermolecular-binding-primary-records/1",
        "retrieved": "2026-07-26",
        "complete_cccbdb_dimer_count": len(dimers),
        "complete_cccbdb_linked_value_count": len(calculated),
        "complete_cccbdb_positive_value_count": sum(Fraction(str(row["value_inscription_kJ_per_mol"])) > 0 for row in calculated),
        "complete_cccbdb_signed_adverse_value_count": sum(Fraction(str(row["value_inscription_kJ_per_mol"])) < 0 for row in calculated),
        "complete_cccbdb_external_zero_glyph_count": sum(Fraction(str(row["value_inscription_kJ_per_mol"])) == 0 for row in calculated),
        "complete_cccbdb_unavailable_dnf_inscription_count": unavailable_dnf,
        "reported_experimental_cluster_dissociation_count": len(experimental),
        "index": {"url": INDEX_URL, "snapshot_path": str(INDEX_PATH.relative_to(ROOT)), "snapshot_hash": _hash_bytes(index)},
        "dimer_pages": dimer_pages,
        "water_cluster_source": {
            "url": WATER_CLUSTER_URL, "snapshot_path": str(WATER_CLUSTER_PATH.relative_to(ROOT)),
            "snapshot_hash": _hash_bytes(water_pdf), "visually_verified_locator": "PDF/article page 13 and references 87-88",
        },
        "ion_cluster_compendium": {
            "url": ION_CLUSTER_URL, "snapshot_path": str(ION_CLUSTER_PATH.relative_to(ROOT)),
            "snapshot_hash": _hash_bytes(ion_pdf), "scope": "complete 62-page NIST-hosted nine-table ion-cluster thermochemistry compilation",
            "numerical_rows_used_as_targets": False,
            "reason": "preserved as complete wider cluster boundary; its mixed enthalpy, D0 and De records are not relabelled as one homogeneous measured quantity",
        },
        "source_class_separation": (
            "The 1,297 CCCBDB rows are calculated benchmarks, not measurements. The two water-cluster rows are "
            "reported dissociation values with uncertainties. Signed adverse CCCBDB inscriptions remain external "
            "source records and never become negative SFT numbers."
        ),
    }
    identity_document = {
        "schema": "sft-v3-intermolecular-binding-identities/1",
        "complete_row_count": len(identities),
        "all_binding_values_absent": True,
        "rows": identities,
    }
    target_document = {
        "schema": "sft-v3-intermolecular-binding-withheld-targets/1",
        "complete_row_count": len(measurements),
        "all_target_values_separate_from_identities": True,
        "rows": measurements,
    }
    _write_json(PRIMARY_PATH, primary)
    _write_json(IDENTITY_PATH, identity_document)
    _write_json(TARGET_PATH, target_document)
    print(json.dumps({
        "dimers": len(dimers), "linked_values": len(calculated),
        "positive": primary["complete_cccbdb_positive_value_count"],
        "signed_adverse": primary["complete_cccbdb_signed_adverse_value_count"],
        "experimental_cluster_values": len(experimental), "target_rows": len(measurements),
        "primary_hash": _hash_bytes(PRIMARY_PATH.read_bytes()),
        "identity_hash": _hash_bytes(IDENTITY_PATH.read_bytes()),
        "target_hash": _hash_bytes(TARGET_PATH.read_bytes()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
