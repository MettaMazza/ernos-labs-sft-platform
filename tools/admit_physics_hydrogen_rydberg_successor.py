#!/usr/bin/env python3
"""Admit and materialize terminal hydrogen Rydberg completion."""

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
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.physics.generated_empirical_law import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.physics.hydrogen_rydberg_successor_laws_v1 import HYDROGEN_RYDBERG_SPEC  # noqa: E402
from sft.physics.hydrogen_rydberg_successor_validation_v1 import (  # noqa: E402
    HYDROGEN_RYDBERG_EMPIRICAL_SPEC,
    SOURCE_HASH,
    SOURCE_ID,
    SOURCE_PATH,
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / HYDROGEN_RYDBERG_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_hydrogen_rydberg_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal hydrogen Rydberg execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    spec = HYDROGEN_RYDBERG_EMPIRICAL_SPEC
    aggregate = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    sources = tuple(aggregate["sources"].values())
    record = experiment_registration_record(spec)
    program = prediction_program_document(spec)
    target_package_hash = sha256_identity(
        (SOURCE_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows))
    )
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": SOURCE_ID, "role": "development_only", "content_hash": SOURCE_HASH}],
        "external_measurement_sources": [
            {
                "source_id": row["source_id"],
                "measurement_body": row["body"],
                "source_uri": row["source_uri"],
                "snapshot_hash": row["snapshot_hash"],
                "retrieved_date": aggregate["retrieval_date"],
                "custody_role": "withheld_target",
            }
            for row in sources
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(dependency) for dependency in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)}],
        "withheld_targets": [
            {"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True}
            for row in spec.target_rows
        ],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001"],
            "external_reference_protocol": "Hash-bound NIST Rydberg, ionization and line rows remain capability-closed while the exact dimensionless hydrogen scale seals; only the post-seal evaluator composes inverse-length units.",
            "proof_value_policy": "positive-generated-counts-and-exact-ratios-only",
            "measurement_record_policy": "external-records-never-become-proof-scalars-or-formal-survivor-selectors",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-rational-source-bound-comparison", spec.experiment_id, spec.falsification_condition)),
            "metrics": [{
                "metric_id": "exact-rational-post-seal-correspondence",
                "definition": "Verify all three source hashes; propagate CODATA and NIST endpoints outward through the sealed scale and immutable line gaps; retain every decision.",
                "unit_protocol": "External inverse-centimetre inscriptions remain source records; only exact positive rational arithmetic enters the evaluator.",
                "all_rows": True,
            }],
            "acceptance_condition": "The scale and ionization intervals are contained, both line intervals overlap, and every tampered row is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Incomplete atomic carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed aggregate or component snapshot is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Changed prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access or forbidden proof value is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "Changed external observation label fails exact comparison."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": target_package_hash,
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-favorable-unfavorable-failed-and-tampered-row",
        "stop_condition": "Halt after every registered source, interval and adverse-control row is evaluated once, or immediately on any violation.",
        "source_hashes": {
            SOURCE_PATH: SOURCE_HASH,
            **{row["snapshot_path"]: row["snapshot_hash"] for row in sources},
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "measured",
    }


def main() -> None:
    spec = HYDROGEN_RYDBERG_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        receipt = read_receipt(ROOT / existing[spec.claim_id]["receipt_path"])
        print(f"retained {spec.claim_id}: {receipt.receipt_hash}")
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            execution.independent_validator,
            execution.source_files,
            execution.empirical_validator,
        )
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), spec.claim_id, spec.exact_result),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    package = ROOT / "claims" / spec.claim_id
    candidate_census = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {
            "boundary": spec.grammar_boundary,
            "completeness_certificate": candidate_census["completeness_certificate_hash"],
            "generator": spec.generation_rule,
        },
        "claim_id": spec.claim_id,
        "dependencies": list(spec.dependencies),
        "empirical_protocol": f"experiments/physics/{HYDROGEN_RYDBERG_EMPIRICAL_SPEC.experiment_id}/registration.json",
        "excluded_inputs": list(spec.exclusions),
        "intended_certificate": f"All {candidate_census['expected_cardinality']:,} typed forms, one survivor, independent exact reconstruction, hostile controls and complete post-seal NIST vector.",
        "provenance_classes": [item.value for item in spec.provenance],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "statement": spec.statement,
        "status": "empirically_tested_and_independently_replicated",
        "title": spec.title,
    })
    experiment_path = ROOT / "experiments/physics" / HYDROGEN_RYDBERG_EMPIRICAL_SPEC.experiment_id / "registration.json"
    experiment_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(experiment_path, experiment_registration())

    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {spec.claim_id}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- Protocol: `observational-data-informed_target-inaccessible_sealed-prediction`",
        "- Observation informed the frozen terminal relation; target-inaccessible execution sealed it before the complete NIST vector was released.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
        f"- Independent validation: `{certificate['external_validation_hash']}`",
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`",
        f"- Engine receipt: `{receipt.receipt_hash}`",
        f"- Receipt path: `{rows[spec.claim_id]['receipt_path']}`", "",
    )), encoding="utf-8")

    survivor = "__".join(axis.survivor.name for axis in spec.axes)
    why = [
        f"# {spec.claim_id}: WHY / DERIVATION / CHECK", "", "## WHY", "", spec.statement, "",
        "Observation informed the explicit frozen law. The measurement vector is then capability-closed; the engine exhausts every target-inaccessible form, selects one survivor and seals the relation; only afterward are the complete NIST records released for exact comparison.",
        "", "## DERIVATION", "", f"Grammar boundary: {spec.grammar_boundary}", "",
        f"The complete {len(spec.axes)}-axis grammar contains {candidate_census['expected_cardinality']:,} forms. Exactly one survives:", "", f"`{survivor}`", "",
    ]
    why.extend(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
    why.extend((
        "", f"Base: {spec.induction_base}", "", f"Successor: {spec.induction_step}", "", f"Exact result: {spec.exact_result}",
        "", "## CHECK", "",
        "- The engine regenerates 1,024 forms and admits exactly one.",
        "- A separate exact implementation reconstructs the proton enclosure and terminal hydrogen interval without source access.",
        "- The terminal scale and absolute ionization are contained in their registered exact intervals.",
        "- The immutable three-quarter and five-thirty-sixth gaps overlap both complete NIST line intervals.",
        "- All three component hashes, uncertainties, displayed-resolution status and adverse control remain visible.",
        "", "## EXCLUSIONS", "",
    ))
    why.extend(f"- {item}" for item in spec.exclusions)
    why.append("")
    (package / "WHY_DERIVATION_CHECK.md").write_text("\n".join(why), encoding="utf-8")
    print(completed.stdout.strip())
    print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
