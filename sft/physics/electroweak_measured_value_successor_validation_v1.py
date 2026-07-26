"""Exact post-seal evaluator for the electroweak measured-value correction."""

from fractions import Fraction
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
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.electroweak_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.precision_value_laws_v1 import terminal_electroweak_cos_squared, terminal_electroweak_sin_squared


TARGET_IDS = ("PDG-ELECTROWEAK-WITHHELD-COMPLETE-MEASURED-VALUE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"electroweak successor source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-electroweak-measured-value-successor-source-record/1":
        raise ValueError("electroweak successor source schema changed")
    if record.get("formal_receipt_hash") != "sha256:263cf79e79ed1d7ba0246f84abe869084aa4db7b195dd0c07300d1dabdef72f4":
        raise ValueError("electroweak formal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete two-source electroweak record required")
    boundary = record.get("methodological_boundary", {})
    required_true = tuple(key for key in boundary if key != "measurement_selected_formal_survivor")
    if not all(boundary.get(key) is True for key in required_true) or boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("electroweak measurement-method boundary changed")
    return record


def interval(center: Fraction, uncertainty: Fraction):
    if center <= uncertainty or uncertainty <= 0:
        raise ValueError("electroweak measured interval must remain positive")
    return center - uncertainty, center + uncertainty


def exact_electroweak_analysis(target):
    direct = interval(Fraction(target["on_shell_sin_squared_center"]), Fraction(target["on_shell_sin_squared_standard_uncertainty"]))
    z = interval(Fraction(target["z_mass_GeV"]), Fraction(target["z_mass_standard_uncertainty_GeV"]))
    compatible_w = interval(Fraction(target["compatible_w_mass_GeV"]), Fraction(target["compatible_w_mass_standard_uncertainty_GeV"]))
    all_w = interval(Fraction(target["all_input_w_mass_GeV"]), Fraction(target["all_input_w_mass_standard_uncertainty_GeV"]))
    compatible_wz = ((compatible_w[0] / z[1]) ** 2, (compatible_w[1] / z[0]) ** 2)
    all_input_wz = ((all_w[0] / z[1]) ** 2, (all_w[1] / z[0]) ** 2)
    sine = terminal_electroweak_sin_squared()
    cosine = terminal_electroweak_cos_squared()
    return {
        "direct_on_shell_interval": direct,
        "compatible_WZ_squared_interval": compatible_wz,
        "all_input_WZ_squared_method_record": all_input_wz,
        "forced_sine_inside_direct_interval": direct[0] <= sine <= direct[1],
        "forced_cosine_inside_compatible_WZ_interval": compatible_wz[0] <= cosine <= compatible_wz[1],
        "exact_partition": sine + cosine == Fraction(1, 1),
        "incompatible_input_disclosure_retained": target["all_input_aggregate_contains_source_identified_incompatible_CDF_2022_input"] is True,
        "poor_consistency_disclosure_retained": target["source_reports_including_CDF_2022_produces_very_poor_consistency"] is True,
        "inconsistent_aggregate_not_used_as_target": target["all_input_aggregate_is_not_used_as_a_physical_target"] is True,
        "all_source_rows_retained": target["all_source_rows_retained_unchanged"] is True,
    }


class ElectroweakMeasuredValueSuccessorValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong electroweak successor seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        target = authoritative_record(self.root)["registered_target"]
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets={TARGET_IDS[0]: target}, custody_nonce=sha256_identity((registration_hash, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("electroweak successor prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("electroweak successor prediction label changed")
        analysis = exact_electroweak_analysis(context[TARGET_IDS[0]])
        non_boolean = {"direct_on_shell_interval", "compatible_WZ_squared_interval", "all_input_WZ_squared_method_record"}
        empirical = all(value for key, value in analysis.items() if key not in non_boolean)
        tampered_direct = dict(context[TARGET_IDS[0]]); tampered_direct["on_shell_sin_squared_center"] = "0.22000"
        tampered_direct_rejected = not exact_electroweak_analysis(tampered_direct)["forced_sine_inside_direct_interval"]
        tampered_w = dict(context[TARGET_IDS[0]]); tampered_w["compatible_w_mass_GeV"] = "81"
        tampered_w_rejected = not exact_electroweak_analysis(tampered_w)["forced_cosine_inside_compatible_WZ_interval"]
        passed = all(row[2] for row in SPEC.operational_witnesses) and empirical and tampered_direct_rejected and tampered_w_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-electroweak-measured-value-successor/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "tampered_direct_rejected": tampered_direct_rejected, "tampered_w_rejected": tampered_w_rejected}
        measurements = (
            "The exact forced on-shell share 1930922298157999/8642477221479757 lies inside [22333,22351]/100000.",
            "Its exact One-complement lies inside the complete compatible-input W/Z squared interval.",
            "No uncertainty was widened and no measured row selected the formal relation.",
            "The all-input aggregate and its uncertainties remain unchanged, but its source-identified incompatible input prevents it from being treated as a second like-typed physical target.",
            "Tampered direct-angle and compatible-W controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_source_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("ElectroweakMeasuredValueSuccessorValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_electroweak_analysis", "source_hashes")
