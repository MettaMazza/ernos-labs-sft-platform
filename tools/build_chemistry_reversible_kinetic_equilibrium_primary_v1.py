#!/usr/bin/env python3
"""Build the complete post-seal KIN-009 reversible/equilibrium evidence ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-009-reversible-kinetic-equilibrium-v1"
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:cc936c64ac170830e26ec3fece37d246511b5e76e895c90db82ccaca4a5d3152"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:5d7c24d3d62d2b3217a62e7e3f34be9e7425c2d5a3f65ed6acb7b7a404542722"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_target_identities_v1.json"
IDENTITY_HASH = "sha256:512caad8d5b26bd6da8ac04ca0a9f8b68f2700f8d83444bb1abbfc457ac9a720"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_withheld_targets_v1.json"
TARGET_HASH = "sha256:050afd47917ceac491e51e737837e37b89fdf2e57a0a800d6706e073d7e6cf14"
PRIMARY_PATH = SNAPSHOT_ROOT / "reversible-kinetic-equilibrium-primary-records-v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: str) -> str:
    return " ".join(value.replace("–", "-").replace("−", "-").split())


def require_fragments(text: str, fragments: tuple[str, ...], identity: str) -> None:
    for fragment in fragments:
        if normalized(fragment) not in text:
            raise ValueError(f"KIN-009 source fragment changed in {identity}: {fragment}")


def main() -> None:
    for path, expected in (
        (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH),
        (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"KIN-009 sealed evidence changed: {path}")
    inventory = json.loads(INVENTORY_PATH.read_text())
    targets = json.loads(TARGET_PATH.read_text())
    rows = tuple(targets.get("rows", ()))
    if (
        targets.get("complete_registered_target_count") != 164
        or targets.get("complete_pdf_page_target_count") != 155
        or targets.get("complete_supplementary_movie_target_count") != 1
        or targets.get("complete_source_data_archive_member_target_count") != 8
        or len(rows) != 164
    ):
        raise ValueError("KIN-009 complete target census changed")
    pages = {
        (row["source_document_identity"], row["source_page_ordinal"]): normalized(row["target_payload"]["complete_extracted_page_text"])
        for row in rows if row["source_document_identity"].endswith(".pdf")
    }
    p81 = pages[("supplementary-information.pdf", 81)]
    p82 = pages[("supplementary-information.pdf", 82)]
    p83 = pages[("supplementary-information.pdf", 83)]
    p84 = pages[("supplementary-information.pdf", 84)]
    p85 = pages[("supplementary-information.pdf", 85)]
    p86 = pages[("supplementary-information.pdf", 86)]
    p87 = pages[("supplementary-information.pdf", 87)]
    p88 = pages[("supplementary-information.pdf", 88)]
    p89 = pages[("supplementary-information.pdf", 89)]
    require_fragments(p81, ("83% 2-E-II and 17% 2-E-I", "32% 2-E-II and 68% 2-E-I", "88 hours", "G = 0.5 kcal mol"), "SI page 81")
    require_fragments(p82, ("2-E-II to 2-E-I", "slope m = 0.001007", "Gibbs free energy of activation", "25.6 kcal/mol"), "SI page 82")
    require_fragments(p83, ("98% 2-E-I and 2% 2-E-II", "71% 2-E-I and 29% 2-E-II", "82 hours", "G = 0.6 kcal mol"), "SI page 83")
    require_fragments(p84, ("2-E-I to 2-E-II", "slope m = 0. 000691", "Gibbs free energy of activation", "25.9 kcal mol"), "SI page 84")
    require_fragments(p85, ("58% 2-E-I and 42% 2-Z-I", "84% 2-E-I and 16% 2-Z-I", "71 hours", "G = 1.0 kcal/mol"), "SI page 85")
    require_fragments(p86, ("2-E-I to 2-Z-I", "slope m = 0. 003854", "Gibbs free energy of activation", "21.8 kcal mol"), "SI page 86")
    require_fragments(p87, ("61% 2-E-II and 39% 2-Z-II", "80% 2-E-II and 20% 2-Z-II", "71 hours", "G = 0.9 kcal kcal mol"), "SI page 87")
    require_fragments(p88, ("2-E-II to 2-Z-II", "slope m = 0. 005570", "Gibbs free energy of activation", "21.6 kcal mol"), "SI page 88")
    require_fragments(p89, ("Supplementary Table 1", "2-Z-I 21.8", "2-E-II 25.9", "Supplementary Table 2", "2-E-I 0", "2-Z-II 1.4"), "SI page 89")

    bidirectional_pair = {
        "state_pair_identity": ["2-E-I", "2-E-II"],
        "held_condition": "80 degree Celsius in (CDCl2)2 solution; NMR spectra recorded at 25 degree Celsius",
        "directional_records": [
            {
                "direction_identity": "2-E-II-to-2-E-I",
                "initial_support": {"2-E-II": "83/100", "2-E-I": "17/100"},
                "terminal_equilibrium_support": {"2-E-II": "8/25", "2-E-I": "17/25"},
                "elapsed_hour_exact_positive_fraction": "88",
                "reported_fit_slope_external_inscription": "0.001007",
                "reported_fit_slope_exact_positive_fraction": "1007/1000000",
                "reported_pair_energy_difference_exact_positive_fraction_kcal_per_mol": "1/2",
            },
            {
                "direction_identity": "2-E-I-to-2-E-II",
                "initial_support": {"2-E-I": "49/50", "2-E-II": "1/50"},
                "terminal_equilibrium_support": {"2-E-I": "71/100", "2-E-II": "29/100"},
                "elapsed_hour_exact_positive_fraction": "82",
                "reported_fit_slope_external_inscription": "0.000691",
                "reported_fit_slope_exact_positive_fraction": "691/1000000",
                "reported_pair_energy_difference_exact_positive_fraction_kcal_per_mol": "3/5",
            }
        ],
        "equilibrium_disagreement_retained_not_averaged": "68/32 and 71/29 terminal compositions remain separate source observations",
        "same_two_state_graph_observed_from_both_initial_directions": True,
    }
    continuation_pairs = [
        {
            "state_pair_identity": ["2-E-I", "2-Z-I"],
            "held_condition": "40 degree Celsius in (CDCl2)2 solution; NMR spectra recorded at 25 degree Celsius",
            "observed_direction_identity": "2-Z-I-to-2-E-I",
            "source_kinetic_analysis_direction_label": "2-E-I-to-2-Z-I",
            "direction_label_disagreement_retained": True,
            "initial_support": {"2-E-I": "29/50", "2-Z-I": "21/50"},
            "terminal_equilibrium_support": {"2-E-I": "21/25", "2-Z-I": "4/25"},
            "elapsed_hour_exact_positive_fraction": "71",
            "reported_fit_slope_external_inscription": "0.003854",
            "reported_fit_slope_exact_positive_fraction": "1927/500000",
            "reported_pair_energy_difference_exact_positive_fraction_kcal_per_mol": "1",
        },
        {
            "state_pair_identity": ["2-E-II", "2-Z-II"],
            "held_condition": "40 degree Celsius in (CDCl2)2 solution; NMR spectra recorded at 25 degree Celsius",
            "observed_direction_identity": "2-Z-II-to-2-E-II",
            "source_kinetic_analysis_direction_label": "2-E-II-to-2-Z-II",
            "direction_label_disagreement_retained": True,
            "initial_support": {"2-E-II": "61/100", "2-Z-II": "39/100"},
            "terminal_equilibrium_support": {"2-E-II": "4/5", "2-Z-II": "1/5"},
            "elapsed_hour_exact_positive_fraction": "71",
            "reported_fit_slope_external_inscription": "0.005570",
            "reported_fit_slope_exact_positive_fraction": "557/100000",
            "reported_pair_energy_difference_exact_positive_fraction_kcal_per_mol": "9/10",
        },
    ]
    table_one = [
        {"isomer": "2-Z-I", "activation_energy": "109/5", "uncertainty": "3/10"},
        {"isomer": "2-Z-II", "activation_energy": "108/5", "uncertainty": "1/10"},
        {"isomer": "2-E-I", "activation_energy": "128/5", "uncertainty": "1/10"},
        {"isomer": "2-E-II", "activation_energy": "259/10", "uncertainty": "1/10"},
    ]
    table_two = [
        {"isomer": "2-E-I", "external_energy_inscription": "0", "sft_interpretation": "structural-EmptyOne-reference-separation", "uncertainty": "structural-EmptyOne-not-reported"},
        {"isomer": "2-E-II", "energy": "3/5", "uncertainty": "1/5"},
        {"isomer": "2-Z-I", "energy": "1", "uncertainty": "3/10"},
        {"isomer": "2-Z-II", "energy": "7/5", "uncertainty": "3/10"},
    ]
    primary = {
        "schema": "sft-v3-reversible-kinetic-equilibrium-primary-records/1",
        "claim_id": "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-009",
        "article_doi": "10.1038/s41467-023-40190-4",
        "prefetch_spec_hash": SPEC_HASH,
        "source_inventory_hash": INVENTORY_HASH,
        "identity_registry_hash": IDENTITY_HASH,
        "withheld_target_registry_hash": TARGET_HASH,
        "complete_source_file_count": inventory["complete_source_file_count"],
        "complete_registered_target_count": len(rows),
        "complete_pdf_page_target_count": targets["complete_pdf_page_target_count"],
        "complete_supplementary_movie_frame_count": next(row["target_payload"]["frame_count"] for row in rows if row["source_record_class"] == "complete-supplementary-movie"),
        "complete_source_data_archive_member_count": targets["complete_source_data_archive_member_target_count"],
        "bidirectional_same_pair_record": bidirectional_pair,
        "continuation_reversible_pair_records": continuation_pairs,
        "complete_reversible_state_pair_count": 3,
        "complete_directional_experiment_count": 4,
        "complete_terminal_equilibrium_composition_count": 4,
        "supplementary_table_1_activation_energy_vector": table_one,
        "supplementary_table_2_relative_energy_vector": table_two,
        "source_reported_equations_fits_slopes_energies_corrections_and_calculations_retained_as_postseal_provenance": True,
        "equilibrium_disagreement_adverse_record_preserved": True,
        "source_direction_label_disagreements_preserved_without_selection": True,
        "imported_reversible_rate_equation_equilibrium_law_or_constant_stochastic_premise_fitted_direction_weight_steady_state_selection_refit_average_interpolation_renormalization_or_target_correction_used_in_law": False,
        "source_fit_slope_or_energy_used_as_fold_proof_parameter": False,
        "external_zero_reference_glyph_translates_only_to_structural_EmptyOne": True,
        "all_favorable_adverse_unresolved_source_pages_movie_and_archive_members_preserved": True,
    }
    PRIMARY_PATH.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary_path": str(PRIMARY_PATH.relative_to(ROOT)),
        "primary_hash": sha_file(PRIMARY_PATH),
        "complete_reversible_state_pair_count": primary["complete_reversible_state_pair_count"],
        "complete_directional_experiment_count": primary["complete_directional_experiment_count"],
        "complete_registered_target_count": primary["complete_registered_target_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
