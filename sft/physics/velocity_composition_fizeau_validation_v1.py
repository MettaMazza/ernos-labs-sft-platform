"""Claim-specific post-seal validation of the complete Fizeau record."""

from __future__ import annotations

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
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.velocity_composition_fizeau_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    PDF_HASH,
    PDF_PATH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("ARXIV-1201.0501-WITHHELD-COMPLETE-FIZEAU-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes() -> dict[str, str]:
    return {SOURCE_PATH: SOURCE_HASH, PDF_PATH: PDF_HASH}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"Fizeau source identity changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-velocity-composition-fizeau-source-record/1" or record.get("source_id") != SOURCE_IDS[0]:
        raise ValueError("Fizeau source record identity changed")
    source = record.get("source", {})
    if source.get("snapshot_hash") != PDF_HASH or source.get("snapshot_path") != PDF_PATH:
        raise ValueError("Fizeau PDF binding changed")
    target = record.get("registered_target", {})
    expected = {
        "water_measured_slope_rad_s_per_m": "274/1000",
        "water_measured_standard_uncertainty_rad_s_per_m": "3/1000",
        "relativistic_raw_prediction_rad_s_per_m": "248/1000",
        "relativistic_profile_and_dispersion_corrected_prediction_rad_s_per_m": "299/1000",
        "ordinary_addition_prediction_rad_s_per_m": "563/1000",
        "reported_corrected_agreement_fraction": "8/100",
    }
    if any(target.get(key) != value for key, value in expected.items()):
        raise ValueError("Fizeau exact target row changed")
    if target.get("air_nonrelativistic_prediction_ruled_out") is not True or target.get("air_measurements_compatible_with_relativistic_calculation") is not True:
        raise ValueError("Fizeau air control changed")
    limitations = target.get("systematic_limitations_retained", ())
    if len(limitations) != 4:
        raise ValueError("Fizeau limitation ledger changed")
    custody = record.get("row_custody", {})
    required_true = (
        "formal_sft_claim_sealed_before_source_retrieval",
        "measured_slope_retained",
        "measured_uncertainty_retained",
        "raw_relativistic_prediction_retained",
        "corrected_relativistic_prediction_retained",
        "ordinary_addition_unfavorable_control_retained",
        "air_result_retained",
        "systematic_limitations_retained",
        "target_inaccessible_to_formal_derivation",
    )
    if not all(custody.get(key) is True for key in required_true) or custody.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("Fizeau custody row changed")
    return record


def exact_fizeau_analysis(target: dict[str, object]) -> dict[str, object]:
    measured = Fraction(target["water_measured_slope_rad_s_per_m"])
    uncertainty = Fraction(target["water_measured_standard_uncertainty_rad_s_per_m"])
    raw = Fraction(target["relativistic_raw_prediction_rad_s_per_m"])
    corrected = Fraction(target["relativistic_profile_and_dispersion_corrected_prediction_rad_s_per_m"])
    ordinary = Fraction(target["ordinary_addition_prediction_rad_s_per_m"])
    lower = measured - uncertainty
    upper = measured + uncertainty
    raw_distance = measured - raw if measured >= raw else raw - measured
    corrected_distance = measured - corrected if measured >= corrected else corrected - measured
    ordinary_distance = measured - ordinary if measured >= ordinary else ordinary - measured
    best_relativistic_distance = min(raw_distance, corrected_distance)
    return {
        "measured": measured,
        "uncertainty": uncertainty,
        "measured_interval": (lower, upper),
        "raw_relativistic": raw,
        "corrected_relativistic": corrected,
        "ordinary_addition": ordinary,
        "raw_distance": raw_distance,
        "corrected_distance": corrected_distance,
        "best_relativistic_distance": best_relativistic_distance,
        "ordinary_distance": ordinary_distance,
        "measurement_inside_complete_relativistic_systematics_bracket": raw <= lower and upper <= corrected,
        "relativistic_more_than_ten_times_closer": best_relativistic_distance * 10 < ordinary_distance,
        "ordinary_outside_measurement_interval": ordinary > upper,
        "air_control_retained": target["air_nonrelativistic_prediction_ruled_out"] and target["air_measurements_compatible_with_relativistic_calculation"],
        "all_limitations_retained": len(target["systematic_limitations_retained"]) == 4,
    }


class VelocityCompositionFizeauValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Fizeau comparison seal")
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
            raise ValueError("Fizeau prediction package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.family != "physical-observation" or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("Fizeau prediction label changed")
        analysis = exact_fizeau_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        all_rows = analysis["all_limitations_retained"] and analysis["air_control_retained"]
        discriminator = all((
            analysis["measurement_inside_complete_relativistic_systematics_bracket"],
            analysis["relativistic_more_than_ten_times_closer"],
            analysis["ordinary_outside_measurement_interval"],
        ))
        tampered = dict(context[TARGET_IDS[0]])
        tampered["ordinary_addition_prediction_rad_s_per_m"] = tampered["water_measured_slope_rad_s_per_m"]
        tampered_rejected = not exact_fizeau_analysis(tampered)["relativistic_more_than_ten_times_closer"]
        passed = all((formal, all_rows, discriminator, tampered_rejected))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-Fizeau-velocity-composition-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
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
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "seal": sealed.seal_hash,
            "prediction_seal": prediction_seal.seal_hash,
            "source_hashes": source_hashes(),
            "target_identity": target_identity,
            "analysis": analysis,
            "formal": formal,
            "all_rows": all_rows,
            "discriminator": discriminator,
            "tampered_rejected": tampered_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "The exact Fold velocity operation was admitted before the Fizeau source was retrieved.",
            "The water slope is retained as 274/1000 +/- 3/1000 rad s/m.",
            "The raw and corrected relativistic rows 248/1000 and 299/1000 bracket the measured interval.",
            "Ordinary addition predicts 563/1000; its distance 289/1000 exceeds the nearest relativistic distance 25/1000 by more than tenfold.",
            "The air row rejects ordinary addition and is compatible with relativistic composition.",
            "Flow calibration, turbulent-profile and path-length systematics are retained; no precision overclaim is made.",
            "A tampered ordinary-addition row equal to the measured central value destroys the discriminator and is rejected.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            all_rows,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = ("FALSIFICATION_CONDITION", "TARGET_IDS", "VelocityCompositionFizeauValidator", "authoritative_record", "exact_fizeau_analysis", "source_hashes")
