#!/usr/bin/env python3
"""Build complete post-seal ECHEM-002-004 vectors from one preserved NIST PDF."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
PDF = SNAP / "nist-agcl-standard-potential-1954.pdf"
OUT = SNAP / "complete-postseal-analysis-v2.json"
EXPECTED_INVENTORY = "sha256:47e583b3cd375da8f3f8a18b900f581b2189dedd0869a8b96dac5984dba32c7d"
EXPECTED_PDF = "sha256:e1ebb99701a17746d9eb417938e435084c05d0cdaa50642279f54b706d2275ab"

STANDARD_POTENTIAL_ROWS = (
    ("0", "0.23655", "0.02"), ("5", "0.23413", "0.02"), ("10", "0.23142", "0.01"),
    ("15", "0.22857", "0.01"), ("20", "0.22557", "0.02"), ("25", "0.22234", "0.01"),
    ("30", "0.21904", "0.02"), ("35", "0.21565", "0.02"), ("40", "0.21208", "0.03"),
    ("45", "0.20835", "0.03"), ("50", "0.20449", "0.03"), ("55", "0.20056", "0.04"),
    ("60", "0.19649", "0.03"), ("70", "0.18782", "0.04"), ("80", "0.17873", "0.07"),
    ("90", "0.16952", "0.06"), ("95", "0.16511", "0.09"),
)
TEMPERATURES = ("0", "10", "20", "25", "30", "40", "50", "60", "70", "80", "90")
EMF_ROWS = (
    ("0.001", ("0.56330", "0.57019", "0.57631", "0.57909", "0.58178", "0.58683", "0.59125", "0.59525", "0.59860", "0.6015", "0.6043")),
    ("0.002", ("0.53131", "0.53701", "0.54198", "0.54418", "0.54628", "0.55018", "0.55344", "0.55628", "0.55848", "0.5602", "0.5619")),
    ("0.005", ("0.48931", "0.49351", "0.49695", "0.49840", "0.49977", "0.50211", "0.50388", "0.50517", "0.50589", "0.5062", "0.5063")),
    ("0.01", ("0.45787", "0.46091", "0.46323", "0.46412", "0.46493", "0.46613", "0.46678", "0.46694", "0.46655", "0.4657", "0.4648")),
    ("0.02", ("0.42669", "0.42853", "0.42985", "0.43019", "0.43044", "0.43049", "0.43006", "0.42909", "0.42764", "0.4258", "0.4238")),
    ("0.05", ("0.38588", "0.38636", "0.38613", "0.38579", "0.38533", "0.38391", "0.38211", "0.37969", "0.37691", "0.3737", "0.3703")),
    ("0.07", ("0.37094", "0.37089", "0.37016", "0.36957", "0.36885", "0.36691", "0.36461", "0.36174", "0.35848", "0.3548", "0.3509")),
    ("0.1", ("0.35505", "0.35444", "0.35316", "0.35233", "0.35134", "0.34888", "0.34608", "0.34275", "0.33904", "0.3349", "0.3304")),
)
ACTIVITY_ROWS = (
    ("0.001", ("0.9670", "0.9660", "0.9654", "0.9650", "0.9648", "0.9642", "0.9635", "0.9631", "0.962", "0.962", "0.961")),
    ("0.002", ("0.9540", "0.9533", "0.9524", "0.9520", "0.9518", "0.9507", "0.9499", "0.9493", "0.948", "0.947", "0.946")),
    ("0.005", ("0.9313", "0.9299", "0.9289", "0.9283", "0.9274", "0.9268", "0.9252", "0.9249", "0.923", "0.921", "0.920")),
    ("0.01", ("0.9081", "0.9069", "0.9054", "0.9045", "0.9034", "0.9026", "0.9006", "0.9000", "0.898", "0.895", "0.893")),
    ("0.02", ("0.8805", "0.8786", "0.8766", "0.8753", "0.8741", "0.8735", "0.8707", "0.8700", "0.867", "0.863", "0.860")),
    ("0.05", ("0.8381", "0.8357", "0.8331", "0.8308", "0.8291", "0.8283", "0.8239", "0.8227", "0.817", "0.813", "0.810")),
    ("0.07", ("0.8223", "0.8196", "0.8163", "0.8137", "0.8119", "0.8107", "0.8058", "0.8033", "0.797", "0.792", "0.788")),
    ("0.1", ("0.8067", "0.8038", "0.8000", "0.7967", "0.7946", "0.7927", "0.7867", "0.7828", "0.775", "0.769", "0.765")),
)

def digest(payload):
    return "sha256:" + hashlib.sha256(payload).hexdigest()

def exact_pages():
    rows = []
    for number, page in enumerate(PdfReader(PDF).pages, start=1):
        text = "\n".join(line.strip() for line in (page.extract_text() or "").replace("\u00ad", "").splitlines() if line.strip())
        rows.append({"page": number, "complete_extracted_text": text, "text_sha256": digest(text.encode()), "character_count": len(text)})
    return rows

def table_rows(source):
    return [{"molality": molality, "measurements": [{"temperature_celsius_source_inscription": temperature, "value_source_inscription": value} for temperature, value in zip(TEMPERATURES, values)]} for molality, values in source]

def strictly_descending(values):
    return all(Decimal(left) > Decimal(right) for left, right in zip(values, values[1:]))

def main():
    if OUT.exists():
        raise SystemExit("ECHEM-002-004 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY or digest(PDF.read_bytes()) != EXPECTED_PDF:
        raise SystemExit("ECHEM-002-004 source custody changed")
    pages = exact_pages()
    if len(pages) != 8:
        raise SystemExit("complete NIST page count changed")
    complete_text = "\n".join(row["complete_extracted_text"] for row in pages).casefold()
    squashed = "".join(character for character in complete_text if character.isalnum())
    required = ("standard potential", "silver-silver-chloride", "hydrochloric acid", "electromotive-force", "activity coefficient", "least squares")
    if not all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in required):
        raise SystemExit("required NIST surface missing")
    standard = [{"temperature_celsius_source_inscription": t, "observed_standard_potential_absolute_volt_source_inscription": e, "standard_deviation_millivolt_source_inscription": s} for t, e, s in STANDARD_POTENTIAL_ROWS]
    emf, activity = table_rows(EMF_ROWS), table_rows(ACTIVITY_ROWS)
    echem_002 = {
        "claim_id": "SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002",
        "complete_standard_potential_row_count": len(standard),
        "complete_standard_potential_rows": standard,
        "temperature_vector_source_inscriptions": [row[0] for row in STANDARD_POTENTIAL_ROWS],
        "observed_potential_vector_source_inscriptions": [row[1] for row in STANDARD_POTENTIAL_ROWS],
        "standard_deviation_vector_source_inscriptions": [row[2] for row in STANDARD_POTENTIAL_ROWS],
        "all_observed_potentials_strictly_descend_with_temperature": strictly_descending([row[1] for row in STANDARD_POTENTIAL_ROWS]),
        "reference_and_condition_retained": all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in ("standard potential of the cell", "0 to 95 c", "absolute volts")),
        "convention_reversal_retained": "twocommonconventions" in squashed,
        "least_squares_and_adjustable_parameter_provenance_retained": all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in ("least squares", "adjustable parameter")),
        "adverse_cross_study_difference_and_unexplained_result_retained": "nosimplereasonableexplanation" in squashed,
    }
    echem_003 = {
        "claim_id": "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003",
        "cell_source_inscription": "Pt; H2 (g, 1 atm), HCl (m), AgCl; Ag",
        "cell_without_liquid_junction_retained": "withoutliquidjunction" in squashed,
        "two_hydrogen_and_two_silver_chloride_electrodes_retained": all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in ("two hydrogen electrodes", "two silver silver chloride electrodes")),
        "complete_smoothed_emf_row_count": sum(len(row[1]) for row in EMF_ROWS),
        "complete_smoothed_emf_rows": emf,
        "every_fixed_temperature_emf_column_strictly_descends_with_molality": all(strictly_descending([row[1][index] for row in EMF_ROWS]) for index in range(len(TEMPERATURES))),
        "all_values_are_complete_cell_absolute_volt_source_inscriptions": True,
        "measurement_corrections_and_unapplied_corrections_retained": all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in ("corrected to a partial pressure", "corrections were not applied")),
    }
    echem_004 = {
        "claim_id": "SFT-CHEM-CONCENTRATION-DEPENDENT-POTENTIAL-004",
        "complete_molality_count": len(EMF_ROWS),
        "complete_temperature_count": len(TEMPERATURES),
        "complete_emf_measurement_count": sum(len(row[1]) for row in EMF_ROWS),
        "complete_activity_coefficient_measurement_count": sum(len(row[1]) for row in ACTIVITY_ROWS),
        "complete_activity_coefficient_rows": activity,
        "every_fixed_temperature_activity_column_strictly_descends_with_molality": all(strictly_descending([row[1][index] for row in ACTIVITY_ROWS]) for index in range(len(TEMPERATURES))),
        "every_fixed_temperature_emf_column_strictly_descends_with_molality": all(strictly_descending([row[1][index] for row in EMF_ROWS]) for index in range(len(TEMPERATURES))),
        "source_logarithm_Debye_Huckel_least_squares_and_smoothing_models_retained_only_as_external_provenance": all("".join(character for character in fragment if character.isalnum()) in squashed for fragment in ("activity coefficient", "least squares", "smoothed")),
        "source_explicitly_reports_anomalous_or_unexplained_behavior": "anomalous" in squashed and "notbeenexplained" in squashed,
    }
    payload = {
        "schema": "sft-v3-chemistry-echem-002-004-complete-postseal-analysis/1",
        "source_inventory_sha256": EXPECTED_INVENTORY,
        "source_pdf_sha256": EXPECTED_PDF,
        "complete_pdf_page_count": len(pages),
        "complete_pdf_extracted_character_count": sum(row["character_count"] for row in pages),
        "complete_pages_in_order": pages,
        "echem_002": echem_002,
        "echem_003": echem_003,
        "echem_004": echem_004,
        "all_conventional_signed_zero_decimal_continuum_fitted_and_smoothed_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"analysis": OUT.relative_to(ROOT).as_posix(), "analysis_sha256": digest(OUT.read_bytes()), "result_vector_sha256": payload["complete_result_vector_sha256"], "pages": len(pages), "characters": payload["complete_pdf_extracted_character_count"], "standard_potential_rows": len(standard), "emf_measurements": echem_003["complete_smoothed_emf_row_count"], "activity_measurements": echem_004["complete_activity_coefficient_measurement_count"]}, indent=2))

if __name__ == "__main__":
    main()
