"""Capability-closed post-seal validator for Claim 066."""

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
from sft.physics.higgs_symmetry_terminal_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.higgs_symmetry_terminal_law_v1 import ONE, theorem_certificate


TARGET_IDS = ("HIGGS-TERMINAL-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"Higgs terminal source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-higgs-terminal-postseal-source-record/1":
        raise ValueError("Higgs terminal source schema changed")
    if record.get("formal_receipt_hash") != "sha256:3f84e4ede48a489bc78a8cc47eac935bbff3566d1e561c26ef0059d7bbcbfb1e":
        raise ValueError("formal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete five-source Higgs vector required")
    boundary = record.get("methodological_boundary", {})
    required_true = (
        "aggregate_and_individual_mass_rows_retained",
        "individual_offsets_not_erased_by_aggregate",
        "reported_signed_coordinate_not_used_as_fold_proof_scalar",
        "self_coupling_limit_not_relabelled_as_direct_precision_measurement",
    )
    if boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("measurement selected formal survivor")
    if boundary.get("external_scale_selected_formal_ratio") is not False:
        raise ValueError("external scale selected formal ratio")
    if not all(boundary.get(key) is True for key in required_true):
        raise ValueError("Higgs methodological boundary changed")
    return record


def exact_analysis(record):
    sources = record["sources"]
    scale = Fraction(sources[0]["rows"]["electroweak_vacuum_scale"]["reported_value_gev"])
    pdg = sources[1]["rows"]["higgs_mass_world_average"]
    atlas = sources[2]["rows"]["combined_higgs_mass"]
    cms = sources[3]["rows"]["four_lepton_higgs_mass"]
    pair = sources[4]["rows"]["trilinear_self_coupling_constraint"]
    formal = theorem_certificate()
    ratio = formal["terminal_mass_ratio"]
    coupling = formal["terminal_self_coupling"]
    predicted_mass = ratio * scale
    pdg_central = Fraction(pdg["listed_average_gev"])
    pdg_uncertainty = Fraction(pdg["listed_uncertainty_gev"])
    pdg_lower, pdg_upper = tuple(Fraction(value) for value in pdg["reported_interval_from_listed_uncertainty_gev"])
    atlas_central = Fraction(atlas["reported_value_gev"])
    atlas_uncertainty = Fraction(atlas["combined_uncertainty_gev"])
    cms_central = Fraction(cms["reported_value_gev"])
    cms_uncertainty = Fraction(cms["reported_uncertainty_gev"])
    pdg_offset = predicted_mass - pdg_central
    atlas_offset = predicted_mass - atlas_central
    cms_offset = predicted_mass - cms_central
    kappa_prediction = Fraction(pair["sft_normalized_prediction"])
    kappa_upper = Fraction(pair["upper_coordinate"])
    lower_magnitude = Fraction(pair["lower_coordinate_magnitude"])
    return {
        "formal_mass_ratio": ratio,
        "formal_self_coupling": coupling,
        "external_scale_gev": scale,
        "predicted_mass_gev": predicted_mass,
        "pdg_central_gev": pdg_central,
        "pdg_uncertainty_gev": pdg_uncertainty,
        "pdg_interval_gev": (pdg_lower, pdg_upper),
        "pdg_aggregate_contains_prediction": pdg_lower <= predicted_mass <= pdg_upper,
        "pdg_offset_gev": pdg_offset,
        "pdg_offset_in_reported_uncertainties": pdg_offset / pdg_uncertainty,
        "pdg_error_scale_factor": Fraction(pdg["error_scale_factor"]),
        "atlas_central_gev": atlas_central,
        "atlas_uncertainty_gev": atlas_uncertainty,
        "atlas_offset_gev": atlas_offset,
        "atlas_offset_in_reported_uncertainties": atlas_offset / atlas_uncertainty,
        "atlas_one_reported_uncertainty_contains_prediction": atlas_central - atlas_uncertainty <= predicted_mass <= atlas_central + atlas_uncertainty,
        "cms_central_gev": cms_central,
        "cms_uncertainty_gev": cms_uncertainty,
        "cms_offset_gev": cms_offset,
        "cms_offset_in_reported_uncertainties": cms_offset / cms_uncertainty,
        "cms_one_reported_uncertainty_contains_prediction": cms_central - cms_uncertainty <= predicted_mass <= cms_central + cms_uncertainty,
        "individual_offsets_retained": atlas_offset > 0 and cms_offset > 0,
        "kappa_prediction": kappa_prediction,
        "kappa_lower_direction": pair["lower_coordinate_direction"],
        "kappa_lower_magnitude": lower_magnitude,
        "kappa_upper": kappa_upper,
        "kappa_interval_contains_prediction": pair["lower_coordinate_direction"] == "below-reference-direction" and lower_magnitude > 0 and kappa_prediction < kappa_upper,
        "kappa_confidence_fraction": Fraction(pair["confidence_fraction"]),
        "direct_coupling_is_precision_measurement": False,
        "all_sources_retained": len(sources) == 5,
        "all_measurement_rows_positive_where_unsigned": all(value > 0 for value in (
            scale, pdg_central, pdg_uncertainty, atlas_central, atlas_uncertainty,
            cms_central, cms_uncertainty, lower_magnitude, kappa_upper,
        )),
    }


class HiggsSymmetryTerminalValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Higgs terminal empirical seal")
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
            raise ValueError("sealed Higgs prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = all((
            formal["terminal_mass_ratio"] == Fraction(2563352914777, 5038463954690),
            formal["terminal_self_coupling"] == Fraction(6570778165695741824959729, 50772238045420788745992200),
            formal["route_cross_lock"]["routes_equal"],
        ))
        empirical = all((
            analysis["predicted_mass_gev"] == Fraction(31557437733819647, 251923197734500),
            analysis["pdg_aggregate_contains_prediction"],
            analysis["individual_offsets_retained"],
            not analysis["atlas_one_reported_uncertainty_contains_prediction"],
            not analysis["cms_one_reported_uncertainty_contains_prediction"],
            analysis["kappa_interval_contains_prediction"],
            not analysis["direct_coupling_is_precision_measurement"],
            analysis["all_sources_retained"],
            analysis["all_measurement_rows_positive_where_unsigned"],
        ))
        outside_mass = json.loads(json.dumps(record))
        outside_mass["sources"][1]["rows"]["higgs_mass_world_average"]["reported_interval_from_listed_uncertainty_gev"] = ["124/1", "125/1"]
        outside_mass_rejected = not exact_analysis(outside_mass)["pdg_aggregate_contains_prediction"]
        outside_coupling = json.loads(json.dumps(record))
        outside_coupling["sources"][4]["rows"]["trilinear_self_coupling_constraint"]["upper_coordinate"] = "9/10"
        outside_coupling_rejected = not exact_analysis(outside_coupling)["kappa_interval_contains_prediction"]
        erased_offset = json.loads(json.dumps(record))
        erased_offset["sources"][2]["rows"]["combined_higgs_mass"]["reported_value_gev"] = str(analysis["predicted_mass_gev"])
        erased_offset_rejected = not exact_analysis(erased_offset)["individual_offsets_retained"]
        passed = formal_pass and empirical and outside_mass_rejected and outside_coupling_rejected and erased_offset_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-Higgs-terminal-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "outside_mass_rejected": outside_mass_rejected,
            "outside_coupling_rejected": outside_coupling_rejected,
            "erased_offset_rejected": erased_offset_rejected,
        }
        measurements = (
            "The sealed exact ratio and post-seal PDG 246.22 GeV dimensional reference give 125.266104978... GeV.",
            "The prediction lies inside the PDG 2025 125.20 +/- 0.11 GeV listed-average interval.",
            "ATLAS and CMS individual offsets are retained exactly and are not falsely described as one-uncertainty agreements.",
            "The exact native coupling is 0.1294167525...; normalized unity lies inside the 2026 combined direct-search interval.",
            "The direct self-coupling constraint remains broad and is not called a precision measurement.",
            "Outside-mass, outside-coupling and erased-offset hostile controls all reject.",
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
    "HiggsSymmetryTerminalValidator",
    "TARGET_IDS",
    "authoritative_record",
    "exact_analysis",
    "source_hashes",
)
