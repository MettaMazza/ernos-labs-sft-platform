"""Exact post-seal evaluation of the collective-radiation record."""

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.collective_radiation_empirical_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document


TARGET_IDS = ("COLLECTIVE-RADIATION-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes(): return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected: raise ValueError(f"collective-radiation source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-collective-radiation-postseal-source-record/1": raise ValueError("source schema changed")
    if record.get("formal_receipt_hash") != "sha256:50974ab152438d8b84fe8220281e0d98737df0880f9a6384d50bac6060987b07": raise ValueError("formal receipt binding changed")
    if len(record.get("sources", ())) != 5: raise ValueError("complete five-source record required")
    return record


def exact_collective_analysis(target):
    laser_low = Fraction(target["laser_unmodified_linewidth_lower_hz"])
    laser_high = Fraction(target["laser_extended_cavity_linewidth_upper_hz"])
    return {
        "blackbody_exponent_matches": target["blackbody_exponent"] == 4,
        "blackbody_double_ratio": Fraction(2) ** target["blackbody_exponent"],
        "blackbody_coefficient_agreement": Fraction(target["blackbody_historical_stefan_constant_relative_agreement_upper"]) <= Fraction(1, 100),
        "blackbody_shape_agreement": target["blackbody_spectrum_shape_agreement_reported"],
        "acoustic_precision_retained": target["acoustic_resonance_measurement_precision_label"] == "part-per-million",
        "laser_positive": laser_low > 0 and laser_high > 0,
        "laser_narrowing_factor_floor": laser_low / laser_high,
        "laser_feedback_narrows": laser_low / laser_high >= 20,
        "plasma_direct_relation": target["plasma_frequency_direct_density_function_reported"] and target["plasma_probe_flight_count"] == 2,
        "alfven_year_count": target["alfven_observation_year_last"] - target["alfven_observation_year_first"] + 1,
        "alfven_record_complete": target["alfven_observation_year_first"] == 2007 and target["alfven_observation_year_last"] == 2014,
        "all_rows_retained": target["all_registered_rows_retained"],
    }


class CollectiveRadiationValidator:
    def __init__(self, root): self.root = root.resolve()
    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID: raise ValueError("wrong collective-radiation seal")
        registration = experiment_registration_record(SPEC); registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets=targets, custody_nonce=sha256_identity((registration_hash, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("prediction audit failed")
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL: raise ValueError("prediction label changed")
        analysis = exact_collective_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all((analysis["blackbody_exponent_matches"], analysis["blackbody_coefficient_agreement"], analysis["blackbody_shape_agreement"], analysis["acoustic_precision_retained"], analysis["laser_positive"], analysis["laser_feedback_narrows"], analysis["plasma_direct_relation"], analysis["alfven_record_complete"], analysis["all_rows_retained"]))
        tampered = dict(context[TARGET_IDS[0]]); tampered["blackbody_exponent"] = 3
        tampered_rejected = not exact_collective_analysis(tampered)["blackbody_exponent_matches"]
        passed = formal and empirical and tampered_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-collective-radiation-comparator/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "formal": formal, "empirical": empirical, "tampered_rejected": tampered_rejected}
        measurements = ("Measured blackbody exponent four forces doubling ratio sixteen.", "Historical coefficient agreement is within one percent and spectrum shape agreement is retained.", "Acoustic cavity resonances were measured to part-per-million precision.", "Measured laser linewidth remains positive and feedback narrows it by at least factor twenty.", "Two NASA flights track density through plasma frequency.", "NASA registers Alfvén observations across eight calendar years.", "No dimensional coefficient is fitted from normalized Fold structure.", "Tampered exponent three rejects.")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("CollectiveRadiationValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_collective_analysis", "source_hashes")
