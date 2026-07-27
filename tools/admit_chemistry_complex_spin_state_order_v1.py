#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-007 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.complex_spin_state_order_batch_v1 import (  # noqa: E402
    COMPLEX_SPIN_STATE_ORDER_SPEC, PRIMARY_PATH,
)
from sft.chemistry.complex_spin_state_order_validation_v1 import _source_rows, exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / COMPLEX_SPIN_STATE_ORDER_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_007", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load INORG-007 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COMPLEX_SPIN_STATE_ORDER_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
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

    receipt = EngineRepository(ROOT).execute_official(
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
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
    primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    analysis = exact_analysis(rows, primary)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-INORG-007",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
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
            "complete_six_electron_signature_count": analysis["signature_count"],
            "forced_low_signature": analysis["low_signature"],
            "forced_low_spin_width": analysis["low_spin_width"],
            "forced_low_split_crossings": analysis["low_crossings"],
            "forced_high_signature": analysis["high_signature"],
            "forced_high_spin_width": analysis["high_spin_width"],
            "forced_high_split_crossings": analysis["high_crossings"],
            "exact_order_vector": analysis["order_vector"],
            "exact_cost_vector": analysis["cost_vector"],
            "complete_registered_external_surface_count": 3,
            "external_exact_distance_vector_pm": analysis["external_distance_vector_pm"],
            "external_exact_temperature_vector_k": analysis["external_temperature_vector_k"],
            "external_exact_term_vector": analysis["external_term_vector"],
            "external_state_vector": analysis["external_state_vector"],
            "external_dilution_direction_match": analysis["external_dilution_direction_match"],
            "registered_transport_mismatch_preserved": analysis["transport_mismatch_preserved"],
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_or_free_parameter_used": False,
            "imported_orbital_field_pairing_spectrochemical_model_used": False,
            "dimensional_distance_temperature_or_term_fitted_or_derived": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)

    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-INORG-007`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Complete six-electron quotient census: `10` signatures.\n"
        "- Forced low state: three lower pairs, spin width `1`, crossing `EmptyOne`.\n"
        "- Forced high state: one lower pair, two lower singles, two upper singles, spin width `5`, crossings `2`.\n"
        "- Exact order: high-before-low, crossover coincidence, low-before-high.\n"
        "- External vector: `1016/5 pm, 115 K, 1A1, low-spin` to `2199/10 pm, 227 K, 5T2, high-spin`; registered transport mismatch preserved.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete external vector: 3 rows; exact crossover values and transport mismatch preserved")


if __name__ == "__main__":
    main()
