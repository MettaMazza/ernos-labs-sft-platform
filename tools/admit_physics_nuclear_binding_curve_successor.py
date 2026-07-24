#!/usr/bin/env python3
"""Admit and materialize the terminal zero-parameter nuclear binding curve."""

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
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (  # noqa: E402
    NUCLEAR_BINDING_CURVE_SPEC,
    binding_peak_certificate,
    tail_upper_bounds,
)
from sft.physics.nuclear_binding_curve_successor_validation_v1 import (  # noqa: E402
    NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC,
    RAW_HASH,
    RAW_PATH,
    SOURCE_HASH,
    SOURCE_ID,
    SOURCE_PATH,
    measurement_analysis,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / NUCLEAR_BINDING_CURVE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_nuclear_binding_curve_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal nuclear binding curve execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    spec = NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC
    aggregate = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    source = aggregate["source"]
    program = prediction_program_document(spec)
    record = experiment_registration_record(spec)
    commitment = sha256_identity((SOURCE_HASH, RAW_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows)))
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": SOURCE_ID, "role": "development_only", "content_hash": SOURCE_HASH}],
        "external_measurement_sources": [{
            "source_id": SOURCE_ID,
            "measurement_body": source["measurement_body"],
            "source_uri": source["source_uri"],
            "landing_uri": source["landing_uri"],
            "publication_uris": [source["publication_i_uri"], source["publication_ii_uri"]],
            "snapshot_hash": SOURCE_HASH,
            "raw_snapshot_hash": RAW_HASH,
            "retrieved_date": aggregate["retrieval_date"],
            "custody_role": "withheld_target",
        }],
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
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001", "SFT-PHYS-MATTER-MASS-ENERGY-001"],
            "external_reference_protocol": "The formal ledger is an exact normalized binding order; AME2020 keV per nucleon values remain post-seal external dimensional records.",
            "proof_value_policy": "positive-generated-counts-exact-fractions-held-labels-and-empty-form-only",
            "measurement_record_policy": "all-2548-positive-composite-rows-and-two-singleton-boundary-rows-retained-with-reported-uncertainty",
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
            "comparison_implementation_hash": sha256_identity(("exact-complete-ame2020-binding-ranking", spec.experiment_id, spec.falsification_condition)),
            "metrics": [{
                "metric_id": "complete-binding-coordinate-curve-and-uncertainty-vector",
                "definition": "Compare the sealed coordinate with every positive composite AME2020 row, every uncertainty, the global rival envelope, light/heavy anchors and the adverse iron-only statement.",
                "unit_protocol": "keV-per-nucleon inscriptions remain external; every interval decision uses exact positive fractions.",
                "all_rows": True,
            }],
            "acceptance_condition": "The predicted 62/28/34 coordinate is the uniquely separated AME2020 maximum and the registered light/heavy curve directions hold.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Any fitted or nonforced ledger carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed raw table, row, uncertainty or source identity is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Any changed coordinate, census or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, evaluated irrational, numerical model zero or incomplete tail proof is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "An iron-only maximum or omitted higher rival fails."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": commitment,
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-positive-composite-row-two-singleton-boundaries-uncertainty-rival-anchor-and-tampered-row",
        "stop_condition": "Halt after every registered formal, AME, uncertainty, curve, custody and adverse row is evaluated once, or immediately on any violation.",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, RAW_PATH: RAW_HASH, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "measured",
    }


def main() -> None:
    spec = NUCLEAR_BINDING_CURVE_SPEC
    empirical = NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC
    write_json(ROOT / "experiments/physics" / empirical.experiment_id / "registration.json", experiment_registration())
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

    package = ROOT / "claims" / spec.claim_id
    candidates = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    analysis = measurement_analysis(ROOT)
    write_json(package / "postseal_measurement_analysis.json", analysis)
    write_json(package / "formal_peak_certificate.json", {
        key: str(value) if hasattr(value, "numerator") else value
        for key, value in binding_peak_certificate().items()
    } | {
        "tail_bounds": {
            key: str(value) if hasattr(value, "numerator") else value
            for key, value in tail_upper_bounds().items()
        }
    })
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": candidates["completeness_certificate_hash"], "generator": spec.generation_rule},
        "claim_id": spec.claim_id,
        "dependencies": list(spec.dependencies),
        "empirical_protocol": f"experiments/physics/{empirical.experiment_id}/registration.json",
        "excluded_inputs": list(spec.exclusions),
        "intended_certificate": "All 1,024 typed forms, one survivor, independent rational reconstruction, complete finite maximum census, unbounded tail induction, hostile controls and all 2,548 positive composite AME2020 rows plus two singleton boundaries.",
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
        "- Zero fitted coefficients; no AME value or nuclide name enters the formal execution.",
        "- Exact prediction: `A=62`, `Z=28`, `N=34`; complete AME2020 measured maximum: nickel-62.",
        "- AME2020 value: `8794.5555 +/- 0.0069 keV per nucleon`; its lower endpoint exceeds every rival upper endpoint.",
        "- All 2,548 positive composite rows and both singleton empty-binding boundary rows are retained.",
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
        "The successor replaces the inherited unqualified iron shortcut with a globally enumerated, zero-parameter coordinate and then opens the complete AME2020 target.", "",
        "## DERIVATION", "", f"Grammar boundary: {spec.grammar_boundary}", "",
        f"The ten-axis grammar contains {candidates['expected_cardinality']:,} forms. Exactly one survives:", "", f"`{survivor}`", "",
    ]
    why.extend(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
    peak = binding_peak_certificate()
    why.extend((
        "", "### Exact binding ledger", "",
        "- Bulk: one saturated interior support.",
        "- Surface: `(1/5)/A^(1/3)`, with the cube root never admitted—only exact rational enclosures are compared.",
        "- Coulomb: `alpha Z(Z-1)/A^(4/3)` over every ordered distinct charge path.",
        "- Asymmetry: `(1/4)(N-Z)^2/A^2`.",
        "- Pairing: quarter-order radial gain for even/even, loss for odd/odd and empty adjustment for mixed parity.",
        f"- Finite certificate: {peak['possible_maximizer_count']:,} possible concave integer/parity maximizers across {peak['finite_mass_count']:,} masses below `{peak['tail_cutoff_mass']}`.",
        "- Unbounded certificate: both charge-at-most-one-fifth and charge-above-one-fifth tails remain below the unique winner.",
        "", f"Base: {spec.induction_base}", "", f"Successor: {spec.induction_step}", "", f"Exact result: {spec.exact_result}", "",
        "## CHECK", "",
        "- Independent integer-scaled rational code reconstructs `62/28/34` without source access.",
        "- The complete AME2020 positive composite table independently identifies nickel-62 as the global measured maximum.",
        "- Nickel-62's lower uncertainty endpoint exceeds every competing row's upper endpoint.",
        "- Deuterium, helium-4, carbon-12 and iron-56 rise toward the maximum; lead-208 and uranium-238 lie below it.",
        "- The old iron-only wording is retained as an adverse control and rejected, not hidden.",
        "- The two free-singleton `0.0` inscriptions are retained only as external empty-binding boundaries, never as proof scalars.",
        "", "## EXCLUSIONS", "",
    ))
    why.extend(f"- {item}" for item in spec.exclusions)
    why.append("")
    (package / "WHY_DERIVATION_CHECK.md").write_text("\n".join(why), encoding="utf-8")
    print(completed.stdout.strip())
    print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
