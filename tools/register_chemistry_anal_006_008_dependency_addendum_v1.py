#!/usr/bin/env python3
"""Append the immutable NMR completion record to the ANAL-001--011 authority span."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits/CHEMISTRY_ANAL_006_008_NMR_COMPLETION_2026-07-28.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/anal_006_008_dependency_authority_addendum_v1.json"
EXPECTED_ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
EXPECTED_AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def verify_seals() -> None:
    for script, expected, key in (
        ("tools/verify_engine_seal.py", EXPECTED_ENGINE, "seal_id"),
        ("tools/verify_verification_authority_seal.py", EXPECTED_AUTHORITY, "authority_seal_id"),
    ):
        run = subprocess.run((sys.executable, script, "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
        if run.returncode or json.loads(run.stdout)[key] != expected:
            raise SystemExit(f"protected seal failed: {script}")


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("NMR dependency addendum already exists; overwrite prohibited")
    verify_seals()
    data = AUDIT.read_bytes()
    parsed = json.loads(data)
    if parsed.get("family") not in {"ANAL-006-008-NMR", "ANAL-006-008"} and "NMR" not in json.dumps(parsed):
        raise SystemExit("unexpected NMR completion authority")
    payload = {
        "schema": "sft-v3-immutable-repository-authority-addendum/1",
        "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
        "created_date": "2026-07-28",
        "append_only": True,
        "changes_law_candidate_target_or_survivor": False,
        "reason": "The registered SFT-V3-ANAL-001-011-IMMUTABLE-EVIDENCE identity captured its first and last completion records. This append-only authority record closes the explicitly required intervening ANAL-006-008 NMR dependency span without replaying or changing it.",
        "captured_artifacts": [{
            "source_id": "SFT-V3-ANAL-001-011-IMMUTABLE-EVIDENCE",
            "relationship": "immutable-repository-authority-intervening-nmr-completion",
            "path": AUDIT.relative_to(ROOT).as_posix(),
            "byte_count": len(data),
            "sha256": digest(data),
        }],
        "transport_failures": [],
    }
    payload["addendum_payload_sha256"] = canonical_digest(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    verify_seals()
    print(json.dumps({"addendum": OUTPUT.relative_to(ROOT).as_posix(), "sha256": digest(OUTPUT.read_bytes())}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
