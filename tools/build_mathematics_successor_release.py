#!/usr/bin/env python3
"""Assemble Mathematics Paper 001 version 1.2 and its exact evidence archive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/release/mathematics-1.2.0"
SUCCESSOR = ROOT / "publications/successors/mathematics"
INVENTORY = ROOT / "publications/inventories/mathematics.json"

FILES = (
    ("00_From-Fold-to-Mathematics_Mathematics-Branch-Paper-001-v1.2.pdf", ROOT / "output/pdf/from-fold-to-mathematics-branch-paper-001.pdf"),
    ("01_From-Fold-to-Mathematics_Mathematics-Branch-Paper-001-v1.2.md", ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md"),
    ("03_Mathematics-Paper-001-v1.2-Evidence-Map.json", ROOT / "publications/current/mathematics/evidence_map.json"),
    ("04_Mathematics-Paper-001-v1.2-Manifest.json", ROOT / "publications/current/mathematics/manifest.json"),
    ("05_Mathematics-Paper-001-v1.2-Publication-Receipt.json", ROOT / "publications/current/mathematics/publication_receipt.json"),
    ("06_Mathematics-Prior-Obligations.json", ROOT / "census/mathematics_prior_obligations.json"),
    ("07_Mathematics-Version-1.2-Inventory.json", INVENTORY),
    ("08_Smithian-Fold-Calculator-Completion-Audit.md", ROOT / "audits/SFT_CALCULATOR_COMPLETION_AUDIT_2026-07-25.md"),
)


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_paths() -> tuple[Path, ...]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    rows = {row["claim_id"]: row for row in census}
    selected: set[Path] = {
        ROOT / "AGENTS.md",
        ROOT / "CONSTITUTION.md",
        ROOT / "pyproject.toml",
        ROOT / "sft/mathematics/README.md",
        ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md",
        ROOT / "publications/current/mathematics/evidence_map.json",
        ROOT / "publications/current/mathematics/manifest.json",
        ROOT / "publications/current/mathematics/publication_receipt.json",
        INVENTORY,
        ROOT / "census/mathematics_prior_obligations.json",
        ROOT / "audits/SFT_CALCULATOR_COMPLETION_AUDIT_2026-07-25.md",
    }
    for path in (ROOT / "sft/mathematics").rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            selected.add(path)
    for claim_id in inventory["required_claim_ids"]:
        for path in (ROOT / "claims" / claim_id).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                selected.add(path)
        selected.add(ROOT / rows[claim_id]["receipt_path"])
    for base in (ROOT / "generated/mathematics", ROOT / "calculator_launchers", ROOT / "launchers"):
        for path in base.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                selected.add(path)
    for path in (ROOT / "tests").glob("test_mathematics*.py"):
        selected.add(path)
    for path in (ROOT / "tools").glob("*mathematics*.py"):
        selected.add(path)
    selected.add(ROOT / "tools/validate_mathematics_calculator.py")
    for path in selected:
        if not path.is_file():
            raise SystemExit(f"missing source archive member: {path}")
    return tuple(sorted(selected, key=lambda value: value.relative_to(ROOT).as_posix()))


def write_archive(path: Path) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for source in evidence_paths():
            name = source.relative_to(ROOT).as_posix()
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())


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

    archive_path = OUT / "02_Ernos-Labs-SFT-Mathematics-Branch-Evidence-and-Source-v1.2.0.zip"
    write_archive(archive_path)
    checksums.insert(2, {"filename": archive_path.name, "bytes": archive_path.stat().st_size, "sha256": sha(archive_path)})

    checksum_path = OUT / "09_SHA256SUMS.json"
    checksum_path.write_text(
        json.dumps({"schema": "sft-mathematics-1.2-release-checksums/1", "files": checksums}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / "publication/mathematics_zenodo_metadata.json", SUCCESSOR / "zenodo_metadata.json")
    shutil.copyfile(ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md", SUCCESSOR / "FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_2.md")
    shutil.copyfile(ROOT / "publications/current/mathematics/evidence_map.json", SUCCESSOR / "evidence_map.json")
    shutil.copyfile(ROOT / "publications/current/mathematics/manifest.json", SUCCESSOR / "manifest.json")
    shutil.copyfile(ROOT / "publications/current/mathematics/publication_receipt.json", SUCCESSOR / "publication_receipt.json")
    print(f"assembled {len(checksums) + 1} files in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
