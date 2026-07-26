"""Exact post-seal evaluator for the corrected hadron Regge vector."""

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
from sft.physics.hadron_regge_dimensional_terminal_law_v1 import squared_resonance_carrier
from sft.physics.hadron_regge_measured_value_successor_v1 import CLAIM_ID, EXPERIMENT_ID, OBSERVATION_LABEL, SOURCE_FILES, SOURCE_HASH, SOURCE_IDS, SOURCE_PATH, SPEC


TARGET_IDS = ("HADRON-REGGE-WITHHELD-COMPLETE-MEASURED-VALUE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"Regge successor source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-hadron-regge-measured-value-successor-source-record/1":
        raise ValueError("Regge successor schema changed")
    custody = record.get("custody", {})
    required_true = (
        "development_targets_already_known",
        "formal_law_sealed_before_this_record_is_opened_in_execution",
        "all_five_registered_rows_retained",
        "mass_and_width_uncertainties_retained",
        "rho5_summary_omission_retained",
        "pole_mass_uncertainty_not_mislabelled_as_resonance_support",
        "no_slope_intercept_or_residual_fit",
        "no_uncertainty_or_width_widening",
    )
    if any(custody.get(key) is not True for key in required_true):
        raise ValueError("Regge custody disclosure changed")
    if custody.get("formal_law_contains_particle_names_masses_widths_or_units") is not False:
        raise ValueError("Regge formal target isolation changed")
    if custody.get("measurements_select_formal_survivors") is not False:
        raise ValueError("Regge measurement-selection boundary changed")
    expected_keys = ("pdg_2025_rho_770", "pdg_2025_a2_1320", "pdg_2025_rho3_1690", "pdg_2025_a4_1970", "pdg_2025_rho5_2350")
    if tuple(record.get("sources", {})) != expected_keys:
        raise ValueError("complete five-row Regge source vector required")
    return record


def most_restrictive_resonance_support(row):
    centre = Fraction(row["mass_MeV"])
    mass_uncertainty = Fraction(row["mass_standard_uncertainty_MeV"])
    width = Fraction(row["width_MeV"])
    width_lower_uncertainty = Fraction(row["width_lower_uncertainty_MeV"])
    if min(centre, mass_uncertainty, width, width_lower_uncertainty) <= 0 or width <= width_lower_uncertainty:
        raise ValueError("Regge mass/width record must remain exact and positive")
    half_minimum_width = (width - width_lower_uncertainty) / 2
    lower_energy = centre + mass_uncertainty - half_minimum_width
    upper_energy = centre - mass_uncertainty + half_minimum_width
    if lower_energy <= 0 or lower_energy > upper_energy:
        raise ValueError("most restrictive resonance-support intersection is empty")
    unit = Fraction(1000, 1)
    return {
        "minimum_width_MeV": width - width_lower_uncertainty,
        "energy_interval_MeV": (lower_energy, upper_energy),
        "squared_interval_GeV2": ((lower_energy / unit) ** 2, (upper_energy / unit) ** 2),
    }


def exact_regge_analysis(target):
    rows = tuple(item["reported_record"] for item in target["sources"].values())
    if tuple(row["spin_J"] for row in rows) != (1, 2, 3, 4, 5):
        raise ValueError("Regge spin ordering changed")
    expected_jpc = ("1--", "2++", "3--", "4++", "5--")
    supports = tuple(most_restrictive_resonance_support(row) for row in rows)
    carriers = tuple(squared_resonance_carrier(rank) for rank in range(1, 6))
    passes = tuple(support["squared_interval_GeV2"][0] <= carrier <= support["squared_interval_GeV2"][1] for carrier, support in zip(carriers, supports))
    return {
        "row_results": tuple({
            "state": row["state"],
            "spin_J": row["spin_J"],
            "JPC": row["JPC"],
            "exact_squared_carrier_GeV2": carrier,
            "minimum_measured_width_MeV": support["minimum_width_MeV"],
            "most_restrictive_energy_interval_MeV": support["energy_interval_MeV"],
            "most_restrictive_squared_interval_GeV2": support["squared_interval_GeV2"],
            "inside_measured_resonance_support": passed,
            "table_status": row["table_status"],
        } for row, carrier, support, passed in zip(rows, carriers, supports, passes)),
        "complete_five_rows": len(rows) == 5,
        "natural_parity_vector": tuple(row["JPC"] for row in rows) == expected_jpc,
        "exact_carrier_vector": carriers == (Fraction(3, 5), Fraction(9, 5), Fraction(3), Fraction(21, 5), Fraction(27, 5)),
        "all_five_inside_measured_support": all(passes),
        "rho5_omission_retained": "OMITTED FROM SUMMARY TABLE" in rows[-1]["table_status"],
        "no_fit_declared": target["custody"]["no_slope_intercept_or_residual_fit"] is True,
        "no_widening_declared": target["custody"]["no_uncertainty_or_width_widening"] is True,
    }


class HadronReggeMeasuredValueSuccessorValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Regge successor seal")
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
            raise ValueError("Regge successor prediction audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("Regge successor prediction label changed")
        released = context[TARGET_IDS[0]]
        analysis = exact_regge_analysis(released)
        empirical = all(analysis[key] for key in ("complete_five_rows", "natural_parity_vector", "exact_carrier_vector", "all_five_inside_measured_support", "rho5_omission_retained", "no_fit_declared", "no_widening_declared"))
        tampered = json.loads(json.dumps(released))
        tampered["sources"]["pdg_2025_a2_1320"]["reported_record"]["mass_MeV"] = "1000"
        tampered["sources"]["pdg_2025_a2_1320"]["reported_record"]["width_MeV"] = "107"
        tampered_rejected = not exact_regge_analysis(tampered)["all_five_inside_measured_support"]
        missing = json.loads(json.dumps(released))
        missing["sources"].pop("pdg_2025_rho5_2350")
        try:
            missing_rejected = not exact_regge_analysis(missing)["complete_five_rows"]
        except ValueError:
            missing_rejected = True
        passed = all(row[2] for row in SPEC.operational_witnesses) and empirical and tampered_rejected and missing_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-hadron-regge-measured-value-successor/1", registration_hash, FALSIFICATION_CONDITION)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "sources": source_hashes(), "target": target_identity, "analysis": analysis, "tampered_rejected": tampered_rejected, "missing_rejected": missing_rejected}
        measurements = (
            "Exact zero-parameter Regge base is 3/5 GeV^2 and exact successor step is 6/5 GeV^2.",
            "All five exact squared carriers lie inside the corresponding most-restrictive measured resonance-support intervals.",
            "Every mass, mass uncertainty, width, width uncertainty and listing status is retained once.",
            "The rho5 summary omission and single-measurement status remain explicit.",
            "No slope, intercept, residual or correction is fitted; displaced and missing-row controls reject.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, analysis["complete_five_rows"], SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("HadronReggeMeasuredValueSuccessorValidator", "FALSIFICATION_CONDITION", "TARGET_IDS", "authoritative_record", "exact_regge_analysis", "most_restrictive_resonance_support", "source_hashes")
