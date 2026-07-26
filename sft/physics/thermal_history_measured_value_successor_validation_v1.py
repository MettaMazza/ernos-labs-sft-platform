"""Exact post-seal evaluator for corrected thermal-history measurements."""

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
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.helium_isotope_closure_terminal_law_v1 import isotope_closure_ledger
from sft.physics.thermal_history_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC


TARGET_IDS = ("THERMAL-HISTORY-WITHHELD-COMPLETE-MEASURED-VALUE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"thermal successor source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-thermal-history-measured-value-successor-source-record/1":
        raise ValueError("thermal successor schema changed")
    if record.get("physical_isotope_receipt_hash") != "sha256:a3b3a44a0d3add7032680427c3b2b504147c0eb824d05fa5d044cef454c5ebc4":
        raise ValueError("physical helium receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete thermal source vector required")
    boundary = record.get("methodological_boundary", {})
    if not all(value is True for key, value in boundary.items() if key != "measurement_selected_formal_survivor"):
        raise ValueError("thermal methodological boundary changed")
    if boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("thermal measurement-selection boundary changed")
    original = json.loads((root / record["registered_target_source"]["path"]).read_text(encoding="utf-8"))
    return {"record": record, "original": original}


def interval(center: str, uncertainty: str):
    centre, width = Fraction(center), Fraction(uncertainty)
    if centre <= width or width <= 0:
        raise ValueError("thermal interval must remain positive")
    return centre - width, centre + width


def exact_thermal_analysis(target):
    record, original = target["record"], target["original"]
    measured = original["registered_target"]
    temperature = interval(measured["cmb_temperature_exponent_central"], measured["cmb_temperature_exponent_standard_uncertainty"])
    helium = interval(measured["primordial_helium_mass_fraction_central"], measured["primordial_helium_mass_fraction_standard_uncertainty"])
    deuterium = interval(measured["primordial_deuterium_times_100000_central"], measured["primordial_deuterium_times_100000_standard_uncertainty"])
    physical_helium = isotope_closure_ledger()["physical_helium_isotope_share"]
    peak_positions = tuple(Fraction(value) for value in measured["planck_tt_peak_multipoles"])
    peak_position_uncertainties = tuple(Fraction(value) for value in measured["planck_tt_peak_multipole_uncertainties"])
    peak_amplitudes = tuple(Fraction(value) for value in measured["planck_tt_peak_amplitudes"])
    peak_amplitude_uncertainties = tuple(Fraction(value) for value in measured["planck_tt_peak_amplitude_uncertainties"])
    return {
        "temperature_exponent_interval": temperature,
        "physical_helium_interval": helium,
        "deuterium_scaled_interval": deuterium,
        "physical_helium_exact": physical_helium,
        "temperature_exponent_One_passed": temperature[0] <= 1 <= temperature[1],
        "physical_helium_59_over_240_passed": helium[0] <= physical_helium <= helium[1],
        "analytic_and_physical_helium_separately_typed": record["methodological_boundary"]["analytic_quarter_and_physical_59_over_240_are_separately_typed"] is True,
        "deuterium_positive_minor_channel": deuterium[0] > 0 and deuterium[1] / 100000 < helium[0],
        "freezeout_sequence_retained": measured["pdg_freezeout_neutron_proton_label"] == "approximately 1/6" and measured["pdg_capture_entry_neutron_proton_label"] == "approximately 1/7",
        "finite_recombination_record_retained": Fraction(measured["planck_recombination_redshift_central"]) > Fraction(measured["planck_recombination_redshift_standard_uncertainty"]) > 0,
        "complete_peak_census_retained": measured["planck_detected_peak_count"] == 18 and len(peak_positions) == len(peak_position_uncertainties) == len(peak_amplitudes) == len(peak_amplitude_uncertainties) == 7,
        "all_peak_rows_positive": all(value > 0 for values in (peak_positions, peak_position_uncertainties, peak_amplitudes, peak_amplitude_uncertainties) for value in values),
        "projection_boundary_retained_without_mismatch_reward": record["methodological_boundary"]["angular_projection_rows_are_method_records_not_exact_internal_mode_values"] is True and record["methodological_boundary"]["noninteger_angular_positions_are_not_rewarded_as_a_result"] is True,
        "all_source_rows_retained": record["registered_target_source"]["all_original_rows_retained"] is True and measured["all_registered_rows_retained"] is True,
    }


class ThermalHistoryMeasuredValueSuccessorValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong thermal successor seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        target = authoritative_record(self.root)
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets={TARGET_IDS[0]: target}, custody_nonce=sha256_identity((registration_hash, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("thermal successor prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("thermal successor prediction label changed")
        released = context[TARGET_IDS[0]]
        analysis = exact_thermal_analysis(released)
        non_boolean = {"temperature_exponent_interval", "physical_helium_interval", "deuterium_scaled_interval", "physical_helium_exact"}
        empirical = all(value for key, value in analysis.items() if key not in non_boolean)
        tampered_helium = json.loads(json.dumps(released))
        tampered_helium["original"]["registered_target"]["primordial_helium_mass_fraction_central"] = "0.2300"
        tampered_helium["original"]["registered_target"]["primordial_helium_mass_fraction_standard_uncertainty"] = "0.0001"
        tampered_helium_rejected = not exact_thermal_analysis(tampered_helium)["physical_helium_59_over_240_passed"]
        tampered_peaks = json.loads(json.dumps(released))
        tampered_peaks["original"]["registered_target"]["planck_detected_peak_count"] = 17
        tampered_peaks_rejected = not exact_thermal_analysis(tampered_peaks)["complete_peak_census_retained"]
        passed = all(row[2] for row in SPEC.operational_witnesses) and empirical and tampered_helium_rejected and tampered_peaks_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-thermal-history-measured-value-successor/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "tampered_helium_rejected": tampered_helium_rejected, "tampered_peaks_rejected": tampered_peaks_rejected}
        measurements = (
            "Exact CMB temperature exponent One lies inside [49/50,517/500].",
            "Exact physical primordial helium share 59/240 lies inside [489/2000,2471/10000].",
            "The one-sixth to one-seventh freezeout sequence and positive deuterium channel remain complete.",
            "Finite recombination support, eighteen extrema and all seven TT rows remain source-bound and positive; angular projection records are not mismatch results.",
            "No uncertainty was widened; displaced helium and incomplete-peak controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_source_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("ThermalHistoryMeasuredValueSuccessorValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_thermal_analysis", "source_hashes")
