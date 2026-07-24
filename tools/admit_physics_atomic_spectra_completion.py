#!/usr/bin/env python3
"""Admit and materialize the atomic-spectrum completion group."""

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
from sft.physics.atomic_spectra_completion_laws_v1 import ATOMIC_SPECS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location(f"sft_atomic_spectra_{claim_id}", path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load atomic-spectrum execution: {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    repository = EngineRepository(ROOT)
    manifest_path = ROOT / "census/execution_manifest.json"
    for spec in ATOMIC_SPECS:
        census_path = ROOT / "census/claims.json"
        existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
        if spec.claim_id in existing:
            receipt = read_receipt(ROOT / existing[spec.claim_id]["receipt_path"])
            print(f"retained {spec.claim_id}: {receipt.receipt_hash}")
        else:
            execution = load_execution(spec.claim_id)
            receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files)
            print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
            write_json(manifest_path, manifest)
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), spec.claim_id, spec.exact_result),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout + completed.stderr)
        rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
        package = ROOT / "claims" / spec.claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        registration["status"] = "independently_replicated"
        write_json(package / "registration.json", registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{receipt.receipt_hash}`\n"
            f"- Receipt path: `{rows[spec.claim_id]['receipt_path']}`\n",
            encoding="utf-8",
        )
        print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
