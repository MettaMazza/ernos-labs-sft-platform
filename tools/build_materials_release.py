#!/usr/bin/env python3
"""Build the deterministic four-file Materials Science archival release."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "output/release/materials-1.0.0"
PREFIX = "ernos-labs-sft-materials-branch-1.0.0/"
FILES = {
    "00_From-Fold-to-Materials_Materials-Science-Branch-Paper-001.pdf": ROOT / "output/pdf/from-fold-to-materials-branch-paper-001.pdf",
    "02_From-Fold-to-Materials_Materials-Science-Branch-Paper-001.md": ROOT / "publications/current/materials/FROM_FOLD_TO_MATERIALS.md",
}
ARCHIVE = "01_Ernos-Labs-SFT-Materials-Branch-Evidence-and-Source-v1.0.0.zip"
CHECKSUMS = "99_SHA256SUMS.txt"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    for existing in RELEASE.iterdir():
        if existing.is_file():
            existing.unlink()
    for public_name, source in FILES.items():
        if not source.is_file():
            raise SystemExit(f"missing release input: {source.relative_to(ROOT)}")
        shutil.copyfile(source, RELEASE / public_name)
    subprocess.run(
        ["git", "archive", "--format=zip", f"--prefix={PREFIX}", "HEAD", "-o", str(RELEASE / ARCHIVE)],
        cwd=ROOT,
        check=True,
    )
    names = sorted(name for name in (*FILES, ARCHIVE))
    ledger = "".join(f"{digest(RELEASE / name)}  {name}\n" for name in names)
    (RELEASE / CHECKSUMS).write_text(ledger, encoding="utf-8")
    for name in (*names, CHECKSUMS):
        print(f"{name} sha256:{digest(RELEASE / name)}")


if __name__ == "__main__":
    main()
