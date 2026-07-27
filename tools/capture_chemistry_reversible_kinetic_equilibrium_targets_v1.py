#!/usr/bin/env python3
"""Release complete KIN-009 source records only after the value-free identity seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-009-reversible-kinetic-equilibrium-v1"
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:cc936c64ac170830e26ec3fece37d246511b5e76e895c90db82ccaca4a5d3152"
INVENTORY_PATH = SNAPSHOT_ROOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:5d7c24d3d62d2b3217a62e7e3f34be9e7425c2d5a3f65ed6acb7b7a404542722"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_target_identities_v1.json"
IDENTITY_HASH = "sha256:512caad8d5b26bd6da8ac04ca0a9f8b68f2700f8d83444bb1abbfc457ac9a720"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_withheld_targets_v1.json"
SOURCE_HASHES = {
    "article.html": "sha256:c2011aa9108d6e2baaa5beed58ab5976c5ad489d62e6af8ac0b1a4657968e7aa",
    "article.pdf": "sha256:f6d481ffa2c7dfb27739bb4795f67b434e322e58abf56d729a05a7fbede922bc",
    "supplementary-information.pdf": "sha256:3311c49444849d6932b531236e46620f2ec5fb2ecf446c4ce4a65767ca43c5d4",
    "additional-file-description.pdf": "sha256:6b4df61d509ebeb24ddbeb67210b0447db859d186c19d3d66973c1945492569d",
    "supplementary-movie.gif": "sha256:f4462d9274601b7991848b765c6b0f126253690926b5f5d60fa22a30aa3ae2d9",
    "source-data.zip": "sha256:004410f7f073c6a7c218fa199b2df7efbc6806c6ff5be11001a12888cb8e10f9",
}


def sha_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def safe_member(name: str) -> Path:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("KIN-009 unsafe source archive member")
    return Path(*pure.parts)


def page_payload(path: Path, page_ordinal: int) -> dict[str, object]:
    document = fitz.open(path)
    page = document[page_ordinal - 1]
    text = page.get_text("text")
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    png = pixmap.tobytes("png")
    return {
        "source_page_ordinal": page_ordinal,
        "complete_extracted_page_text": text,
        "complete_extracted_page_text_hash": sha_bytes(text.encode("utf-8")),
        "complete_rendered_page_hash": sha_bytes(png),
        "rendered_page_width": pixmap.width,
        "rendered_page_height": pixmap.height,
    }


def main() -> None:
    for path, expected in ((SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH)):
        if sha_file(path) != expected:
            raise ValueError(f"KIN-009 sealed registration changed: {path}")
    for name, expected in SOURCE_HASHES.items():
        if sha_file(SNAPSHOT_ROOT / name) != expected:
            raise ValueError(f"KIN-009 source snapshot changed: {name}")
    identities_document = json.loads(IDENTITY_PATH.read_text())
    identities = tuple(identities_document.get("rows", ()))
    if identities_document.get("target_values_or_hashes_present") is not False or len(identities) != 164:
        raise ValueError("KIN-009 value-free identity seal changed")

    archive_payloads = {}
    member_root = SNAPSHOT_ROOT / "source-data-members"
    with zipfile.ZipFile(SNAPSHOT_ROOT / "source-data.zip") as archive:
        for info in archive.infolist():
            member_path = safe_member(info.filename)
            content = archive.read(info)
            destination = member_root / member_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            archive_payloads[info.filename] = {
                "source_member_identity": info.filename,
                "complete_member_snapshot_path": str(destination.relative_to(ROOT)),
                "complete_member_hash": sha_bytes(content),
                "complete_member_byte_count": len(content),
                "archive_directory_entry": info.is_dir(),
            }

    movie_path = SNAPSHOT_ROOT / "supplementary-movie.gif"
    with Image.open(movie_path) as movie:
        movie_payload = {
            "complete_movie_hash": sha_file(movie_path),
            "complete_movie_byte_count": movie_path.stat().st_size,
            "frame_count": getattr(movie, "n_frames", 1),
            "pixel_width": movie.width,
            "pixel_height": movie.height,
            "source_format": movie.format,
        }

    rows = []
    for identity in identities:
        document_identity = identity["source_document_identity"]
        if document_identity.endswith(".pdf"):
            payload = page_payload(SNAPSHOT_ROOT / document_identity, identity["source_page_ordinal"])
        elif document_identity == "supplementary-movie.gif":
            payload = movie_payload
        elif document_identity == "source-data.zip":
            payload = archive_payloads[identity["source_record_identity"]]
        else:
            raise ValueError("KIN-009 unregistered source-record class")
        rows.append({**identity, "target_payload": payload})
    if len(rows) != 164:
        raise ValueError("KIN-009 complete target release changed")
    document = {
        "schema": "sft-v3-reversible-kinetic-equilibrium-withheld-target-release/1",
        "claim_id": "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-009",
        "prefetch_spec_hash": SPEC_HASH,
        "source_inventory_hash": INVENTORY_HASH,
        "identity_registry_hash": IDENTITY_HASH,
        "release_requires_complete_identity_and_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "complete_pdf_page_target_count": 155,
        "complete_supplementary_movie_target_count": 1,
        "complete_source_data_archive_member_target_count": 8,
        "all_complete_source_records_preserved": True,
        "rows": rows,
    }
    TARGET_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "target_path": str(TARGET_PATH.relative_to(ROOT)),
        "target_hash": sha_file(TARGET_PATH),
        "complete_registered_target_count": len(rows),
        "complete_pdf_page_target_count": 155,
        "complete_source_data_archive_member_target_count": 8,
        "complete_movie_frame_count": movie_payload["frame_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
