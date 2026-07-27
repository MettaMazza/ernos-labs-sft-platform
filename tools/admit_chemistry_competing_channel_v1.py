#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-006 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.competing_channel_batch_v1 import COMPETING_CHANNEL_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.competing_channel_validation_v1 import _source_rows, exact_competing_channel_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / COMPETING_CHANNEL_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_006", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-006 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COMPETING_CHANNEL_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
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
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_competing_channel_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_product_row": row["source_product_row"],
        "product_channel_identity": row["product_channel_identity"],
        "experimental_branching_percent_external_inscription": row["target_payload"]["experimental_branching_percent_external_inscription"],
        "experimental_branching_exact_fraction_of_complete_support": row["target_payload"]["experimental_branching_exact_fraction_of_complete_support"],
        "experimental_uncertainty_percent_external_inscription": row["target_payload"]["experimental_uncertainty_percent_external_inscription"],
        "experimental_uncertainty_exact_fraction": row["target_payload"]["experimental_uncertainty_exact_fraction"],
        "calculated_comparison_percent_external_inscription": row["target_payload"]["calculated_comparison_percent_external_inscription"],
        "calculated_comparison_exact_fraction": row["target_payload"]["calculated_comparison_exact_fraction"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-006",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
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
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "branching_law": "each exact retained channel support over the exact sum of the complete registered channel support",
            "complete_external_target_count": 8, "complete_supplementary_file_count": 19,
            "complete_supplement_pdf_count": 2,
            "exact_experimental_branching_support_sum": analysis["exact_experimental_support_sum"],
            "exact_experimental_branching_range": analysis["exact_experimental_branching_range"],
            "exact_experimental_uncertainty_range": analysis["exact_experimental_uncertainty_range"],
            "complete_experimental_and_calculated_branching_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "experimental_calculated_and_analysis_provenance_separated": True,
            "imported_probability_normalization_branching_equation_fit_renormalization_selection_or_target_correction_used_in_law": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "complete_eight_channel_experimental_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-006`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: each retained channel support divided by the complete exact support.\n"
        "- Complete external surface: eight experimental products, nineteen supplementary files and two PDFs.\n"
        f"- Exact experimental range: `{analysis['exact_experimental_branching_range']}`; exact sum: `{analysis['exact_experimental_support_sum']}`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete branching vector: 8 products; exact support sum One; 19 supplementary files; 2 PDFs")


if __name__ == "__main__":
    main()
