#!/usr/bin/env python3
"""Admit and materialize terminal proton/electron precision."""

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
from sft.physics.matter_flavour_terminal_proton_laws_v1 import TERMINAL_PROTON_SPEC as SPEC  # noqa: E402
from sft.physics.matter_flavour_terminal_proton_validation_v1 import EMPIRICAL_SPEC  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_terminal_proton_execution", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal proton execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if SPEC.claim_id in existing:
        receipt = read_receipt(ROOT / existing[SPEC.claim_id]["receipt_path"])
        print(f"retained {SPEC.claim_id}: {receipt.receipt_hash}")
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        print(f"admitted {SPEC.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if SPEC.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": SPEC.claim_id, "execution_file": f"claims/{SPEC.claim_id}/execution.py"})
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), SPEC.claim_id, SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    package = ROOT / "claims" / SPEC.claim_id
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested_and_independently_replicated"
    write_json(package / "registration.json", registration)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    experiment_path = ROOT / "experiments" / "physics" / EMPIRICAL_SPEC.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {SPEC.claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n"
        "- Protocol: `observational-data-informed_target-inaccessible_sealed-prediction`\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`\n"
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        f"- Receipt path: `{rows[SPEC.claim_id]['receipt_path']}`\n",
        encoding="utf-8",
    )
    print(f"materialized {SPEC.claim_id}")


if __name__ == "__main__":
    main()
