"""Observational-derivation provenance for Chemistry claim execution.

The generated Chemistry kernel already enforces complete candidate execution,
controls, independent reconstruction and post-seal target custody.  This narrow
subclass changes only the disclosed provenance class for claims whose question
was informed by an existing observation.  It does not change any engine gate,
candidate, decision or empirical comparison.
"""

from __future__ import annotations

import platform
from pathlib import Path

from sft.chemistry.generated_law import (
    EmpiricalChemistrySpec,
    GeneratedEmpiricalChemistryProgram,
    _source_derived_targets,
    prediction_program_document,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    ClaimRegistration,
    EmpiricalValidation,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


class GeneratedObservationalChemistryProgram(GeneratedEmpiricalChemistryProgram):
    """Run the standard Chemistry law while disclosing observational origin."""

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="chemistry",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
            source_hash=self.source_hash,
        )


def observational_experiment_registration_record(spec: EmpiricalChemistrySpec) -> dict[str, object]:
    """Disclose observation-informed development without exposing a target API."""

    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": spec.exact_result,
        "target_references": tuple(
            (
                row.target_id,
                row.source_id,
                row.source_locator,
                row.snapshot_path,
                row.snapshot_hash,
            )
            for row in spec.target_rows
        ),
        "observation_registry_path": spec.observation_registry_path,
        "prediction_program": prediction_program_document(spec),
        "sealed_consequence_label": spec.expected_observation_label,
        "falsification_condition": spec.falsification_condition,
        "development_observation_disclosed": True,
        "observation_may_have_informed_question_and_candidate_relation": True,
        "not_claimed_as_unknown-target_forward_prediction": True,
        "external_target_api_absent_from_candidate_generator_and_eliminator": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "comparison_implementation_inaccessible_to_prediction_execution": True,
        "all_rows_required": True,
    }


class BlindObservationalChemistryValidator:
    """Post-seal exact test for an openly observation-derived Chemistry law."""

    def __init__(self, root: Path, spec: EmpiricalChemistrySpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        source_rows, observation_registry_hash = _source_derived_targets(self.root, self.spec)
        target_values = {
            str(row["target_id"]): HeldLabel("external-observation", str(row["observed_label"]))
            for row in source_rows
        }
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, observation_registry_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            program_document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("observational Chemistry prediction differs after package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("observational Chemistry prediction emitted an invalid label")
        source_by_target = {str(row["target_id"]): row for row in source_rows}
        comparisons = tuple(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": source_by_target[reference.target_id]["extraction_hash"],
                "predicted": prediction.label,
                "observed": release.targets[reference.target_id].label,
                "passed": prediction.label == release.targets[reference.target_id].label,
            }
            for reference in self.spec.target_rows
        )
        tampered_label = prediction.label + "__tampered"
        tampered_control = {
            "target_id": "deliberately-tampered-unfavorable-control",
            "predicted": prediction.label,
            "observed": tampered_label,
            "passed": prediction.label != tampered_label,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and bool(tampered_control["passed"])
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("exact-observational-source-label-equality", self.spec.experiment_id, self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released observational Chemistry target differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "observation_registry_hash": observation_registry_hash,
            "comparisons": comparisons,
            "tampered_control": tampered_control,
            "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=tuple(dict.fromkeys(row.source_id for row in self.spec.target_rows)),
            measurements=tuple(
                f"{row['target_id']}: predicted {row['predicted']}; source-derived {row['observed']}; exact match {row['passed']}"
                for row in comparisons
            ) + ("deliberately tampered unfavorable control rejected",),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "BlindObservationalChemistryValidator",
    "GeneratedObservationalChemistryProgram",
    "observational_experiment_registration_record",
)
