#!/usr/bin/env python3
"""Admit and materialize post-seal gravity/spacetime validations."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.physics.gravity_spacetime_validation_v1 import VALIDATION_SPECS  # noqa: E402


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_gravity_validation_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT); captured_by_claim = {}
    for spec in VALIDATION_SPECS:
        execution = load_execution(spec.claim_id); captured = {}

        class CaptureIndependent:
            def validate(self, sealed):
                captured["sealed"] = sealed; result = execution.independent_validator.validate(sealed); captured["external"] = result; return result

        class CaptureEmpirical:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed); captured["empirical"] = result; return result

        receipt = repository.execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
        captured_by_claim[spec.claim_id] = (execution, receipt, captured)
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8")); known = {row["claim_id"] for row in manifest["claims"]}
    for spec in VALIDATION_SPECS:
        if spec.claim_id not in known: manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    rows = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
    for spec in VALIDATION_SPECS:
        execution, receipt, captured = captured_by_claim[spec.claim_id]; sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
        package = ROOT / "claims" / spec.claim_id; row = rows[spec.claim_id]
        payloads = {
            "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
            "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
            "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
            "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
            "certificate.json": {
                "claim_id": spec.claim_id, "status": "empirically_tested_and_independently_replicated",
                "source_manifest_hash": execution.program.registration.source_hash,
                "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
                "derivation_seal_hash": sealed.seal_hash, "external_validation_hash": receipt.external_validation_hash,
                "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash,
                "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": row["receipt_path"], "exact_result": spec.exact_result,
                "closure_scope": receipt.closure_status, "controls_passed": all(item.passed for item in sealed.controls),
                "independently_recomputed": external.passed, "all_measurement_rows_preserved": empirical.all_rows_preserved,
                "external_data_source_ids": list(empirical.data_source_ids), "falsification_condition": empirical.falsification_condition,
            },
        }
        for name, payload in payloads.items(): write_json(package / name, payload)
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(package / "registration.json", registration)
        experiment_path = ROOT / "experiments/physics" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "measured"; write_json(experiment_path, experiment)
        certificate = payloads["certificate.json"]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n- Closure: `{certificate['closure_scope']}`\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n- Independent validation: `{certificate['external_validation_hash']}`\n"
            f"- Blind external measurement: `{certificate['empirical_validation_hash']}`\n- Measurement receipt: `{certificate['measurement_receipt_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n- External source IDs: {', '.join(certificate['external_data_source_ids'])}\n", encoding="utf-8")
        print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
