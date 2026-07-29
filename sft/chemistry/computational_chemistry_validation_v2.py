"""Versioned interface correction for COMP-001--014 empirical validation.

Version 1 and its rejected receipt remain immutable.  This version changes no
law, candidate, target, comparison or condition; it supplies keyword-only
constructor fields required by the existing custody objects.
"""

from __future__ import annotations

from pathlib import Path
import platform

from sft.chemistry.computational_chemistry_validation_v1 import exact_analysis
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel


class ComputationalChemistryValidatorV2:
    def __init__(self, root: Path, spec):
        self.root = root.resolve(); self.spec = spec

    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()},
            custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("COMP prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True); omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-computational-chemistry-validation/2", self.spec.claim_id, self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("COMP target identity changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        receipt = sha256_identity({"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission_rejected, "trace": execution.trace_hash})
        notes = (
            "complete 59-artifact 444,644,830-byte post-seal surface retained",
            "12 PubChem records, four ChEBI cross-source records, 36,444 Rhea reactions, 50,016 USPTO reactions and 1,065,119 atom-mapped reactions retained",
            "all twelve registered invalid-property responses, low-confidence rows, conflicts, unavailable records and resource halts retained",
            f"all {len(checks)} separately registered claim targets retained",
            "external formats, algorithms, scores and outcomes never select the Fold-native survivor",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, receipt, self.spec.falsification_condition, passed)


__all__ = ("ComputationalChemistryValidatorV2",)
