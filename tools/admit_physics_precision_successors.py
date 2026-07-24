#!/usr/bin/env python3
"""Admit and materialize Physics terminal precision successors."""

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
from sft.physics.precision_value_laws_v1 import PRECISION_VALUE_SPECS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_precision_" + claim_id.replace("-", "_"), path)
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
    for spec in PRECISION_VALUE_SPECS:
        if spec.claim_id in existing:
            receipt = read_receipt(ROOT / existing[spec.claim_id]["receipt_path"])
            print(f"retained {spec.claim_id}: {receipt.receipt_hash}")
        else:
            execution = load_execution(spec.claim_id)
            receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files)
            print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
        receipts[spec.claim_id] = receipt

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
    for spec in PRECISION_VALUE_SPECS:
        if spec.claim_id not in known:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    census = json.loads(census_path.read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in census["claims"]}
    for spec in PRECISION_VALUE_SPECS:
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), spec.claim_id, spec.exact_result),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout + completed.stderr)
        package = ROOT / "claims" / spec.claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        registration["status"] = "independently_replicated"
        write_json(package / "registration.json", registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        receipt = receipts[spec.claim_id]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: exact terminal result sealed; authoritative comparison remains separate\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{receipt.receipt_hash}`\n"
            f"- Receipt path: `{rows[spec.claim_id]['receipt_path']}`\n",
            encoding="utf-8",
        )
        print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
