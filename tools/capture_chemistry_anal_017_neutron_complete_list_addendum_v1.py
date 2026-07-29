#!/usr/bin/env python3
"""Capture the complete NIST neutron table linked by the registered identity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import requests


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
SOURCE_PAGE = SNAP / "nist-neutron-scattering-lengths.html"
OUTPUT = ROOT / "experiments/external_sources/chemistry/anal_017_neutron_complete_list_transport_addendum_v1.json"
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


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("neutron addendum already exists; overwrite prohibited")
    verify_seals()
    page = SOURCE_PAGE.read_text()
    declared_url = "https://www.nist.gov/ncnr/neutron-scattering-lengths-list"
    if declared_url not in page:
        raise SystemExit("complete-list identity absent from registered NIST capture")
    legacy_url = "https://ncnr.nist.gov/resources/n-lengths/list.html"
    response = requests.get(legacy_url, timeout=90, headers={"User-Agent": "Ernos-Labs-SFT-V3-neutron-complete-capture/1 (Maria.Smith.Sftoe@gmail.com)"})
    response.raise_for_status()
    if not response.content:
        raise SystemExit("empty complete neutron table")
    path = SNAP / "nist-neutron-scattering-lengths-complete-list.html"
    if path.exists():
        raise SystemExit("complete neutron table path already exists; overwrite prohibited")
    path.write_bytes(response.content)
    payload = {
        "schema": "sft-v3-linked-source-transport-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "claim_id": "SFT-CHEM-ELECTRON-NEUTRON-DIFFRACTION-017",
        "created_date": "2026-07-28",
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "registered_identity_page_path": SOURCE_PAGE.relative_to(ROOT).as_posix(),
        "registered_identity_page_sha256": digest(SOURCE_PAGE.read_bytes()),
        "current_link_identity": declared_url,
        "current_link_transport_status": "HTTP 404 observed post-seal and retained",
        "official_nist_legacy_complete_list_url": legacy_url,
        "selection_rule": "Follow the registered NIST page's declared complete-list identity; when its current route returns 404, retain that adverse transport result and capture the same complete-list path on NIST NCNR's official legacy host without selecting rows.",
        "captured_artifacts": [{
            "source_id": "NIST-NEUTRON-SCATTERING-LENGTHS",
            "relationship": "official-nist-linked-complete-isotope-table-legacy-transport",
            "url": legacy_url,
            "final_url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "path": path.relative_to(ROOT).as_posix(),
            "byte_count": len(response.content),
            "sha256": digest(response.content),
        }],
        "transport_failures": [{"url": declared_url, "http_status": 404, "preserved": True}],
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({"addendum": OUTPUT.relative_to(ROOT).as_posix(), "sha256": digest(OUTPUT.read_bytes()), "captured_bytes": len(response.content)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
