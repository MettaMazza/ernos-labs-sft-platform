"""Exact post-seal evaluation of the thermal-history observation record."""

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
from sft.physics.thermal_history_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("THERMAL-HISTORY-WITHHELD-COMPLETE-OBSERVATION-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes() -> dict[str, str]:
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"thermal-history source identity changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-thermal-history-postseal-source-record/1":
        raise ValueError("thermal-history source schema changed")
    if record.get("formal_receipt_hash") != "sha256:25dda78644ebc04ad43cd3e416950ad76dae6b124ed023f41364f0661eae9c00":
        raise ValueError("thermal-history formal receipt binding changed")
    if len(record.get("sources", ())) != 6:
        raise ValueError("complete six-source record is required")
    target = record.get("registered_target", {})
    expected = {
        "cmb_temperature_exponent_central": "1.007",
        "cmb_temperature_exponent_standard_uncertainty": "0.027",
        "primordial_helium_mass_fraction_central": "0.2458",
        "primordial_helium_mass_fraction_standard_uncertainty": "0.0013",
        "primordial_deuterium_times_100000_central": "2.527",
        "primordial_deuterium_times_100000_standard_uncertainty": "0.030",
        "planck_recombination_redshift_central": "1089.92",
        "planck_recombination_redshift_standard_uncertainty": "0.25",
        "planck_detected_peak_count": 18,
    }
    if any(target.get(key) != value for key, value in expected.items()):
        raise ValueError("thermal-history target row changed")
    if len(target.get("planck_tt_peak_multipoles", ())) != 7 or len(target.get("planck_tt_peak_amplitudes", ())) != 7:
        raise ValueError("complete Planck TT peak rows are required")
    custody = record.get("row_custody", {})
    if not all(custody.get(key) is True for key in (
        "formal_receipt_precedes_new_source_retrieval",
        "target_inaccessible_to_formal_executable",
        "target_did_not_rewrite_formal_survivor",
        "current_unfavourable_helium_interval_retained",
        "old_exact_observed-quarter-equality_rejected",
        "old_exact_angular-integer-multiple_claim_rejected",
        "projection_and_visibility_types_retained",
        "complete_uncertainty_and_peak_rows_retained",
    )):
        raise ValueError("thermal-history custody record changed")
    return record


def exact_thermal_analysis(target: dict[str, object]) -> dict[str, object]:
    exponent = Fraction(target["cmb_temperature_exponent_central"])
    exponent_width = Fraction(target["cmb_temperature_exponent_standard_uncertainty"])
    exponent_interval = (exponent - exponent_width, exponent + exponent_width)
    helium = Fraction(target["primordial_helium_mass_fraction_central"])
    helium_width = Fraction(target["primordial_helium_mass_fraction_standard_uncertainty"])
    helium_interval = (helium - helium_width, helium + helium_width)
    deuterium = Fraction(target["primordial_deuterium_times_100000_central"]) / 100000
    deuterium_width = Fraction(target["primordial_deuterium_times_100000_standard_uncertainty"]) / 100000
    recombination = Fraction(target["planck_recombination_redshift_central"])
    recombination_width = Fraction(target["planck_recombination_redshift_standard_uncertainty"])
    peak_centres = tuple(Fraction(value) for value in target["planck_tt_peak_multipoles"])
    peak_widths = tuple(Fraction(value) for value in target["planck_tt_peak_multipole_uncertainties"])
    peak_intervals = tuple((centre - width, centre + width) for centre, width in zip(peak_centres, peak_widths))
    first = peak_intervals[0]
    integer_overlap = []
    for mode, interval in enumerate(peak_intervals[1:], start=2):
        scaled_first = (mode * first[0], mode * first[1])
        integer_overlap.append(not (scaled_first[1] < interval[0] or interval[1] < scaled_first[0]))
    amplitudes = tuple(Fraction(value) for value in target["planck_tt_peak_amplitudes"])
    amplitude_widths = tuple(Fraction(value) for value in target["planck_tt_peak_amplitude_uncertainties"])
    return {
        "temperature_exponent_interval": exponent_interval,
        "exact_one_inside_temperature_interval": exponent_interval[0] <= Fraction(1) <= exponent_interval[1],
        "helium_interval": helium_interval,
        "analytic_quarter": Fraction(1, 4),
        "exact_quarter_excluded": Fraction(1, 4) > helium_interval[1],
        "helium_gap_from_analytic_quarter": Fraction(1, 4) - helium,
        "deuterium_interval": (deuterium - deuterium_width, deuterium + deuterium_width),
        "deuterium_positive_minor_channel": deuterium - deuterium_width > 0 and deuterium + deuterium_width < helium_interval[0],
        "recombination_interval": (recombination - recombination_width, recombination + recombination_width),
        "finite_positive_recombination_support": recombination_width > 0 and recombination - recombination_width > 0,
        "peak_intervals": peak_intervals,
        "complete_seven_tt_peaks": len(peak_intervals) == len(amplitudes) == len(amplitude_widths) == 7,
        "detected_peak_count": target["planck_detected_peak_count"],
        "finite_eighteen_peak_record": target["planck_detected_peak_count"] == 18,
        "angular_integer_multiple_claim_rejected": not any(integer_overlap),
        "freezeout_sequence_retained": target["pdg_freezeout_neutron_proton_label"] == "approximately 1/6" and target["pdg_capture_entry_neutron_proton_label"] == "approximately 1/7",
        "analytic_quarter_label_retained": target["pdg_analytic_helium_partition_label"] == "approximately 0.25",
        "all_rows_retained": target["all_registered_rows_retained"],
    }


class ThermalHistoryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong thermal-history comparison seal")
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
            raise ValueError("thermal-history prediction package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("thermal-history prediction label changed")
        analysis = exact_thermal_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all((
            analysis["exact_one_inside_temperature_interval"],
            analysis["exact_quarter_excluded"],
            analysis["deuterium_positive_minor_channel"],
            analysis["finite_positive_recombination_support"],
            analysis["complete_seven_tt_peaks"],
            analysis["finite_eighteen_peak_record"],
            analysis["angular_integer_multiple_claim_rejected"],
            analysis["freezeout_sequence_retained"],
            analysis["analytic_quarter_label_retained"],
            analysis["all_rows_retained"],
        ))
        tampered = dict(context[TARGET_IDS[0]])
        tampered["cmb_temperature_exponent_central"] = "1.100"
        tampered_rejected = not exact_thermal_analysis(tampered)["exact_one_inside_temperature_interval"]
        passed = formal and empirical and tampered_rejected
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-thermal-history-comparator/1", registration_hash, FALSIFICATION_CONDITION))
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
        payload = {"seal": sealed.seal_hash, "source_hashes": source_hashes(), "target_identity": target_identity, "analysis": analysis, "formal": formal, "empirical": empirical, "tampered_rejected": tampered_rejected}
        measurements = (
            "The formal thermal-history law was admitted before the new primary snapshots were retrieved.",
            "Direct high-redshift CMB thermometry contains exact exponent One.",
            "The external freeze-out sequence is approximately One/six then One/seven.",
            "Current direct helium measurement excludes exact One/four; the old exact measured-equality reading is rejected without fitting.",
            "Direct primordial deuterium remains a positive minor light-nuclide channel.",
            "Planck retains finite recombination support, eighteen extrema and all seven TT peak rows.",
            "Observed angular multipoles reject exact integer multiples of the first peak, preserving the internal-mode/projection distinction.",
            "A tampered temperature exponent rejects the comparison.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("FALSIFICATION_CONDITION", "TARGET_IDS", "ThermalHistoryValidator", "authoritative_record", "exact_thermal_analysis", "source_hashes")
