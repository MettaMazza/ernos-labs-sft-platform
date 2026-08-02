#!/usr/bin/env python3
"""Bind the twelve current-lineage proof certificates to their executed sources."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import build_source_manifest
from sft.openai_2026.obligations_v1 import ORDER


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    specification = importlib.util.spec_from_file_location("bind_" + claim_id.replace("-", "_"), path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        if completed.returncode or json.loads(completed.stdout).get("status") != expected:
            raise SystemExit(f"source binding halted: {tool}")
    results = []
    for claim_id in ORDER:
        built = execution(claim_id)
        manifest = build_source_manifest(ROOT, built.source_files)
        if manifest.manifest_hash != built.program.registration.source_hash:
            raise SystemExit(f"source binding halted: executable mismatch: {claim_id}")
        certificate_path = ROOT / "claims" / claim_id / "certificate.json"
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
        row = next(row for row in census["claims"] if row["claim_id"] == claim_id)
        if certificate.get("engine_receipt_hash") != row["receipt_hash"]:
            raise SystemExit(f"source binding halted: certificate lineage mismatch: {claim_id}")
        certificate["source_manifest_hash"] = manifest.manifest_hash
        write_json(certificate_path, certificate)
        results.append({"claim_id": claim_id, "source_manifest_hash": manifest.manifest_hash})
    print(json.dumps({"status": "BOUND", "count": len(results), "claims": results}, indent=2))


if __name__ == "__main__":
    main()
