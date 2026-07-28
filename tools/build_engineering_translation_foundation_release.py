#!/usr/bin/env python3
"""Build and verify the local Engineering Translation evidence release."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output/release/engineering-translation-1.0.0"
MD = ROOT / "publications/current/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md"
PDF = ROOT / "output/pdf/from-one-law-to-a-working-world-engineering-translation-foundation-paper-001-v1.0.pdf"
META = ROOT / "publication/engineering_translation_foundation_zenodo_metadata.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    metadata = json.loads(META.read_text())
    integration = json.loads((ROOT / "audits/engineering_translation_foundation_integration.json").read_text())
    if metadata["publication_authorized"] is not False or metadata["remote_publish_status"] != "not_authorized":
        raise ValueError("remote publication state changed")
    if integration["admitted_claim_count"] != 72 or integration["candidate_count"] != 18432:
        raise ValueError("Engineering integration incomplete")
    pages = len(PdfReader(str(PDF)).pages)
    words = len(MD.read_text().split())
    if pages < 100 or words < 30000:
        raise ValueError("paper depth gate failed")
    RELEASE.mkdir(parents=True, exist_ok=True)
    md_name = "02_From-One-Law-to-a-Working-World_Engineering-Translation-Foundation-Paper-001-v1.0.md"
    pdf_name = "01_From-One-Law-to-a-Working-World_Engineering-Translation-Foundation-Paper-001-v1.0.pdf"
    shutil.copy2(MD, RELEASE / md_name)
    shutil.copy2(PDF, RELEASE / pdf_name)
    shutil.copy2(META, RELEASE / "03_Zenodo-Metadata.json")
    evidence = [
        path
        for base in (
            ROOT / "claims",
            ROOT / "experiments/engineering_translation",
            ROOT / "audits",
            ROOT / "publications/inventories",
            ROOT / "census",
        )
        for path in base.rglob("*")
        if path.is_file() and ("SFT-ENG-" in str(path) or "engineering_translation" in path.name or "engineering-translation" in path.name)
    ]
    zip_path = RELEASE / "04_Engineering-Translation-Foundation-Evidence-1.0.0.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(set(evidence)):
            archive.write(path, path.relative_to(ROOT))
    files = sorted(path for path in RELEASE.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    manifest = {
        "schema": "sft-v3-engineering-translation-foundation-local-release/1",
        "version": "1.0.0",
        "publication_authorized": False,
        "remote_actions_performed": False,
        "paper_words": words,
        "pdf_pages": pages,
        "claims": 72,
        "candidates": 18432,
        "evidence_files": len(evidence),
        "integration_hash": integration["integration_hash"],
        "files": {path.name: "sha256:" + sha(path) for path in files},
    }
    manifest["release_hash"] = "sha256:" + hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (RELEASE / "release_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    files = sorted(path for path in RELEASE.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (RELEASE / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files))
    checkpoint = ROOT / "census/engineering_translation_continuation_checkpoint.json"
    state = json.loads(checkpoint.read_text())
    state.update(
        {
            "status": "foundational_branch_current_evidence_closed_extension_open_local_release_ready",
            "paper_path": str(MD.relative_to(ROOT)),
            "pdf_path": str(PDF.relative_to(ROOT)),
            "paper_word_count": words,
            "pdf_page_count": pages,
            "local_release_path": str(RELEASE.relative_to(ROOT)),
            "local_release_hash": manifest["release_hash"],
            "remote_publication_authorized": False,
            "next_exact_operation": "commit_branch_artifacts_locally_then_reconcile_all_foundations",
        }
    )
    checkpoint.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"Engineering local release gate: PASS claims=72 candidates=18432 words={words} pages={pages} evidence={len(evidence)} publication_authorized=false")


if __name__ == "__main__":
    main()
