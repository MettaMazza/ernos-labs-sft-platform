"""Capability-closed post-seal validator for Claim 064."""

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
from sft.physics.strong_cp_baryon_stability_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.strong_cp_baryon_stability_terminal_law_v1 import EMPTY_ONE, ONE, theorem_certificate


TARGET_IDS = ("STRONG-CP-BARYON-STABILITY-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"strong-CP/baryon source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-strong-cp-baryon-stability-postseal-source-record/1":
        raise ValueError("strong-CP/baryon source schema changed")
    if record.get("formal_receipt_hash") != "sha256:6bd69d2eb78150c11fefc82f512bdfd775eaa2f3a2667127407d7a34bd695657":
        raise ValueError("formal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete four-source vector required")
    boundary = record.get("methodological_boundary", {})
    required_true = (
        "all_registered_modes_and_uncertainties_retained",
        "background_compatible_candidates_not_relabelled_as_decay",
        "finite_limits_not_relabelled_as_completed_infinity",
        "null_central_estimate_not_relabelled_as_numerical_proof_zero",
    )
    if boundary.get("measurement_selected_formal_survivor") is not False or not all(boundary.get(key) is True for key in required_true):
        raise ValueError("methodological boundary changed")
    return record


def lifetime_value(row):
    return Fraction(row["partial_lifetime_lower_limit_mantissa"]) * (10 ** int(row["power_of_ten_years"]))


def exact_analysis(record):
    sources = record["sources"]
    nedm = sources[0]["rows"]["neutron_electric_dipole_moment"]
    denominator = int(nedm["scientific_power_denominator"])
    upper = Fraction(nedm["upper_limit_mantissa"]) / denominator
    statistical = Fraction(nedm["reported_statistical_uncertainty_mantissa"]) / denominator
    systematic = Fraction(nedm["reported_systematic_uncertainty_mantissa"]) / denominator
    proton_rows = (
        sources[1]["rows"]["p_to_e_plus_pi0"],
        sources[1]["rows"]["p_to_mu_plus_pi0"],
        sources[2]["rows"]["p_to_e_plus_eta"],
        sources[2]["rows"]["p_to_mu_plus_eta"],
        sources[3]["rows"]["p_to_e_plus_pi0_pi0"],
        sources[3]["rows"]["p_to_mu_plus_pi0_pi0"],
    )
    accepted_statuses = {
        "no-proton-decay-signal",
        "consistent-with-atmospheric-neutrino-background",
        "no-significant-excess-no-indication-of-proton-decay",
        "compatible-with-expected-atmospheric-neutrino-background",
    }
    limits = tuple(lifetime_value(row) for row in proton_rows)
    return {
        "nedm_reported_central_status": nedm["reported_central_status"],
        "nedm_upper_limit": upper,
        "nedm_statistical_uncertainty": statistical,
        "nedm_systematic_uncertainty": systematic,
        "nedm_direct_record_consistent": nedm["reported_central_status"] == "null-central-estimate" and upper > 0 and statistical > 0 and systematic > 0,
        "proton_lifetime_lower_limits_years": limits,
        "proton_mode_count": len(proton_rows),
        "all_proton_limits_positive": all(value > ONE for value in limits),
        "no_significant_decay_signal": all(row["interpretation"] in accepted_statuses for row in proton_rows),
        "background_candidates_retained": sum("candidate_count" in row for row in proton_rows) == 4,
        "all_confidence_rows_retained": all(Fraction(row["confidence_fraction"]) == Fraction(9, 10) for row in proton_rows) and Fraction(nedm["confidence_fraction"]) == Fraction(9, 10),
        "finite_limits_not_infinity": record["methodological_boundary"]["finite_limits_not_relabelled_as_completed_infinity"],
        "null_not_proof_zero": record["methodological_boundary"]["null_central_estimate_not_relabelled_as_numerical_proof_zero"],
        "all_sources_retained": len(sources) == 4,
    }


class StrongCpBaryonStabilityValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong strong-CP/baryon empirical seal")
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
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets={TARGET_IDS[0]: authoritative_record(self.root)},
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
            raise ValueError("prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("sealed formal prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = all((
            formal["alignment"]["strong_phase"] == ("aligned-One", ONE),
            formal["alignment"]["electric_dipole_carrier"] == EMPTY_ONE,
            formal["actions"]["generated_cross_fibre_actions"] == (),
            formal["baryon_One_invariant"],
        ))
        empirical = all((
            analysis["nedm_direct_record_consistent"],
            analysis["proton_mode_count"] == 6,
            analysis["all_proton_limits_positive"],
            analysis["no_significant_decay_signal"],
            analysis["background_candidates_retained"],
            analysis["all_confidence_rows_retained"],
            analysis["finite_limits_not_infinity"],
            analysis["null_not_proof_zero"],
            analysis["all_sources_retained"],
        ))
        tampered_edm = json.loads(json.dumps(record))
        tampered_edm["sources"][0]["rows"]["neutron_electric_dipole_moment"]["reported_central_status"] = "confirmed-nonempty-displacement"
        confirmed_edm_rejected = not exact_analysis(tampered_edm)["nedm_direct_record_consistent"]
        tampered_decay = json.loads(json.dumps(record))
        tampered_decay["sources"][1]["rows"]["p_to_e_plus_pi0"]["interpretation"] = "confirmed-proton-decay"
        confirmed_decay_rejected = not exact_analysis(tampered_decay)["no_significant_decay_signal"]
        passed = formal_pass and empirical and confirmed_edm_rejected and confirmed_decay_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-strong-cp-baryon-stability-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "sources": source_hashes(),
            "target": target_identity,
            "analysis": analysis,
            "formal": formal_pass,
            "confirmed_edm_rejected": confirmed_edm_rejected,
            "confirmed_decay_rejected": confirmed_decay_rejected,
        }
        measurements = (
            "PSI reports a null neutron-EDM central displacement with both positive uncertainty magnitudes and a finite 90-percent upper limit of 1.8e-26 e cm.",
            "The neutron-EDM row is consistent with the sealed empty-One strong-dipole prediction; it is not relabelled as numerical proof zero.",
            "All six registered Super-Kamiokande proton modes retain their finite 90-percent partial-lifetime lower limits.",
            "No registered mode reports a statistically significant proton-decay signal; every candidate interpretation, including background-compatible events, is retained.",
            "Finite lifetime limits are not called infinity and do not select the already sealed proton-stability law.",
            "Confirmed-EDM and confirmed-proton-decay hostile controls both reject.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            analysis["all_sources_retained"],
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION",
    "StrongCpBaryonStabilityValidator",
    "TARGET_IDS",
    "authoritative_record",
    "exact_analysis",
    "source_hashes",
)
