#!/usr/bin/env python3
"""Submit the post-seal criticality and turbulence empirical successor."""

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
from sft.physics.criticality_universality_turbulence_empirical_v1 import (  # noqa: E402
    CLAIM_ID,
    EXPERIMENT_ID,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.criticality_universality_turbulence_validation_v1 import TARGET_IDS  # noqa: E402
from sft.physics.generated_empirical_law import prediction_program_document  # noqa: E402


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_engine():
    result = subprocess.run(
        (sys.executable, str(ROOT / "tools/verify_engine_seal.py"), "--json"),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode or json.loads(result.stdout).get("status") != "VALID_CANONICAL_ENGINE":
        raise SystemExit(result.stdout + result.stderr + "\ncriticality/turbulence empirical admission halted")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_criticality_turbulence_empirical", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load criticality/turbulence empirical execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def source_record():
    return json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))


def experiment_registration():
    record = source_record()
    program = prediction_program_document(SPEC)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational-data-informed_target-inaccessible_sealed-comparison",
        "development_observations": [
            record["historical_boundary"],
            "Formal Claim 047, its complete 256-form census, and its official engine receipt preceded the four bound target records.",
            "La02 and every finite-Reynolds or analysis-range limitation remain retained as evidence, not removed as inconveniences.",
        ],
        "external_measurement_sources": [
            {
                "source_id": source["source_id"],
                "measurement_body": source["title"],
                "source_uri": source["url"],
                "snapshot_hash": source["snapshot_hash"],
                "source_pages": [source["source_page"]],
                "custody_role": source["role"],
            }
            for source in record["sources"]
        ],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(value) for value in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "withheld_targets": [
            {"target_id": target_id, "source_ids": list(SOURCE_IDS), "content_withheld_from_prediction": True}
            for target_id in TARGET_IDS
        ],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "forbidden_capabilities": [
                "clock",
                "dynamic_import",
                "environment",
                "filesystem_read",
                "filesystem_write",
                "foreign_function",
                "network",
                "subprocess",
            ],
        },
        "evaluation_protocol": {
            "evaluator_id": EXPERIMENT_ID + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-criticality-universality-turbulence-comparator/1", SPEC.falsification_condition)),
            "acceptance_condition": "The complete erbium vector passes; exactly the four registered manganite samples pass and La02 remains a nonmatch; the structure interval contains 2/3; both physical spectrum routes exhibit the five-thirds plateau; all boundaries and controls remain retained.",
            "falsification_condition": SPEC.falsification_condition,
        },
        "controls": [
            {
                "control_id": kind.upper(),
                "kind": kind,
                "expected_rejection": "Any premise, source, artifact, row, interval, class-membership or spectrum-orientation violation halts.",
            }
            for kind in ("false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement")
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((SOURCE_HASH, SOURCE_FILES, TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain all four sources, all five manganite rows including La02, every interval, both spectrum methods, and every finite-Reynolds, range, threshold and empty-exponent limitation",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)},
        "registration_date": "2026-07-25",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def claim_registration():
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
        "intended_certificate": "Complete 256-form census, independent reconstruction, capability-closed custody, complete critical-exponent and turbulence vector, exact interval comparison, unfavorable-row retention, limitations and adverse-control rejection.",
        "provenance_classes": ["observational_derivation"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-25",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "unfavorable_measurement"],
        "statement": SPEC.exact_result,
        "status": "empirically_tested_and_independently_replicated",
        "title": SPEC.title,
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
        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"})
        write_json(manifest_path, manifest)
    materialized = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if materialized.returncode:
        raise RuntimeError(materialized.stdout + materialized.stderr)
    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", claim_registration())
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    row = next(item for item in json.loads(census_path.read_text(encoding="utf-8"))["claims"] if item["claim_id"] == CLAIM_ID)
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text(
        "\n".join(
            (
                f"# {CLAIM_ID}",
                "",
                "Status: `empirically_tested_and_independently_replicated`",
                "",
                "- Erbium beta/gamma/nu intervals contain the sealed exact vector.",
                "- Four complete manganite beta/gamma/delta vectors contain the sealed exact vector.",
                "- La02 is retained and rejects complete membership in that exponent class.",
                "- The exact turbulence interval `[666,692]/1000` contains `2/3`.",
                "- The physical flow exhibits five-thirds compensated plateaux by two analysis routes.",
                "- All finite-Reynolds, range, threshold and empty-exponent boundaries remain retained.",
                "- Tampered interval, relabelled nonmatch, removed-row and reversed-spectrum controls reject.",
                f"- Closure: `{certificate['closure_scope']}`",
                f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
                f"- Engine receipt: `{row['receipt_hash']}`",
                "",
            )
        ),
        encoding="utf-8",
    )
    verify_engine()
    print(materialized.stdout.strip())


if __name__ == "__main__":
    main()
