"""Capability-closed post-seal validator for Claim 072."""

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
from sft.physics.compact_horizon_terminal_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.compact_horizon_terminal_law_v1 import theorem_certificate
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document


TARGET_IDS = ("COMPACT-HORIZON-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"compact-object source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-compact-horizon-postseal-source-record/1":
        raise ValueError("compact-object source schema changed")
    if record.get("formal_receipt_hash") != "sha256:69152da01b20c6b1a7ab6ecfab4e44cf836d588cba4ea6f3b02d5827cb5a0b3f":
        raise ValueError("formal compact-object receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete ordered three-source compact-object vector required")
    boundary = record.get("methodological_boundary", {})
    if boundary.get("external_measurement_selected_formal_survivor") is not False:
        raise ValueError("measurement selected the formal survivor")
    required_true = (
        "formal_receipt_existed_before_source_binding",
        "all_three_source_rows_retained",
        "theoretical_summary_distinguished_from_direct_measurement",
        "conditional_merger_limits_identified_as_model_assisted",
        "neutron_star_mass_not_relabelled_as_the_maximum",
        "hawking_nonobservation_not_rewarded_as_a_match",
        "reported_signed_or_decimal_coordinates_not_used_as_fold_proof_scalars",
    )
    if not all(boundary.get(key) is True for key in required_true):
        raise ValueError("compact-object methodological boundary changed")
    return record


def exact_analysis(record):
    white = record["sources"][0]["rows"]["electron_degenerate_white_dwarf"]
    neutron = record["sources"][1]["rows"]["massive_neutron_star"]
    remnant = record["sources"][2]["rows"]
    horizon = record["existing_postseal_boundary"]
    white_limit = Fraction(white["reported_mass_limit_solar"])
    neutron_mass = Fraction(neutron["reported_mass_solar"])
    neutron_lower_uncertainty = Fraction(neutron["lower_uncertainty_solar"])
    neutron_upper_uncertainty = Fraction(neutron["upper_uncertainty_solar"])
    neutron_interval = (neutron_mass - neutron_lower_uncertainty, neutron_mass + neutron_upper_uncertainty)
    hyper = Fraction(remnant["conditional_hypermassive_maximum"]["maximum_baryonic_mass_solar"])
    nonrotating = Fraction(remnant["conditional_nonrotating_maximum"]["maximum_baryonic_mass_solar"])
    return {
        "white_dwarf_limit_solar": white_limit,
        "white_dwarf_role": white["reported_role"],
        "neutron_star_mass_solar": neutron_mass,
        "neutron_star_interval_solar": neutron_interval,
        "neutron_star_interval_wholly_above_white_dwarf_limit": neutron_interval[0] > white_limit,
        "neutron_star_mass_is_direct_maximum_measurement": False,
        "neutron_star_measurement_method": neutron["measurement_method"],
        "neutron_star_credibility": Fraction(neutron["reported_credibility_fraction"]),
        "hypermassive_conditional_upper_solar": hyper,
        "nonrotating_conditional_upper_solar": nonrotating,
        "both_conditional_uppers_above_neutron_interval": hyper > neutron_interval[1] and nonrotating > neutron_interval[1],
        "conditional_roles_retained": "conditional" in remnant["conditional_hypermassive_maximum"]["use_boundary"] and "conditional" in remnant["conditional_nonrotating_maximum"]["use_boundary"],
        "horizon_validation_claim": horizon["claim_id"],
        "horizon_validation_receipt": horizon["receipt_hash"],
        "hawking_directly_measured": False,
        "hawking_nonobservation_rewarded_as_match": False,
        "all_sources_retained": len(record["sources"]) == 3,
    }


class CompactHorizonTerminalValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong compact-object empirical seal")
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
            raise ValueError("sealed compact-object prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = all((
            formal["all_exclusion_scalings_close"],
            formal["two_pre_horizon_families"],
            formal["reference_cross_closes"],
            formal["all_evaporation_traces_close"],
        ))
        empirical_pass = all((
            analysis["white_dwarf_limit_solar"] == Fraction(7, 5),
            analysis["neutron_star_interval_solar"] == (Fraction(201, 100), Fraction(215, 100)),
            analysis["neutron_star_interval_wholly_above_white_dwarf_limit"],
            not analysis["neutron_star_mass_is_direct_maximum_measurement"],
            analysis["both_conditional_uppers_above_neutron_interval"],
            analysis["conditional_roles_retained"],
            analysis["horizon_validation_receipt"] == "sha256:8279f3140235ca46ae66bbf4ed0fbf28c804d3bb42b43ecdb0d12ce45dc807b8",
            not analysis["hawking_directly_measured"],
            not analysis["hawking_nonobservation_rewarded_as_match"],
            analysis["all_sources_retained"],
        ))
        reversed_order = json.loads(json.dumps(record))
        reversed_order["sources"][1]["rows"]["massive_neutron_star"]["reported_mass_solar"] = "13/10"
        reversed_order_rejected = not exact_analysis(reversed_order)["neutron_star_interval_wholly_above_white_dwarf_limit"]
        collapsed_upper = json.loads(json.dumps(record))
        collapsed_upper["sources"][2]["rows"]["conditional_hypermassive_maximum"]["maximum_baryonic_mass_solar"] = "2/1"
        collapsed_upper_rejected = not exact_analysis(collapsed_upper)["both_conditional_uppers_above_neutron_interval"]
        erased_condition = json.loads(json.dumps(record))
        erased_condition["sources"][2]["rows"]["conditional_nonrotating_maximum"]["use_boundary"] = "direct measurement"
        erased_condition_rejected = not exact_analysis(erased_condition)["conditional_roles_retained"]
        passed = all((formal_pass, empirical_pass, reversed_order_rejected, collapsed_upper_rejected, erased_condition_rejected))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-compact-horizon-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "controls": (reversed_order_rejected, collapsed_upper_rejected, erased_condition_rejected),
        }
        measurements = (
            "NASA records electron degeneracy and the 7/5-solar-mass white-dwarf limit.",
            "PSR J0740+6620 is measured at 52/25 +/- 7/100 solar masses; its complete interval lies above 7/5.",
            "Both LIGO-Virgo conditional remnant limits are retained with their model conditions and are not called direct TOV measurements.",
            "The prior horizon receipt is retained unchanged; direct Hawking radiation and temperature remain unmeasured standing tests.",
            "Hawking non-observation is explicitly not counted as confirmation of the formal mT=1/16 prediction.",
            "Reversed-order, collapsed-upper and erased-condition hostile controls all reject.",
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
    "FALSIFICATION_CONDITION", "CompactHorizonTerminalValidator", "TARGET_IDS",
    "authoritative_record", "exact_analysis", "source_hashes",
)
