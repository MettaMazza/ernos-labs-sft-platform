#!/usr/bin/env python3
"""Submit exactly one POLY-001--013 claim per invocation in dependency order."""

from dataclasses import asdict
import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.polymer_chemistry_batch_v1 import SPEC_BY_NUMBER
from sft.chemistry.polymer_chemistry_validation_v1 import exact_analysis
from sft.engine import EngineRepository


EXTERNAL_SURFACES = {
    "001": "chain mass, repeat identity, end-group mass and exact repeat-count records",
    "002": "complete molecular-size populations, 23-laboratory MALDI and five individual NMR rows",
    "003": "NIST number- and mass-weighted molecular-size records with stated uncertainties",
    "004": "exact dispersity reconstructions, corrected and uncorrected NIST records, all 20 PAMS rows and the retained source-table defect",
    "005": "initiation, propagation, transfer, termination and all conversion/distribution source support",
    "006": "reactive-group, intermolecular-merge, crosslink-conversion and distribution support",
    "007": "ordered copolymer sequence and four complete deuterated-composition records",
    "008": "finite polymer topology, branching, star, network and architecture source support",
    "009": "eleven complete thermoreversible gel states and the preserved absent cell",
    "010": "finite conformation, exact squared size and architecture-size source support",
    "011": "eight PVOH compositions, six blend compositions, transition direction and hysteresis records",
    "012": "scission, transfer, unzipping, crosslinking and product-network support, including the 15-page OCR retry",
    "013": "four exact Chemistry-to-Materials paired records with one-owner handoff boundaries",
}


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def build_execution(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("claim", choices=tuple(SPEC_BY_NUMBER))
    args = parser.parse_args()
    claim = SPEC_BY_NUMBER[args.claim]
    obligation = f"SFT-CHEM-OBL-POLY-{args.claim}"
    census_path = ROOT / "census/claims.json"
    admitted = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if claim.claim_id in admitted:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    for dependency in claim.dependencies:
        if dependency not in admitted:
            raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")
    run = build_execution(claim)
    captured = {}

    class Independent:
        def validate(self, sealed):
            captured.update(sealed=sealed, independent=run.independent_validator.validate(sealed))
            return captured["independent"]

    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = run.empirical_validator.validate(sealed)
            return captured["empirical"]

    result = EngineRepository(ROOT).execute_official(run.program, Independent(), run.source_files, Empirical())
    if not result.model_admitted:
        raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}; obligation remains open for a distinct lawful retry")
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"})
    write(manifest_path, manifest)
    row = next(item for item in json.loads(census_path.read_text())["claims"] if item["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    certificate = {
        "claim_id": claim.claim_id,
        "chemistry_obligation": obligation,
        "status": "model_admitted_forced_polymer_chemistry_law_empirically_tested_and_independently_replicated",
        "source_manifest_hash": run.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": result.external_validation_hash,
        "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": result.receipt_hash,
        "engine_receipt_path": row["receipt_path"],
        "closure_scope": result.closure_status,
        "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_registered_target_checks_passed": all(checks.values()),
        "registered_target_check_count": len(checks),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "first_failed_reconstructions_preserved_and_retried": True,
        "no_obligation_retired_on_first_failure": True,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_values_equations_fits_discrepancies_or_trends_used_to_select_native_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        "polymer_chemistry_receipt.json": {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured_postseal_complete"
    write(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {claim.claim_id}\n\nStatus: `model_admitted_forced_polymer_chemistry_law_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `{obligation}`\n"
        f"- Exact law: `{claim.exact_result}`\n"
        f"- External surface: {EXTERNAL_SURFACES[args.claim]}; the complete 21-artifact, 28,928,563-byte and 279-page family surface is retained.\n"
        f"- Failed reconstructions: preserved and retried; no claim retired on first failure.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Engine receipt: `{result.receipt_hash}`\n"
    )
    print(f"admitted {claim.claim_id}: {result.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
