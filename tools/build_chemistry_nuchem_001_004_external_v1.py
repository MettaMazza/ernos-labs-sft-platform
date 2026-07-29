#!/usr/bin/env python3
"""Reconstruct the complete post-seal NUCHEM-001–004 source surface."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
OUT = SNAP / "complete-postseal-analysis-v1.json"
EXPECTED_INVENTORY = "sha256:c225880187ffd2839a2dc549b5d5466e91d650e4bc68373dd7674a18df34dc52"

FILES = {
    "general": (
        "nist-radioactivity-srms-general-info-2025.pdf",
        "sha256:5a317028fc096189811926609fb10e08b63079e9f52ab72eca5fae4bf88d3ab7",
        "pdf",
        4,
    ),
    "strontium_90": (
        "nist-srm-4239a-strontium-90.pdf",
        "sha256:e8f3f5397db147ce57a270c25e4fd655ca6bacc5b8e6652e3a3df57c36ea346e",
        "pdf",
        4,
    ),
    "uranium_232": (
        "nist-srm-4324c-uranium-232.html",
        "sha256:ab8ce95a445b7c665187d5d347ff57fa06e94082aa9177c09ec2df8c77433a23",
        "html",
        1,
    ),
    "nuclear_data": (
        "nist-nuclear-physics-data.html",
        "sha256:941be0198b93685269bab074e5f25ddf903fb11ea48d8ef789229f1591ec3862",
        "html",
        1,
    ),
}


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


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
    parser = _VisibleText()
    parser.feed(path.read_text(errors="strict"))
    text = clean_lines("\n".join(parser.parts))
    return [{"document": 1, "character_count": len(text), "text_sha256": digest(text.encode())}], text


def compact(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def require(text: str, fragments: tuple[str, ...], source: str) -> None:
    normalized = compact(text)
    missing = [fragment for fragment in fragments if compact(fragment) not in normalized]
    if missing:
        raise SystemExit(f"required {source} evidence missing: {missing}")


def main() -> None:
    if OUT.exists():
        raise SystemExit("NUCHEM-001–004 analysis already exists; rebuild prohibited")
    if digest(INVENTORY.read_bytes()) != EXPECTED_INVENTORY:
        raise SystemExit("NUCHEM-001–004 source inventory changed")

    sources, texts = {}, {}
    for key, (name, expected, kind, expected_units) in FILES.items():
        path = SNAP / name
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"registered source bytes changed: {key}")
        vector, text = pdf_surface(path) if kind == "pdf" else html_surface(path)
        if len(vector) != expected_units:
            raise SystemExit(f"registered source unit count changed: {key}")
        sources[key] = {
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_sha256": expected,
            "surface_kind": kind,
            "surface_unit_count": len(vector),
            "extracted_character_count": sum(row["character_count"] for row in vector),
            "complete_surface_vector": vector,
        }
        texts[key] = text

    require(texts["general"], ("number of atoms", "average number of nuclear transformations per second", "half-life", "probability per decay", "one nuclear transformation per second", "quantitative statement of its uncertainty"), "general information")
    require(texts["strontium_90"], ("Strontium-90", "29.492", "0.088", "25 December 2019", "0.30 %", "90Sr/90Y equilibrium", "25 μg", "34 μg", "1.02 mol", "28.80", "2.6684", "12.312", "144 results"), "strontium-90 certificate")
    require(texts["uranium_232"], ("Uranium-232 is an isotope of uranium", "212 Pb", "212 Bi", "208 Tl", "212 Po", "300 ± 2", "26.30", "0.23", "in equilibrium with its progeny", "0.66", "0.30", "0.84"), "uranium-232 record")
    require(texts["nuclear_data"], ("isotopic compositions or abundances", "elements 1 through 112", "relative atomic masses"), "nuclear data")

    sr_uncertainty = [
        {"component": "LS measurement precision", "relative_standard_uncertainty_percent": "0.042", "assessment": "A", "record": "144 results; Normal distribution"},
        {"component": "90Sr/90Y disequilibrium", "relative_standard_uncertainty_percent": "0.02", "assessment": "B"},
        {"component": "gravimetric mass measurements", "relative_standard_uncertainty_percent": "0.06", "assessment": "B"},
        {"component": "live-time determination", "relative_standard_uncertainty_percent": "0.07", "assessment": "B"},
        {"component": "90Sr decay correction", "relative_standard_uncertainty_percent": "0.0002", "assessment": "B"},
        {"component": "90Sr/90Y equilibrium ratio", "relative_standard_uncertainty_percent": "0.00006", "assessment": "B"},
        {"component": "3H decay correction", "relative_standard_uncertainty_percent": "0.0004", "assessment": "B"},
        {"component": "3H standard massic activity", "relative_standard_uncertainty_percent": "0.035", "assessment": "B"},
        {"component": "90Sr and 90Y nuclear data", "relative_standard_uncertainty_percent": "<0.01", "assessment": "B"},
        {"component": "computed beta detection efficiencies", "relative_standard_uncertainty_percent": "<0.1", "assessment": "B"},
        {"component": "combined standard uncertainty", "relative_standard_uncertainty_percent": "0.15"},
        {"component": "expanded uncertainty", "relative_standard_uncertainty_percent": "0.30", "coverage_factor": "2"},
    ]
    u_confirmations = [
        {"comparison": "CNET re-standardization versus decay-corrected SRM 4324b", "agreement_percent": "0.66"},
        {"comparison": "LS comparative measurement versus CNET", "agreement_percent": "0.30"},
        {"comparison": "gamma-ray spectrometry versus CNET", "agreement_percent": "0.84"},
    ]

    nuchem_001 = {
        "claim_id": "SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001",
        "element_identity_surface": "NIST isotopic-composition database covers elements 1 through 112, 114 and 116",
        "complete_nuclide_identity_vector": ["90Sr", "90Y", "3H", "232U", "232Th", "233U", "208Tl", "212Pb", "212Bi", "212Po"],
        "nuclear_state_custody": "source nuclide inscriptions retained exactly; no unreported ground/metastable state inferred",
        "chemical_carrier": "approximately 5 mL standardized 90Sr solution in a stable homogeneous matrix",
        "complete_solution_composition_vector": ["nominal 25 μg·g-1 Sr+2", "nominal 34 μg·g-1 Y+3", "1.02 mol·L-1 HCl"],
        "complete_phase_matrix_vector": ["solution", "liquid", "flame-sealed borosilicate-glass ampoule", "acidic matrix"],
        "amount_forms": ["number of atoms", "activity", "emission rate", "solution quantity per gram of liquid"],
        "certified_massic_activity": {"nuclide": "90Sr", "value": "29.492", "expanded_uncertainty": "0.088", "unit": "kBq·g-1", "coverage_factor": "2", "relative_expanded_uncertainty_percent": "0.30", "reference_time": "1200 EST, 25 December 2019"},
        "complete_uncertainty_vector": sr_uncertainty,
        "noncertified_values_distinguished_from_certified_values": True,
        "complete_registered_source_surface_retained": True,
    }
    nuchem_002 = {
        "claim_id": "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002",
        "parent_daughter_vector": [{"parent": "90Sr", "daughter": "90Y"}, {"parent": "232U", "daughter_or_progeny": "212Pb"}, {"parent": "212Pb", "daughter_or_progeny": "212Bi"}, {"parent": "212Bi", "daughter_or_progeny": "212Po and 208Tl"}],
        "parent_daughter_chemical_states": ["Sr+2 in HCl solution", "Y+3 in HCl solution", "232U standard material with progeny"],
        "channel_identity_vector": ["alpha emitters in 232U decay chain", "beta-emitting 212Pb", "beta-emitting 212Bi", "beta-emitting 208Tl", "short-lived 212Po daughter with 212Bi parent"],
        "complete_directed_network_retained": True,
        "equilibrium_records": ["90Sr in radioactive equilibrium with 90Y", "232U in equilibrium with its progeny"],
        "method_assumption_vector": ["alpha emitters assumed detected with 100 % efficiency", "212Po and 212Bi assumed combined 100 % efficiency", "simplified decay scheme used for 212Pb, 212Bi and 208Tl"],
        "complete_confirmatory_comparison_vector": u_confirmations,
        "all_source_disagreements_and_assumptions_retained": True,
        "complete_registered_source_surface_retained": True,
    }
    nuchem_003 = {
        "claim_id": "SFT-CHEM-ACTIVITY-AMOUNT-TIME-003",
        "identity_and_chemical_form_retained": True,
        "amount_forms": ["number of atoms", "mass", "activity", "emission rate", "per gram of liquid"],
        "activity_definition": "average number of nuclear transformations per second",
        "becquerel_definition": "one nuclear transformation per second",
        "curie_correspondence": {"curie": "1", "becquerel": "3.7 x 10^10"},
        "half_life_relation": "if half-life is known, number of atoms or mass can be calculated from activity and vice versa",
        "reference_time_vector": ["1200 EST, 25 December 2019", "1200 EST, 31 October 2022"],
        "complete_massic_activity_vector": [{"nuclide": "90Sr", "value": "29.492", "expanded_uncertainty": "0.088", "unit": "kBq·g-1", "coverage_factor": "2"}, {"nuclide": "232U", "value": "26.30", "expanded_uncertainty": "0.23", "unit": "Bq·g-1", "coverage_factor": "2"}],
        "complete_half_life_vector": [{"nuclide": "90Sr", "value": "28.80", "uncertainty": "0.07", "unit": "a"}, {"nuclide": "90Y", "value": "2.6684", "uncertainty": "0.0013", "unit": "d"}, {"nuclide": "3H", "value": "12.312", "uncertainty": "0.025", "unit": "a"}],
        "decay_correction_and_reference_time_retained": True,
        "complete_uncertainty_vector": sr_uncertainty,
        "external_decimal_signed_zero_and_continuum_inscriptions_are_downstream_measurement_provenance_only": True,
        "complete_registered_source_surface_retained": True,
    }
    nuchem_004 = {
        "claim_id": "SFT-CHEM-RADIOACTIVE-BRANCHING-CHEMICAL-YIELD-004",
        "complete_channel_vector": ["alpha chain", "212Pb beta", "212Bi beta", "208Tl beta", "212Bi–212Po combined detection"],
        "complete_daughter_vector": ["212Pb", "212Bi", "208Tl", "212Po"],
        "probability_per_decay_relation": "emission rate is calculated from activity when the fraction of decays producing the radiation is known",
        "numeric_probability_per_decay_rows_in_registered_sources": "absent__source_says_suggested_values_usually_accompany_each_SRM_or_are_available_from_NIST",
        "chemical_recovery_custody": "SRM 4239a is intended for monitoring radiochemical procedures; complete certified and non-certified chemical carrier records retained",
        "partition_support": "all reported 232U progeny and all stated decay/detection channels retained without renormalizing after omission",
        "primary_method_vector": ["4παβ liquid-scintillation spectrometry", "CIEMAT/NIST efficiency tracing", "composition-matched 3H cocktails", "MICELLE2 calculated beta efficiencies"],
        "complete_confirmatory_method_vector": ["two commercial LS counters", "two LS measurement systems", "two LS cocktail compositions", "live-timed anticoincidence reference", "gamma-ray spectrometry"],
        "complete_assumption_discrepancy_uncertainty_vector": {"assumptions": nuchem_002["method_assumption_vector"], "confirmations": u_confirmations, "sr90_uncertainties": sr_uncertainty},
        "unavailable_numeric_branch_fractions_preserved_as_unavailable_not_fabricated": True,
        "complete_registered_source_surface_retained": True,
    }

    payload = {
        "schema": "sft-v3-chemistry-nuchem-001-004-complete-postseal-analysis/1",
        "source_inventory_sha256": EXPECTED_INVENTORY,
        "complete_source_count": len(sources),
        "complete_pdf_page_count": sum(row["surface_unit_count"] for row in sources.values() if row["surface_kind"] == "pdf"),
        "complete_html_document_count": sum(row["surface_unit_count"] for row in sources.values() if row["surface_kind"] == "html"),
        "complete_extracted_character_count": sum(row["extracted_character_count"] for row in sources.values()),
        "complete_source_reconstruction": sources,
        "nuchem_001": nuchem_001,
        "nuchem_002": nuchem_002,
        "nuchem_003": nuchem_003,
        "nuchem_004": nuchem_004,
        "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({
        "analysis": OUT.relative_to(ROOT).as_posix(),
        "analysis_sha256": digest(OUT.read_bytes()),
        "result_vector_sha256": payload["complete_result_vector_sha256"],
        "sources": payload["complete_source_count"],
        "pdf_pages": payload["complete_pdf_page_count"],
        "html_documents": payload["complete_html_document_count"],
        "characters": payload["complete_extracted_character_count"],
        "sr90_uncertainty_rows": len(sr_uncertainty),
        "u232_confirmatory_rows": len(u_confirmations),
    }, indent=2))


if __name__ == "__main__":
    main()
