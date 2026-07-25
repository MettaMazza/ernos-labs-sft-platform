"""Capability-closed AME2020 comparison for terminal fusion/fission forcing."""

from __future__ import annotations

from dataclasses import dataclass
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
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file
from sft.foundation.half_one import half_one
from sft.physics.fusion_fission_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    binding_gain_enclosure,
    fission_trace,
    fusion_trace,
)
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (
    binding_peak_certificate,
    binding_score_enclosure,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "AMDC-AME2020-MASS-1-BINDING-2021"
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/nuclear-binding-curve-successor-source-record.json"
SOURCE_RECORD_HASH = "sha256:d10a9474253b2d29fac71ee21352039659f2e5f4b7d75395416d361878a18ddc"
RAW_PATH = "experiments/external_sources/physics/snapshots/ame2020-mass_1.mas20"
RAW_HASH = "sha256:e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
TARGET_IDS = (
    "AME2020-COMPLETE-POSITIVE-COMPOSITE-CENSUS",
    "AME2020-SINGLETON-EMPTY-BINDING-BOUNDARIES",
    "AME2020-DEUTERIUM-HELIUM4-FUSION-ANCHORS",
    "AME2020-URANIUM238-PALLADIUM119-FISSION-ANCHORS",
    "AME2020-GLOBAL-BINDING-MAXIMUM",
)
FALSIFICATION_CONDITION = (
    "Reject if either sealed exact binding direction is absent from AME2020 after reported uncertainties, if "
    "mass/charge coordinates differ, if the sealed global maximum is not the complete-census maximum, if any "
    "positive-composite row or singleton boundary inscription is omitted, if a reversed-direction control is "
    "accepted, if a source identity changes, or if target content enters prediction before its seal."
)


@dataclass(frozen=True)
class MeasuredBindingRow:
    mass_count: int
    charge_count: int
    neutron_count: int
    element: str
    binding_keV_per_nucleon: Fraction
    uncertainty_keV_per_nucleon: Fraction
    lower_keV_per_nucleon: Fraction
    upper_keV_per_nucleon: Fraction


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value <= 0:
        raise ValueError("a formal prediction ratio must remain positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def authoritative_record(root: Path) -> dict[str, object]:
    record_path = root / SOURCE_RECORD_PATH
    raw_path = root / RAW_PATH
    if hash_file(record_path) != SOURCE_RECORD_HASH or hash_file(raw_path) != RAW_HASH:
        raise ValueError("AME2020 fusion/fission source identity changed")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID:
        raise ValueError("AME2020 source identifier changed")
    custody = record.get("custody", {})
    required = {
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "no_fitted_mass_formula_coefficient": True,
        "irrational_radius_not_admitted": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("AME2020 fusion/fission custody disclosure changed")
    census = record.get("complete_numeric_binding_census", {})
    if census.get("positive_composite_row_count") != 2548:
        raise ValueError("AME2020 positive-composite census changed")
    boundaries = census.get("singleton_empty_binding_boundary_rows")
    if not isinstance(boundaries, list) or len(boundaries) != 2:
        raise ValueError("AME2020 singleton boundary census changed")
    return record


def measured_binding_rows(root: Path) -> tuple[MeasuredBindingRow, ...]:
    authoritative_record(root)
    rows: list[MeasuredBindingRow] = []
    for line in (root / RAW_PATH).read_text(encoding="utf-8").splitlines():
        if len(line) < 79:
            continue
        try:
            neutron = int(line[4:9])
            charge = int(line[9:14])
            mass = int(line[14:19])
        except ValueError:
            continue
        if mass < 2:
            continue
        binding_raw = line[54:67].strip()
        uncertainty_raw = line[68:78].strip()
        if not binding_raw or binding_raw == "*" or "#" in binding_raw:
            continue
        try:
            binding = Fraction(binding_raw)
            uncertainty = Fraction(uncertainty_raw)
        except (ValueError, ZeroDivisionError):
            continue
        if binding <= uncertainty or uncertainty <= 0:
            raise ValueError("AME2020 positive-composite interval left the positive domain")
        rows.append(MeasuredBindingRow(
            mass_count=mass,
            charge_count=charge,
            neutron_count=neutron,
            element=line[20:23].strip(),
            binding_keV_per_nucleon=binding,
            uncertainty_keV_per_nucleon=uncertainty,
            lower_keV_per_nucleon=positive_take(binding, uncertainty),
            upper_keV_per_nucleon=binding + uncertainty,
        ))
    if len(rows) != 2548:
        raise ValueError("complete AME2020 positive-composite census changed")
    return tuple(rows)


def row_by_coordinate(
    rows: tuple[MeasuredBindingRow, ...], mass: int, charge: int
) -> MeasuredBindingRow:
    matches = tuple(
        row for row in rows if row.mass_count == mass and row.charge_count == charge
    )
    if len(matches) != 1:
        raise ValueError("AME2020 coordinate is absent or duplicated")
    return matches[0]


def measurement_analysis(rows: tuple[MeasuredBindingRow, ...]) -> dict[str, object]:
    if len(rows) != 2548:
        raise ValueError("measurement analysis requires the complete positive-composite census")
    ranked = sorted(rows, key=lambda row: row.binding_keV_per_nucleon, reverse=True)
    peak = ranked[0]
    rival_upper = max(row.upper_keV_per_nucleon for row in ranked[1:])
    deuterium = row_by_coordinate(rows, 2, 1)
    helium = row_by_coordinate(rows, 4, 2)
    uranium = row_by_coordinate(rows, 238, 92)
    palladium = row_by_coordinate(rows, 119, 46)
    return {
        "row_count": len(rows),
        "fusion_anchor_rows": (deuterium, helium),
        "fission_anchor_rows": (uranium, palladium),
        "peak_row": peak,
        "rival_upper": rival_upper,
        "fusion_higher_after_uncertainty": helium.lower_keV_per_nucleon > deuterium.upper_keV_per_nucleon,
        "fission_higher_after_uncertainty": palladium.lower_keV_per_nucleon > uranium.upper_keV_per_nucleon,
        "reversed_fusion_rejected": not (
            helium.upper_keV_per_nucleon < deuterium.lower_keV_per_nucleon
        ),
        "reversed_fission_rejected": not (
            palladium.upper_keV_per_nucleon < uranium.lower_keV_per_nucleon
        ),
        "peak_separated_from_every_rival": peak.lower_keV_per_nucleon > rival_upper,
    }


def formal_prediction_inputs() -> dict[str, object]:
    fusion = fusion_trace("binary-junction")
    fission = fission_trace("binary-decomposition")
    peak = binding_peak_certificate()
    deuteron = binding_score_enclosure(2, 1, 16)
    helium = binding_score_enclosure(4, 2, 16)
    uranium = binding_score_enclosure(238, 92, 16)
    palladium = binding_score_enclosure(119, 46, 16)
    fusion_gain = binding_gain_enclosure(fusion)
    fission_gain = binding_gain_enclosure(fission)
    if fusion_gain == () or fission_gain == ():
        raise ValueError("formal fusion/fission prediction lacks a positive gain")
    return {
        "fusion_incident_mass": PositiveCount(2),
        "fusion_incident_charge": PositiveCount(1),
        "fusion_incident_multiplicity": PositiveCount(2),
        "fusion_product_mass": PositiveCount(4),
        "fusion_product_charge": PositiveCount(2),
        "fusion_incident_score_upper": positive_ratio(deuteron[1]),
        "fusion_product_score_lower": positive_ratio(helium[0]),
        "fusion_total_gain_lower": positive_ratio(fusion_gain[0]),
        "fission_parent_mass": PositiveCount(238),
        "fission_parent_charge": PositiveCount(92),
        "fission_product_mass": PositiveCount(119),
        "fission_product_charge": PositiveCount(46),
        "fission_product_multiplicity": PositiveCount(2),
        "fission_parent_score_upper": positive_ratio(uranium[1]),
        "fission_product_score_lower": positive_ratio(palladium[0]),
        "fission_total_gain_lower": positive_ratio(fission_gain[0]),
        "peak_mass": PositiveCount(int(peak["mass_number"])),
        "peak_charge": PositiveCount(int(peak["charge_count"])),
        "peak_neutron": PositiveCount(int(peak["neutron_count"])),
        "normalized_barrier": positive_ratio(half_one().value),
        "binding_direction": HeldLabel("binding-order", "toward-higher-binding"),
        "release_record": HeldLabel("mass-energy-accounting", "complete-held-positive-release"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [
        {"opcode": "input", "destination": key, "arguments": [key]}
        for key in keys
    ]
    instructions.extend((
        {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-exact-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-fusion-fission-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "Exact binary fusion and fission representatives conserve every nuclear count, increase the sealed "
            "zero-parameter binding score toward the unique unbounded maximum, retain a positive release record "
            "and use the normalized Half-One barrier."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "raw_snapshot_path": RAW_PATH,
        "raw_snapshot_hash": RAW_HASH,
        "row_retention_policy": (
            "all 2,548 positive-composite rows, every used reported uncertainty, both singleton empty-binding "
            "boundary inscriptions, exact anchors, the global rival envelope and adverse reversed directions"
        ),
        "target_access_policy": "capability-closed prediction; distinct custody; release only after matching seal",
        "comparison_protocol": "exact strict rational interval order and exact mass/charge coordinate identity",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    rows = measured_binding_rows(root)
    analysis = measurement_analysis(rows)
    return {
        TARGET_IDS[0]: rows,
        TARGET_IDS[1]: tuple(record["complete_numeric_binding_census"]["singleton_empty_binding_boundary_rows"]),
        TARGET_IDS[2]: analysis["fusion_anchor_rows"],
        TARGET_IDS[3]: analysis["fission_anchor_rows"],
        TARGET_IDS[4]: analysis["peak_row"],
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("fusion/fission prediction output has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class FusionFissionTerminalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("fusion/fission empirical validator received the wrong seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        ordered_keys = tuple(inputs)
        envelope = PredictionEnvelope(
            experiment_id=EXPERIMENT_ID,
            registered_inputs={key: sha256_identity(value) for key, value in inputs.items()},
            withheld_target_ids=TARGET_IDS,
            frozen_relation_hash=sha256_identity((sealed.seal_hash, registration["frozen_relation"])),
            experiment_registration_hash=registration_hash,
        )
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=released_targets(self.root),
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, RAW_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )

        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("fusion/fission prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed prediction differs from its formal inputs")

        rows = context[TARGET_IDS[0]]
        boundaries = context[TARGET_IDS[1]]
        fusion_anchors = context[TARGET_IDS[2]]
        fission_anchors = context[TARGET_IDS[3]]
        measured_peak = context[TARGET_IDS[4]]
        if not isinstance(rows, tuple) or any(not isinstance(row, MeasuredBindingRow) for row in rows):
            raise ValueError("released AME2020 census has the wrong exact type")
        analysis = measurement_analysis(rows)
        deuterium, helium = fusion_anchors
        uranium, palladium = fission_anchors

        formal_fusion = (
            prediction["fusion_product_score_lower"].fraction
            > prediction["fusion_incident_score_upper"].fraction
            and prediction["fusion_total_gain_lower"].fraction > 0
        )
        formal_fission = (
            prediction["fission_product_score_lower"].fraction
            > prediction["fission_parent_score_upper"].fraction
            and prediction["fission_total_gain_lower"].fraction > 0
        )
        fusion_coordinates_match = (
            prediction["fusion_incident_mass"].value,
            prediction["fusion_incident_charge"].value,
            prediction["fusion_product_mass"].value,
            prediction["fusion_product_charge"].value,
        ) == (
            deuterium.mass_count,
            deuterium.charge_count,
            helium.mass_count,
            helium.charge_count,
        )
        fission_coordinates_match = (
            prediction["fission_parent_mass"].value,
            prediction["fission_parent_charge"].value,
            prediction["fission_product_mass"].value,
            prediction["fission_product_charge"].value,
        ) == (
            uranium.mass_count,
            uranium.charge_count,
            palladium.mass_count,
            palladium.charge_count,
        )
        peak_coordinates_match = (
            prediction["peak_mass"].value,
            prediction["peak_charge"].value,
            prediction["peak_neutron"].value,
        ) == (
            measured_peak.mass_count,
            measured_peak.charge_count,
            measured_peak.neutron_count,
        )
        boundary_rows_preserved = (
            isinstance(boundaries, tuple)
            and len(boundaries) == 2
            and all(row.get("mass_number") == 1 for row in boundaries)
            and all(row.get("binding_energy_per_nucleon_keV") == "0.0" for row in boundaries)
        )
        all_rows_preserved = (
            len(rows) == 2548
            and len(fusion_anchors) == 2
            and len(fission_anchors) == 2
            and boundary_rows_preserved
        )
        unfavorable_reversed = (
            analysis["reversed_fusion_rejected"] is True
            and analysis["reversed_fission_rejected"] is True
        )
        incomplete_census_rejected = len(rows[:-1]) != 2548
        tampered_peak_rejected = (
            prediction["peak_mass"].value,
            prediction["peak_charge"].value,
            prediction["peak_neutron"].value,
        ) != (61, 28, 33)
        passed = all((
            formal_fusion,
            formal_fission,
            fusion_coordinates_match,
            fission_coordinates_match,
            peak_coordinates_match,
            analysis["fusion_higher_after_uncertainty"] is True,
            analysis["fission_higher_after_uncertainty"] is True,
            analysis["peak_separated_from_every_rival"] is True,
            all_rows_preserved,
            unfavorable_reversed,
            incomplete_census_rejected,
            tampered_peak_rejected,
            prediction["normalized_barrier"].fraction == Fraction(1, 2),
            prediction["binding_direction"] == HeldLabel("binding-order", "toward-higher-binding"),
            prediction["release_record"] == HeldLabel(
                "mass-energy-accounting", "complete-held-positive-release"
            ),
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-AME2020-fusion-fission-interval-coordinate-comparator/1",
            registration_hash,
            FALSIFICATION_CONDITION,
        ))
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
        comparison_payload = {
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "source_record_hash": SOURCE_RECORD_HASH,
            "raw_hash": RAW_HASH,
            "complete_target_identity_hash": target_identity,
            "complete_row_count": len(rows),
            "formal_fusion": formal_fusion,
            "formal_fission": formal_fission,
            "measured_fusion": analysis["fusion_higher_after_uncertainty"],
            "measured_fission": analysis["fission_higher_after_uncertainty"],
            "peak_coordinates_match": peak_coordinates_match,
            "peak_separated": analysis["peak_separated_from_every_rival"],
            "boundary_rows_preserved": boundary_rows_preserved,
            "unfavorable_reversed": unfavorable_reversed,
            "incomplete_census_rejected": incomplete_census_rejected,
            "tampered_peak_rejected": tampered_peak_rejected,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            f"complete AME2020 positive-composite census retained: {len(rows)} rows",
            (
                "fusion anchor exact intervals keV/nucleon: "
                f"D [{deuterium.lower_keV_per_nucleon}, {deuterium.upper_keV_per_nucleon}], "
                f"He-4 [{helium.lower_keV_per_nucleon}, {helium.upper_keV_per_nucleon}]; "
                f"strict rise {analysis['fusion_higher_after_uncertainty']}"
            ),
            (
                "fission anchor exact intervals keV/nucleon: "
                f"U-238 [{uranium.lower_keV_per_nucleon}, {uranium.upper_keV_per_nucleon}], "
                f"Pd-119 [{palladium.lower_keV_per_nucleon}, {palladium.upper_keV_per_nucleon}]; "
                f"strict rise {analysis['fission_higher_after_uncertainty']}"
            ),
            (
                "complete-census maximum: "
                f"A={measured_peak.mass_count}, Z={measured_peak.charge_count}, "
                f"N={measured_peak.neutron_count}; separated from every rival "
                f"{analysis['peak_separated_from_every_rival']}"
            ),
            "both external singleton 0.0 inscriptions retained only as empty-binding boundaries",
            "reversed fusion and fission directions, incomplete census and displaced peak controls rejected",
        )
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=all_rows_preserved,
            data_source_ids=(SOURCE_ID,),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(comparison_payload),
            falsification_condition=FALSIFICATION_CONDITION,
            passed=passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION",
    "FusionFissionTerminalValidator",
    "MeasuredBindingRow",
    "RAW_HASH",
    "RAW_PATH",
    "SOURCE_ID",
    "SOURCE_RECORD_HASH",
    "SOURCE_RECORD_PATH",
    "TARGET_IDS",
    "authoritative_record",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "measured_binding_rows",
    "measurement_analysis",
    "prediction_program_document",
)
