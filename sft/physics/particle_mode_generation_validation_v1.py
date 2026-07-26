"""Exact evaluator for the complete particle-generation external vector."""

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
from sft.physics.charged_lepton_validation import comparison_record
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.matter_flavour_terminal_ckm_validation_v1 import terminal_ckm_classification
from sft.physics.matter_flavour_validation_v1 import neutrino_classification, quark_ckm_classification
from sft.physics.particle_mode_generation_empirical_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.terminal_lepton_law import terminal_product_invariant


TARGET_IDS = ("PARTICLE-MODE-GENERATION-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"particle-mode generation source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-particle-mode-generation-postseal-source-record/1":
        raise ValueError("particle-mode generation source schema changed")
    if record.get("formal_receipt_hash") != "sha256:18e4aac0792a01c613d31f4d980951b0e2da69107155c4e50967ed80c9eaa700":
        raise ValueError("particle-mode generation formal binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete five-source particle-mode record required")
    boundary = record.get("interpretive_boundary", {})
    required_true = tuple(key for key in boundary if key not in {"measurement_selected_formal_survivor", "blind_forward_discovery_claimed"})
    if not all(boundary.get(key) is True for key in required_true) or boundary.get("measurement_selected_formal_survivor") is not False or boundary.get("blind_forward_discovery_claimed") is not False:
        raise ValueError("particle-mode interpretation boundary changed")
    return record


def exact_particle_mode_analysis(target):
    forced = int(target["generation_count_forced"])
    fit_center = int(target["neutrino_type_fit_center"])
    fit_uncertainty = int(target["neutrino_type_fit_uncertainty"])
    fit_denominator = int(target["neutrino_type_fit_denominator"])
    direct_center = int(target["neutrino_type_direct_center"])
    direct_uncertainty = int(target["neutrino_type_direct_uncertainty"])
    direct_denominator = int(target["neutrino_type_direct_denominator"])
    fit_interval = (fit_center - fit_uncertainty, fit_center + fit_uncertainty)
    direct_interval = (direct_center - direct_uncertainty, direct_center + direct_uncertainty)
    direct_displacement = (forced * direct_denominator - direct_center, direct_uncertainty)
    masses = tuple(Fraction(target[f"{name}_mass_MeV"]) for name in ("electron", "muon", "tau"))
    mass_uncertainties = tuple(Fraction(target[f"{name}_mass_uncertainty_MeV"]) for name in ("electron", "muon", "tau"))
    mass_intervals = tuple((center - uncertainty, center + uncertainty) for center, uncertainty in zip(masses, mass_uncertainties))
    electron_life_seconds_lower = Fraction(target["electron_mean_life_lower_years"]) * 31536000
    muon_life = Fraction(target["muon_mean_life_seconds"])
    muon_uncertainty = Fraction(target["muon_mean_life_uncertainty_seconds"])
    tau_life = Fraction(target["tau_mean_life_seconds"])
    tau_uncertainty = Fraction(target["tau_mean_life_uncertainty_seconds"])
    return {
        "positive_exact_carriers": all(value > 0 for value in (*fit_interval, *direct_interval, *direct_displacement, *masses, *mass_uncertainties, electron_life_seconds_lower, muon_life, muon_uncertainty, tau_life, tau_uncertainty)),
        "fit_interval": fit_interval,
        "direct_interval": direct_interval,
        "direct_standard_uncertainty_displacement": direct_displacement,
        "fit_contains_three": fit_interval[0] <= forced * fit_denominator <= fit_interval[1],
        "direct_row_exactly_eight_fifths_from_three": direct_displacement == (8, 5),
        "measurement_boundaries_retained": target["neutrino_fit_is_model_dependent"] is True and target["neutrino_direct_row_retained_without_adjustment"] is True and target["neutrino_direct_row_did_not_select_the_forced_count"] is True,
        "charged_lepton_mass_intervals_strictly_ordered": mass_intervals[0][1] < mass_intervals[1][0] < mass_intervals[2][0],
        "charged_lepton_lifetimes_reverse_order": electron_life_seconds_lower > muon_life + muon_uncertainty > tau_life + tau_uncertainty,
        "declared_mass_order_retained": tuple(target["charged_lepton_mass_order"]) == ("electron", "muon", "tau"),
        "declared_lifetime_order_retained": tuple(target["charged_lepton_lifetime_order"]) == ("electron", "muon", "tau"),
        "terminal_lepton_ratios_pass": target["terminal_charged_lepton_both_mass_ratio_intervals_pass"] is True,
        "available_quark_ratios_pass": target["terminal_quark_s_over_d_interval_passes"] is True and target["terminal_quark_b_over_s_interval_passes"] is True,
        "top_charm_boundary_retained": target["terminal_quark_t_over_c_has_no_exact_scheme_matched_direct_comparator"] is True,
        "terminal_ckm_vector_pass": target["terminal_CKM_complete_four_row_vector_passes_three_standard_uncertainty_intervals"] is True,
        "positive_neutrino_vector_pass": target["positive_neutrino_PMNS_CP_vector_passes_registered_three_standard_uncertainty_support"] is True and target["positive_neutrino_mass_sum_below_registered_direct_and_cosmological_bounds"] is True,
        "ordering_boundary_retained": target["normal_neutrino_ordering_not_decisively_measured"] is True,
        "heavy_lepton_search_limits_positive": Fraction(target["heavy_charged_lepton_search_lower_mass_GeV"]) > 0 and Fraction(target["stable_heavy_charged_lepton_search_lower_mass_GeV"]) > 0,
        "all_rows_retained": target["all_registered_rows_retained"] is True,
    }


class ParticleModeGenerationValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong particle-mode empirical seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets=targets, custody_nonce=sha256_identity((registration_hash, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("particle-mode prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("particle-mode prediction label changed")
        analysis = exact_particle_mode_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        external_recomputations = all((
            comparison_record(self.root, terminal_product_invariant())["all_rows_passed"],
            quark_ckm_classification(self.root).startswith("dressed-sd-and-bs-inside"),
            terminal_ckm_classification(self.root).startswith("terminal-CKM-s12-s23-s13-and-J-all-overlap"),
            neutrino_classification(self.root).startswith("positive-normal-neutrino-mass-structure"),
        ))
        empirical = all(value for key, value in analysis.items() if key not in {"fit_interval", "direct_interval", "direct_standard_uncertainty_displacement"})
        tampered_fit = dict(context[TARGET_IDS[0]]); tampered_fit["neutrino_type_fit_center"] = 2800
        tampered_fit_rejected = not exact_particle_mode_analysis(tampered_fit)["fit_contains_three"]
        altered_direct_record = dict(context[TARGET_IDS[0]]); altered_direct_record["neutrino_direct_row_retained_without_adjustment"] = False
        altered_direct_record_rejected = not exact_particle_mode_analysis(altered_direct_record)["measurement_boundaries_retained"]
        reversed_lifetime = dict(context[TARGET_IDS[0]]); reversed_lifetime["tau_mean_life_seconds"] = "3"
        reversed_lifetime_rejected = not exact_particle_mode_analysis(reversed_lifetime)["charged_lepton_lifetimes_reverse_order"]
        passed = formal and external_recomputations and empirical and tampered_fit_rejected and altered_direct_record_rejected and reversed_lifetime_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-particle-mode-generation-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "formal": formal, "external_recomputations": external_recomputations, "tampered_fit_rejected": tampered_fit_rejected, "altered_direct_record_rejected": altered_direct_record_rejected, "reversed_lifetime_rejected": reversed_lifetime_rejected}
        measurements = (
            "The precision fitted neutrino-type interval [2989,3003]/1000 contains the forced count three.",
            "The independent direct determination 292/100 with stated uncertainty 5/100 is retained without adjustment.",
            "Its exact central-value displacement from three is 8/5 stated uncertainties; it does not select or alter the forced law.",
            "Both terminal charged-lepton ratios, available s/d and b/s ratios, all terminal CKM rows and the positive-neutrino vector pass their registered comparisons.",
            "No exact scheme-matched direct t/c comparator is claimed.",
            "Charged-lepton mass intervals increase electron-muon-tau and lifetimes decrease in the same label order.",
            "Heavy-lepton search limits, measurement-model provenance and nondecisive neutrino-ordering boundaries are retained.",
            "No coordinate fraction is relabelled as mass and no structural reach count is relabelled as seconds.",
            "Tampered fit, altered direct record and reversed-lifetime controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("FALSIFICATION_CONDITION", "TARGET_IDS", "ParticleModeGenerationValidator", "authoritative_record", "exact_particle_mode_analysis", "source_hashes")
