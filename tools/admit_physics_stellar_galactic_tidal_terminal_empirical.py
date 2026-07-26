#!/usr/bin/env python3
"""Admit the post-seal stellar/galactic/tidal comparison through the sealed engine."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import prediction_program_document
from sft.physics.stellar_galactic_tidal_terminal_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.stellar_galactic_tidal_terminal_validation_v1 import TARGET_IDS, source_hashes


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_engine():
    result = subprocess.run((sys.executable, str(ROOT / "tools/verify_engine_seal.py"), "--json"), cwd=ROOT, text=True, capture_output=True)
    if result.returncode or json.loads(result.stdout).get("status") != "VALID_CANONICAL_ENGINE":
        raise SystemExit(result.stdout + result.stderr + "\nstellar/galactic/tidal empirical admission halted")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_stellar_galactic_tidal_empirical_068", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load stellar/galactic/tidal empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration():
    record = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    program = prediction_program_document(SPEC)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": "V1-V2-STELLAR-GALACTIC-TIDAL-CONTEXT", "role": "development_only", "content_hash": sha256_identity("prior-obligation-only")}],
        "external_measurement_sources": [
            {
                "source_id": row["source_id"],
                "measurement_body": row["title"],
                "source_uri": row["source_uri"],
                "snapshot_hash": row["snapshot_hash"],
                "retrieved_date": record["retrieval_date"],
                "custody_role": "withheld_target",
            }
            for row in record["sources"]
        ],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(value) for value in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [{"input_id": "STELLAR-GALACTIC-TIDAL-FORMAL-RECEIPT", "value_kind": "admitted-formal-receipt", "content_hash": record["formal_receipt_hash"]}],
        "withheld_targets": [{"target_id": TARGET_IDS[0], "source_id": "COMPLETE-SEVEN-SOURCE-VECTOR", "content_withheld_from_prediction": True}],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["hydrostatic restoration", "stellar terminal powers", "flat-curve support", "fourth-power rotation carrier", "isolated tidal terminal"],
            "external_reference_protocol": "The seven sources supply only post-seal observational comparisons, reported uncertainties and declared capability boundaries.",
            "proof_value_policy": "positive exact whole and fractional Fold forms only",
            "measurement_record_policy": "reported coordinates remain external records and never select or alter the Fold proof",
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
            "comparison_implementation_hash": sha256_identity(("exact-stellar-galactic-tidal-comparator/1", SPEC.falsification_condition)),
            "metrics": [
                {"metric_id": "SOLAR-STRUCTURE", "definition": "Retain helioseismic precision and the observed/reference interval without relabelling the conventional model as SFT.", "unit_protocol": "exact rational solar-radius fractions and precision orders", "all_rows": True},
                {"metric_id": "STELLAR-PIECEWISE", "definition": "Compare powers three/four against all six measured slope intervals.", "unit_protocol": "exact rational slopes and uncertainties", "all_rows": True},
                {"metric_id": "GALAXY-SUPPORT", "definition": "Retain SPARC, central/systematic Tully-Fisher and Bullet Cluster rows together.", "unit_protocol": "exact counts, slopes, scatter and significance", "all_rows": True},
                {"metric_id": "TIDAL-BOUNDARY", "definition": "Retain lunar 1:1 and Mercury 3:2 records together.", "unit_protocol": "exact rational periods and whole cycle ratios", "all_rows": True},
            ],
            "acceptance_condition": "All seven sources and every favorable, offset, piecewise and boundary row remain, with formal and observational roles kept separate.",
            "falsification_condition": SPEC.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A law not descending from Claim 067 rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any source identity or registered row change rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed census, trace or certificate rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, fitting, omission or role relabelling rejects."},
            {"control_id": "ERASED-STELLAR-REGIMES", "kind": "unfavorable_measurement", "expected_rejection": "Deleting four non-endpoint regimes rejects completeness."},
            {"control_id": "CENTRAL-ONLY-TULLY-FISHER", "kind": "unfavorable_measurement", "expected_rejection": "Deleting the systematic interval or hiding the central offset rejects."},
            {"control_id": "FALSE-LUNAR-LOCK", "kind": "unfavorable_measurement", "expected_rejection": "Unequal lunar periods reject the 1:1 comparison."},
            {"control_id": "ERASED-MERCURY-BOUNDARY", "kind": "unfavorable_measurement", "expected_rejection": "Relabelling Mercury as 1:1 rejects the explicit resonance boundary."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": EXPERIMENT_ID + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((SOURCE_HASH, SOURCE_FILES, TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-all-seven-sources-six-stellar-regimes-both-Tully-intervals-and-both-tidal-cases",
        "stop_condition": "Halt without admission on changed evidence, omitted row, hidden offset, target access, fitting, role conflation or failed hostile control.",
        "source_hashes": source_hashes(),
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
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
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": SPEC.grammar_boundary, "completeness_certificate": "generated by the untouched admission engine from the complete declared product", "generator": SPEC.generation_rule},
        "claim_id": CLAIM_ID,
        "dependencies": list(SPEC.dependencies),
        "excluded_inputs": list(SPEC.exclusions),
        "empirical_protocol": f"experiments/physics/{EXPERIMENT_ID}/registration.json",
        "intended_certificate": "Complete 256-form census, seven-source post-seal vector, all six stellar regimes, complete central/systematic galaxy comparison, and lunar/Mercury boundary controls.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested",
        "title": SPEC.title,
    })
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- The complete seven-source record was inaccessible until Claim 067 sealed.",
        "- All six stellar slope regimes remain; only the two terminal endpoint domains contain powers four and three.",
        "- The Tully-Fisher central offset and full systematic interval are both retained.",
        "- SPARC, Bullet Cluster, lunar 1:1 and Mercury 3:2 observations remain together.",
        "- Row-erasure, central-only, false-lock and erased-boundary controls reject.",
        f"- Closure: `{certificate['closure_scope']}`", f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`", f"- Engine receipt: `{row['receipt_hash']}`", "",
    )), encoding="utf-8")
    verify_engine()
    print(materialized.stdout.strip())


if __name__ == "__main__":
    main()
