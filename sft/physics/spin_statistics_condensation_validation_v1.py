"""Exact post-seal evaluator for finite BEC, Pauli blocking and spinor return."""

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
from sft.physics.spin_statistics_condensation_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("SPIN-STATISTICS-CONDENSATION-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"spin-statistics source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-spin-statistics-condensation-postseal-source-record/1":
        raise ValueError("spin-statistics source schema changed")
    if record.get("formal_receipt_hash") != "sha256:f71da5b86f99d6569a1f33dc6fc37024cc5d458b12e625c5dbc4faf3c33ccda7":
        raise ValueError("formal spin-statistics receipt binding changed")
    if len(record.get("sources", ())) != 3:
        raise ValueError("complete three-source spin-statistics record required")
    return record


def exact_spin_statistics_analysis(target):
    bec_center = int(target["bec_transition_ratio_center"])
    bec_uncertainty = int(target["bec_transition_ratio_uncertainty"])
    bec_denominator = int(target["bec_transition_ratio_denominator"])
    spin_forced = int(target["spinor_forced_return_degrees"])
    spin_center = int(target["spinor_measured_return_degrees_center"])
    spin_uncertainty = int(target["spinor_measured_return_degrees_uncertainty"])
    bec_interval = (bec_center - bec_uncertainty, bec_center + bec_uncertainty)
    spin_interval = (spin_center - spin_uncertainty, spin_center + spin_uncertainty)
    return {
        "positive_exact_carriers": all(
            value > 0
            for value in (
                *bec_interval,
                bec_uncertainty,
                bec_denominator,
                int(target["bec_reported_finite_population_correction_percent"]),
                int(target["pauli_spin_state_count"]),
                int(target["pauli_collision_cross_section_reduction_factor"]),
                spin_forced,
                spin_uncertainty,
                *spin_interval,
            )
        ),
        "bec_interval": bec_interval,
        "spinor_interval": spin_interval,
        "bec_interval_ordered": bec_interval[0] <= bec_interval[1] < bec_denominator + 1,
        "bec_finite_population": target["bec_finite_population_measurement"] is True,
        "bec_ground_measured": target["bec_ground_state_occupation_measured"] is True,
        "bec_cooling_direction": target["bec_ground_share_increases_as_temperature_is_lowered"] is True,
        "bec_transition_observed": target["bec_sharp_transition_feature_observed"] is True,
        "pauli_observed": target["pauli_blocking_directly_observed"] is True,
        "pauli_two_spin_states": int(target["pauli_spin_state_count"]) == 2,
        "pauli_reported_factor_retained": int(target["pauli_collision_cross_section_reduction_factor"]) == 2,
        "spinor_interval_contains_forced_return": spin_interval[0] <= spin_forced <= spin_interval[1],
        "spinor_one_turn_changes": target["spinor_one_turn_changes_held_orientation"] is True,
        "spinor_two_turns_restore": target["spinor_two_turns_restore_identical_state"] is True,
        "all_rows_retained": target["all_registered_rows_retained"] is True,
    }


class SpinStatisticsCondensationValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong spin-statistics seal")
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
            raise ValueError("spin-statistics prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("spin-statistics prediction label changed")
        analysis = exact_spin_statistics_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all(
            analysis[key]
            for key in (
                "positive_exact_carriers",
                "bec_interval_ordered",
                "bec_finite_population",
                "bec_ground_measured",
                "bec_cooling_direction",
                "bec_transition_observed",
                "pauli_observed",
                "pauli_two_spin_states",
                "pauli_reported_factor_retained",
                "spinor_interval_contains_forced_return",
                "spinor_one_turn_changes",
                "spinor_two_turns_restore",
                "all_rows_retained",
            )
        )
        tampered_spinor = dict(context[TARGET_IDS[0]])
        tampered_spinor["spinor_measured_return_degrees_center"] = 600
        tampered_spinor_rejected = not exact_spin_statistics_analysis(tampered_spinor)["spinor_interval_contains_forced_return"]
        tampered_bec = dict(context[TARGET_IDS[0]])
        tampered_bec["bec_ground_share_increases_as_temperature_is_lowered"] = False
        tampered_bec_rejected = not exact_spin_statistics_analysis(tampered_bec)["bec_cooling_direction"]
        passed = formal and empirical and tampered_spinor_rejected and tampered_bec_rejected
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-spin-statistics-condensation-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "empirical": empirical,
            "tampered_spinor_rejected": tampered_spinor_rejected,
            "tampered_bec_rejected": tampered_bec_rejected,
        }
        measurements = (
            "Finite rubidium-87 Bose gas ground occupation is measured and rises as temperature is lowered.",
            "BEC transition interval is [89,99]/100 of the declared trap scale; its finite-population correction remains retained.",
            "Two-spin-state potassium-40 gas directly exhibits Pauli blocking and the reported factor-two collision reduction.",
            "Neutron spinor interval [666,742] degrees contains the sealed two-turn 720-degree return.",
            "One turn changes the held spinor orientation and two turns restore the identical state.",
            "Trap-specific BEC and collision-response magnitudes remain external scale records, not formal-law selectors.",
            "Tampered spinor and reversed-cooling controls reject.",
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
    "FALSIFICATION_CONDITION",
    "TARGET_IDS",
    "SpinStatisticsCondensationValidator",
    "authoritative_record",
    "exact_spin_statistics_analysis",
    "source_hashes",
)
