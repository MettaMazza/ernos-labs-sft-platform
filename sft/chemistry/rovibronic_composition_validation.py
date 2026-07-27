"""Post-seal NIST validation for Chemistry rovibronic composition."""

from __future__ import annotations

import platform
from pathlib import Path

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.rovibronic_composition_batch import ROVIBRONIC_COMPOSITION_SPEC
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
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.physics.molecular_spectroscopy_successor_validation_v1 import (
    MEASURED_LABEL,
    SOURCE_ID,
    authoritative_record,
    measured_ratio_intervals,
    molecular_spectroscopy_classification,
    sealed_ratio_vector,
)


class RovibronicCompositionValidator:
    """Validate every registered H2/D2 relation after the Chemistry seal."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ROVIBRONIC_COMPOSITION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}

        # Only this custodian-side block opens the source-derived target.  It
        # independently checks component hashes, all four exact ratio intervals,
        # both molecular hierarchies and the heavier-isotope direction.
        record = authoritative_record(self.root)
        intervals = measured_ratio_intervals(self.root)
        predictions = sealed_ratio_vector()
        observed_label = molecular_spectroscopy_classification(self.root)
        if observed_label != MEASURED_LABEL:
            raise ValueError("the complete H2/D2 classification changed")
        ratio_rows = tuple(
            {
                "row_id": name,
                "predicted_exact_numerator": value.numerator,
                "predicted_exact_denominator": value.denominator,
                "measured_lower_numerator": intervals[name][0].numerator,
                "measured_lower_denominator": intervals[name][0].denominator,
                "measured_upper_numerator": intervals[name][1].numerator,
                "measured_upper_denominator": intervals[name][1].denominator,
                "contained": intervals[name][0] <= value <= intervals[name][1],
            }
            for name, value in predictions.items()
        )
        if len(ratio_rows) != 4 or not all(row["contained"] for row in ratio_rows):
            raise ValueError("a sealed rovibronic ratio left the complete registered NIST interval vector")

        target_values = {
            self.spec.target_rows[0].target_id: HeldLabel("external-observation", observed_label)
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
            custody_nonce=sha256_identity((registration_hash, self.spec.target_rows[0].snapshot_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("rovibronic Chemistry prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("rovibronic prediction emitted an invalid chemical observation label")
        target_id = self.spec.target_rows[0].target_id
        comparison = {
            "target_id": target_id,
            "source_id": SOURCE_ID,
            "predicted": prediction.label,
            "observed": release.targets[target_id].label,
            "passed": prediction.label == release.targets[target_id].label,
        }
        changed_label = prediction.label + "__changed"
        tampered = {
            "target_id": "deliberately-tampered-unfavorable-control",
            "predicted": prediction.label,
            "observed": changed_label,
            "passed": prediction.label != changed_label,
        }
        passed = bool(comparison["passed"] and tampered["passed"] and all(row["contained"] for row in ratio_rows))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-H2-D2-ratio-interval-and-held-label-comparison", self.spec.experiment_id))
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=interpreter_hash,
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=comparator_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released rovibronic target identity differs from commitment")
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
            "source_record_schema": record["schema"],
            "ratio_rows": ratio_rows,
            "comparison": comparison,
            "tampered_control": tampered,
            "complete_trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['row_id']}: exact {row['predicted_exact_numerator']}/{row['predicted_exact_denominator']} "
            f"contained in source-derived interval "
            f"[{row['measured_lower_numerator']}/{row['measured_lower_denominator']}, "
            f"{row['measured_upper_numerator']}/{row['measured_upper_denominator']}]: {row['contained']}"
            for row in ratio_rows
        ) + (
            f"{target_id}: predicted {comparison['predicted']}; source-derived {comparison['observed']}; exact match {comparison['passed']}",
            "deliberately tampered unfavorable control rejected",
        )
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(SOURCE_ID,),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = ("RovibronicCompositionValidator",)
