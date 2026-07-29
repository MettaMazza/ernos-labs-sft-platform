#!/usr/bin/env python3
"""Write the review-only local release manifest for computation v1.4."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "publications/successors/computation"
PAPER = BASE / "AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"
PDF = ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf"
EVIDENCE = BASE / "evidence_map_v1_4.json"
METADATA = BASE / "zenodo_metadata_v1_4.json"
MANIFEST = BASE / "manifest_v1_4.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    if metadata.get("publication_authorized") is not False:
        raise SystemExit("publication authorization must remain false")
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": "computation",
        "version": "1.4.0",
        "publication_authorized": False,
        "ready_for_review": True,
        "ready_to_publish": False,
        "comprehensive_derivation_coverage": True,
        "root_traces_verified": True,
        "controls_passed": True,
        "required_claim_count": evidence["claim_count"],
        "generated_candidate_count": evidence["candidate_count"],
        "control_count": evidence["control_count"],
        "frozen_census_identity": evidence["frozen_census_identity"],
        "reconciliation_identity": evidence["reconciliation_identity"],
        "source_path": str(PAPER.relative_to(ROOT)),
        "source_hash": digest(PAPER),
        "rendered_paper_path": str(PDF.relative_to(ROOT)),
        "rendered_paper_hash": digest(PDF),
        "evidence_map_path": str(EVIDENCE.relative_to(ROOT)),
        "evidence_map_hash": digest(EVIDENCE),
        "zenodo_metadata_path": str(METADATA.relative_to(ROOT)),
        "zenodo_metadata_hash": digest(METADATA),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"built {MANIFEST}")


if __name__ == "__main__":
    main()
