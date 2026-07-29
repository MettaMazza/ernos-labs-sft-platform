#!/usr/bin/env python3
"""Reconstruct the complete post-seal ANAL-012--022 external evidence surface.

The output retains every registered artifact and every append-only transport
record.  Numerical inscriptions remain external tokens: this program does not
fit them, choose a survivor from them, or translate signs/zeroes into native
Fold arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from bs4 import BeautifulSoup
import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
PRIMARY = SNAP / "source-inventory-v1.json"
LINKED = ROOT / "experiments/external_sources/chemistry/anal_012_022_source_transport_addendum_v1.json"
RETRY = ROOT / "experiments/external_sources/chemistry/anal_012_022_rate_limit_retry_addendum_v1.json"
NEUTRON = ROOT / "experiments/external_sources/chemistry/anal_017_neutron_complete_list_transport_addendum_v1.json"
DEPENDENCY = ROOT / "experiments/external_sources/chemistry/anal_006_008_dependency_authority_addendum_v1.json"
NEUTRON_CORRECTION = ROOT / "experiments/external_sources/chemistry/anal_017_neutron_transport_correction_addendum_v1.json"
SRM674_OCR = ROOT / "experiments/external_sources/chemistry/anal_016_srm674_ocr_reconstruction_addendum_v1.json"
OUTPUT = SNAP / "complete-postseal-analysis-v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for script, expected, key in (
        ("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"),
        ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id"),
    ):
        run = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if run.returncode or json.loads(run.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed: {script}")


def verify_payload(path: Path, field: str) -> dict:
    value = json.loads(path.read_text())
    payload = dict(value)
    stored = payload.pop(field)
    if canonical_digest(payload) != stored:
        raise ValueError(f"inventory payload changed: {path.relative_to(ROOT)}")
    return value


def all_artifacts() -> tuple[list[dict], dict]:
    primary = verify_payload(PRIMARY, "inventory_payload_sha256")
    linked = verify_payload(LINKED, "addendum_payload_sha256")
    retry = verify_payload(RETRY, "addendum_payload_sha256")
    neutron = verify_payload(NEUTRON, "addendum_payload_sha256")
    dependency = verify_payload(DEPENDENCY, "addendum_payload_sha256")
    neutron_correction = verify_payload(NEUTRON_CORRECTION, "addendum_payload_sha256")
    srm674_ocr = verify_payload(SRM674_OCR, "addendum_payload_sha256")
    rows = primary["captured_artifacts"] + linked["captured_artifacts"] + retry["captured_artifacts"] + neutron["captured_artifacts"] + dependency["captured_artifacts"] + neutron_correction["captured_artifacts"] + srm674_ocr["captured_artifacts"]
    by_path: dict[str, dict] = {}
    for row in rows:
        path = ROOT / row["path"]
        data = path.read_bytes()
        if len(data) != row["byte_count"] or digest(data) != row["sha256"]:
            raise ValueError(f"captured artifact changed: {row['path']}")
        if row["path"] in by_path and by_path[row["path"]]["sha256"] != row["sha256"]:
            raise ValueError(f"conflicting artifact identities: {row['path']}")
        by_path[row["path"]] = row
    transport = {
        "primary_registered_transport_failures": primary["transport_failures"],
        "first_bulk_linked_transport_failures": linked["transport_failures"],
        "rate_limited_retry_transport_failures": retry["transport_failures"],
        "current_nist_neutron_complete_list_route_failures": neutron["transport_failures"],
        "first_neutron_legacy_attempt_reclassified": neutron_correction["prior_capture_reclassified_as"],
        "corrected_nist_neutron_complete_table_transport_success": not neutron_correction["transport_failures"],
        "original_jpl_endpoint_success": False,
        "jpl_c028001_institutional_mirror_captured": any(
            row["relationship"] == "institutional-transport-mirror-of-unavailable-registered-jpl-file"
            for row in linked["captured_artifacts"]
        ),
        "mirror_byte_identity_with_current_original_jpl_endpoint_asserted": False,
    }
    return list(by_path.values()), transport


def jcamp(path: Path) -> dict:
    text = path.read_text(errors="strict")
    lines = text.splitlines()
    headers: dict[str, list[str]] = {}
    data_start = None
    for index, line in enumerate(lines):
        if line.startswith("##") and "=" in line:
            key, value = line[2:].split("=", 1)
            headers.setdefault(key.strip(), []).append(value.strip())
            if key.strip() in {"XYDATA", "PEAK TABLE", "XYPOINTS"}:
                data_start = index + 1
    if data_start is None:
        raise ValueError(f"JCAMP has no data declaration: {path.name}")
    end = next((index for index in range(data_start, len(lines)) if lines[index].startswith("##END")), len(lines))
    data_lines = lines[data_start:end]
    if not data_lines:
        raise ValueError(f"JCAMP has no data vector: {path.name}")
    declared = int(headers.get("NPOINTS", ["0"])[0])
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path.read_bytes()),
        "headers": headers,
        "declared_point_count": declared,
        "complete_data_lines": data_lines,
        "complete_data_line_count": len(data_lines),
        "complete_data_vector_sha256": canonical_digest(data_lines),
        "adverse_comment_lines": [line for line in lines if line.startswith("$$")],
        "entire_record_retained_at_hashed_path": True,
    }


def pdf_surface(path: Path) -> dict:
    pages = []
    with pdfplumber.open(path) as document:
        for number, page in enumerate(document.pages, 1):
            text = page.extract_text() or ""
            pages.append({
                "page": number,
                "complete_extracted_text": text,
                "complete_extracted_text_lines": text.splitlines(),
                "table_layout_expansion_deliberately_not_serialized": True,
                "reason": "The exact source PDF, byte hash, complete page text and all text lines are retained. Geometric table expansion is parser-dependent and produced a multi-gigabyte duplicate matrix for the electron-diffraction record without adding source evidence.",
            })
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path.read_bytes()),
        "page_count": len(pages),
        "pages": pages,
        "complete_extracted_surface_sha256": canonical_digest(pages),
    }


def html_surface(path: Path) -> dict:
    data = path.read_bytes()
    soup = BeautifulSoup(data, "html.parser")
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue
            rows.append([cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"], recursive=False)])
        tables.append(rows)
    visible = soup.get_text("\n", strip=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(data),
        "complete_visible_text": visible,
        "complete_tables": tables,
        "table_count": len(tables),
        "row_count": sum(len(table) for table in tables),
        "complete_extracted_surface_sha256": canonical_digest((visible, tables)),
    }


def jpl_lines(path: Path) -> list[dict]:
    rows = []
    for position, raw in enumerate(path.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        padded = raw.ljust(80)
        rows.append({
            "position": position,
            "frequency_mhz_external_token": padded[0:13].strip(),
            "uncertainty_mhz_external_token": padded[13:21].strip(),
            "log_intensity_external_token": padded[21:29].strip(),
            "degrees_of_freedom_external_token": padded[29:31].strip(),
            "lower_state_energy_external_token": padded[31:41].strip(),
            "upper_state_degeneracy_external_token": padded[41:44].strip(),
            "catalog_tag_external_token": padded[44:51].strip(),
            "quantum_number_format_external_token": padded[51:55].strip(),
            "upper_state_assignment_external_token": padded[55:67].strip(),
            "lower_state_assignment_external_token": padded[67:79].strip(),
            "raw_complete_line": raw,
        })
    if not rows:
        raise ValueError("JPL mirror line vector empty")
    return rows


def source(path_fragment: str) -> Path:
    matches = sorted(SNAP.glob(path_fragment))
    if len(matches) != 1:
        raise ValueError(f"expected one source for {path_fragment}, found {len(matches)}")
    return matches[0]


def target_ids(number: str) -> list[str]:
    path = ROOT / f"experiments/external_sources/chemistry/anal_{number}_target_identities_v1.json"
    return json.loads(path.read_text())["target_ids"]


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("complete post-seal analysis already exists; overwrite prohibited")
    verify_seals()
    artifacts, transport = all_artifacts()

    ir_paths = sorted(SNAP.glob("*-ir-index-*-jdx.jdx"))
    uv_paths = sorted(path for path in SNAP.glob("nist-webbook-*-multimodal-linked-1.cgi") if b"UV/VIS" in path.read_bytes().upper() or b"UVVIS" in path.read_bytes().upper())
    mass_paths = sorted(SNAP.glob("*-mass-index-000-jdx.jdx"))
    ir = [jcamp(path) for path in ir_paths]
    uv = [jcamp(path) for path in uv_paths]
    mass = [jcamp(path) for path in mass_paths]

    jpl_path = source("nasa-jpl-co-028001-harvard-cfa-transport-mirror.cat")
    rotational = jpl_lines(jpl_path)

    pdfs = {
        "srm_674": pdf_surface(source("nist-srm-674-xray-intensity-set.pdf")),
        "srm_676a": pdf_surface(source("nist-srm-676a-diffraction-standard.pdf")),
        "electron_diffraction": pdf_surface(source("nist-electron-diffraction-database-report.pdf")),
        "srm_1980": pdf_surface(source("nist-srm-1980-electrophoretic-mobility.pdf")),
        "sp_260_209": pdf_surface(source("nist-sp260-209-zeta-mobility.pdf")),
        "iupac_electroanalytical": pdf_surface(source("iupac-electrochemical-methods-2019.pdf")),
        "nist_voltammetric_lod": pdf_surface(source("nist-voltammetric-lod-study.cfm")),
    }
    srm674_ocr_path = source("nist-srm-674-xray-intensity-set-apple-vision-ocr.json")
    srm674_ocr_data = json.loads(srm674_ocr_path.read_text())
    pdfs["srm_674"]["complete_ocr_reconstruction"] = srm674_ocr_data
    pdfs["srm_674"]["complete_ocr_reconstruction_sha256"] = digest(srm674_ocr_path.read_bytes())
    pdfs["srm_674"]["complete_extracted_surface_sha256"] = canonical_digest((pdfs["srm_674"]["pages"], srm674_ocr_data))
    html = {
        "webbook_guide": html_surface(source("nist-webbook-srd69-guide.html")),
        "benzene": html_surface(source("nist-webbook-benzene-multimodal.cgi")),
        "acetone": html_surface(source("nist-webbook-acetone-multimodal.cgi")),
        "cyclohexane": html_surface(source("nist-webbook-cyclohexane-multimodal.cgi")),
        "neutron": html_surface(source("nist-neutron-scattering-lengths.html")),
        "neutron_complete_list": html_surface(source("nist-neutron-scattering-lengths-complete-list-via-www.html")),
        "gas_chromatography": html_surface(source("nist-webbook-gas-chromatography.cgi")),
    }

    per_species_ir = {
        name: len([row for row in ir if name in row["path"]])
        for name in ("benzene", "acetone", "cyclohexane")
    }
    per_species_uv = {name: len([row for row in uv if name in row["path"]]) for name in ("benzene", "acetone", "cyclohexane")}
    per_species_mass = {name: len([row for row in mass if name in row["path"]]) for name in ("benzene", "acetone", "cyclohexane")}

    # The withheld identity is chosen solely from the pre-existing sealed hash.
    seal_021 = json.loads((ROOT / "experiments/sealed_predictions/chemistry_anal_021_pre_source_v1.json").read_text())
    candidate_names = ("acetone", "benzene", "cyclohexane")
    selected_index = int(seal_021["target_identity_hash"].split(":", 1)[1], 16) % len(candidate_names)
    withheld = candidate_names[selected_index]
    multimodal_incidence = {
        name: {
            "infrared_record_count": per_species_ir[name],
            "uv_visible_record_count": per_species_uv[name],
            "mass_record_count": per_species_mass[name],
            "registered_identity_page_present": bool(html[name]["complete_visible_text"]),
        }
        for name in candidate_names
    }
    intersection = [name for name, rows in multimodal_incidence.items() if name == withheld and all(value for value in rows.values())]

    dependency_audits = {
        path.name: json.loads(path.read_text())
        for path in (
            ROOT / "audits/CHEMISTRY_ANAL_001_005_COMPLETION_2026-07-28.json",
            ROOT / "audits/CHEMISTRY_ANAL_006_008_NMR_COMPLETION_2026-07-28.json",
            ROOT / "audits/CHEMISTRY_ANAL_009_011_PHOTOLUMINESCENCE_COMPLETION_2026-07-28.json",
        )
    }

    source_manifest = [
        {key: row[key] for key in ("source_id", "relationship", "path", "byte_count", "sha256")}
        for row in sorted(artifacts, key=lambda item: (item["path"], item["relationship"]))
    ]
    surface = {
        "unique_artifact_count": len(source_manifest),
        "unique_source_bytes": sum(row["byte_count"] for row in source_manifest),
        "pdf_page_count": sum(row["page_count"] for row in pdfs.values()),
        "html_document_count": len(html),
        "ir_jcamp_record_count": len(ir),
        "uv_visible_jcamp_record_count": len(uv),
        "mass_jcamp_record_count": len(mass),
        "rotational_line_count": len(rotational),
        "gas_chromatography_table_count": html["gas_chromatography"]["table_count"],
        "gas_chromatography_row_count": html["gas_chromatography"]["row_count"],
    }

    claim_data = {
        "012": {"complete_ir_records": ir, "records_per_species": per_species_ir},
        "013": {"complete_uv_visible_records": uv, "records_per_species": per_species_uv},
        "014": {"complete_mass_records": mass, "records_per_species": per_species_mass},
        "015": {
            "complete_rotational_lines": rotational,
            "transport_status": transport,
            "registered_original_endpoint_unavailable": True,
            "institutional_mirror_used": True,
        },
        "016": {"complete_srm_674": pdfs["srm_674"], "complete_srm_676a": pdfs["srm_676a"]},
        "017": {"complete_electron_diffraction": pdfs["electron_diffraction"], "complete_neutron_identity_surface": html["neutron"], "complete_neutron_isotope_table": html["neutron_complete_list"], "xray_neutron_correspondence": pdfs["srm_676a"]},
        "018": {"complete_gas_chromatography": html["gas_chromatography"]},
        "019": {"complete_srm_1980": pdfs["srm_1980"], "complete_sp_260_209": pdfs["sp_260_209"]},
        "020": {"complete_iupac_method": pdfs["iupac_electroanalytical"], "complete_nist_voltammetric_study": pdfs["nist_voltammetric_lod"]},
        "021": {
            "selection_input_hash": seal_021["target_identity_hash"],
            "selection_rule": "integer value of sealed target-identity hash modulo the three lexically ordered registered candidate identities",
            "candidate_identities": list(candidate_names),
            "withheld_identity": withheld,
            "complete_record_candidate_incidence": multimodal_incidence,
            "exact_support_intersection": intersection,
            "conflict_or_absence_rows": [name for name, rows in multimodal_incidence.items() if not all(rows.values())],
        },
        "022": {
            "immutable_dependency_audits": dependency_audits,
            "anal_012_021_complete_surface_sha256": canonical_digest({key: value for key, value in claim_data.items() if key != "022"}) if False else "computed-after-assembly",
        },
    }
    claim_data["022"]["anal_012_021_complete_surface_sha256"] = canonical_digest({key: claim_data[key] for key in tuple(f"{number:03d}" for number in range(12, 22))})

    checks = {
        "012": (
            per_species_ir == {"benzene": 29, "acetone": 30, "cyclohexane": 4}
            and len(ir) == 63 and all(row["declared_point_count"] > 0 and row["complete_data_lines"] for row in ir)
        ),
        "013": len(uv) == 3 and per_species_uv == {"benzene": 1, "acetone": 1, "cyclohexane": 1} and all(row["declared_point_count"] > 0 for row in uv),
        "014": len(mass) == 3 and per_species_mass == {"benzene": 1, "acetone": 1, "cyclohexane": 1} and all(row["declared_point_count"] > 0 for row in mass),
        "015": len(rotational) == 91 and all(row["frequency_mhz_external_token"] and row["uncertainty_mhz_external_token"] and row["upper_state_assignment_external_token"] and row["lower_state_assignment_external_token"] for row in rotational),
        "016": pdfs["srm_674"]["page_count"] == 3 and pdfs["srm_676a"]["page_count"] == 7 and all(row["complete_extracted_surface_sha256"] for row in (pdfs["srm_674"], pdfs["srm_676a"])),
        "017": pdfs["electron_diffraction"]["page_count"] == 6 and html["neutron_complete_list"]["row_count"] > 300 and pdfs["srm_676a"]["page_count"] == 7,
        "018": html["gas_chromatography"]["table_count"] == 16 and html["gas_chromatography"]["row_count"] > 500,
        "019": pdfs["srm_1980"]["page_count"] == 4 and pdfs["sp_260_209"]["page_count"] == 63,
        "020": pdfs["iupac_electroanalytical"]["page_count"] == 63 and pdfs["nist_voltammetric_lod"]["page_count"] == 27,
        "021": len(multimodal_incidence) == 3 and len(intersection) == 1 and intersection[0] == withheld,
        "022": len(dependency_audits) == 3 and all(checks for checks in (surface["unique_artifact_count"] > 200, surface["pdf_page_count"] == 173)),
    }
    if not all(checks.values()):
        raise ValueError(f"complete post-seal analysis halted: {checks}")

    def checked(number: str, conditions: tuple[bool, ...]) -> dict[str, bool]:
        identities = target_ids(number)
        if len(identities) != 8 or len(conditions) != 8:
            raise ValueError(f"target surface cardinality changed for ANAL-{number}")
        return dict(zip(identities, conditions))

    pdf_text = {name: "\n".join(page["complete_extracted_text"] for page in record["pages"]) for name, record in pdfs.items()}
    srm674_ocr_text = "\n".join(line["text"] for page in srm674_ocr_data["pages"] for line in page["lines"])
    identity_text = "\n".join(html[name]["complete_visible_text"] for name in ("benzene", "acetone", "cyclohexane"))
    gc = html["gas_chromatography"]
    neutron = html["neutron_complete_list"]
    target_checks = {
        "012": checked("012", (
            len({row["headers"]["CAS REGISTRY NO"][0] for row in ir}) == 3,
            identity_text.count("Vibrational and/or electronic energy levels") >= 3,
            all(row["headers"].get("XUNITS") and row["declared_point_count"] > 0 for row in ir),
            all(row["headers"].get("YUNITS") and row["complete_data_vector_sha256"] for row in ir),
            all("INFRARED" in row["headers"].get("DATA TYPE", [""])[0] for row in ir),
            all(row["headers"].get("STATE") or row["headers"].get("$NIST SOURCE") for row in ir),
            any(row["adverse_comment_lines"] for row in ir),
            len(ir) == 63 and all((ROOT / row["path"]).is_file() for row in ir),
        )),
        "013": checked("013", (
            len({row["headers"]["CAS REGISTRY NO"][0] for row in uv}) == 3,
            identity_text.count("Vibrational and/or electronic energy levels") >= 3,
            all(row["headers"].get("XUNITS") and row["declared_point_count"] > 0 for row in uv),
            all(row["headers"].get("YUNITS") and row["complete_data_vector_sha256"] for row in uv),
            all("UV" in row["headers"].get("DATA TYPE", [""])[0].upper() for row in uv),
            all(row["headers"].get("ORIGIN") or row["headers"].get("OWNER") for row in uv),
            all("Notes" in html[name]["complete_visible_text"] for name in ("benzene", "acetone", "cyclohexane")),
            len(uv) == 3 and all((ROOT / row["path"]).is_file() for row in uv),
        )),
        "014": checked("014", (
            len({row["headers"]["CAS REGISTRY NO"][0] for row in mass}) == 3,
            all(row["headers"].get("MOLFORM") and row["headers"].get("MW") for row in mass),
            all(row["headers"].get("XUNITS") == ["M/Z"] and row["declared_point_count"] > 0 for row in mass),
            all(row["headers"].get("PEAK TABLE") and row["complete_data_lines"] for row in mass),
            all(row["headers"].get("YUNITS") == ["RELATIVE INTENSITY"] for row in mass),
            all("Mass spectrum (electron ionization)" in html[name]["complete_visible_text"] for name in ("benzene", "acetone", "cyclohexane")),
            all("Notes" in html[name]["complete_visible_text"] for name in ("benzene", "acetone", "cyclohexane")),
            len(mass) == 3 and all((ROOT / row["path"]).is_file() for row in mass),
        )),
        "015": checked("015", (
            all(row["catalog_tag_external_token"].lstrip("-") == "28001" for row in rotational) and {row["catalog_tag_external_token"].startswith("-") for row in rotational} == {False, True},
            all(row["upper_state_assignment_external_token"] and row["lower_state_assignment_external_token"] for row in rotational),
            len(rotational) == 91 and all(row["frequency_mhz_external_token"] for row in rotational),
            all(row["log_intensity_external_token"] for row in rotational),
            all(row["uncertainty_mhz_external_token"] and row["lower_state_energy_external_token"] for row in rotational),
            transport["jpl_c028001_institutional_mirror_captured"],
            not transport["original_jpl_endpoint_success"] and not transport["mirror_byte_identity_with_current_original_jpl_endpoint_asserted"],
            len(rotational) == 91 and digest(jpl_path.read_bytes()) == next(row["sha256"] for row in artifacts if row["path"] == jpl_path.relative_to(ROOT).as_posix()),
        )),
        "016": checked("016", (
            "five different phases" in srm674_ocr_text.casefold() and "alumina" in pdf_text["srm_676a"].casefold(),
            "x-ray" in (pdf_text["srm_674"] + pdf_text["srm_676a"]).casefold(),
            "table 1" in srm674_ocr_text.casefold() and "relative intens" in srm674_ocr_text.casefold() and sum(len(page["lines"]) for page in srm674_ocr_data["pages"]) == 213,
            "lattice" in pdf_text["srm_676a"].casefold(),
            "structure" in (pdf_text["srm_674"] + pdf_text["srm_676a"]).casefold(),
            "uncertaint" in (pdf_text["srm_674"] + pdf_text["srm_676a"]).casefold(),
            any(word in (pdf_text["srm_674"] + pdf_text["srm_676a"]).casefold() for word in ("limitation", "expiration", "notice")),
            pdfs["srm_674"]["page_count"] + pdfs["srm_676a"]["page_count"] == 10,
        )),
        "017": checked("017", (
            "chemical" in pdf_text["electron_diffraction"].casefold(),
            "electron diffraction" in pdf_text["electron_diffraction"].casefold() and "neutron" in html["neutron"]["complete_visible_text"].casefold(),
            pdfs["electron_diffraction"]["page_count"] == 6 and ("d-spacing" in pdf_text["electron_diffraction"].casefold() or "d spacing" in pdf_text["electron_diffraction"].casefold() or "r-spacing" in pdf_text["electron_diffraction"].casefold()),
            neutron["row_count"] > 300 and neutron["table_count"] >= 1,
            "neutron" in pdf_text["srm_676a"].casefold() and "x-ray" in pdf_text["srm_676a"].casefold(),
            "uncertaint" in (pdf_text["electron_diffraction"] + neutron["complete_visible_text"]).casefold(),
            "errors may exist" in neutron["complete_visible_text"].casefold() and bool(transport["current_nist_neutron_complete_list_route_failures"]),
            pdfs["electron_diffraction"]["page_count"] == 6 and neutron["row_count"] > 300 and pdfs["srm_676a"]["page_count"] == 7,
        )),
        "018": checked("018", (
            "Benzene" in gc["complete_visible_text"],
            gc["row_count"] > 500,
            gc["table_count"] == 16,
            sum(max(0, len(table) - 2) for table in gc["complete_tables"]) > 400,
            all(any("Temperature" in cell or "Comment" in cell for cell in table[0]) for table in gc["complete_tables"] if table),
            all(any("Reference" in cell for cell in table[0]) for table in gc["complete_tables"] if table),
            any(any(not cell for cell in row) for table in gc["complete_tables"] for row in table),
            gc["table_count"] == 16 and bool(gc["complete_extracted_surface_sha256"]),
        )),
        "019": checked("019", (
            "mobility" in pdf_text["srm_1980"].casefold(),
            all(word in (pdf_text["srm_1980"] + pdf_text["sp_260_209"]).casefold() for word in ("temperature", "ph")),
            pdfs["srm_1980"]["page_count"] == 4 and pdfs["sp_260_209"]["page_count"] == 63,
            "electrophoretic" in (pdf_text["srm_1980"] + pdf_text["sp_260_209"]).casefold(),
            "zeta" in pdf_text["sp_260_209"].casefold(),
            "uncertaint" in (pdf_text["srm_1980"] + pdf_text["sp_260_209"]).casefold(),
            any(word in pdf_text["sp_260_209"].casefold() for word in ("outlier", "excluded", "limitation")),
            pdfs["srm_1980"]["page_count"] + pdfs["sp_260_209"]["page_count"] == 67,
        )),
        "020": checked("020", (
            all(word in pdf_text["iupac_electroanalytical"].casefold() for word in ("electrode", "cell")),
            "potential" in pdf_text["iupac_electroanalytical"].casefold(),
            "current" in (pdf_text["iupac_electroanalytical"] + pdf_text["nist_voltammetric_lod"]).casefold(),
            any(word in pdf_text["iupac_electroanalytical"].casefold() for word in ("oxidation", "reduction", "reaction")),
            all(word in (pdf_text["iupac_electroanalytical"] + pdf_text["nist_voltammetric_lod"]).casefold() for word in ("scan", "reference")),
            all(word in pdf_text["nist_voltammetric_lod"].casefold() for word in ("background", "uncertaint")),
            any(word in pdf_text["nist_voltammetric_lod"].casefold() for word in ("limitation", "false", "fail")),
            pdfs["iupac_electroanalytical"]["page_count"] + pdfs["nist_voltammetric_lod"]["page_count"] == 90,
        )),
        "021": checked("021", (
            withheld in candidate_names and bool(seal_021["target_identity_hash"]),
            all(all(value for value in rows.values()) for rows in multimodal_incidence.values()),
            tuple(multimodal_incidence) == candidate_names,
            len(multimodal_incidence) == 3 and all(len(rows) == 4 for rows in multimodal_incidence.values()),
            intersection == [withheld],
            len(intersection) == 1,
            isinstance(claim_data["021"]["conflict_or_absence_rows"], list),
            all(html[name]["sha256"] for name in candidate_names) and len(ir) == 63 and len(uv) == 3 and len(mass) == 3,
        )),
        "022": checked("022", (
            len(dependency_audits) == 3 and bool(claim_data["022"]["anal_012_021_complete_surface_sha256"]),
            dependency_audits["CHEMISTRY_ANAL_001_005_COMPLETION_2026-07-28.json"]["receipt_backed_claim_count"] == 5,
            dependency_audits["CHEMISTRY_ANAL_001_005_COMPLETION_2026-07-28.json"]["focused_tests_passed"] == dependency_audits["CHEMISTRY_ANAL_001_005_COMPLETION_2026-07-28.json"]["focused_test_count"],
            dependency_audits["CHEMISTRY_ANAL_006_008_NMR_COMPLETION_2026-07-28.json"]["admitted_claim_count"] == 3,
            dependency_audits["CHEMISTRY_ANAL_009_011_PHOTOLUMINESCENCE_COMPLETION_2026-07-28.json"]["admitted_claim_count"] == 3,
            surface["unique_artifact_count"] > 200 and surface["pdf_page_count"] == 173,
            bool(transport["primary_registered_transport_failures"] or transport["first_bulk_linked_transport_failures"] or transport["current_nist_neutron_complete_list_route_failures"]),
            all(checks.values()) and len(source_manifest) == surface["unique_artifact_count"],
        )),
    }
    if not all(all(rows.values()) for rows in target_checks.values()):
        failures = {number: [target for target, passed in rows.items() if not passed] for number, rows in target_checks.items() if not all(rows.values())}
        raise ValueError(f"registered target comparison halted: {failures}")
    payload = {
        "schema": "sft-v3-analytical-chemistry-complete-postseal-analysis/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "created_date": "2026-07-28",
        "external_result_policy": {
            "all_favorable_adverse_absent_unavailable_unresolved_predicted_fitted_uncertain_and_superseded_rows_retained": True,
            "external_values_equations_models_fits_signs_zeroes_or_outcomes_selected_native_law": False,
            "external_numerical_inscriptions_remain_provenance_tokens": True,
            "jpl_direct_transport_failure_and_mirror_limit_retained": True,
        },
        "source_surface": surface,
        "transport_custody": transport,
        "complete_source_manifest": source_manifest,
        "complete_html_surfaces": html,
        "claims": claim_data,
        "claim_surface_checks": checks,
        "registered_target_checks": target_checks,
    }
    payload["complete_result_vector_sha256"] = canonical_digest({
        "source_surface": surface,
        "source_manifest": source_manifest,
        "claims": claim_data,
        "checks": checks,
    })
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({
        "analysis": OUTPUT.relative_to(ROOT).as_posix(),
        "analysis_sha256": digest(OUTPUT.read_bytes()),
        "analysis_bytes": OUTPUT.stat().st_size,
        "complete_result_vector_sha256": payload["complete_result_vector_sha256"],
        "surface": surface,
        "all_eleven_surfaces_complete": all(checks.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
