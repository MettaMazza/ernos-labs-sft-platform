"""Capability-closed post-seal validator for Claim 070."""

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
from sft.physics.stellar_nuclear_collapse_terminal_empirical_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.stellar_nuclear_collapse_terminal_law_v1 import theorem_certificate


TARGET_IDS = ("STELLAR-NUCLEAR-COLLAPSE-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"stellar nuclear/collapse source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-stellar-nuclear-collapse-postseal-source-record/1":
        raise ValueError("stellar nuclear/collapse source schema changed")
    if record.get("formal_receipt_hash") != "sha256:a41b28a935f54de5daabdbe77b6c1aba9286f174526b8feaa60829ec848e08af":
        raise ValueError("formal stellar nuclear/collapse receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete ordered five-source vector required")
    boundary = record.get("methodological_boundary", {})
    if boundary.get("external_measurement_selected_formal_survivor") is not False:
        raise ValueError("measurement selected formal survivor")
    for key in ("all_six_stage_rows_and_nonmonotonic_duration_row_retained", "development_targets_already_known", "model_assisted_interpretations_identified", "observational_rows_opened_only_after_formal_receipt", "reported_signed_coordinate_not_used_as_fold_proof_scalar"):
        if boundary.get(key) is not True:
            raise ValueError("stellar nuclear/collapse methodological boundary changed")
    return record


def exact_analysis(record):
    sources = record["sources"]
    stages = sources[0]["rows"]["massive_star_burning_stages"]
    cno = sources[1]["rows"]["solar_cno_neutrino_detection"]
    collapse = sources[2]["rows"]["sn1987a_neutrino_reanalysis"]
    gamma = sources[3]["rows"]["sn2014j_nickel_cobalt_gamma_lines"]
    capture = sources[4]["rows"]["gw170817_strontium_identification"]
    stage_rows = tuple(stages["complete_rows"])
    temperatures = tuple(Fraction(row["stage_temperature_billion_kelvin"]) for row in stage_rows)
    durations = tuple(Fraction(row["duration_years"]) for row in stage_rows)
    ratio = Fraction(gamma["measured_line_ratio"])
    ratio_uncertainty = Fraction(gamma["measured_line_ratio_uncertainty"])
    branch = Fraction(gamma["reported_branch_ratio"])
    return {
        "stage_row_count": len(stage_rows),
        "declared_stage_row_count": stages["row_count"],
        "stage_temperatures_billion_kelvin": temperatures,
        "stage_temperatures_strict": all(left < right for left, right in zip(temperatures, temperatures[1:])),
        "stage_durations_years": durations,
        "all_stage_durations_retained": len(durations) == 6,
        "durations_strictly_decreasing": all(left > right for left, right in zip(durations, durations[1:])),
        "oxygen_neon_duration_irregularity_retained": durations[3] < durations[4],
        "onion_support_reported": stages["onion_support_reported"] is True,
        "cno_rate": Fraction(cno["cno_interaction_rate_cpd_per_100_tonnes"]),
        "cno_lower_uncertainty": Fraction(cno["lower_uncertainty_cpd_per_100_tonnes"]),
        "cno_upper_uncertainty": Fraction(cno["upper_uncertainty_cpd_per_100_tonnes"]),
        "cno_minimum_significance": Fraction(cno["minimum_significance_sigma"]),
        "cno_confidence": Fraction(cno["confidence_fraction"]),
        "collapse_detector_count": len(collapse["detectors"]),
        "collapse_probability_ratio": Fraction(collapse["minimum_two_to_one_component_probability_ratio"]),
        "collapse_accretion_duration_upper_seconds": Fraction(collapse["accretion_component_duration_upper_seconds"]),
        "collapse_model_assisted_retained": "model-assisted" in collapse["use_boundary"],
        "gamma_line_energies_kev": (Fraction(gamma["cobalt_line_1_energy_kev"]), Fraction(gamma["cobalt_line_2_energy_kev"])),
        "gamma_fluxes": (Fraction(gamma["cobalt_line_1_flux_1e_minus_4_ph_cm2_s"]), Fraction(gamma["cobalt_line_2_flux_1e_minus_4_ph_cm2_s"])),
        "gamma_flux_uncertainties": (Fraction(gamma["cobalt_line_1_flux_uncertainty"]), Fraction(gamma["cobalt_line_2_flux_uncertainty"])),
        "gamma_ratio_interval": (ratio - ratio_uncertainty, ratio + ratio_uncertainty),
        "gamma_branch_ratio": branch,
        "gamma_interval_contains_branch_ratio": ratio - ratio_uncertainty <= branch <= ratio + ratio_uncertainty,
        "gamma_spectrum_significance": Fraction(gamma["spectrum_nonempty_significance_sigma"]),
        "gamma_model_assisted_retained": "model-assisted" in gamma["use_boundary"],
        "capture_identified_element": capture["identified_element"],
        "capture_feature_nm": Fraction(capture["absorption_feature_nm"]),
        "capture_first_day": Fraction(capture["first_spectrum_days_after_merger"]),
        "capture_last_day": Fraction(capture["last_registered_spectrum_days_after_merger"]),
        "capture_broadening_c": Fraction(capture["feature_broadening_light_speed_fraction"]),
        "capture_blueshift_c": Fraction(capture["feature_blueshift_light_speed_fraction"]),
        "capture_model_assisted_retained": "modelling" in capture["use_boundary"],
        "all_sources_retained": len(sources) == 5,
    }


class StellarNuclearCollapseTerminalValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong stellar nuclear/collapse empirical seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets={TARGET_IDS[0]: authoritative_record(self.root)}, custody_nonce=sha256_identity((registration_hash, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("sealed stellar nuclear/collapse prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = all((formal["all_chains_strict"], formal["binding_terminal"]["unique"], formal["binding_terminal"]["tail_closed"], formal["support_loss"]["collapse_forced_when_no_other_support"], formal["all_thermonuclear_finite"], formal["all_neutral_capture_closed"]))
        empirical_pass = all((
            analysis["stage_row_count"] == analysis["declared_stage_row_count"] == 6,
            analysis["stage_temperatures_strict"], analysis["all_stage_durations_retained"],
            not analysis["durations_strictly_decreasing"], analysis["oxygen_neon_duration_irregularity_retained"], analysis["onion_support_reported"],
            analysis["cno_rate"] == Fraction(36, 5), analysis["cno_minimum_significance"] >= 5,
            analysis["collapse_detector_count"] == 3, analysis["collapse_probability_ratio"] >= 100, analysis["collapse_model_assisted_retained"],
            analysis["gamma_line_energies_kev"] == (847, 1238), analysis["gamma_interval_contains_branch_ratio"], analysis["gamma_spectrum_significance"] == Fraction(113, 10), analysis["gamma_model_assisted_retained"],
            analysis["capture_identified_element"] == "strontium", analysis["capture_feature_nm"] == 810, analysis["capture_model_assisted_retained"], analysis["all_sources_retained"],
        ))
        erased_stage = json.loads(json.dumps(record)); erased_stage["sources"][0]["rows"]["massive_star_burning_stages"]["complete_rows"].pop()
        erased_stage_rejected = exact_analysis(erased_stage)["stage_row_count"] != 6
        hidden_irregularity = json.loads(json.dumps(record)); hidden_irregularity["sources"][0]["rows"]["massive_star_burning_stages"]["complete_rows"][4]["duration_years"] = "1/1000"
        hidden_irregularity_rejected = not exact_analysis(hidden_irregularity)["oxygen_neon_duration_irregularity_retained"]
        erased_detector = json.loads(json.dumps(record)); erased_detector["sources"][2]["rows"]["sn1987a_neutrino_reanalysis"]["detectors"].pop()
        erased_detector_rejected = exact_analysis(erased_detector)["collapse_detector_count"] != 3
        outside_ratio = json.loads(json.dumps(record)); outside_ratio["sources"][3]["rows"]["sn2014j_nickel_cobalt_gamma_lines"]["measured_line_ratio_uncertainty"] = "1/100"
        outside_ratio_rejected = not exact_analysis(outside_ratio)["gamma_interval_contains_branch_ratio"]
        erased_capture = json.loads(json.dumps(record)); erased_capture["sources"][4]["rows"]["gw170817_strontium_identification"]["identified_element"] = "unidentified"
        erased_capture_rejected = exact_analysis(erased_capture)["capture_identified_element"] != "strontium"
        passed = all((formal_pass, empirical_pass, erased_stage_rejected, hidden_irregularity_rejected, erased_detector_rejected, outside_ratio_rejected, erased_capture_rejected))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-stellar-nuclear-collapse-comparator/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "formal": formal_pass, "controls": (erased_stage_rejected, hidden_irregularity_rejected, erased_detector_rejected, outside_ratio_rejected, erased_capture_rejected)}
        measurements = (
            "All six stellar stages have strictly increasing measured temperatures; every duration, including the nonmonotonic neon/oxygen pair, is retained.",
            "Borexino directly records CNO fusion neutrinos at 36/5 +3 -17/10 cpd per 100 tonnes and at least five-sigma significance.",
            "The complete three-detector SN1987A neutrino record is retained, with model preference explicitly identified as model-assisted.",
            "Both SN2014J cobalt lines, flux errors and ratio are retained; the measured ratio interval contains 17/25.",
            "GW170817 spectroscopy identifies strontium while retaining every spectral-modelling boundary.",
            "Erased-stage, hidden-irregularity, erased-detector, outside-ratio and erased-capture controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_sources_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("FALSIFICATION_CONDITION", "StellarNuclearCollapseTerminalValidator", "TARGET_IDS", "authoritative_record", "exact_analysis", "source_hashes")
