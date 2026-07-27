#!/usr/bin/env python3
"""Seal value-free KIN-011 source-record identities before target content opens."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_capture_spec_v1.json"
SPEC_HASH = "sha256:c75f6820adff1a1ec7b3057033d0a563f98ec6a69df80c9c4e985385fb011f24"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-011-diffusion-limited-reaction-v1"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:40a4ecfacbba80be1c0f9ed3e307ae65493dc5b975ad34c1f1ddd60be961fa21"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_target_identities_v1.json"
PDF_IDENTITIES = (
    "article.pdf", "supplementary-information.pdf", "additional-supplementary.pdf", "reporting-summary.pdf",
)
VIDEO_IDENTITIES = ("supplementary-video-one.avi", "supplementary-video-two.avi")


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def video_topology(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
            "-show_entries", "stream=nb_read_frames,nb_frames,width,height,r_frame_rate,duration",
            "-of", "json", str(path),
        ], check=True, capture_output=True, text=True,
    )
    stream = json.loads(result.stdout)["streams"][0]
    return {
        "declared_frame_count": int(stream["nb_read_frames"]),
        "declared_pixel_width": int(stream["width"]), "declared_pixel_height": int(stream["height"]),
        "declared_frame_rate_inscription": stream["r_frame_rate"],
        "declared_duration_inscription_seconds": stream["duration"],
    }


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH or sha_file(INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("KIN-011 prefetch boundary changed")
    inventory = json.loads(INVENTORY_PATH.read_text())
    files = {Path(row["snapshot_path"]).name: row for row in inventory["complete_source_files"]}
    for row in files.values():
        if sha_file(ROOT / row["snapshot_path"]) != row["snapshot_hash"]:
            raise ValueError("KIN-011 captured source changed")
    page_counts = {name: len(PdfReader(str(SNAPSHOT_ROOT / name)).pages) for name in PDF_IDENTITIES}
    if page_counts != {
        "article.pdf": 10, "supplementary-information.pdf": 22,
        "additional-supplementary.pdf": 1, "reporting-summary.pdf": 10,
    }:
        raise ValueError("KIN-011 PDF page topology changed")
    video_topologies = {name: video_topology(SNAPSHOT_ROOT / name) for name in VIDEO_IDENTITIES}
    if tuple(video_topologies[name]["declared_frame_count"] for name in VIDEO_IDENTITIES) != (750, 600):
        raise ValueError("KIN-011 movie topology changed")
    rows = []

    def add(source_document_identity: str, source_record_class: str, source_record_identity: str, **extra) -> None:
        ordinal = len(rows) + 1
        rows.append({
            "target_id": f"SFT-CHEM-KIN011-COMPLETE-SOURCE-RECORD-{ordinal:03d}",
            "source_id": "NATURE-COMMUNICATIONS-S41467-025-68008-5-COMPLETE",
            "article_doi": "10.1038/s41467-025-68008-5",
            "figshare_repository_doi": "10.6084/m9.figshare.30344179",
            "diffusion_reaction_system_identity": "Li-plus-benzene-dimer-helium-droplet-complete-transport-reaction-surface",
            "source_document_identity": source_document_identity,
            "source_record_class": source_record_class,
            "source_record_identity": source_record_identity,
            "source_record_ordinal": ordinal,
            **extra,
        })

    add("article.html", "complete-article-landing-record", "complete-article-landing-html")
    for document, page_count in page_counts.items():
        for page in range(1, page_count + 1):
            add(document, "complete-pdf-page", f"page-{page:03d}", source_page_ordinal=page)
    for document, topology in video_topologies.items():
        add(document, "complete-supplementary-video", "complete-video", **topology)
    add("figshare-record-metadata.json", "complete-figshare-metadata-record", "complete-figshare-record-metadata")
    for archive in inventory["archive_topology_only"]:
        for member in archive["members"]:
            add(
                archive["archive_identity"], "complete-source-data-archive-member",
                member["source_member_identity"], archive_identity=archive["archive_identity"],
                source_member_ordinal=member["source_member_ordinal"],
                archive_directory_entry=member["archive_directory_entry"],
                declared_compressed_byte_count=member["declared_compressed_byte_count"],
                declared_uncompressed_byte_count=member["declared_uncompressed_byte_count"],
            )
    if len(rows) != 251 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 252)):
        raise ValueError("KIN-011 complete identity census changed")
    document = {
        "schema": "sft-v3-diffusion-limited-reaction-target-identities/1",
        "claim_id": "SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-011",
        "prefetch_spec_hash": SPEC_HASH, "source_inventory_hash": INVENTORY_HASH,
        "complete_registered_target_count": len(rows), "complete_pdf_page_count": sum(page_counts.values()),
        "complete_supplementary_video_count": 2,
        "complete_supplementary_video_frame_count": sum(row["declared_frame_count"] for row in video_topologies.values()),
        "complete_archive_count": len(inventory["archive_topology_only"]),
        "complete_source_data_archive_member_count": sum(row["archive_member_count"] for row in inventory["archive_topology_only"]),
        "target_values_or_hashes_present": False,
        "all_distance_time_velocity_yield_rate_fit_distribution_simulation_uncertainty_condition_status_value_and_target_hash_values_absent": True,
        "rows": rows,
    }
    IDENTITY_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "identity_path": str(IDENTITY_PATH.relative_to(ROOT)), "identity_hash": sha_file(IDENTITY_PATH),
        "complete_registered_target_count": len(rows), "complete_pdf_page_count": sum(page_counts.values()),
        "complete_supplementary_video_frame_count": document["complete_supplementary_video_frame_count"],
        "complete_source_data_archive_member_count": document["complete_source_data_archive_member_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
