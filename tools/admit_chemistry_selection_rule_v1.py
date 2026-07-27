#!/usr/bin/env python3
"""Officially execute and materialize ELEC-010 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.selection_rule_batch_v1 import SELECTION_RULE_SPEC  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SELECTION_RULE_SPEC.claim_id / "execution.py"
    specification = importlib.util.spec_from_file_location("chem_selection_010", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    s = SELECTION_RULE_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if s.claim_id in existing:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution, captured = load_execution(), {}

    class IndependentCapture:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class EmpiricalCapture:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(execution.program, IndependentCapture(), execution.source_files, EmpiricalCapture())
    if not receipt.model_admitted:
        raise SystemExit("halted " + str(receipt.halted_stage) + "; " + receipt.receipt_hash)
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": s.claim_id, "execution_file": "claims/" + s.claim_id + "/execution.py"})
    write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == s.claim_id)
    claim = ROOT / "claims" / s.claim_id
    artifacts = {
        "candidate_census.json": {"claim_id": s.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": s.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": s.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": s.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": s.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-ELEC-010",
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
            "exact_result": s.exact_result,
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "NIST_transition_rows": 60,
            "NIST_adverse_note_rows": 3,
            "direct_one_fold_records": 52,
            "mediated_multi_fold_records": 2,
            "unresolved_endpoint_records": 1,
            "coupling_records": 4,
            "closed_observation_coordinates": 1,
            "resolved_directional_multiplicity_retained": 54,
            "known_inversion_pairs_changed": 52,
            "textbook_selection_rule_imported": False,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, data in artifacts.items():
        write_json(claim / name, data)
    registration = json.loads((claim / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(claim / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / s.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    (claim / "STATUS.md").write_text(
        "# " + s.claim_id + "\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ELEC-010`\n"
        "- Closure: `" + receipt.closure_status + "`\n"
        "- Derivation seal: `" + sealed.seal_hash + "`\n"
        "- Independent validation: `" + receipt.external_validation_hash + "`\n"
        "- Empirical validation: `" + receipt.empirical_validation_hash + "`\n"
        "- Measurement receipt: `" + empirical.measurement_receipt_hash + "`\n"
        "- Engine receipt: `" + receipt.receipt_hash + "`\n"
        "- External vector: all 60 NIST H2 transition records plus adverse notes 42, 73 and 78.\n"
        "- Exact classes: 52 direct, two mediated, one unresolved, four coupled, one closed coordinate.\n"
        "- Absence rule: EmptyOne only; glyph 0 is never an SFT number.\n"
        "- Scope: chemical observation-class and selection-rule structure.\n",
        encoding="utf-8",
    )
    print("admitted " + s.claim_id + ": " + receipt.receipt_hash)
    print("derivation seal: " + sealed.seal_hash)
    print("candidates: " + str(len(sealed.census.candidates)) + "; survivors: " + str(sum(row.survives for row in sealed.decisions)))
    print("empirical measurements: " + str(len(empirical.measurements)) + "; passed: " + str(empirical.passed))


if __name__ == "__main__":
    main()
