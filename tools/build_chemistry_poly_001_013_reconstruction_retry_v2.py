#!/usr/bin/env python3
"""Resolve POLY source-reconstruction failures without erasing attempt one."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/complete-postseal-analysis-v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/complete-postseal-analysis-v2.json"
THERMAL_OCR = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/13_nist_polymer_thermal_degradation_ocr_v1.json"
PAMS_OCR = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1/03_nist_monodisperse_pams_kinetic_network_ocr_v1.json"
PAMS_PDF = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1/03_nist_monodisperse_pams_kinetic_network.pdf"
AUDIT = ROOT / "audits/CHEMISTRY_POLY_SOURCE_RECONSTRUCTION_RETRY_2026-07-28.json"

EXPECTED = {
    THERMAL_OCR: "sha256:9e93a55985618dc5a2889442d87f50a627db315587696366658ad4d3c2fd5cec",
    PAMS_OCR: "sha256:69b7da6fa152732b2b2edf4b9cc2aba1e515917578d3fc6a3aec824c07a65cbd",
    PAMS_PDF: "sha256:eef4adecc8fd23cdf05dc3e8a8ae7b1193638dac0d0f2b036d149ec11b1da44d",
}


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def exact_record(value: Fraction) -> dict[str, object]:
    return {"numerator": value.numerator, "denominator": value.denominator, "exact_inscription": str(value)}


def all_ocr_text(document: dict) -> str:
    return "\n".join(line["text"] for page in document["pages"] for line in page["lines"])


def interval_compatible(mn: Fraction, mw: Fraction, reported: Fraction) -> bool:
    """Can rounded integer masses yield a ratio rounding to the printed hundredth?"""
    lower_ratio = (mw - Fraction(1, 2)) / (mn + Fraction(1, 2))
    upper_ratio = (mw + Fraction(1, 2)) / (mn - Fraction(1, 2))
    lower_printed = reported - Fraction(1, 200)
    upper_printed = reported + Fraction(1, 200)
    return max(lower_ratio, lower_printed) < min(upper_ratio, upper_printed)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("Polymer reconstruction retry v2 already exists")
    if not V1.exists():
        raise SystemExit("Polymer first-attempt analysis is missing")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"OCR artifact changed: {path.relative_to(ROOT)}")

    v1 = json.loads(V1.read_text())
    thermal = json.loads(THERMAL_OCR.read_text())
    pams = json.loads(PAMS_OCR.read_text())
    thermal_text = all_ocr_text(thermal).casefold()
    pams_text = all_ocr_text(pams).casefold()
    pams_embedded_text = "\n".join((page.extract_text() or "") for page in PdfReader(PAMS_PDF).pages).casefold()
    thermal_anchors = tuple(
        phrase for phrase in ("thermal degradation", "depolymerization", "monomer", "scission", "products")
        if phrase in thermal_text
    )
    if thermal["pageCount"] != 15 or len(thermal_anchors) != 5:
        raise SystemExit("thermal-degradation OCR retry did not reconstruct the registered surface")
    for inscription in ("Table 4", "2.9", "890", "1011", "1.24", "58", "88", "175", "1.98"):
        if inscription.casefold() not in pams_text and inscription.casefold() not in pams_embedded_text:
            raise SystemExit(f"PAMS dual reconstruction omitted {inscription}")

    rows = v1["measurement_vectors"]["pams_table4_complete_rows"]
    reconstructions = []
    irreconcilable = []
    resolution_compatible = []
    for row in rows:
        mn = Fraction(row["mn_gpc_x1000_g_mol"])
        mw = Fraction(row["mw_gpc_x1000_g_mol"])
        reported = Fraction(row["reported_dispersity"])
        quotient = mw / mn
        compatible = interval_compatible(mn, mw, reported)
        record = {
            "sample": row["sample"],
            "conversion_percent": row["conversion_percent"],
            "displayed_mn_gpc_x1000_g_mol": exact_record(mn),
            "displayed_mw_gpc_x1000_g_mol": exact_record(mw),
            "exact_quotient_from_displayed_masses": exact_record(quotient),
            "printed_dispersity": exact_record(reported),
            "compatible_with_displayed_integer_mass_and_hundredth_ratio_resolution": compatible,
        }
        reconstructions.append(record)
        (resolution_compatible if compatible else irreconcilable).append(record)
    if [(row["sample"], row["conversion_percent"]) for row in irreconcilable] != [("A", "2.9")]:
        raise SystemExit("PAMS retry did not isolate the one source-internal arithmetic defect")

    result = dict(v1)
    result["schema"] = "sft-v3-polymer-chemistry-complete-postseal-analysis/2"
    result["supersedes_analysis"] = {
        "path": str(V1.relative_to(ROOT)),
        "sha256": sha(V1),
        "preserved": True,
    }
    result["first_attempt_extraction_adverse_rows_preserved"] = v1["extraction_adverse_rows"]
    result["extraction_adverse_rows"] = []
    result["resolved_extraction_rows"] = [{
        "source_id": "NIST-POLYMER-THERMAL-DEGRADATION",
        "first_attempt_status": "embedded_text_unavailable",
        "retry_route": "rendered-page-Apple-Vision-OCR",
        "page_count": thermal["pageCount"],
        "ocr_line_count": sum(len(page["lines"]) for page in thermal["pages"]),
        "registered_anchors": thermal_anchors,
        "ocr_sha256": sha(THERMAL_OCR),
        "status": "resolved_by_distinct_reconstruction",
    }]
    result["measurement_vectors"] = dict(v1["measurement_vectors"])
    result["measurement_vectors"]["pams_dispersity_resolution_reconstruction_v2"] = reconstructions
    result["measurement_vectors"]["pams_source_internal_arithmetic_defects"] = irreconcilable
    result["measurement_vectors"]["pams_resolution_compatible_rows"] = resolution_compatible
    result["retry_audit"] = {"path": str(AUDIT.relative_to(ROOT)), "sha256": sha(AUDIT)}
    result["source_reconstruction_failures_retired_claims"] = False
    result["source_defects_selected_native_law_or_survivor"] = False
    result["every_obligation_remained_open_until_untouched_engine_admission"] = True

    vector_payload = dict(result)
    vector_payload.pop("complete_result_vector_sha256", None)
    result["complete_result_vector_sha256"] = "sha256:" + hashlib.sha256(
        json.dumps(vector_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({
        "analysis": sha(OUTPUT),
        "result_vector": result["complete_result_vector_sha256"],
        "resolved_extraction_rows": len(result["resolved_extraction_rows"]),
        "source_internal_arithmetic_defects": len(irreconcilable),
        "retired_claims": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
