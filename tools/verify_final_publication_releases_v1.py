#!/usr/bin/env python3
"""Fail closed over the seven final-publication candidate release surfaces."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paper:
    branch: str
    version: str
    previous_doi: str
    manuscript: str
    pdf: str
    evidence: str
    manifest: str
    metadata: str
    release: str
    claims: int
    candidates: int
    controls: int
    pages: int


PAPERS = (
    Paper("mathematics", "1.5.0", "10.5281/zenodo.21627708", "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md", "output/pdf/from-fold-to-mathematics-branch-paper-001-v1.5.pdf", "publications/successors/mathematics/evidence_map_v1_5.json", "publications/successors/mathematics/manifest_v1_5.json", "publications/successors/mathematics/zenodo_metadata_v1_5.json", "output/release/mathematics-1.5.0", 323, 97280, 1292, 272),
    Paper("information_science", "1.4.0", "10.5281/zenodo.21627717", "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md", "output/pdf/from-distinction-to-information-branch-paper-001-v1.4.pdf", "publications/successors/information_science/evidence_map_v1_4.json", "publications/successors/information_science/manifest_v1_4.json", "publications/successors/information_science/zenodo_metadata_v1_4.json", "output/release/information-science-1.4.0", 262, 75776, 1048, 498),
    Paper("computation", "1.4.0", "10.5281/zenodo.21627721", "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md", "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf", "publications/successors/computation/evidence_map_v1_4.json", "publications/successors/computation/manifest_v1_4.json", "publications/successors/computation/zenodo_metadata_v1_4.json", "output/release/classical-computation-1.4.0", 369, 94464, 1476, 719),
    Paper("quantum_computation", "1.4.0", "10.5281/zenodo.21627748", "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md", "output/pdf/the-quantum-fold-machine-branch-paper-001-v1.4.pdf", "publications/successors/quantum_computation/evidence_map_v1_4.json", "publications/successors/quantum_computation/manifest_v1_4.json", "publications/successors/quantum_computation/zenodo_metadata_v1_4.json", "output/release/quantum-computation-1.4.0", 288, 73728, 1152, 334),
    Paper("physics", "1.3.0", "10.5281/zenodo.21627765", "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md", "output/pdf/from-fold-to-physics-branch-paper-001-v1.3.pdf", "publications/successors/physics/v1_3/evidence_map_v1_3.json", "publications/successors/physics/v1_3/manifest_v1_3.json", "publications/successors/physics/zenodo_metadata_v1_3.json", "output/release/physics-1.3.0", 368, 257776, 1472, 886),
    Paper("chemistry", "1.3.0", "10.5281/zenodo.21627782", "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md", "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.3.pdf", "publications/successors/chemistry/evidence_map_v1.3.json", "publications/successors/chemistry/manifest_v1.3.json", "publications/successors/chemistry/zenodo_metadata_v1.3_draft.json", "output/release/chemistry-1.3.0", 281, 71936, 1124, 1796),
    Paper("materials", "1.3.0", "10.5281/zenodo.21629306", "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md", "output/pdf/from-fold-to-materials-branch-paper-001-v1.3.pdf", "publications/successors/materials/evidence_map_v1_3.json", "publications/successors/materials/manifest_v1_3.json", "publications/successors/materials/zenodo_metadata_v1_3.json", "output/release/materials-1.3.0", 289, 73984, 1156, 790),
)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def scalar(payload, *keys):
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def verify_checksum_ledger(release: Path) -> int:
    json_ledger = release / "99_SHA256SUMS.json"
    text_ledger = release / "99_SHA256SUMS.txt"
    if json_ledger.is_file():
        rows = read(json_ledger)["files"]
        require(read(json_ledger).get("publication_authorized") is False, f"authorized checksum ledger: {release}")
        for row in rows:
            path = release / row["filename"]
            require(path.is_file() and sha(path) == row["sha256"], f"checksum mismatch: {path}")
        return len(rows)
    require(text_ledger.is_file(), f"checksum ledger missing: {release}")
    rows = [line.split(None, 1) for line in text_ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    for digest, name in rows:
        path = release / name.strip()
        require(path.is_file() and sha(path) == "sha256:" + digest, f"checksum mismatch: {path}")
    return len(rows)


def main() -> None:
    manuscript_gate = {row["branch"]: row for row in read(ROOT / "audits/FINAL_PUBLICATION_MANUSCRIPT_AUDIT_V4_2026-07-29.json")["papers"]}
    pdf_gate = {row["branch"]: row for row in read(ROOT / "audits/FINAL_PUBLICATION_PDF_MECHANICAL_AUDIT_V2_2026-07-29.json")["papers"]}
    raster_gate = {row["branch"]: row for row in read(ROOT / "audits/FINAL_PUBLICATION_PDF_RASTER_REVIEW_V1_2026-07-29.json")["papers"]}
    reports = []
    for paper in PAPERS:
        manuscript = ROOT / paper.manuscript
        pdf = ROOT / paper.pdf
        evidence_path = ROOT / paper.evidence
        manifest_path = ROOT / paper.manifest
        metadata_path = ROOT / paper.metadata
        release = ROOT / paper.release
        evidence = read(evidence_path)
        manifest = read(manifest_path)
        metadata = read(metadata_path)
        require(manuscript_gate[paper.branch]["status"] == "PASS", f"manuscript gate halt: {paper.branch}")
        require(pdf_gate[paper.branch]["status"] == "PASS", f"PDF gate halt: {paper.branch}")
        require(raster_gate[paper.branch]["status"] == "PASS", f"raster gate halt: {paper.branch}")
        require(metadata["metadata"]["version"] == paper.version, f"metadata version mismatch: {paper.branch}")
        require(metadata.get("publication_authorized") is False, f"publication authorization changed: {paper.branch}")
        require(metadata.get("ready_to_publish", False) is False, f"ready-to-publish changed: {paper.branch}")
        require(any(row.get("identifier") == paper.previous_doi and row.get("relation") == "isNewVersionOf" for row in metadata["metadata"].get("related_identifiers", [])), f"existing Zenodo lineage missing: {paper.branch}")
        require(manifest.get("publication_authorized") is False, f"manifest authorization changed: {paper.branch}")
        require(evidence.get("publication_authorized") is False, f"evidence authorization changed: {paper.branch}")
        require(scalar(manifest, "source_hash", "paper_sha256") == sha(manuscript), f"manuscript manifest hash mismatch: {paper.branch}")
        require(scalar(manifest, "rendered_paper_hash", "rendered_paper_sha256") == sha(pdf), f"PDF manifest hash mismatch: {paper.branch}")
        require(scalar(manifest, "evidence_map_hash", "evidence_map_sha256") == sha(evidence_path), f"evidence manifest hash mismatch: {paper.branch}")
        if scalar(manifest, "zenodo_metadata_hash", "metadata_sha256") is not None:
            require(scalar(manifest, "zenodo_metadata_hash", "metadata_sha256") == sha(metadata_path), f"metadata manifest hash mismatch: {paper.branch}")
        claims = scalar(evidence, "required_claim_count", "claim_count", "current_claim_count", "live_claim_count")
        candidates = scalar(evidence, "required_candidate_count", "candidate_count")
        controls = scalar(evidence, "control_count")
        pages = scalar(evidence.get("pdf", {}), "pages") or scalar(evidence, "rendered_page_count") or scalar(manifest, "pdf_pages", "rendered_page_count")
        require((claims, candidates, controls, pages) == (paper.claims, paper.candidates, paper.controls, paper.pages), f"release totals mismatch: {paper.branch}")
        release_pdfs = list(release.glob("*.pdf"))
        release_mds = list(release.glob("*.md"))
        require(len(release_pdfs) == 1 and sha(release_pdfs[0]) == sha(pdf), f"release PDF mismatch: {paper.branch}")
        manuscript_matches = [path for path in release_mds if sha(path) == sha(manuscript)]
        require(len(manuscript_matches) == 1, f"release Markdown mismatch: {paper.branch}")
        checksum_files = verify_checksum_ledger(release)
        reports.append(
            {
                "branch": paper.branch,
                "version": paper.version,
                "previous_version_doi": paper.previous_doi,
                "claims": claims,
                "candidates": candidates,
                "controls": controls,
                "pages": pages,
                "manuscript_sha256": sha(manuscript),
                "pdf_sha256": sha(pdf),
                "release_checksum_file_count": checksum_files,
                "publication_authorized": False,
                "status": "PASS",
            }
        )
    result = {
        "schema": "sft-v3-final-publication-release-gate/1",
        "date": "2026-07-29",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": len(reports),
            "claims": sum(row["claims"] for row in reports),
            "candidates": sum(row["candidates"] for row in reports),
            "controls": sum(row["controls"] for row in reports),
            "pages": sum(row["pages"] for row in reports),
            "publication_authorized": False,
            "zenodo_action_performed": False,
        },
    }
    destination = ROOT / "audits/FINAL_PUBLICATION_RELEASE_GATE_V1_2026-07-29.json"
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
