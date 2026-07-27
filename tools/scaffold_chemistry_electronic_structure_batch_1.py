#!/usr/bin/env python3
"""Scaffold the first full-discipline molecular-electronic Chemistry claim."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.electronic_structure_batch_1 import ELECTRONIC_STRUCTURE_BATCH_1_SPECS  # noqa: E402
from sft.chemistry.generated_law import prediction_program_document  # noqa: E402
from sft.chemistry.generated_observational_law import observational_experiment_registration_record  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record  # noqa: E402
from tools.scaffold_chemistry_ready_claims import independent_source, note  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def source_record(source_id: str) -> dict[str, object]:
    registry = json.loads((ROOT / "experiments/external_sources/chemistry/authoritative_sources.json").read_text(encoding="utf-8"))
    matches = [row for row in registry["sources"] if row.get("source_id") == source_id]
    if len(matches) != 1:
        raise ValueError(f"Chemistry source identity is not unique: {source_id}")
    return matches[0]


def claim_registration(spec) -> dict[str, object]:
    return {
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete 256-form molecular-electronic census, sole survivor, depth-independent successor, "
            "implementation-distinct regeneration and disclosed observational post-seal correspondence."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = observational_experiment_registration_record(spec)
    program = prediction_program_document(spec)
    source = source_record(spec.target_rows[0].source_id)
    target_commitment_hash = sha256_identity(
        tuple((row.target_id, row.source_id, row.source_locator, row.snapshot_hash) for row in spec.target_rows)
    )
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {"source_id": spec.target_rows[0].source_id, "role": "development_only", "content_hash": spec.target_rows[0].snapshot_hash}
        ],
        "external_measurement_sources": [
            {
                "source_id": spec.target_rows[0].source_id,
                "measurement_body": source["body"],
                "source_uri": source["source_uri"],
                "snapshot_hash": spec.target_rows[0].snapshot_hash,
                "retrieved_date": "2026-07-26",
                "custody_role": "withheld_target",
            }
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(value) for value in spec.dependencies],
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
            "derived_dimension_carriers": ["finite molecular carrier", "positive electron-occurrence count", "held spin and electronic-support labels"],
            "external_reference_protocol": "IUPAC identifies the observed class during development; its byte snapshot and normalized target remain inaccessible to prediction execution and are compared only after the derivation seal.",
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
            "evaluator_id": spec.experiment_id + "-post-seal-source-evaluator",
            "comparison_implementation_hash": sha256_identity(("observational-source-fragment-extraction", spec.experiment_id)),
            "metrics": [
                {
                    "metric_id": "source-derived-structural-correspondence",
                    "definition": "Reconstruct every registered feature from the byte-sealed official definition and compare it exactly with the sealed Fold consequence.",
                    "unit_protocol": "Categorical structural observation; no numerical measurement is claimed by this prerequisite.",
                    "all_rows": True,
                }
            ],
            "acceptance_condition": "Every registered source-derived row matches and the deliberately changed row is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A state lacking an identified molecular carrier rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed IUPAC snapshot or required fragment rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A missing, duplicate or additional survivor rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, an imported electronic model, forbidden proof value or free rule rejects."},
            {"control_id": "UNFAVORABLE-CORRESPONDENCE", "kind": "unfavorable_measurement", "expected_rejection": "A changed external feature label fails exact comparison."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": target_commitment_hash,
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-registered-favorable-unfavorable-failed-and-tampered-row",
        "stop_condition": "Halt after every target and control is evaluated once, or immediately on any violation.",
        "source_hashes": {
            spec.target_rows[0].snapshot_path: spec.target_rows[0].snapshot_hash,
            spec.observation_registry_path: hash_file(ROOT / spec.observation_registry_path),
            "observational-experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.electronic_structure_batch_1 import ELECTRONIC_STRUCTURE_BATCH_1_SPECS
from sft.chemistry.generated_observational_law import BlindObservationalChemistryValidator, GeneratedObservationalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in ELECTRONIC_STRUCTURE_BATCH_1_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/chemistry/electronic_structure_derivation.py",
        root / "sft/chemistry/electronic_structure_batch_1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "claims/{spec.claim_id}/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            "{spec.claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindObservationalChemistryValidator(root, spec),
    )
'''


def main() -> None:
    for spec in ELECTRONIC_STRUCTURE_BATCH_1_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        narrative = note(spec).replace(
            "The prediction specification contains the public source and snapshot identities,",
            "The IUPAC observation that motivated this question is disclosed. Its target adapter and comparison content remain inaccessible to prediction execution,",
        ).replace(
            "This is categorical authoritative correspondence, not a claim that a term definition is a measured numerical constant.",
            "This is an openly observationally derived categorical prerequisite, not an unknown-target forward prediction and not a numerical-value claim.",
        )
        write(package / "WHY_DERIVATION_CHECK.md", narrative)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
