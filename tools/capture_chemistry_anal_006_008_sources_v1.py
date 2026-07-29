#!/usr/bin/env python3
"""Capture the fixed official ANAL-006–008 NMR source surface post-seal."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "experiments/external_sources/chemistry/snapshots/anal-006-008-nmr-v1"
USER_AGENT = "Ernos-Labs-SFT-V3-open-empirical-source-capture/1"
SOURCES = (
    ("iupac-nmr-nomenclature-2001.html", "https://publications.iupac.org/pac/73/11/1795/index.html", "html", ("NMR nomenclature", "chemical shifts")),
    ("iupac-nmr-nomenclature-2001.pdf", "https://publications.iupac.org/publications/pac/2001/pdf/7311x1795.pdf", "pdf", ("%PDF",)),
    ("bmrb-68-summary.html", "https://bmrb.io/data_library/summary/index.php?bmrbId=68", "html", ("BMRB Entry 68", "chemical shifts")),
    ("bmr68_3.str", "https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr68/bmr68_3.str", "nmr-star", ("data_68", "_Atom_chem_shift.Val")),
    ("bmrb-16582-summary.html", "https://bmrb.io/data_library/summary/index.php?bmrbId=16582", "html", ("BMRB Entry 16582", "coupling constants")),
    ("bmr16582_3.str", "https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr16582/bmr16582_3.str", "nmr-star", ("data_16582", "_Coupling_constant.Val")),
    ("bmrb-52365-summary.html", "https://bmrb.io/data_library/summary/index.php?bmrbId=52365", "html", ("BMRB Entry 52365", "T1")),
    ("bmr52365_3.str", "https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr52365/bmr52365_3.str", "nmr-star", ("data_52365", "relaxation")),
    ("bmrb-27257-summary.html", "https://bmrb.io/data_library/summary/index.php?bmrbId=27257", "html", ("BMRB Entry 27257", "exchange rate")),
    ("bmr27257_3.str", "https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr27257/bmr27257_3.str", "nmr-star", ("data_27257", "_H_exch_rate.Val")),
)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def capture(name: str, url: str, media_kind: str, markers: tuple[str, ...]) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        status = response.status
    text = body.decode("utf-8", errors="replace")
    if not body or any(marker.casefold() not in text.casefold() for marker in markers):
        raise RuntimeError(f"source identity markers failed for {name}")
    path = DESTINATION / name
    path.write_bytes(body)
    return {
        "path": str(path.relative_to(ROOT)),
        "registered_url": url,
        "final_url": final_url,
        "media_kind": media_kind,
        "http_status": status,
        "content_type": content_type,
        "byte_count": len(body),
        "sha256": sha256_bytes(body),
        "identity_markers": list(markers),
    }


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    rows = [capture(*source) for source in SOURCES]
    inventory_without_hash = {
        "schema": "sft-v3-complete-source-capture/1",
        "family": "ANAL-006-008-NMR",
        "captured_date": "2026-07-28",
        "capture_occurred_after_all_three_derivation_seals": True,
        "source_count": len(rows),
        "sources": rows,
        "all_favorable_adverse_absent_unavailable_unresolved_rows_required": True,
    }
    payload = json.dumps(inventory_without_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
    inventory = dict(inventory_without_hash)
    inventory["inventory_payload_sha256"] = sha256_bytes(payload)
    path = DESTINATION / "source-inventory-v1.json"
    path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": len(rows), "inventory": str(path.relative_to(ROOT)), "inventory_sha256": sha256_bytes(path.read_bytes()), "payload_sha256": inventory["inventory_payload_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
