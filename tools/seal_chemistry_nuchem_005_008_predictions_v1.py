#!/usr/bin/env python3
"""Seal four NUCHEM-005–008 laws and value-free targets before source capture."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROWS = (
    ("005", "SFT-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005", "radiochemical_equilibrium_law_v1.py", "517914e1953e8bde79ec94c56001ebd78008fdf84fa0227896d58e1914048a69", "5aa52d065525eb8f6fad00e7ace2b09b2c73b66216659bc9d0a2918d93791487", "held-parent-daughter-identity__positive-ordered-resource-intervals__exact-counted-activity-pair__held-ratio-or-structural-absence__persistent-nonOne-ratio-forces-transient__persistent-One-ratio-forces-secular__complete-parent-daughter-time-vector__finite-successor-recomputes-regime", "complete_NIST_sources_development_observed_and_reused__no_blind_claim"),
    ("006", "SFT-CHEM-ISOTOPE-EXCHANGE-006", "isotope_exchange_law_v1.py", "8020c83a3cd234074d80695493dd9b615671030fce80bead491fbc26a03a81d4", "9ebf33adb3d143519029025bc31b2a7d5a8a9fff6b691457abe2c039844b81b6", "held-element-light-heavy-isotopes__held-distinct-chemical-carriers__positive-complete-four-count-inventory__exact-isotope-and-carrier-conservation__held-direction-positive-Take__exact-cross-product-exchange-quotient__equal-forward-reverse-closes-EmptyOne__successor-preserves-identities-and-totals", "title_abstract_and_scope_development_observed__complete_USGS_pages_tables_and_values_unopened"),
    ("007", "SFT-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007", "equilibrium_isotope_fractionation_law_v1.py", "b5df27ccdcce7c48864b69d26837f5c34586faab26a0325f9b2d83ddd887eccd", "98fbc69aba91a79c974cd49824febdf8f2c36d76d00e9b75cb75d16498f6a216", "held-light-heavy-isotopes__held-distinct-phase-pair__positive-complete-isotope-counts__exact-heavy-per-light-ratios__exact-ratio-of-ratios__held-enrichment-or-EmptyOne-coincidence__exchange-balance-plus-stable-factor__complete-vector-successor-recomputes", "titles_and_scopes_development_observed__complete_USGS_pages_tables_curves_and_values_unopened"),
    ("008", "SFT-CHEM-KINETIC-ISOTOPE-FRACTIONATION-008", "kinetic_isotope_fractionation_law_v1.py", "7ee759e8694ce914142c47d0b3b648771090119b81a0a951ed796cdc5ee3d331", "94a2706d5a1b8a3fcdb69036b4cfb8b1a675acb811c50fbbb74301384f951b99", "held-reaction-light-heavy-identities__positive-ordered-resource-intervals__positive-counted-isotope-products__exact-products-per-resource-rates__exact-light-heavy-rate-ratio__held-faster-class-or-EmptyOne__positive-Take-or-EmptyOne-remainder__finite-time-series-successor-recomputes", "NBS_title_abstract_and_selected_summary_values_development_observed__complete_ten_page_table_curve_and_correction_vector_unopened"),
)


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for number, claim, law, law_hash, identity_hash, survivor, exposure in ROWS:
        law_path = ROOT / "sft/chemistry" / law
        identity_path = ROOT / f"experiments/external_sources/chemistry/nuchem_{number}_target_identities_v1.json"
        out = ROOT / f"experiments/sealed_predictions/chemistry_nuchem_{number}_pre_source_v1.json"
        if out.exists():
            raise SystemExit(f"seal exists {number}")
        if file_hash(law_path) != "sha256:" + law_hash or file_hash(identity_path) != "sha256:" + identity_hash:
            raise SystemExit(f"law/identity changed {number}")
        payload = {
            "schema": "sft-v3-source-exposure-disclosed-derivation-seal/1",
            "branch": "chemistry", "family": "NUCHEM-005-008", "claim_id": claim,
            "obligation_id": f"SFT-CHEM-OBL-NUCHEM-{number}", "sealed_date": "2026-07-28",
            "derivation_path": law_path.relative_to(ROOT).as_posix(), "derivation_hash": file_hash(law_path),
            "target_identity_path": identity_path.relative_to(ROOT).as_posix(), "target_identity_hash": file_hash(identity_path),
            "candidate_cardinality": 256, "operational_witness_count": 8, "predicted_unique_survivor": survivor,
            "source_exposure_before_seal": exposure,
            "complete_postseal_source_capture_had_occurred_before_this_seal": False,
            "source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator": False,
            "prior_source_exposure_never_relabelled_blind": True,
        }
        payload["sealed_payload_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(number, file_hash(out), payload["sealed_payload_hash"])


if __name__ == "__main__":
    main()
