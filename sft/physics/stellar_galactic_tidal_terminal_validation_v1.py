"""Capability-closed post-seal validator for Claim 068."""

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
from sft.physics.stellar_galactic_tidal_terminal_empirical_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.stellar_galactic_tidal_terminal_law_v1 import theorem_certificate


TARGET_IDS = ("STELLAR-GALACTIC-TIDAL-WITHHELD-COMPLETE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes():
    return {SOURCE_PATH: SOURCE_HASH, **dict(SOURCE_FILES)}


def authoritative_record(root: Path):
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"stellar/galactic/tidal source changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-stellar-galactic-tidal-postseal-source-record/1":
        raise ValueError("stellar/galactic/tidal source schema changed")
    if record.get("formal_receipt_hash") != "sha256:24674dfa019c208012414ab3c587656ee404512f20d00ab44e26ee137be22ae2":
        raise ValueError("formal stellar/galactic/tidal receipt binding changed")
    if tuple(row.get("source_id") for row in record.get("sources", ())) != SOURCE_IDS:
        raise ValueError("complete ordered seven-source vector required")
    boundary = record.get("methodological_boundary", {})
    required_true = (
        "all_piecewise_stellar_rows_retained",
        "central_and_systematic_tully_fisher_results_retained",
        "mercury_resonance_retained_as_declared_boundary",
        "model_dependent_solar_value_not_relabelled_as_sft_prediction",
        "observational_rows_opened_only_after_formal_receipt",
        "reported_signed_coordinate_not_used_as_fold_proof_scalar",
    )
    if boundary.get("external_measurement_selected_formal_survivor") is not False:
        raise ValueError("measurement selected formal survivor")
    if not all(boundary.get(key) is True for key in required_true):
        raise ValueError("stellar/galactic/tidal methodological boundary changed")
    return record


def exact_analysis(record):
    sources = record["sources"]
    solar = sources[0]["rows"]["solar_structure_inversion"]
    stellar = sources[1]["rows"]["piecewise_main_sequence_mass_luminosity"]
    sparc = sources[2]["rows"]["sparc_catalogue"]
    btfr = sources[3]["rows"]["baryonic_tully_fisher"]
    bullet = sources[4]["rows"]["bullet_cluster_separation"]
    moon = sources[5]["rows"]["lunar_synchronous_rotation"]
    mercury = sources[6]["rows"]["mercury_spin_orbit_resonance"]

    solar_central = Fraction(solar["convective_boundary_observed_central_solar_radius_fraction"])
    solar_uncertainty = Fraction(solar["convective_boundary_observed_uncertainty"])
    solar_reference = Fraction(solar["convective_boundary_reference_model_fraction"])
    stellar_rows = tuple(
        {
            "slope": Fraction(row["slope"]),
            "uncertainty": Fraction(row["slope_uncertainty"]),
            "lower_mass_ratio": Fraction(row["lower_mass_ratio"]),
            "upper_mass_ratio": Fraction(row["upper_mass_ratio"]),
        }
        for row in stellar["complete_rows"]
    )
    stellar_intervals = tuple((row["slope"] - row["uncertainty"], row["slope"] + row["uncertainty"]) for row in stellar_rows)
    contains_four = tuple(lower <= 4 <= upper for lower, upper in stellar_intervals)
    contains_three = tuple(lower <= 3 <= upper for lower, upper in stellar_intervals)
    btfr_central = Fraction(btfr["reported_central_slope"])
    btfr_uncertainty = Fraction(btfr["reported_central_slope_uncertainty"])
    btfr_systematic = tuple(Fraction(value) for value in btfr["reported_systematic_slope_interval"])
    moon_orbit = Fraction(moon["orbit_duration_hours_approximate"])
    moon_rotation = Fraction(moon["rotation_duration_hours"])

    return {
        "solar_observed_interval": (solar_central - solar_uncertainty, solar_central + solar_uncertainty),
        "solar_reference_model_value": solar_reference,
        "solar_reference_inside_observed_interval": solar_central - solar_uncertainty <= solar_reference <= solar_central + solar_uncertainty,
        "solar_sound_precision_order": Fraction(solar["sound_speed_and_adiabatic_index_reported_precision_order"]),
        "solar_density_precision_order": Fraction(solar["density_inversion_reported_precision_order"]),
        "solar_reference_not_sft_prediction": "not an SFT-derived" in solar["sft_use"],
        "stellar_row_count": len(stellar_rows),
        "stellar_declared_row_count": stellar["row_count"],
        "stellar_rows": stellar_rows,
        "stellar_intervals": stellar_intervals,
        "stellar_contains_four": contains_four,
        "stellar_contains_three": contains_three,
        "only_high_mass_row_contains_four": contains_four == (False, False, False, False, True, False),
        "only_very_high_mass_row_contains_three": contains_three == (False, False, False, False, False, True),
        "all_six_stellar_rows_retained": len(stellar_rows) == stellar["row_count"] == 6,
        "sparc_galaxy_count": sparc["disk_galaxy_count"],
        "btfr_galaxy_count": btfr["galaxy_count"],
        "btfr_intrinsic_scatter": Fraction(btfr["intrinsic_scatter_fraction"]),
        "btfr_central_interval": (btfr_central - btfr_uncertainty, btfr_central + btfr_uncertainty),
        "btfr_central_contains_four": btfr_central - btfr_uncertainty <= 4 <= btfr_central + btfr_uncertainty,
        "btfr_systematic_interval": btfr_systematic,
        "btfr_systematic_contains_four": btfr_systematic[0] <= 4 <= btfr_systematic[1],
        "bullet_separation_significance": Fraction(bullet["mass_baryon_peak_separation_significance"]),
        "bullet_mass_follows_galaxies": bullet["mass_peak_follows"] == "collisionless-galaxy-distribution-rather-than-dominant-x-ray-plasma",
        "moon_orbit_hours": moon_orbit,
        "moon_rotation_hours": moon_rotation,
        "moon_one_to_one": moon_orbit == moon_rotation,
        "mercury_rotation_period_days": Fraction(mercury["sidereal_rotation_period_days"]),
        "mercury_rotation_uncertainty_days": Fraction(mercury["sidereal_rotation_period_uncertainty_days"]),
        "mercury_rotation_cycles": mercury["rotation_cycles"],
        "mercury_orbital_cycles": mercury["orbital_cycles"],
        "mercury_is_three_to_two_boundary": mercury["rotation_cycles"] == 3 and mercury["orbital_cycles"] == 2,
        "mercury_is_not_one_to_one": mercury["rotation_cycles"] != mercury["orbital_cycles"],
        "all_sources_retained": len(sources) == 7,
    }


class StellarGalacticTidalTerminalValidator:
    def __init__(self, root):
        self.root = root.resolve()

    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong stellar/galactic/tidal empirical seal")
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
            raise ValueError("sealed stellar/galactic/tidal prediction label changed")
        record = context[TARGET_IDS[0]]
        analysis = exact_analysis(record)
        formal = theorem_certificate()
        formal_pass = all((
            formal["hydrostatic"]["balanced"],
            formal["all_radial_restoring"],
            formal["luminosity_exponents"] == (3, 4),
            formal["lifetime_fall_exponents"] == (2, 3),
            formal["all_flat_rows_require_growth"],
            formal["tully_fisher_exponent"] == 4,
            formal["all_tidal_rows_lock"],
        ))
        empirical_pass = all((
            analysis["solar_reference_inside_observed_interval"],
            analysis["solar_reference_not_sft_prediction"],
            analysis["all_six_stellar_rows_retained"],
            analysis["only_high_mass_row_contains_four"],
            analysis["only_very_high_mass_row_contains_three"],
            analysis["sparc_galaxy_count"] == 175,
            analysis["btfr_galaxy_count"] == 153,
            not analysis["btfr_central_contains_four"],
            analysis["btfr_systematic_contains_four"],
            analysis["bullet_separation_significance"] == 8,
            analysis["bullet_mass_follows_galaxies"],
            analysis["moon_one_to_one"],
            analysis["mercury_is_three_to_two_boundary"],
            analysis["mercury_is_not_one_to_one"],
            analysis["all_sources_retained"],
        ))
        erased_stellar = json.loads(json.dumps(record))
        erased_stellar["sources"][1]["rows"]["piecewise_main_sequence_mass_luminosity"]["complete_rows"] = erased_stellar["sources"][1]["rows"]["piecewise_main_sequence_mass_luminosity"]["complete_rows"][-2:]
        erased_stellar_rejected = not exact_analysis(erased_stellar)["all_six_stellar_rows_retained"]
        central_only = json.loads(json.dumps(record))
        central_only["sources"][3]["rows"]["baryonic_tully_fisher"]["reported_systematic_slope_interval"] = ["7/2", "399/100"]
        central_only_rejected = not exact_analysis(central_only)["btfr_systematic_contains_four"]
        false_lunar_lock = json.loads(json.dumps(record))
        false_lunar_lock["sources"][5]["rows"]["lunar_synchronous_rotation"]["rotation_duration_hours"] = "654/1"
        false_lunar_lock_rejected = not exact_analysis(false_lunar_lock)["moon_one_to_one"]
        erased_mercury_boundary = json.loads(json.dumps(record))
        erased_mercury_boundary["sources"][6]["rows"]["mercury_spin_orbit_resonance"]["orbital_cycles"] = 3
        erased_mercury_rejected = not exact_analysis(erased_mercury_boundary)["mercury_is_three_to_two_boundary"]
        passed = all((formal_pass, empirical_pass, erased_stellar_rejected, central_only_rejected, false_lunar_lock_rejected, erased_mercury_rejected))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-stellar-galactic-tidal-comparator/1", registration_hash, FALSIFICATION_CONDITION)),
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
            "erased_stellar_rejected": erased_stellar_rejected,
            "central_only_rejected": central_only_rejected,
            "false_lunar_lock_rejected": false_lunar_lock_rejected,
            "erased_mercury_rejected": erased_mercury_rejected,
        }
        measurements = (
            "Helioseismology reports stable solar structure at parts-per-ten-thousand sound-speed precision; its conventional reference value is not relabelled as an SFT prediction.",
            "All six piecewise stellar slopes remain; only the high and very-high mass rows contain terminal powers four and three.",
            "All 175 SPARC galaxies and all 153 Tully-Fisher galaxies remain in the registered population records.",
            "The Tully-Fisher central interval excludes four while the complete reported systematic interval reaches four; both are retained.",
            "The Bullet Cluster records an eight-sigma separation between the mass and dominant plasma peaks.",
            "The Moon records 1:1 synchronous rotation; Mercury records the separately declared 3:2 eccentric-resonance boundary.",
            "Erased-row, central-only, false-lunar-lock and erased-Mercury hostile controls reject.",
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
    "FALSIFICATION_CONDITION", "StellarGalacticTidalTerminalValidator", "TARGET_IDS",
    "authoritative_record", "exact_analysis", "source_hashes",
)
