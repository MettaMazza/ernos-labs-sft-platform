"""Admit the clean V3 atomic-constant prerequisite chain in dependency order."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.physics.atomic_constants import ATOMIC_CONSTANT_SPECS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_atomic_constant_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT)
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"]: row for row in census["claims"]}
    receipts = {}
    for index, spec in enumerate(ATOMIC_CONSTANT_SPECS, 1):
        if spec.claim_id in admitted:
            receipt = read_receipt(ROOT / admitted[spec.claim_id]["receipt_path"])
            print(f"[{index}/{len(ATOMIC_CONSTANT_SPECS)}] retained {spec.claim_id}: {receipt.receipt_hash}")
        else:
            execution = load_execution(spec.claim_id)
            receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files)
            print(f"[{index}/{len(ATOMIC_CONSTANT_SPECS)}] admitted {spec.claim_id}: {receipt.receipt_hash}")
        receipts[spec.claim_id] = receipt

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
    for spec in ATOMIC_CONSTANT_SPECS:
        if spec.claim_id not in known:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    for index, spec in enumerate(ATOMIC_CONSTANT_SPECS, 1):
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
            "- Empirical status: formal result sealed; post-seal external validation is separate\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{receipt.receipt_hash}`\n",
            encoding="utf-8",
        )
        print(f"[{index}/{len(ATOMIC_CONSTANT_SPECS)}] materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
