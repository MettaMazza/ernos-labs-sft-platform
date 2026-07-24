#!/usr/bin/env python3
"""Admit and materialize all gravity/spacetime successor claims."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.physics.gravity_spacetime_laws_v1 import GRAVITY_SPACETIME_SPECS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_physics_gravity_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    repository = EngineRepository(ROOT)
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    receipts = {}
    for position, item in enumerate(GRAVITY_SPACETIME_SPECS, 1):
        if item.claim_id in existing:
            receipt = read_receipt(ROOT / existing[item.claim_id]["receipt_path"])
            print(f"[{position}/{len(GRAVITY_SPACETIME_SPECS)}] retained {item.claim_id}: {receipt.receipt_hash}")
        else:
            execution = load_execution(item.claim_id)
            receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files)
            print(f"[{position}/{len(GRAVITY_SPACETIME_SPECS)}] admitted {item.claim_id}: {receipt.receipt_hash}")
            existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
        receipts[item.claim_id] = receipt

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
    for item in GRAVITY_SPACETIME_SPECS:
        if item.claim_id not in known:
            manifest["claims"].append({"claim_id": item.claim_id, "execution_file": f"claims/{item.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    for position, item in enumerate(GRAVITY_SPACETIME_SPECS, 1):
        completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), item.claim_id, item.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout + completed.stderr)
        package = ROOT / "claims" / item.claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        registration["status"] = "independently_replicated"
        write_json(package / "registration.json", registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        receipt = receipts[item.claim_id]
        (package / "STATUS.md").write_text(
            f"# {item.claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: formal exact result sealed; authoritative comparison remains separate\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{receipt.receipt_hash}`\n"
            f"- Receipt path: `{rows[item.claim_id]['receipt_path']}`\n",
            encoding="utf-8",
        )
        print(f"[{position}/{len(GRAVITY_SPACETIME_SPECS)}] materialized {item.claim_id}")


if __name__ == "__main__":
    main()
