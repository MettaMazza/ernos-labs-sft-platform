"""Execute, admit and materialize one empirical Physics group."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.physics.group_registry import GROUPS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_physics_group_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=tuple(GROUPS))
    args = parser.parse_args()
    _, _, specs = GROUPS[args.group]
    repository = EngineRepository(ROOT)
    captured_by_claim = {}
    for index, spec in enumerate(specs, 1):
        execution = load_execution(spec.claim_id)
        captured = {}

        class CaptureIndependent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["external"] = result
                return result

        class CaptureEmpirical:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed)
                captured["empirical"] = result
                return result

        receipt = repository.execute_official(
            execution.program,
            CaptureIndependent(),
            execution.source_files,
            CaptureEmpirical(),
        )
        captured_by_claim[spec.claim_id] = (execution, receipt, captured)
        print(f"[{index}/{len(specs)}] admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["claim_id"] for row in manifest["claims"]}
    for spec in specs:
        if spec.claim_id not in known:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in census["claims"]}
    for index, spec in enumerate(specs, 1):
        execution, receipt, captured = captured_by_claim[spec.claim_id]
        sealed = captured["sealed"]
        external = captured["external"]
        empirical = captured["empirical"]
        package = ROOT / "claims" / spec.claim_id
        row = rows[spec.claim_id]
        payloads = {
            "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
            "elimination_receipt.json": {
                "claim_id": spec.claim_id,
                "decisions": asdict(sealed)["decisions"],
                "closure": asdict(sealed.closure),
            },
            "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
            "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
            "certificate.json": {
                "claim_id": spec.claim_id,
                "status": "empirically_tested_and_independently_replicated",
                "source_manifest_hash": execution.program.registration.source_hash,
                "independent_implementation_hash": external.implementation_hash,
                "independent_certificate_hash": external.certificate_hash,
                "derivation_seal_hash": sealed.seal_hash,
                "external_validation_hash": receipt.external_validation_hash,
                "empirical_validation_hash": receipt.empirical_validation_hash,
                "measurement_receipt_hash": empirical.measurement_receipt_hash,
                "engine_receipt_hash": receipt.receipt_hash,
                "engine_receipt_path": row["receipt_path"],
                "exact_result": spec.exact_result,
                "closure_scope": receipt.closure_status,
                "controls_passed": all(item.passed for item in sealed.controls),
                "independently_recomputed": external.passed,
                "all_measurement_rows_preserved": empirical.all_rows_preserved,
                "external_data_source_ids": list(empirical.data_source_ids),
                "falsification_condition": empirical.falsification_condition,
            },
        }
        for name, payload in payloads.items():
            write_json(package / name, payload)
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(package / "registration.json", registration)
        experiment_path = ROOT / "experiments/physics" / spec.experiment_id / "registration.json"
        experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "measured"; write_json(experiment_path, experiment)
        certificate = payloads["certificate.json"]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- Independent validation: `{certificate['external_validation_hash']}`\n- Blind external measurement: `{certificate['empirical_validation_hash']}`\n"
            f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`\n- Engine receipt: `{row['receipt_hash']}`\n"
            f"- External source IDs: {', '.join(certificate['external_data_source_ids'])}\n", encoding="utf-8")
        print(f"[{index}/{len(specs)}] materialized from admission trace: {len(sealed.census.candidates)} candidates; {len(empirical.measurements)} measurement rows")
    from tools.freeze_physics_inventory import main as refresh_physics_inventory
    refresh_physics_inventory()


if __name__ == "__main__":
    main()
