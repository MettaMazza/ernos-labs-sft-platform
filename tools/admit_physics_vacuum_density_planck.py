#!/usr/bin/env python3
"""Admit the post-seal Planck/CODATA vacuum-density comparison."""

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
from sft.physics.generated_empirical_law import prediction_program_document  # noqa: E402
from sft.physics.vacuum_density_planck_empirical_v1 import (  # noqa: E402
    CLAIM_ID,
    CODATA_HASH,
    CODATA_PATH,
    EXPERIMENT_ID,
    PDF_HASH,
    PDF_PATH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.vacuum_density_planck_validation_v1 import TARGET_IDS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_engine() -> None:
    completed = subprocess.run((sys.executable, str(ROOT / "tools/verify_engine_seal.py"), "--json"), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0 or json.loads(completed.stdout).get("status") != "VALID_CANONICAL_ENGINE":
        raise SystemExit(completed.stdout + completed.stderr + "\nvacuum-density empirical admission halted")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_vacuum_density_Planck", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load vacuum-density empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    record = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    program = prediction_program_document(SPEC)
    source_rows = record["sources"]
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational-data-informed_target-inaccessible_sealed-comparison",
        "development_observations": [
            "V1/V2 cosmological targets and an older local Planck transcription were known before V3 reconstruction; no historical-blindness claim is made.",
            "Formal claim 035 was admitted before the primary Planck PDF was retrieved for this comparison.",
            "The page-225 H0 row is 67.68 +/- 0.42 and corrects the older local 67.66 transcription without changing any prior receipt.",
        ],
        "external_measurement_sources": [
            {
                "source_id": source_rows[0]["source_id"],
                "measurement_body": source_rows[0]["title"],
                "source_uri": source_rows[0]["source_uri"],
                "snapshot_hash": PDF_HASH,
                "retrieved_date": record["retrieval_date"],
                "custody_role": "withheld_primary_Planck_density_and_Hubble_rows",
            },
            {
                "source_id": source_rows[1]["source_id"],
                "measurement_body": source_rows[1]["title"],
                "source_uri": source_rows[1]["source_uri"],
                "snapshot_hash": CODATA_HASH,
                "retrieved_date": record["retrieval_date"],
                "custody_role": "withheld_exact_dimensional_speed_reference",
            },
        ],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "withheld_targets": [{"target_id": target_id, "source_ids": list(SOURCE_IDS), "content_withheld_from_prediction": True} for target_id in TARGET_IDS],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-vacuum-density-Planck-comparator/1", SPEC.falsification_condition)),
            "acceptance_condition": "Both exact Fold magnitudes lie in their complete Planck intervals, the central budget closes, dimensional transport is positive, type and transcription controls pass, and the tampered target fails.",
            "falsification_condition": SPEC.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "An imported continuum vacuum sum cannot replace the sealed finite ledger."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed source record, primary PDF or CODATA table is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed coefficient, prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Early target access, fitted transport or untyped floor/fraction equality is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "A vacuum central value changed to 0.6000 rejects the interval comparison."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((SOURCE_HASH, PDF_HASH, CODATA_HASH, TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain all Planck vacuum, matter, H0, uncertainty, CODATA exact-c, transcription-correction and local/global type-control rows",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, PDF_PATH: PDF_HASH, CODATA_PATH: CODATA_HASH},
        "registration_date": "2026-07-25",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def claim_registration() -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": SPEC.grammar_boundary, "completeness_certificate": "generated by the admission engine from the complete declared product", "generator": SPEC.generation_rule},
        "claim_id": CLAIM_ID,
        "dependencies": list(SPEC.dependencies),
        "excluded_inputs": list(SPEC.exclusions),
        "empirical_protocol": f"experiments/physics/{EXPERIMENT_ID}/registration.json",
        "intended_certificate": "Complete 256-form census, independent reconstruction, capability-closed target custody and exact evaluation of all Planck, CODATA, transcription-correction, uncertainty and type-control rows.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-25",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested_and_independently_replicated",
        "title": SPEC.title,
    }


def main() -> None:
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
    completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", claim_registration())
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {CLAIM_ID}", "",
        "Status: `empirically_tested_and_independently_replicated`", "",
        "- Exact `11/16` lies inside the complete Planck vacuum-fraction interval.",
        "- Exact normalized `33/16` lies inside the corresponding three-direction interval.",
        "- Planck H0 and CODATA exact c transport the sealed coefficient to a positive exact dimensional interval.",
        "- Local `One/2^20`, finite-ledger mean, global share and dimensional Lambda remain distinct typed quantities.",
        "- The primary page-225 `67.68` H0 row corrects the older local transcription without rewriting prior receipts.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
        f"- Independent validation: `{certificate['external_validation_hash']}`",
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`",
        f"- Engine receipt: `{row['receipt_hash']}`",
        f"- Receipt path: `{row['receipt_path']}`", "",
    )), encoding="utf-8")
    verify_engine()
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
