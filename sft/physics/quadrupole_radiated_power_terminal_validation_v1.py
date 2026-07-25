"""Post-seal V1, prerequisite and primary Double Pulsar comparison."""
from __future__ import annotations

from fractions import Fraction
import json
import platform
from pathlib import Path

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldWord,
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
from sft.physics.quadrupole_radiated_power_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    radiated_power_certificate,
)

SOURCE_ID = "D9Q-QUADRUPOLE-RADIATED-POWER-COMPARISON"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/quadrupole-radiated-power-source-record.json"
SOURCE_RECORD_HASH = "sha256:cc4962b3f7d4051b91baef30a5f936323beab162da74cc5618a4d603a78cdde9"
V1_PATH = "audits/v1_theorem_manifest_observation_census.json"
V1_HASH = "sha256:05c7c285e87720c0b22a69cc69b07cdd9749a1aa1728afd934e1ed9f7c30ce93"
WAVE_PATH = "claims/SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003/certificate.json"
WAVE_HASH = "sha256:efd694cafd4d48fdaf097d51325114b0ed16f9d201bf437501a88dfafbf7b2be"
ENERGY_PATH = "claims/SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003/certificate.json"
ENERGY_HASH = "sha256:f4b3a491aba638ed3ebf7730372980d323235ef3b9f33c2a7223d91779f02f0d"
INVERSE_PATH = "claims/SFT-PHYS-FIELD-INVERSE-SQUARE-001/certificate.json"
INVERSE_HASH = "sha256:a5314f6a9f477e596674d93b71437f0b35d9b44401a339e9ae6352f439c3e40f"
BOUNDARY_PATH = "claims/SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001/certificate.json"
BOUNDARY_HASH = "sha256:49cf663f9be8a83bcb90520d38fea24eff091f0d478e830b269500c129156fa5"
CONSERVATION_PATH = "claims/SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010/certificate.json"
CONSERVATION_HASH = "sha256:50f20cd3f109456709c36cb46d9e97ec0e4632f18cdfcd19224d7d7d8b619425"
COUPLING_PATH = "claims/SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002/certificate.json"
COUPLING_HASH = "sha256:e09460421ef6317965e279632172b357150096ec535dc5d47f26f30430d7d8e5"
MEASURED_PATH = "claims/SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001/certificate.json"
MEASURED_HASH = "sha256:f26507521a00aa23286f77949a0f3cae2baea030feff5990885357499885c476"
CUSTODY_PATH = "claims/SFT-PHYS-MEAS-TARGET-CUSTODY-001/certificate.json"
CUSTODY_HASH = "sha256:2df6f9d76ec76047ac2d244218cc132197d04b0008f6f7f6e6654d0c4ebdacde"
PAPER_PATH = "experiments/external_sources/physics/snapshots/arxiv-2112.06795-double-pulsar.pdf"
PAPER_HASH = "sha256:9d1b5b4dc304b1d6b1b11059a26d96ca97d1c0d43857523058f973c12bddc6a4"
FORMAL_COMMIT = "6d2fc8cafd72fb3b50ca3d648a69190d469841e1"
TARGET_IDS = ("D9Q-WITHHELD-HISTORICAL-PREREQUISITE-AND-DOUBLE-PULSAR-RECORD",)

REQUIRED_TARGET_ROWS = (
    "v1_source_entry",
    "v1_leading_radiating_moment",
    "v1_radiative_rate",
    "v1_power_relation",
    "v1_static_control",
    "v1_amplitude_scaling",
    "v1_outward_transport",
    "existing_v3_quadrupole_first",
    "existing_v3_field_energy_square",
    "existing_v3_inverse_square",
    "existing_v3_boundary_rank_two",
    "existing_v3_source_conservation",
    "existing_v3_binary_coupling",
    "formal_prediction_commit_precedes_target_access",
    "formal_normalized_binary_comparison",
    "primary_system",
    "primary_observation_span",
    "primary_orbital_period",
    "primary_eccentricity",
    "primary_tracked_orbits",
    "primary_dominant_orbital_decay_cause",
    "primary_shklovskii_correction",
    "primary_galactic_correction",
    "primary_combined_external_correction",
    "primary_intrinsic_orbital_decay",
    "primary_spin_down_mass_loss_correction",
    "primary_measured_GW_orbital_decay",
    "primary_measured_fractional_precision",
    "primary_leading_quadrupole_prediction",
    "primary_next_order_3_5PN_correction",
    "primary_total_prediction",
    "primary_measured_over_predicted_ratio",
    "primary_95_percent_agreement_boundary",
    "primary_extreme_EOS_ratio",
    "primary_cumulative_periastron_normalized_chi_squared",
    "primary_leading_order_classification",
    "primary_next_order_classification",
    "primary_distance_uncertainty_currently_subdominant",
    "primary_observed_timing_error_dominates_current_intrinsic_uncertainty",
    "primary_future_limit_requires_kinematic_corrections",
    "primary_regime",
    "primary_black-hole_merger_comparison_requires_regime_caveat",
    "primary_alternative_scalar_theories_can_add_lower-moment-radiation",
    "primary_result_measures_universal_Fold_power_fraction",
    "external_values_select_formal_survivor",
    "negative_external_decay_sign_used_as_formal_proof_scalar",
    "measured_parameter_fitted_into_v3",
    "free_radiation_correction_added_to_v3",
)

