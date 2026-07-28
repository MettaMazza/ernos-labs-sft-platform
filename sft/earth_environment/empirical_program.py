"""Sealed Earth laws and post-seal external evidence validation."""

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
from sft.earth_environment.external_bindings import (
    BINDING_BY_CLAIM,
    BINDINGS_PATH,
    EXTERNAL_TARGETS_PATH,
    SOURCE_FEATURE_AUDIT_PATH,
)
from sft.earth_environment.generated_law import EARTH_BLUEPRINTS, EarthBlueprint
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
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram, LawChoice, LawDimension


PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json"
QUAKE_FIRST_RESULT_PATH = "experiments/earth_environment/quake_magnitude_frequency_result.json"
QUAKE_HOLDOUT_RESULT_PATH = "experiments/earth_environment/quake_magnitude_frequency_holdout_result_v2.json"


def _verified_payload(root: Path, relative: str, identity_key: str) -> dict[str, object]:
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    claimed = payload.pop(identity_key)
    if sha256_identity(payload) != claimed:
        raise ValueError(f"Earth evidence identity mismatch: {relative}")
    payload[identity_key] = claimed
    return payload


def _adapt_dimensions(blueprint: EarthBlueprint) -> tuple[LawDimension, ...]:
    return tuple(
        LawDimension(
            dimension.key,
            tuple(
                LawChoice(
                    choice.name,
                    dimension.required_property in choice.properties,
                    choice.explanation,
                )
                for choice in dimension.choices
            ),
        )
        for dimension in blueprint.dimensions
    )


@dataclass(frozen=True)
class EmpiricalEarthSpec:
    blueprint: EarthBlueprint
    target_id: str
    source_ids: tuple[str, ...]
    directness: str
    empirical_disposition: str

    def __getattr__(self, name: str):
        return getattr(self.blueprint, name)

    @property
    def dimensions(self) -> tuple[LawDimension, ...]:
        return _adapt_dimensions(self.blueprint)

    @property
    def expected_observation_label(self) -> str:
        return self.blueprint.predicted_observation_label

    def validate(self) -> None:
        self.blueprint.validate()
        binding = BINDING_BY_CLAIM.get(self.claim_id)
        if binding is None:
            raise ValueError("Earth claim lacks a post-seal external binding")
        if self.target_id != binding.target_id or self.source_ids != binding.source_ids:
            raise ValueError("Earth external identity changed")
        if self.expected_observation_label != binding.expected_label:
            raise ValueError("Earth external consequence changed")
        if len(self.dimensions) != 8 or any(len(row.choices) != 2 for row in self.dimensions):
            raise ValueError("Earth adapter does not preserve the frozen grammar")


def _target_payload(root: Path) -> dict[str, object]:
    return _verified_payload(root, EXTERNAL_TARGETS_PATH, "targets_hash")


def _specs() -> tuple[EmpiricalEarthSpec, ...]:
    targets = _target_payload(Path(__file__).resolve().parents[2])
    by_claim = {row["claim_id"]: row for row in targets["targets"]}
    return tuple(
        EmpiricalEarthSpec(
            blueprint=row,
            target_id=BINDING_BY_CLAIM[row.claim_id].target_id,
            source_ids=BINDING_BY_CLAIM[row.claim_id].source_ids,
            directness=by_claim[row.claim_id]["directness"],
            empirical_disposition=by_claim[row.claim_id]["empirical_disposition"],
        )
        for row in EARTH_BLUEPRINTS
    )


EARTH_SPECS = _specs()


