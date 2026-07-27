#!/usr/bin/env python3
"""Open and bind the complete KIN-011 source vector after identity sealing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_capture_spec_v1.json"
SPEC_HASH = "sha256:c75f6820adff1a1ec7b3057033d0a563f98ec6a69df80c9c4e985385fb011f24"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-011-diffusion-limited-reaction-v1"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:40a4ecfacbba80be1c0f9ed3e307ae65493dc5b975ad34c1f1ddd60be961fa21"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_target_identities_v1.json"
IDENTITY_HASH = "sha256:a25e15f60b000b37b523d117c9aee657d7b3d65e710246a71024ec384689cd49"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/diffusion_limited_reaction_withheld_targets_v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha_stream(stream) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    while True:
        block = stream.read(1024 * 1024)
        if not block:
            break
        digest.update(block)
        count += len(block)
    return "sha256:" + digest.hexdigest(), count


def video_payload(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
            "-show_entries", "stream=nb_read_frames,nb_frames,width,height,r_frame_rate,duration",
            "-of", "json", str(path),
        ], check=True, capture_output=True, text=True,
    )
    stream = json.loads(result.stdout)["streams"][0]
    return {
        "complete_movie_hash": sha_file(path), "complete_movie_byte_count": path.stat().st_size,
        "frame_count": int(stream["nb_read_frames"]), "pixel_width": int(stream["width"]),
        "pixel_height": int(stream["height"]), "frame_rate_external_inscription": stream["r_frame_rate"],
        "duration_external_inscription_seconds": stream["duration"], "source_format": "AVI",
    }


def main() -> None:
    for path, expected in ((SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH)):
        if sha_file(path) != expected:
            raise ValueError("KIN-011 sealed boundary changed")
    inventory = json.loads(INVENTORY_PATH.read_text())
    identities = json.loads(IDENTITY_PATH.read_text())
    rows = tuple(identities.get("rows", ()))
    if len(rows) != 251 or identities.get("target_values_or_hashes_present") is not False:
        raise ValueError("KIN-011 identity census changed")
    file_rows = {Path(row["snapshot_path"]).name: row for row in inventory["complete_source_files"]}
    for row in file_rows.values():
        if sha_file(ROOT / row["snapshot_path"]) != row["snapshot_hash"]:
            raise ValueError("KIN-011 captured source changed")
    pdfs = {
        name: PdfReader(str(SNAPSHOT_ROOT / name))
        for name in ("article.pdf", "supplementary-information.pdf", "additional-supplementary.pdf", "reporting-summary.pdf")
    }
    pdf_page_payloads = {
        (name, index): {
            "complete_extracted_page_text": page.extract_text() or "",
            "complete_extracted_page_text_hash": "sha256:" + hashlib.sha256((page.extract_text() or "").encode()).hexdigest(),
        }
        for name, reader in pdfs.items() for index, page in enumerate(reader.pages, start=1)
    }
    videos = {
        name: video_payload(SNAPSHOT_ROOT / name)
        for name in ("supplementary-video-one.avi", "supplementary-video-two.avi")
    }
    metadata_path = SNAPSHOT_ROOT / "figshare-record-metadata.json"
    metadata = json.loads(metadata_path.read_text())
    archives: dict[str, zipfile.ZipFile] = {}
    try:
        for archive in inventory["archive_topology_only"]:
            archives[archive["archive_identity"]] = zipfile.ZipFile(SNAPSHOT_ROOT / archive["archive_identity"])
        target_rows = []
        for identity in rows:
            record_class = identity["source_record_class"]
            if record_class == "complete-article-landing-record":
                path = SNAPSHOT_ROOT / "article.html"
                payload = {
                    "complete_document_hash": sha_file(path), "complete_document_byte_count": path.stat().st_size,
                    "source_content_class": "HTML",
                }
            elif record_class == "complete-pdf-page":
                payload = pdf_page_payloads[(identity["source_document_identity"], identity["source_page_ordinal"])]
            elif record_class == "complete-supplementary-video":
                payload = videos[identity["source_document_identity"]]
            elif record_class == "complete-figshare-metadata-record":
                payload = {
                    "complete_metadata_hash": sha_file(metadata_path), "complete_metadata_byte_count": metadata_path.stat().st_size,
                    "record_id": metadata["id"], "record_doi": metadata["doi"],
                    "record_published_date": metadata["published_date"], "record_modified_date": metadata["modified_date"],
                    "record_file_count": len(metadata["files"]), "record_file_id": metadata["files"][0]["id"],
                    "record_file_name": metadata["files"][0]["name"], "record_file_size": metadata["files"][0]["size"],
                    "record_file_md5_external_inscription": metadata["files"][0]["computed_md5"],
                }
            elif record_class == "complete-source-data-archive-member":
                archive = archives[identity["archive_identity"]]
                info = archive.getinfo(identity["source_record_identity"])
                if info.is_dir():
                    member_hash, member_count = "sha256:" + hashlib.sha256(b"").hexdigest(), 0
                else:
                    with archive.open(info) as stream:
                        member_hash, member_count = sha_stream(stream)
                if member_count != identity["declared_uncompressed_byte_count"]:
                    raise ValueError("KIN-011 archive member byte count changed")
                payload = {
                    "archive_identity": identity["archive_identity"],
                    "source_member_identity": identity["source_record_identity"],
                    "archive_directory_entry": info.is_dir(), "complete_member_byte_count": member_count,
                    "complete_member_hash": member_hash,
                }
            else:
                raise ValueError("KIN-011 source record class changed")
            target_rows.append({**identity, "target_payload": payload})
    finally:
        for archive in archives.values():
            archive.close()
    document = {
        "schema": "sft-v3-diffusion-limited-reaction-withheld-targets/1",
        "claim_id": identities["claim_id"], "chemistry_obligation": identities["chemistry_obligation"],
        "prefetch_spec_hash": SPEC_HASH, "source_inventory_hash": INVENTORY_HASH,
        "identity_registry_hash": IDENTITY_HASH, "complete_registered_target_count": len(target_rows),
        "complete_pdf_page_target_count": 43, "complete_supplementary_video_target_count": 2,
        "complete_source_data_archive_member_target_count": 204,
        "release_requires_complete_identity_and_prediction_seal": True,
        "all_complete_source_records_preserved": True, "rows": target_rows,
    }
    TARGET_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "target_path": str(TARGET_PATH.relative_to(ROOT)), "target_hash": sha_file(TARGET_PATH),
        "complete_registered_target_count": len(target_rows), "complete_pdf_page_target_count": 43,
        "complete_supplementary_video_frame_count": sum(row["frame_count"] for row in videos.values()),
        "complete_source_data_archive_member_target_count": 204,
    }, indent=2))


if __name__ == "__main__":
    main()
