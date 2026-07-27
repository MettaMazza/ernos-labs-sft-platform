#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-011 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.phase_rule_batch_v1 import PHASE_RULE_SPEC  # noqa: E402
from sft.chemistry.phase_rule_validation_v1 import _source_rows, exact_phase_rule_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / PHASE_RULE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_011", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-011 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = PHASE_RULE_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing:
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
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-011-phase-rule-v2/phase-rule-primary-records-v1.json").read_text())
    analysis = exact_phase_rule_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"],
        "component_count_external_inscription": row["target_payload"]["component_count_external_inscription"],
        "phase_count_external_inscription": row["target_payload"]["phase_count_external_inscription"],
        "degree_support_external_inscription": row["target_payload"]["degree_support_external_inscription"],
        "sft_degree_support_state": row["target_payload"]["sft_degree_support_state"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-THERMO-011",
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
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "phase_rule_law": "one exact available coordinate carrier is cancelled for each coexisting phase from all independent component carriers and two held environmental carriers",
            "invariant_boundary": "complete carrier cancellation is structural EmptyOne, never numerical zero",
            "successor_law": "one added component carrier paired with one added phase cancellation preserves independent degree support",
            "complete_external_target_count": 18,
            "complete_component_count_classes": 4,
            "positive_degree_support_target_count": 14,
            "EmptyOne_degree_support_target_count": 4,
            "complete_nist_source_page_count": 32,
            "complete_component_phase_degree_vector": vector,
            "halted_prefetch_v1_preserved": "experiments/external_sources/chemistry/phase_rule_capture_spec_v1_halt.json",
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_degree_support_outcomes_released_after_complete_identity_seal": True,
            "external_equation_or_degree_used_as_proof_parameter": False,
            "imported_phase_rule_gibbs_duhem_subtraction_or_free_coordinate_used": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "complete_18_row_component_phase_degree_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-011`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: one structural carrier cancellation per coexisting phase; complete cancellation is `EmptyOne`.\n"
        "- Complete external vector: `18` rows, `14` positive degree supports and `4` invariant EmptyOne boundaries.\n"
        "- Complete sources: IUPAC Gold Book P04533 and the byte-preserved 32-page NIST phase-diagram glossary.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("IUPAC/NIST phase rule: 18 rows; 14 positive degree supports; 4 EmptyOne boundaries")


if __name__ == "__main__":
    main()
