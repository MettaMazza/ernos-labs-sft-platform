#!/usr/bin/env python3
"""Assemble Classical Computation Paper 001 version 1.1 release artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/release/classical-computation-1.1.0"
SUCCESSOR = ROOT / "publications/successors/computation"

FILES = (
    ("00_After-Turing-The-Fold-Machine_Classical-Computation-Branch-Paper-001-v1.1.pdf", ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001.pdf"),
    ("01_After-Turing-The-Fold-Machine_Classical-Computation-Branch-Paper-001-v1.1.md", ROOT / "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md"),
    ("02_Classical-Computation-Paper-001-v1.1-Evidence-Map.json", ROOT / "publications/current/computation/evidence_map.json"),
    ("03_Classical-Computation-Paper-001-v1.1-Manifest.json", ROOT / "publications/current/computation/manifest.json"),
    ("04_Classical-Computation-Paper-001-v1.1-Publication-Receipt.json", ROOT / "publications/current/computation/publication_receipt.json"),
    ("05_Classical-Computation-Prior-Obligations.json", ROOT / "census/computation_prior_obligations.json"),
    ("06_Classical-Computation-Frozen-Inventory.json", ROOT / "publications/inventories/computation.json"),
)


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SUCCESSOR.mkdir(parents=True, exist_ok=True)
    checksums = []
    for public_name, source in FILES:
        if not source.is_file():
            raise SystemExit(f"missing release source: {source}")
        destination = OUT / public_name
        shutil.copyfile(source, destination)
        checksums.append({"filename": public_name, "bytes": destination.stat().st_size, "sha256": sha(destination)})
    checksum_path = OUT / "07_SHA256SUMS.json"
    checksum_path.write_text(
        json.dumps({"schema": "sft-classical-computation-1.1-release-checksums/1", "files": checksums}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / "publication/computation_zenodo_metadata.json", SUCCESSOR / "zenodo_metadata.json")
    shutil.copyfile(ROOT / "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md", SUCCESSOR / "AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_1.md")
    shutil.copyfile(ROOT / "publications/current/computation/evidence_map.json", SUCCESSOR / "evidence_map.json")
    shutil.copyfile(ROOT / "publications/current/computation/manifest.json", SUCCESSOR / "manifest.json")
    shutil.copyfile(ROOT / "publications/current/computation/publication_receipt.json", SUCCESSOR / "publication_receipt.json")
    print(f"assembled {len(FILES) + 1} files in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
