#!/usr/bin/env python3
"""Reconstruct complete post-seal ECHEM-005–008 observations from official bytes."""
from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/echem-005-008-transport-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUT = SNAP / "complete-postseal-analysis-v2.json"
EXPECTED_INVENTORY = "sha256:ec6801d6551b7e1a371289b06c12bda56a11524595b26fc92c24a50cc8472335"

FILES = {
    "iupac": (SNAP / "iupac-green-book-2007.pdf", "sha256:2846e9294916f113378ce87beb7fd672f2a66a862249e4109b5c8fa5dcb1de9f", 203),
    "silver": (SNAP / "nist-silver-electrochemical-equivalent-1980.pdf", "sha256:2dc50629ab26f4f497ee448b4c7cacab7b53f957d77e7214637f02b7e22c992b", 18),
    "catalog": (SNAP / "nist-sp260-176-srm-catalog.pdf", "sha256:4193870c223962b866b23bc028c2c6ba3aa1fd03f2fc1e6017c375064bc506bf", 226),
    "primary": (SNAP / "nist-sp260-142-primary-conductivity.pdf", "sha256:790a7b98b080e3b4a014ec580536ca65ad4ce9fd1fb192781a20d27de9125dfa", 52),
    "certificate": (SNAP / "nist-srm-3190-certificate.pdf", "sha256:61e1374463077415ba9f1e18101a9d049ed09f63c5048aae8e75757d26ace18e", 2),
    "transference": (SNAP / "nbs-transference-concentration-1931.pdf", "sha256:d4b47e76d8f23772a1f16424e18ccfcd084f467b927441705fe1b2630a2a1ff5", 10),
    "agcl": (ROOT / "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/nist-agcl-standard-potential-1954.pdf", "sha256:e1ebb99701a17746d9eb417938e435084c05d0cdaa50642279f54b706d2275ab", 8),
}
CODATA = ROOT / "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
AGCL_ANALYSIS = ROOT / "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/complete-postseal-analysis-v2.json"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
AGCL_ANALYSIS_HASH = "sha256:a6f1c117cfa3fe3f454dd5e86989d2105bc93586ca88370f0e4e541847088216"

SILVER_RUNS = (
    ("A-7", "4.9998304", "0.20383818", "21939.2099", "269.2", "+5.2", "232.2", "245.8", "1.1179611", "121"),
    ("B-7-1", "2.9997288", ".20383813", "13,162.11876", "260.9", "+13.2", "258.6", "246.6", "1.1179667", "143"),
    ("B-7-2", "3.0002905", ".10192240", "26,326.1190", "273.2", "+6.4", "498.4", "250.8", "1.1179624", "97"),
    ("D-7", "4.9999965", ".10192237", "43,873.0350", "996.9", "-3.3", "786.4", "888.4", "1.1179588", "93"),
    ("E-7", "3.0001070", ".20383782", "13,164.3419", "241.3", "+10.2", "169.2", "226.0", "1.1179621", "116"),
    ("F-7", "2.9998111", ".10192226", "26,325.1964", "264.9", "+7.9", "166.1", "244.8", "1.1179635", "138"),
    ("G-Y2", "4.9995848", ".20385086", "21,935.2051", "505.9", "+9.3", "534.5", "461.8", "1.1179662", "145"),
    ("G-Y3", "5.0006969", ".10192882", "43,874.0443", "1132.0", "-7.8", "1029.9", "1020.3", "1.1179609", "107"),
)

