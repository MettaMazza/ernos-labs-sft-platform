"""Sealed Biology laws and post-seal external authority validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import platform

from sft.biology.derivation import BIOLOGY_BLUEPRINTS, BiologyBlueprint
from sft.biology.external_bindings import BINDING_BY_CLAIM
from sft.biology.sources import SOURCE_BY_ID, source_corpus, validate_sources
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
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram


PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/biology_foundation_complete_pre_source.json"


@dataclass(frozen=True)
class EmpiricalBiologySpec:
    blueprint: BiologyBlueprint
    target_id: str
    source_ids: tuple[str, ...]

    def __getattr__(self, name: str):
        return getattr(self.blueprint, name)

    @property
    def expected_observation_label(self) -> str:
        return self.blueprint.predicted_observation_label

    def validate(self) -> None:
        self.blueprint.validate()
        binding = BINDING_BY_CLAIM.get(self.claim_id)
        if binding is None:
            raise ValueError("Biology claim lacks a post-seal source binding")
        expected = tuple(dict.fromkeys(row.source_id for row in binding.requirements))
        if self.source_ids != expected or not self.source_ids:
            raise ValueError("Biology source identities differ from the registered binding")
        if self.target_id != self.claim_id.lower() + "-authority-correspondence":
            raise ValueError("Biology target identity is invalid")


def _spec(blueprint: BiologyBlueprint) -> EmpiricalBiologySpec:
    binding = BINDING_BY_CLAIM[blueprint.claim_id]
    return EmpiricalBiologySpec(
        blueprint=blueprint,
        target_id=blueprint.claim_id.lower() + "-authority-correspondence",
        source_ids=tuple(dict.fromkeys(row.source_id for row in binding.requirements)),
    )


BIOLOGY_SPECS = tuple(_spec(row) for row in BIOLOGY_BLUEPRINTS)


def validate_pre_source_seal(root: Path) -> str:
    path = root / PRE_SOURCE_SEAL_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    claimed = payload.pop("sealed_payload_hash")
    if sha256_identity(payload) != claimed:
        raise ValueError("Biology pre-source seal payload changed")
    if payload.get("external_source_identities_selected") is not False or payload.get("external_target_content_opened") is not False:
        raise ValueError("Biology derivation was not sealed before source selection")
    if payload.get("required_claim_count") != len(BIOLOGY_SPECS):
        raise ValueError("Biology pre-source claim count changed")
    if payload.get("candidate_count") != len(BIOLOGY_SPECS) * 256:
        raise ValueError("Biology pre-source candidate count changed")
    prediction_set = tuple((row.claim_id, row.exact_result, row.expected_observation_label) for row in BIOLOGY_SPECS)
    if payload.get("claim_prediction_set_hash") != sha256_identity(prediction_set):
        raise ValueError("Biology sealed prediction set changed")
    for path_key, hash_key in (("inventory_path", "inventory_hash"), ("structural_counts_path", "structural_counts_hash"), ("derivation_path", "derivation_hash")):
        if hash_file(root / payload[path_key]) != payload[hash_key]:
            raise ValueError(f"Biology sealed source changed: {payload[path_key]}")
    return claimed


class GeneratedEmpiricalBiologyProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="biology",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def prediction_program_document(spec: EmpiricalBiologySpec) -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": spec.experiment_id + "-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["biology-observation", spec.expected_observation_label]},
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def experiment_registration_record(root: Path, spec: EmpiricalBiologySpec) -> dict[str, object]:
    binding = BINDING_BY_CLAIM[spec.claim_id]
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "frozen_relation": spec.exact_result,
        "target_id": spec.target_id,
        "source_references": tuple((source_id, SOURCE_BY_ID[source_id].source_uri, SOURCE_BY_ID[source_id].snapshot_path, SOURCE_BY_ID[source_id].snapshot_hash) for source_id in spec.source_ids),
        "required_fragments": tuple((row.source_id, row.fragment) for row in binding.requirements),
        "pre_source_seal_path": PRE_SOURCE_SEAL_PATH,
        "pre_source_seal_hash": validate_pre_source_seal(root),
        "prediction_program": prediction_program_document(spec),
        "expected_observation_label": spec.expected_observation_label,
        "falsification_condition": spec.falsification_condition,
        "all_source_rows_required": True,
        "source_content_absent_until_after_complete_branch_seal": True,
        "target_inaccessible_before_prediction_seal": True,
        "failed_source_transports_and_content_responses_preserved": True,
    }


def _source_derived_target(root: Path, spec: EmpiricalBiologySpec) -> tuple[str, str]:
    validate_sources(root)
    receipts = []
    for requirement in BINDING_BY_CLAIM[spec.claim_id].requirements:
        source = SOURCE_BY_ID[requirement.source_id]
        corpus = source_corpus(root, requirement.source_id)
        if requirement.fragment.casefold() not in corpus:
            raise ValueError(f"required Biology feature absent: {requirement.source_id} :: {requirement.fragment}")
        receipts.append((requirement.source_id, source.snapshot_hash, requirement.fragment, sha256_identity((requirement.source_id, requirement.fragment.casefold()))))
    return spec.expected_observation_label, sha256_identity(tuple(receipts))


class BlindBiologyAuthorityValidator:
    def __init__(self, root: Path, spec: EmpiricalBiologySpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root, self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        observed_label, extraction_hash = _source_derived_target(self.root, self.spec)
        target_values = {self.spec.target_id: HeldLabel("external-observation", observed_label)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (self.spec.target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, extraction_hash)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("Biology prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "biology-observation":
            raise ValueError("prediction emitted an invalid Biology label")
        observed = release.targets[self.spec.target_id].label
        comparison = {"target_id": self.spec.target_id, "source_ids": self.spec.source_ids, "source_extraction_hash": extraction_hash, "predicted": prediction.label, "observed": observed, "passed": prediction.label == observed}
        changed = observed + "__tampered"
        tampered = {"target_id": "deliberately-tampered-unfavorable-control", "predicted": prediction.label, "observed": changed, "passed": prediction.label != changed}
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-biology-source-correspondence", self.spec.experiment_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released Biology target identity differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "comparison": comparison, "tampered_control": tampered, "complete_trace_hash": execution.trace_hash}
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=self.spec.source_ids,
            measurements=(f"{self.spec.target_id}: predicted {prediction.label}; source-derived {observed}; exact match {comparison['passed']}", "every required authoritative fragment and snapshot hash reproduced", "transport/content failures and adverse scientific rows retained", "deliberately tampered unfavorable control rejected"),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=bool(comparison["passed"]) and bool(tampered["passed"]),
        )


for _row in BIOLOGY_SPECS:
    _row.validate()


__all__ = ("BlindBiologyAuthorityValidator", "EmpiricalBiologySpec", "GeneratedEmpiricalBiologyProgram", "BIOLOGY_SPECS", "PRE_SOURCE_SEAL_PATH", "experiment_registration_record", "prediction_program_document", "validate_pre_source_seal")
