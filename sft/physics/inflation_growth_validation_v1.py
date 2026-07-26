"""Exact post-seal evaluation of the inflation-growth observation record."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor,
    TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.inflation_growth_empirical_v1 import (
    CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC,
)


TARGET_IDS = ("INFLATION-GROWTH-WITHHELD-COMPLETE-OBSERVATION-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes() -> dict[str, str]:
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"inflation-growth source identity changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-inflation-growth-postseal-source-record/1":
        raise ValueError("inflation-growth source schema changed")
    if record.get("formal_receipt_hash") != "sha256:00aa52b47f8ebfe57fb5a90530a54614ba175d87f6708c69e454fcf9fd888aa7":
        raise ValueError("inflation-growth formal receipt binding changed")
    if len(record.get("sources", ())) != 2:
        raise ValueError("complete two-source record is required")
    target = record.get("registered_target", {})
    expected = {
        "planck_scalar_index_central": "0.9649",
        "planck_scalar_index_standard_uncertainty": "0.0042",
        "bicep_planck_tensor_ratio_upper_95": "0.032",
        "tensor_bound_strict": True,
        "all_registered_rows_retained": True,
    }
    if any(target.get(key) != value for key, value in expected.items()):
        raise ValueError("inflation-growth target row changed")
    custody = record.get("row_custody", {})
    if not all(custody.get(key) is True for key in (
        "formal_receipt_precedes_source_retrieval", "target_inaccessible_to_formal_executable",
        "target_did_not_rewrite_formal_survivor", "complete_uncertainty_and_bound_rows_retained",
        "no_conventional_efold_value_asserted",
    )):
        raise ValueError("inflation-growth custody record changed")
    return record


def exact_inflation_analysis(target: dict[str, object]) -> dict[str, object]:
    centre = Fraction(target["planck_scalar_index_central"])
    width = Fraction(target["planck_scalar_index_standard_uncertainty"])
    interval = (centre - width, centre + width)
    scalar = Fraction(31, 32)
    tensor = Fraction(1, 32)
    bound = Fraction(target["bicep_planck_tensor_ratio_upper_95"])
    return {
        "scalar_prediction": scalar,
        "scalar_interval": interval,
        "scalar_inside_interval": interval[0] <= scalar <= interval[1],
        "scalar_distance_from_central": abs(scalar - centre),
        "tensor_prediction": tensor,
        "tensor_upper_bound": bound,
        "tensor_strictly_below_bound": target["tensor_bound_strict"] and tensor < bound,
        "tensor_bound_margin": bound - tensor,
        "partition_complete": scalar + tensor == Fraction(1),
        "all_rows_retained": target["all_registered_rows_retained"],
    }


class InflationGrowthValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong inflation-growth comparison seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("inflation-growth prediction package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("inflation-growth prediction label changed")
        analysis = exact_inflation_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all((
            analysis["scalar_inside_interval"], analysis["tensor_strictly_below_bound"],
            analysis["partition_complete"], analysis["all_rows_retained"],
        ))
        tampered = dict(context[TARGET_IDS[0]])
        tampered["planck_scalar_index_central"] = "0.9000"
        tampered_rejected = not exact_inflation_analysis(tampered)["scalar_inside_interval"]
        passed = formal and empirical and tampered_rejected
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-inflation-growth-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=interpreter_hash,
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=comparator_hash, prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"seal": sealed.seal_hash, "source_hashes": source_hashes(), "target_identity": target_identity, "analysis": analysis, "formal": formal, "empirical": empirical, "tampered_rejected": tampered_rejected}
        measurements = (
            "The formal inflation-growth law was admitted before the primary snapshots were bound.",
            "Exact scalar support 31/32 lies within Planck ns=0.9649+/-0.0042.",
            "Exact tensor support 1/32 lies strictly below r<0.032 by 3/4000.",
            "The complete 31/32 plus 1/32 partition is retained without fitting.",
            "No measured equality is claimed between five Fold doublings and conventional logarithmic e-folds.",
            "A tampered scalar target rejects the comparison.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("FALSIFICATION_CONDITION", "TARGET_IDS", "InflationGrowthValidator", "authoritative_record", "exact_inflation_analysis", "source_hashes")
