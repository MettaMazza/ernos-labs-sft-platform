#!/usr/bin/env python3
"""Seal value-free KIN-010 source-record identities before target content opens."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/catalytic_turnover_capture_spec_v1.json"
SPEC_HASH = "sha256:e8874415767d9e257d94e860701dc839fdefd2761611a3a399b2885101e9a033"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-010-catalytic-turnover-v1"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:1a70201cef55873701d19bae35487868c55fa23852cc251f98df0afec6ec9ee9"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/catalytic_turnover_target_identities_v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def video_topology(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
            "-show_entries", "stream=nb_read_frames,nb_frames,width,height,r_frame_rate,duration",
            "-of", "json", str(path),
        ],
        check=True, capture_output=True, text=True,
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
        raise ValueError("KIN-010 prefetch boundary changed")
    inventory = json.loads(INVENTORY_PATH.read_text())
    files = {Path(row["snapshot_path"]).name: row for row in inventory["complete_source_files"]}
    for row in files.values():
        if sha_file(ROOT / row["snapshot_path"]) != row["snapshot_hash"]:
            raise ValueError("KIN-010 captured source changed")
    supplement = SNAPSHOT_ROOT / "supplementary-information.pdf"
    page_count = len(PdfReader(str(supplement)).pages)
    if page_count != 106:
        raise ValueError("KIN-010 supplementary page topology changed")
    movie = video_topology(SNAPSHOT_ROOT / "supplementary-video.mp4")
    if movie["declared_frame_count"] != 1604:
        raise ValueError("KIN-010 movie topology changed")
    rows = []

    def add(source_document_identity: str, source_record_class: str, source_record_identity: str, **extra) -> None:
        ordinal = len(rows) + 1
        rows.append({
            "target_id": f"SFT-CHEM-KIN010-COMPLETE-SOURCE-RECORD-{ordinal:03d}",
            "source_id": "NATURE-NANOTECHNOLOGY-S41565-021-00959-4-COMPLETE",
            "article_doi": "10.1038/s41565-021-00959-4",
            "source_data_repository_doi": "10.5281/zenodo.4903414",
            "catalytic_system_identity": "single-palladium-molecule-Suzuki-Miyaura-complete-cycle-surface",
            "source_document_identity": source_document_identity,
            "source_record_class": source_record_class,
            "source_record_identity": source_record_identity,
            "source_record_ordinal": ordinal,
            **extra,
        })

    add("article.html", "complete-article-landing-record", "complete-article-landing-html")
    add("article.pdf", "attempted-article-pdf-returned-html-record", "complete-returned-response")
    for page in range(1, page_count + 1):
        add(
            "supplementary-information.pdf", "complete-supplementary-information-page", f"page-{page:03d}",
            source_page_ordinal=page,
        )
    add("supplementary-video.mp4", "complete-supplementary-video", "complete-supplementary-video", **movie)
    add("zenodo-record-metadata.json", "complete-zenodo-metadata-record", "complete-zenodo-record-metadata")
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
    if len(rows) != 497 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 498)):
        raise ValueError("KIN-010 complete identity census changed")
    document = {
        "schema": "sft-v3-catalytic-turnover-target-identities/1",
        "claim_id": "SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-010",
        "prefetch_spec_hash": SPEC_HASH, "source_inventory_hash": INVENTORY_HASH,
        "complete_registered_target_count": len(rows),
        "complete_supplementary_information_page_count": page_count,
        "complete_supplementary_movie_count": 1,
        "complete_supplementary_movie_frame_count": movie["declared_frame_count"],
        "complete_archive_count": len(inventory["archive_topology_only"]),
        "complete_source_data_archive_member_count": sum(row["archive_member_count"] for row in inventory["archive_topology_only"]),
        "article_pdf_unavailable_response_preserved": True,
        "target_values_or_hashes_present": False,
        "all_cycle_state_transition_duration_turnover_frequency_condition_fit_rate_constant_uncertainty_product_control_status_value_and_target_hash_values_absent": True,
        "rows": rows,
    }
    IDENTITY_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "identity_path": str(IDENTITY_PATH.relative_to(ROOT)), "identity_hash": sha_file(IDENTITY_PATH),
        "complete_registered_target_count": len(rows),
        "complete_supplementary_information_page_count": page_count,
        "complete_supplementary_movie_frame_count": movie["declared_frame_count"],
        "complete_source_data_archive_member_count": document["complete_source_data_archive_member_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
