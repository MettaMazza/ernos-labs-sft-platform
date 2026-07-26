#!/usr/bin/env python3
"""Admit the versioned exact Koide measured-value validation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository
from sft.physics.charged_lepton_validation import KOIDE_VALIDATION_CLAIM_ID, KOIDE_VALIDATION_SPEC


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / KOIDE_VALIDATION_CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_koide_v2_validation_execution", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load versioned Koide validation execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(
        execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator
    )
    if not receipt.model_admitted:
        raise RuntimeError("versioned Koide validation was not admitted")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if KOIDE_VALIDATION_CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": KOIDE_VALIDATION_CLAIM_ID, "execution_file": f"claims/{KOIDE_VALIDATION_CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), KOIDE_VALIDATION_CLAIM_ID, KOIDE_VALIDATION_SPEC.exact_result),
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    print(f"admitted {KOIDE_VALIDATION_CLAIM_ID}: {receipt.receipt_hash}")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