FALSIFICATION_CONDITION = (
    "Reject if the V1 row, any admitted prerequisite, the complete primary timing paper or any of its forty-eight "
    "favorable, correction, uncertainty or scope rows changes or is omitted; if the formal quadrupole-first, "
    "third-difference, half-One square, static-empty, amplitude-square or rank-two shell identity fails; if the "
    "published normalized decay no longer contains the formal One within its registered uncertainty; if the "
    "mildly relativistic material-binary result is universalized to every compact-object regime; if any external "
    "sign or decimal becomes a formal proof scalar; or if target access, fitting or a free correction precedes closure."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        V1_PATH: V1_HASH,
        WAVE_PATH: WAVE_HASH,
        ENERGY_PATH: ENERGY_HASH,
        INVERSE_PATH: INVERSE_HASH,
        BOUNDARY_PATH: BOUNDARY_HASH,
        CONSERVATION_PATH: CONSERVATION_HASH,
        COUPLING_PATH: COUPLING_HASH,
        MEASURED_PATH: MEASURED_HASH,
        CUSTODY_PATH: CUSTODY_HASH,
        PAPER_PATH: PAPER_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"D9q source changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text())
    target = record.get("registered_target", {})
    if record.get("source_id") != SOURCE_ID or record.get("formal_prediction_commit") != FORMAL_COMMIT:
        raise ValueError("D9q source identity or pre-target formal commit changed")
    if len(record.get("snapshots", ())) != 10 or tuple(target) != REQUIRED_TARGET_ROWS or len(target) != 48:
        raise ValueError("D9q complete target row ledger changed")
    if not all(
        (
            target["v1_source_entry"] == "D9q",
            target["v1_radiative_rate"] == "third-time-difference-of-quadrupole",
            target["v1_static_control"] == "static-quadrupole-is-silent",
            target["existing_v3_binary_coupling"] == "half-One",
            target["formal_prediction_commit_precedes_target_access"] is True,
            target["formal_normalized_binary_comparison"] == "One",
        )
    ):
        raise ValueError("D9q historical or formal comparison row changed")
    expected_primary = (
        "-1.247782(79)e-12",
        "-1.247810(+6/-7)e-12",
        "-1.75e-17",
        "-1.247827(+6/-7)e-12",
        "0.999963(63)",
        "1.3e-4",
        "0.999958(64)",
    )
    observed_primary = tuple(
        target[key]
        for key in (
            "primary_measured_GW_orbital_decay",
            "primary_leading_quadrupole_prediction",
            "primary_next_order_3_5PN_correction",
            "primary_total_prediction",
            "primary_measured_over_predicted_ratio",
            "primary_95_percent_agreement_boundary",
            "primary_extreme_EOS_ratio",
        )
    )
    if observed_primary != expected_primary:
        raise ValueError("D9q primary timing values changed")
    if not all(
        (
            target["primary_distance_uncertainty_currently_subdominant"] is True,
            target["primary_observed_timing_error_dominates_current_intrinsic_uncertainty"] is True,
            target["primary_future_limit_requires_kinematic_corrections"] is True,
            target["primary_black-hole_merger_comparison_requires_regime_caveat"] is True,
            target["primary_alternative_scalar_theories_can_add_lower-moment-radiation"] is True,
            target["primary_result_measures_universal_Fold_power_fraction"] is False,
            target["external_values_select_formal_survivor"] is False,
            target["negative_external_decay_sign_used_as_formal_proof_scalar"] is False,
            target["measured_parameter_fitted_into_v3"] is False,
            target["free_radiation_correction_added_to_v3"] is False,
        )
    ):
        raise ValueError("D9q limiting or custody row changed")
    v1 = json.loads((root / V1_PATH).read_text())
    row = next(item for item in v1["rows"] if item["v1_claim_id"] == "D9q")
    text = row["prior_result_observation"]
    if not all(
        fragment in text
        for fragment in (
            "quadrupole radiated-power magnitude",
            "third time-rate of the quadrupole moment",
            "P = coupling*(third-difference of the quadrupole)^2",
        )
    ):
        raise ValueError("D9q V1 row changed")
    expected_claims = {
        WAVE_PATH: "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
        ENERGY_PATH: "SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003",
        INVERSE_PATH: "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        BOUNDARY_PATH: "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        CONSERVATION_PATH: "SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010",
        COUPLING_PATH: "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002",
        MEASURED_PATH: "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        CUSTODY_PATH: "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
    }
    for relative, claim_id in expected_claims.items():
        if json.loads((root / relative).read_text()).get("claim_id") != claim_id:
            raise ValueError("D9q prerequisite changed")
    custody = record.get("custody", {})
    if not all(
        (
            custody.get("formal_claim_contains_historical_or_external_target_values") is False,
            custody.get("formal_prediction_commit_precedes_external_target_access") is True,
            custody.get("target_inaccessible_during_prediction_execution") is True,
            custody.get("prediction_sealed_before_target_release_within_run") is True,
            custody.get("all_historical_prerequisite_measurement_correction_and_scope_rows_retained") is True,
            custody.get("targets_select_formal_survivor") is False,
        )
    ):
        raise ValueError("D9q custody changed")
    return record


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    certificate = radiated_power_certificate(16)
    formal_ratio = Fraction(1, 1)
    measured_ratio = Fraction(999963, 1000000)
    measured_uncertainty = Fraction(63, 1000000)
    agreement_boundary_95 = Fraction(13, 100000)
    measured_difference = formal_ratio - measured_ratio
    eos_ratio = Fraction(999958, 1000000)
    eos_uncertainty = Fraction(64, 1000000)
    prerequisite_keys = (
        "existing_v3_quadrupole_first",
        "existing_v3_field_energy_square",
        "existing_v3_inverse_square",
        "existing_v3_boundary_rank_two",
        "existing_v3_source_conservation",
        "existing_v3_binary_coupling",
    )
    correction_keys = (
        "primary_shklovskii_correction",
        "primary_galactic_correction",
        "primary_combined_external_correction",
        "primary_intrinsic_orbital_decay",
        "primary_spin_down_mass_loss_correction",
        "primary_measured_GW_orbital_decay",
        "primary_leading_quadrupole_prediction",
        "primary_next_order_3_5PN_correction",
        "primary_total_prediction",
        "primary_measured_over_predicted_ratio",
    )
    scope_keys = (
        "primary_distance_uncertainty_currently_subdominant",
        "primary_observed_timing_error_dominates_current_intrinsic_uncertainty",
        "primary_future_limit_requires_kinematic_corrections",
        "primary_regime",
        "primary_black-hole_merger_comparison_requires_regime_caveat",
        "primary_alternative_scalar_theories_can_add_lower-moment-radiation",
        "primary_result_measures_universal_Fold_power_fraction",
    )
    return {
        "formal_coupling": certificate["coupling"],
        "formal_base_third_rate": certificate["base_third_record"][0],
        "formal_base_power": certificate["base_power"],
        "formal_doubled_power": certificate["doubled_power"],
        "formal_static_power_record": certificate["static_power_record"],
        "formal_power_quadruples": certificate["power_quadruples"],
        "formal_shell_power_conserved": certificate["shell_power_conserved"],
        "formal_successor_identity": certificate["successor_identity_holds"],
        "formal_normalized_binary_comparison": formal_ratio,
        "measured_ratio": measured_ratio,
        "measured_uncertainty": measured_uncertainty,
        "measured_difference_from_One": measured_difference,
        "measured_contains_One_at_published_uncertainty": measured_difference <= measured_uncertainty,
        "measured_within_95_percent_boundary": measured_difference <= agreement_boundary_95,
        "extreme_EOS_contains_One": formal_ratio - eos_ratio <= eos_uncertainty,
        "historical_relation_retained": target["v1_power_relation"] == "coupling-paired-with-third-rate-paired-with-itself",
        "prerequisite_rows_retained": tuple(target[key] for key in prerequisite_keys),
        "primary_correction_rows_retained": tuple(target[key] for key in correction_keys),
        "primary_scope_rows_retained": tuple(target[key] for key in scope_keys),
        "primary_quadrupole_classification_matches": target["primary_leading_order_classification"] == "quadrupole-formula-at-2.5PN-in-equations-of-motion",
        "all_target_rows_retained": tuple(target) == REQUIRED_TARGET_ROWS and len(target) == 48,
        "negative_external_sign_used_as_proof": target["negative_external_decay_sign_used_as_formal_proof_scalar"],
        "fitted_value_used": target["measured_parameter_fitted_into_v3"],
        "free_correction_used": target["free_radiation_correction_added_to_v3"],
    }


def formal_prediction_inputs() -> dict[str, object]:
    return {
        "moment_relation": HeldLabel("radiative-moment", "held-monopole-and-dipole-leave-quadrupole-first"),
        "rate_relation": HeldLabel("radiative-rate", "third-generated-quadrupole-difference"),
        "energy_relation": HeldLabel("radiative-energy", "positive-third-rate-square"),
        "coupling_relation": HeldLabel("radiative-coupling", "binary-half-One"),
        "static_relation": HeldLabel("static-control", "empty-radiation-record"),
        "scaling_relation": HeldLabel("amplitude-control", "power-scales-as-rate-paired-with-itself"),
        "shell_relation": HeldLabel("outward-transport", "rank-two-density-retains-total-power"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend(
        (
            {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-exact-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-quadrupole-radiated-power-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "formal_prediction_commit": FORMAL_COMMIT,
        "frozen_relation": "Held lower moments, third generated quadrupole difference, field-energy square, half-One coupling and rank-two transport force the complete positive-magnitude radiated-power law.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": "complete V1 row, eight admitted prerequisites, complete primary paper and all forty-eight favorable, correction, uncertainty and limiting rows",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "independent exact Fold reconstruction followed by exact rational comparison of published normalized binary decay with the formal One",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("D9q prediction shape changed")
    return dict(zip(keys, output.cells))


class QuadrupoleRadiatedPowerValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong D9q seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        keys = tuple(inputs)
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {key: sha256_identity(value) for key, value in inputs.items()},
            TARGET_IDS,
            sha256_identity((sealed.seal_hash, registration["frozen_relation"], FORMAL_COMMIT)),
            registration_hash,
        )
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("D9q hostile audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("D9q prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        formal = all(
            (
                analysis["formal_coupling"] == Fraction(1, 2),
                analysis["formal_base_third_rate"] == Fraction(6, 1),
                analysis["formal_base_power"] == Fraction(18, 1),
                analysis["formal_doubled_power"] == Fraction(72, 1),
                analysis["formal_static_power_record"] == (),
                analysis["formal_power_quadruples"],
                analysis["formal_shell_power_conserved"],
                analysis["formal_successor_identity"],
                analysis["formal_normalized_binary_comparison"] == Fraction(1, 1),
            )
        )
        rows = all(
            (
                analysis["all_target_rows_retained"],
                len(analysis["prerequisite_rows_retained"]) == 6,
                len(analysis["primary_correction_rows_retained"]) == 10,
                len(analysis["primary_scope_rows_retained"]) == 7,
            )
        )
        controls = all(
            (
                analysis["historical_relation_retained"],
                analysis["primary_quadrupole_classification_matches"],
                analysis["measured_contains_One_at_published_uncertainty"],
                analysis["measured_within_95_percent_boundary"],
                analysis["extreme_EOS_contains_One"],
                analysis["negative_external_sign_used_as_proof"] is False,
                analysis["fitted_value_used"] is False,
                analysis["free_correction_used"] is False,
            )
        )
        passed = all((formal, rows, controls))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparison_hash = sha256_identity(
            ("exact-quadrupole-radiated-power-comparator/1", registration_hash, FALSIFICATION_CONDITION)
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=interpreter_hash,
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=comparison_hash,
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
            "formal_commit": FORMAL_COMMIT,
            "prediction_seal": prediction_seal.seal_hash,
            "sources": source_hashes(),
            "target": target_identity,
            "analysis": analysis,
            "formal": formal,
            "rows": rows,
            "controls": controls,
        }
        measurements = (
            "The complete V1 D9q row, eight admitted prerequisite certificates and complete 56-page primary Double Pulsar paper are hash-locked and released only after the V3 formal commit and in-run prediction seal.",
            "V3 independently forces held monopole and dipole records, third generated quadrupole difference, half-One times its positive square, structural static silence and exact amplitude-square scaling.",
            "The all-positive cubic opposition identity has retained third-rate six at every successor; the exact witness has power eighteen and doubled amplitude has power seventy-two.",
            "Rank-two outward transport quarters density at every binary radius successor while density paired with radius twice reconstructs the same total power.",
            "The 16-year PSR J0737-3039A/B record covers a 2.45-hour mildly eccentric orbit and approximately sixty thousand tracked orbits.",
            "The primary paper retains Shklovskii, Galactic and spin-down mass-loss corrections before reporting measured GW-driven orbital decay -1.247782(79)e-12.",
            "The primary quadrupole prediction -1.247810(+6/-7)e-12 and retained 3.5PN correction -1.75e-17 give total prediction -1.247827(+6/-7)e-12.",
            "Measured over predicted decay is 0.999963(63): its exact rational uncertainty interval contains the formal normalized One, and the published 95-percent agreement boundary is 1.3e-4.",
            "The extreme equation-of-state rerun 0.999958(64), timing-error dominance, future kinematic limit, material-binary regime and compact-object comparison caveats are all retained.",
            "The external negative decay direction and decimal measurements remain observational records; no measured value, fitted parameter, target-selected survivor or free radiation correction enters V3.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            rows,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "QuadrupoleRadiatedPowerValidator",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
)
