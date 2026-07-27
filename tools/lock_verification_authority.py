#!/usr/bin/env python3
"""Apply cross-platform local write protection to the sealed authority files."""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance" / "verification_authority_seal_v1.json"
EXTRA_PROTECTED = (
    MANIFEST,
    ROOT / "tools" / "verify_verification_authority_seal.py",
    Path(__file__).resolve(),
)


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = [ROOT / row["path"] for row in payload["files"]]
    paths.extend(EXTRA_PROTECTED)
    unique = tuple(dict.fromkeys(path.resolve() for path in paths))
    for path in unique:
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"cannot protect missing or symbolic authority path: {path}")
    for path in unique:
        mode = stat.S_IMODE(path.stat().st_mode)
        path.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    if sys.platform == "darwin":
        completed = subprocess.run(
            ("chflags", "uchg", *(str(path) for path in unique)),
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise SystemExit("write bits removed, but macOS user-immutable flags failed: " + completed.stderr)
    print("SFT VERIFICATION AUTHORITY: LOCAL WRITE PROTECTION APPLIED")
    print(f"protected paths: {len(unique)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
