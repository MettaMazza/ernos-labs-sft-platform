#!/usr/bin/env python3
"""Build the complete post-seal KIN-008 evidence ledger from byte-bound sources."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-008-parallel-mechanism-v1"
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/parallel_mechanism_capture_spec_v1.json"
SPEC_HASH = "sha256:f32b98d3cc4f02c02f01249b0f92ce799d1453ae04d1f8c9c107be6a509a6e89"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:a3c79878aeb0383a64d8bcf9242e9865c791c872ac50f59692348b978cead0d0"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/parallel_mechanism_target_identities_v1.json"
IDENTITY_HASH = "sha256:08d42e20f3e4fa66ff46f98d046e160e5a7375b32f7d6d036debddfe3f1b90ca"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/parallel_mechanism_withheld_targets_v1.json"
TARGET_HASH = "sha256:da263dc7147b66565c6737be47f492fb0c585c6048db078b17f643e037c78443"
PRIMARY_PATH = SNAPSHOT_ROOT / "parallel-mechanism-primary-records-v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def cells_by_coordinate(row: dict) -> dict[str, dict]:
    return {cell["cell_coordinate"]: cell for cell in row["complete_rectangular_cells"]}


def source_label(cell: dict) -> str:
    if cell.get("source_value_class") != "held-source-label":
        raise ValueError("KIN-008 expected a held source label")
    return str(cell["source_label"])


def source_identifier(cell: dict) -> str:
    if cell.get("source_value_class") == "held-source-label":
        return str(cell["source_label"])
    if cell.get("source_value_class") == "exact-positive-observed-magnitude":
        return str(cell["source_numeric_inscription"])
    raise ValueError("KIN-008 expected a held or positive source identifier")


def positive_fraction(cell: dict) -> Fraction:
    if cell.get("source_value_class") != "exact-positive-observed-magnitude":
        raise ValueError("KIN-008 expected an exact positive source magnitude")
    return Fraction(str(cell["exact_positive_fraction"]))


def main() -> None:
    for path, expected in (
        (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH),
        (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"KIN-008 sealed evidence changed: {path}")
    inventory = json.loads(INVENTORY_PATH.read_text())
    targets = json.loads(TARGET_PATH.read_text())
    rows = tuple(targets.get("rows", ()))
    if (
        targets.get("complete_registered_target_count") != 28
        or targets.get("complete_registered_rectangular_cell_position_count") != 18158
        or len(rows) != 28
    ):
        raise ValueError("KIN-008 complete workbook target census changed")
    by_sheet = {row["source_sheet_identity"]: row for row in rows}
    if len(by_sheet) != 28:
        raise ValueError("KIN-008 duplicated a source-data worksheet")

    fig4 = cells_by_coordinate(by_sheet["Fig.4b"])
    fig4_times = tuple(positive_fraction(fig4[f"B{row}"]) for row in range(4, 11))
    fig4_products = tuple(source_identifier(fig4[f"{column}3"]) for column in "CDEFG")
    fig4_raw = tuple(fig4[f"{column}{row}"] for row in range(4, 11) for column in "CDEFGHIJKLMNOPQ")
    fig4_formula_columns = ("R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA")
    fig4_formulas = tuple(fig4[f"{column}{row}"] for row in range(4, 11) for column in fig4_formula_columns)
    if len(fig4_times) != 7 or len(fig4_products) != 5 or len(fig4_raw) != 105 or len(fig4_formulas) != 70:
        raise ValueError("KIN-008 Figure 4b complete product-time surface changed")

    supp32 = cells_by_coordinate(by_sheet["Supplementary Fig.32"])
    supp32_times = tuple(positive_fraction(supp32[f"E{row}"]) for row in range(6, 16))
    supp32_products = tuple(source_identifier(supp32[f"{column}5"]) for column in "FGHIJKL")
    supp32_raw = tuple(supp32[f"{column}{row}"] for row in range(6, 16) for column in "FGHIJKL")
    if len(supp32_times) != 10 or len(supp32_products) != 7 or len(supp32_raw) != 70:
        raise ValueError("KIN-008 Supplementary Figure 32 complete product-time surface changed")

    fig5 = cells_by_coordinate(by_sheet["Fig.5c"])
    fig5_times = tuple(positive_fraction(fig5[f"B{row}"]) for row in range(4, 14))
    fig5_products = tuple(source_identifier(fig5[f"{column}3"]) for column in "CDEFGHI")
    fig5_raw = tuple(fig5[f"{column}{row}"] for row in range(4, 14) for column in "CDEFGHIJKLMNOPQRSTUVW")
    fig5_formulas = tuple(fig5[f"{column}{row}"] for row in range(4, 14) for column in ("X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK"))
    if len(fig5_times) != 10 or len(fig5_products) != 7 or len(fig5_raw) != 210 or len(fig5_formulas) != 140:
        raise ValueError("KIN-008 Figure 5c complete product-time surface changed")

    article_pdf = SNAPSHOT_ROOT / "article.pdf"
    supplement_pdf = SNAPSHOT_ROOT / "supplementary-information.pdf"
    peer_pdf = SNAPSHOT_ROOT / "transparent-peer-review.pdf"
    article_reader = PdfReader(article_pdf)
    supplement_reader = PdfReader(supplement_pdf)
    peer_reader = PdfReader(peer_pdf)
    article_page_seven = article_reader.pages[6].extract_text() or ""
    supplement_page_forty_nine = supplement_reader.pages[48].extract_text() or ""
    supplement_page_fifty = supplement_reader.pages[49].extract_text() or ""
    required = (
        "Temporal programming of competing cascade reactions",
        "Reaction network showing multiple competing pathways",
        "Supplementary Fig. 31",
        "two possible structures",
        "Supplementary Fig. 32",
        "subsequent conversion to 9 followed by hydrolysis to give 2",
    )
    combined = " ".join("\n".join((article_page_seven, supplement_page_forty_nine, supplement_page_fifty)).split())
    if any(fragment not in combined for fragment in required):
        raise ValueError("KIN-008 primary parallel-path or unresolved disclosure changed")

    path_family = (
        {
            "path_row": 1,
            "path_identity": "hydrolysis-then-click",
            "ordered_state_word": ["1-EP", "1", "2"],
            "path_status": "experimentally-retained-parallel-path",
        },
        {
            "path_row": 2,
            "path_identity": "two-acyl-transfers-then-click-and-hydrolysis",
            "ordered_state_word": ["1-EP", "7", "8", "9", "2"],
            "path_status": "experimentally-retained-parallel-path",
        },
        {
            "path_row": 3,
            "path_identity": "direct-click-then-hydrolysis-trace-path",
            "ordered_state_word": ["1-EP", "2-EP", "2"],
            "path_status": "weak-trace-path-retained-from-complete-product-vector",
        },
    )
    if {state for path in path_family for state in path["ordered_state_word"]} != set(supp32_products):
        raise ValueError("KIN-008 complete path family does not cover every Supplementary Figure 32 product identity")

    primary = {
        "schema": "sft-v3-parallel-mechanism-primary-records/1",
        "claim_id": "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-008",
        "article_doi": "10.1038/s41467-026-70199-4",
        "prefetch_spec_hash": SPEC_HASH,
        "source_inventory_hash": INVENTORY_HASH,
        "identity_registry_hash": IDENTITY_HASH,
        "withheld_target_registry_hash": TARGET_HASH,
        "complete_source_file_count": inventory["complete_source_file_count"],
        "complete_source_files": inventory["complete_source_files"],
        "article_page_count": len(article_reader.pages),
        "supplementary_information_page_count": len(supplement_reader.pages),
        "transparent_peer_review_page_count": len(peer_reader.pages),
        "complete_source_data_worksheet_count": len(rows),
        "complete_registered_rectangular_cell_position_count": targets["complete_registered_rectangular_cell_position_count"],
        "complete_cell_class_census": targets["complete_cell_class_census"],
        "complete_parallel_path_family": path_family,
        "parallel_path_count": len(path_family),
        "common_initial_state_identity": "1-EP",
        "common_terminal_state_identity": "2",
        "all_seven_supplementary_product_identities_covered_by_path_family": True,
        "figure_4b_complete_vector": {
            "time_count": len(fig4_times), "product_count": len(fig4_products), "replicate_count": 3,
            "raw_product_time_observation_count": len(fig4_raw), "source_formula_count": len(fig4_formulas),
            "exact_time_fraction_word": [str(value) for value in fig4_times], "product_identity_word": fig4_products,
        },
        "supplementary_figure_32_complete_vector": {
            "time_count": len(supp32_times), "product_count": len(supp32_products),
            "raw_product_time_observation_count": len(supp32_raw),
            "exact_time_fraction_word": [str(value) for value in supp32_times], "product_identity_word": supp32_products,
        },
        "figure_5c_complete_adverse_comparator_vector": {
            "time_count": len(fig5_times), "product_count": len(fig5_products), "replicate_count": 3,
            "raw_product_time_observation_count": len(fig5_raw), "source_formula_count": len(fig5_formulas),
            "exact_time_fraction_word": [str(value) for value in fig5_times], "product_identity_word": fig5_products,
        },
        "complete_primary_parallel_product_time_observation_count": len(fig4_raw) + len(supp32_raw) + len(fig5_raw),
        "complete_primary_source_formula_count": len(fig4_formulas) + len(fig5_formulas),
        "unresolved_source_disclosure": {
            "source_identity": "Supplementary Figure 31 peak x",
            "assignment_status": "two possible structures retained; no preferred structure selected",
            "maximum_extent_external_inscription_mM": "approximately 0.4",
            "exact_positive_reported_magnitude_fraction": "2/5",
            "used_as_fold_proof_parameter": False,
        },
        "source_formulas_retained_as_provenance_and_never_used_as_fold_proof_parameters": True,
        "imported_parallel_reaction_equation_stochastic_premise_fitted_path_weight_steady_state_selection_average_interpolation_or_target_correction_used_in_law": False,
        "external_values_used_as_proof_parameters": False,
        "external_zero_glyphs_translate_only_to_structural_EmptyOne": True,
        "all_weak_adverse_unresolved_unassigned_formula_and_empty_cells_preserved": True,
    }
    PRIMARY_PATH.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "primary_hash": sha_file(PRIMARY_PATH),
        "parallel_path_count": len(path_family),
        "complete_primary_parallel_product_time_observation_count": primary["complete_primary_parallel_product_time_observation_count"],
        "complete_source_data_worksheet_count": len(rows),
    }, indent=2))


if __name__ == "__main__":
    main()
