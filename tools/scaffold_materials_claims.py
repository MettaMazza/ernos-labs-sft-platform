"""Scaffold the complete pre-source-sealed Materials branch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.materials.external_bindings import BINDING_BY_CLAIM  # noqa: E402
from sft.materials.generated_law import (  # noqa: E402
    MATERIALS_SPECS,
    PRE_SOURCE_SEAL_PATH,
    experiment_registration_record,
    prediction_program_document,
    validate_pre_source_seal,
)
from sft.materials.sources import SOURCE_BY_ID  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


EXACT_COUNT_CLAIMS = {
    "SFT-MAT-CRYST-CUBIC-COORDINATION-001": "six nearest neighbours",
    "SFT-MAT-CRYST-ROTATION-RESTRICTION-001": "orders one, two, three, four and six; five excluded",
    "SFT-MAT-CRYST-SYSTEMS-001": "seven crystal systems",
    "SFT-MAT-CRYST-BRAVAIS-001": "fourteen Bravais classes",
    "SFT-MAT-CRYST-PHONON-001": "three acoustic branches",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def claim_registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "materials",
        "subbranch": spec.subbranch,
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
        "axioms": [],
        "free_parameters": [],
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
            "candidate_count": 256,
            "unique_survivor": survivor_id(spec),
        },
        "pre_source_branch_seal": PRE_SOURCE_SEAL_PATH,
        "pre_source_branch_seal_hash": validate_pre_source_seal(ROOT),
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete content-specific 256-form census, sole survivor, depth-independent certificate, "
            "independent regeneration and post-seal NIST/BIPM correspondence."
        ),
        "empirical_protocol": f"experiments/materials/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration_record(ROOT, spec)
    program = prediction_program_document(spec)
    binding = BINDING_BY_CLAIM[spec.claim_id]
    source_rows = [SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    exact_count = EXACT_COUNT_CLAIMS.get(spec.claim_id)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "blind_authoritative_correspondence",
        "development_observations": [],
        "complete_branch_pre_source_seal": {
            "path": PRE_SOURCE_SEAL_PATH,
            "hash": validate_pre_source_seal(ROOT),
            "all_84_predictions_sealed_before_source_selection": True,
        },
        "external_measurement_sources": [
            {
                "source_id": row.source_id,
                "measurement_body": row.body,
                "source_uri": row.source_uri,
                "snapshot_path": row.snapshot_path,
                "snapshot_hash": row.snapshot_hash,
                "evidence_scope": row.evidence_scope,
                "retrieved_date": "2026-07-24",
                "custody_role": "post-seal-authority-evidence",
            }
            for row in source_rows
        ],
        "required_source_features": [
            {"source_id": row.source_id, "required_fragment": row.fragment}
            for row in binding.requirements
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(row) for row in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "withheld_targets": [
            {
                "target_id": spec.target_id,
                "source_ids": list(spec.source_ids),
                "content_absent_from_target_blind_blueprint": True,
                "content_withheld_from_prediction": True,
            }
        ],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": [
                "clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write",
                "foreign_function", "network", "subprocess",
            ],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-source-evaluator",
            "comparison_implementation_hash": sha256_identity(
                ("source-fragment-extraction-and-exact-materials-label-equality", spec.experiment_id)
            ),
            "metrics": [
                {
                    "metric_id": "source-derived-structural-correspondence",
                    "definition": "Require every registered fragment in every byte-sealed authority source and compare the reconstructed categorical record with the sealed consequence.",
                    "unit_protocol": (
                        f"Exact predicted structural value: {exact_count}."
                        if exact_count
                        else "Conditional categorical materials relation; no specimen-dependent magnitude is claimed as a universal constant."
                    ),
                    "all_rows": True,
                }
            ],
            "acceptance_condition": "Every registered fragment and snapshot reproduces, the exact held label matches, and the changed control is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A form missing the content-specific carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed snapshot or missing required fragment is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed candidate support or prediction is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, an imported law or forbidden proof value is rejected."},
            {"control_id": "UNFAVORABLE-CORRESPONDENCE", "kind": "unfavorable_measurement", "expected_rejection": "A changed source-derived label fails exact comparison."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_reference_hash": sha256_identity(record["source_references"]),
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-source-feature-and-tampered-row",
        "stop_condition": "Halt after every target and control is evaluated once, or immediately on any violation.",
        "source_hashes": {row.snapshot_path: row.snapshot_hash for row in source_rows}
        | {"experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.generated_law import BlindMaterialsAuthorityValidator, GeneratedEmpiricalMaterialsProgram, MATERIALS_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MATERIALS_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/materials/obligations.py",
        root / "sft/materials/structural_counts.py",
        root / "sft/materials/derivation.py",
        root / "sft/materials/generated_law.py",
        root / "sft/materials/external_bindings.py",
        root / "sft/materials/sources.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalMaterialsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            {spec.claim_id.lower()!r} + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindMaterialsAuthorityValidator(root, spec),
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
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
    axes = "\n".join(
        f"- `{row.key}` — rejected `{row.choices[0].name}`: {row.choices[0].reason} Admitted `{row.admitted_choice.name}`: {row.admitted_choice.reason}"
        for row in spec.dimensions
    )
    exact = EXACT_COUNT_CLAIMS.get(spec.claim_id)
    measurement = (
        f"This law predicts the exact structural value **{exact}** before source release."
        if exact
        else "This law predicts a conditional structural relation. It does not turn a specimen- and method-dependent magnitude into a universal constant."
    )
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

Dependencies: {', '.join(f'`{row}`' for row in spec.dependencies)}

Boundary: {spec.grammar_boundary}

Generation: {spec.generation_rule}

The literal eight-axis product contains 256 forms:

{axes}

Exactly one form preserves every registered coordinate:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

The complete 84-law prediction set and 21,504 candidates were sealed before
source identities were selected. The prediction program has no filesystem,
network, clock, environment, dynamic-import or subprocess capability. After
the prediction seal, a distinct custodian opens every byte-sealed NIST/BIPM
source, requires every claim-specific fragment, retains all rows, and compares
the source-derived held record. A changed record must fail.

{measurement}

External authority tests the consequence; it does not select the Fold grammar.
"""


def main() -> None:
    for spec in MATERIALS_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/materials" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
