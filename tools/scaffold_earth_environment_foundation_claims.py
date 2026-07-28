#!/usr/bin/env python3
"""Scaffold all 74 pre-source-sealed Earth foundation claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.earth_environment.empirical_program import (  # noqa: E402
    EARTH_SPECS,
    PRE_SOURCE_SEAL_PATH,
    experiment_registration_record,
    prediction_program_document,
    validate_external_evidence,
    validate_pre_source_seal,
)
from sft.earth_environment.external_bindings import (  # noqa: E402
    BINDINGS_PATH,
    EXTERNAL_TARGETS_PATH,
    SOURCE_FEATURE_AUDIT_PATH,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


CHECKPOINT = ROOT / "census/earth_environment_continuation_checkpoint.json"
EXACT_RESULTS = {
    "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001": "The generated size-count grammar uniquely selects exponent 1. The first mixed USGS catalogue was adverse (N≥5/N≥6 = 18469/1494); the separately preregistered homogeneous mww holdout was compatible (N≥6/N≥7 = 253/27, exact exceedance 27/253; registered interval 0.085657503235220589–0.13089188889528297 contains 1/10).",
    "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001": "A bounded cavity forces distinct recurrence modes; no dimensional resonance frequency is imported as a proof value. Primary measurement evidence supplies the separate dimensional observation boundary.",
    "SFT-EARTH-EARTH-SYSTEM-TIPPING-001": "The exact two-basin Fold witness forces distinguishable basins with a shared image; it does not manufacture a universal dimensional or one-half physical tipping threshold.",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def claim_registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "earth_environment",
        "subbranch": spec.family,
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
        "intended_certificate": "Complete claim-specific 256-form census, unique survivor, depth-independent structural certificate, implementation-distinct reconstruction, and post-seal purpose-matched Earth evidence comparison retaining every adverse, absent, unresolved and failed row.",
        "empirical_protocol": f"experiments/earth_environment/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-28",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration_record(ROOT, spec)
    audit, targets, bindings = validate_external_evidence(ROOT)
    target = next(row for row in targets["targets"] if row["claim_id"] == spec.claim_id)
    program = prediction_program_document(spec)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "post_seal_purpose_matched_authoritative_observation_or_primary_measurement_boundary_correspondence",
        "development_observations": [],
        "complete_branch_pre_source_seal": {
            "path": PRE_SOURCE_SEAL_PATH,
            "hash": validate_pre_source_seal(ROOT),
            "all_74_predictions_and_18944_candidates_sealed_before_source_selection": True,
        },
        "external_target_record": {
            "path": EXTERNAL_TARGETS_PATH,
            "hash": targets["targets_hash"],
            "target_id": target["target_id"],
            "source_ids": list(spec.source_ids),
            "directness": spec.directness,
            "empirical_disposition": spec.empirical_disposition,
            "source_evidence": target["source_evidence"],
            "numeric_comparison": target["numeric_comparison"],
        },
        "evidence_census": {
            "bindings_path": BINDINGS_PATH,
            "bindings_hash": bindings["bindings_hash"],
            "feature_audit_path": SOURCE_FEATURE_AUDIT_PATH,
            "feature_audit_hash": audit["audit_hash"],
            "registered_features": audit["registered_feature_count"],
            "present_features": audit["present_feature_count"],
            "absent_features_preserved": audit["absent_feature_count"],
            "failed_transports_preserved": audit["failed_transports_preserved"],
        },
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_structural_law": True,
        },
        "withheld_targets": [{"target_id": spec.target_id, "source_ids": list(spec.source_ids), "content_withheld_from_claim_prediction_until_derivation_seal": True}],
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program": program,
            "program_hash": sha256_identity(program),
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-source-evaluator",
            "metrics": [{"metric_id": "source-derived-boundary-correspondence", "definition": "Reconstruct the registered Earth evidence consequence while preserving every source feature, adverse result, absence, unresolved row and failed transport, then compare with the sealed claim consequence.", "all_rows": True}],
            "acceptance_condition": "Every source identity and snapshot reproduces; evidence classes remain explicit; the source-derived consequence matches; every adverse, absent and failed row remains; and a changed control is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A form missing the complete Earth carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed source, capture, manifest or result is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed candidate support, target row or prediction is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, an imported model, a forbidden proof value or a fitted parameter is rejected."},
            {"control_id": "UNFAVORABLE-CONSEQUENCE", "kind": "unfavorable_measurement", "expected_rejection": "A changed external consequence label fails exact comparison."},
        ],
        "custody_protocol": {"custodian_id": spec.experiment_id + "-external-target-custodian", "custodian_distinct_from_executor": True, "release_requires_matching_seal": True},
        "target_access_policy": "structurally-denied-before-claim-derivation-seal",
        "row_retention_policy": "retain every registered feature, favorable, adverse, absent, mixed, unresolved, censored, missing and transport row",
        "stop_condition": "Halt after the target and controls are evaluated once, or immediately on any violation.",
        "registration_record_hash": sha256_identity(record),
        "registration_date": "2026-07-28",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.earth_environment.empirical_program import BlindEarthBoundaryValidator, EARTH_SPECS, GeneratedEmpiricalEarthProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in EARTH_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/earth_environment/obligations.py",
        root / "sft/earth_environment/structural_model.py",
        root / "sft/earth_environment/generated_law.py",
        root / "sft/earth_environment/external_bindings.py",
        root / "sft/earth_environment/empirical_program.py",
        root / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json",
        root / "experiments/earth_environment/source_registry.json",
        root / "experiments/earth_environment/claim_source_bindings.json",
        root / "experiments/earth_environment/source_feature_audit.json",
        root / "experiments/earth_environment/claim_specific_external_targets.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_protocol.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_result.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_holdout_protocol_v2.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_holdout_result_v2.json",
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
        program=GeneratedEmpiricalEarthProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator({spec.claim_id.lower()!r} + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindEarthBoundaryValidator(root, spec),
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct product validator for {spec.claim_id}."""
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
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {{row: row == SURVIVOR for row in generated}} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {{"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}}}, sort_keys=True))
if __name__ == "__main__": main()
'''


def note(spec) -> str:
    axes = "\n".join(f"- `{row.key}` — reject `{row.choices[0].name}`: {row.choices[0].reason} Admit `{row.admitted_choice.name}`: {row.admitted_choice.reason}" for row in spec.dimensions)
    special = EXACT_RESULTS.get(spec.claim_id, "The result is the unique eight-coordinate preserving Earth form. Site-, time-, method- and instrument-dependent dimensional records remain empirical records rather than proof parameters.")
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

All 74 Earth predictions and 18,944 candidate forms were sealed before source selection. The capability-closed prediction has no filesystem, network, clock, environment or target capability. A distinct post-seal custodian opens the complete registered target row and preserves all source features, adverse boundaries, absences, unresolved rows and transport failures.

Evidence classification: `{spec.directness}` / `{spec.empirical_disposition}`.

{special}

External evidence tests the sealed consequence and never selects the structural law. A model, forecast, retrieval or proxy is never relabelled as direct observation.
"""


def main() -> None:
    for spec in EARTH_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/earth_environment" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "complete_claim_packages_and_independent_validators_scaffolded_not_admitted",
        "claim_package_count": len(EARTH_SPECS),
        "independent_validator_count": len(EARTH_SPECS),
        "next_exact_operation": f"admit_{EARTH_SPECS[0].claim_id}",
    })
    write(CHECKPOINT, json.dumps(checkpoint, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
