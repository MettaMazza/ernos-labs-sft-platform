"""Exact post-seal evaluator for corrected criticality measurements."""

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
from sft.physics.criticality_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document


TARGET_IDS = ("CRITICALITY-WITHHELD-COMPLETE-MEASURED-VALUE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"criticality successor source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-criticality-measured-value-successor-source-record/1":
        raise ValueError("criticality successor schema changed")
    if record.get("formal_receipt_hash") != "sha256:0601d19640943c4b99eb8cccf061e3115c520773eac5e762bf7c5b7440339b25":
        raise ValueError("criticality formal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete criticality source vector required")
    boundary = record.get("methodological_boundary", {})
    if not all(value is True for key, value in boundary.items() if key != "measurement_selected_formal_survivor"):
        raise ValueError("criticality methodological boundary changed")
    if boundary.get("measurement_selected_formal_survivor") is not False:
        raise ValueError("criticality measurement-selection boundary changed")
    original = json.loads((root / record["registered_target_source"]["path"]).read_text(encoding="utf-8"))
    return {"record": record, "original": original}


def exact_interval(center, uncertainty, denominator):
    centre, width = Fraction(center, denominator), Fraction(uncertainty, denominator)
    if centre <= width or width <= 0:
        raise ValueError("criticality interval must remain positive")
    return centre - width, centre + width


def exact_criticality_analysis(target):
    record, original = target["record"], target["original"]
    measured = original["registered_target"]
    denominator = measured["manganite_measurement_denominator"]
    class_key = record["manganite_complete_structural_key"]
    target_values = {"beta": Fraction(1, 2), "gamma": Fraction(1, 1), "delta": Fraction(3, 1)}
    material_rows = []
    residual_sum = Fraction(0, 1)
    for row in measured["manganite_rows"]:
        residuals = {}
        intervals = {}
        for key, target_value in target_values.items():
            center = Fraction(row[f"{key}_center"], denominator)
            uncertainty = Fraction(row[f"{key}_uncertainty"], denominator)
            residuals[key] = (center - target_value) ** 2 / uncertainty ** 2
            intervals[key] = (center - uncertainty, center + uncertainty)
            residual_sum += residuals[key]
        material_rows.append({"sample": row["sample"], "residuals": residuals, "intervals": intervals, "complete_key": True})
    complete_mean = residual_sum / (len(material_rows) * len(target_values))
    erbium_denominator = measured["erbium_measurement_denominator"]
    erbium = {
        "beta": exact_interval(measured["erbium_beta_center"], measured["erbium_beta_uncertainty"], erbium_denominator),
        "gamma": exact_interval(measured["erbium_gamma_center"], measured["erbium_gamma_uncertainty"], erbium_denominator),
        "nu": exact_interval(measured["erbium_nu_center"], measured["erbium_nu_uncertainty"], erbium_denominator),
    }
    turbulence = exact_interval(measured["turbulence_measured_structure_center"], measured["turbulence_measured_structure_uncertainty"], measured["turbulence_measured_structure_denominator"])
    structural_true = tuple(key for key, value in class_key.items() if key != "sample_ids" and value is True)
    return {
        "material_rows": tuple(material_rows),
        "complete_fifteen_value_mean_squared_residual": complete_mean,
        "erbium_intervals": erbium,
        "turbulence_interval": turbulence,
        "all_five_material_keys_complete": tuple(row["sample"] for row in material_rows) == tuple(class_key["sample_ids"]) and len(structural_true) == 5,
        "complete_manganite_residual_below_One": complete_mean < 1,
        "complete_residual_exact_value": complete_mean == Fraction(5286961, 10584000),
        "La02_retained_without_mismatch_reward": any(row["sample"] == "La02" for row in material_rows) and record["methodological_boundary"]["La02_individual_displacements_are_retained_but_not_rewarded_as_a_result"] is True,
        "erbium_vector_passed": erbium["beta"][0] <= Fraction(1, 2) <= erbium["beta"][1] and erbium["gamma"][0] <= 1 <= erbium["gamma"][1] and erbium["nu"][0] <= Fraction(1, 2) <= erbium["nu"][1],
        "turbulence_structure_passed": turbulence[0] <= Fraction(2, 3) <= turbulence[1],
        "both_spectrum_routes_passed": measured["spectrum_five_thirds_compensation_used"] is True and measured["spectrum_fourier_plateau_observed"] is True and measured["spectrum_hilbert_plateau_observed"] is True,
        "limitations_retained": measured["turbulence_finite_reynolds_limit_retained"] is True and measured["spectrum_structure_function_range_limitation_retained"] is True and measured["normalized_half_one_threshold_not_universal_lab_temperature"] is True,
        "all_source_rows_retained": record["registered_target_source"]["all_original_rows_retained"] is True and measured["all_manganite_rows_retained"] is True and measured["all_registered_rows_retained"] is True,
    }


class CriticalityMeasuredValueSuccessorValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong criticality successor seal")
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
            raise ValueError("criticality successor prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("criticality successor prediction label changed")
        released = context[TARGET_IDS[0]]
        analysis = exact_criticality_analysis(released)
        non_boolean = {"material_rows", "complete_fifteen_value_mean_squared_residual", "erbium_intervals", "turbulence_interval"}
        empirical = all(value for key, value in analysis.items() if key not in non_boolean)
        tampered_vector = json.loads(json.dumps(released))
        tampered_vector["original"]["registered_target"]["manganite_rows"][1]["gamma_center"] = 200
        tampered_vector_rejected = not exact_criticality_analysis(tampered_vector)["complete_manganite_residual_below_One"]
        tampered_key = json.loads(json.dumps(released))
        tampered_key["record"]["manganite_complete_structural_key"]["Widom_relation_verified_for_reported_exponents"] = False
        tampered_key_rejected = not exact_criticality_analysis(tampered_key)["all_five_material_keys_complete"]
        passed = all(row[2] for row in SPEC.operational_witnesses) and empirical and tampered_vector_rejected and tampered_key_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-criticality-measured-value-successor/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "tampered_vector_rejected": tampered_vector_rejected, "tampered_key_rejected": tampered_key_rejected}
        measurements = (
            "All five complete manganite structural class keys identify the registered mean-field class.",
            "All fifteen beta/gamma/delta measurements enter once; their exact mean squared normalized residual is 5286961/10584000, below the One.",
            "The complete erbium vector contains one-half, One and one-half; the independent turbulence interval contains two-thirds.",
            "Both physical spectral routes exhibit the falling five-thirds compensated plateau with all limitations retained.",
            "La02 remains visible without its displacement becoming a result; tampered vector and structural-key controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["all_source_rows_retained"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("CriticalityMeasuredValueSuccessorValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_criticality_analysis", "source_hashes")
