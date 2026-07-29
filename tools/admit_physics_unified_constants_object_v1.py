#!/usr/bin/env python3
"""Admit the Unified Constants Object through the untouched engine."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    checks = (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    )
    for tool, expected in checks:
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools" / tool), "--json"),
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if completed.returncode:
            raise SystemExit(completed.stdout + completed.stderr + "\nUnified Constants Object admission halted")
        if json.loads(completed.stdout).get("status") != expected:
            raise SystemExit(completed.stdout + "\nUnified Constants Object admission halted")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_physics_unified_constants_object_077", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Unified Constants Object execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    verify_seals()
    from sft.engine import EngineRepository
    from sft.physics.unified_constants_object_law_v1 import CLAIM_ID, SPEC

    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"]: row for row in census["claims"]}
    missing = tuple(claim_id for claim_id in SPEC.dependencies if claim_id not in existing)
    if missing:
        raise SystemExit("Unified Constants Object dependencies are not admitted: " + ", ".join(missing))
    if CLAIM_ID in existing:
        raise SystemExit("Unified Constants Object already has an admitted receipt")

    execution = load_execution(CLAIM_ID)
    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        execution.independent_validator,
        execution.source_files,
    )
    if not receipt.model_admitted:
        raise RuntimeError("Unified Constants Object did not enter the model")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["claims"].append({
        "claim_id": CLAIM_ID,
        "execution_file": f"claims/{CLAIM_ID}/execution.py",
    })
    write_json(manifest_path, manifest)

    materialized = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), CLAIM_ID, SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if materialized.returncode:
        raise RuntimeError(materialized.stdout + materialized.stderr)

    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    registration["statement"] = SPEC.exact_result
    write_json(package / "registration.json", registration)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}",
        "",
        "Status: `independently_replicated`",
        "",
        "- This is the separate V3 constants-as-one-object derivation; Grand Lock 075/076 remains unchanged.",
        "- Every registered sector is reachable from the foundational One through shared typed carriers.",
        "- The complete foundation-order and V3 terminal vectors cross-lock exactly.",
        "- The generator-successor probe moves every generator-dependent carrier.",
        "- Binary-only half-One and independently held spatial and boundary ranks remain fixed.",
        "- External measurements select no form; measured-value reconciliation is a separate successor obligation.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Engine receipt: `{row['receipt_hash']}`",
        "",
    )), encoding="utf-8")
    verify_seals()
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    print(materialized.stdout.strip())


if __name__ == "__main__":
    main()
