#!/usr/bin/env python3
"""Capture the complete predeclared KIN-009 source surface after the prefetch seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:cc936c64ac170830e26ec3fece37d246511b5e76e895c90db82ccaca4a5d3152"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-009-reversible-kinetic-equilibrium-v1"
BASE = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-023-40190-4/MediaObjects"
URLS = {
    "article_html": "https://www.nature.com/articles/s41467-023-40190-4",
    "article_pdf": "https://www.nature.com/articles/s41467-023-40190-4.pdf",
    "supplementary_information": f"{BASE}/41467_2023_40190_MOESM1_ESM.pdf",
    "additional_file_description": f"{BASE}/41467_2023_40190_MOESM2_ESM.pdf",
    "supplementary_movie": f"{BASE}/41467_2023_40190_MOESM3_ESM.gif",
    "source_data": f"{BASE}/41467_2023_40190_MOESM4_ESM.zip",
}
FILE_NAMES = {
    "article_html": "article.html",
    "article_pdf": "article.pdf",
    "supplementary_information": "supplementary-information.pdf",
    "additional_file_description": "additional-file-description.pdf",
    "supplementary_movie": "supplementary-movie.gif",
    "source_data": "source-data.zip",
}


def sha_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=240) as response:
        return response.read()


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH:
        raise ValueError("KIN-009 prefetch specification changed")
    spec = json.loads(SPEC_PATH.read_text())
    if (
        spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_refit_average_interpolation_renormalization_inference_or_correction_permitted") is not False
    ):
        raise ValueError("KIN-009 prefetch boundary changed")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for source_class, url in URLS.items():
        path = SNAPSHOT_ROOT / FILE_NAMES[source_class]
        content = path.read_bytes() if path.exists() else fetch(url)
        path.write_bytes(content)
        records.append({
            "source_class": source_class,
            "url": url,
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_hash": sha_bytes(content),
            "byte_count": len(content),
        })
    archive_path = SNAPSHOT_ROOT / FILE_NAMES["source_data"]
    with zipfile.ZipFile(archive_path) as archive:
        topology = tuple({
            "source_member_ordinal": ordinal,
            "source_member_identity": info.filename,
            "declared_uncompressed_byte_count": info.file_size,
            "declared_compressed_byte_count": info.compress_size,
            "archive_directory_entry": info.is_dir(),
        } for ordinal, info in enumerate(archive.infolist(), start=1))
    if not topology:
        raise ValueError("KIN-009 source-data archive has no member")
    inventory = {
        "schema": "sft-v3-reversible-kinetic-equilibrium-source-inventory/1",
        "prefetch_spec_hash": SPEC_HASH,
        "article_doi": "10.1038/s41467-023-40190-4",
        "complete_source_file_count": len(records),
        "complete_source_files": records,
        "source_data_archive_topology_only": topology,
        "archive_member_content_values_or_hashes_present": False,
        "all_archive_members_registered_without_value_selection": True,
    }
    inventory_path = SNAPSHOT_ROOT / "source-inventory-v1.json"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "inventory_path": str(inventory_path.relative_to(ROOT)),
        "inventory_hash": sha_file(inventory_path),
        "complete_source_file_count": len(records),
        "source_data_member_count": len(topology),
        "source_data_topology": topology,
    }, indent=2))


if __name__ == "__main__":
    main()
