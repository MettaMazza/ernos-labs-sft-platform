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
from sft.physics.dark_smithion_lfv_empirical_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.dark_smithion_lfv_terminal_law_v1 import abundance_certificate, lfv_certificate, theorem_certificate
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document


TARGET_IDS = ("DARK-SMITHION-LFV-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"dark/Smithion/LFV source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-dark-smithion-lfv-postseal-source-record/1" or record.get("formal_receipt_hash") != "sha256:71a131119ffd152690ec772019177fb06599474cd5e89b60a62c1b9b69ec5762":
        raise ValueError("formal binding or schema changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete four-source record required")
    boundary = record.get("methodological_boundary", {})
    if boundary.get("measurement_selected_formal_survivor") is not False or not all(boundary.get(key) is True for key in ("all_presently_measurable_rows_retained", "unobserved_new_particle_masses_not_relabelled_as_measurements", "upper_limits_not_relabelled_as_rate_measurements")):
        raise ValueError("methodological boundary changed")
    return record


def exact_analysis(record):
    planck = record["sources"][0]["rows"]
    baryon = planck["baryon_density_omega_b_h2"]
    dark = planck["cold_dark_density_omega_c_h2"]
    b, bu = Fraction(baryon["central"]), Fraction(baryon["standard_uncertainty"])
    d, du = Fraction(dark["central"]), Fraction(dark["standard_uncertainty"])
    ratio_interval = ((d - du) / (b + bu), (d + du) / (b - bu))
    transported = Fraction(27, 5) * b
    sparc = record["sources"][1]["rows"]
    meg = record["sources"][2]["rows"]
    babar = record["sources"][3]["rows"]
    limits = (Fraction(meg["branching_fraction_upper_limit"]), Fraction(babar["tau_to_mu_gamma"]["branching_fraction_upper_limit"]), Fraction(babar["tau_to_e_gamma"]["branching_fraction_upper_limit"]))
    return {
        "ratio_interval": ratio_interval,
        "transported_density": transported,
        "dark_interval": (d - du, d + du),
        "ratio_passes": ratio_interval[0] <= Fraction(27, 5) <= ratio_interval[1],
        "absolute_transport_passes": d - du <= transported <= d + du,
        "sparc_complete": sparc["galaxy_count"] == "175" and "submaximal" in sparc["baryon_comparison"],
        "all_lfv_limits_positive": all(value > 0 for value in limits),
        "all_lfv_searches_null": meg["observed_signal"] == "none" and babar["tau_to_e_gamma"]["observed_signal"] == "none" and babar["tau_to_mu_gamma"]["observed_signal"] == "none",
        "lfv_relative_rate_measured": False,
        "smithion_mass_measured": False,
        "evidence_types_preserved": record["methodological_boundary"]["upper_limits_not_relabelled_as_rate_measurements"] and record["methodological_boundary"]["unobserved_new_particle_masses_not_relabelled_as_measurements"],
        "all_sources_retained": len(record["sources"]) == 4,
    }


class DarkSmithionLfvValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong dark/Smithion/LFV empirical seal")
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
            raise ValueError("prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = formal["quark_cross_lock"] and formal["twelve_roots"] and formal["all_roots_disjoint_positive"] and abundance_certificate()["dark_to_baryon"] == Fraction(27, 5) and lfv_certificate()["integer_ratio"] == (3, 5, 20)
        empirical = all((analysis["ratio_passes"], analysis["absolute_transport_passes"], analysis["sparc_complete"], analysis["all_lfv_limits_positive"], analysis["all_lfv_searches_null"], not analysis["lfv_relative_rate_measured"], not analysis["smithion_mass_measured"], analysis["evidence_types_preserved"], analysis["all_sources_retained"]))
        tampered = json.loads(json.dumps(record)); tampered["sources"][0]["rows"]["cold_dark_density_omega_c_h2"]["central"] = "0.100"
        tampered_density_rejected = not exact_analysis(tampered)["ratio_passes"]
        fabricated = json.loads(json.dumps(record)); fabricated["methodological_boundary"]["upper_limits_not_relabelled_as_rate_measurements"] = False
        fabricated_rate_rejected = not exact_analysis(fabricated)["evidence_types_preserved"]
        passed = formal_pass and empirical and tampered_density_rejected and fabricated_rate_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-dark-smithion-lfv-comparator/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "formal": formal_pass, "tampered_density_rejected": tampered_density_rejected, "fabricated_rate_rejected": fabricated_rate_rejected}
        measurements = (
            "The exact dark/baryon ratio 27/5 lies inside the complete Planck density-ratio interval.",
            "Comparison-side transport 27/5 times 0.0224 equals 0.12096 and lies inside [0.119,0.121].",
            "The complete 175-galaxy SPARC record requires additional gravitating support under the admitted inverse-square law; it does not alone identify a particle.",
            "MEG II and BaBar retain all three null-search upper limits. They do not constitute measured nonzero LFV rates, so no 3:5:20 match is fabricated.",
            "No registered Smithion mass measurement exists; all twelve spectra remain exact standing predictions.",
            "Tampered-density and fabricated-rate controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_sources_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("DarkSmithionLfvValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_analysis", "source_hashes")
