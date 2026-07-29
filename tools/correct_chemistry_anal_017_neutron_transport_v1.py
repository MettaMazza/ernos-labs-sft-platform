#!/usr/bin/env python3
"""Preserve and correct the first ANAL-017 legacy-host transport attempt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from bs4 import BeautifulSoup
import requests


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/anal-012-022-whole-subfield-v1"
PRIOR = ROOT / "experiments/external_sources/chemistry/anal_017_neutron_complete_list_transport_addendum_v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/anal_017_neutron_transport_correction_addendum_v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for script, expected, key in (("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"), ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id")):
        run = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if run.returncode or json.loads(run.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed: {script}")


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("neutron transport correction already exists; overwrite prohibited")
    verify_seals()
    prior = json.loads(PRIOR.read_text())
    prior_path = ROOT / prior["captured_artifacts"][0]["path"]
    prior_soup = BeautifulSoup(prior_path.read_bytes(), "html.parser")
    if len(prior_soup.find_all("tr")) != 0 or "NIST Center for Neutron Research" not in prior_soup.get_text(" ", strip=True):
        raise SystemExit("unexpected first transport-attempt content")
    url = "https://www.ncnr.nist.gov/resources/n-lengths/list.html"
    response = requests.get(url, timeout=90, headers={"User-Agent": "Ernos-Labs-SFT-V3-neutron-corrected-transport/1 (Maria.Smith.Sftoe@gmail.com)"})
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    if len(soup.find_all("tr")) < 380 or "Neutron Scattering Lengths and cross sections" not in soup.get_text(" ", strip=True):
        raise SystemExit("corrected NIST transport did not return the complete table")
    path = SNAP / "nist-neutron-scattering-lengths-complete-list-via-www.html"
    if path.exists():
        raise SystemExit("corrected neutron capture already exists; overwrite prohibited")
    path.write_bytes(response.content)
    payload = {
        "schema": "sft-v3-source-transport-correction-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "claim_id": "SFT-CHEM-ELECTRON-NEUTRON-DIFFRACTION-017",
        "created_date": "2026-07-28",
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "prior_addendum_path": PRIOR.relative_to(ROOT).as_posix(),
        "prior_addendum_sha256": digest(PRIOR.read_bytes()),
        "correction": "The first legacy URL redirected to the NIST NCNR landing page and therefore did not contain the complete isotope table. That capture and the failed current route remain preserved. The www.ncnr.nist.gov form of the same fixed legacy path returns the complete NIST table and is captured here.",
        "prior_capture_reclassified_as": "official-NIST-redirect-landing-page-not-complete-table",
        "captured_artifacts": [{
            "source_id": "NIST-NEUTRON-SCATTERING-LENGTHS",
            "relationship": "official-nist-linked-complete-isotope-table-corrected-legacy-transport",
            "url": url,
            "final_url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "path": path.relative_to(ROOT).as_posix(),
            "byte_count": len(response.content),
            "sha256": digest(response.content),
            "html_table_count": len(soup.find_all("table")),
            "html_row_count": len(soup.find_all("tr")),
        }],
        "transport_failures": [],
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({"addendum": OUTPUT.relative_to(ROOT).as_posix(), "sha256": digest(OUTPUT.read_bytes()), "table_rows": len(soup.find_all('tr'))}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
