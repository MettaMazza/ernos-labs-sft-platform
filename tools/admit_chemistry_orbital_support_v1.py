#!/usr/bin/env python3
"""Officially execute and materialize ELEC-003."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.orbital_support_batch_v1 import ORBITAL_SUPPORT_SPEC  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / ORBITAL_SUPPORT_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_orbital_support_003", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load ELEC-003 execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = ORBITAL_SUPPORT_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        raise SystemExit(f"claim already admitted; immutable receipt preserved: {spec.claim_id}")
    execution = load_execution()
    captured: dict[str, object] = {}

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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; receipt preserved: {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    artifacts = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-ELEC-003",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result,
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "external_state_rows": 360,
            "external_term_assignments": 362,
            "external_configuration_assignments": 87,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "exact_state_energy_order_claimed": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in artifacts.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `SFT-CHEM-OBL-ELEC-003`\n- Closure: `{receipt.closure_status}`\n- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Measurement receipt: `{empirical.measurement_receipt_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
        "- External vector: 360 NIST state rows, 362 term assignments and 87 configuration assignments; all retained.\n"
        "- Scope: support composition and occupancy; exact ground/excited state ordering is ELEC-004.\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(row.survives for row in sealed.decisions)}")
    print(f"empirical measurements: {len(empirical.measurements)}; passed: {empirical.passed}")


if __name__ == "__main__":
    main()
