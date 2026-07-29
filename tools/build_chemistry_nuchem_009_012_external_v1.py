#!/usr/bin/env python3
"""Reconstruct the complete post-seal NUCHEM-009–012 source surface."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-009-012-radiochemistry-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUT = SNAP / "complete-postseal-analysis-v1.json"
EXPECTED_INVENTORY = "sha256:6e420b9e739c6899345641ea0091efad147d508f65fec5e956f82c8ec764b071"
FILES = {
    "radiotracer": ("iaea-tcs31-radiotracer-rtd-2008.pdf", "sha256:54917c0e0ccd224c20788d3aaecc2050e2c780c8827d907455ff3c13ed11e6b1", 163),
    "separation": ("doe-osti-1580278-isotope-harvesting-hfslm.pdf", "sha256:fa8b7127877b653608c9b0a6c967eeb0b717a2bea71639a2947c354e2bed8e08", 19),
    "fission_products": ("doe-ornl-4865-fission-product-behavior-msre.pdf", "sha256:ff16c9951db9555870de6cbb593785f0bd1878dfe08c7a5b9811fc83d9ed188a", 156),
    "radiolysis": ("nbs-nsrds45-radiation-chemistry-nitrous-oxide.pdf", "sha256:b9933ebecd6c235b614f336359cd98033b8e51f092af56aa2d57645eed1348d1", 32),
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def clean(text: str) -> str:
    return "\n".join(line.strip() for line in text.replace("\u00ad", "").splitlines() if line.strip())


def surface(path: Path) -> tuple[list[dict], str]:
    rows, texts = [], []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = clean(page.extract_text() or "")
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())}); texts.append(text)
    return rows, "\n".join(texts)


def compact(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    normalized = compact(text); missing = [fragment for fragment in fragments if compact(fragment) not in normalized]
    if missing: raise SystemExit(f"required {source} evidence missing: {missing}")


def main() -> None:
    if OUT.exists(): raise SystemExit("NUCHEM-009–012 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY: raise SystemExit("NUCHEM-009–012 source inventory changed")
    sources, texts = {}, {}
    for key, (name, expected, expected_pages) in FILES.items():
        path = SNAP / name
        if digest(path.read_bytes()) != expected: raise SystemExit(f"registered source bytes changed: {key}")
        vector, text = surface(path)
        if len(vector) != expected_pages: raise SystemExit(f"registered page count changed: {key}")
        sources[key] = {"snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_sha256": expected, "surface_kind": "pdf", "surface_unit_count": len(vector), "extracted_character_count": sum(row["character_count"] for row in vector), "complete_surface_vector": vector}
        texts[key] = text

    require(texts["radiotracer"], ("Radiotracer Residence Time Distribution Method", "58CoCl2", "70 to 75%", "79 min", "8.7 min", "40 min", "5%", "30% of the volume"), "radiotracer")
    require(texts["separation"], ("Hollow Fiber Supported Liquid Membrane", "1626", "92% recovery", "18.5", "1.6", "13.2", "71% extraction", "only 1% extraction"), "radiochemical separation")
    require(texts["fission_products"], ("Fission Product Behavior", "distinct chemical groups", "Kr and Xe", "Rb", "Cs", "Sr", "Ba", "lanthanides", "Nb", "Mo", "Tc", "Ru", "middle quartiles", "inventory with a median", "one-fourth to one-third"), "fission-product chemistry")
    require(texts["radiolysis"], ("Radiation Chemistry", "Preferred value", "10.0", "2.0", "4.0", "Rare gas sensitized radiolysis", "tentative", "Linearity was not observed"), "radiolysis")

    n009 = {
        "claim_id": "SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009",
        "complete_tracer_chemical_vector": ["82Br in water", "K82Br in gold slurry", "Na-24 activated tail material", "58CoCl2 precursor", "58CoO", "58CoS", "59Fe-labelled mineral", "NaH51CrO4-labelled coal ash"],
        "detector_support": {"simple_experiment_detector_count": "2", "particular_site_detector_count": "4-6", "complex_reactor_detector_count": ">10-20", "one_inch_NaI_Br82_water_sensitivity": "65 cpm per kBq m-3"},
        "gold_leach_vector": {"processing_tanks": "8", "flow_rate_m3_per_h": "100", "tank_1_volume_m3": "500", "tank_7_8_volume_each_m3": "250", "tank_1_injected_activity_mCi": "100", "tank_7_injected_activity_mCi": "130", "tank_1_surface_bypass_percent": "3-5", "tank_7_8_surface_bypass_percent": "1-2"},
        "flotation_mean_residence_time_minutes": [{"machine": "TK", "liquid": "3.3", "solid": "3.2"}, {"machine": "DO", "liquid": "5.3", "solid": "3.4"}, {"machine": "WE", "liquid": "6.2", "solid": "5.3"}],
        "cobalt_recovery_vector": {"tracer_forms": ["58CoO", "58CoS"], "plug_flow_descent_minutes": "79", "mixed_tanks_mean_residence_minutes": "8.7", "tanks_in_series_J": "3.2", "sampling_duration_hours": "about 6", "recovery_in_copper_matte_percent": "70-75", "delay_minutes": "40", "short_circuit_percent": "about 5", "blocked_settling_tank_volume_percent": "nearly 30"},
        "observation_model_boundary": "measured curves, background/decay corrections, normalization, fitted model forms, model parameters, plant interpretations and recommendations remain separately identified",
        "all_background_decay_correction_normalization_loss_fit_assumption_adverse_absent_unavailable_and_unresolved_rows_retained": True,
    }
    n010 = {
        "claim_id": "SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010",
        "complete_species_vector": ["48V", "51V", "Ti", "47Sc", "44mSc", "Mn", "Cr", "B", "P", "Ni", "VO2(OH)2-", "VO2+", "VO(OH)3", "VO3(OH)2-"],
        "complete_process_vector": ["target dissolution", "AG50-X8 cation-resin titanium removal", "aqueous neutral feed", "Aliquat 336 liquid membrane", "counter-current strip", "feed sampling", "strip sampling", "HPGe gamma spectroscopy", "ICP-MS"],
        "cold_vanadium_vector": {"feed_start_ppm": "0.2 ± 0.01", "feed_end": "below 1 ppb detection limit", "strip_end_ppm": "0.4 ± 0.02", "time_minutes": "60", "concentration_effect": "2x"},
        "adverse_initial_radiotracer_vector": {"measured_48V_mCi": "2.55", "theoretical_48V_mCi": "2.23", "extraction_percent": "1", "status": "unexpected", "titanium_feed_ppm": "435"},
        "resin_vector": {"pre_column_48V_uCi": "2562", "pre_column_47Sc_uCi": "46", "pre_column_44mSc_uCi": "33", "retained_48V_uCi": "734", "retained_47Sc_uCi": "19", "retained_44mSc_uCi": "13", "post_column_48V_uCi": "1626", "48V_recovery_percent": "92", "post_column_Sc": "not detectable"},
        "post_titanium_removal_vector": {"feed_start_48V_ppt": "18.5", "feed_end_48V_ppt": "1.6", "strip_end_48V_ppt": "13.2", "time_minutes": "180", "extraction_percent": "71", "replicates": "n=1", "error_basis": "counting-statistics uncertainty"},
        "competitive_species_vector": {"feed_start_48V_ppt": "8", "feed_end_48V_ppt": "0.5", "strip_end_48V_ppt": "5.7", "time_minutes": "60", "extraction_percent": "71", "replicates": "n=1", "competitors": ["Mn", "Cr", "Ti", "B", "P", "Ni"]},
        "projected_not_measured_distinguished": {"7000_L_to_1_L_concentration_factor": "projected 7000", "58Ni_one_week_concentration_ppt": "estimated 900", "48V_atoms": "calculated 1.92e17"},
        "all_detection_limits_uncertainties_single_replicates_losses_interference_unexpected_adverse_estimates_and_future_work_retained": True,
    }
    n011 = {
        "claim_id": "SFT-CHEM-FISSION-PRODUCT-CHEMICAL-DISTRIBUTION-011",
        "complete_chemical_groups": {
            "noble_gases": ["Kr", "Xe"],
            "stable_salt_soluble_fluorides": ["Rb", "Cs", "Sr", "Ba", "Y", "Zr", "lanthanides"],
            "noble_metals_or_nonstable_fluorides": ["Nb", "Mo", "Tc", "Ru", "Ag", "Sb", "Te"],
            "iodine": "less-certain salt-retention classification retained separately",
        },
        "phase_location_behavior": ["noble gases stripped to off-gas and diffuse into moderator graphite", "daughter products deposit on nearby surfaces including salt", "stable fluorides remain soluble in fuel salt", "small salt-mist amount reaches off-gas", "noble metals deposit on metal, graphite and salt-gas interface"],
        "operating_support": {"235U_period_months": "26", "235U_effective_full_power_hours": ">9000", "233U_period_months": "about 15", "233U_effective_full_power_hours": ">5100", "total_operating_period": "nearly four years"},
        "sample_support": ["pump-bowl liquid and gas samples", "pump-bowl exposed surfaces", "five core surveillance assemblies", "system-segment specimens", "remote collimated gamma surveys"],
        "iodine_balance_vector": {"salt_inventory_range_percent": "45-71", "median_percent": "62", "surveillance_and_gas_samples_percent": "<1 of remainder", "unaccounted_fraction": "about one-quarter to one-third", "status": "not adequately accounted for"},
        "surface_vector": {"metal_area_percent": "26", "graphite_area_percent": "74", "net_deposition": "generally more intense on metal and under more turbulent flow", "surface_roughness_effect": "no apparent effect"},
        "adverse_and_unresolved_vector": ["noble-metal fates remain partly conjectural", "changing spray, oil-cracking and overflow conditions were uncontrolled", "wide variance and poor noble-metal material balances prevent more than qualitative fate specification", "iodine/tellurium off-gas evidence does not support the inferred missing path", "flow effects were not experimentally studied", "future chemical processing will change distributions"],
        "all_inventory_bases_samples_conditions_variances_losses_conjectures_adverse_absent_unavailable_and_unresolved_rows_retained": True,
    }
    rare_gas_table = [
        {"sensitizer": "He", "G_N2": "7.3", "G_O2": "2.8", "G_NO": "3.0", "G_minus_N2O": "8.8"},
        {"sensitizer": "Ne", "G_N2": "6.3", "G_O2": "2.4", "G_NO": "3.2", "G_minus_N2O": "7.9"},
        {"sensitizer": "Ar", "G_N2": "3.0", "G_O2": "1.5", "G_NO": "0.0", "G_minus_N2O": "3.0"},
        {"sensitizer": "Kr", "G_N2": "2.9", "G_O2": "1.6", "G_NO": "0.5", "G_minus_N2O": "3.2"},
        {"sensitizer": "Xe", "G_N2": "3.8", "G_O2": "1.8", "G_NO": "0.5", "G_minus_N2O": "4.1"},
    ]
    n012 = {
        "claim_id": "SFT-CHEM-RADIATION-CHEMISTRY-REACTION-NETWORK-012",
        "yield_definition": "G is the number of molecules produced or consumed per registered absorbed-energy resource",
        "complete_product_vector": ["N2", "O2", "NO", "NO2", "N2O3", "N2O consumed"],
        "preferred_yield_vector": [
            {"species": "N2", "G": "10.0", "uncertainty": "0.2", "conditions": "N2O 100-1000 torr; 290-300 K; <=0.1 mol percent conversion; total dose <=1e20 eV g-1"},
            {"species": "O2 measured after trapping at 77 K", "G": "2.0", "uncertainty": "0.2", "conditions": "same registered low-dose conditions"},
            {"species": "O2 calculated", "G": "4.0", "uncertainty": "0.4", "conditions": "same registered low-dose conditions plus stated trap stoichiometry"},
            {"species": "NO", "G": "4.0", "uncertainty": "0.4", "conditions": "290-300 K; <=0.1 mol percent conversion; total dose <=1e20 eV g-1"},
        ],
        "very_high_dose_vector": [{"G_N2": "12.4 ± 0.4", "G_O2_measured": "2.5 ± 0.3", "G_O2": "5.0 ± 0.2", "G_NO": "5.0 ± 0.2", "dose_rate_eV_g-1_s-1": "1e27"}, {"G_N2": "12.3 ± 0.3", "dose_rate_eV_g-1_s-1": "2e28"}],
        "complete_rare_gas_sensitized_table": rare_gas_table,
        "reaction_vector": ["2NO + O2 -> 2NO2", "4NO + O2 -> 2N2O3", "N2O3 -> NO + NO2", "2NO2 + 2OH- -> NO2- + NO3- + H2O"],
        "adverse_and_limit_vector": ["preferred values are selected from multiple discrepant methods", "values corrected to G(N2)=10 remain marked corrected", "some energy-measurement methods are unstated", "some calculation bases are not fully explained", "vessel-volume and wall effects remain", "G values fall with accumulating products and total dose", "low-pressure investigations disagree", "rare-gas-sensitized yields are tentative", "energy partition by electron fraction is an assumption", "Xe plots were nonlinear for every product", "some values are missing or below detection", "complete tables preserve conventional zero and signed inscriptions as external provenance"],
        "all_methods_conditions_dosimetry_corrections_tentative_unreliable_questionable_nonlinear_adverse_absent_unavailable_and_unresolved_rows_retained": True,
    }
    payload = {
        "schema": "sft-v3-chemistry-nuchem-009-012-complete-postseal-analysis/1", "source_inventory_sha256": EXPECTED_INVENTORY,
        "complete_source_count": len(sources), "complete_pdf_page_count": sum(row["surface_unit_count"] for row in sources.values()),
        "complete_extracted_character_count": sum(row["extracted_character_count"] for row in sources.values()), "complete_source_reconstruction": sources,
        "nuchem_009": n009, "nuchem_010": n010, "nuchem_011": n011, "nuchem_012": n012,
        "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_fit_estimate_loss_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"analysis": OUT.relative_to(ROOT).as_posix(), "analysis_sha256": digest(OUT.read_bytes()), "result_vector_sha256": payload["complete_result_vector_sha256"], "sources": payload["complete_source_count"], "pdf_pages": payload["complete_pdf_page_count"], "characters": payload["complete_extracted_character_count"], "radiotracer_rows": len(n009["complete_tracer_chemical_vector"]), "separation_species": len(n010["complete_species_vector"]), "fission_groups": len(n011["complete_chemical_groups"]), "preferred_radiolysis_yields": len(n012["preferred_yield_vector"]), "rare_gas_rows": len(rare_gas_table)}, indent=2))


if __name__ == "__main__": main()
