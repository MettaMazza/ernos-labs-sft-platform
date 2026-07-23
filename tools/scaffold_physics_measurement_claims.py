"""Materialize the nine empirical measurement/metrology claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import (  # noqa: E402
    completeness_record,
    experiment_registration_record,
    prediction_program_document,
    survivor_id,
)
from sft.physics.measurement_laws import MEASUREMENT_SPECS  # noqa: E402

EXTERNAL_REGISTRY = json.loads(
    (ROOT / "experiments/external_sources/physics/authoritative_sources.json").read_text(encoding="utf-8")
)
EXTERNAL_BY_ID = {row["source_id"]: row for row in EXTERNAL_REGISTRY["sources"]}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def claim_registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "physics",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": "Complete 256-form census, sole survivor, independent regeneration and blind post-seal external comparison.",
        "empirical_protocol": f"experiments/physics/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-23",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration_record(spec)
    program = prediction_program_document(spec)
    program_hash = sha256_identity(program)
    target_package_hash = sha256_identity(
        (spec.source_snapshot_hash, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows))
    )
    external = EXTERNAL_BY_ID[spec.target_rows[0].source_id]
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "blind_empirical_test",
        "development_observations": [],
        "external_measurement_sources": [
            {
                "source_id": spec.target_rows[0].source_id,
                "measurement_body": external["body"],
                "source_uri": external["source_uri"],
                "snapshot_hash": spec.source_snapshot_hash,
                "retrieved_date": "2026-07-23",
                "custody_role": "withheld_target",
            }
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(dependency) for dependency in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [
            {"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)}
        ],
        "withheld_targets": [
            {"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True}
            for row in spec.target_rows
        ],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001" if "DIMENSION-COMPOSITION" not in spec.claim_id else "SFT-PHYS-MEAS-QUANTITY-CARRIER-001"],
            "external_reference_protocol": f"{external['body']} snapshot {spec.source_snapshot_hash}; used only after prediction sealing.",
            "proof_value_policy": "positive-generated-counts-and-exact-ratios-only",
            "measurement_record_policy": "external-records-never-become-proof-scalars-or-law-selectors",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": program_hash,
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-held-label-equality", spec.experiment_id, spec.falsification_condition)),
            "metrics": [
                {"metric_id": "exact-held-label-correspondence", "definition": "Compare every registered predicted structural label with its committed external observation label by exact identity.", "unit_protocol": "Structural metrology correspondence; external unit inscriptions remain records.", "all_rows": True}
            ],
            "acceptance_condition": "Every registered external row matches and the deliberately changed row is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Incomplete physical carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Changed BIPM snapshot identity is rejected."},
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
        "stop_condition": "Halt after every registered target and adverse-control row is evaluated once, or immediately on any violation.",
        "source_hashes": {
            spec.source_snapshot_path: spec.source_snapshot_hash,
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-23",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator, GeneratedEmpiricalPhysicsProgram
from sft.physics.measurement_laws import MEASUREMENT_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MEASUREMENT_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measurement_laws.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {spec.claim_id.lower()!r} + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExternalMeasurementValidator(root, spec),
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Independent product validator for {spec.claim_id}."""
from itertools import product
import json
import sys
CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and
              sealed["census"]["expected_cardinality"] == len(generated) and
              len(set(received)) == len(generated) and
              decisions == {{row: row == SURVIVOR for row in generated}} and
              sum(decisions.values()) == 1 and
              sealed["closure"]["scope"] == "depth_independent" and
              sealed["closure"]["minimality_passed"] is True and
              sealed["closure"]["named_shape_uniqueness_passed"] is True and
              {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}} and
              all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True,
                      "passed": passed, "certificate": {{"claim_id": CLAIM_ID, "candidate_count": len(generated),
                      "survivor": SURVIVOR if passed else None}}}}, sort_keys=True))
if __name__ == "__main__": main()
'''


def note(spec) -> str:
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## Why and derivation

{spec.statement}

The complete registered eight-axis product contains 256 forms. Exactly one form
retains the complete Fold carrier, the forced relation, source-bound proof,
capability-closed prediction, a separate measurement record, all rows, a
One/successor certificate and no extra rule:

`{survivor_id(spec)}`

The exact result is:

> {spec.exact_result}

The base certificate is: {spec.induction_base}

The successor certificate is: {spec.induction_step}

## Blind external check

The target custodian commits {len(spec.target_rows)} externally sourced rows before the Fold
prediction runs. The predictor receives only the sealed derivation premise and
has no filesystem, network, process, clock, environment, import or foreign-
function instruction. After sealing, the evaluator opens every committed row,
performs the registered exact label comparison and rejects a deliberately
changed unfavorable row. Any omitted or mismatched row falsifies the registered
claim boundary.

This correspondence does not allow the external body to select the Fold relation
and does not convert a reported decimal inscription into a proof value.
"""


def main() -> None:
    for spec in MEASUREMENT_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/physics" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