def validate_pre_source_seal(root: Path) -> str:
    payload = json.loads((root / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed = payload.pop("complete_branch_pre_source_seal_hash")
    if sha256_identity(payload) != claimed:
        raise ValueError("Earth pre-source seal payload changed")
    if any(payload.get(key) is not False for key in ("external_source_identities_selected", "external_source_content_opened", "external_outcomes_opened")):
        raise ValueError("Earth derivation was not sealed before source selection")
    if payload.get("required_claim_count") != len(EARTH_SPECS) or payload.get("candidate_count") != len(EARTH_SPECS) * 256:
        raise ValueError("Earth pre-source census changed")
    predictions = tuple(
        (row.claim_id, row.exact_result, row.expected_observation_label, row.falsification_condition)
        for row in EARTH_SPECS
    )
    if payload.get("claim_prediction_set_hash") != sha256_identity(predictions):
        raise ValueError("Earth sealed prediction set changed")
    for relative, wanted in payload["sealed_files"].items():
        if hash_file(root / relative) != wanted:
            raise ValueError(f"Earth pre-source file changed: {relative}")
    return claimed


def validate_external_evidence(root: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    audit = _verified_payload(root, SOURCE_FEATURE_AUDIT_PATH, "audit_hash")
    targets = _verified_payload(root, EXTERNAL_TARGETS_PATH, "targets_hash")
    bindings = _verified_payload(root, BINDINGS_PATH, "bindings_hash")
    if targets["source_feature_audit_hash"] != audit["audit_hash"] or targets["bindings_hash"] != bindings["bindings_hash"]:
        raise ValueError("Earth target record binds different evidence")
    if targets["claim_count"] != len(EARTH_SPECS) or targets["passed_claim_count"] != len(EARTH_SPECS) or targets["unresolved_claim_count"] != 0:
        raise ValueError("Earth external target record is incomplete")
    if audit["present_feature_count"] + audit["absent_feature_count"] != audit["registered_feature_count"]:
        raise ValueError("Earth source-feature accounting is incomplete")
    if not audit["failed_transports_preserved"] or not targets["all_adverse_absent_and_failed_rows_preserved"]:
        raise ValueError("Earth adverse evidence was not preserved")
    for source in audit["sources"]:
        for transport in source["transport_history"]:
            relative, wanted = transport.get("snapshot_path"), transport.get("snapshot_hash")
            if relative and wanted and hash_file(root / relative) != wanted:
                raise ValueError(f"Earth source snapshot changed: {relative}")
    first = _verified_payload(root, QUAKE_FIRST_RESULT_PATH, "result_hash")
    holdout = _verified_payload(root, QUAKE_HOLDOUT_RESULT_PATH, "result_hash")
    quake = next(row for row in targets["targets"] if row["claim_id"] == "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001")
    numeric = quake["numeric_comparison"]
    if first["passed"] is not False or holdout["passed"] is not True or numeric["first_adverse_result_reclassified"] is not False:
        raise ValueError("Earth earthquake adverse/holdout disposition changed")
    if numeric["first_mixed_catalog_result"]["result_hash"] != first["result_hash"] or numeric["independent_homogeneous_holdout"]["result_hash"] != holdout["result_hash"]:
        raise ValueError("Earth earthquake result identity changed")
    return audit, targets, bindings


def _target_row(root: Path, spec: EmpiricalEarthSpec) -> tuple[dict[str, object], str]:
    audit, targets, bindings = validate_external_evidence(root)
    row = next(item for item in targets["targets"] if item["claim_id"] == spec.claim_id)
    if row["target_id"] != spec.target_id or row["expected_label"] != spec.expected_observation_label:
        raise ValueError("Earth target binding changed")
    if row["observed_label"] != row["expected_label"] or row["exact_match"] is not True:
        raise ValueError("Earth external boundary consequence is unresolved")
    if row["external_evidence_selected_survivor"] is not False:
        raise ValueError("Earth evidence selected the structural survivor")
    if row["formal_structure_relabelled_as_direct_measurement"] is not False or row["model_or_forecast_relabelled_as_observation"] is not False:
        raise ValueError("Earth evidence classes were conflated")
    return row, sha256_identity((audit["audit_hash"], targets["targets_hash"], bindings["bindings_hash"], row))


class GeneratedEmpiricalEarthProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="earth_environment",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def prediction_program_document(spec: EmpiricalEarthSpec) -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": spec.experiment_id + "-external-consequence-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["earth-external-consequence", spec.expected_observation_label]},
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def experiment_registration_record(root: Path, spec: EmpiricalEarthSpec) -> dict[str, object]:
    row, extraction_hash = _target_row(root, spec)
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "frozen_structural_relation": spec.exact_result,
        "complete_branch_pre_source_seal": validate_pre_source_seal(root),
        "target_id": spec.target_id,
        "source_ids": spec.source_ids,
        "expected_external_consequence": spec.expected_observation_label,
        "directness": spec.directness,
        "empirical_disposition": spec.empirical_disposition,
        "target_row_hash": extraction_hash,
        "source_evidence": row["source_evidence"],
        "numeric_comparison": row["numeric_comparison"],
        "prediction_program": prediction_program_document(spec),
        "falsification_condition": spec.falsification_condition,
        "all_adverse_absent_failed_and_unresolved_rows_required": True,
        "target_inaccessible_before_claim_derivation_seal": True,
        "external_evidence_cannot_select_structural_survivor": True,
    }


class BlindEarthBoundaryValidator:
    def __init__(self, root: Path, spec: EmpiricalEarthSpec):
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
        target_values = {self.spec.target_id: HeldLabel("external-earth-boundary", row["observed_label"])}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (self.spec.target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, extraction_hash)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("Earth prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "earth-external-consequence":
            raise ValueError("prediction emitted an invalid Earth consequence label")
        observed = release.targets[self.spec.target_id].label
        comparison = {"target_id": self.spec.target_id, "predicted": prediction.label, "observed": observed, "passed": prediction.label == observed}
        tampered = {"predicted": prediction.label, "observed": observed + "__tampered", "passed": prediction.label != observed + "__tampered"}
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-earth-boundary-equality", self.spec.experiment_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released Earth target identity differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        audit, _, _ = validate_external_evidence(self.root)
        passed = bool(comparison["passed"] and tampered["passed"] and row["missing_and_absent_features_preserved"])
        measurement_payload = {"registration": registration_hash, "seal": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "extraction": extraction_hash, "comparison": comparison, "tampered": tampered, "numeric_comparison": row["numeric_comparison"], "trace": execution.trace_hash}
        measurements = [
            f"{self.spec.target_id}: predicted {prediction.label}; source-derived {observed}; exact match {comparison['passed']}",
            f"source features: {audit['present_feature_count']} present; {audit['absent_feature_count']} absent preserved; {audit['registered_feature_count']} registered",
            "the original failed transport and every adverse, absent and unresolved row remain preserved",
            "a deliberately changed external consequence was rejected",
        ]
        if row["numeric_comparison"] is not None:
            measurements.append("earthquake unit-exponent test: mixed catalogue adverse retained; separately preregistered homogeneous mww holdout compatible")
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=self.spec.source_ids,
            measurements=tuple(measurements),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


for _row in EARTH_SPECS:
    _row.validate()


__all__ = (
    "BlindEarthBoundaryValidator",
    "EARTH_SPECS",
    "EmpiricalEarthSpec",
    "GeneratedEmpiricalEarthProgram",
    "PRE_SOURCE_SEAL_PATH",
    "experiment_registration_record",
    "prediction_program_document",
    "validate_external_evidence",
    "validate_pre_source_seal",
)
