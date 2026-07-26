#!/usr/bin/env python3
"""Admit and materialize the post-seal Landauer comparison."""

from __future__ import annotations

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
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.physics.landauer_demon_empirical_v1 import (  # noqa: E402
    CLAIM_ID,
    EXPERIMENT_ID,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_landauer_empirical", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Landauer empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    source = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    base = experiment_registration_record(SPEC)
    program = prediction_program_document(SPEC)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational-data-informed_target-inaccessible_sealed-comparison",
        "development_observations": [],
        "external_measurement_sources": [
            {"source_id": source_id, "measurement_body": source["sources"][source_id]["body"], "source_uri": source["sources"][source_id]["source_uri"], "snapshot_hash": SOURCE_HASH, "retrieved_date": source["retrieval_date"], "custody_role": "withheld_target"}
            for source_id in SOURCE_IDS
        ],
        "frozen_relation": {"statement": SPEC.exact_result, "relation_hash": sha256_identity(SPEC.exact_result), "dependency_hashes": [sha256_identity(item) for item in SPEC.dependencies], "candidate_grammar": SPEC.generation_rule, "exact_domain": SPEC.grammar_boundary, "target_did_not_select_law": True},
        "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(SPEC.dependencies)}],
        "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True} for row in SPEC.target_rows],
        "dimension_unit_boundary": {"derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001"], "external_reference_protocol": "The conventional k_B T ln 2 inscription remains an external conditional thermal-energy record.", "proof_value_policy": "positive-generated-counts-exact-ratios-held-labels-and-empty-form-only", "measurement_record_policy": "external-logarithmic-and-dimensional-records-never-become-SFT-proof-scalars"},
        "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": EXPERIMENT_ID + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]},
        "evaluation_protocol": {"evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator", "comparison_implementation_hash": sha256_identity(("exact-Landauer-structural-comparison", EXPERIMENT_ID, SPEC.falsification_condition)), "metrics": [{"metric_id": "complete-erasure-bound-scope-vector", "definition": "Retain every reset, heat, bound, experimental-saturation and limitation row exactly.", "unit_protocol": "Dimensional and logarithmic inscriptions remain external records.", "all_rows": True}], "acceptance_condition": "Every registered primary-source and scope row matches the sealed structural prediction and the tampered label is rejected.", "falsification_condition": SPEC.falsification_condition},
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A reset lacking two distinguishable preimages is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed source record is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access or dimensional proof-value import is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "A changed heat, bound, saturation or scope label fails."}
        ],
        "custody_protocol": {"exchange_id": "sft-v3-portable-target-exchange/1", "custodian_id": EXPERIMENT_ID + "-external-target-custodian", "custodian_distinct_from_executor": True, "target_commitment_hash": sha256_identity((SOURCE_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in SPEC.target_rows))), "release_requires_matching_seal": True},
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-favorable-limiting-and-tampered-row",
        "stop_condition": "Halt after every registered target and adverse-control row is evaluated once, or immediately on any violation.",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, "experiment-registration-record": sha256_identity(base)},
        "registration_date": "2026-07-25",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def main() -> None:
    expected_engine = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
    actual_engine = subprocess.run(("git", "rev-parse", "HEAD:sft/engine"), cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if actual_engine != expected_engine or subprocess.run(("git", "diff", "--quiet", "--", "sft/engine"), cwd=ROOT).returncode != 0:
        raise SystemExit("frozen engine identity changed; admission halted")
    write_json(ROOT / "experiments/physics" / EXPERIMENT_ID / "registration.json", experiment_registration())
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if CLAIM_ID in existing:
        raise SystemExit(f"{CLAIM_ID} is already admitted; immutable receipt retained")
    execution = load_execution()
    receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
    print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    package = ROOT / "claims" / CLAIM_ID
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested_and_independently_replicated"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/physics" / EXPERIMENT_ID / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((f"# {CLAIM_ID}", "", "Status: `empirically_tested_and_independently_replicated`", "", "- Protocol: `observational-data-informed_target-inaccessible_sealed-comparison`", "- All reset, heat, bound, long-cycle and limitation rows are retained.", "- Native half-One is not misreported as a dimensional energy equality.", f"- Closure: `{certificate['closure_scope']}`", f"- Derivation seal: `{certificate['derivation_seal_hash']}`", f"- Independent validation: `{certificate['external_validation_hash']}`", f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`", f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`", f"- Engine receipt: `{receipt.receipt_hash}`", f"- Receipt path: `{row['receipt_path']}`", "")), encoding="utf-8")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
