#!/usr/bin/env python3
"""Admit and materialize the post-seal glueball spectrum comparison."""

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
from sft.physics.yang_mills_singlet_gap_empirical_v1 import (  # noqa: E402
    CLAIM_ID,
    EXPERIMENT_ID,
    PDG_HASH,
    PDG_PATH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.yang_mills_singlet_gap_empirical_validation_v1 import TARGET_IDS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_yang_mills_singlet_gap_empirical", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Yang-Mills spectrum execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    record = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    program = prediction_program_document(SPEC)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational-data-informed_target-inaccessible_sealed-comparison",
        "development_observations": ["V1/V2 and the glueball literature were known before this V3 reconstruction; no blind-discovery claim is made."],
        "external_measurement_sources": [{
            "source_id": SOURCE_IDS[0],
            "measurement_body": record["source"]["body"],
            "source_uri": record["source"]["source_uri"],
            "snapshot_hash": PDG_HASH,
            "retrieved_date": record["retrieval_date"],
            "custody_role": "withheld_external_spectrum_boundary",
        }],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "withheld_targets": [{"target_id": target_id, "source_id": SOURCE_IDS[0], "content_withheld_from_prediction": True} for target_id in TARGET_IDS],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-yang-mills-singlet-gap-spectrum-comparator/1", SPEC.falsification_condition)),
            "acceptance_condition": "All precise intervals are positive and ordered, every scope/nonidentification row is retained, and the tampered control fails.",
            "falsification_condition": SPEC.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "An isolated colour carrier is not a physical singlet."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Either changed source hash is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "A dimensionful fit, continuum overclaim or early target access is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "An altered lowest mass that breaks interval order is rejected."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((SOURCE_HASH, PDG_HASH, TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain all three precise mass/uncertainty rows plus ground-order, quenched, mixing, full-QCD and nonidentification boundaries",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, PDG_PATH: PDG_HASH},
        "registration_date": "2026-07-25",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def claim_registration() -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {
            "boundary": SPEC.grammar_boundary,
            "completeness_certificate": "generated by the admission engine from the complete declared product",
            "generator": SPEC.generation_rule,
        },
        "claim_id": CLAIM_ID,
        "dependencies": list(SPEC.dependencies),
        "excluded_inputs": list(SPEC.exclusions),
        "empirical_protocol": f"experiments/physics/{EXPERIMENT_ID}/registration.json",
        "intended_certificate": "Complete generated-form census, independent reconstruction and exact post-seal evaluation of every registered spectrum and boundary row.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-25",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested_and_independently_replicated",
        "title": SPEC.title,
    }


def main() -> None:
    expected_engine = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
    actual_engine = subprocess.run(("git", "rev-parse", "HEAD:sft/engine"), cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if actual_engine != expected_engine or subprocess.run(("git", "diff", "--quiet", "--", "sft/engine"), cwd=ROOT).returncode != 0:
        raise SystemExit("frozen engine identity changed; admission halted")
    experiment_path = ROOT / "experiments/physics" / EXPERIMENT_ID / "registration.json"
    write_json(experiment_path, experiment_registration())
    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"] for row in census["claims"]}
    if CLAIM_ID not in existing:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
        print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    else:
        row = next(item for item in census["claims"] if item["claim_id"] == CLAIM_ID)
        receipt_payload = json.loads((ROOT / row["receipt_path"]).read_text(encoding="utf-8"))
        print(f"retained admitted {CLAIM_ID}: {receipt_payload['receipt_hash']}")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", claim_registration())
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == CLAIM_ID)
    receipt_payload = json.loads((ROOT / row["receipt_path"]).read_text(encoding="utf-8"))
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}", "",
        "Status: `empirically_tested_and_independently_replicated`", "",
        "- Protocol: `observational-data-informed_target-inaccessible_sealed-comparison`.",
        "- Every registered lattice mass, uncertainty, ordering and limitation row is retained.",
        "- No lattice value is fitted to or identified with the normalized Fold gap.",
        "- No direct glueball detection or conventional continuum Yang-Mills proof is claimed.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
        f"- Independent validation: `{certificate['external_validation_hash']}`",
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`",
        f"- Engine receipt: `{receipt_payload['receipt_hash']}`",
        f"- Receipt path: `{row['receipt_path']}`", "",
    )), encoding="utf-8")
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
