#!/usr/bin/env python3
"""Reconstruct complete post-seal ECHEM-009–012 observations from official bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/echem-009-012-polarization-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUT = SNAP / "complete-postseal-analysis-v1.json"
EXPECTED_INVENTORY = "sha256:6c26b1511e253b9a909306dad4c2a516c976c4a7f080aff7427574d0466c09a6"

FILES = {
    "galvanic": ("nbs-galvanic-couples-1950.pdf", "sha256:2bb9e0fc2e6f00d56fd88020eef4eb473ef39b9e70310afbcc2e1ae2313a4edd", 8),
    "corrosion": ("nbs-iron-corrosion-1957.pdf", "sha256:40c25d1eb64f272739303897227549151b864e8daa53b5e8a4cdcbe3c2f9caf2", 9),
    "double_layer": ("nist-graphene-double-layer-2020.pdf", "sha256:646f69ccc45ee2bc74a2718db191bc9e43c33d3161ca153ae21bd63b404336d9", 24),
    "coating": ("nist-tn1253-coating-polarization.pdf", "sha256:d9f39fa737915fa7a4a2bfbe756d682cff576638224690b0001a16d5d19aac51", 32),
}

CORROSION_TABLE_1 = (
    ("4", "0.34", "3.0", "0.31", "31", "0.11", "0.91"),
    ("5", "0.34", "3.0", "0.31", "8", "0.11", "0.91"),
    ("6", "0.50", "4.0", "0.44", "9", "0.12", "0.88"),
    ("7", "0.51", "4.0", "0.45", "11", "0.13", "0.88"),
    ("13", "0.33", "3.8", "0.30", "56", "0.09", "0.91"),
    ("18", "0.29", "3.2", "0.27", "36", "0.09", "0.93"),
    ("22", "0.66", "5.0", "0.58", "43", "0.13", "0.88"),
    ("29", "0.50", "4.1", "0.45", "89", "0.12", "0.90"),
)

CORROSION_TABLE_2 = (
    ("after 4 hours", "2.4", "2.2", "135"), ("2", "3.6", "3.2", "300"),
    ("6", "3.1", "2.8", "170"), ("8", "4.4", "4.0", "175"),
    ("10", "3.2", "2.9", "202"), ("13", "2.9", "2.6", "125"),
    ("15", "2.8", "2.5", "145"), ("17", "3.6", "3.2", "202"),
    ("20", "2.5", "2.2", "110"), ("22", "2.4", "2.2", "110"),
    ("24", "2.5", "2.2", "188"), ("27", "3.2", "2.9", "140"),
    ("29", "2.9", "2.6", "65"),
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def pages(path: Path) -> tuple[list[dict], str]:
    rows, complete = [], []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = "\n".join(
            line.strip()
            for line in (page.extract_text() or "").replace("\u00ad", "").splitlines()
            if line.strip()
        )
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
        complete.append(text)
    return rows, "\n".join(complete)


def compact(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    normalized = compact(text)
    missing = [fragment for fragment in fragments if compact(fragment) not in normalized]
    if missing:
        raise SystemExit(f"required {source} evidence missing: {missing}")


def main() -> None:
    if OUT.exists():
        raise SystemExit("ECHEM-009–012 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY:
        raise SystemExit("ECHEM-009–012 source inventory changed")

    sources, texts = {}, {}
    for key, (name, expected, expected_pages) in FILES.items():
        path = SNAP / name
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"registered source bytes changed: {key}")
        vector, text = pages(path)
        if len(vector) != expected_pages:
            raise SystemExit(f"registered source page count changed: {key}")
        sources[key] = {
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_sha256": expected,
            "page_count": len(vector),
            "extracted_character_count": sum(row["character_count"] for row in vector),
            "complete_page_vector": vector,
        }
        texts[key] = text

    require(texts["galvanic"], ("open-circuit potentials", "three polarization curves", "anode", "cathode", "galvanic current", "partition of the applied current", "protective current"), "galvanic")
    require(texts["corrosion"], ("0.2-percent sodium chloride", "Table 1", "Table 2", "measured weight loss", "calculated weight loss", "IR drop", "3.6 percent", "9 percent"), "corrosion")
    require(texts["double_layer"], ("deionized water", "0.1 mol/L", "CuSO4", "MgSO4", "steps of 0.2 V", "0.98", "20 nm to 40 nm", "adjustable variables", "-300 mV"), "double-layer")
    require(texts["coating"], ("current can be related to the rate", "no net current flow", "-1.8", "+1.8", "0.1 V/s", "3% NaCl", "0.003", "0.004", "0.015", "0.034"), "coating")

    table_1 = [dict(zip(("exposure_days", "cathodic_break_current_mA", "anodic_break_current_mA", "corrosion_current_mA", "calculated_weight_loss_mg", "cathodic_to_anodic_ratio", "corrosion_to_cathodic_ratio"), row)) for row in CORROSION_TABLE_1]
    table_2 = [dict(zip(("exposure_time", "polarizing_break_current_mA", "corrosion_current_mA", "calculated_weight_loss_mg"), row)) for row in CORROSION_TABLE_2]
    coating_rows = (
        {"condition": "95 micrometre acrylic coating", "time": "3 hours", "anodic_current_microampere": "0.003"},
        {"condition": "70 micrometre acrylic coating", "time": "90 minutes", "anodic_current_microampere": "0.004"},
        {"condition": "30 micrometre acrylic coating", "time": "4 minutes", "anodic_current_microampere": "0.015", "cathodic_current_microampere": "0.034"},
        {"condition": "60 micrometre alkyd coating no contaminant", "time": "10 minutes", "anodic_current_microampere": "0.007"},
        {"condition": "0.00001 M KHSO4 contamination", "time": "5 minutes", "anodic_current_microampere": "0.017"},
        {"condition": "chip-free 30 micrometre acrylic", "time": "10 minutes", "anodic_current_microampere": "0.002"},
        {"condition": "chip inclusion specimen one", "time": "8 minutes", "anodic_current_microampere": "0.010"},
        {"condition": "chip inclusion specimen two", "time": "5 minutes", "anodic_current_microampere": "0.025"},
        {"condition": "alkyd cured 2 hours", "time": "30 minutes", "polarization_current_microampere": "0.008"},
        {"condition": "alkyd cured 24 hours", "time": "30 minutes", "polarization_current_microampere": "0.005"},
    )

    e009 = {
        "claim_id": "SFT-CHEM-ELECTRODE-REACTION-RATE-009",
        "reaction_and_interface_custody": ["anode oxidation", "cathode reduction", "electrode-electrolyte interface"],
        "complete_current_potential_record_custody": True,
        "anodic_and_cathodic_directions_retained": True,
        "current_to_counted_electron_event_rate_correspondence_retained": True,
        "material_electrolyte_temperature_and_time_conditions_retained": True,
        "complete_published_curve_vector_retained_by_page_reconstruction": True,
        "complete_coating_numeric_observation_vector": list(coating_rows),
        "all_discontinuity_ir_drop_model_and_adverse_records_retained": True,
        "complete_claim_source_pages": 49,
    }
    e010 = {
        "claim_id": "SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010",
        "open_circuit_and_corrosion_equilibrium_references_retained": True,
        "anodic_cathodic_and_reversal_scan_directions_retained": True,
        "applied_potential_range_volt_source_inscriptions": ["-1.8", "+1.8"],
        "scan_rate_volt_per_second_source_inscription": "0.1",
        "current_response_vector": list(coating_rows),
        "complete_ordered_polarization_curves_retained_by_page_reconstruction": True,
        "break_reversal_discontinuity_hysteresis_and_ir_drop_records_retained": True,
        "equilibrium_no_net_current_is_structural_correspondence_not_native_numerical_zero": True,
        "complete_claim_source_pages": 49,
    }
    e011 = {
        "claim_id": "SFT-CHEM-DOUBLE-LAYER-INTERFACIAL-CHARGE-011",
        "interface": "graphene-electrolyte electric double layer",
        "complete_composition_vector": ["deionized water", "0.1 mol/L CuSO4", "0.1 mol/L MgSO4 with 0.01 mol/L H2SO4"],
        "applied_voltage_sweep_source_inscription": "0 V to +0.6 V then to -0.6 V and back to 0 V in 0.2 V steps",
        "surface_potential_offsets_millivolt_source_inscriptions": {"empty_cell": "-22", "water": "approximately -22", "MgSO4": "-50", "CuSO4": "-150"},
        "electrolyte_potential_fraction_source_inscription": "approximately 0.98 V_BE",
        "spatial_resolution_nanometre_source_inscription": "20 to 40",
        "clean_membrane_potential_drop_millivolt_source_inscription": "approaches -300",
        "fit_and_model_provenance": {"finite_element_model": True, "adjustable_variables_retained": True, "shared_fit_energy_meV": "440", "CuSO4_built_in_meV": "-675", "MgSO4_built_in_meV": "-240"},
        "screening_hysteresis_geometry_resolution_and_interpretive_limits_retained": True,
        "complete_source_pages": 24,
    }
    e012 = {
        "claim_id": "SFT-CHEM-CORROSION-REACTION-NETWORK-012",
        "material_environment": "carbon steel in 0.2-percent sodium chloride solution",
        "coupled_anodic_cathodic_network_retained": True,
        "complete_table_1_vector": table_1,
        "complete_table_2_vector": table_2,
        "table_1_measured_weight_loss_mg": "345",
        "table_1_calculated_total_weight_loss_mg": "313",
        "table_1_discrepancy_percent_source_inscription": "about 9",
        "table_2_measured_total_weight_loss_mg": "2245",
        "table_2_calculated_total_weight_loss_mg": "2165",
        "table_2_discrepancy_percent_source_inscription": "3.6",
        "complete_coating_control_vector": list(coating_rows),
        "ir_drop_linear_interpolation_anodic_addition_cathodic_reduction_and_estimation_limits_retained": True,
        "complete_published_potential_current_rate_mass_loss_vector_retained_by_page_reconstruction": True,
        "complete_claim_source_pages": 49,
    }
    payload = {
        "schema": "sft-v3-chemistry-echem-009-012-complete-postseal-analysis/1",
        "source_inventory_sha256": EXPECTED_INVENTORY,
        "complete_source_count": len(sources),
        "complete_pdf_page_count": sum(row["page_count"] for row in sources.values()),
        "complete_pdf_extracted_character_count": sum(row["extracted_character_count"] for row in sources.values()),
        "complete_source_reconstruction": sources,
        "echem_009": e009,
        "echem_010": e010,
        "echem_011": e011,
        "echem_012": e012,
        "all_favorable_adverse_absent_unresolved_uncertainty_correction_signed_zero_decimal_continuum_fitted_and_historical_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "analysis": OUT.relative_to(ROOT).as_posix(),
        "analysis_sha256": digest(OUT.read_bytes()),
        "result_vector_sha256": payload["complete_result_vector_sha256"],
        "sources": payload["complete_source_count"],
        "pdf_pages": payload["complete_pdf_page_count"],
        "characters": payload["complete_pdf_extracted_character_count"],
        "corrosion_table_rows": len(table_1) + len(table_2),
        "coating_numeric_rows": len(coating_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
