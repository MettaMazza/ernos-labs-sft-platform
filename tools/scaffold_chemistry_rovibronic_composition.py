#!/usr/bin/env python3
"""Scaffold the Chemistry rovibronic-composition claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.generated_law import prediction_program_document  # noqa: E402
from sft.chemistry.generated_observational_law import observational_experiment_registration_record  # noqa: E402
from sft.chemistry.rovibronic_composition_batch import ROVIBRONIC_COMPOSITION_SPEC, SOURCE_HASH, SOURCE_PATH  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record  # noqa: E402
from sft.physics.molecular_spectroscopy_successor_validation_v1 import authoritative_record  # noqa: E402
from tools.scaffold_chemistry_ready_claims import independent_source, note  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
            "Complete 256-form molecular joint-state census, sole survivor, depth-independent successor, "
            "implementation-distinct regeneration and full post-seal NIST H2/D2 exact-ratio vector."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = authoritative_record(ROOT)
    registration = observational_experiment_registration_record(spec)
    program = prediction_program_document(spec)
    source_rows = record["sources"]
    external_sources = [
        {
            "source_id": row["source_id"],
            "measurement_body": row["body"],
            "source_uri": row["source_uri"],
            "snapshot_hash": row["snapshot_hash"],
            "retrieved_date": record["retrieval_date"],
            "custody_role": "withheld_target",
        }
        for row in source_rows.values()
    ]
    target_commitment_hash = sha256_identity(
        tuple((row.target_id, row.source_id, row.source_locator, row.snapshot_hash) for row in spec.target_rows)
    )
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {"source_id": spec.target_rows[0].source_id, "role": "development_only", "content_hash": SOURCE_HASH}
        ],
        "external_measurement_sources": external_sources,
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
            "derived_dimension_carriers": [
                "positive molecular-state occurrence counts",
                "positive vibrational and rotational recurrence counts",
                "held isotope, spin and observation labels",
                "exact positive molecular-spectroscopy ratios inherited from the admitted Physics receipt",
            ],
            "external_reference_protocol": "The H2/D2 component records remain capability-closed until the Chemistry prediction seals; the custodian then checks all four exact ratio intervals and all structural hierarchy rows.",
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
            "evaluator_id": spec.experiment_id + "-post-seal-NIST-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-H2-D2-ratio-interval-and-held-label-comparison", spec.experiment_id)),
            "metrics": [
                {
                    "metric_id": "complete-H2-D2-exact-ratio-vector",
                    "definition": "Check every displayed source endpoint, all four sealed exact ratios, both state hierarchies, the isotope direction and a deliberately changed row.",
                    "unit_protocol": "NIST inverse-centimetre and angstrom inscriptions remain source records; the evaluator uses exact positive rational interval propagation.",
                    "all_rows": True,
                }
            ],
            "acceptance_condition": "All four exact ratios are contained, both hierarchy rows and the isotope direction hold, and the tampered row rejects.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A form lacking the identified molecular carrier rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed aggregate or component source identity rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A missing, duplicate or additional survivor rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, imported molecular model, forbidden proof value or free exception rejects."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "A changed external state label or ratio fails exact comparison."},
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
        "stop_condition": "Halt after every source, ratio, hierarchy and adverse row is evaluated once, or immediately on any violation.",
        "source_hashes": {
            SOURCE_PATH: SOURCE_HASH,
            **{row["snapshot_path"]: row["snapshot_hash"] for row in source_rows.values()},
            "observational-experiment-registration-record": sha256_identity(registration),
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
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rovibronic_composition_batch import ROVIBRONIC_COMPOSITION_SPEC
from sft.chemistry.rovibronic_composition_validation import RovibronicCompositionValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = ROVIBRONIC_COMPOSITION_SPEC
    source_files = (
        root / "sft/chemistry/electronic_structure_derivation.py",
        root / "sft/chemistry/rovibronic_composition_derivation.py",
        root / "sft/chemistry/rovibronic_composition_batch.py",
        root / "sft/chemistry/rovibronic_composition_validation.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/molecular_spectroscopy_successor_laws_v1.py",
        root / "sft/physics/molecular_spectroscopy_successor_validation_v1.py",
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
        empirical_validator=RovibronicCompositionValidator(root),
    )
'''


def main() -> None:
    spec = ROVIBRONIC_COMPOSITION_SPEC
    package = ROOT / "claims" / spec.claim_id
    write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source(spec))
    write(package / "independent_validator.py", independent_source(spec))
    write(package / "WHY_DERIVATION_CHECK.md", note(spec).replace(
        "This is categorical authoritative correspondence, not a claim that a term definition is a measured numerical constant.",
        "This is an openly observation-derived molecular-state law. Its quantitative check retains all four exact H2/D2 ratio intervals, but it does not claim absolute bond lengths or absolute spectroscopy constants."
    ))
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment = ROOT / "experiments/chemistry" / spec.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
    print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
