#!/usr/bin/env python3
"""Capture the complete pre-registered KIN-011 source surface without parsing targets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_capture_spec_v1.json"
SPEC_HASH = "sha256:c75f6820adff1a1ec7b3057033d0a563f98ec6a69df80c9c4e985385fb011f24"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-011-diffusion-limited-reaction-v1"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
FILENAMES = (
    "article.html", "article.pdf", "supplementary-information.pdf", "additional-supplementary.pdf",
    "supplementary-video-one.avi", "supplementary-video-two.avi", "reporting-summary.pdf",
    "nature-source-data.zip", "figshare-record-metadata.json", "figshare-source-data.zip",
)


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "SFT-v3-complete-source-capture/1"})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as stream:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            stream.write(block)


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH:
        raise ValueError("KIN-011 prefetch specification changed")
    spec = json.loads(SPEC_PATH.read_text())
    requests = tuple(spec.get("complete_source_requests", ()))
    if len(requests) != len(FILENAMES):
        raise ValueError("KIN-011 complete source request census changed")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    source_files = []
    archive_topologies = []
    for row, filename in zip(requests, FILENAMES):
        path = SNAPSHOT_ROOT / filename
        fetch(row["url"], path)
        source_files.append({
            "source_class": row["source_class"], "url": row["url"],
            "snapshot_path": str(path.relative_to(ROOT)), "snapshot_hash": sha_file(path),
            "byte_count": path.stat().st_size,
        })
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                members = tuple({
                    "source_member_ordinal": ordinal, "source_member_identity": info.filename,
                    "archive_directory_entry": info.is_dir(), "declared_compressed_byte_count": info.compress_size,
                    "declared_uncompressed_byte_count": info.file_size,
                } for ordinal, info in enumerate(archive.infolist(), start=1))
            archive_topologies.append({
                "archive_identity": filename, "archive_member_count": len(members), "members": members,
            })
    inventory = {
        "schema": "sft-v3-diffusion-limited-reaction-source-inventory/1",
        "article_doi": spec["article_doi"], "figshare_repository_doi": spec["figshare_repository_doi"],
        "prefetch_spec_hash": SPEC_HASH, "complete_source_file_count": len(source_files),
        "complete_source_files": source_files, "complete_archive_count": len(archive_topologies),
        "archive_topology_only": archive_topologies,
        "all_archive_members_registered_without_value_selection": True,
        "archive_member_content_values_or_hashes_present": False,
    }
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "inventory_path": str(INVENTORY_PATH.relative_to(ROOT)), "inventory_hash": sha_file(INVENTORY_PATH),
        "complete_source_file_count": len(source_files), "complete_archive_count": len(archive_topologies),
        "complete_archive_member_count": sum(row["archive_member_count"] for row in archive_topologies),
        "complete_source_byte_count": sum(row["byte_count"] for row in source_files),
    }, indent=2))


if __name__ == "__main__":
    main()
