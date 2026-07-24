"""Scaffold the two atomic-spectrum post-seal comparison packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.atomic_spectra_postseal_validation_v1 import (  # noqa: E402
    CUBIC_VALIDATION_ID,
    HYDROGEN_VALIDATION_ID,
    SOURCE_RECORD_HASH,
    SOURCE_RECORD_PATH,
    VALIDATION_SPECS,
    source_record,
)
from sft.physics.generated_empirical_law import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from tools.scaffold_physics_measurement_claims import (  # noqa: E402
    claim_registration,
    independent_source,
    note,
    write,
)


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_spectra_postseal_validation_v1 import VALIDATION_SPECS, VALIDATOR_BY_ID
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in VALIDATION_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/atomic_spectra_completion_laws_v1.py",
        root / "sft/physics/atomic_spectra_postseal_validation_v1.py",
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
        empirical_validator=VALIDATOR_BY_ID[spec.claim_id](root),
    )
'''


def _source_ids(spec) -> tuple[str, ...]:
    if spec.claim_id == CUBIC_VALIDATION_ID:
        return ("NIST-NCNR-DCS-SUPERFLUID-HELIUM",)
    if spec.claim_id == HYDROGEN_VALIDATION_ID:
        return (
            "NIST-ASD-HYDROGEN-ATOMIC-DATA",
            "NIST-KRAMIDA-HYDROGEN-CRITICAL-COMPILATION-2010-2019",
        )
    raise ValueError(f"unknown atomic validation: {spec.claim_id}")


def experiment_registration(spec) -> dict[str, object]:
    aggregate = source_record(ROOT)
    sources = {row["source_id"]: row for row in aggregate["sources"]}
    selected = tuple(sources[source_id] for source_id in _source_ids(spec))
    record = experiment_registration_record(spec)
    program = prediction_program_document(spec)
    target_package_hash = sha256_identity(
        (SOURCE_RECORD_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows))
    )
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {
                "source_id": "NIST-ATOMIC-SPECTRA-POSTSEAL-SOURCE-RECORD",
                "role": "development_only",
                "content_hash": SOURCE_RECORD_HASH,
            }
        ],
        "external_measurement_sources": [
            {
                "source_id": row["source_id"],
                "measurement_body": row["body"],
                "source_uri": row["source_uri"],
                "snapshot_hash": row["snapshot_hash"],
                "retrieved_date": aggregate["retrieval_date"],
                "custody_role": "withheld_target",
            }
            for row in selected
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
            {
                "input_id": "registered-premise",
                "value_kind": "held-sealed-derivation",
                "content_hash": sha256_identity(spec.dependencies),
            }
        ],
        "withheld_targets": [
            {"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True}
            for row in spec.target_rows
        ],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001"],
            "external_reference_protocol": (
                "Authoritative NIST snapshots are hash-bound in " + SOURCE_RECORD_HASH
                + "; observation informed law formation, but the execution surface cannot access comparison targets before sealing."
            ),
            "proof_value_policy": "positive-generated-counts-and-exact-ratios-only",
            "measurement_record_policy": "external-records-never-become-proof-scalars-or-law-selectors",
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
            "metrics": [
                {
                    "metric_id": "exact-rational-post-seal-correspondence",
                    "definition": "Verify every source hash, evaluate the immutable exact relation, retain every reported interval endpoint, and compare every row after seal release.",
                    "unit_protocol": "External unit inscriptions remain source records; only exact positive rational arithmetic enters the evaluator.",
                    "all_rows": True,
                }
            ],
            "acceptance_condition": "Every registered exact comparison passes and the deliberately changed row is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Incomplete physical carrier is rejected."},
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
        "stop_condition": "Halt after every registered source, target and adverse-control row is evaluated once, or immediately on any violation.",
        "source_hashes": {
            SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
            **{row["snapshot_path"]: row["snapshot_hash"] for row in selected},
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def main() -> None:
    for spec in VALIDATION_SPECS:
        registration = claim_registration(spec)
        registration["provenance_classes"] = ["observational_derivation"]
        registration["registration_date"] = "2026-07-24"
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        disclosure = (
            "\n## Observational-derivation disclosure\n\n"
            "The authoritative records were known during law formation and are disclosed in the source record. "
            "The empirical prediction claim is that the frozen relation is executed by a capability-closed engine "
            "that cannot read the committed targets, seals its trace, and only then permits exact comparison. "
            "No human-ignorance claim is made.\n"
        )
        write(package / "WHY_DERIVATION_CHECK.md", note(spec) + disclosure)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        write(
            ROOT / "experiments/physics" / spec.experiment_id / "registration.json",
            json.dumps(experiment_registration(spec), indent=2) + "\n",
        )
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
