"""Admit and materialize the formal source-boundary growth method."""

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
from sft.physics.source_boundary_growth import CLAIM_ID, SPEC  # noqa: E402


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    module_spec = importlib.util.spec_from_file_location("sft_boundary_growth_execution", path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("cannot load boundary-growth execution")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    execution = load_execution()
    repository = EngineRepository(ROOT)
    receipt = repository.execute_official(
        execution.program,
        execution.independent_validator,
        execution.source_files,
    )

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"}
        )
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), CLAIM_ID, SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "independently_replicated"
    write_json(package / "registration.json", registration)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text(
        f"# {CLAIM_ID}\n\nStatus: `independently_replicated`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        "- Empirical status: formal measurement discriminator; physical result not yet opened\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
