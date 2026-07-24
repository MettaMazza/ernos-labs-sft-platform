#!/usr/bin/env python3
"""Admit and materialize the jointly empirical spatial-flatness law."""

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
from sft.physics.spatial_flatness_law import SPATIAL_FLATNESS_CLAIM_ID, SPATIAL_FLATNESS_SPEC


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SPATIAL_FLATNESS_CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_spatial_flatness_execution", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load spatial-flatness execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        execution.independent_validator,
        execution.source_files,
        execution.empirical_validator,
    )
    if not receipt.model_admitted:
        raise RuntimeError("spatial-flatness law was not admitted")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if SPATIAL_FLATNESS_CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({
            "claim_id": SPATIAL_FLATNESS_CLAIM_ID,
            "execution_file": f"claims/{SPATIAL_FLATNESS_CLAIM_ID}/execution.py",
        })
        write_json(manifest_path, manifest)
    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), SPATIAL_FLATNESS_CLAIM_ID, SPATIAL_FLATNESS_SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    package = ROOT / "claims" / SPATIAL_FLATNESS_CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(package / "registration.json", registration)
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == SPATIAL_FLATNESS_CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text(
        f"# {SPATIAL_FLATNESS_CLAIM_ID}\n\nStatus: `independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        "- Provenance: `observational_derivation` with executable independence from V1 answer artifacts\n"
        "- Exact result: complete positive partitions leave the empty One curvature remainder\n"
        "- Empirical status: the absence result is inside the complete Planck equation 47b interval\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n",
        encoding="utf-8",
    )
    print(f"admitted {SPATIAL_FLATNESS_CLAIM_ID}: {receipt.receipt_hash}")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
