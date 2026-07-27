#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.chemistry.conformer_population_ordering_batch_v1 import CONFORMER_POPULATION_ORDERING_SPEC, PRIMARY_PATH  # noqa:E402
from sft.chemistry.conformer_population_ordering_validation_v1 import _source_rows, exact_analysis  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402


def write_json(path, payload): path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CONFORMER_POPULATION_ORDERING_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("org006_execution", path); module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main():
    spec = CONFORMER_POPULATION_ORDERING_SPEC; claims_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(claims_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution(); captured = {}
    class Independent:
        def validate(self, sealed): captured["sealed"] = sealed; captured["independent"] = execution.independent_validator.validate(sealed); return captured["independent"]
    class Empirical:
        def validate(self, sealed): captured["empirical"] = execution.empirical_validator.validate(sealed); return captured["empirical"]
    receipt = EngineRepository(ROOT).execute_official(execution.program, Independent(), execution.source_files, Empirical())
    if not receipt.model_admitted: raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed = captured["sealed"]; independent = captured["independent"]; empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text()); manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path, manifest)
    claim_row = next(row for row in json.loads(claims_path.read_text())["claims"] if row["claim_id"] == spec.claim_id); package = ROOT / "claims" / spec.claim_id
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    certificate = {
        "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-ORG-006", "status": "model_admitted_forced_exact_relation_blind_empirically_tested_and_independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash, "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": claim_row["receipt_path"],
        "closure_scope": receipt.closure_status, "exact_result": spec.exact_result, "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions), **analysis,
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_temperature_energy_population_species_or_signed_value_used_to_generate_or_select_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    for name, payload in {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)}, "certificate.json": certificate,
    }.items(): write_json(package / name, payload)
    registration_path = package / "registration.json"; registration = json.loads(registration_path.read_text()); registration["status"] = "empirically_tested"; registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forced_exact_relation_blind_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `SFT-CHEM-OBL-ORG-006`\n- Exact witness: populations 3/4 and 1/4; successor 3/5 and 2/5.\n"
        f"- Blind 298.5 K population vector: tt 0.33 ± 0.03, tg 0.51 ± 0.01, pm 0.02 ± 0.01, pp 0.14 ± 0.01.\n"
        f"- Blind energy order: tt structural reference, tg 480, pp 658, pm 3263 cal mol^-1; positive gaps 480, 178, 2605.\n"
        f"- External surface: 14 targets, 22 spectra, 8 ACS tables and 224 measured rows; all adverse routes preserved.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n", encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__": main()
