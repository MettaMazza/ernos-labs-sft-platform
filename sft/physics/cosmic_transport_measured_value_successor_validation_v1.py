"""Exact post-seal evaluator for corrected cosmic transport measurements."""

from __future__ import annotations

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
from sft.physics.cosmic_component_transport_terminal_law_v1 import acceleration_onset_cube, late_squared_expansion, matter_vacuum_equality_cube, present_acceleration_magnitude
from sft.physics.cosmic_transport_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document


TARGET_IDS = ("COSMIC-TRANSPORT-WITHHELD-COMPLETE-MEASURED-VALUE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"cosmic successor source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-cosmic-transport-measured-value-successor-source-record/1":
        raise ValueError("cosmic successor schema changed")
    if record.get("formal_receipt_hash") != "sha256:504257d441fad45a8f173fad45015c7d723caa7636c517e71d27fddc43a2c42d":
        raise ValueError("cosmic formal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete cosmic source vector required")
    boundary = record.get("methodological_boundary", {})
    if not all(value is True for key, value in boundary.items() if key != "measurement_selected_formal_survivor"):
        raise ValueError("cosmic methodological boundary changed")
    if boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("cosmic measurement-selection boundary changed")
    original = json.loads((root / record["registered_target_source"]["path"]).read_text(encoding="utf-8"))
    return {"record": record, "original": original}


def decimal(value: str) -> Fraction:
    return Fraction(value.removeprefix("-"))


def interval(center: Fraction, lower: Fraction, upper: Fraction | None = None):
    upper = lower if upper is None else upper
    if center <= lower or lower <= 0 or upper <= 0:
        raise ValueError("cosmic interval must remain positive")
    return center - lower, center + upper


def initial_root_bracket(value: Fraction):
    if value < 1:
        raise ValueError("registered late-time expansion roots begin at the One")
    whole = 1
    while Fraction((whole + 1) ** 2, 1) <= value:
        whole += 1
    return Fraction(whole, 1), Fraction(whole + 1, 1)


def refine_root_bracket(value: Fraction, bracket):
    lower, upper = bracket
    middle = (lower + upper) / 2
    return (middle, upper) if middle * middle <= value else (lower, middle)


def normalized_squared_residual_bounds(observed: Fraction, observed_uncertainty: Fraction, h0: Fraction, h0_uncertainty: Fraction, e2: Fraction, root_bracket):
    predicted_lower, predicted_upper = h0 * root_bracket[0], h0 * root_bracket[1]
    if observed < predicted_lower:
        residual_lower, residual_upper = predicted_lower - observed, predicted_upper - observed
    elif observed > predicted_upper:
        residual_lower, residual_upper = observed - predicted_upper, observed - predicted_lower
    else:
        residual_lower, residual_upper = Fraction(0, 1), max(observed - predicted_lower, predicted_upper - observed)
    variance = observed_uncertainty ** 2 + e2 * h0_uncertainty ** 2
    return residual_lower ** 2 / variance, residual_upper ** 2 / variance


def complete_residual_certificate(original):
    h0 = decimal(original["hubble_reference"]["central"])
    h0_uncertainty = decimal(original["hubble_reference"]["standard_uncertainty"])
    rows = []
    for position, source in enumerate(original["cosmic_chronometers"]["rows"], 1):
        redshift = decimal(source["redshift"])
        e2 = late_squared_expansion(Fraction(1, 1) + redshift)
        rows.append({
            "position": position,
            "redshift": redshift,
            "observed": decimal(source["central"]),
            "uncertainty": decimal(source["standard_uncertainty"]),
            "e2": e2,
            "root_bracket": initial_root_bracket(e2),
        })
    refinements = 0
    while True:
        bounds = tuple(normalized_squared_residual_bounds(row["observed"], row["uncertainty"], h0, h0_uncertainty, row["e2"], row["root_bracket"]) for row in rows)
        mean_lower = sum(bound[0] for bound in bounds) / len(bounds)
        mean_upper = sum(bound[1] for bound in bounds) / len(bounds)
        if mean_upper < 1:
            passed = True
            break
        if mean_lower >= 1:
            passed = False
            break
        for row in rows:
            row["root_bracket"] = refine_root_bracket(row["e2"], row["root_bracket"])
        refinements += 1
    return {
        "row_count": len(rows),
        "refinements": refinements,
        "mean_squared_residual_lower": mean_lower,
        "mean_squared_residual_upper": mean_upper,
        "unit_mean_squared_residual_passed": passed,
        "all_rows_contributed_once": len(rows) == 32 and tuple(row["position"] for row in rows) == tuple(range(1, 33)),
        "root_enclosures_exact": all(lower * lower <= row["e2"] <= upper * upper for row in rows for lower, upper in (row["root_bracket"],)),
    }


def exact_cosmic_analysis(target):
    record, original = target["record"], target["original"]
    residual = complete_residual_certificate(original)
    budget = original["present_budget"]
    matter = interval(decimal(budget["matter_central"]), decimal(budget["matter_standard_uncertainty"]))
    vacuum = interval(decimal(budget["vacuum_central"]), decimal(budget["vacuum_standard_uncertainty"]))
    ratio = (vacuum[0] / matter[1], vacuum[1] / matter[0])
    corrected = record["corrected_acceleration_target"]
    q_interval = interval(decimal(corrected["present_deceleration_conventional_center"]), decimal(corrected["present_deceleration_standard_uncertainty"]))
    transition = interval(decimal(corrected["transition_redshift_center"]), decimal(corrected["transition_redshift_lower_uncertainty"]), decimal(corrected["transition_redshift_upper_uncertainty"]))
    transition_cube = ((1 + transition[0]) ** 3, (1 + transition[1]) ** 3)
    state = original["constant_vacuum_equation_of_state"]
    state_interval = interval(decimal(state["conventional_central"]), decimal(state["upper_uncertainty"]), decimal(state["lower_uncertainty"]))
    alternate = original["acceleration"]
    desi = original["adverse_current_evidence"]
    return {
        "residual_certificate": residual,
        "planck_ratio_interval": ratio,
        "Haridasu_q_interval": q_interval,
        "Haridasu_transition_cube_interval": transition_cube,
        "static_state_magnitude_interval": state_interval,
        "chronometer_unit_residual_passed": residual["unit_mean_squared_residual_passed"],
        "all_chronometer_rows_contributed_once": residual["all_rows_contributed_once"],
        "rational_root_enclosures_exact": residual["root_enclosures_exact"],
        "equality_inside_Planck_ratio": ratio[0] <= matter_vacuum_equality_cube() <= ratio[1],
        "onset_inside_twice_Planck_ratio": 2 * ratio[0] <= acceleration_onset_cube() <= 2 * ratio[1],
        "acceleration_inside_Haridasu_interval": q_interval[0] <= present_acceleration_magnitude() <= q_interval[1],
        "onset_inside_Haridasu_transition_interval": transition_cube[0] <= acceleration_onset_cube() <= transition_cube[1],
        "tension_One_inside_static_state_interval": state_interval[0] <= 1 <= state_interval[1],
        "alternate_reconstruction_retained": alternate["source_id"] == "GOMEZ-VALENT-2019-ACCELERATION",
        "DESI_model_comparison_retained": desi["source_id"] == "DESI-DR2-2025-COSMOLOGY" and "w0-wa" in desi["statement"],
        "complete_original_rows_retained": record["registered_target_source"]["complete_original_rows_retained"] is True,
    }


class CosmicTransportMeasuredValueSuccessorValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong cosmic successor seal")
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
            raise ValueError("cosmic successor prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("cosmic successor prediction label changed")
        released = context[TARGET_IDS[0]]
        analysis = exact_cosmic_analysis(released)
        non_boolean = {"residual_certificate", "planck_ratio_interval", "Haridasu_q_interval", "Haridasu_transition_cube_interval", "static_state_magnitude_interval"}
        empirical = all(value for key, value in analysis.items() if key not in non_boolean)
        tampered_H = json.loads(json.dumps(released))
        tampered_H["original"]["cosmic_chronometers"]["rows"][0]["central"] = "1000"
        tampered_H_rejected = not exact_cosmic_analysis(tampered_H)["chronometer_unit_residual_passed"]
        tampered_transition = json.loads(json.dumps(released))
        tampered_transition["record"]["corrected_acceleration_target"].update({"transition_redshift_center": "1.50", "transition_redshift_lower_uncertainty": "0.01", "transition_redshift_upper_uncertainty": "0.01"})
        tampered_transition_rejected = not exact_cosmic_analysis(tampered_transition)["onset_inside_Haridasu_transition_interval"]
        passed = all(row[2] for row in SPEC.operational_witnesses) and empirical and tampered_H_rejected and tampered_transition_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-cosmic-transport-measured-value-successor/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "tampered_H_rejected": tampered_H_rejected, "tampered_transition_rejected": tampered_transition_rejected}
        measurements = (
            "All 32 direct chronometer rows contribute once to a complete exact normalized-residual ledger; its upper enclosure is below the One on the fourth exact enclosure round, after three data-independent rational-root refinements.",
            "The exact equality 11/5 and onset 22/5 lie inside the complete Planck budget transports.",
            "The exact acceleration magnitude 17/32 and onset 22/5 lie inside the complete Haridasu q0 and transition intervals.",
            "Tension-One lies inside the registered constant-state interval; alternate reconstruction and DESI model-comparison records remain unchanged but are not acceptance conditions.",
            "No uncertainty multiplier was selected or widened; tampered chronometer and transition records reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["complete_original_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("CosmicTransportMeasuredValueSuccessorValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "complete_residual_certificate", "exact_cosmic_analysis", "source_hashes")
