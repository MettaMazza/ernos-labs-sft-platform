"""Exact post-seal evaluator for acoustic and Johnson-noise thermometry."""

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
from sft.physics.thermal_equilibrium_empirical_v1 import (
    CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH,
    SOURCE_IDS, SOURCE_PATH, SPEC,
)


TARGET_IDS = ("THERMAL-EQUILIBRIUM-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"thermal-equilibrium source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-thermal-equilibrium-postseal-source-record/1":
        raise ValueError("thermal-equilibrium source schema changed")
    if record.get("formal_receipt_hash") != "sha256:cf536f7516eb1c85bb075500d9c1a0ebd64bdddb544878f26a27424d08de25bf":
        raise ValueError("formal thermal-equilibrium receipt binding changed")
    if len(record.get("sources", ())) != 3:
        raise ValueError("complete three-source thermometry record required")
    return record


def exact_thermal_analysis(target):
    exact = int(target["exact_si_kb_scaled"])
    acoustic_center = int(target["acoustic_kb_scaled_center"])
    acoustic_uncertainty = int(target["acoustic_kb_scaled_standard_uncertainty"])
    electronic_center = int(target["electronic_kb_scaled_center"])
    electronic_uncertainty = int(target["electronic_kb_scaled_standard_uncertainty"])
    acoustic_interval = (acoustic_center - acoustic_uncertainty, acoustic_center + acoustic_uncertainty)
    electronic_interval = (electronic_center - electronic_uncertainty, electronic_center + electronic_uncertainty)
    return {
        "positive_exact_carriers": all(
            value > 0
            for value in (
                *acoustic_interval,
                *electronic_interval,
                exact,
                acoustic_uncertainty,
                electronic_uncertainty,
                int(target["scale_denominator"]),
            )
        ) and acoustic_interval[0] <= acoustic_interval[1] and electronic_interval[0] <= electronic_interval[1],
        "acoustic_interval": acoustic_interval,
        "electronic_interval": electronic_interval,
        "acoustic_contains_exact": acoustic_interval[0] <= exact <= acoustic_interval[1],
        "electronic_contains_exact": electronic_interval[0] <= exact <= electronic_interval[1],
        "route_count_exact": int(target["measurement_route_count"]) == 2,
        "routes_distinct": target["measurement_routes_physically_distinct"] is True,
        "kinetic_temperature_relation": target["acoustic_temperature_measures_average_kinetic_energy"] is True,
        "johnson_response_relation": target["electronic_johnson_noise_power_depends_on_resistance_and_temperature"] is True,
        "johnson_accuracy_retained": int(target["electronic_johnson_relation_accuracy_parts_per_million"]) == 1,
        "dyadic_direct_measurement_not_claimed": target["universal_dyadic_population_ladder_reported_as_measured"] is False,
        "fold_response_direct_measurement_not_claimed": target["three_quarter_response_reported_as_universal_measured_value"] is False,
        "all_rows_retained": target["all_registered_rows_retained"] is True,
    }


class ThermalEquilibriumValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong thermal-equilibrium seal")
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
            raise ValueError("thermal-equilibrium prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("thermal-equilibrium prediction label changed")
        analysis = exact_thermal_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all(
            analysis[key]
            for key in (
                "positive_exact_carriers", "acoustic_contains_exact", "electronic_contains_exact",
                "route_count_exact", "routes_distinct", "kinetic_temperature_relation",
                "johnson_response_relation", "johnson_accuracy_retained",
                "dyadic_direct_measurement_not_claimed", "fold_response_direct_measurement_not_claimed",
                "all_rows_retained",
            )
        )
        tampered = dict(context[TARGET_IDS[0]])
        tampered["acoustic_kb_scaled_center"] = 13000000
        tampered_rejected = not exact_thermal_analysis(tampered)["acoustic_contains_exact"]
        passed = formal and empirical and tampered_rejected
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-thermal-equilibrium-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "tampered_rejected": tampered_rejected,
        }
        measurements = (
            "Exact SI k_B is 13806490/10^30 J/K.",
            "Acoustic interval [13806456,13806512]/10^30 J/K contains exact SI k_B.",
            "Johnson-noise interval [13806340,13806680]/10^30 J/K contains exact SI k_B.",
            "Acoustic and electronic routes are physically distinct and both remain complete.",
            "Acoustic thermometry retains the mean-kinetic-energy temperature relation.",
            "Johnson noise retains joint temperature/resistance response at the reported one-part-per-million regime.",
            "No direct universal measurement is claimed for the dyadic ladder or 3/4:1/4 Fold coordinates.",
            "Tampered acoustic interval excludes the exact carrier and rejects.",
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
    "FALSIFICATION_CONDITION", "TARGET_IDS", "ThermalEquilibriumValidator",
    "authoritative_record", "exact_thermal_analysis", "source_hashes",
)
