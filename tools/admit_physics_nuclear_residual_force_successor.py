#!/usr/bin/env python3
"""Admit and materialize terminal residual nuclear-interaction closure."""

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
from sft.physics.nuclear_residual_force_successor_laws_v1 import NUCLEAR_RESIDUAL_FORCE_SPEC  # noqa: E402
from sft.physics.nuclear_residual_force_successor_validation_v1 import (  # noqa: E402
    NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC,
    SOURCE_HASH,
    SOURCE_ID,
    SOURCE_PATH,
    measurement_analysis,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / NUCLEAR_RESIDUAL_FORCE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_nuclear_residual_force_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal residual nuclear-force execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    spec = NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC
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
                "snapshot_hash": SOURCE_HASH,
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
            "external_reference_protocol": "PDG MeV, NIST MeV-fm and NIST barn inscriptions remain external records; formal execution uses exact normalized carriers only.",
            "proof_value_policy": "positive-generated-counts-exact-fractions-held-labels-and-empty-form-only",
            "measurement_record_policy": "external-records-never-become-proof-scalars-formal-survivor-selectors-or-universal-quarter-strengths",
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
            "comparison_implementation_hash": sha256_identity(("exact-nuclear-residual-range-comparison", spec.experiment_id, spec.falsification_condition)),
            "metrics": [{
                "metric_id": "complete-residual-range-and-scattering-vector",
                "definition": "Compare every mediator mass/range, conversion, scattering interval, channel difference, context scope and unfavorable universal-strength row exactly.",
                "unit_protocol": "Dimensional inscriptions remain external records; interval propagation and reciprocal ordering use exact positive fractions.",
                "all_rows": True,
            }],
            "acceptance_condition": "Residual interaction evidence remains positive, pion ranges remain above vector ranges, channel dependence is retained and quarter-One is not relabelled as a measured strength.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Raw colour or first-order external exchange is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed mass, conversion, scattering or context row is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Changed prediction or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, a fitted profile or forbidden proof values are rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "Conflating quarter-One with a universal measured strength or hiding channel dependence fails."},
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
        "stop_condition": "Halt after every residual, mass, range, scattering, context and custody row is evaluated once, or immediately on any violation.",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "measured",
    }


def main() -> None:
    spec = NUCLEAR_RESIDUAL_FORCE_SPEC
    empirical = NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC
    write_json(ROOT / "experiments/physics" / empirical.experiment_id / "registration.json", experiment_registration())
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
    write_json(package / "postseal_measurement_analysis.json", measurement_analysis(ROOT))
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": candidates["completeness_certificate_hash"], "generator": spec.generation_rule},
        "claim_id": spec.claim_id,
        "dependencies": list(spec.dependencies),
        "empirical_protocol": f"experiments/physics/{empirical.experiment_id}/registration.json",
        "excluded_inputs": list(spec.exclusions),
        "intended_certificate": "All 1,024 typed forms, one survivor, independent reconstruction, hostile controls and complete PDG/NIST mediator-range/scattering evidence including the adverse universal-strength control.",
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
        "- Quarter-One is the exact structural residual order, not a universal measured nuclear-force coefficient.",
        "- Complete PDG/NIST mass, range, scattering and channel-dependence rows are retained.",
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
        "Observation informed the explicit law; target-inaccessible enumeration and sealing precede release of the complete PDG/NIST vector.", "",
        "## DERIVATION", "", f"Grammar boundary: {spec.grammar_boundary}", "",
        f"The ten-axis grammar contains {candidates['expected_cardinality']:,} forms. Exactly one survives:", "", f"`{survivor}`", "",
    ]
    why.extend(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
    why.extend((
        "", f"Base: {spec.induction_base}", "", f"Successor: {spec.induction_step}", "", f"Exact result: {spec.exact_result}", "",
        "## CHECK", "",
        "- Independent code reconstructs paired half-One support and positive reciprocal ordering without source access.",
        "- NIST hydrogen and deuterium scattering intervals are both positive, supporting a nonempty external interaction.",
        "- Their disjoint strengths close the universal-quarter interpretation as false while preserving quarter-One as the exact structural order.",
        "- Complete PDG mass intervals and NIST conversion force the pion range envelope above rho/omega, with every uncertainty retained.",
        "- The finite reciprocal range is a scale, never a hard numerical-zero cutoff.",
        "", "## EXCLUSIONS", "",
    ))
    why.extend(f"- {item}" for item in spec.exclusions)
    why.append("")
    (package / "WHY_DERIVATION_CHECK.md").write_text("\n".join(why), encoding="utf-8")
    print(completed.stdout.strip())
    print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
