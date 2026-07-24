#!/usr/bin/env python3
"""Execute, admit and materialize the unbounded finite fault-order theorem."""

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
from sft.quantum_computation.lineage_laws import UNBOUNDED_FAULT_TOLERANCE as SPEC  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_quantum_lineage_admission", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load quantum lineage execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    census_path = ROOT / "census" / "claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"]: row for row in census["claims"]}
    if SPEC.claim_id not in existing:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files)
        print(f"admitted {SPEC.claim_id}: {receipt.receipt_hash}")
    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if SPEC.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": SPEC.claim_id, "execution_file": f"claims/{SPEC.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), SPEC.claim_id, SPEC.exact_result),
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    registration_path = ROOT / "claims" / SPEC.claim_id / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(registration_path, registration)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == SPEC.claim_id)
    certificate = json.loads((ROOT / "claims" / SPEC.claim_id / "certificate.json").read_text(encoding="utf-8"))
    (ROOT / "claims" / SPEC.claim_id / "STATUS.md").write_text(
        f"# {SPEC.claim_id}\n\nStatus: `independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        "- Empirical status: formal unbounded positive-finite code theorem; physical threshold measurement not applicable\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- External validation: `{certificate['external_validation_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n"
        f"- Receipt path: `{row['receipt_path']}`\n",
        encoding="utf-8",
    )
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
