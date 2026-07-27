#!/usr/bin/env python3
"""Capture the complete predeclared KIN-006 branching article and supplements after the value-free seal."""

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
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/competing_channel_capture_spec_v1.json"
SPEC_HASH = "sha256:8ddf07528578576a12867f3c8ccf0d7690567bf59376ccbcde08576bb3731ca2"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-006-competing-channel-v1"
ARTICLE_PATH = SNAPSHOT_ROOT / "PMC11245511-full-text.xml"
SUPPLEMENT_ZIP_PATH = SNAPSHOT_ROOT / "PMC11245511-supplementary-files.zip"
PRIMARY_PATH = SNAPSHOT_ROOT / "competing-channel-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/competing_channel_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/competing_channel_withheld_targets_v1.json"
ARTICLE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11245511/fullTextXML"
SUPPLEMENT_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11245511/supplementaryFiles"


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


def normalized_text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def exact_percent(inscription: str) -> str:
    value = Fraction(int(inscription), 100)
    if value <= 0:
        raise ValueError("KIN-006 branching support must be exact and positive")
    return str(value)


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH:
        raise ValueError("KIN-006 prefetch capture specification changed")
    spec = json.loads(SPEC_PATH.read_text())
    if (
        spec.get("schema") != "sft-v3-competing-channel-prefetch-capture-spec/1"
        or spec.get("all_product_channel_branching_condition_spectrum_uncertainty_analysis_target_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_average_renormalization_digitization_inference_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 1
    ):
        raise ValueError("KIN-006 prefetch boundary is not value-free and complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    article_raw = ARTICLE_PATH.read_bytes() if ARTICLE_PATH.exists() else fetch(ARTICLE_URL)
    supplement_zip_raw = SUPPLEMENT_ZIP_PATH.read_bytes() if SUPPLEMENT_ZIP_PATH.exists() else fetch(SUPPLEMENT_URL)
    ARTICLE_PATH.write_bytes(article_raw)
    SUPPLEMENT_ZIP_PATH.write_bytes(supplement_zip_raw)
    root = ET.fromstring(article_raw)
    article_text = normalized_text(root)
    if "10.1038/s42004-024-01239-7" not in article_text or "propargyl radical gas-phase recombination" not in article_text:
        raise ValueError("KIN-006 primary article identity changed")

    supplementary_files = []
    supplement_pdf_records = []
    with zipfile.ZipFile(io.BytesIO(supplement_zip_raw)) as archive:
        names = archive.namelist()
        if len(names) != 19 or sum(name.lower().endswith(".pdf") for name in names) != 2:
            raise ValueError("KIN-006 supplementary file census changed")
        for name in names:
            if Path(name).name != name or name.startswith("."):
                raise ValueError("KIN-006 unsafe supplementary archive member")
            content = archive.read(name)
            path = SNAPSHOT_ROOT / name
            path.write_bytes(content)
            record = {
                "file_name": name,
                "snapshot_path": str(path.relative_to(ROOT)),
                "snapshot_hash": sha_bytes(content),
                "byte_count": len(content),
            }
            supplementary_files.append(record)
            if name.lower().endswith(".pdf"):
                reader = PdfReader(str(path))
                text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
                text_path = path.with_suffix(".txt")
                text_path.write_text(text, encoding="utf-8")
                supplement_pdf_records.append({
                    **record,
                    "page_count": len(reader.pages),
                    "text_snapshot_path": str(text_path.relative_to(ROOT)),
                    "text_snapshot_hash": sha_file(text_path),
                })

    table_wrap = None
    for element in root.iter("table-wrap"):
        if "Branching ratios of the C3H3" in normalized_text(element):
            if table_wrap is not None:
                raise ValueError("KIN-006 duplicate complete branching table")
            table_wrap = element
    if table_wrap is None:
        raise ValueError("KIN-006 complete experimental branching table absent")
    rows = []
    for tr in table_wrap.iter("tr"):
        cells = [normalized_text(cell) for cell in tr if cell.tag in {"td", "th"}]
        if len(cells) == 3 and "±" in cells[1] and cells[1].endswith("%") and cells[2].endswith("%"):
            match = re.fullmatch(r"([0-9]+)\s*±\s*([0-9]+)%", cells[1])
            calc = re.fullmatch(r"([0-9]+)%", cells[2])
            if match is None or calc is None:
                raise ValueError("KIN-006 branching table exact inscription changed")
            rows.append({
                "source_product_row": len(rows) + 1,
                "product_channel_identity": cells[0],
                "experimental_branching_percent_external_inscription": match.group(1),
                "experimental_branching_exact_fraction_of_complete_support": exact_percent(match.group(1)),
                "experimental_uncertainty_percent_external_inscription": match.group(2),
                "experimental_uncertainty_exact_fraction": exact_percent(match.group(2)),
                "calculated_comparison_percent_external_inscription": calc.group(1),
                "calculated_comparison_exact_fraction": exact_percent(calc.group(1)),
            })
    if len(rows) != 8 or len({row["product_channel_identity"] for row in rows}) != 8:
        raise ValueError("KIN-006 complete eight-channel table changed")
    if sum(Fraction(row["experimental_branching_exact_fraction_of_complete_support"]) for row in rows) != Fraction(1, 1):
        raise ValueError("KIN-006 complete experimental channel support no longer forms one whole")

    shared_identity = {
        "source_id": spec["sources"][0]["source_id"],
        "article_doi": spec["sources"][0]["doi"],
        "reaction_identity": "propargyl-radical-self-recombination",
        "measurement_identity": "mass-selected-threshold-photoelectron-spectroscopy",
        "condition_identity": "held-source-pressure-and-temperature-condition",
        "source_table_identity": "complete-primary-branching-table",
    }
    identities = tuple({
        "target_id": f"KIN-006-PRODUCT-CHANNEL-{row['source_product_row']:02d}",
        **shared_identity,
        "source_product_row": row["source_product_row"],
        "product_channel_identity": row["product_channel_identity"],
    } for row in rows)
    identity_document = {
        "schema": "sft-v3-competing-channel-value-free-target-identities/1",
        "claim_id": spec["claim_id"],
        "prefetch_specification": (str(SPEC_PATH.relative_to(ROOT)), SPEC_HASH),
        "complete_registered_product_channel_count": 8,
        "all_branching_condition_spectrum_uncertainty_analysis_and_target_hash_values_absent": True,
        "rows": identities,
    }
    write_json(IDENTITY_PATH, identity_document)

    targets = tuple({
        **identity,
        "pressure_external_inscription_mbar": "4",
        "temperature_external_inscription": "room-temperature",
        "experimental_branching_percent_external_inscription": row["experimental_branching_percent_external_inscription"],
        "experimental_branching_exact_fraction_of_complete_support": row["experimental_branching_exact_fraction_of_complete_support"],
        "experimental_uncertainty_percent_external_inscription": row["experimental_uncertainty_percent_external_inscription"],
        "experimental_uncertainty_exact_fraction": row["experimental_uncertainty_exact_fraction"],
        "calculated_comparison_percent_external_inscription": row["calculated_comparison_percent_external_inscription"],
        "calculated_comparison_exact_fraction": row["calculated_comparison_exact_fraction"],
        "source_status": "experimentally determined branching ratio with separately retained calculated comparison",
    } for identity, row in zip(identities, rows))
    target_document = {
        "schema": "sft-v3-competing-channel-withheld-targets/1",
        "claim_id": spec["claim_id"],
        "identity_registry_hash": sha_file(IDENTITY_PATH),
        "release_requires_complete_identity_prediction_seal": True,
        "complete_registered_product_channel_count": 8,
        "rows": targets,
    }
    write_json(TARGET_PATH, target_document)

    primary = {
        "schema": "sft-v3-competing-channel-complete-primary-record/1",
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
        "complete_supplementary_file_count": len(supplementary_files),
        "complete_supplementary_files": supplementary_files,
        "supplement_pdf_records": supplement_pdf_records,
        "complete_registered_product_channel_count": len(targets),
        "complete_source_ordered_branching_table": targets,
        "exact_experimental_branching_support_sum": str(sum(Fraction(row["experimental_branching_exact_fraction_of_complete_support"]) for row in rows)),
        "experimental_and_calculated_columns_separated": True,
        "reference_spectrum_Monte_Carlo_and_analysis_disclosures_retained": True,
        "all_article_and_supplement_files_preserved": True,
        "image_curves_not_digitized_and_unreported_values_not_inferred": True,
        "external_values_used_as_proof_parameters": False,
        "imported_probability_normalization_branching_equation_fitted_ratio_selection_renormalization_or_target_correction_used_in_fold_law": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "article_hash": sha_file(ARTICLE_PATH),
        "supplement_archive_hash": sha_file(SUPPLEMENT_ZIP_PATH),
        "identity_registry_hash": sha_file(IDENTITY_PATH),
        "withheld_target_hash": sha_file(TARGET_PATH),
        "primary_record_hash": sha_file(PRIMARY_PATH),
        "complete_product_channel_count": len(targets),
        "complete_supplementary_file_count": len(supplementary_files),
        "complete_supplement_pdf_count": len(supplement_pdf_records),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
