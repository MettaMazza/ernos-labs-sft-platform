"""Capability-closed validator for the complete post-seal waveform record."""

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
from sft.physics.gravitational_wave_chirp_ringdown_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.gravitational_wave_chirp_ringdown_terminal_law_v1 import theorem_certificate


TARGET_IDS = ("GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-WITHHELD-POSTSEAL-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"gravitational-wave source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-gravitational-wave-chirp-ringdown-postseal-source-record/1":
        raise ValueError("gravitational-wave source schema changed")
    if record.get("formal_receipt_hash") != "sha256:7add0b09e795aee79758286268637f442b40155f4af5c83a4a123f90e2150e19":
        raise ValueError("formal chirp/ringdown receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("withheld_postseal_sources", ())) != SOURCE_IDS:
        raise ValueError("complete ordered two-source post-seal vector required")
    boundary = record.get("methodological_boundary", {})
    required = (
        "formal_receipt_existed_before_withheld_source_binding",
        "gw150914_retained_as_preseal_development_context",
        "gw150914_not_counted_as_blind_validation",
        "all_postseal_source_rows_retained",
        "dimensional_frequency_not_imported_as_fold_proof_scalar",
        "model_assisted_mass_and_ringdown_roles_retained",
        "exact_half_One_damping_not_claimed_as_directly_measured",
        "cross_event_stage_support_explicit",
    )
    if boundary.get("measurement_selected_formal_survivor") is not False or not all(boundary.get(key) is True for key in required):
        raise ValueError("gravitational-wave methodological boundary changed")
    return record


def exact_analysis(record):
    development = record["development_context"][0]
    chirp = record["withheld_postseal_sources"][0]["rows"]
    ring = record["withheld_postseal_sources"][1]["rows"]
    chirp_signal = chirp["signal"]
    chirp_source = chirp["source_and_remnant"]
    ring_signal = ring["signal"]
    ring_source = ring["source_and_remnant"]
    ringdown = ring["ringdown"]
    return {
        "development_source_not_blind": development["blind_validation_role"] == "none",
        "chirp_frequency_interval_hz": (Fraction(chirp_signal["frequency_start_hz"]), Fraction(chirp_signal["frequency_end_hz"])),
        "chirp_frequency_rises": Fraction(chirp_signal["frequency_end_hz"]) > Fraction(chirp_signal["frequency_start_hz"]),
        "chirp_amplitude_rises": chirp_signal["amplitude_direction"] == "rising-to-peak",
        "chirp_cycle_count": Fraction(chirp_signal["cycle_count"]),
        "positive_radiated_energy": Fraction(chirp_source["radiated_energy_solar_c2"]) > 0,
        "chirp_two_to_one": Fraction(chirp_source["initial_component_count"]) == 2 and Fraction(chirp_source["final_remnant_count"]) == 1,
        "chirp_model_role_retained": "waveform models" in chirp["scope"]["waveform_role"],
        "ring_frequency_rises": Fraction(ring_signal["frequency_end_hz"]) > Fraction(ring_signal["frequency_start_hz"]),
        "ring_two_to_one": Fraction(ring_source["initial_component_count"]) == 2 and Fraction(ring_source["final_remnant_count"]) == 1,
        "ringdown_quadrupolar": "l-equals-m-equals-two" in ringdown["reported_mode"],
        "ringdown_decays": ringdown["damping_direction"] == "decaying-post-peak-support",
        "half_One_not_directly_measured": ringdown["exact_half_One_damping_directly_measured"] is False,
        "conditional_role_retained": ring["scope"]["interpretation_role"] == "quasicircular-binary interpretation is conditional",
        "alternative_interpretations_retained": ring["scope"]["alternative_interpretations_retained"] is True,
        "all_sources_retained": len(record["withheld_postseal_sources"]) == 2 and len(record["development_context"]) == 1,
    }


class GravitationalWaveChirpRingdownValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong gravitational-wave empirical seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
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
            raise ValueError("sealed gravitational-wave prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = formal["all_chirps_close"] and formal["merger_closes"] and formal["all_ringdowns_close"]
        empirical_pass = all((
            analysis["development_source_not_blind"],
            analysis["chirp_frequency_interval_hz"] == (Fraction(35), Fraction(450)),
            analysis["chirp_frequency_rises"], analysis["chirp_amplitude_rises"],
            analysis["chirp_cycle_count"] == 55, analysis["positive_radiated_energy"],
            analysis["chirp_two_to_one"], analysis["chirp_model_role_retained"],
            analysis["ring_frequency_rises"], analysis["ring_two_to_one"],
            analysis["ringdown_quadrupolar"], analysis["ringdown_decays"],
            analysis["half_One_not_directly_measured"], analysis["conditional_role_retained"],
            analysis["alternative_interpretations_retained"], analysis["all_sources_retained"],
        ))
        reversed_frequency = json.loads(json.dumps(record))
        reversed_frequency["withheld_postseal_sources"][0]["rows"]["signal"]["frequency_end_hz"] = "30/1"
        reversed_rejected = not exact_analysis(reversed_frequency)["chirp_frequency_rises"]
        erased_remnant = json.loads(json.dumps(record))
        erased_remnant["withheld_postseal_sources"][0]["rows"]["source_and_remnant"]["final_remnant_count"] = "2/1"
        remnant_rejected = not exact_analysis(erased_remnant)["chirp_two_to_one"]
        relabelled_development = json.loads(json.dumps(record))
        relabelled_development["development_context"][0]["blind_validation_role"] = "blind"
        relabelling_rejected = not exact_analysis(relabelled_development)["development_source_not_blind"]
        erased_scope = json.loads(json.dumps(record))
        erased_scope["withheld_postseal_sources"][1]["rows"]["scope"]["interpretation_role"] = "unconditional"
        scope_rejected = not exact_analysis(erased_scope)["conditional_role_retained"]
        passed = all((formal_pass, empirical_pass, reversed_rejected, remnant_rejected, relabelling_rejected, scope_rejected))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-gravitational-wave-chirp-ringdown-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "analysis": analysis, "formal": formal_pass, "controls": (reversed_rejected, remnant_rejected, relabelling_rejected, scope_rejected)}
        measurements = (
            "GW150914 is retained as pre-seal observational context and is not counted as blind validation.",
            "GW151226 rises in frequency from 35 to 450 Hz and in amplitude over 55 cycles.",
            "GW151226 retains positive radiated energy and the two-component-to-one-remnant transition with full uncertainties and model role.",
            "GW190521 retains one remnant, a decaying least-damped quadrupolar mode and compatibility with the full waveform analysis.",
            "GW190521's conditional quasicircular interpretation, short-signal limit and alternative interpretations remain explicit.",
            "No dimensional frequency or exact half-One damping value is relabelled as a Fold proof scalar or direct universal measurement.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_sources_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("FALSIFICATION_CONDITION", "GravitationalWaveChirpRingdownValidator", "TARGET_IDS", "authoritative_record", "exact_analysis", "source_hashes")
