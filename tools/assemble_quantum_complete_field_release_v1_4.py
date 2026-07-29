#!/usr/bin/env python3
"""Assemble the review-only Quantum Computation v1.4 local release."""

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/release/quantum-computation-1.4.0"
BASE = ROOT / "publications/successors/quantum_computation"
FILES = (
    ("00_The-Quantum-Fold-Machine_Quantum-Computation-Branch-Paper-001-v1.4.pdf", ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001-v1.4.pdf"),
    ("01_The-Quantum-Fold-Machine_Quantum-Computation-Branch-Paper-001-v1.4.md", BASE / "THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md"),
    ("02_Quantum-Computation-Paper-001-v1.4-Evidence-Map.json", BASE / "evidence_map_v1_4.json"),
    ("03_Quantum-Computation-Paper-001-v1.4-Manifest.json", BASE / "manifest_v1_4.json"),
    ("04_Quantum-Computation-Paper-001-v1.4-Zenodo-Metadata-Draft.json", BASE / "zenodo_metadata_v1_4.json"),
    ("05_Quantum-Computation-Frozen-Complete-Field-Census.json", ROOT / "census/quantum_computation_discipline_obligations.json"),
    ("06_Quantum-Computation-Final-Reconciliation-v13.json", ROOT / "census/quantum_computation_discipline_current_reconciliation_v13.json"),
    ("07_Quantum-Computation-Active-Completion-Checkpoint.md", ROOT / "audits/ACTIVE_QUANTUM_COMPUTATION_CONTINUATION_CHECKPOINT_2026-07-29.md"),
)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checksums = []
    for public_name, source in FILES:
        if not source.is_file():
            raise SystemExit(f"missing release source: {source}")
        destination = OUT / public_name
        shutil.copyfile(source, destination)
        checksums.append({"filename": public_name, "bytes": destination.stat().st_size, "sha256": digest(destination)})
    checksum_path = OUT / "99_SHA256SUMS.json"
    checksum_path.write_text(
        json.dumps({"schema": "sft-quantum-computation-1.4-review-checksums/1", "publication_authorized": False, "files": checksums}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"assembled {len(FILES) + 1} review files in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
