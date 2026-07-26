#!/usr/bin/env python3
"""Admit Claim 074 through the frozen engine and materialize its evidence."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_engine() -> None:
    result = subprocess.run((sys.executable, str(ROOT / "tools/verify_engine_seal.py"), "--json"), cwd=ROOT, text=True, capture_output=True)
    if result.returncode or json.loads(result.stdout).get("status") != "VALID_CANONICAL_ENGINE":
        raise SystemExit(result.stdout + result.stderr + "\nClaim 074 admission halted")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_gravitational_wave_chirp_ringdown_empirical_074", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Claim 074 execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    verify_engine()
    from sft.engine import EngineRepository
    from sft.engine.canonical import sha256_identity
    from sft.physics.generated_empirical_law import prediction_program_document
    from sft.physics.gravitational_wave_chirp_ringdown_empirical_v1 import CLAIM_ID, EXPERIMENT_ID, SOURCE_FILES, SOURCE_HASH, SOURCE_PATH, SPEC
    from sft.physics.gravitational_wave_chirp_ringdown_validation_v1 import TARGET_IDS, source_hashes

    record = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    program = prediction_program_document(SPEC)
    registration = {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational_derivation_with_postseal_independent_comparison",
        "development_observations": [{
            "source_id": record["development_context"][0]["source_id"],
            "role": "preseal-development-context-not-blind-validation",
            "content_hash": record["development_context"][0]["snapshot_hash"],
        }],
        "external_measurement_sources": [{
            "source_id": row["source_id"],
            "measurement_body": "LIGO Scientific Collaboration and Virgo Collaboration",
            "source_uri": row["source_uri"],
            "snapshot_hash": row["snapshot_hash"],
            "retrieved_date": record["retrieval_date"],
            "custody_role": "withheld_postseal_target",
        } for row in record["withheld_postseal_sources"]],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(value) for value in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [{"input_id": "GRAVITATIONAL-WAVE-FORMAL-RECEIPT", "value_kind": "admitted-formal-receipt", "content_hash": record["formal_receipt_hash"]}],
        "withheld_targets": [{"target_id": TARGET_IDS[0], "source_id": "COMPLETE-POSTSEAL-GRAVITATIONAL-WAVE-VECTOR", "content_withheld_from_prediction": True}],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["positive radiation take", "squared frequency ordering", "two-to-one source join", "positive finite damping"],
            "external_reference_protocol": "Dimensional event records open only after Claim 073 and never set a Fold scale.",
            "proof_value_policy": "positive exact whole and fractional Fold forms only",
            "measurement_record_policy": "dimensional values, uncertainties and model roles remain typed external records",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": EXPERIMENT_ID + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-gravitational-wave-chirp-ringdown-comparator/1", SPEC.falsification_condition)),
            "metrics": [
                {"metric_id": "RISING-CHIRP", "definition": "Retain all GW151226 frequency, amplitude, cycle and scope rows.", "unit_protocol": "exact rational external records", "all_rows": True},
                {"metric_id": "TWO-TO-ONE-MERGER", "definition": "Retain both event source/remnant and radiated-energy rows with uncertainties.", "unit_protocol": "typed source and exact rational records", "all_rows": True},
                {"metric_id": "DAMPED-RINGDOWN", "definition": "Retain GW190521 quadrupolar decay and every interpretation boundary.", "unit_protocol": "typed mode and scope records", "all_rows": True},
                {"metric_id": "PROVENANCE", "definition": "Retain GW150914 as development context, never as blind validation.", "unit_protocol": "typed provenance record", "all_rows": True},
            ],
            "acceptance_condition": "All stages and all provenance, uncertainty and scope rows remain; no target changes Claim 073.",
            "falsification_condition": SPEC.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A law not descending from Claim 073 rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any source or row change rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed census, trace or certificate rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, fitting, omission or provenance relabelling rejects."},
            {"control_id": "REVERSED-CHIRP", "kind": "unfavorable_measurement", "expected_rejection": "Falling post-seal event frequency rejects."},
            {"control_id": "ERASED-REMNANT", "kind": "unfavorable_measurement", "expected_rejection": "Failure of the two-to-one transition rejects."},
            {"control_id": "FALSE-BLINDNESS", "kind": "unfavorable_measurement", "expected_rejection": "Relabelling GW150914 as blind rejects."},
            {"control_id": "ERASED-SCOPE", "kind": "unfavorable_measurement", "expected_rejection": "Deleting the conditional/model boundary rejects."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": EXPERIMENT_ID + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((SOURCE_HASH, SOURCE_FILES, TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-empirical-prediction-seal",
        "row_retention_policy": "retain-development-provenance-and-every-postseal-value-error-condition-and-scope-row",
        "stop_condition": "Halt on changed evidence, omission, role conflation, target access, fitting or failed hostile control.",
        "source_hashes": source_hashes(),
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }
    experiment_path = ROOT / "experiments" / "physics" / EXPERIMENT_ID / "registration.json"
    write_json(experiment_path, registration)

    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"]: row for row in census["claims"]}
    missing = [claim_id for claim_id in SPEC.dependencies if claim_id not in existing]
    if missing:
        raise SystemExit("Claim 074 dependencies are not admitted: " + ", ".join(missing))
    if CLAIM_ID in existing:
        print(f"retained admitted {CLAIM_ID}: {existing[CLAIM_ID]['receipt_hash']}")
    else:
        execution = load_execution(CLAIM_ID)
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
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": SPEC.grammar_boundary, "completeness_certificate": "generated by the untouched admission engine from the complete declared product", "generator": SPEC.generation_rule},
        "claim_id": CLAIM_ID,
        "dependencies": list(SPEC.dependencies),
        "excluded_inputs": list(SPEC.exclusions),
        "empirical_protocol": f"experiments/physics/{EXPERIMENT_ID}/registration.json",
        "intended_certificate": "Complete 256-form census, explicit observational provenance and full post-seal two-event chirp/merger/ringdown vector.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested",
        "title": SPEC.title,
    })
    registration["status"] = "measured"
    write_json(experiment_path, registration)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- GW150914 remains disclosed pre-seal observational context, not a blind prediction.",
        "- GW151226 supplies the complete post-seal rising-chirp and two-to-one merger record.",
        "- GW190521 supplies the complete post-seal damped quadrupolar remnant record with all scope boundaries.",
        "- No dimensional value or fitted waveform selected or changed Claim 073.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Engine receipt: `{row['receipt_hash']}`", "",
    )), encoding="utf-8")
    verify_engine()
    print(materialized.stdout.strip())


if __name__ == "__main__":
    main()
