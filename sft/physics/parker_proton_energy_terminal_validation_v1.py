"""Target-inaccessible Parker and CODATA comparison for the exact energy share."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
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
from sft.physics.parker_proton_energy_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    historical_leading_fraction,
    proton_energy_fraction,
    structural_formula_census,
)


SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/parker-proton-energy-source-record.json"
SOURCE_RECORD_HASH = "sha256:bd644fb01e46ae9ee3cdb096776e4d68fcfecc4ecb9bba078f3ac185edaecae1"
PARKER_PATH = "experiments/external_sources/physics/snapshots/desai-2025-parker-400kev.pdf"
PARKER_HASH = "sha256:6c950a6e142edf57df600d06e1ce40445fc18c84d42c3d2b916d63679a100fb5"
CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
SOURCE_IDS = ("DESAI-ET-AL-2025-PARKER-HCS-PROTONS", "NIST-CODATA-2022")
TARGET_IDS = ("WITHHELD-PARKER-PROTON-RANGE-AND-CODATA-SCALE",)
FALSIFICATION_CONDITION = (
    "Reject if any source identity or registered row changes; if the terminal "
    "fraction or NIST-propagated prediction leaves the complete 67-527 keV Parker "
    "analysis range; if approximately 400 keV is presented as an exact cutoff or "
    "given an unreported uncertainty; if the broad observation is claimed to "
    "empirically select eight over every adverse formula; if a local plasma value "
    "enters the derivation; or if targets are accessible before prediction sealing."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        PARKER_PATH: PARKER_HASH,
        CODATA_PATH: CODATA_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"Parker source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-parker-proton-energy-source-record/1" or record.get("source_id") != "DESAI-2025-PARKER-NIST-CODATA-PROTON-ENERGY":
        raise ValueError("Parker source record identity changed")
    sources = tuple((row.get("source_id"), row.get("snapshot_path"), row.get("snapshot_hash")) for row in record.get("sources", ()))
    if sources != (
        (SOURCE_IDS[0], PARKER_PATH, PARKER_HASH),
        (SOURCE_IDS[1], CODATA_PATH, CODATA_HASH),
    ):
        raise ValueError("Parker source bindings changed")
    target = record.get("registered_target", {})
    event = target.get("parker_event", {})
    required_event = {
        "event_date": "2022-12-12",
        "heliocentric_distance_solar_radii": "16.25",
        "spectral_analysis_lower_keV": "67",
        "spectral_analysis_upper_keV": "527",
        "pitch_angle_analysis_lower_keV": "67",
        "pitch_angle_analysis_upper_keV": "570",
        "reported_power_law_index_magnitude": "5.1",
        "available_magnetic_energy_per_particle_keV": "0.56",
        "approximately_400_is_exact_cutoff_measurement": False,
        "approximately_400_has_reported_standard_uncertainty": False,
        "paper_calls_399_714_keV_a_prediction": False,
    }
    if any(event.get(key) != value for key, value in required_event.items()) or len(event.get("reported_energy_wording", ())) != 3:
        raise ValueError("Parker event rows changed")
    proton = target.get("proton_rest_energy", {})
    if proton != {
        "quantity": "proton mass energy equivalent in MeV",
        "value_MeV": "938.27208943",
        "standard_uncertainty_MeV": "0.00000029",
    }:
        raise ValueError("CODATA proton row changed")
    custody = record.get("row_custody", {})
    required_true = (
        "abstract_and_event_rows_retained",
        "complete_spectral_range_retained",
        "complete_pitch_angle_range_retained",
        "power_law_and_magnetic_energy_context_retained",
        "approximation_and_missing_uncertainty_retained",
        "proton_mass_and_uncertainty_retained",
        "target_inaccessible_to_prediction_program",
    )
    if not all(custody.get(key) is True for key in required_true) or custody.get("measurement_selects_formula") is not False or custody.get("precision_cutoff_claim_permitted") is not False:
        raise ValueError("Parker custody rows changed")
    return record


def formal_prediction_inputs() -> dict[str, object]:
    terminal = proton_energy_fraction()
    leading = historical_leading_fraction()
    return {
        "terminal_fraction": PositiveRatio.from_pair(terminal.numerator, terminal.denominator),
        "historical_fraction": PositiveRatio.from_pair(leading.numerator, leading.denominator),
        "channel_relation": HeldLabel("proton-colour-channels", "three-squared-Take-One-is-eight"),
        "energy_relation": HeldLabel("field-energy", "electromagnetic-amplitude-self-composition"),
        "scale_boundary": HeldLabel("dimensionful-scale", "proton-rest-energy-postseal-only"),
        "provenance": HeldLabel("provenance", "observational-derivation-not-historical-blindness"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend((
        {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-exact-prediction", "instructions": instructions}


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-parker-proton-energy-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "frozen_relation": "The current exact proton share is eight terminal-alpha squared; the leading-rung V2 fraction remains a historical control.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_ids": SOURCE_IDS,
        "source_hashes": source_hashes(),
        "row_retention_policy": "complete primary event/range/context rows, exact CODATA proton row, all forced-sector/power controls and precision nonclaim",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "exact rational interval propagation and complete adverse-formula range census",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("Parker prediction has wrong Fold shape")
    return dict(zip(keys, output.cells))


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    event = target["parker_event"]
    proton = target["proton_rest_energy"]
    mass = Fraction(proton["value_MeV"])
    uncertainty = Fraction(proton["standard_uncertainty_MeV"])
    mass_interval = (mass - uncertainty, mass + uncertainty)
    terminal = proton_energy_fraction()
    leading = historical_leading_fraction()
    terminal_interval = tuple(edge * 1000 * terminal for edge in mass_interval)
    leading_interval = tuple(edge * 1000 * leading for edge in mass_interval)
    reported_range = (Fraction(event["spectral_analysis_lower_keV"]), Fraction(event["spectral_analysis_upper_keV"]))
    point = Fraction(400, 1)
    terminal_centre = mass * 1000 * terminal
    adverse = tuple({
        **row,
        "energy_keV": mass * 1000 * row["fraction"],
        "inside_reported_range": reported_range[0] <= mass * 1000 * row["fraction"] <= reported_range[1],
    } for row in structural_formula_census())
    return {
        "mass_interval_MeV": mass_interval,
        "terminal_prediction_interval_keV": terminal_interval,
        "terminal_prediction_centre_keV": terminal_centre,
        "leading_prediction_interval_keV": leading_interval,
        "reported_spectrum_range_keV": reported_range,
        "terminal_inside_complete_range": reported_range[0] <= terminal_interval[0] <= terminal_interval[1] <= reported_range[1],
        "leading_inside_complete_range": reported_range[0] <= leading_interval[0] <= leading_interval[1] <= reported_range[1],
        "absolute_difference_from_approximate_400_keV": point - terminal_centre if point >= terminal_centre else terminal_centre - point,
        "relative_difference_from_approximate_label": (point - terminal_centre if point >= terminal_centre else terminal_centre - point) / point,
        "approximate_label_has_uncertainty": event["approximately_400_has_reported_standard_uncertainty"],
        "approximate_label_is_exact_cutoff": event["approximately_400_is_exact_cutoff_measurement"],
        "adverse_formula_rows": adverse,
        "adverse_inside_range": tuple((row["sector"], row["power"]) for row in adverse if row["inside_reported_range"]),
        "observation_uniquely_selects_structural_formula": sum(row["inside_reported_range"] for row in adverse) == 1,
    }


class ParkerProtonEnergyValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Parker proton-energy seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        keys = tuple(inputs)
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {key: sha256_identity(value) for key, value in inputs.items()},
            TARGET_IDS,
            sha256_identity((sealed.seal_hash, registration["frozen_relation"])),
            registration_hash,
        )
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
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
            raise ValueError("Parker hostile-package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("Parker prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        all_rows = len(analysis["adverse_formula_rows"]) == 12 and len(context[TARGET_IDS[0]]["parker_event"]["reported_energy_wording"]) == 3
        controls = all((
            analysis["terminal_inside_complete_range"],
            analysis["leading_inside_complete_range"],
            analysis["approximate_label_has_uncertainty"] is False,
            analysis["approximate_label_is_exact_cutoff"] is False,
            analysis["observation_uniquely_selects_structural_formula"] is False,
            (2, 2) in analysis["adverse_inside_range"],
            (3, 2) in analysis["adverse_inside_range"],
        ))
        tampered = json.loads(json.dumps(context[TARGET_IDS[0]]))
        tampered["parker_event"]["spectral_analysis_upper_keV"] = "300"
        tampered_rejected = not exact_measurement_analysis(tampered)["terminal_inside_complete_range"]
        passed = all((all_rows, controls, tampered_rejected))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-parker-proton-energy-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=interpreter_hash,
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=comparator_hash,
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
            "prediction_seal": prediction_seal.seal_hash,
            "source_hashes": source_hashes(),
            "target_identity": target_identity,
            "analysis": analysis,
            "all_rows": all_rows,
            "controls": controls,
            "tampered_rejected": tampered_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "The primary Parker manuscript, complete CODATA source and curated row record are hash-locked and released only after the exact Fold prediction seal.",
            "The terminal prediction from the complete current alpha rung is approximately 399.714077 keV after post-seal CODATA scale translation; the retained V2 leading-rung control is approximately 399.714072 keV.",
            "Both exact propagated prediction intervals lie inside the paper's complete 67-527 keV analyzed proton spectrum.",
            "The primary paper reports protons up to, above and upwards of approximately 400 keV; it does not register 400 keV as an exact cutoff and gives no standard uncertainty for that approximate label.",
            "Therefore the earlier 'within 0.1 percent' wording is not admitted as a precision measurement claim; only range-level correspondence is supported.",
            "The complete forced-sector/power control census is retained. Both three-alpha-squared and eight-alpha-squared land inside the broad observed range, so the Parker event alone does not select the eight-channel formula.",
            "Eight channels remain structurally selected by the independently admitted proton colour sector, never by the Parker target.",
            "Changing the external upper range to 300 keV rejects the prediction as an unfavorable control.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            all_rows,
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION",
    "ParkerProtonEnergyValidator",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
)
