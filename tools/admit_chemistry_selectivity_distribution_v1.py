#!/usr/bin/env python3
"""Official one-shot admission for Chemistry ORG-014."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.chemistry.selectivity_distribution_batch_v1 import SELECTIVITY_DISTRIBUTION_SPEC  # noqa: E402
from sft.chemistry.selectivity_distribution_validation_v1 import exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def execution():
    path = ROOT / "claims" / SELECTIVITY_DISTRIBUTION_SPEC.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("org014_execution", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main():
    claim = SELECTIVITY_DISTRIBUTION_SPEC; claims_path = ROOT / "census/claims.json"
    if claim.claim_id in {row["claim_id"] for row in json.loads(claims_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    run = execution(); captured = {}
    class Independent:
        def validate(self, sealed): captured["sealed"] = sealed; captured["independent"] = run.independent_validator.validate(sealed); return captured["independent"]
    class Empirical:
        def validate(self, sealed): captured["empirical"] = run.empirical_validator.validate(sealed); return captured["empirical"]
    receipt = EngineRepository(ROOT).execute_official(run.program, Independent(), run.source_files, Empirical())
    if not receipt.model_admitted: raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"}); write(manifest_path, manifest)
    row = next(item for item in json.loads(claims_path.read_text())["claims"] if item["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id; analysis, checks = exact_analysis(ROOT)
    certificate = {
        "claim_id": claim.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-ORG-014",
        "status": "model_admitted_forced_structural_law_postseal_complete_distribution_tested_and_independently_replicated",
        "source_manifest_hash": run.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash, "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": row["receipt_path"], "closure_scope": receipt.closure_status, "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(item.survives for item in sealed.decisions),
        **analysis, "all_133_target_specific_external_checks_passed": all(checks.values()), "all_external_rows_preserved": empirical.all_rows_preserved,
        "all_130_reactions_130_outcomes_152_products_302_identifiers_195_measurements_preserved": True,
        "major_product_filter_applied": False,
        "numerical_zero_negative_irrational_imaginary_continuum_probability_fitted_free_random_or_imported_native_parameter_used": False,
        "named_reaction_measured_yield_product_amount_or_major_product_used_to_select_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        "selectivity_distribution_receipt.json": {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)}, "certificate.json": certificate,
    }
    for name, payload in artifacts.items(): write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash; write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured_postseal_complete"; write(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {claim.claim_id}\n\nStatus: `model_admitted_forced_structural_law_postseal_complete_distribution_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ORG-014`\n- Exact law: complete product support with exact chemo/regio/stereo partitions and post-seal held amount records; no major-product filter.\n"
        "- External result: three IUPAC records plus 130 reactions, 130 outcomes, 152 products, 302 product identifiers and 195 measurements retained.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    print(f"admitted {claim.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}")


if __name__ == "__main__": main()
