#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-016 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_diffusion_batch_v1 import MOLECULAR_DIFFUSION_SPEC  # noqa: E402
from sft.chemistry.molecular_diffusion_validation_v1 import _source_rows, exact_molecular_diffusion_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / MOLECULAR_DIFFUSION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_016", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-016 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = MOLECULAR_DIFFUSION_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-016-molecular-diffusion-v1/molecular-diffusion-primary-records-v1.json").read_text())
    analysis = exact_molecular_diffusion_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_id": row["source_id"],
        "diffusion_class": row["diffusion_class"], "dataset_ordinal": row["dataset_ordinal"],
        "source_point_ordinal": row["source_point_ordinal"],
        "component_orgnums": row["target_payload"]["component_orgnums"],
        "property_component_orgnum": row["target_payload"]["property_component_orgnum"],
        "solvent_orgnums": row["target_payload"]["solvent_orgnums"],
        "phase_metadata": row["target_payload"]["complete_phase_metadata"],
        "measurement_method": row["target_payload"]["measurement_method"],
        "diffusion_coefficient_source_declared_unit": row["target_payload"]["property_name"],
        "diffusion_coefficient_external_inscription": row["target_payload"]["diffusion_coefficient_m2_per_s_external_inscription"],
        "diffusion_uncertainty_external_record": row["target_payload"]["diffusion_uncertainty_external_record"],
        "variable_external_inscriptions": row["target_payload"]["variable_external_inscriptions"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-016",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash, "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "transition_law": "counted adjacent generated-cell redistribution with migrating identity and complete constituent conservation",
            "determinism_law": "all transitions and resources are exact counted support; observation uncertainty does not install a random premise",
            "diffusion_classes": ["binary", "self", "tracer"],
            "complete_external_target_count": 164, "complete_binary_target_count": 138,
            "complete_self_target_count": 4, "complete_tracer_target_count": 22,
            "complete_diffusion_dataset_count": 11, "complete_source_dataset_count": 30,
            "complete_source_point_count": 373, "structural_EmptyOne_condition_count": 26,
            "exact_external_diffusion_ranges_under_literal_source_declared_unit_labels": analysis["exact_diffusion_ranges_m2_per_s"],
            "exact_positive_condition_ranges": analysis["exact_positive_condition_ranges"],
            "complete_molecular_diffusion_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved, "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_and_prediction_seal": True,
            "literal_NIST_value_inscriptions_and_declared_unit_labels_preserved_without_post_hoc_scale_correction": True,
            "non_diffusion_companion_datasets_preserved_but_excluded_from_measurements": True,
            "Fick_Brownian_random_walk_Stokes_Einstein_activation_transport_fit_logarithm_continuum_interpolation_regression_selection_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text()); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text()); experiment["status"] = "complete_138_binary_4_self_22_tracer_vector_opened_postseal"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-016`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: deterministic counted adjacent-cell redistribution with held molecular identity, complete constituent conservation and exact time/space support.\n"
        "- Complete NIST surface: `138` binary, `4` self and `22` tracer diffusion records; all `30` source datasets and `373` points preserved.\n"
        "- Source boundary: literal NIST value inscriptions and unit labels retained without invented scale correction.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete diffusion: 138 binary; 4 self; 22 tracer; 164 total")


if __name__ == "__main__":
    main()
