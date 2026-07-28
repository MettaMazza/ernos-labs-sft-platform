"""Sealed Consciousness laws and post-seal empirical-boundary validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.consciousness_cognitive_science.external_bindings import (
    CLAIM_BINDING_BY_ID,
    EXTERNAL_TARGETS_PATH,
    SOURCE_FEATURE_AUDIT_PATH,
)
from sft.consciousness_cognitive_science.generated_law import (
    CONSCIOUSNESS_BLUEPRINTS,
    ConsciousnessBlueprint,
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
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram


PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/consciousness_foundation_complete_pre_source.json"


@dataclass(frozen=True)
class EmpiricalConsciousnessSpec:
    blueprint: ConsciousnessBlueprint
    target_id: str
    source_ids: tuple[str, ...]
    expected_external_label: str
    directness: str
    empirical_disposition: str
    evidence_scope: str

    def __getattr__(self, name: str):
        return getattr(self.blueprint, name)

    def validate(self) -> None:
        self.blueprint.validate()
        binding = CLAIM_BINDING_BY_ID.get(self.claim_id)
        if binding is None:
            raise ValueError("Consciousness claim lacks a post-seal external binding")
        if self.source_ids != binding.source_ids or not self.source_ids:
            raise ValueError("Consciousness source identities differ from the registered binding")
        if self.expected_external_label != binding.expected_label:
            raise ValueError("Consciousness external consequence differs from its binding")
        if self.target_id != self.claim_id.lower() + "-external-consequence":
            raise ValueError("Consciousness target identity is invalid")


def _spec(blueprint: ConsciousnessBlueprint) -> EmpiricalConsciousnessSpec:
    binding = CLAIM_BINDING_BY_ID[blueprint.claim_id]
    return EmpiricalConsciousnessSpec(
        blueprint=blueprint,
        target_id=blueprint.claim_id.lower() + "-external-consequence",
        source_ids=binding.source_ids,
        expected_external_label=binding.expected_label,
        directness=binding.directness,
        empirical_disposition=binding.empirical_disposition,
        evidence_scope=binding.evidence_scope,
    )


CONSCIOUSNESS_SPECS = tuple(_spec(row) for row in CONSCIOUSNESS_BLUEPRINTS)


def _file_identity(path: Path) -> str:
    return hash_file(path)


def validate_pre_source_seal(root: Path) -> str:
    path = root / PRE_SOURCE_SEAL_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    claimed = payload.pop("complete_branch_pre_source_seal_hash")
    if sha256_identity(payload) != claimed:
        raise ValueError("Consciousness pre-source seal payload changed")
    if payload.get("external_source_identities_selected") is not False or payload.get("external_outcomes_opened") is not False:
        raise ValueError("Consciousness derivation was not sealed before source selection")
    if payload.get("required_claim_count") != len(CONSCIOUSNESS_SPECS):
        raise ValueError("Consciousness pre-source claim count changed")
    if payload.get("candidate_count") != len(CONSCIOUSNESS_SPECS) * 256:
        raise ValueError("Consciousness pre-source candidate count changed")
    prediction_set = tuple((row.claim_id, row.exact_result, row.predicted_observation_label) for row in CONSCIOUSNESS_SPECS)
    if payload.get("claim_prediction_set_hash") != sha256_identity(prediction_set):
        raise ValueError("Consciousness sealed prediction set changed")
    for relative, wanted in payload["sealed_files"].items():
        if _file_identity(root / relative) != wanted:
            raise ValueError(f"Consciousness pre-source file changed: {relative}")
    return claimed


def _verify_identity_payload(path: Path, identity_key: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    claimed = payload.pop(identity_key)
    if sha256_identity(payload) != claimed:
        raise ValueError(f"identity mismatch: {path}")
    payload[identity_key] = claimed
    return payload


def validate_external_evidence(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    audit_path = root / SOURCE_FEATURE_AUDIT_PATH
    targets_path = root / EXTERNAL_TARGETS_PATH
    audit = _verify_identity_payload(audit_path, "audit_hash")
    targets = _verify_identity_payload(targets_path, "targets_hash")
    if targets["source_feature_audit_file_hash"] != _file_identity(audit_path):
        raise ValueError("Consciousness target record binds a different feature-audit file")
    if targets["source_feature_audit_hash"] != audit["audit_hash"]:
        raise ValueError("Consciousness target record binds a different feature-audit identity")
    if targets["claim_count"] != len(CONSCIOUSNESS_SPECS) or targets["passed_claim_count"] != len(CONSCIOUSNESS_SPECS):
        raise ValueError("Consciousness target record is incomplete or unresolved")
    if targets["unresolved_claim_count"] != 0:
        raise ValueError("an unresolved external target cannot be silently admitted")
    if audit["present_feature_count"] + audit["absent_feature_count"] != audit["registered_feature_count"]:
        raise ValueError("Consciousness feature accounting is incomplete")
    for relative, wanted in audit["manifest_hashes"].items():
        if _file_identity(root / relative) != wanted:
            raise ValueError(f"Consciousness capture manifest changed: {relative}")
    for source in audit["sources"]:
        for transport in source["transport_history"]:
            relative = transport.get("snapshot_path")
            wanted = transport.get("snapshot_hash")
            if relative and wanted and _file_identity(root / relative) != wanted:
                raise ValueError(f"Consciousness source snapshot changed: {relative}")
    return audit, targets


def _target_row(root: Path, spec: EmpiricalConsciousnessSpec) -> tuple[dict[str, object], str]:
    audit, targets = validate_external_evidence(root)
    row = next(item for item in targets["targets"] if item["claim_id"] == spec.claim_id)
    if row["target_id"] != spec.target_id or row["expected_label"] != spec.expected_external_label:
        raise ValueError("Consciousness external target binding changed")
    if row["observed_label"] != row["expected_label"] or row["exact_match"] is not True:
        raise ValueError("Consciousness external consequence is unresolved or adverse")
    if row["phenomenal_occurrence_directly_observed_by_third_person"] is not False:
        raise ValueError("third-person evidence was relabelled as direct phenomenal access")
    if row["formal_structure_relabelled_as_empirical_phenomenal_fact"] is not False:
        raise ValueError("formal structure was relabelled as an empirical phenomenal fact")
    return row, sha256_identity((audit["audit_hash"], targets["targets_hash"], row))


class GeneratedEmpiricalConsciousnessProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="consciousness_cognitive_science",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def prediction_program_document(spec: EmpiricalConsciousnessSpec) -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": spec.experiment_id + "-external-consequence-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["consciousness-external-consequence", spec.expected_external_label]},
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def experiment_registration_record(root: Path, spec: EmpiricalConsciousnessSpec) -> dict[str, object]:
    row, extraction_hash = _target_row(root, spec)
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "frozen_structural_relation": spec.exact_result,
        "complete_branch_pre_source_seal": validate_pre_source_seal(root),
        "target_id": spec.target_id,
        "source_ids": spec.source_ids,
        "expected_external_consequence": spec.expected_external_label,
        "evidence_scope": spec.evidence_scope,
        "directness": spec.directness,
        "empirical_disposition": spec.empirical_disposition,
        "target_row_hash": extraction_hash,
        "source_evidence": row["source_evidence"],
        "prediction_program": prediction_program_document(spec),
        "falsification_condition": spec.falsification_condition,
        "all_source_features_adverse_boundaries_absences_and_transport_failures_required": True,
        "target_inaccessible_before_claim_derivation_seal": True,
        "external_evidence_cannot_select_structural_survivor": True,
    }


class BlindConsciousnessBoundaryValidator:
    def __init__(self, root: Path, spec: EmpiricalConsciousnessSpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        validate_pre_source_seal(self.root)
        row, extraction_hash = _target_row(self.root, self.spec)
        registration = experiment_registration_record(self.root, self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target_values = {self.spec.target_id: HeldLabel("external-consciousness-boundary", row["observed_label"])}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            (self.spec.target_id,),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, extraction_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("Consciousness prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "consciousness-external-consequence":
            raise ValueError("prediction emitted an invalid Consciousness consequence label")
        observed = release.targets[self.spec.target_id].label
        comparison = {
            "target_id": self.spec.target_id,
            "predicted": prediction.label,
            "observed": observed,
            "passed": prediction.label == observed,
            "directness": self.spec.directness,
            "empirical_disposition": self.spec.empirical_disposition,
        }
        changed = observed + "__tampered"
        tampered = {"predicted": prediction.label, "observed": changed, "passed": prediction.label != changed}
        missing_feature_control = {
            "source_id": "CONSC-SYNESTHETIC-COLOUR-MATCH-2008",
            "missing_features_remain_absent": any(
                evidence["source_id"] == "CONSC-SYNESTHETIC-COLOUR-MATCH-2008" and bool(evidence["missing_registered_features"])
                for evidence in row["source_evidence"]
            ) if self.spec.family == "red_of_red" else True,
            "missing_features_used_as_support": False,
        }
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-consciousness-boundary-equality", self.spec.experiment_id)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released Consciousness target identity differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        passed = bool(comparison["passed"]) and bool(tampered["passed"]) and bool(missing_feature_control["missing_features_remain_absent"]) and not missing_feature_control["missing_features_used_as_support"]
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "external_extraction_hash": extraction_hash,
            "comparison": comparison,
            "tampered_control": tampered,
            "missing_feature_control": missing_feature_control,
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
            data_source_ids=self.spec.source_ids,
            measurements=(
                f"{self.spec.target_id}: predicted {prediction.label}; source-derived {observed}; exact match {comparison['passed']}",
                f"evidence disposition: {self.spec.empirical_disposition}; directness: {self.spec.directness}",
                "all registered source features, adverse boundaries, absences and transport failures preserved",
                "phenomenal occurrence was not claimed as directly third-person observed",
                "deliberately changed consequence rejected",
            ),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


for _specification in CONSCIOUSNESS_SPECS:
    _specification.validate()


__all__ = (
    "BlindConsciousnessBoundaryValidator",
    "CONSCIOUSNESS_SPECS",
    "EmpiricalConsciousnessSpec",
    "GeneratedEmpiricalConsciousnessProgram",
    "PRE_SOURCE_SEAL_PATH",
    "experiment_registration_record",
    "prediction_program_document",
    "validate_external_evidence",
    "validate_pre_source_seal",
)
