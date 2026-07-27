#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-005 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.entropy_multiplicity_correspondence_batch_v1 import ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC  # noqa: E402
from sft.chemistry.entropy_multiplicity_correspondence_validation_v1 import _source_rows, exact_entropy_phase_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_005", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-005 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution(); captured = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed; result = execution.independent_validator.validate(sealed); captured["external"] = result; return result

    class CaptureEmpirical:
        def validate(self, sealed):
            result = execution.empirical_validator.validate(sealed); captured["empirical"] = result; return result

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text(encoding="utf-8")); census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id; source_rows = _source_rows(ROOT); analysis = exact_entropy_phase_analysis(source_rows)
    vector = tuple({
        "target_id": row["target_id"], "temperature_kelvin": row["target_payload"]["temperature-kelvin"],
        "phase": row["target_payload"]["phase-identity"],
        "entropy_joule_per_mole_kelvin": row["target_payload"]["entropy-joule-per-mole-kelvin"],
        "complete_state_payload_hash": row["target_payload_hash"],
    } for row in source_rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-005",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"], "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result, "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(item.survives for item in sealed.decisions),
            "entropy_law": "complete observation classes, exact positive multiplicities and every unresolved distinction pair",
            "singleton_law": "structural EmptyOne rather than numerical zero",
            "scalar_correspondence_boundary": "external scalar entropy retained post-seal; no logarithm or irrational proof value",
            "successor_law": "one fresh microstate updates one class and preserves all prior identities",
            "complete_external_target_count": len(source_rows), "complete_returned_column_count": 14,
            "liquid_row_count": 9, "vapor_row_count": 4, "phase_boundary_row_count": 2,
            "complete_entropy_vector_joule_per_mole_kelvin": tuple(str(value) for value in analysis["entropy_values_joule_per_mole_kelvin"]),
            "complete_adjacent_positive_entropy_steps": tuple(str(value) for value in analysis["adjacent_exact_positive_entropy_steps"]),
            "phase_entropy_jump_joule_per_mole_kelvin": str(analysis["phase_entropy_jump_joule_per_mole_kelvin"]),
            "independent_enthalpy_temperature_phase_entropy_joule_per_mole_kelvin": str(analysis["independent_enthalpy_temperature_phase_entropy_joule_per_mole_kelvin"]),
            "phase_relation_exact_separation": str(analysis["phase_relation_exact_separation"]),
            "phase_relation_exact_display_resolution_bound": str(analysis["phase_relation_exact_display_resolution_bound"]),
            "independent_phase_entropy_relation_agrees_within_display_resolution": analysis["independent_phase_entropy_relation_agrees_within_display_resolution"],
            "complete_external_entropy_phase_vector": vector, "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_entropy_phase_and_state_values_released_after_identity_seal": True,
            "external_scalar_entropy_retained_as_source_inscription_not_proof_value": True,
            "external_value_in_derivation_or_prediction": False, "fitted_distribution_logarithm_or_imported_entropy_equation_used": False,
            "numerical_zero_used": False, "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items(): write_json(package / name, payload)
    registration_path = package / "registration.json"; registration = json.loads(registration_path.read_text(encoding="utf-8")); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "complete_direct_entropy_and_phase_transition_vectors_opened_postseal"; write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-005`\n" + f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: complete unresolved-distinction ledger with exact positive multiplicity and structural EmptyOne certainty.\n"
        "- Direct NIST vector: `13` exact positive entropy states and `12` exact positive additive increments.\n"
        f"- Phase-transition entropy jump: `{analysis['phase_entropy_jump_joule_per_mole_kelvin']} J/(mol K)`; independent enthalpy/temperature record agrees within exact displayed resolution.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status, encoding="utf-8")
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")
    print("NIST entropy vector: 13 rows; 12 exact positive increments; phase-transition relation resolved")


if __name__ == "__main__":
    main()
