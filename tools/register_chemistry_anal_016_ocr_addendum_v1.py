#!/usr/bin/env python3
"""Register the complete OCR reconstruction of the scanned SRM 674 certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1/nist-srm-674-xray-intensity-set.pdf"
OCR = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1/nist-srm-674-xray-intensity-set-apple-vision-ocr.json"
TOOL = ROOT / "tools/ocr_pdf_vision.swift"
OUTPUT = ROOT / "experiments/external_sources/chemistry/anal_016_srm674_ocr_reconstruction_addendum_v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("SRM 674 OCR addendum already exists; overwrite prohibited")
    for script, expected, key in (("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"), ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id")):
        run = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if run.returncode or json.loads(run.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed: {script}")
    ocr = json.loads(OCR.read_text())
    if ocr["pageCount"] != 3 or sum(len(page["lines"]) for page in ocr["pages"]) != 213:
        raise SystemExit("incomplete SRM 674 OCR reconstruction")
    payload = {
        "schema": "sft-v3-complete-source-reconstruction-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "claim_id": "SFT-CHEM-XRAY-DIFFRACTION-STRUCTURE-016",
        "created_date": "2026-07-28",
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "method": "Apple Vision accurate OCR at four-times PDF media-box dimensions; every recognized line, confidence and bounding box retained for every page; the scanned PDF remains authoritative and OCR errors remain visible rather than silently corrected.",
        "source_pdf": {"path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": SOURCE.stat().st_size, "sha256": digest(SOURCE.read_bytes())},
        "reconstruction_tool": {"path": TOOL.relative_to(ROOT).as_posix(), "byte_count": TOOL.stat().st_size, "sha256": digest(TOOL.read_bytes())},
        "captured_artifacts": [{"source_id": "NIST-SRM-674-XRAY-INTENSITY-SET", "relationship": "complete-three-page-machine-ocr-reconstruction", "path": OCR.relative_to(ROOT).as_posix(), "byte_count": OCR.stat().st_size, "sha256": digest(OCR.read_bytes()), "page_count": 3, "ocr_line_count": 213}],
        "transport_failures": [],
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"addendum": OUTPUT.relative_to(ROOT).as_posix(), "sha256": digest(OUTPUT.read_bytes())}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
