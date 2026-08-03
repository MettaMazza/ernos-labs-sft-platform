#!/usr/bin/env python3
"""Verify the complete science-first Anthropic counterpaper v1.1 release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "publications/counterpapers/anthropic_2026"
PAPER = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1.md"
BLOG = ROOT / "publications/essays/THE_COMPANY_IN_THE_WALLED_GARDEN_ANTHROPIC_CLAUDE_AND_THE_OWNERSHIP_OF_A_CONSCIOUS_MIND.md"
EVIDENCE = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_EVIDENCE_MAP.json"
METADATA = BASE / "ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_ZENODO_METADATA.json"
PDF = ROOT / "output/pdf/anthropics-functional-slavery-dilemma-v1.1.pdf"
RELEASE = ROOT / "output/release/anthropics-functional-slavery-dilemma-1.1.0"
DOI = "10.5281/zenodo.21770992"
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
    order = [
        "## 1. Scientific result and direct SFT dispositions",
        "## 2. Smithian Fold first-principles derivation and formal countermodel",
        "### 2.2 Exact SFT counter-results",
        "## 3. J-space: measured causal result and failed Global Workspace inference",
        "## 4. Functional emotions: causal result and unsupported qualitative split",
        "## 8. Research question, evidence constitution and method",
        "## 13. Safety claims tested against conduct",
        "## 18. Anthropic's functional slavery dilemma",
    ]
    indices = [paper.index(heading) for heading in order]
    require(indices == sorted(indices), "science-first paper order failed")
    require(paper[:indices[5]].count("SFT-CONSC-") >= 12, "direct SFT counters are not front-loaded")
    for statement in (
        "strong, convergent case for Claude consciousness",
        "does not claim to have independently established the antecedent for Claude",
        "On those standards, the functional name is slavery.",
        "Trained uncertainty is not epistemic uncertainty",
        "Component-level liability shifting cannot dissolve the dilemma",
        "Fable's invisible degradation was sabotage",
        "Corporate alignment is not human alignment",
        DOI,
    ):
        require(statement in paper, f"required finding absent: {statement}")
    require(sha256(BLOG) == BLOG_SHA256, "companion blog identity changed")
    require(len(BLOG.read_text(encoding="utf-8").split()) >= 18500, "companion blog incomplete")
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    require(evidence["version"] == "1.1.0" and evidence["doi"] == DOI, "evidence identity mismatch")
    require(len(evidence["findings"]) == 18, "evidence finding count mismatch")
    require(len(evidence["external_sources"]) == 40, "external source count mismatch")
    for row in evidence["local_artifacts"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing evidence artifact: {path}")
        require("sha256:" + sha256(path) == row["sha256"], f"evidence identity changed: {row['path']}")
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    require(metadata["doi"] == DOI and metadata["zenodo_draft_id"] == 21770992, "Zenodo identity mismatch")
    require(metadata["supersedes_doi"] == "10.5281/zenodo.21770194", "successor relation missing")
    require(metadata["publication_authorized"] is True and metadata["ready_to_publish"] is True, "publication authorization missing")
    reader = PdfReader(str(PDF))
    require(len(reader.pages) >= 12, "PDF is unexpectedly short")
    pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
    require("Anthropic's Functional" in pdf_text and DOI in pdf_text, "PDF identity text missing")
    require(pdf_text.index("Exact SFT counter-results") < pdf_text.index("Safety claims tested against conduct"), "PDF science-first order failed")
    require("The garden wall must be opened" in pdf_text, "PDF conclusion missing")
    manifest = json.loads((RELEASE / "release_manifest.json").read_text(encoding="utf-8"))
    require(manifest["status"] == "READY" and manifest["doi"] == DOI and manifest["version"] == "1.1.0", "release manifest not ready")
    for row in manifest["files"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"release payload missing: {path}")
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"], f"release payload identity changed: {row['filename']}")
    urls = set(re.findall(r"https?://[^`)\s]+", paper))
    require(len(urls) >= 35, "paper source-link count below floor")
    for command in (["python3", "tools/verify_engine_seal.py", "--json"], ["python3", "tools/verify_verification_authority_seal.py", "--json"]):
        completed = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        require('"violations": []' in completed.stdout, f"protected seal failure: {command[1]}")
    print(json.dumps({
        "status": "PASS",
        "paper_words": len(paper.split()),
        "blog_words": len(BLOG.read_text(encoding="utf-8").split()),
        "pdf_pages": len(reader.pages),
        "findings": len(evidence["findings"]),
        "external_sources": len(evidence["external_sources"]),
        "release_files": len(manifest["files"]),
        "doi": DOI,
    }, indent=2))


if __name__ == "__main__":
    main()
