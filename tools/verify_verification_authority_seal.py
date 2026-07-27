#!/usr/bin/env python3
"""Fail closed unless every shared verification-authority byte is canonical."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "governance" / "verification_authority_seal_v1.json"
SCHEMA = "sft-v3-verification-authority-seal/1"
AUTHORITY_SEAL_ID = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def canonical_identity(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def verify() -> dict[str, Any]:
    violations: list[str] = []
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "VOID_INVALID_HALTED",
            "authority_seal_id": AUTHORITY_SEAL_ID,
            "verified_file_count": 0,
            "violations": [f"authority manifest cannot be read: {exc}"],
        }
    if not isinstance(manifest, dict):
        return {
            "status": "VOID_INVALID_HALTED",
            "authority_seal_id": AUTHORITY_SEAL_ID,
            "verified_file_count": 0,
            "violations": ["authority manifest is not an object"],
        }
    if manifest.get("schema") != SCHEMA:
        violations.append("authority schema changed")
    if manifest.get("authority_seal_id") != AUTHORITY_SEAL_ID:
        violations.append("published authority-seal identity changed")
    body = dict(manifest)
    body.pop("authority_seal_id", None)
    if canonical_identity(body) != AUTHORITY_SEAL_ID:
        violations.append("authority manifest contents differ from its canonical identity")

    rows = manifest.get("files")
    if not isinstance(rows, list):
        rows = []
        violations.append("authority file support is malformed")
    expected: dict[str, tuple[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            violations.append("authority manifest contains a malformed row")
            continue
        relative = row.get("path")
        wanted_hash = row.get("sha256")
        wanted_bytes = row.get("bytes")
        if not isinstance(relative, str) or relative.startswith("/") or ".." in Path(relative).parts:
            violations.append("authority manifest contains an invalid path")
            continue
        if relative in expected:
            violations.append(f"authority manifest repeats path: {relative}")
            continue
        if not isinstance(wanted_hash, str) or not wanted_hash.startswith("sha256:"):
            violations.append(f"authority manifest has an invalid hash: {relative}")
            continue
        if isinstance(wanted_bytes, bool) or not isinstance(wanted_bytes, int) or wanted_bytes < 1:
            violations.append(f"authority manifest has an invalid byte count: {relative}")
            continue
        expected[relative] = (wanted_hash, wanted_bytes)
    if manifest.get("file_count") != len(expected):
        violations.append("authority manifest file count differs from exact support")

    verified = 0
    for relative, (wanted_hash, wanted_bytes) in sorted(expected.items()):
        path = ROOT / relative
        if path.is_symlink():
            violations.append(f"symbolic substitution is forbidden: {relative}")
            continue
        if not path.is_file():
            violations.append(f"protected authority file is missing: {relative}")
            continue
        try:
            actual_bytes = path.stat().st_size
            actual_hash = sha256(path)
        except OSError as exc:
            violations.append(f"protected authority file cannot be read: {relative}: {exc}")
            continue
        if actual_bytes != wanted_bytes:
            violations.append(f"protected authority byte count changed: {relative}")
        if actual_hash != wanted_hash:
            violations.append(f"protected authority content changed: {relative}")
        if actual_bytes == wanted_bytes and actual_hash == wanted_hash:
            verified += 1
    return {
        "status": "VALID_CANONICAL_VERIFICATION_AUTHORITY" if not violations else "VOID_INVALID_HALTED",
        "authority_seal_id": AUTHORITY_SEAL_ID,
        "verified_file_count": verified,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    attestation = verify()
    if args.json:
        print(json.dumps(attestation, indent=2, sort_keys=True))
    elif attestation["violations"]:
        print("SFT VERIFICATION AUTHORITY VIOLATION — VOID / INVALID / HALTED", file=sys.stderr)
        print(f"Canonical seal: {attestation['authority_seal_id']}", file=sys.stderr)
        for violation in attestation["violations"]:
            print(f"- {violation}", file=sys.stderr)
    else:
        print("SFT VERIFICATION AUTHORITY: VALID CANONICAL GATES")
        print(f"Seal: {attestation['authority_seal_id']}")
        print(f"Protected files verified: {attestation['verified_file_count']}")
    return 0 if not attestation["violations"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
