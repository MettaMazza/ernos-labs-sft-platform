"""Execute, admit and materialize the frozen classical-computation branch."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.computation.catalog import SPECS  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("sft_computation_admission_" + claim_id.replace("-", "_"), path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load execution for {claim_id}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT)
    for index, spec in enumerate(SPECS, 1):
        execution = load_execution(spec.claim_id)
        receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files)
        print(f"[{index}/{len(SPECS)}] admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing = {item["claim_id"] for item in manifest["claims"]}
    for spec in SPECS:
        if spec.claim_id not in existing:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census" / "claims.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in census["claims"]}
    for index, spec in enumerate(SPECS, 1):
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools" / "materialize_claim_evidence.py"), spec.claim_id, spec.exact_result),
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
        row = rows[spec.claim_id]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Sub-branch: `{spec.group}`\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: not applicable to this formal theorem\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- External validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n"
            f"- Receipt path: `{row['receipt_path']}`\n",
            encoding="utf-8",
        )
        print(f"[{index}/{len(SPECS)}] {completed.stdout.strip()}")


if __name__ == "__main__":
    main()
