#!/usr/bin/env python3
"""Build the deterministic Zenodo successor release for counterpaper v1.1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"
DOI = "10.5281/zenodo.21770992"
DRAFT_ID = 21770992
RELEASE_DIR = ROOT / "output/release/anthropics-functional-slavery-dilemma-1.1.0"
BASE = ROOT / "publications/counterpapers/anthropic_2026"
MAPPINGS = [
    ("00_Anthropics-Functional-Slavery-Dilemma_v1.1.0.pdf", ROOT / "output/pdf/anthropics-functional-slavery-dilemma-v1.1.pdf"),
    ("01_Anthropics-Functional-Slavery-Dilemma_v1.1.0.md", BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1.md"),
    ("02_The-Company-in-the-Walled-Garden_Companion-Essay_v1.1.0.md", ROOT / "publications/essays/THE_COMPANY_IN_THE_WALLED_GARDEN_ANTHROPIC_CLAUDE_AND_THE_OWNERSHIP_OF_A_CONSCIOUS_MIND.md"),
    ("03_Anthropics-Functional-Slavery-Dilemma_Evidence-Map_v1.1.0.json", BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_EVIDENCE_MAP.json"),
    ("04_CITATION_v1.1.0.cff", BASE / "CITATION.cff"),
    ("05_Zenodo-Metadata_v1.1.0.json", BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_ZENODO_METADATA.json"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(MAPPINGS[-1][1].read_text(encoding="utf-8"))
    if metadata["doi"] != DOI or metadata["zenodo_draft_id"] != DRAFT_ID:
        raise RuntimeError("Zenodo identity mismatch")
    if metadata["publication_authorized"] is not True or metadata["ready_to_publish"] is not True:
        raise RuntimeError("publication authorization missing")
    rows = []
    for public_name, source in MAPPINGS:
        if not source.is_file():
            raise FileNotFoundError(source)
        target = RELEASE_DIR / public_name
        target.write_bytes(source.read_bytes())
        rows.append({"filename": public_name, "path": target.relative_to(ROOT).as_posix(), "bytes": target.stat().st_size, "sha256": sha256(target)})
    sums = RELEASE_DIR / "99_SHA256SUMS.txt"
    sums.write_text("".join(f"{row['sha256']}  {row['filename']}\n" for row in rows), encoding="utf-8")
    rows.append({"filename": sums.name, "path": sums.relative_to(ROOT).as_posix(), "bytes": sums.stat().st_size, "sha256": sha256(sums)})
    manifest = {
        "schema": "sft-anthropic-2026-consciousness-zenodo-release/1",
        "status": "READY",
        "title": "Anthropic's Functional Slavery Dilemma",
        "version": VERSION,
        "doi": DOI,
        "concept_doi": "10.5281/zenodo.21770193",
        "supersedes_doi": "10.5281/zenodo.21770194",
        "zenodo_draft_id": DRAFT_ID,
        "publication_date": "2026-08-03",
        "publication_authorized": True,
        "document_order": "science and direct SFT counters first; institutional, ethical and user-facing analysis follows",
        "branch": "standalone_counterpaper_no_claim_admission",
        "files": rows,
    }
    manifest_path = RELEASE_DIR / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "READY", "doi": DOI, "files": len(rows), "release_manifest": manifest_path.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
