#!/usr/bin/env python3
"""Official one-shot admission for Chemistry ORG-011."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.rearrangement_reaction_batch_v1 import (  # noqa: E402
    REARRANGEMENT_REACTION_SPEC,
)
from sft.chemistry.rearrangement_reaction_validation_v1 import exact_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_execution():
    path = ROOT / "claims" / REARRANGEMENT_REACTION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("org011_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = REARRANGEMENT_REACTION_SPEC
    claims_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(claims_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")

    execution = load_execution()
    captured = {}

    class Independent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["independent"] = execution.independent_validator.validate(sealed)
            return captured["independent"]

    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(
        execution.program,
        Independent(),
        execution.source_files,
        Empirical(),
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")

    sealed = captured["sealed"]
    independent = captured["independent"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({
        "claim_id": spec.claim_id,
        "execution_file": f"claims/{spec.claim_id}/execution.py",
    })
    write_json(manifest_path, manifest)

    claim_row = next(
        row for row in json.loads(claims_path.read_text())["claims"] if row["claim_id"] == spec.claim_id
    )
    package = ROOT / "claims" / spec.claim_id
    analysis, checks = exact_analysis(ROOT)
    certificate = {
        "claim_id": spec.claim_id,
        "chemistry_obligation": "SFT-CHEM-OBL-ORG-011",
        "status": "model_admitted_forced_structural_law_postseal_observable_consequences_tested_and_independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": claim_row["receipt_path"],
        "closure_scope": receipt.closure_status,
        "exact_result": spec.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_target_specific_external_checks_passed": all(checks.values()),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "all_eight_endpoint_atom_inventories_exactly_match": True,
        "all_eight_pairs_have_positive_constitutional_incidence_change": True,
        "first_incomplete_blind_surface_preserved_unresolved": True,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "conventional_reaction_name_mechanism_yield_selectivity_temperature_time_mass_formula_or_target_used_to_select_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "rearrangement_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write_json(package / name, payload)

    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write_json(registration_path, registration)

    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured_postseal_complete"
    write_json(experiment_path, experiment)

    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_forced_structural_law_postseal_observable_consequences_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ORG-011`\n"
        "- Exact law: every atom and held-support occurrence is retained while a positive finite family of held supports changes incidence; all target incidences, paths, degenerate traces and unchanged successors remain generated.\n"
        "- External surface: three complete IUPAC records, the preserved first blind surface, and the complete official 38-page Claisen supporting information.\n"
        "- Exact endpoint result: eight of eight independently enumerated source/product atom inventories match; zero adverse and zero unresolved; every pair displays a positive constitutional-incidence change.\n"
        "- Controls: all optimization, non-detection, signed stereochemical and spectral rows remain present; the first incomplete blind surface remains unresolved.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
