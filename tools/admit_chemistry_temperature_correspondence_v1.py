#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-002 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.temperature_correspondence_batch_v1 import TEMPERATURE_CORRESPONDENCE_SPEC  # noqa: E402
from sft.chemistry.temperature_correspondence_validation_v1 import _source_rows, exact_temperature_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / TEMPERATURE_CORRESPONDENCE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_002", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-002 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = TEMPERATURE_CORRESPONDENCE_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
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
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    source_rows = _source_rows(ROOT)
    analysis = exact_temperature_analysis(source_rows)
    external_value_vector = tuple({
        "target_id": row["target_id"], "source_class": row["source_class"],
        "source_id": row["source_id"], "chemical_composition_identity": row["chemical_composition_identity"],
        "phase_identity": row["phase_identity"], "postseal_target": row["target_payload"],
        "postseal_target_hash": row["target_payload_hash"],
    } for row in source_rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-002",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "physics_temperature_carrier_law": "Chemistry consumes the admitted Physics temperature carrier unchanged",
            "chemical_ownership_law": "composition, phase, equilibrium reference and chemical-state consequence remain held",
            "equilibrium_law": "distinct compositions and thermometric routes share one exact common carrier",
            "composition_successor_law": "new composition consequences preserve the common carrier without rescaling",
            "exact_si_common_carrier_scaled_numerator": analysis["exact_common_carrier_scaled_numerator"],
            "common_scale_denominator": analysis["common_scale_denominator"],
            "exact_si_common_carrier": "13806490/10^30 joule per kelvin",
            "acoustic_argon_interval": "[13806456,13806512]/10^30 joule per kelvin",
            "Johnson_noise_interval": "[13806340,13806680]/10^30 joule per kelvin",
            "acoustic_contains_exact_common_carrier": analysis["acoustic_contains_exact_common_carrier"],
            "electronic_contains_exact_common_carrier": analysis["electronic_contains_exact_common_carrier"],
            "argon_gas_TPW_context_retained": analysis["argon_gas_TPW_context_retained"],
            "kinetic_temperature_relation_retained": analysis["kinetic_temperature_relation_retained"],
            "Johnson_temperature_response_retained": analysis["Johnson_temperature_response_retained"],
            "complete_external_target_count": len(source_rows),
            "complete_physically_distinct_thermometry_route_count": 2,
            "external_value_vector": external_value_vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_uncertainties_intervals_and_relation_flags_released_after_identity_seal": True,
            "external_value_in_derivation_or_prediction": False,
            "chemical_rescaling_calibration_fit_or_composition_parameter_used": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "complete_exact_common_carrier_and_two_route_value_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-002`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: Chemistry consumes one unchanged Physics temperature carrier and owns held composition consequences.\n"
        "- Exact SI carrier: `13806490/10^30 J/K`.\n"
        "- Acoustic argon interval: `[13806456,13806512]/10^30 J/K`; contains exact carrier.\n"
        "- Johnson-noise interval: `[13806340,13806680]/10^30 J/K`; contains exact carrier.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print("exact carrier: 13806490/10^30 J/K; both complete measured intervals contain it")


if __name__ == "__main__":
    main()
