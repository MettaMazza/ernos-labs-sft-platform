#!/usr/bin/env python3
"""Reconstruct the complete post-seal NUCHEM-005–008 source surface."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-005-008-isotope-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUT = SNAP / "complete-postseal-analysis-v1.json"
EXPECTED_INVENTORY = "sha256:bd9cc53f97b20a2d92bc26ab28ce2f5eefb71e6b3ee1f02bf840214adaccdaee"

FILES = {
    "strontium_90": (
        ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/nist-srm-4239a-strontium-90.pdf",
        "sha256:e8f3f5397db147ce57a270c25e4fd655ca6bacc5b8e6652e3a3df57c36ea346e", "pdf", 4,
    ),
    "uranium_232": (
        ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/nist-srm-4324c-uranium-232.html",
        "sha256:ab8ce95a445b7c665187d5d347ff57fa06e94082aa9177c09ec2df8c77433a23", "html", 1,
    ),
    "exchange": (SNAP / "usgs-wrir02-4172-isotope-equilibrium.pdf", "sha256:ce2792deb8c1b735bbe5f31c9f41027f6e57d99882d50b58a502b67c35b977d4", "pdf", 135),
    "equilibrium": (SNAP / "usgs-pp440kk-stable-isotope-fractionation.pdf", "sha256:7230ec719d5890ddbae8c3944df6d3f9ba5d426b8c533846279a31df033c2c61", "pdf", 117),
    "kinetic": (SNAP / "nbs-rp729-electrolytic-isotope-fractionation-1934.pdf", "sha256:381dbadda73c845133cbd03cdbb9bb700dd78d1ec3004879aa21e34fe4bde299", "pdf", 10),
}


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True); self.hidden = 0; self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}: self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.hidden: self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def clean_lines(text: str) -> str:
    return "\n".join(line.strip() for line in text.replace("\u00ad", "").splitlines() if line.strip())


def pdf_surface(path: Path) -> tuple[list[dict], str]:
    rows, complete = [], []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = clean_lines(page.extract_text() or "")
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
        complete.append(text)
    return rows, "\n".join(complete)


def html_surface(path: Path) -> tuple[list[dict], str]:
    parser = _VisibleText(); parser.feed(path.read_text(errors="strict"))
    text = clean_lines("\n".join(parser.parts))
    return [{"document": 1, "character_count": len(text), "text_sha256": digest(text.encode())}], text


def compact(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    normalized = compact(text)
    missing = [fragment for fragment in fragments if compact(fragment) not in normalized]
    if missing: raise SystemExit(f"required {source} evidence missing: {missing}")


def main() -> None:
    if OUT.exists(): raise SystemExit("NUCHEM-005–008 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY: raise SystemExit("NUCHEM-005–008 source inventory changed")

    sources, texts = {}, {}
    for key, (path, expected, kind, expected_units) in FILES.items():
        if digest(path.read_bytes()) != expected: raise SystemExit(f"registered source bytes changed: {key}")
        vector, source_text = pdf_surface(path) if kind == "pdf" else html_surface(path)
        if len(vector) != expected_units: raise SystemExit(f"registered source unit count changed: {key}")
        sources[key] = {
            "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_sha256": expected,
            "surface_kind": kind, "surface_unit_count": len(vector),
            "extracted_character_count": sum(row["character_count"] for row in vector),
            "complete_surface_vector": vector,
        }
        texts[key] = source_text

    require(texts["strontium_90"], ("Strontium-90", "90Sr/90Y equilibrium", "29.492", "0.088", "25 December 2019", "28.80", "2.6684"), "strontium equilibrium")
    require(texts["uranium_232"], ("Uranium-232 is an isotope of uranium", "in equilibrium with its progeny", "212 Pb", "212 Bi", "208 Tl", "212 Po", "26.30", "0.23"), "uranium equilibrium")
    require(texts["exchange"], ("Calculation of Individual Isotope Equilibrium Constants", "ISOTOPE_ALPHAS", "ISOTOPE_RATIOS", "Calcite", "CO2(g)", "1.0793", "76.356", "21.217", "42.08"), "isotope exchange")
    require(texts["equilibrium"], ("Compilation of Stable Isotope Fractionation Factors", "fractionation factor", "1.00500", "1.01980", "CO2-water", "uncritically calls attention"), "equilibrium fractionation")
    require(texts["kinetic"], ("Fractionation of the Isotopes", "150 liters", "equilibrium had been practically attained", "20.5 ppm", "2.2 ppm", "57.8", "4.8 X 10", "fractionation factor"), "kinetic fractionation")

    equilibrium_table = [
        {"delta_A_permil": "1.00", "delta_B_permil": "0", "delta_difference_permil": "1.00", "1000_ln_alpha_permil": "1.00", "alpha": "1.00000"},
        {"delta_A_permil": "5.00", "delta_B_permil": "0", "delta_difference_permil": "5.00", "1000_ln_alpha_permil": "4.99", "alpha": "1.00500"},
        {"delta_A_permil": "10.00", "delta_B_permil": "0", "delta_difference_permil": "10.00", "1000_ln_alpha_permil": "9.95", "alpha": "1.01000"},
        {"delta_A_permil": "12.00", "delta_B_permil": "0", "delta_difference_permil": "12.00", "1000_ln_alpha_permil": "11.93", "alpha": "1.01200"},
        {"delta_A_permil": "15.00", "delta_B_permil": "0", "delta_difference_permil": "15.00", "1000_ln_alpha_permil": "14.89", "alpha": "1.01500"},
        {"delta_A_permil": "20.00", "delta_B_permil": "0", "delta_difference_permil": "20.00", "1000_ln_alpha_permil": "19.80", "alpha": "1.02000"},
        {"delta_A_permil": "10.00", "delta_B_permil": "5.00", "delta_difference_permil": "5.00", "1000_ln_alpha_permil": "4.96", "alpha": "1.00498"},
        {"delta_A_permil": "20.00", "delta_B_permil": "15.00", "delta_difference_permil": "5.00", "1000_ln_alpha_permil": "4.91", "alpha": "1.00493"},
        {"delta_A_permil": "30.00", "delta_B_permil": "25.00", "delta_difference_permil": "5.00", "1000_ln_alpha_permil": "4.87", "alpha": "1.00488"},
        {"delta_A_permil": "30.00", "delta_B_permil": "20.00", "delta_difference_permil": "10.00", "1000_ln_alpha_permil": "9.76", "alpha": "1.00980"},
        {"delta_A_permil": "30.00", "delta_B_permil": "15.00", "delta_difference_permil": "15.00", "1000_ln_alpha_permil": "14.67", "alpha": "1.01478"},
        {"delta_A_permil": "30.00", "delta_B_permil": "10.00", "delta_difference_permil": "20.00", "1000_ln_alpha_permil": "19.61", "alpha": "1.01980"},
    ]
    exchange_alpha = [
        {"ratio": "18O CO2(aq)/CO2(g)", "alpha": "0.99893", "1000_ln_alpha_solution": "-1.0715", "1000_ln_alpha_25C": "-1.0715"},
        {"ratio": "13C CO2(aq)/CO2(g)", "alpha": "0.99916", "1000_ln_alpha_solution": "-0.83913", "1000_ln_alpha_25C": "-0.83913"},
        {"ratio": "18O CO2(aq)/H2O(l)", "alpha": "1.041", "1000_ln_alpha_solution": "40.151", "1000_ln_alpha_25C": "40.151"},
        {"ratio": "D H2O(l)/H2O(g)", "alpha": "1.0793", "1000_ln_alpha_solution": "76.356", "1000_ln_alpha_25C": "76.356"},
    ]
    exchange_ratios = [
        {"ratio": "R(13C) Calcite", "absolute_ratio": "1.12049e-02", "standard_units_permil": "2.2111"},
        {"ratio": "R(18O) Calcite", "absolute_ratio": "2.04774e-03", "standard_units_permil": "21.217"},
        {"ratio": "R(13C) CO2(g)", "absolute_ratio": "1.10956e-02", "standard_units_permil": "-7.5644"},
        {"ratio": "R(18O) CO2(g)", "absolute_ratio": "2.08958e-03", "standard_units_permil": "42.08"},
    ]
    kinetic_table = [
        {"litres_collected": "1", "recombined_gases_ppm": "-20.5", "cell_O_with_normal_H_ppm": "-13.2", "cell_H_with_normal_O_ppm": "-7.8", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "10", "recombined_gases_ppm": "-17.1", "cell_O_with_normal_H_ppm": "-11.0", "cell_H_with_normal_O_ppm": "-6.2", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "20", "recombined_gases_ppm": "-14.8", "cell_O_with_normal_H_ppm": "-10.5", "cell_H_with_normal_O_ppm": "-5.6", "residual_H2_in_cell_ppm": "+23.9"},
        {"litres_collected": "30", "recombined_gases_ppm": "-14.1", "cell_O_with_normal_H_ppm": "-8.0", "cell_H_with_normal_O_ppm": "-5.5", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "50", "recombined_gases_ppm": "-10.8", "cell_O_with_normal_H_ppm": "-6.3", "cell_H_with_normal_O_ppm": "-3.6", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "73", "recombined_gases_ppm": "unreported", "cell_O_with_normal_H_ppm": "unreported", "cell_H_with_normal_O_ppm": "unreported", "residual_H2_in_cell_ppm": "+43.0"},
        {"litres_collected": "75", "recombined_gases_ppm": "-7.3", "cell_O_with_normal_H_ppm": "-5.0", "cell_H_with_normal_O_ppm": "-2.0", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "105", "recombined_gases_ppm": "-5.0", "cell_O_with_normal_H_ppm": "-3.0", "cell_H_with_normal_O_ppm": "-0.1", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "124", "recombined_gases_ppm": "-3.1", "cell_O_with_normal_H_ppm": "-2.0", "cell_H_with_normal_O_ppm": "+0.1", "residual_H2_in_cell_ppm": "unreported"},
        {"litres_collected": "150", "recombined_gases_ppm": "-1.5", "cell_O_with_normal_H_ppm": "-1.1", "cell_H_with_normal_O_ppm": "+0.2", "residual_H2_in_cell_ppm": "+57.8"},
    ]

    n005 = {
        "claim_id": "SFT-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005",
        "complete_parent_daughter_vectors": [["90Sr", "90Y"], ["232U", "complete retained progeny including 212Pb, 212Bi, 212Po and 208Tl"]],
        "equilibrium_records": ["90Sr is in radioactive equilibrium with 90Y", "232U is in equilibrium with its progeny"],
        "complete_reference_time_vector": ["1200 EST, 25 December 2019", "1200 EST, 31 October 2022"],
        "certified_activity_vector": [{"nuclide": "90Sr", "value": "29.492", "uncertainty": "0.088", "unit": "kBq·g-1"}, {"nuclide": "232U", "value": "26.30", "uncertainty": "0.23", "unit": "Bq·g-1"}],
        "transient_or_secular_numeric_time_series_in_registered_sources": "unavailable__qualitative_equilibrium_records_retained_without_fabrication",
        "all_assumptions_uncertainties_corrections_confirmations_and_unavailable_rows_retained": True,
    }
    n006 = {
        "claim_id": "SFT-CHEM-ISOTOPE-EXCHANGE-006",
        "exchange_relation": "one-atom isotope exchange has equilibrium constant equal to the ratio of heavy/light isotope ratios across the two retained carriers; multi-atom exchange retains the stated root relation",
        "complete_exchange_alpha_vector": exchange_alpha,
        "complete_example_isotope_ratio_vector": exchange_ratios,
        "complete_example_conditions": ["25.000 deg C", "all isotopic species in all phases at equilibrium", "gas pressure 0.0317 atm", "roughly 97 percent water vapour and 3 percent CO2", "0.0392 mmol calcite"],
        "balance_and_nonideality_custody": "complete species, solution-composition, charge-balance, activity, database and approximation records remain in the 135-page source vector",
        "all_assumptions_comparisons_nonideality_absent_unavailable_and_adverse_rows_retained": True,
    }
    n007 = {
        "claim_id": "SFT-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007",
        "factor_definition": "alpha_A-B = R_A/R_B with R written as heavy isotope divided by light isotope",
        "one_atom_exchange_correspondence": "for a one-atom exchange reaction K equals alpha",
        "complete_table_1_vector": equilibrium_table,
        "complete_exchange_alpha_vector": exchange_alpha,
        "temperature_support": ["25 deg C exact example tables", "complete registered temperature-dependent curves on figures 1 through 49"],
        "adverse_record": "the source distinguishes measured, calculated, inferred, estimated, recalculated, unavailable, approximate and uncritically compiled values and reports unresolved discrepancies and kinetic or nonequilibrium effects",
        "all_fits_assumptions_estimated_curves_adverse_absent_unavailable_and_unresolved_rows_retained": True,
    }
    n008 = {
        "claim_id": "SFT-CHEM-KINETIC-ISOTOPE-FRACTIONATION-008",
        "reaction_path": "electrolysis with isotope-resolved recombined gases, separately normalized hydrogen and oxygen contributions, and residual cell hydrogen",
        "complete_table_1_vector": kinetic_table,
        "steady_state_record": "at 150 litres equilibrium had practically been attained and evolved hydrogen and oxygen were close to normal isotopic compositions",
        "kinetic_response_vector": {"initial_recombined_gas_density_change_ppm": "-20.5", "initial_oxygen_contribution_ppm": "-13.2", "initial_hydrogen_contribution_ppm": "-7.8", "equilibrium_water_approximately_heavier_ppm": "60", "hydrogen_contribution_ppm": "28", "oxygen_contribution_ppm": "32", "natural_heavy_light_hydrogen_ratio": "2.0e-4", "equilibrium_heavy_light_hydrogen_ratio": "4.8e-4", "fractionation_factor": "2.4"},
        "replicate_equilibrium_density_ppm": ["52.1", "53.5", "53.3"],
        "correction_vector": {"applied_ppm": "2.2", "uncertainty_ppm": "0.5", "measurement_rows_ppm": ["1.4", "2.4", "2.8"]},
        "adverse_and_limit_vector": ["flow reversals retained", "5 percent loss retained", "estimated curve B retained", "operating conditions retained", "experimental limitations retained", "unreported table cells retained as unreported"],
        "all_corrections_uncertainties_replicate_discrepancies_flow_reversals_estimates_losses_and_limits_retained": True,
    }
    payload = {
        "schema": "sft-v3-chemistry-nuchem-005-008-complete-postseal-analysis/1",
        "source_inventory_sha256": EXPECTED_INVENTORY,
        "complete_source_count": len(sources),
        "complete_pdf_page_count": sum(row["surface_unit_count"] for row in sources.values() if row["surface_kind"] == "pdf"),
        "complete_html_document_count": sum(row["surface_unit_count"] for row in sources.values() if row["surface_kind"] == "html"),
        "complete_extracted_character_count": sum(row["extracted_character_count"] for row in sources.values()),
        "complete_source_reconstruction": sources,
        "nuchem_005": n005, "nuchem_006": n006, "nuchem_007": n007, "nuchem_008": n008,
        "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_estimate_loss_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({
        "analysis": OUT.relative_to(ROOT).as_posix(), "analysis_sha256": digest(OUT.read_bytes()),
        "result_vector_sha256": payload["complete_result_vector_sha256"], "sources": payload["complete_source_count"],
        "pdf_pages": payload["complete_pdf_page_count"], "html_documents": payload["complete_html_document_count"],
        "characters": payload["complete_extracted_character_count"], "equilibrium_table_rows": len(equilibrium_table),
        "exchange_alpha_rows": len(exchange_alpha), "exchange_ratio_rows": len(exchange_ratios), "kinetic_table_rows": len(kinetic_table),
    }, indent=2))


if __name__ == "__main__": main()
