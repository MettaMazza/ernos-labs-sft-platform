#!/usr/bin/env python3
"""Admit the corrected complete Regge measurement successor."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import prediction_program_document  # noqa: E402
from sft.physics.hadron_regge_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC  # noqa: E402
from sft.physics.hadron_regge_measured_value_successor_validation_v1 import TARGET_IDS, source_hashes  # noqa: E402


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_engine():
    result = subprocess.run((sys.executable, str(ROOT / "tools/verify_engine_seal.py"), "--json"), cwd=ROOT, text=True, capture_output=True)
    if result.returncode or json.loads(result.stdout).get("status") != "VALID_CANONICAL_ENGINE":
        raise SystemExit(result.stdout + result.stderr + "\nRegge successor admission halted")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_hadron_regge_measured_060", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Regge successor execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def source_record():
    return json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))


def experiment_registration():
    record = source_record()
    program = prediction_program_document(SPEC)
    external_sources = []
    for source_id, source in zip(SOURCE_IDS, record["sources"].values()):
        external_sources.append({"source_id": source_id, "measurement_body": source["body"], "source_uri": source["source_uri"], "snapshot_hash": SOURCE_HASH, "retrieved_date": record["retrieval_date"], "custody_role": "withheld_target"})
    return {
        "$schema": "../../../governance/experiment.schema.json", "experiment_id": EXPERIMENT_ID, "claim_id": CLAIM_ID, "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": "V1-V2-HADRON-REGGE-CONTEXT", "role": "development_only", "content_hash": SOURCE_FILES[0][1]}],
        "external_measurement_sources": external_sources,
        "frozen_relation": {"statement": SPEC.exact_result, "relation_hash": sha256_identity(SPEC.exact_result), "dependency_hashes": [sha256_identity(value) for value in SPEC.dependencies], "candidate_grammar": SPEC.generation_rule, "exact_domain": SPEC.grammar_boundary, "target_did_not_select_law": True},
        "inputs": [{"input_id": "REGGE-NORMALIZED-RECEIPT", "value_kind": "admitted-formal-receipt", "content_hash": SOURCE_FILES[1][1]}, {"input_id": "REGGE-DIMENSIONAL-RECEIPT", "value_kind": "admitted-formal-receipt", "content_hash": SOURCE_FILES[2][1]}],
        "withheld_targets": [{"target_id": TARGET_IDS[0], "source_id": SOURCE_IDS[0], "content_withheld_from_prediction": True}],
        "dimension_unit_boundary": {"derived_dimension_carriers": ["exact 3/5 base", "exact 6/5 successor", "depth-independent (6J-3)/5 squared carrier"], "external_reference_protocol": "The common positive GeV-squared comparison label and all resonance records are attached only after the formal seal.", "proof_value_policy": "positive-generated-counts-and-exact-ratios-only", "measurement_record_policy": "external-records-never-become-proof-scalars-or-law-selectors"},
        "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": EXPERIMENT_ID + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]},
        "evaluation_protocol": {"evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator", "comparison_implementation_hash": sha256_identity(("exact-hadron-regge-measured-value-successor/1", SPEC.falsification_condition)), "metrics": [{"metric_id": "COMPLETE-RESONANCE-SUPPORT", "definition": "Each exact squared carrier must lie inside its most restrictive mass-and-width support intersection.", "unit_protocol": "exact rational GeV-squared intervals", "all_rows": True}, {"metric_id": "COMPLETE-ROW-CUSTODY", "definition": "All five mass, uncertainty, width, width-uncertainty and status records retained.", "unit_protocol": "source-bound complete vector", "all_rows": True}], "acceptance_condition": "All five exact carriers lie inside their complete measured resonance supports; no mismatch is an acceptance condition.", "falsification_condition": SPEC.falsification_condition},
        "controls": [{"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A carrier not descending from Claim 059 rejects."}, {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any source or row change rejects."}, {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed census, trace or certificate rejects."}, {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, fitting, row deletion, width widening or mismatch-as-success rejects."}, {"control_id": "DISPLACED-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "A deliberately displaced mass or missing rho5 row rejects rather than becoming a passing label."}],
        "custody_protocol": {"exchange_id": "sft-v3-portable-target-exchange/1", "custodian_id": EXPERIMENT_ID + "-external-target-custodian", "custodian_distinct_from_executor": True, "target_commitment_hash": sha256_identity((SOURCE_HASH, SOURCE_FILES, TARGET_IDS)), "release_requires_matching_seal": True},
        "target_access_policy": "structurally-denied-before-seal", "row_retention_policy": "retain-every-registered-measurement-status-and-control-row", "stop_condition": "Halt without admission on a changed source, excluded carrier, omitted row, target access, fitting, width widening, mismatch-as-success or failed control.",
        "source_hashes": source_hashes(), "registration_date": "2026-07-25", "registered_by": "Maria Smith", "status": "registered",
    }


def main():
    verify_engine()
    experiment_path = ROOT / "experiments" / "physics" / EXPERIMENT_ID / "registration.json"
    write_json(experiment_path, experiment_registration())
    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"]: row for row in census["claims"]}
    if CLAIM_ID in existing:
        print(f"retained admitted {CLAIM_ID}: {existing[CLAIM_ID]['receipt_hash']}")
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
        print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    materialized = subprocess.run((sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True)
    if materialized.returncode:
        raise RuntimeError(materialized.stdout + materialized.stderr)
    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", {"$schema": "../../governance/claim.schema.json", "branch": "physics", "candidate_grammar": {"boundary": SPEC.grammar_boundary, "completeness_certificate": "generated by the untouched admission engine from the complete declared product", "generator": SPEC.generation_rule}, "claim_id": CLAIM_ID, "dependencies": list(SPEC.dependencies), "excluded_inputs": list(SPEC.exclusions), "empirical_protocol": f"experiments/physics/{EXPERIMENT_ID}/registration.json", "intended_certificate": "Complete 256-form census, independent reconstruction, all-five exact measured resonance-support comparison and hostile controls.", "provenance_classes": ["observational_derivation"], "registered_by": "Maria Smith", "registration_date": "2026-07-25", "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"], "statement": SPEC.exact_result, "status": "empirically_tested", "title": SPEC.title})
    experiment = json.loads(experiment_path.read_text(encoding="utf-8")); experiment["status"] = "measured"; write_json(experiment_path, experiment)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((f"# {CLAIM_ID}", "", "Status: `empirically_tested_and_independently_replicated`", "", "- The zero-parameter formal law has exact base `3/5` and exact successor `6/5`.", "- Exact carriers `3/5, 9/5, 3, 21/5, 27/5` all lie inside their complete measured resonance supports.", "- All five masses, uncertainties, widths, width uncertainties and listing statuses are retained.", "- The rho5 summary omission remains explicit; no slope, intercept, residual or correction was fitted.", "- Displaced-mass and missing-row controls reject.", "- This successor replaces Claim 005 for Regge empirical closure while preserving its formal multiplet result and immutable receipt.", f"- Closure: `{certificate['closure_scope']}`", f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`", f"- Engine receipt: `{row['receipt_hash']}`", "")), encoding="utf-8")
    verify_engine()
    print(materialized.stdout.strip())


if __name__ == "__main__":
    main()
