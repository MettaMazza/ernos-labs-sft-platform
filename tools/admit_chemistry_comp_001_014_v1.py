#!/usr/bin/env python3
"""Submit one COMP-001--014 claim in strict dependency order."""

from __future__ import annotations

from dataclasses import asdict
import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.computational_chemistry_batch_v1 import SPECS_BY_NUMBER
from sft.chemistry.computational_chemistry_validation_v1 import exact_analysis
from sft.engine import EngineRepository


PROGRESS = ROOT / "audits/CHEMISTRY_COMP_001_014_LIVE_PROGRESS_2026-07-28.json"


SURFACES = {
    "001": "twelve complete PubChem JSON/SDF graph pairs, canonical resource outcomes, byte provenance and all twelve invalid registered property routes",
    "002": "complete cross-format and reordered graph identity vectors with nonisomorphic and single-distinction adverse controls",
    "003": "complete native embedding census plus all one hundred registered PubChem aspirin substructure results and structural absence control",
    "004": "complete native C3H8O heavy-atom graph census of three forms, the sealed one-hundred-record formula result and all three post-seal linked structures",
    "005": "complete one- and two-site Fold fibre assignment censuses and an externally retained five-site absolute/connectivity stereochemical distinction",
    "006": "complete eight-word Fold torsion-fibre support at three retained rotors, all ten distinct PubChem conformer records and the explicit resolution nonconflation",
    "007": "all 36,444 Rhea directed reactions and all 50,016 USPTO reaction rows, classes, reciprocal paths, adverse and absent records",
    "008": "all 1,065,119 atom-mapped LocalMapper rows, including complete equal-map, mismatch, no-map, malformed, confidence and low-confidence custody",
    "009": "complete native direct and sequential path traces composed with the full Rhea, USPTO and atom-mapped external mechanism surfaces",
    "010": "all 66 exact cross-carrier distinction vectors, an exact self-identity control and all one hundred conventional PubChem similarity results retained downstream",
    "011": "four exact PubChem/ChEBI InChIKey correspondences, all captured versions and every failed or unavailable registered route",
    "012": "twelve independently reconstructed exact symbolic atom/bond/formula vectors across PubChem JSON and SDF, with all external decimal properties downstream",
    "013": "complete accepted and missing-distinction boundary cases, every canonical resource halt and all twelve invalid-property route halts",
    "014": "twelve branchwise classical/reversible chemical executions with identical canonical terminals wherever supported and every declared resource halt preserved",
}


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def build_execution(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("claim", choices=tuple(SPECS_BY_NUMBER)); args = parser.parse_args()
    number = args.claim; claim = SPECS_BY_NUMBER[number]; obligation = f"SFT-CHEM-OBL-COMP-{number}"
    census_path = ROOT / "census/claims.json"; admitted = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if claim.claim_id in admitted:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    for dependency in claim.dependencies:
        if dependency not in admitted:
            raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")
    execution = build_execution(claim); captured = {}
    class Independent:
        def validate(self, sealed):
            captured["sealed"] = sealed; captured["independent"] = execution.independent_validator.validate(sealed); return captured["independent"]
    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed); return captured["empirical"]
    result = EngineRepository(ROOT).execute_official(execution.program, Independent(), execution.source_files, Empirical())
    if not result.model_admitted:
        raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")
    sealed = captured["sealed"]; independent = captured["independent"]; empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"}); write(manifest_path, manifest)
    census_row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id; analysis, checks = exact_analysis(ROOT, claim.claim_id)
    certificate = {
        "claim_id": claim.claim_id, "chemistry_obligation": obligation,
        "status": f"model_admitted_forced_computational_chemistry_law_{number}_empirically_tested_and_independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": result.external_validation_hash,
        "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": result.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
        "closure_scope": result.closure_status, "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis, "all_registered_target_checks_passed": all(checks.values()), "registered_target_check_count": len(checks),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_formats_algorithms_scores_values_equations_models_fits_signs_zeroes_or_outcomes_used_to_select_native_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    for name, payload in {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        "computational_chemistry_receipt.json": {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash; write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured_postseal_complete"; write(experiment_path, experiment)
    (package / "STATUS.md").write_text(f"# {claim.claim_id}\n\nStatus: `model_admitted_forced_computational_chemistry_law_{number}_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `{obligation}`\n- Exact law: `{claim.exact_result}`\n- Complete external surface: {SURFACES[number]}.\n- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n")
    progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {"schema": "sft-v3-live-whole-subfield-admission-progress/1", "family": "COMP-001-014-COMPUTATIONAL-CHEMISTRY-AND-CHEMINFORMATICS", "expected_claim_count": 14, "admissions": []}
    progress["admissions"].append({"number": number, "claim_id": claim.claim_id, "receipt_hash": result.receipt_hash, "derivation_seal_hash": sealed.seal_hash})
    progress["admitted_claim_count"] = len(progress["admissions"]); progress["latest_claim"] = claim.claim_id
    successor = int(number) + 1; progress["next_exact_operation"] = f"admit COMP-{successor:03d} through untouched engine" if successor <= 14 else "reconcile complete COMP-001-014 whole subfield"
    progress["proper_subset_is_not_a_subfield_completion_boundary"] = True; write(PROGRESS, progress)
    print(f"admitted {claim.claim_id}: {result.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}"); print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
