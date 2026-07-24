#!/usr/bin/env python3
"""Admit and materialize terminal nucleon-binding completion."""

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
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.physics.nucleon_binding_successor_laws_v1 import NUCLEON_BINDING_SPEC  # noqa: E402
from sft.physics.nucleon_binding_successor_validation_v1 import (  # noqa: E402
    NUCLEON_BINDING_EMPIRICAL_SPEC,
    NIST_CODATA_HASH,
    PDG_QUARK_MASS_HASH,
    SOURCE_HASH,
    SOURCE_ID,
    SOURCE_PATH,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / NUCLEON_BINDING_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_nucleon_binding_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal nucleon-binding execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    spec = NUCLEON_BINDING_EMPIRICAL_SPEC
    aggregate = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    program = prediction_program_document(spec)
    record = experiment_registration_record(spec)
    commitment = sha256_identity((SOURCE_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows)))
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
                "snapshot_hash": row.get("snapshot_hash", SOURCE_HASH),
                "retrieved_date": aggregate["retrieval_date"],
                "custody_role": "withheld_target",
            }
            for row in aggregate["sources"].values()
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)}],
        "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True} for row in spec.target_rows],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001"],
            "external_reference_protocol": "PDG MSbar masses and NIST MeV inscriptions remain external records; formal execution uses only normalized exact Fold carriers.",
            "proof_value_policy": "positive-generated-counts-exact-ratios-held-labels-and-empty-neutral-form-only",
            "measurement_record_policy": "external-records-never-become-proof-scalars-or-formal-survivor-selectors",
            "nonconflation_policy": "the exact 1/128 structural cell is not asserted equal to a scheme-dependent current-quark mass ratio",
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
            "comparison_implementation_hash": sha256_identity(("exact-nucleon-binding-comparison", spec.experiment_id, spec.falsification_condition)),
            "metrics": [{
                "metric_id": "complete-composition-dominance-ordering-vector",
                "definition": "Compare every registered colour/composition, scheme, dominance, nonconflation, d/u ordering, nucleon interval and direct-difference row exactly.",
                "unit_protocol": "External MeV units remain source records; all interval and fraction decisions use exact positive fractions.",
                "all_rows": True,
            }],
            "acceptance_condition": "Every registered composition, strict inequality, scheme disclosure, uncertainty endpoint and ordering row passes while structural/current-mass nonconflation remains explicit.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Incomplete colour, ledger or ordering carriers are rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed source record or bound snapshot is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Changed prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, fitted mass terms or forbidden proof values are rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "A one-percent boundary crossing, ordering reversal or interval overlap fails."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": commitment,
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-favorable-unfavorable-failed-and-tampered-row",
        "stop_condition": "Halt after every registered composition, interval, disclosure and control row is evaluated once, or immediately on any violation.",
        "source_hashes": {
            SOURCE_PATH: SOURCE_HASH,
            aggregate["sources"]["pdg_light_quark_masses"]["snapshot_path"]: PDG_QUARK_MASS_HASH,
            aggregate["sources"]["nist_nucleon_masses"]["snapshot_path"]: NIST_CODATA_HASH,
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "measured",
    }


def main() -> None:
    spec = NUCLEON_BINDING_SPEC
    empirical = NUCLEON_BINDING_EMPIRICAL_SPEC
    experiment_path = ROOT / "experiments/physics" / empirical.experiment_id / "registration.json"
    write_json(experiment_path, experiment_registration())
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        receipt = read_receipt(ROOT / existing[spec.claim_id]["receipt_path"])
        print(f"retained {spec.claim_id}: {receipt.receipt_hash}")
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), spec.claim_id, spec.exact_result),
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    package = ROOT / "claims" / spec.claim_id
    candidates = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": candidates["completeness_certificate_hash"], "generator": spec.generation_rule},
        "claim_id": spec.claim_id,
        "dependencies": list(spec.dependencies),
        "empirical_protocol": f"experiments/physics/{empirical.experiment_id}/registration.json",
        "excluded_inputs": list(spec.exclusions),
        "intended_certificate": "All 4,096 typed forms, one survivor, independent reconstruction, hostile controls and complete PDG/NIST composition-dominance-ordering vector.",
        "provenance_classes": [item.value for item in spec.provenance],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "statement": spec.statement,
        "status": "empirically_tested_and_independently_replicated",
        "title": spec.title,
    })

    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {spec.claim_id}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- Protocol: `observational-data-informed_target-inaccessible_sealed-prediction`",
        "- Structural 1/128 and the PDG scheme-dependent current-quark fraction remain explicitly non-identical comparison objects.",
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
        "Observation informed the explicit law; target-inaccessible enumeration and sealing precede the complete PDG/NIST release.", "",
        "## DERIVATION", "", f"Grammar boundary: {spec.grammar_boundary}", "",
        f"The twelve-axis grammar contains {candidates['expected_cardinality']:,} forms. Exactly one survives:", "", f"`{survivor}`", "",
    ]
    why.extend(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
    why.extend((
        "", f"Base: {spec.induction_base}", "", f"Successor: {spec.induction_step}", "", f"Exact result: {spec.exact_result}", "",
        "## CHECK", "",
        "- Independent code reconstructs the colour cycle, exact charge words, depth-seven ledger and rational quark-root ordering.",
        "- PDG independently retains three colours, qqq singlets and complete scheme-bound u/d uncertainty intervals.",
        "- Both structural and PDG uud current-mass ledgers pass the strict below-one-percent/above-ninety-nine-percent dominance class without being conflated.",
        "- NIST proton, neutron and direct mass-difference intervals preserve the sealed neutron-heavier ordering.",
        "", "## EXCLUSIONS", "",
    ))
    why.extend(f"- {item}" for item in spec.exclusions)
    why.append("")
    (package / "WHY_DERIVATION_CHECK.md").write_text("\n".join(why), encoding="utf-8")
    print(completed.stdout.strip())
    print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
