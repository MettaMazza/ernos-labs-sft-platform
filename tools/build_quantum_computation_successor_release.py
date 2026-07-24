#!/usr/bin/env python3
"""Assemble Quantum Computation Paper 001 version 1.1 release artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/release/quantum-computation-1.1.0"
SUCCESSOR = ROOT / "publications/successors/quantum_computation"

FILES = (
    ("00_The-Quantum-Fold-Machine_Quantum-Computation-Branch-Paper-001-v1.1.pdf", ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001.pdf"),
    ("01_The-Quantum-Fold-Machine_Quantum-Computation-Branch-Paper-001-v1.1.md", ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md"),
    ("02_Quantum-Computation-Paper-001-v1.1-Evidence-Map.json", ROOT / "publications/current/quantum_computation/evidence_map.json"),
    ("03_Quantum-Computation-Paper-001-v1.1-Manifest.json", ROOT / "publications/current/quantum_computation/manifest.json"),
    ("04_Quantum-Computation-Paper-001-v1.1-Publication-Receipt.json", ROOT / "publications/current/quantum_computation/publication_receipt.json"),
    ("05_Quantum-Computation-Prior-Obligations.json", ROOT / "census/quantum_computation_prior_obligations.json"),
    ("06_Quantum-Computation-Frozen-Inventory.json", ROOT / "publications/inventories/quantum_computation.json"),
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
    checksum_path.write_text(json.dumps({"schema": "sft-quantum-computation-1.1-release-checksums/1", "files": checksums}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copyfile(ROOT / "publication/quantum_computation_zenodo_metadata.json", SUCCESSOR / "zenodo_metadata.json")
    shutil.copyfile(ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md", SUCCESSOR / "THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_1.md")
    shutil.copyfile(ROOT / "publications/current/quantum_computation/evidence_map.json", SUCCESSOR / "evidence_map.json")
    shutil.copyfile(ROOT / "publications/current/quantum_computation/manifest.json", SUCCESSOR / "manifest.json")
    shutil.copyfile(ROOT / "publications/current/quantum_computation/publication_receipt.json", SUCCESSOR / "publication_receipt.json")
    print(f"assembled {len(FILES) + 1} files in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
