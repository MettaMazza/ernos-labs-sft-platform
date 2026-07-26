#!/usr/bin/env python3
"""Admit and materialize the terminal Parker proton-energy comparison."""

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
from sft.physics.parker_proton_energy_terminal_law_v1 import (  # noqa: E402
    CLAIM_ID,
    EXPERIMENT_ID,
    SPEC,
)
from sft.physics.parker_proton_energy_terminal_validation_v1 import (  # noqa: E402
    FALSIFICATION_CONDITION,
    SOURCE_IDS,
    TARGET_IDS,
    experiment_registration_record,
    source_hashes,
)


ENGINE_TREE = "ad30f4866c18b2adbade95a0b2de40d5caa61308"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_parker_proton_energy_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load Parker proton-energy execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    internal = experiment_registration_record()
    source_record = json.loads(
        (ROOT / "experiments/external_sources/physics/snapshots/parker-proton-energy-source-record.json").read_text(
            encoding="utf-8"
        )
    )
    sources = {row["source_id"]: row for row in source_record["sources"]}
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "evidence_mode": "observational-data-informed_target-inaccessible_sealed-comparison",
        "development_observations": [
            "The earlier SFT formula and the Parker report were known before this V3 reconstruction; no historical-blindness claim is made.",
            "The external manuscripts do not define approximately 400 keV as an exact cutoff or report an uncertainty for that label.",
        ],
        "external_measurement_sources": [
            {
                "source_id": source_id,
                "measurement_body": sources[source_id]["measurement_body"],
                "source_uri": sources[source_id]["source_uri"],
                "snapshot_hash": sources[source_id]["snapshot_hash"],
                "retrieved_date": source_record["retrieval_date"],
                "custody_role": "withheld_external_target_boundary",
            }
            for source_id in SOURCE_IDS
        ],
        "frozen_relation": {
            "statement": SPEC.exact_result,
            "relation_hash": sha256_identity(SPEC.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in SPEC.dependencies],
            "candidate_grammar": SPEC.generation_rule,
            "exact_domain": SPEC.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "withheld_targets": [
            {
                "target_id": target_id,
                "source_ids": list(SOURCE_IDS),
                "content_withheld_from_prediction": True,
            }
            for target_id in TARGET_IDS
        ],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": internal["prediction_program"]["program_id"],
            "program_hash": sha256_identity(internal["prediction_program"]),
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
            "comparison_implementation_hash": sha256_identity(
                ("exact-parker-proton-energy-comparator/1", FALSIFICATION_CONDITION)
            ),
            "acceptance_condition": (
                "The exact propagated terminal interval lies within the complete registered Parker spectrum range, "
                "every context and adverse-formula row is retained, the precision overclaim is rejected, and the "
                "unfavorable altered-range control fails."
            ),
            "falsification_condition": FALSIFICATION_CONDITION,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A named proton without the admitted colour structure is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed source identity is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed prediction, census or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Early target access, a local plasma fit or a precision-cutoff overclaim is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "Reducing the registered spectrum ceiling below the prediction rejects the correspondence."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": sha256_identity((source_hashes(), TARGET_IDS)),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": internal["row_retention_policy"],
        "source_hashes": source_hashes(),
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
        "intended_certificate": (
            "Complete generated-form census, independent exact reconstruction, capability-closed prediction, "
            "complete source custody, exact uncertainty propagation and adverse-formula comparison."
        ),
        "provenance_classes": [item.value for item in SPEC.provenance],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-25",
        "required_controls": [
            "false_premise",
            "tampered_source",
            "tampered_artifact",
            "boundary",
            "unfavorable_measurement",
        ],
        "statement": SPEC.exact_result,
        "status": "empirically_tested_and_independently_replicated",
        "title": SPEC.title,
    }


def verify_engine() -> None:
    actual = subprocess.run(
        ("git", "rev-parse", "HEAD:sft/engine"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = subprocess.run(("git", "diff", "--quiet", "--", "sft/engine"), cwd=ROOT).returncode
    if actual != ENGINE_TREE or dirty != 0:
        raise SystemExit("frozen engine identity changed; admission halted")


def main() -> None:
    verify_engine()
    experiment_path = ROOT / "experiments/physics" / EXPERIMENT_ID / "registration.json"
    write_json(experiment_path, experiment_registration())
    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text(encoding="utf-8"))
    existing = {row["claim_id"] for row in census["claims"]}
    if CLAIM_ID not in existing:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        print(f"admitted {CLAIM_ID}: {receipt.receipt_hash}")
    else:
        row = next(item for item in census["claims"] if item["claim_id"] == CLAIM_ID)
        receipt = json.loads((ROOT / row["receipt_path"]).read_text(encoding="utf-8"))
        print(f"retained admitted {CLAIM_ID}: {receipt['receipt_hash']}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if CLAIM_ID not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append(
            {"claim_id": CLAIM_ID, "execution_file": f"claims/{CLAIM_ID}/execution.py"}
        )
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), CLAIM_ID, SPEC.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    package = ROOT / "claims" / CLAIM_ID
    write_json(package / "registration.json", claim_registration())
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "measured"
    write_json(experiment_path, experiment)
    census = json.loads(census_path.read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == CLAIM_ID)
    receipt = json.loads((ROOT / row["receipt_path"]).read_text(encoding="utf-8"))
    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text(
        "\n".join(
            (
                f"# {CLAIM_ID}",
                "",
                "Status: `empirically_tested_and_independently_replicated`",
                "",
                "- Exact terminal fraction: `108147617771025486368/253861190227103943729961 = 8 alpha_terminal^2`.",
                "- The external proton scale translates this post-seal to approximately `399.714077 keV`.",
                "- The propagated interval lies within the paper's complete `67-527 keV` analyzed spectrum.",
                "- Approximately `400 keV` is not treated as an exact measured cutoff and no unsupported precision is claimed.",
                "- The Parker range does not select eight channels; the admitted proton colour structure does.",
                f"- Closure: `{certificate['closure_scope']}`",
                f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
                f"- Independent validation: `{certificate['external_validation_hash']}`",
                f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
                f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`",
                f"- Engine receipt: `{receipt['receipt_hash']}`",
                f"- Receipt path: `{row['receipt_path']}`",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(completed.stdout.strip())


if __name__ == "__main__":
    main()