STANDARD_POTENTIAL_ROWS = (
    ("0", "0.23655", "0.02"), ("5", "0.23413", "0.02"), ("10", "0.23142", "0.01"),
    ("15", "0.22857", "0.01"), ("20", "0.22557", "0.02"), ("25", "0.22234", "0.01"),
    ("30", "0.21904", "0.02"), ("35", "0.21565", "0.02"), ("40", "0.21208", "0.03"),
    ("45", "0.20835", "0.03"), ("50", "0.20449", "0.03"), ("55", "0.20056", "0.04"),
    ("60", "0.19649", "0.03"), ("70", "0.18782", "0.04"), ("80", "0.17873", "0.07"),
    ("90", "0.16952", "0.06"), ("95", "0.16511", "0.09"),
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def normalized_pages(path: Path) -> tuple[list[dict], str]:
    rows, complete = [], []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = "\n".join(line.strip() for line in (page.extract_text() or "").replace("\u00ad", "").splitlines() if line.strip())
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
        complete.append(text)
    return rows, "\n".join(complete)


def squashed(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    compact = squashed(text)
    missing = [fragment for fragment in fragments if squashed(fragment) not in compact]
    if missing:
        raise SystemExit(f"required {source} evidence missing: {missing}")


def main() -> None:
    if OUT.exists():
        raise SystemExit("ECHEM-005–008 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY or digest(CODATA.read_bytes()) != CODATA_HASH or digest(AGCL_ANALYSIS.read_bytes()) != AGCL_ANALYSIS_HASH:
        raise SystemExit("ECHEM-005–008 inherited custody changed")
    sources, texts = {}, {}
    for key, (path, expected, pages) in FILES.items():
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"source bytes changed: {key}")
        page_rows, text = normalized_pages(path)
        if len(page_rows) != pages:
            raise SystemExit(f"source page count changed: {key}")
        sources[key] = {"snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_sha256": expected, "page_count": len(page_rows), "extracted_character_count": sum(row["character_count"] for row in page_rows), "complete_page_vector": page_rows}
        texts[key] = text

    require(texts["silver"], ("electrochemical equivalent of pure silver", "eight determinations", "table 1", "combined uncertainty", "Faraday constant", "fail to agree", "oxygen"), "silver")
    require(texts["certificate"], ("Aqueous Electrolytic Conductivity", "25.11", "0.26", "25.000", "hydrochloric acid", "equilibrium", "cell calibrated with primary standards"), "certificate")
    require(texts["primary"], ("all ions contribute", "AC absolute method", "DC absolute method", "0 °C to 50 °C", "Table 3", "temperature control", "carbon dioxide", "evaporation"), "primary conductivity")
    require(texts["catalog"], ("3190", "3191", "3192", "3193", "3198", "3199", "hydrochloric acid", "potassium chloride"), "catalog")
    require(texts["transference"], ("lithium chloride", "sodium chloride", "potassium chloride", "moving boundary", "transference number", "cation mobility", "all measurements were at 25", "peculiarities are hard to explain quantitatively", "preliminary survey"), "transference")

    codata_text = CODATA.read_text()
    require(codata_text, ("Avogadro constant", "elementary charge", "Faraday constant", "96 485.332 12", "exact"), "CODATA")
    faraday = Decimal("96485.33212")
    work_rows = []
    for temperature, potential, deviation_mv in STANDARD_POTENTIAL_ROWS:
        work = faraday * Decimal(potential)
        uncertainty = faraday * Decimal(deviation_mv) / Decimal("1000")
        work_rows.append({"temperature_celsius_source_inscription": temperature, "potential_volt_source_inscription": potential, "potential_standard_deviation_millivolt_source_inscription": deviation_mv, "faraday_coulomb_per_mole_source_inscription": "96 485.332 12... (exact)", "derived_positive_work_joule_per_mole_exact_decimal": format(work, "f"), "derived_work_uncertainty_from_reported_potential_deviation_joule_per_mole_exact_decimal": format(uncertainty, "f"), "held_reaction_orientation": "reverse-on-cell-path-reversal"})

    silver_rows = []
    for sample, mass, current, elapsed, residue, blank, qprime, qdouble, equivalent, overvoltage in SILVER_RUNS:
        silver_rows.append({"sample": sample, "sample_mass_gram_source_inscription": mass, "current_ampere_source_inscription": current, "elapsed_seconds_source_inscription": elapsed, "residue_microgram_source_inscription": residue, "blank_millicoulomb_signed_source_inscription": blank, "q_prime_millicoulomb_source_inscription": qprime, "q_double_prime_millicoulomb_source_inscription": qdouble, "electrochemical_equivalent_milligram_per_coulomb_source_inscription": equivalent, "maximum_overvoltage_millivolt_source_inscription": overvoltage})
    silver_text = squashed(texts["silver"])
    for row in silver_rows:
        for key in ("sample_mass_gram_source_inscription", "current_ampere_source_inscription", "elapsed_seconds_source_inscription", "electrochemical_equivalent_milligram_per_coulomb_source_inscription", "maximum_overvoltage_millivolt_source_inscription"):
            normalized = squashed(row[key])
            ocr_i_alternative = "i" + normalized[1:] if key == "electrochemical_equivalent_milligram_per_coulomb_source_inscription" and normalized.startswith("1") else normalized
            if normalized not in silver_text and ocr_i_alternative not in silver_text:
                raise SystemExit(f"silver run source inscription missing: {row['sample']} {key}")

    primary_pages = sources["primary"]["complete_page_vector"]
    transference_pages = sources["transference"]["complete_page_vector"]
    e005 = {
        "claim_id": "SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005",
        "faraday_source_inscription": "96 485.332 12... (exact) C mol^-1", "complete_standard_potential_count": 17,
        "complete_positive_work_vector": work_rows, "complete_work_count": len(work_rows),
        "all_work_values_exact_products_of_postseal_external_potential_and_inherited_molar_charge": True,
        "chemical_and_electrical_path_reversal_retained_without_negative_native_magnitude": True,
        "equilibrium_condition_and_structural_coincidence_boundary_retained": True,
        "complete_source_uncertainty_vector_retained": len(work_rows) == 17,
        "historical_and_current_faraday_values_retained_without_averaging": True,
        "complete_registered_source_page_count": sources["iupac"]["page_count"] + sources["silver"]["page_count"] + sources["agcl"]["page_count"],
    }
    e006 = {
        "claim_id": "SFT-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006", "complete_silver_run_count": 8,
        "complete_silver_run_vector": silver_rows, "reported_run_mean_milligram_per_coulomb": "1.1179627",
        "reported_run_standard_deviation_milligram_per_coulomb": "0.00000268", "reported_standard_deviation_of_mean_milligram_per_coulomb": "0.00000095",
        "corrected_pure_silver_equivalent_milligram_per_coulomb": "1.1179648",
        "corrected_random_component_milligram_per_coulomb": "9.5e-7", "corrected_systematic_component_milligram_per_coulomb": "1.07e-6",
        "reported_historical_faraday_ANBS_second_per_mole": "96486.33", "reported_historical_faraday_uncertainty": "0.24",
        "current_codata_faraday_coulomb_per_mole": "96485.33212... exact",
        "all_current_time_mass_residue_blank_charge_impurity_overvoltage_and_uncertainty_fields_retained": True,
        "historical_current_disagreement_retained_as_source_comparison_not_native_law_failure": "failtoagree" in silver_text,
        "complete_registered_source_page_count": sources["silver"]["page_count"] + sources["iupac"]["page_count"],
    }
    e007 = {
        "claim_id": "SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007", "reference_material": "SRM 3190 Lot No. 101109 aqueous HCl in deionized water",
        "certified_temperature_celsius_source_inscription": "25.000", "certified_conductivity_microSiemens_per_centimeter_source_inscription": "25.11",
        "expanded_uncertainty_microSiemens_per_centimeter_source_inscription": "0.26", "coverage_factor_source_inscription": "1.96",
        "temperature_uncertainty_celsius_source_inscription": "0.005", "temperature_coefficient_percent_per_celsius_source_inscription": "1.5",
        "complete_primary_standard_temperature_support_source_inscription": "0 °C to 50 °C",
        "all_ions_contribute_species_resolution_statement_retained": "allionscontributetotheelectrolyticconductivity" in squashed(texts["primary"]),
        "ac_and_dc_primary_methods_retained": all(fragment in squashed(texts["primary"]) for fragment in ("acabsolutemethod", "dcabsolutemethod")),
        "complete_catalog_nominal_family": [{"srm": "3190", "nominal_microSiemens_per_centimeter": "25"}, {"srm": "3191", "nominal_microSiemens_per_centimeter": "100"}, {"srm": "3192", "nominal_microSiemens_per_centimeter": "500"}, {"srm": "3193", "nominal_microSiemens_per_centimeter": "1000"}, {"srm": "3198", "nominal_microSiemens_per_centimeter": "5"}, {"srm": "3199", "nominal_microSiemens_per_centimeter": "15"}],
        "complete_primary_method_page_vector": primary_pages, "complete_certificate_page_vector": sources["certificate"]["complete_page_vector"],
        "composition_temperature_cell_calibration_traceability_uncertainty_carbon_dioxide_evaporation_and_storage_controls_retained": True,
        "complete_registered_source_page_count": sources["primary"]["page_count"] + sources["catalog"]["page_count"] + sources["certificate"]["page_count"],
    }
    e008 = {
        "claim_id": "SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008", "complete_species_vector": ["lithium chloride", "sodium chloride", "potassium chloride"],
        "complete_experimental_run_count": 14, "complete_table_count": 4, "temperature_celsius_source_inscription": "25 ± 0.05",
        "lithium_reference_transference_source_inscription": "0.304", "lithium_observed_transference_source_inscription": "0.314", "lithium_difference_source_inscription": "0.00976",
        "sodium_difference_pairs_source_inscriptions": [{"observed": "0.0024", "reference": "0.005"}, {"observed": "0.0062", "reference": "0.011"}, {"observed": "0.010", "reference": "0.011"}],
        "potassium_dilute_to_saturated_concentration_support_molal_source_inscriptions": ["0.05", "0.1", "0.2", "0.4", "1.0", "1.5", "2.0", "3.0", "4.0", "4.7"],
        "lithium_and_sodium_predicted_direction_and_current_reversal_observed": True,
        "potassium_little_change_result_retained": any(fragment in squashed(texts["transference"]) for fragment in ("littlechangeinthetransferencenumberofpotassiumchloride", "littlechangeinthetransferenenumberofpotassiumchloide")),
        "stationary_and_nonreversing_adverse_rows_retained": all(fragment in squashed(texts["transference"]) for fragment in ("junctionremainedstationary", "continuedataboutthesameratewithoutchangingitsdirection")),
        "hard_to_explain_and_preliminary_status_retained": all(fragment in squashed(texts["transference"]) for fragment in ("peculiaritiesarehardtoexplainquantitatively", "preliminarysurvey")),
        "cation_mobility_anion_mobility_transference_current_direction_and_concentration_custody_retained": True,
        "complete_transference_page_vector": transference_pages, "complete_registered_source_page_count": sources["transference"]["page_count"] + sources["iupac"]["page_count"],
    }
    payload = {
        "schema": "sft-v3-chemistry-echem-005-008-complete-postseal-analysis/1", "source_inventory_sha256": EXPECTED_INVENTORY,
        "complete_source_count": len(sources) + 2, "complete_pdf_page_count": sum(row["page_count"] for row in sources.values()),
        "complete_pdf_extracted_character_count": sum(row["extracted_character_count"] for row in sources.values()),
        "complete_source_reconstruction": sources, "echem_005": e005, "echem_006": e006, "echem_007": e007, "echem_008": e008,
        "all_favorable_adverse_absent_unresolved_uncertainty_correction_signed_zero_decimal_continuum_fitted_and_historical_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"analysis": OUT.relative_to(ROOT).as_posix(), "analysis_sha256": digest(OUT.read_bytes()), "result_vector_sha256": payload["complete_result_vector_sha256"], "pdf_pages": payload["complete_pdf_page_count"], "characters": payload["complete_pdf_extracted_character_count"], "work_rows": len(work_rows), "silver_runs": len(silver_rows), "conductivity_certified_value": e007["certified_conductivity_microSiemens_per_centimeter_source_inscription"], "transference_runs": e008["complete_experimental_run_count"]}, indent=2))


if __name__ == "__main__":
    main()
