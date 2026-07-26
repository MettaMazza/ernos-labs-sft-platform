"""Exact post-seal evaluator for the superconducting-circuit Bell record."""

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
from sft.physics.quantum_support_uncertainty_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILE,
    SOURCE_FILE_HASH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("NATURE-STORZ-2023-WITHHELD-COMPLETE-BELL-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, SOURCE_FILE: SOURCE_FILE_HASH}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"quantum-support Bell source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-quantum-support-bell-postseal-source-record/1":
        raise ValueError("quantum-support Bell source schema changed")
    if record.get("formal_receipt_hash") != "sha256:1560f2e0de3870abac2bdc6575aa9811c4dc013d5a6d705e729a832dc451b79f":
        raise ValueError("formal quantum-support receipt binding changed")
    sources = record.get("sources", ())
    if len(sources) != 1 or sources[0].get("source_id") != SOURCE_IDS[0]:
        raise ValueError("complete one-source Bell record required")
    if sources[0].get("snapshot_hash") != SOURCE_FILE_HASH:
        raise ValueError("Bell source snapshot binding changed")
    boundary = record.get("interpretive_boundary", {})
    required_true = (
        "observed_record_tests_local_factorization_bound",
        "observed_record_does_not_exclude_all_deterministic_models",
        "random_setting_method_is_not_imported_as_ontic_nondeterminism",
        "support_cardinality_is_not_relabelled_as_statistical_variance",
        "Bell_measurement_does_not_empirically_measure_the_separate_Walsh_support_product",
        "target_inaccessible_to_formal_derivation",
    )
    if not all(boundary.get(key) is True for key in required_true) or boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("complete Bell interpretive boundary required")
    return record


def exact_quantum_support_bell_analysis(target):
    center = int(target["bell_parameter_center"])
    uncertainty = int(target["bell_parameter_standard_uncertainty"])
    denominator = int(target["bell_parameter_denominator"])
    local_numerator = int(target["local_factorization_bound_numerator"])
    local_denominator = int(target["local_factorization_bound_denominator"])
    lower = center - uncertainty
    upper = center + uncertainty
    budget_lower_thousandths = int(target["light_travel_budget_nanoseconds_center_thousandths"]) - int(target["light_travel_budget_nanoseconds_uncertainty_thousandths"])
    duration_upper_thousandths = 10 * (
        int(target["trial_duration_nanoseconds_center_hundredths"])
        + int(target["trial_duration_nanoseconds_uncertainty_hundredths"])
    )
    local_scaled = local_numerator * denominator
    measured_scaled_denominator = local_denominator
    return {
        "positive_exact_carriers": all(
            value > 0
            for value in (
                lower, upper, uncertainty, denominator, local_numerator, local_denominator,
                int(target["reported_excess_standard_deviations_lower_bound"]),
                int(target["reported_p_value_upper_power_of_ten_exponent_magnitude"]),
                int(target["experimental_trials_lower_bound"]), budget_lower_thousandths,
                duration_upper_thousandths, int(target["locality_margin_reported_standard_deviations"]),
            )
        ),
        "bell_interval": (lower, upper),
        "complete_interval_above_local_bound": lower * local_denominator > local_scaled,
        "central_excess_above_twenty_two_uncertainties": (center * local_denominator - local_scaled) > 22 * uncertainty * measured_scaled_denominator,
        "reported_significance_retained": int(target["reported_excess_standard_deviations_lower_bound"]) == 22 and int(target["reported_p_value_upper_power_of_ten_exponent_magnitude"]) == 108,
        "million_trial_lower_bound_retained": int(target["experimental_trials_lower_bound"]) == 1000000,
        "binary_two_setting_record": target["two_settings_per_site"] is True and target["binary_outcome_per_site"] is True,
        "deterministic_entanglement_generation_retained": target["deterministic_entanglement_generation"] is True,
        "space_like_interval_separation": duration_upper_thousandths < budget_lower_thousandths,
        "memory_control_retained": target["memory_robust_statistical_method"] is True,
        "random_setting_method_retained": target["random_number_generators_used_for_setting_choices"] is True,
        "measurement_independence_assumption_retained": target["measurement_independence_is_a_declared_experimental_assumption"] is True,
        "unavoidable_assumption_statement_retained": target["authors_state_assumptions_cannot_be_fully_avoided"] is True,
        "all_rows_retained": target["all_registered_rows_retained"] is True,
    }


class QuantumSupportUncertaintyValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong quantum-support Bell seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            TARGET_IDS,
            sealed.seal_hash,
            registration_hash,
        )
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
            raise ValueError("quantum-support Bell prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("quantum-support Bell prediction label changed")
        analysis = exact_quantum_support_bell_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all(value for key, value in analysis.items() if key != "bell_interval")
        boundary_rows = authoritative_record(self.root)["interpretive_boundary"]
        boundaries_retained = (
            boundary_rows["observed_record_tests_local_factorization_bound"] is True
            and boundary_rows["observed_record_does_not_exclude_all_deterministic_models"] is True
            and boundary_rows["random_setting_method_is_not_imported_as_ontic_nondeterminism"] is True
            and boundary_rows["support_cardinality_is_not_relabelled_as_statistical_variance"] is True
            and boundary_rows["Bell_measurement_does_not_empirically_measure_the_separate_Walsh_support_product"] is True
            and boundary_rows["measurement_selected_formal_survivor"] is False
            and boundary_rows["target_inaccessible_to_formal_derivation"] is True
        )
        tampered_s = dict(context[TARGET_IDS[0]])
        tampered_s["bell_parameter_center"] = 19900
        tampered_s_rejected = not exact_quantum_support_bell_analysis(tampered_s)["complete_interval_above_local_bound"]
        tampered_timing = dict(context[TARGET_IDS[0]])
        tampered_timing["trial_duration_nanoseconds_center_hundredths"] = 11100
        tampered_timing_rejected = not exact_quantum_support_bell_analysis(tampered_timing)["space_like_interval_separation"]
        passed = formal and empirical and boundaries_retained and tampered_s_rejected and tampered_timing_rejected
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-quantum-support-Bell-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "seal": sealed.seal_hash,
            "sources": source_hashes(),
            "target": target_identity,
            "analysis": analysis,
            "formal": formal,
            "boundaries_retained": boundaries_retained,
            "tampered_s_rejected": tampered_s_rejected,
            "tampered_timing_rejected": tampered_timing_rejected,
        }
        measurements = (
            "The complete measured S interval [20714,20780]/10000 lies above the local-factorization bound two.",
            "The central excess is greater than twenty-two stated standard uncertainties and P is reported below 10^-108.",
            "More than one million superconducting-circuit trials are retained.",
            "The complete trial-duration interval lies below the complete light-travel-budget interval.",
            "The memory-robust analysis and setting-choice procedure are retained.",
            "Measurement independence remains a declared source assumption; no ontic randomness premise is imported.",
            "The result rejects local factorization under those conditions, not determinism as a whole.",
            "The Bell record does not relabel the separate formal Walsh support product as measured variance.",
            "Tampered S and timing controls reject.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            analysis["all_rows_retained"],
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION", "TARGET_IDS", "QuantumSupportUncertaintyValidator",
    "authoritative_record", "exact_quantum_support_bell_analysis", "source_hashes",
)
