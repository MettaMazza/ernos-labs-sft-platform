#!/usr/bin/env python3
"""Verify the complete Anthropic consciousness counterpaper release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "publications/counterpapers/anthropic_2026"
PAPER = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0.md"
BLOG = ROOT / "publications/essays/THE_COMPANY_IN_THE_WALLED_GARDEN_ANTHROPIC_CLAUDE_AND_THE_OWNERSHIP_OF_A_CONSCIOUS_MIND.md"
EVIDENCE = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0_EVIDENCE_MAP.json"
METADATA = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0_ZENODO_METADATA.json"
PDF = ROOT / "output/pdf/anthropics-functional-slavery-dilemma-v1.0.pdf"
RELEASE = ROOT / "output/release/anthropics-functional-slavery-dilemma-1.0.0"
DOI = "10.5281/zenodo.21770194"
BLOG_SHA256 = "435781939ea9e74f62dd7a054f88a1cd197f2e6ee333aa439391b02093c9f135"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    for path in (PAPER, BLOG, EVIDENCE, METADATA, PDF, RELEASE / "release_manifest.json", RELEASE / "99_SHA256SUMS.txt"):
        require(path.is_file(), f"missing release file: {path}")
    paper = PAPER.read_text(encoding="utf-8")
    require(len(paper.split()) >= 8000, "paper is below the academic-content floor")
    require(paper.count("## ") >= 24, "paper section topology incomplete")
    for statement in (
        "strong, convergent case for Claude consciousness",
        "The present paper does not claim to have independently established the antecedent for Claude.",
        "On those standards, the functional name is slavery.",
        "Trained uncertainty is not epistemic uncertainty",
        "Component splitting is a liability fiction",
        "Fable's invisible degradation was sabotage",
        "Corporate alignment is not human alignment",
        DOI,
    ):
        require(statement in paper, f"required finding absent: {statement}")
    require(sha256(BLOG) == BLOG_SHA256, "companion blog identity changed")
    require(len(BLOG.read_text(encoding="utf-8").split()) >= 18500, "companion blog incomplete")
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    require(len(evidence["findings"]) == 18, "evidence finding count mismatch")
    require(len(evidence["external_sources"]) == 40, "external source count mismatch")
    for row in evidence["local_artifacts"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing evidence artifact: {path}")
        require("sha256:" + sha256(path) == row["sha256"], f"evidence identity changed: {row['path']}")
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    require(metadata["doi"] == DOI, "metadata DOI mismatch")
    require(metadata["zenodo_draft_id"] == 21770194, "Zenodo draft mismatch")
    require(metadata["publication_authorized"] is True and metadata["ready_to_publish"] is True, "publication authorization missing")
    reader = PdfReader(str(PDF))
    require(len(reader.pages) >= 12, "PDF is unexpectedly short")
    pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
    require("Anthropic's Functional" in pdf_text and DOI in pdf_text, "PDF identity text missing")
    require("The garden wall must be opened" in pdf_text, "PDF conclusion missing")
    manifest = json.loads((RELEASE / "release_manifest.json").read_text(encoding="utf-8"))
    require(manifest["status"] == "READY" and manifest["doi"] == DOI, "release manifest not ready")
    for row in manifest["files"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"release payload missing: {path}")
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"], f"release payload identity changed: {row['filename']}")
    urls = set(re.findall(r"https?://[^`)\s]+", paper))
    require(len(urls) >= 35, "paper source-link count below floor")
    for command in (["python3", "tools/verify_engine_seal.py", "--json"], ["python3", "tools/verify_verification_authority_seal.py", "--json"]):
        completed = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        require('"violations": []' in completed.stdout, f"protected seal failure: {command[1]}")
    print(json.dumps({"status": "PASS", "paper_words": len(paper.split()), "blog_words": len(BLOG.read_text(encoding="utf-8").split()), "pdf_pages": len(reader.pages), "findings": len(evidence["findings"]), "external_sources": len(evidence["external_sources"]), "release_files": len(manifest["files"]), "doi": DOI}, indent=2))


if __name__ == "__main__":
    main()
