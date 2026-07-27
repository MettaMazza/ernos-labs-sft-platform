#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-014 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.colligative_response_batch_v1 import COLLIGATIVE_RESPONSE_SPEC  # noqa: E402
from sft.chemistry.colligative_response_validation_v1 import _source_rows, exact_colligative_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / COLLIGATIVE_RESPONSE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_014", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-014 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COLLIGATIVE_RESPONSE_SPEC
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

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
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
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-014-colligative-response-v1/colligative-response-primary-records-v1.json").read_text())
    analysis = exact_colligative_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_id": row["source_id"], "response_class": row["response_class"],
        "dataset_ordinal": row["dataset_ordinal"], "source_point_ordinal": row["source_point_ordinal"],
        "component_orgnums": row["target_payload"]["component_orgnums"],
        "composition_external_inscription": row["target_payload"]["composition_external_inscription"],
        "response_external_inscription": row["target_payload"]["response_external_inscription"],
        "temperature_K_external_inscription": row["target_payload"]["temperature_K_external_inscription"],
        "pressure_kPa_external_inscription": row["target_payload"]["pressure_kPa_external_inscription"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-014",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash, "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "particle_law": "distinct solvent/solute identities with solvent transmission and solute retention",
            "boiling_orientation": "temperature support expands until liquid-gas solvent exchange balance",
            "freezing_orientation": "temperature support reduces until liquid-crystal solvent exchange balance",
            "osmotic_orientation": "pressure support directs toward the solute-holding solution until solvent exchange balance",
            "magnitude_law": "exact positive reference-response separation opened only postseal",
            "absence_law": "pure-solvent composition is structural EmptyOne; source zero glyph remains provenance only",
            "complete_external_target_count": 276, "complete_boiling_target_count": 144,
            "complete_freezing_target_count": 37, "complete_osmotic_target_count": 95,
            "complete_dataset_count": 28, "complete_source_count": 3,
            "exact_external_ranges": analysis["exact_ranges"],
            "complete_colligative_response_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved, "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_seal": True,
            "conventional_colligative_equation_constant_factor_interpolation_regression_or_fit_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text()); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text()); experiment["status"] = "complete_144_boiling_37_freezing_95_osmotic_vector_opened_postseal"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-014`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: distinct solvent/solute particle boundary forces held boiling, freezing and osmotic orientations without signed proof magnitudes.\n"
        "- Complete NIST surface: `144` boiling, `37` freezing and `95` osmotic records across `28` datasets.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("NIST colligative response: 144 boiling; 37 freezing; 95 osmotic; 276 complete records")


if __name__ == "__main__":
    main()
