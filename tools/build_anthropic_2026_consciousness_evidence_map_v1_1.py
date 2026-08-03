#!/usr/bin/env python3
"""Build the source-bound evidence map for v1.1 of the Anthropic counterpaper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_anthropic_2026_consciousness_evidence_map_v1 import FINDINGS, SOURCES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_EVIDENCE_MAP.json"
LOCAL = [
    "CONSTITUTION.md",
    "audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md",
    "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1.md",
    "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1_ZENODO_METADATA.json",
    "publications/counterpapers/anthropic_2026/CITATION.cff",
    "publications/counterpapers/anthropic_2026/README.md",
    "publications/essays/THE_COMPANY_IN_THE_WALLED_GARDEN_ANTHROPIC_CLAUDE_AND_THE_OWNERSHIP_OF_A_CONSCIOUS_MIND.md",
    "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_1_1.md",
    "publications/lean4_verification/SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_PAPER_V1_0_1.md",
    "tools/render_anthropic_2026_consciousness_counterpaper_v1_1.py",
    "tools/build_anthropic_2026_consciousness_evidence_map_v1_1.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    local = []
    for name in LOCAL:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        local.append({"path": name, "bytes": path.stat().st_size, "sha256": "sha256:" + sha256(path)})
    document = {
        "schema": "sft-anthropic-2026-consciousness-evidence-map/1",
        "title": "Anthropic's Functional Slavery Dilemma",
        "version": "1.1.0",
        "doi": "10.5281/zenodo.21770992",
        "concept_doi": "10.5281/zenodo.21770193",
        "supersedes_doi": "10.5281/zenodo.21770194",
        "publication_date": "2026-08-03",
        "document_order": "SFT derivation and direct scientific counters precede institutional, ethical and user-facing consequences",
        "classification": "standalone critical application of published SFT consciousness criterion; no new model admission",
        "protected_engine_modified": False,
        "verification_authority_modified": False,
        "external_sources": [
            {"id": sid, "class": cls, "url": url, "last_checked": "2026-08-03"}
            for sid, cls, url in SOURCES
        ],
        "findings": FINDINGS,
        "local_artifacts": local,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "findings": len(FINDINGS),
        "external_sources": len(SOURCES),
        "local_artifacts": len(local),
        "output": OUT.relative_to(ROOT).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
