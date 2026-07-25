#!/usr/bin/env python3
"""Assemble Physics Branch Paper 001 version 1.1 release artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/release/physics-1.1.0"
PDF_NAME = "00_From-Fold-to-Physics_Physics-Branch-Paper-001-v1.1.pdf"
MD_NAME = "01_From-Fold-to-Physics_Physics-Branch-Paper-001-v1.1.md"
ZIP_NAME = "02_Ernos-Labs-SFT-Physics-Branch-Evidence-and-Source-v1.1.0.zip"
SUM_NAME = "99_SHA256SUMS.txt"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked() -> list[Path]:
    names = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    prefixes = (
        "claims/SFT-PHYS-", "receipts/engine/model_admitted/SFT-PHYS-",
        "sft/engine/", "sft/physics/", "generated/physics/",
        "experiments/physics/", "experiments/external_sources/physics/",
        "publications/current/physics/", "publications/inventories/physics.json",
    )
    exact = {
        "census/claims.json", "census/branches.json", "census/prior_obligation_ownership.json",
        "publication/physics_zenodo_metadata.json", "publication/physics_github_metadata.json",
        "tools/build_physics_branch_scope.py", "tools/build_physics_paper.py",
        "tools/render_physics_paper.py", "tools/verify_physics_publication.py",
        "tools/verify_physics_successor_gate.py", "tools/verify_publication_compliance.py",
        "tools/publish_zenodo_deposit.py", "sft/publication_compliance.py",
        "LICENSE", "LICENSE-CODE", "LICENSE-DOCS", "CITATION.cff",
    }
    selected = [ROOT / name for name in names if name in exact or name.startswith(prefixes)]
    return [path for path in selected if path.is_file()]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.iterdir():
        if path.is_file():
            path.unlink()
    shutil.copyfile(ROOT / "output/pdf/from-fold-to-physics-branch-paper-001.pdf", OUT / PDF_NAME)
    shutil.copyfile(ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md", OUT / MD_NAME)
    with zipfile.ZipFile(OUT / ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(tracked()):
            name = "ernos-labs-sft-physics-branch-1.1.0/" + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, (2026, 7, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    ordered = [PDF_NAME, MD_NAME, ZIP_NAME]
    (OUT / SUM_NAME).write_text("".join(f"{sha(OUT / name)}  {name}\n" for name in ordered), encoding="utf-8")
    for name in [*ordered, SUM_NAME]:
        path = OUT / name
        print(f"{name} bytes={path.stat().st_size} sha256:{sha(path)}")


if __name__ == "__main__":
    main()
