#!/usr/bin/env python3
"""Build the complete post-seal ORG-006 external vector without selecting the Fold law."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402

CLAIM_ID = "SFT-CHEM-CONFORMER-POPULATION-ORDERING-006"
IDENTITY_OUTPUT = ROOT / "experiments/external_sources/chemistry/org_006_complete_target_identities_v1.json"
TARGET_OUTPUT = ROOT / "experiments/external_sources/chemistry/org_006_complete_targets_v1.json"
PRIMARY_OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-core-direct-v5/org-006-primary-record-v1.json"

IDENTITY_DOCUMENTS = (
    ("experiments/external_sources/chemistry/org_006_target_identities_v1.json", "sha256:36643ce7da55fd4a59881b2af84ae5e750efc9e37583334617f34ac688fb2d4a"),
    ("experiments/external_sources/chemistry/org_006_target_identity_addendum_v2.json", "sha256:57d621771714955e5ba9b161526aecf9df27dc2b1ad1a3eedad8f6148d590a80"),
    ("experiments/external_sources/chemistry/org_006_target_identity_addendum_v3.json", "sha256:9021001e93242e5b00dc5b3f843264d6e272974886710b844d1791a41e2a6839"),
    ("experiments/external_sources/chemistry/org_006_target_identity_addendum_v4.json", "sha256:a395cfb5428b665fd430e08dc7351f66f14f0b62d083eb9faad02f74989aadb2"),
    ("experiments/external_sources/chemistry/org_006_target_identity_addendum_v5.json", "sha256:ca55055db1a974973131a5fc18fdafcde47e4e3218f32a2c27e2ee5f9762912d"),
)
V1_INVENTORY = ("experiments/external_sources/chemistry/snapshots/org-006-blind-v1/source-inventory-v1.json", "sha256:6b3fbef19c0bdf233691edcb5cf74856626d273338910ec76becbe313d1f6c31")
V2_INVENTORY = ("experiments/external_sources/chemistry/snapshots/org-006-value-blind-v2/source-inventory-v2.json", "sha256:7030ee5cd2c738d0f89b849626517432e1ced739b15e26556e5f4c4fb2601fe1")
V3_FAILURE = ("experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-v3/failure-inventory-v3.json", "sha256:08d5cfe81d3fc9b6180103316ece4c0780137b40782578fc12258a4b8b10b853")
V4_INVENTORY = ("experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-file-v4/source-inventory-v4.json", "sha256:0b54ce16024ab5646e8498b9bad65aec864c85ec281a3c85035aead2cfe61d0e")
V5_INVENTORY = ("experiments/external_sources/chemistry/snapshots/org-006-core-direct-v5/source-inventory-v5.json", "sha256:0449436d7ea623f79460d4288cfcbcf7bb966ccdd38b5e90e6844779ebcb2350")
SI_PATH = "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-file-v4/jp404315t_si_001.txt"
SI_HASH = "sha256:63d94c807b2068d667de729503eaa1953829cfe27f86d3bb002b3bdba2b80213"
PDF_PATH = "experiments/external_sources/chemistry/snapshots/org-006-core-direct-v5/core-43583184-route-02.pdf"
PDF_HASH = "sha256:97229c4b4ac1870faec3542817397009ac61f749feb7982baa361fdf9c0f65a4"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._depth = 0
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.casefold()
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._table = []
        elif self._depth == 1 and tag == "tr":
            self._row = []
        elif self._depth == 1 and tag in {"td", "th"}:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if self._depth == 1 and tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", " ".join(self._cell)).strip())
            self._cell = None
        elif self._depth == 1 and tag == "tr" and self._row is not None and self._table is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._depth:
            if self._depth == 1 and self._table is not None:
                self.tables.append(self._table)
                self._table = None
            self._depth -= 1


def html_surface(path: str) -> dict:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8", errors="replace")
    parser = TableParser(); parser.feed(text)
    return {
        "snapshot_path": path,
        "snapshot_sha256": hash_file(file_path),
        "snapshot_bytes": file_path.stat().st_size,
        "complete_table_count": len(parser.tables),
        "complete_row_count": sum(len(table) for table in parser.tables),
        "complete_tables": parser.tables,
        "complete_text_contains_lost_molecule": "lost your molecule" in text.casefold(),
    }


def si_tables() -> tuple[dict, ...]:
    text = (ROOT / SI_PATH).read_text(encoding="utf-8")
    lines = text.splitlines()
    medium = molecule = None
    tables: list[dict] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.casefold().startswith("dipoler couplings from"):
            medium = stripped
        elif re.match(r"^(ethane|propane|n-butane|1,3,5-trichlorobenzene) in ", stripped, re.I):
            molecule = stripped
        elif re.match(r"^T\s+D", stripped):
            header = stripped.split()
            rows = []
            cursor = index + 1
            while cursor < len(lines):
                row = lines[cursor].strip()
                if not row:
                    if rows:
                        break
                    cursor += 1
                    continue
                cells = row.split()
                if not re.fullmatch(r"\d+(?:\.\d+)?", cells[0]):
                    break
                rows.append(cells)
                cursor += 1
            tables.append({"medium": medium, "molecule": molecule, "header": header, "rows": rows})
            index = cursor - 1
        index += 1
    return tuple(tables)


def pdf_postseal_facts() -> dict:
    path = ROOT / PDF_PATH
    reader = PdfReader(path)
    page_text = tuple((page.extract_text() or "") for page in reader.pages)
    complete = "\n".join(page_text)
    required = (
        "441±114 cal mol−1", "−1.9±0.3 cal K−1 mol−1", "tt (0 .33± 0.03 [0.30])",
        "tg (0.51± 0.01 [0.54])", "pm (0.02±0.01 [0.005])", "pp (0.14±0.01 [0.16])",
        "Ei nt tg = 480 cal mol−1", "Ei nt pm = 3263 cal mol−1", "Ei nt pp = 658 cal mol−1",
    )
    missing = [value for value in required if value not in complete]
    if missing:
        raise ValueError(f"ORG-006 PDF extraction changed: {missing}")
    return {
        "pdf_page_count": len(reader.pages),
        "pdf_snapshot_path": PDF_PATH,
        "pdf_snapshot_sha256": hash_file(path),
        "measured_spectrum_count": 22,
        "measured_1132_spectrum_count": 16,
        "measured_5CB_spectrum_count": 6,
        "external_condition": "298.5 K",
        "ordered_population_vector": {"tt": "0.33 ± 0.03", "tg": "0.51 ± 0.01", "pm": "0.02 ± 0.01", "pp": "0.14 ± 0.01"},
        "isotropic_population_vector": {"tt": "0.30", "tg": "0.54", "pm": "0.005", "pp": "0.16"},
        "ordered_population_exact_display_fractions": {"tt": "33/100", "tg": "51/100", "pm": "1/50", "pp": "7/50"},
        "ordered_population_exact_display_sum": "1/1",
        "isotropic_population_exact_display_sum": "201/200",
        "isotropic_display_rounding_adverse_row_preserved": True,
        "ordered_population_order": ["tg", "tt", "pp", "pm"],
        "isotropic_population_order": ["tg", "tt", "pp", "pm"],
        "intramolecular_energy_cal_per_mol": {"tt_reference": "external conventional 0", "tg": "480", "pp": "658", "pm": "3263"},
        "fold_positive_energy_order": ["tt-structural-reference-EmptyOne", "tg-480", "pp-658", "pm-3263"],
        "fold_positive_energy_gaps": ["480", "178", "2605"],
        "Etg_300_cal_per_mol": "441 ± 114",
        "Etg_temperature_variation_cal_per_K_per_mol": "-1.9 ± 0.3",
        "all_external_signed_strings_retained_downstream": True,
    }


def main() -> None:
    if IDENTITY_OUTPUT.exists() or TARGET_OUTPUT.exists() or PRIMARY_OUTPUT.exists():
        raise SystemExit("ORG-006 complete external artifacts already exist; preserved without regeneration")
    identities = []
    for path, expected in IDENTITY_DOCUMENTS:
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-006 identity changed: {path}")
        identities.extend(json.loads((ROOT / path).read_text(encoding="utf-8"))["rows"])
    if len(identities) != 14 or [row["target_id"] for row in identities] != [f"SFT-CHEM-ORG-006-{n:03d}" for n in range(1, 15)]:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 complete target identity order changed")
    identity_document = {
        "schema": "sft-v3-composed-value-free-target-identities/1", "claim_id": CLAIM_ID,
        "preserved_identity_documents": [list(row) for row in IDENTITY_DOCUMENTS],
        "complete_registered_target_count": 14, "rows": identities,
        "external_values_or_outcomes_used_to_select_identity": False,
    }
    IDENTITY_OUTPUT.write_text(json.dumps(identity_document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    for path, expected in (V1_INVENTORY, V2_INVENTORY, V3_FAILURE, V4_INVENTORY, V5_INVENTORY):
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-006 capture changed: {path}")
    if hash_file(ROOT / SI_PATH) != SI_HASH or hash_file(ROOT / PDF_PATH) != PDF_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 quantitative source changed")
    v1 = json.loads((ROOT / V1_INVENTORY[0]).read_text()); v2 = json.loads((ROOT / V2_INVENTORY[0]).read_text())
    v3 = json.loads((ROOT / V3_FAILURE[0]).read_text()); v4 = json.loads((ROOT / V4_INVENTORY[0]).read_text()); v5 = json.loads((ROOT / V5_INVENTORY[0]).read_text())
    family = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1"
    source_outcomes = (
        {"complete_term_record": json.loads((family / "iupac-c01262.json").read_text())},
        {"complete_term_record": json.loads((family / "iupac-c01259.json").read_text())},
        {"complete_term_record": json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/goldbook-terms/CT01038.json").read_text())},
        {"complete_nist_surface": html_surface("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/nist-cccbdb-106978-neutral-experimental.html")},
        {"complete_nist_surface": html_surface("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/nist-cccbdb-106978-internal-rotation.html")},
        {"complete_blind_capture": v1["rows"][0]}, {"complete_blind_capture": v1["rows"][1]}, {"complete_blind_capture": v1["rows"][2]},
        {"complete_source_group": v2["rows"][0]}, {"complete_source_group": v2["rows"][1]},
        {"complete_method_failure_and_metadata": v3},
        {"complete_acs_supporting_file": {"capture_inventory": v4, "measurement_tables": si_tables()}},
        {"complete_core_route": v5["captures"][0]},
        {"complete_core_route_and_quantitative_facts": {"capture": v5["captures"][1], "postseal_facts": pdf_postseal_facts()}},
    )
    opened = (
        (identities[0]["snapshot_path"], identities[0]["snapshot_sha256"]), (identities[1]["snapshot_path"], identities[1]["snapshot_sha256"]),
        (identities[2]["snapshot_path"], identities[2]["snapshot_sha256"]), (identities[3]["snapshot_path"], identities[3]["snapshot_sha256"]),
        (identities[4]["snapshot_path"], identities[4]["snapshot_sha256"]),
        *((row["snapshot_path"], row["snapshot_sha256"]) for row in v1["rows"]),
        (V2_INVENTORY[0], V2_INVENTORY[1]), (V2_INVENTORY[0], V2_INVENTORY[1]), (V3_FAILURE[0], V3_FAILURE[1]),
        (V4_INVENTORY[0], V4_INVENTORY[1]), (V5_INVENTORY[0], V5_INVENTORY[1]), (V5_INVENTORY[0], V5_INVENTORY[1]),
    )
    target_rows = []
    identity_keys = ("target_id", "source_record_ordinal", "source_id", "authority", "registered_identity", "source_record_role", "custody_class")
    for identity, outcome, (opened_path, opened_hash) in zip(identities, source_outcomes, opened):
        row = {key: identity[key] for key in identity_keys}
        row.update({"opened_snapshot_path": opened_path, "opened_snapshot_sha256": opened_hash, "source_outcome": outcome})
        row["target_payload_hash"] = sha256_identity((identity["target_id"], identity["source_record_role"], outcome))
        target_rows.append(row)
    target_document = {
        "schema": "sft-v3-complete-opened-target-vector/1", "claim_id": CLAIM_ID,
        "identity_registry": [str(IDENTITY_OUTPUT.relative_to(ROOT)), hash_file(IDENTITY_OUTPUT)],
        "complete_registered_target_count": 14, "rows": target_rows,
        "all_favourable_adverse_absent_unavailable_unresolved_signed_and_rounded_rows_preserved": True,
        "unknown_target_value_blind_rows_present": True, "source_recapture_count": 0,
    }
    TARGET_OUTPUT.write_text(json.dumps(target_document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    si = si_tables(); facts = pdf_postseal_facts()
    analysis = {
        "schema": "sft-v3-postseal-primary-analysis/1", "claim_id": CLAIM_ID,
        "complete_target_count": 14, "complete_target_vector_hash": sha256_identity(tuple(row["target_payload_hash"] for row in target_rows)),
        "blind_quantitative_pdf_obtained": True, "blind_quantitative_supporting_file_obtained": True,
        "acs_supporting_measurement_table_count": len(si), "acs_supporting_measurement_row_count": sum(len(table["rows"]) for table in si),
        "population_condition": facts["external_condition"], "ordered_population_vector": facts["ordered_population_vector"],
        "ordered_population_exact_display_fractions": facts["ordered_population_exact_display_fractions"],
        "ordered_population_exact_display_sum": facts["ordered_population_exact_display_sum"],
        "ordered_population_order": facts["ordered_population_order"], "isotropic_population_vector": facts["isotropic_population_vector"],
        "isotropic_population_order": facts["isotropic_population_order"], "isotropic_population_exact_display_sum": facts["isotropic_population_exact_display_sum"],
        "isotropic_display_rounding_adverse_row_preserved": True, "fold_positive_energy_order": facts["fold_positive_energy_order"],
        "fold_positive_energy_gaps": facts["fold_positive_energy_gaps"], "Etg_300_cal_per_mol": facts["Etg_300_cal_per_mol"],
        "Etg_temperature_variation_cal_per_K_per_mol": facts["Etg_temperature_variation_cal_per_K_per_mol"],
        "condition_and_observation_timescale_retained": True,
        "external_signed_decimal_zero_negative_and_rounded_strings_are_downstream_only": True,
        "all_predecessor_failures_and_adverse_results_preserved": True,
    }
    PRIMARY_OUTPUT.write_text(json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(IDENTITY_OUTPUT.relative_to(ROOT), hash_file(IDENTITY_OUTPUT))
    print(TARGET_OUTPUT.relative_to(ROOT), hash_file(TARGET_OUTPUT))
    print(PRIMARY_OUTPUT.relative_to(ROOT), hash_file(PRIMARY_OUTPUT))
    print("targets", len(target_rows), "si tables", len(si), "si rows", sum(len(table["rows"]) for table in si))


if __name__ == "__main__":
    main()
