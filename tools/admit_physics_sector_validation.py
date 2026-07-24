#!/usr/bin/env python3
"""Admit and materialize the post-seal PDG sector-anchor validation."""

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
from sft.physics.sector_inventory_validation_v1 import SPEC  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    path = ROOT / "claims" / SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_sector_validation", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load sector validation execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    captured = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class CaptureEmpirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if SPEC.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": SPEC.claim_id, "execution_file": f"claims/{SPEC.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    row = next(item for item in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if item["claim_id"] == SPEC.claim_id)
    package = ROOT / "claims" / SPEC.claim_id
    payloads = {
        "candidate_census.json": {"claim_id": SPEC.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": SPEC.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": SPEC.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": SPEC.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": SPEC.claim_id,
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
            "exact_result": SPEC.exact_result,
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
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/physics" / SPEC.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {SPEC.claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Measurement: known sector anchors pass; new sectors remain unmeasured predictions\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Blind external measurement: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {SPEC.claim_id}: {receipt.receipt_hash}")


if __name__ == "__main__":
    main()
