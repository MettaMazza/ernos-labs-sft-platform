#!/usr/bin/env python3
"""Capture the complete predeclared KIN-007 source surface after its value-free identity seal."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import shlex
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/sequential_mechanism_capture_spec_v1.json"
SPEC_HASH = "sha256:63c2480e05d202d88cfec0268e53d8160cd727a6bee88bd8304f37cd74989f3b"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/sequential_mechanism_target_identities_v1.json"
IDENTITY_HASH = "sha256:0022b0988832e714876f66ad53c6dc5d4f5324866be0ebfdc59f98e14dae5872"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/sequential_mechanism_withheld_targets_v1.json"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-007-sequential-mechanism-v1"
ARTICLE_PATH = SNAPSHOT_ROOT / "PMC11217357-full-text.xml"
SUPPLEMENT_ZIP_PATH = SNAPSHOT_ROOT / "PMC11217357-supplementary-files.zip"
PRIMARY_PATH = SNAPSHOT_ROOT / "sequential-mechanism-primary-records-v1.json"
CXIDB_PATH = SNAPSHOT_ROOT / "cxidb-221-custody-record-v1.json"
ARTICLE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11217357/fullTextXML"
SUPPLEMENT_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11217357/supplementaryFiles"
PDB_IDENTITIES = ("8WZF", "8WZG", "8WZR", "8WZT", "8WZV")


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


def exact_decimal(inscription: str) -> str:
    value = Fraction(inscription)
    if value <= 0:
        raise ValueError("KIN-007 exact magnitude must be positive")
    return str(value)


def atom_site_rows(cif_text: str) -> tuple[dict[str, str], ...]:
    lines = cif_text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("_atom_site."))
    headers = []
    index = start
    while index < len(lines) and lines[index].startswith("_atom_site."):
        headers.append(lines[index].strip())
        index += 1
    rows = []
    while index < len(lines) and lines[index].strip() != "#":
        if lines[index].strip():
            values = shlex.split(lines[index], posix=True)
            if len(values) != len(headers):
                raise ValueError("KIN-007 PDB atom-site row width changed")
            rows.append(dict(zip(headers, values)))
        index += 1
    if not rows:
        raise ValueError("KIN-007 PDB atom-site loop absent")
    return tuple(rows)


def exact_observed_feature(inscription: str) -> dict[str, object]:
    if inscription == "0":
        return {
            "external_inscription": "0",
            "sft_interpretation": "structural-EmptyOne-observed-absence",
            "exact_positive_magnitude_present": False,
        }
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*\(\s*([0-9]+(?:\.[0-9]+)?)\s*\)", inscription)
    if match is None:
        raise ValueError(f"KIN-007 unrecognized exact density feature: {inscription}")
    return {
        "sigma_external_inscription": match.group(1),
        "sigma_exact_positive_fraction": exact_decimal(match.group(1)),
        "electron_density_external_inscription": match.group(2),
        "electron_density_exact_positive_fraction": exact_decimal(match.group(2)),
        "orientation": "held-negative-difference-density-direction-with-exact-positive-magnitude",
        "exact_positive_magnitude_present": True,
    }


def parse_power_table(page_text: str) -> tuple[dict[str, object], ...]:
    compact = " ".join(page_text.split())
    if "Supplementary Table 4. Measured changes in the difference density features during power titration" not in compact:
        raise ValueError("KIN-007 complete power-titration table absent")
    boundaries = (
        ("Scale", "Mn"), ("Mn", "COax"), ("COax", "COeq1"),
        ("COeq1", "COeq2"), ("COeq2", "The values were obtained"),
    )
    segments = {}
    for left, right in boundaries:
        match = re.search(re.escape(left) + r"(.*?)" + re.escape(right), compact)
        if match is None:
            raise ValueError(f"KIN-007 power table boundary changed: {left}")
        segments[left] = match.group(1)
    scales = re.findall(r"[0-9]+\.[0-9]+", segments["Scale"])[-7:]
    pair_or_absence = re.compile(r"[0-9]+(?:\.[0-9]+)?\s*\(\s*[0-9]+(?:\.[0-9]+)?\s*\)|(?<![0-9.])0(?![0-9.])")
    vectors = {name: pair_or_absence.findall(segments[name])[-7:] for name in ("Mn", "COax", "COeq1", "COeq2")}
    if len(scales) != 7 or any(len(values) != 7 for values in vectors.values()):
        raise ValueError("KIN-007 complete seven-column power vector changed")
    conditions = (
        ("10 ns", "10 microjoule", "1/100000000", "1/100000"),
        ("10 ns", "20 microjoule", "1/100000000", "1/50000"),
        ("10 ns", "40 microjoule", "1/100000000", "1/25000"),
        ("1 microsecond", "10 microjoule", "1/1000000", "1/100000"),
        ("1 microsecond", "20 microjoule", "1/1000000", "1/50000"),
        ("1 microsecond", "40 microjoule", "1/1000000", "1/25000"),
        ("1 microsecond", "60 microjoule", "1/1000000", "3/50000"),
    )
    return tuple({
        "power_table_column": ordinal,
        "delay_external_inscription": condition[0],
        "power_external_inscription": condition[1],
        "delay_second_exact_fraction": condition[2],
        "power_joule_exact_fraction": condition[3],
        "scale_external_inscription_electron_per_cubic_angstrom_per_sigma": scales[ordinal - 1],
        "scale_exact_positive_fraction": exact_decimal(scales[ordinal - 1]),
        "measured_difference_density_features": {
            name: exact_observed_feature(vectors[name][ordinal - 1])
            for name in ("Mn", "COax", "COeq1", "COeq2")
        },
        "source_status": "experimentally measured complete power-titration column",
    } for ordinal, condition in enumerate(conditions, start=1))


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH or sha_file(IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-007 prefetch or value-free identity seal changed")
    spec = json.loads(SPEC_PATH.read_text())
    identities_document = json.loads(IDENTITY_PATH.read_text())
    identities = tuple(identities_document.get("rows", ()))
    if (
        spec.get("schema") != "sft-v3-sequential-mechanism-prefetch-capture-spec/1"
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_average_interpolation_inference_or_correction_permitted") is not False
        or identities_document.get("complete_registered_target_count") != 17
        or identities_document.get("target_values_or_hashes_present") is not False
        or identities_document.get("all_time_power_coordinate_occupancy_density_resolution_statistic_intermediate_assignment_target_and_target_hash_values_absent") is not True
        or tuple(row["source_row"] for row in identities) != tuple(range(1, 18))
    ):
        raise ValueError("KIN-007 value-free registration boundary changed")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    article_raw = ARTICLE_PATH.read_bytes() if ARTICLE_PATH.exists() else fetch(ARTICLE_URL)
    supplement_zip_raw = SUPPLEMENT_ZIP_PATH.read_bytes() if SUPPLEMENT_ZIP_PATH.exists() else fetch(SUPPLEMENT_URL)
    ARTICLE_PATH.write_bytes(article_raw)
    SUPPLEMENT_ZIP_PATH.write_bytes(supplement_zip_raw)
    root = ET.fromstring(article_raw)
    article_text = normalized_text(root)
    required_article_fragments = (
        "10.1038/s41467-024-49814-9",
        "Real-time observation of a metal complex-driven reaction intermediate",
        "Atomic models and map coefficients were deposited to the Protein Data Bank",
        "Raw diffraction images of all the structures used in this paper were deposited to CXIDB with accession ID 221",
        "10.11577/2203883",
        "BSM00067",
    )
    if any(fragment not in article_text for fragment in required_article_fragments):
        raise ValueError("KIN-007 complete primary article identity or custody declaration changed")

    supplementary_files = []
    supplement_pdf_records = []
    pdf_text_by_name = {}
    with zipfile.ZipFile(io.BytesIO(supplement_zip_raw)) as archive:
        names = archive.namelist()
        if len(names) != 13 or sum(name.lower().endswith(".pdf") for name in names) != 3:
            raise ValueError("KIN-007 supplementary file census changed")
        for name in names:
            if Path(name).name != name or name.startswith("."):
                raise ValueError("KIN-007 unsafe supplementary archive member")
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
                pages = tuple((page.extract_text() or "") for page in reader.pages)
                text = "\n\n".join(pages)
                text_path = path.with_suffix(".txt")
                text_path.write_text(text, encoding="utf-8")
                pdf_text_by_name[name] = pages
                supplement_pdf_records.append({
                    **record,
                    "page_count": len(reader.pages),
                    "text_snapshot_path": str(text_path.relative_to(ROOT)),
                    "text_snapshot_hash": sha_file(text_path),
                })
    main_supplement_name = "41467_2024_49814_MOESM1_ESM.pdf"
    peer_review_name = "41467_2024_49814_MOESM2_ESM.pdf"
    reporting_name = "41467_2024_49814_MOESM3_ESM.pdf"
    if set(pdf_text_by_name) != {main_supplement_name, peer_review_name, reporting_name}:
        raise ValueError("KIN-007 supplementary PDF identities changed")
    main_pages = pdf_text_by_name[main_supplement_name]
    if len(main_pages) != 51 or len(pdf_text_by_name[peer_review_name]) != 34 or len(pdf_text_by_name[reporting_name]) != 3:
        raise ValueError("KIN-007 supplementary PDF page census changed")
    power_rows = parse_power_table(main_pages[40])

    structure_conditions = {
        "8WZF": ("complete darkness", "structural-EmptyOne-no-elapsed-number", "structural-EmptyOne-no-pump-power"),
        "8WZG": ("10 ns after photoexcitation; 20 microjoule", "1/100000000", "1/50000"),
        "8WZR": ("100 ns after photoexcitation; 20 microjoule", "1/10000000", "1/50000"),
        "8WZT": ("1 microsecond after photoexcitation; 20 microjoule", "1/1000000", "1/50000"),
        "8WZV": ("1 microsecond after photoexcitation; 40 microjoule", "1/1000000", "1/25000"),
    }
    expected_xtx = {
        "8WZF": ({"C": 3, "O": 3, "MN": 1}, "1", "Mn-tricarbonyl-reactant"),
        "8WZG": ({"C": 2, "O": 2, "MN": 1}, "9/10", "Mn-biscarbonyl-first-retained-intermediate"),
        "8WZR": ({"C": 2, "O": 2, "MN": 1}, "9/10", "Mn-biscarbonyl-first-retained-intermediate"),
        "8WZT": ({"C": 2, "O": 2, "MN": 1}, "17/20", "Mn-biscarbonyl-first-retained-intermediate"),
        "8WZV": ({"C": 1, "O": 1, "MN": 1}, "13/20", "Mn-monocarbonyl-second-retained-intermediate"),
    }
    pdb_records = []
    for pdb_id in PDB_IDENTITIES:
        cif_path = SNAPSHOT_ROOT / f"{pdb_id}.cif"
        api_path = SNAPSHOT_ROOT / f"{pdb_id}-rcsb-entry.json"
        cif_raw = cif_path.read_bytes() if cif_path.exists() else fetch(f"https://files.rcsb.org/download/{pdb_id}.cif")
        api_raw = api_path.read_bytes() if api_path.exists() else fetch(f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}")
        cif_path.write_bytes(cif_raw)
        api_path.write_bytes(api_raw)
        api = json.loads(api_raw)
        atoms = tuple(row for row in atom_site_rows(cif_raw.decode("utf-8")) if row["_atom_site.label_comp_id"] == "XTX")
        counts = {symbol: sum(row["_atom_site.type_symbol"] == symbol for row in atoms) for symbol in ("C", "O", "MN")}
        occupancies = {str(Fraction(row["_atom_site.occupancy"])) for row in atoms}
        expected_counts, expected_occupancy, state_identity = expected_xtx[pdb_id]
        if counts != expected_counts or occupancies != {expected_occupancy}:
            raise ValueError(f"KIN-007 deposited structure changed: {pdb_id}")
        resolution = tuple(api.get("rcsb_entry_info", {}).get("resolution_combined", ()))
        if resolution != (1.6,):
            raise ValueError(f"KIN-007 deposited resolution changed: {pdb_id}")
        condition, elapsed, power = structure_conditions[pdb_id]
        pdb_records.append({
            "pdb_identity": pdb_id,
            "source_title": api.get("struct", {}).get("title"),
            "source_condition_external_inscription": condition,
            "elapsed_second_exact_fraction_or_EmptyOne": elapsed,
            "pump_power_joule_exact_fraction_or_EmptyOne": power,
            "resolution_angstrom_external_inscription": "1.6",
            "resolution_angstrom_exact_fraction": "8/5",
            "XTX_component_exact_atom_counts": counts,
            "XTX_component_exact_occupancy": expected_occupancy,
            "experimentally_retained_state_identity": state_identity,
            "cif_snapshot_path": str(cif_path.relative_to(ROOT)),
            "cif_snapshot_hash": sha_file(cif_path),
            "rcsb_entry_snapshot_path": str(api_path.relative_to(ROOT)),
            "rcsb_entry_snapshot_hash": sha_file(api_path),
            "source_status": "experimentally deposited atomic model and map-coefficient identity",
        })

    cxidb_record = {
        "schema": "sft-v3-raw-diffraction-custody-record/1",
        "article_doi": "10.1038/s41467-024-49814-9",
        "custody_archive": "Coherent X-ray Imaging Data Bank",
        "custody_accession": "221",
        "custody_doi_as_reported_by_primary_article": "10.11577/2203883",
        "official_entry_url": "https://cxidb.org/id-221.html",
        "official_data_root": "https://www.cxidb.org/data/221/",
        "primary_article_declaration": "Raw diffraction images of all the structures used in this paper were deposited to CXIDB with accession ID 221.",
        "custody_scope": "raw diffraction images of every structure used in the primary study",
        "raw_multi-gigabyte_diffraction_payload_copied_into_repository": False,
        "custody_identity_and_official_location_preserved": True,
    }
    write_json(CXIDB_PATH, cxidb_record)

    late_rows = (
        {
            "source_condition_external_inscription": "1 ms after photoexcitation; 20 microjoule",
            "elapsed_second_exact_fraction": "1/1000",
            "pump_power_joule_exact_fraction": "1/50000",
            "observed_state": "weak negative difference-density feature toward COeq2; possible third CO release",
            "assignment_status": "unresolved-multiple-intermediate-mixture; no precise single atomic model",
            "pdb_deposit_status": "structural-EmptyOne-no-deposited-model",
            "source_status": "experimentally observed late-time record retained with unresolved assignment",
        },
        {
            "source_condition_external_inscription": "17 ms after photoexcitation; 20 microjoule",
            "elapsed_second_exact_fraction": "17/1000",
            "pump_power_joule_exact_fraction": "1/50000",
            "observed_state": "weak negative difference-density feature toward COeq2; possible third CO release or rebinding",
            "assignment_status": "unresolved-multiple-intermediate-mixture; no precise single atomic model",
            "pdb_deposit_status": "structural-EmptyOne-no-deposited-model",
            "source_status": "experimentally observed late-time record retained with unresolved assignment",
        },
    )
    controls = (
        {
            "source_control_external_inscription": "negative delay (+10 ns): pump after X-ray diffraction",
            "held_orientation": "source term negative-delay denotes reversed event order, not an SFT negative number",
            "observed_difference_density": "structural-EmptyOne-no-difference-feature",
            "source_status": "favorable no-light-contamination control retained",
        },
        {
            "source_control_external_inscription": "1 ms interleaved-dark2 control",
            "observed_adverse_result": "possible light contamination with reduced COax difference density",
            "comparison_boundary": "complete-darkness comparison retained as primary; interleaved-dark control remains adverse evidence",
            "source_status": "unfavorable control retained without correction or deletion",
        },
        {
            "source_disclosure": "later than 1 ms may contain simultaneous multiple intermediates and possible Mn rebinding",
            "assignment_boundary": "later-stage structural changes cannot be determined precisely from this experiment",
            "source_status": "unresolved mechanism boundary retained without inferred intermediate",
        },
    )
    target_payloads = tuple(pdb_records) + late_rows + power_rows + controls
    if len(target_payloads) != 17 or len(identities) != 17:
        raise ValueError("KIN-007 target vector width changed")
    targets = tuple({**identity, **payload} for identity, payload in zip(identities, target_payloads))
    target_document = {
        "schema": "sft-v3-sequential-mechanism-withheld-targets/1",
        "claim_id": spec["claim_id"],
        "identity_registry_hash": IDENTITY_HASH,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_registered_target_count": 17,
        "rows": targets,
    }
    write_json(TARGET_PATH, target_document)

    primary = {
        "schema": "sft-v3-sequential-mechanism-complete-primary-record/1",
        "claim_id": spec["claim_id"],
        "prefetch_specification": (str(SPEC_PATH.relative_to(ROOT)), SPEC_HASH),
        "value_free_identity_registry": (str(IDENTITY_PATH.relative_to(ROOT)), IDENTITY_HASH),
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
        "complete_pdb_deposit_count": len(pdb_records),
        "complete_pdb_records": pdb_records,
        "cxidb_custody_record": (str(CXIDB_PATH.relative_to(ROOT)), sha_file(CXIDB_PATH)),
        "computational_trajectory_archive_identity": {
            "archive": "Biological Structure Model Archive",
            "accession": "BSM00067",
            "doi": "10.51093/bsm-00067",
            "scope": "all sixteen QM/MM NEB reaction-path trajectories; retained as calculated comparison, never as measured target or Fold-law parameter",
        },
        "complete_registered_target_count": len(targets),
        "complete_source_ordered_target_vector": targets,
        "complete_deposited_sequence_state_count": len(pdb_records),
        "complete_late_unresolved_state_count": len(late_rows),
        "complete_power_titration_column_count": len(power_rows),
        "complete_favorable_adverse_unresolved_control_count": len(controls),
        "complete_article_supplements_pdb_and_raw_custody_metadata_preserved": True,
        "experimental_deposited_calculated_and_unresolved_provenance_separated": True,
        "image_curves_not_digitized_and_unreported_values_not_inferred": True,
        "external_values_used_as_proof_parameters": False,
        "imported_differential_equation_exponential_decay_fitted_lifetime_steady_state_selection_interpolation_average_or_target_correction_used_in_fold_law": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "identity_registry_hash": IDENTITY_HASH,
        "article_hash": sha_file(ARTICLE_PATH),
        "supplement_archive_hash": sha_file(SUPPLEMENT_ZIP_PATH),
        "withheld_target_hash": sha_file(TARGET_PATH),
        "primary_record_hash": sha_file(PRIMARY_PATH),
        "cxidb_custody_record_hash": sha_file(CXIDB_PATH),
        "complete_target_count": len(targets),
        "complete_supplementary_file_count": len(supplementary_files),
        "complete_supplement_pdf_count": len(supplement_pdf_records),
        "complete_pdb_deposit_count": len(pdb_records),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
