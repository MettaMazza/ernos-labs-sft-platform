"""Execute and admit the nine empirical measurement/metrology laws."""

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
from sft.physics.measurement_laws import MEASUREMENT_SPECS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_physics_measurement_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT)
    for index, spec in enumerate(MEASUREMENT_SPECS, 1):
        execution = load_execution(spec.claim_id)
        receipt = repository.execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        print(f"[{index}/{len(MEASUREMENT_SPECS)}] admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
    for spec in MEASUREMENT_SPECS:
        if spec.claim_id not in known:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in census["claims"]}
    for index, spec in enumerate(MEASUREMENT_SPECS, 1):
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), spec.claim_id, spec.exact_result),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stdout + completed.stderr)
        package = ROOT / "claims" / spec.claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        registration["status"] = "empirically_tested"
        write_json(package / "registration.json", registration)
        experiment_path = ROOT / "experiments/physics" / spec.experiment_id / "registration.json"
        experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
        experiment["status"] = "measured"
        write_json(experiment_path, experiment)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        row = rows[spec.claim_id]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Blind external measurement: `{certificate['empirical_validation_hash']}`\n"
            f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n"
            f"- External body: Bureau International des Poids et Mesures\n",
            encoding="utf-8",
        )
        print(f"[{index}/{len(MEASUREMENT_SPECS)}] {completed.stdout.strip()}")

    subprocess.run((sys.executable, str(ROOT / "tools/freeze_physics_inventory.py")), cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
