"""Execute, admit and materialize the complete registered mathematics branch."""

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
from sft.mathematics.catalog import SPECS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location(
        "sft_mathematics_admission_" + claim_id.replace("-", "_"), path
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load execution for {claim_id}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT)
    receipts = {}
    for spec in SPECS:
        execution = load_execution(spec.claim_id)
        receipt = repository.execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        receipts[spec.claim_id] = receipt
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census" / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing = {item["claim_id"] for item in manifest["claims"]}
    for spec in SPECS:
        if spec.claim_id not in existing:
            manifest["claims"].append({
                "claim_id": spec.claim_id,
                "execution_file": f"claims/{spec.claim_id}/execution.py",
            })
    write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census" / "claims.json").read_text(encoding="utf-8"))
    census_rows = {row["claim_id"]: row for row in census["claims"]}
    for spec in SPECS:
        completed = subprocess.run(
            (
                sys.executable,
                str(ROOT / "tools" / "materialize_claim_evidence.py"),
                spec.claim_id,
                spec.exact_result,
            ),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout + completed.stderr)
        package = ROOT / "claims" / spec.claim_id
        registration_path = package / "registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        registration["status"] = "independently_replicated"
        write_json(registration_path, registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        row = census_rows[spec.claim_id]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\n"
            "Status: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: not applicable to this formal theorem\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- External validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n"
            f"- Receipt path: `{row['receipt_path']}`\n",
            encoding="utf-8",
        )
        print(completed.stdout.strip())


if __name__ == "__main__":
    main()
