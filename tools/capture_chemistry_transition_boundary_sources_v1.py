#!/usr/bin/env python3
"""Capture the complete predeclared KIN-005 article and supplement after the value-free seal."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/transition_boundary_capture_spec_v1.json"
SPEC_HASH = "sha256:b0f0bd0c2e044f7ffa8cd936cf44f2e6fef5215a1ffd5fde51009fa2181ea9b3"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-005-transition-boundary-v1"
ARTICLE_PATH = SNAPSHOT_ROOT / "PMC4073644-full-text.xml"
SUPPLEMENT_ZIP_PATH = SNAPSHOT_ROOT / "PMC4073644-supplementary-files.zip"
SUPPLEMENT_PDF_PATH = SNAPSHOT_ROOT / "nn500703k_si_001.pdf"
SUPPLEMENT_TEXT_PATH = SNAPSHOT_ROOT / "nn500703k_si_001.txt"
PRIMARY_PATH = SNAPSHOT_ROOT / "transition-boundary-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/transition_boundary_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/transition_boundary_withheld_targets_v1.json"
ARTICLE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4073644/fullTextXML"
SUPPLEMENT_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4073644/supplementaryFiles"


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=120) as response:
        return response.read()


def exact_decimal(text: str) -> str:
    value = Fraction(text)
    if value <= 0:
        raise ValueError("KIN-005 measured magnitude must be exact and positive")
    return str(value)


def normalized_text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def required_match(pattern: str, text: str, label: str, flags: int = 0) -> re.Match[str]:
    match = re.search(pattern, text, flags)
    if match is None:
        raise ValueError(f"KIN-005 source no longer exposes {label}")
    return match


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH:
        raise ValueError("KIN-005 prefetch capture specification changed")
    spec = json.loads(SPEC_PATH.read_text())
    if (
        spec.get("schema") != "sft-v3-transition-boundary-prefetch-capture-spec/1"
        or spec.get("all_isotope_barrier_rate_temperature_exposure_uncertainty_figure_table_caption_target_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_average_digitization_inference_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 1
    ):
        raise ValueError("KIN-005 prefetch boundary is not value-free and complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    article_raw = ARTICLE_PATH.read_bytes() if ARTICLE_PATH.exists() else fetch(ARTICLE_URL)
    supplement_zip_raw = SUPPLEMENT_ZIP_PATH.read_bytes() if SUPPLEMENT_ZIP_PATH.exists() else fetch(SUPPLEMENT_URL)
    ARTICLE_PATH.write_bytes(article_raw)
    SUPPLEMENT_ZIP_PATH.write_bytes(supplement_zip_raw)

    root = ET.fromstring(article_raw)
    article_text = normalized_text(root)
    if "10.1021/nn500703k" not in article_text or "Significant Quantum Effects in Hydrogen Activation" not in article_text:
        raise ValueError("KIN-005 primary article identity changed")

    supplementary_files = []
    with zipfile.ZipFile(io.BytesIO(supplement_zip_raw)) as archive:
        names = archive.namelist()
        if "nn500703k_si_001.pdf" not in names:
            raise ValueError("KIN-005 complete supplement PDF is absent")
        if len(names) != 13:
            raise ValueError("KIN-005 supplementary file census changed")
        for name in names:
            if Path(name).name != name or name.startswith("."):
                raise ValueError("KIN-005 unsafe supplementary archive member")
            content = archive.read(name)
            path = SNAPSHOT_ROOT / name
            path.write_bytes(content)
            supplementary_files.append({
                "file_name": name,
                "snapshot_path": str(path.relative_to(ROOT)),
                "snapshot_hash": sha_bytes(content),
                "byte_count": len(content),
            })

    if not SUPPLEMENT_PDF_PATH.exists() or SUPPLEMENT_PDF_PATH.read_bytes()[:4] != b"%PDF":
        raise ValueError("KIN-005 supplement is not a PDF")
    reader = PdfReader(str(SUPPLEMENT_PDF_PATH))
    supplement_text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    SUPPLEMENT_TEXT_PATH.write_text(supplement_text, encoding="utf-8")
    supplement_text = SUPPLEMENT_TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    if "SUPPORTING INFORMATION" not in supplement_text or "Table S1" not in supplement_text:
        raise ValueError("KIN-005 supplement text boundary changed")

    method = required_match(r"using temperature-programmed desorption \(TPD\)", article_text, "experimental method").group(0)
    temperature = required_match(r"temperature in the range of ([0-9]+)[–-]([0-9]+) K", article_text, "experimental temperature range")
    exposure = required_match(
        r"exposure of ([0-9]+) L of molecular hydrogen.*?exposure of ([0-9]+) L of molecular deuterium",
        article_text,
        "complete H2/D2 exposure identity",
    )
    barriers = required_match(
        r"deuterium, the apparent activation energy was found to be ([0-9.]+) ± ([0-9.]+) eV, and for hydrogen it was [−-]([0-9.]+) ± ([0-9.]+) eV",
        article_text,
        "measured isotope barrier pair",
    )
    if barriers.group(2) != barriers.group(4):
        raise ValueError("KIN-005 measured uncertainty pair changed")
    direction = required_match(
        r"uptake of hydrogen decreases when the temperature is raised, while deuterium.s uptake increases at higher sample temperature",
        article_text,
        "measured opposite isotope direction",
    ).group(0)

    shared = {
        "source_id": spec["sources"][0]["source_id"],
        "article_doi": spec["sources"][0]["doi"],
        "material_system_identity": "declared-isolated-Pd-atom-on-Cu-surface",
        "experimental_method_identity": "temperature-programmed-desorption",
        "source_figure_identity": "Figure-1-a-through-c",
    }
    identities = (
        {
            "target_id": "KIN-005-H2-EXPERIMENTAL-BOUNDARY-SIGNATURE",
            **shared,
            "isotopologue_identity": "H2",
            "exposure_identity": "source-hydrogen-exposure",
        },
        {
            "target_id": "KIN-005-D2-EXPERIMENTAL-BOUNDARY-SIGNATURE",
            **shared,
            "isotopologue_identity": "D2",
            "exposure_identity": "source-deuterium-exposure",
        },
    )
    identity_document = {
        "schema": "sft-v3-transition-boundary-value-free-target-identities/1",
        "claim_id": spec["claim_id"],
        "prefetch_specification": (str(SPEC_PATH.relative_to(ROOT)), SPEC_HASH),
        "complete_experimental_isotopologue_count": 2,
        "all_isotope_barrier_rate_temperature_exposure_uncertainty_caption_and_target_hash_values_absent": True,
        "rows": identities,
    }
    write_json(IDENTITY_PATH, identity_document)

    d_barrier, uncertainty, h_barrier = barriers.group(1), barriers.group(2), barriers.group(3)
    targets = (
        {
            **identities[0],
            "surface_coverage_external_inscription_ML": "0.01",
            "temperature_range_K_external_inscription": [temperature.group(1), temperature.group(2)],
            "exposure_L_external_inscription": exposure.group(1),
            "uptake_temperature_order_signature": "uptake-decreases-as-temperature-is-raised",
            "apparent_barrier_external_signed_inscription_eV": "−" + h_barrier,
            "apparent_barrier_external_magnitude_exact_fraction_eV": exact_decimal(h_barrier),
            "apparent_barrier_orientation": "reverse-held-temperature-order",
            "uncertainty_external_inscription_eV": uncertainty,
            "uncertainty_exact_fraction_eV": exact_decimal(uncertainty),
            "source_status": "experimentally measured TPD uptake and source-reported apparent barrier",
        },
        {
            **identities[1],
            "surface_coverage_external_inscription_ML": "0.01",
            "temperature_range_K_external_inscription": [temperature.group(1), temperature.group(2)],
            "exposure_L_external_inscription": exposure.group(2),
            "uptake_temperature_order_signature": "uptake-increases-as-temperature-is-raised",
            "apparent_barrier_external_signed_inscription_eV": d_barrier,
            "apparent_barrier_external_magnitude_exact_fraction_eV": exact_decimal(d_barrier),
            "apparent_barrier_orientation": "held-temperature-order",
            "uncertainty_external_inscription_eV": uncertainty,
            "uncertainty_exact_fraction_eV": exact_decimal(uncertainty),
            "source_status": "experimentally measured TPD uptake and source-reported apparent barrier",
        },
    )
    target_document = {
        "schema": "sft-v3-transition-boundary-withheld-targets/1",
        "claim_id": spec["claim_id"],
        "identity_registry_hash": sha_file(IDENTITY_PATH),
        "release_requires_complete_identity_prediction_seal": True,
        "complete_experimental_isotopologue_count": 2,
        "rows": targets,
    }
    write_json(TARGET_PATH, target_document)

    primary = {
        "schema": "sft-v3-transition-boundary-complete-primary-record/1",
        "claim_id": spec["claim_id"],
        "prefetch_specification": (str(SPEC_PATH.relative_to(ROOT)), SPEC_HASH),
        "article": {
            "retrieval_url": ARTICLE_URL,
            "snapshot_path": str(ARTICLE_PATH.relative_to(ROOT)),
            "snapshot_hash": sha_file(ARTICLE_PATH),
            "byte_count": ARTICLE_PATH.stat().st_size,
        },
        "supplement_archive": {
            "retrieval_url": SUPPLEMENT_URL,
            "snapshot_path": str(SUPPLEMENT_ZIP_PATH.relative_to(ROOT)),
            "snapshot_hash": sha_file(SUPPLEMENT_ZIP_PATH),
            "byte_count": SUPPLEMENT_ZIP_PATH.stat().st_size,
        },
        "supplement_text": {
            "snapshot_path": str(SUPPLEMENT_TEXT_PATH.relative_to(ROOT)),
            "snapshot_hash": sha_file(SUPPLEMENT_TEXT_PATH),
        },
        "complete_supplementary_file_count": len(supplementary_files),
        "complete_supplementary_files": supplementary_files,
        "complete_experimental_target_count": len(targets),
        "complete_experimental_targets": targets,
        "reported_experimental_method_record": method,
        "reported_experimental_opposite_direction_record": direction,
        "calculated_fitted_and_interpretive_records_retained_but_excluded_from_measurement_targets": {
            "source_reports_classical_DFT_and_zero_point_corrected_barriers": True,
            "source_reports_path_integral_and_harmonic_quantum_transition_state_calculations": True,
            "source_reports_kinetic_Monte_Carlo_results": True,
            "source_discloses_systematic_model_parameter_adjustments_for_agreement": True,
            "source_discloses_fitted_or_assumed_model_parameters_in_supplement_Table_S1": True,
            "none_used_as_experimental_measurement_or_fold_law_parameter": True,
        },
        "all_article_and_supplement_files_preserved": True,
        "experimental_and_calculated_provenance_separated": True,
        "image_curves_not_digitized_and_unreported_values_not_inferred": True,
        "external_signed_barrier_inscriptions_preserved_only_as_source_provenance": True,
        "negative_number_used_in_fold_proof": False,
        "transition_state_geometry_saddle_continuum_conventional_kie_equation_arrhenius_prefactor_fitted_barrier_selection_or_target_correction_used_in_fold_law": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "article_hash": sha_file(ARTICLE_PATH),
        "supplement_archive_hash": sha_file(SUPPLEMENT_ZIP_PATH),
        "supplement_pdf_hash": sha_file(SUPPLEMENT_PDF_PATH),
        "identity_registry_hash": sha_file(IDENTITY_PATH),
        "withheld_target_hash": sha_file(TARGET_PATH),
        "primary_record_hash": sha_file(PRIMARY_PATH),
        "complete_experimental_target_count": len(targets),
        "complete_supplementary_file_count": len(supplementary_files),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
