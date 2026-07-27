#!/usr/bin/env python3
"""Capture the complete NIST SRD 101 experimental internal-rotation barrier collection for KIN-004."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/activation_barrier_capture_spec_v1.json"
SPEC_HASH = "sha256:c29aa3d64e8cb0802e91fba795f4c1f71b2ddf05de33b114c2e095ebce991e9f"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-004-activation-barrier-v1"
INDEX_PATH = SNAPSHOT_ROOT / "nist-cccbdb-experimental-internal-rotation-barrier-index.html"
PRIMARY_PATH = SNAPSHOT_ROOT / "activation-barrier-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/activation_barrier_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/activation_barrier_withheld_targets_v1.json"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._link_text: list[str] = []
        self._table_depth = 0
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a":
            self._href = attributes.get("href")
            self._link_text = []
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._table = []
        if tag == "tr" and self._table_depth == 1:
            self._row = []
        if tag in {"th", "td"} and self._table_depth == 1:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.links.append({"href": self._href, "text": " ".join(" ".join(self._link_text).split())})
            self._href = None
            self._link_text = []
        if tag in {"th", "td"} and self._table_depth == 1 and self._cell is not None and self._row is not None:
            self._row.append(" ".join(" ".join(self._cell).split()))
            self._cell = None
        if tag == "tr" and self._table_depth == 1 and self._row is not None and self._table is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        if tag == "table":
            if self._table_depth == 1 and self._table is not None:
                self.tables.append(self._table)
                self._table = None
            self._table_depth -= 1

    def handle_data(self, data: str) -> None:
        clean = unescape(data)
        if clean.strip():
            self.text_parts.append(clean)
            if self._href is not None:
                self._link_text.append(clean)
            if self._cell is not None:
                self._cell.append(clean)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.text_parts).split())


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_page(raw: bytes) -> PageParser:
    parser = PageParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return parser


def fetch(url: str) -> bytes:
    delay = 1
    for attempt in range(1, 7):
        try:
            request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
            with urlopen(request, timeout=60) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code != 429 or attempt == 6:
                raise
            time.sleep(delay * 5)
            delay += 1
    raise RuntimeError("unreachable NIST source retry boundary")


def detail_identity(url: str) -> tuple[str, str]:
    query = parse_qs(urlparse(url).query)
    casno = query.get("casno", [""])[0]
    torsion_index = query.get("ti", [""])[0]
    if not casno.isdigit() or not torsion_index.isdigit() or int(torsion_index) < 1:
        raise ValueError(f"KIN-004 detail identity changed: {url}")
    return casno, torsion_index


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("KIN-004 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    source = spec["sources"][0]
    if (
        spec.get("schema") != "sft-v3-activation-barrier-prefetch-capture-spec/1"
        or spec.get("all_species_path_state_barrier_unit_uncertainty_method_reference_note_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_average_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 1
    ):
        raise ValueError("KIN-004 prefetch boundary is not value-free and complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    index_raw = INDEX_PATH.read_bytes() if INDEX_PATH.exists() else fetch(source["index_url"])
    INDEX_PATH.write_bytes(index_raw)
    index = parse_page(index_raw)
    if "Experimental Barriers to Internal Rotation" not in index.text or "Release 22 (May 2022)" not in index.text:
        raise ValueError("KIN-004 NIST collection identity changed")
    index_details = [link for link in index.links if "exprotbar2x.asp" in link["href"]]
    if not index_details:
        raise ValueError("KIN-004 NIST collection has no detail identities")
    formula_rows: dict[str, str] = {}
    for table in index.tables:
        for row in table:
            if len(row) == 2 and row[0] and row[1] and row[1] in {link["text"] for link in index_details}:
                formula_rows[row[1]] = row[0]

    base_url = source["index_url"]
    queue: list[dict[str, str]] = []
    for link in index_details:
        queue.append({
            "url": urljoin(base_url, link["href"]), "species_name": link["text"],
            "formula_external_inscription": formula_rows.get(link["text"], "structural-source-formula"),
        })
    seen: set[str] = set()
    page_records: list[dict] = []
    identities: list[dict] = []
    targets: list[dict] = []
    unresolved_path_rows: list[dict] = []
    while queue:
        queued = queue.pop(0)
        url = queued["url"]
        if url in seen:
            continue
        seen.add(url)
        casno, _query_torsion_index = detail_identity(url)
        page_ordinal = len(page_records) + 1
        snapshot_name = f"detail-{page_ordinal:04d}-cas-{casno}.html"
        snapshot_path = SNAPSHOT_ROOT / snapshot_name
        snapshot_cached = snapshot_path.exists()
        raw = snapshot_path.read_bytes() if snapshot_cached else fetch(url)
        page = parse_page(raw)
        if "Experimental Barriers to Internal Rotation for" not in page.text:
            raise ValueError(f"KIN-004 detail page identity changed: {url}")
        grid_tables = [
            table for table in page.tables
            if table and len(table[0]) >= 4 and table[0][0:2] == ["torsion index", "Angle"]
        ]
        if len(grid_tables) != 1:
            raise ValueError(f"KIN-004 detail page grid count changed: {url}")
        rows = grid_tables[0][1:]
        if not rows or any(len(row) < 4 for row in rows):
            raise ValueError(f"KIN-004 incomplete path grid: {url}")
        source_match = re.search(r"Data from:\s*(.*?)\s*torsion index", page.text)
        source_reference_record = " ".join(source_match.group(1).split()) if source_match else "EmptyOne"
        source_reference_identity = source_reference_record.split(maxsplit=1)[0] if source_match else "EmptyOne"
        snapshot_path.write_bytes(raw)
        torsion_indices = tuple(dict.fromkeys(row[0] for row in rows))
        page_state_count = 0
        page_target_count = 0
        for torsion_index in torsion_indices:
            torsion_rows = [row for row in rows if row[0] == torsion_index]
            normalized_states = []
            positive_barriers: list[tuple[Fraction, str]] = []
            positive_wavenumbers: list[tuple[Fraction, str]] = []
            external_zero_count = 0
            for state_ordinal, row in enumerate(torsion_rows, start=1):
                angle, energy_kj, energy_cm = row[1], row[2], row[3]
                if not energy_kj and not energy_cm:
                    normalized_states.append({
                        "source_state_ordinal": state_ordinal,
                        "external_angle_state_label": angle,
                        "energy_kJ_mol_minus1_external_inscription": "EmptyOne",
                        "energy_kJ_mol_minus1_fold_support": "EmptyOne",
                        "energy_cm_minus1_external_inscription": "EmptyOne",
                        "energy_cm_minus1_fold_support": "EmptyOne",
                        "source_value_status": "unreported",
                    })
                    continue
                energy_kj_value = Fraction(energy_kj)
                energy_cm_value = Fraction(energy_cm)
                if energy_kj_value < 0 or energy_cm_value < 0:
                    raise ValueError("KIN-004 negative external path displacement is outside the registered surface")
                if energy_kj_value == 0:
                    external_zero_count += 1
                    normalized_kj = "EmptyOne"
                else:
                    positive_barriers.append((energy_kj_value, energy_kj))
                    normalized_kj = energy_kj
                if energy_cm_value == 0:
                    normalized_cm = "EmptyOne"
                else:
                    positive_wavenumbers.append((energy_cm_value, energy_cm))
                    normalized_cm = energy_cm
                normalized_states.append({
                    "source_state_ordinal": state_ordinal,
                    "external_angle_state_label": angle,
                    "energy_kJ_mol_minus1_external_inscription": energy_kj,
                    "energy_kJ_mol_minus1_fold_support": normalized_kj,
                    "energy_cm_minus1_external_inscription": energy_cm,
                    "energy_cm_minus1_fold_support": normalized_cm,
                })
            if not positive_barriers or not positive_wavenumbers:
                unresolved_path_rows.append({
                    "source_detail_ordinal": page_ordinal,
                    "species_name": queued["species_name"],
                    "formula_external_inscription": queued["formula_external_inscription"],
                    "casno_source_identity": casno,
                    "torsion_index_source_identity": torsion_index,
                    "complete_source_ordered_path_states": normalized_states,
                    "unresolved_reason": "source row contains no reported positive barrier support",
                })
                page_state_count += len(normalized_states)
                continue
            barrier_fraction, barrier_inscription = max(positive_barriers, key=lambda pair: pair[0])
            wavenumber_fraction, wavenumber_inscription = max(positive_wavenumbers, key=lambda pair: pair[0])
            path_match = re.search(
                rf"Atoms in torsion {re.escape(torsion_index)} are ([0-9, ]+)\s+The rotor type is (.*?)"
                rf"(?=\s+Atoms in torsion \d+ are|\s+Image:|\s+Got a better number|$)",
                page.text,
            )
            if not path_match:
                raise ValueError(f"KIN-004 path atoms or rotor changed: {url} torsion {torsion_index}")
            atoms = " ".join(path_match.group(1).split())
            rotor = " ".join(path_match.group(2).split())
            target_id = f"SFT-CHEM-KIN-004-BARRIER-{len(targets) + 1:04d}"
            identity = {
                "target_id": target_id,
                "source_id": source["source_id"],
                "source_detail_ordinal": page_ordinal,
                "species_name": queued["species_name"],
                "formula_external_inscription": queued["formula_external_inscription"],
                "casno_source_identity": casno,
                "torsion_index_source_identity": torsion_index,
                "torsion_atom_identity": atoms,
                "rotor_type_identity": rotor,
                "source_reference_identity": source_reference_identity,
                "all_barrier_unit_uncertainty_method_note_and_target_hash_values_absent": True,
            }
            target = {
                **identity,
                "detail_url": url,
                "snapshot_path": str(snapshot_path.relative_to(ROOT)),
                "snapshot_hash": sha_file(snapshot_path),
                "complete_path_state_count": len(normalized_states),
                "complete_source_ordered_path_states": normalized_states,
                "barrier_kJ_mol_minus1_external_inscription": barrier_inscription,
                "barrier_kJ_mol_minus1_exact_fraction": f"{barrier_fraction.numerator}/{barrier_fraction.denominator}",
                "barrier_cm_minus1_external_inscription": wavenumber_inscription,
                "barrier_cm_minus1_exact_fraction": f"{wavenumber_fraction.numerator}/{wavenumber_fraction.denominator}",
                "external_zero_energy_glyph_count_translated_to_EmptyOne": external_zero_count,
                "source_least_state_support": (
                    "explicit-external-zero-glyph-translated-to-EmptyOne"
                    if external_zero_count else "source-least-state-coordinate-absent-as-EmptyOne"
                ),
                "uncertainty_support": "EmptyOne",
                "measurement_method_support": "EmptyOne",
                "source_status": "NIST CCCBDB experimental barrier collection with complete cited-source identity",
                "complete_source_reference_record": source_reference_record,
                "fitted_barrier_or_absolute_energy_origin_used_in_fold_law": False,
            }
            identities.append(identity)
            targets.append(target)
            page_state_count += len(normalized_states)
            page_target_count += 1
        page_records.append({
            "source_detail_ordinal": page_ordinal,
            "detail_url": url, "snapshot_path": str(snapshot_path.relative_to(ROOT)),
            "snapshot_hash": sha_file(snapshot_path), "species_name": queued["species_name"],
            "formula_external_inscription": queued["formula_external_inscription"],
            "casno_source_identity": casno, "torsion_indices": list(torsion_indices),
            "complete_torsion_target_count": page_target_count,
            "complete_path_state_count": page_state_count,
            "source_reference_identity": source_reference_identity,
            "complete_source_reference_record": source_reference_record,
        })
        for link in page.links:
            if "exprotbar2x.asp" not in link["href"]:
                continue
            linked_url = urljoin(url, link["href"])
            linked_cas, _ = detail_identity(linked_url)
            if linked_cas == casno and linked_url not in seen and all(row["url"] != linked_url for row in queue):
                queue.append({
                    "url": linked_url, "species_name": queued["species_name"],
                    "formula_external_inscription": queued["formula_external_inscription"],
                })
        if not snapshot_cached:
            time.sleep(1)

    if len({row["casno_source_identity"] for row in identities}) != len(index_details):
        raise ValueError("KIN-004 did not preserve every index-listed species")
    identity_doc = {
        "schema": "sft-v3-activation-barrier-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_index_species_count": len(index_details),
        "complete_detail_target_count": len(identities),
        "all_species_path_state_identities_retained": True,
        "all_barrier_unit_uncertainty_method_note_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-activation-barrier-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_index_species_count": len(index_details),
        "complete_detail_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-activation-barrier-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": source["source_id"],
        "database_release_identity": source["database_release_identity"],
        "complete_index_url": source["index_url"],
        "complete_index_snapshot_path": str(INDEX_PATH.relative_to(ROOT)),
        "complete_index_snapshot_hash": sha_file(INDEX_PATH),
        "complete_index_species_count": len(index_details),
        "complete_detail_target_count": len(targets),
        "complete_detail_pages": page_records,
        "complete_path_state_count": sum(row["complete_path_state_count"] for row in page_records),
        "complete_unresolved_path_row_count": len(unresolved_path_rows),
        "complete_unresolved_path_rows": unresolved_path_rows,
        "complete_external_zero_energy_glyph_count_translated_to_EmptyOne": sum(
            row["external_zero_energy_glyph_count_translated_to_EmptyOne"] for row in targets
        ),
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_index_species_detail_pages_path_states_references_values_and_absences_preserved": True,
        "transition_state_saddle_continuum_arrhenius_prefactor_fitted_activation_absolute_origin_selection_average_or_target_correction_used_in_law": False,
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "complete_index_species_count": len(index_details),
        "complete_detail_target_count": len(targets),
        "complete_path_state_count": sum(row["complete_path_state_count"] for row in page_records),
        "index_hash": sha_file(INDEX_PATH),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
