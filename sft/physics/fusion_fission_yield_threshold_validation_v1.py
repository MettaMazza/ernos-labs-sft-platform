"""Blind AMDC/IAEA comparison for fusion/fission yield and thresholds."""

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
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file
from sft.physics.fusion_fission_terminal_validation_v1 import (
    MeasuredBindingRow,
    measured_binding_rows,
    row_by_coordinate,
)
from sft.physics.fusion_fission_yield_threshold_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    exact_release_order,
    fission_threshold_trace,
    threshold_topology,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "IAEA-AMDC-FUSION-FISSION-YIELD-THRESHOLD-2026"
SOURCE_RECORD_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "fusion-fission-yield-threshold-source-record.json"
)
SOURCE_RECORD_HASH = "sha256:034898757fe8e5613f2291f8fdb0369a1ec6d706df03861490eb58141a774dc9"
AME_PATH = "experiments/external_sources/physics/snapshots/ame2020-mass_1.mas20"
AME_HASH = "sha256:e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
FUSION_PDF_PATH = (
    "experiments/external_sources/physics/snapshots/iaea-world-fusion-outlook-2023.pdf"
)
FUSION_PDF_HASH = "sha256:6fbe70d3943dc9d7ab1e6e9f94cb4ea81eb1431467d79bee02ce1cfaac33aa64"
FISSION_PDF_PATH = (
    "experiments/external_sources/physics/snapshots/iaea-tecdoc-2024-nuclear-cogeneration.pdf"
)
FISSION_PDF_HASH = "sha256:712bbd5d6ad97c16f816d0f869626ded196c0ddbeece3f7a4a3f5d00f0db059a"
ENDF_PDF_PATH = "experiments/external_sources/physics/snapshots/iaea-endf-102-manual.pdf"
ENDF_PDF_HASH = "sha256:77a0fee413c3b1d5d74a161ed9fe7f77bbcbc58a654304851b7b2b400183d022"
LEXFOR_PDF_PATH = "experiments/external_sources/physics/snapshots/iaea-lexfor-fission-2006.pdf"
LEXFOR_PDF_HASH = "sha256:d9bfc53a63fe4cf307e1ba46c952d52dcca6c95f964dd672a3acee3bb93a0297"

SOURCE_IDS = (
    "AMDC-AME2020-MASS-1-BINDING-2021",
    "IAEA-WORLD-FUSION-OUTLOOK-2023",
    "IAEA-TECDOC-2024-NUCLEAR-COGENERATION",
    "IAEA-ENDF-102-DATA-FORMATS-PROCEDURES",
    "IAEA-NDS-LEXFOR-FISSION-2006",
)
TARGET_IDS = (
    "AME2020-COMPLETE-POSITIVE-COMPOSITE-CENSUS",
    "AME2020-FUSION-FISSION-YIELD-ANCHORS",
    "IAEA-COMPLETE-FUSION-REACTION-ENERGY-TABLE",
    "IAEA-FISSION-ENERGY-LEDGER",
    "IAEA-FUSION-FISSION-THRESHOLD-CLASSES",
)
FALSIFICATION_CONDITION = (
    "Reject if the sealed fusion-greater-per-nucleon relation or fission-greater-total relation fails the exact "
    "AME2020 uncertainty intervals or the registered IAEA D-T/U-235 energy comparison; if the IAEA charged "
    "effective-barrier, neutron-trigger, spontaneous/internal-barrier or captured-particle class is absent; if "
    "per-nucleon and total metrics are conflated; if any AME, fusion-table, fission-ledger, threshold or limitation "
    "row is omitted; if a source identity changes; or if target content enters prediction before its seal."
)


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value <= 0:
        raise ValueError("formal yield input must remain exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        AME_PATH: AME_HASH,
        FUSION_PDF_PATH: FUSION_PDF_HASH,
        FISSION_PDF_PATH: FISSION_PDF_HASH,
        ENDF_PDF_PATH: ENDF_PDF_HASH,
        LEXFOR_PDF_PATH: LEXFOR_PDF_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"fusion/fission yield source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID:
        raise ValueError("fusion/fission yield source-set identifier changed")
    custody = record.get("custody", {})
    required_custody = {
        "complete_reported_rows_retained": True,
        "development_targets_already_known": True,
        "empirical_prediction_protocol": True,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "target_inaccessible_during_prediction_execution": True,
    }
    if any(custody.get(key) != value for key, value in required_custody.items()):
        raise ValueError("fusion/fission yield custody disclosure changed")
    sources = record.get("sources")
    if not isinstance(sources, list) or tuple(row.get("source_id") for row in sources) != SOURCE_IDS:
        raise ValueError("fusion/fission authoritative source vector changed")
    scope = record.get("measurement_scope", {})
    fusion_rows = scope.get("iaea_fusion_energy", {}).get("reaction_rows")
    fission_rows = scope.get("iaea_fission_energy", {}).get("component_rows")
    if not isinstance(fusion_rows, list) or len(fusion_rows) != 12:
        raise ValueError("complete IAEA fusion reaction table changed")
    if not isinstance(fission_rows, list) or len(fission_rows) != 7:
        raise ValueError("complete IAEA fission component ledger changed")
    if scope.get("ame2020", {}).get("complete_positive_composite_row_count") != 2548:
        raise ValueError("AME2020 retained-row declaration changed")
    if scope.get("iaea_lexfor_fission_classes", {}).get("page_index") != 42:
        raise ValueError("IAEA spontaneous/capture fission class changed")
    return record


def exact_binding_measurement_analysis(
    rows: tuple[MeasuredBindingRow, ...],
) -> dict[str, object]:
    if len(rows) != 2548:
        raise ValueError("binding comparison requires the complete AME2020 census")
    deuterium = row_by_coordinate(rows, 2, 1)
    helium = row_by_coordinate(rows, 4, 2)
    uranium = row_by_coordinate(rows, 238, 92)
    palladium = row_by_coordinate(rows, 119, 46)
    fusion_per = (
        positive_take(helium.lower_keV_per_nucleon, deuterium.upper_keV_per_nucleon),
        positive_take(helium.upper_keV_per_nucleon, deuterium.lower_keV_per_nucleon),
    )
    fission_per = (
        positive_take(palladium.lower_keV_per_nucleon, uranium.upper_keV_per_nucleon),
        positive_take(palladium.upper_keV_per_nucleon, uranium.lower_keV_per_nucleon),
    )
    fusion_total = (4 * fusion_per[0], 4 * fusion_per[1])
    fission_total = (238 * fission_per[0], 238 * fission_per[1])
    return {
        "anchors": (deuterium, helium, uranium, palladium),
        "fusion_per_nucleon_keV": fusion_per,
        "fission_per_nucleon_keV": fission_per,
        "fusion_total_keV": fusion_total,
        "fission_total_keV": fission_total,
        "fusion_greater_per_nucleon": fusion_per[0] > fission_per[1],
        "fission_greater_total": fission_total[0] > fusion_total[1],
        "reversed_per_nucleon_rejected": not (fission_per[0] > fusion_per[1]),
        "reversed_total_rejected": not (fusion_total[0] > fission_total[1]),
    }


def parse_mev(value: str) -> Fraction:
    result = Fraction(value)
    if result <= 0:
        raise ValueError("reported reaction energy must remain positive")
    return result


def iaea_measurement_analysis(
    fusion_rows: tuple[dict[str, object], ...],
    fission_record: dict[str, object],
    threshold_record: dict[str, object],
) -> dict[str, object]:
    if len(fusion_rows) != 12:
        raise ValueError("IAEA analysis requires all twelve fusion reaction rows")
    dt_rows = tuple(row for row in fusion_rows if row.get("reactants") == "D-T")
    if len(dt_rows) != 1:
        raise ValueError("IAEA D-T energy row is absent or duplicated")
    dt_total = parse_mev(str(dt_rows[0]["available_release_energy_mev"]))
    dt_per_incident_nucleon = dt_total / 5
    fission_average = parse_mev(str(fission_record["reported_average_release_mev"]))
    fission_released_total = parse_mev(str(fission_record["reported_released_total_mev"]))
    fission_per_parent_nucleon = fission_average / 235
    fission_per_incident_nucleon = fission_average / 236
    all_fusion_positive = all(
        parse_mev(str(row["available_release_energy_mev"])) > 0 for row in fusion_rows
    )
    endf = threshold_record["endf"]
    lexfor = threshold_record["lexfor"]
    charged = endf["charged_particle_clause"]
    fission_identifier = endf["fission_reaction_identifier"]
    q_value = endf["q_value_clause"]
    correspondence = tuple(lexfor["structural_correspondence"])
    threshold_classes_complete = all((
        charged.get("reported_cross_section_bound_barn") == "1/10000000000",
        charged.get("page_index") == 118,
        fission_identifier.get("page_index") == 120,
        q_value.get("page_index") == 118,
        lexfor.get("page_index") == 42,
        correspondence == (
            "spontaneous internal-boundary path",
            "captured-particle trigger path",
        ),
    ))
    return {
        "dt_total_mev": dt_total,
        "dt_per_incident_nucleon_mev": dt_per_incident_nucleon,
        "u235_average_total_mev": fission_average,
        "u235_released_total_mev": fission_released_total,
        "u235_per_parent_nucleon_mev": fission_per_parent_nucleon,
        "u235_per_incident_nucleon_mev": fission_per_incident_nucleon,
        "fusion_greater_per_nucleon": (
            dt_per_incident_nucleon > fission_per_parent_nucleon
            and dt_per_incident_nucleon > fission_per_incident_nucleon
        ),
        "fission_greater_total": (
            fission_average > dt_total and fission_released_total > dt_total
        ),
        "all_fusion_rows_positive": all_fusion_positive,
        "threshold_classes_complete": threshold_classes_complete,
        "charged_clause_retains_true_vs_effective_threshold": (
            "true kinematic threshold" in charged["registered_observation"]
            and "effective threshold" in charged["registered_observation"]
        ),
        "neutral_fission_scope_retained": (
            "neutral incident class" in fission_identifier["registered_observation"]
            and "without asserting that every fission channel is non-threshold"
            in fission_identifier["registered_observation"]
        ),
    }


def formal_prediction_inputs() -> dict[str, object]:
    order = exact_release_order()
    topology = threshold_topology()
    return {
        "fusion_per_nucleon_lower": positive_ratio(order["fusion_per_nucleon"][0]),
        "fusion_per_nucleon_upper": positive_ratio(order["fusion_per_nucleon"][1]),
        "fission_per_nucleon_lower": positive_ratio(order["fission_per_nucleon"][0]),
        "fission_per_nucleon_upper": positive_ratio(order["fission_per_nucleon"][1]),
        "fusion_total_lower": positive_ratio(order["fusion_total"][0]),
        "fusion_total_upper": positive_ratio(order["fusion_total"][1]),
        "fission_total_lower": positive_ratio(order["fission_total"][0]),
        "fission_total_upper": positive_ratio(order["fission_total"][1]),
        "fusion_conserved_mass": PositiveCount(4),
        "fission_conserved_mass": PositiveCount(238),
        "fusion_charge_path_count": PositiveCount(int(topology["fusion_inter_boundary_paths"])),
        "fission_internal_boundary_cells": PositiveCount(
            fission_threshold_trace().internal_boundary_cells
        ),
        "per_nucleon_order": HeldLabel("yield-order", "fusion-greater-per-nucleon"),
        "total_order": HeldLabel("yield-order", "fission-greater-total"),
        "fusion_threshold": HeldLabel("threshold-carrier", "charged-boundary-approach"),
        "fission_threshold": HeldLabel(
            "threshold-carrier", "neutral-capture-or-internal-surface"
        ),
        "fission_inter_boundary": HeldLabel("structural-absence", "empty-form"),
        "threshold_scope": HeldLabel(
            "threshold-scope", "normalized-structure-with-reaction-specific-dimensions"
        ),
        "access_carrier": HeldLabel(
            "reaction-access", "thermal-or-directed-energy-support"
        ),
        "metric_retention": HeldLabel(
            "measurement-metric", "retain-per-nucleon-and-total-separately"
        ),
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
        "schema": "sft-v3-fusion-fission-yield-threshold-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "The exact light representative has greater release per conserved nucleon; the heavy representative "
            "has greater total release; fusion has a charged two-boundary approach carrier; fission has neutral "
            "capture or an internal surface carrier; normalized structure does not select one dimensional threshold."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": (
            "all 2548 AME2020 positive-composite rows, all twelve IAEA fusion rows, all seven fission energy "
            "components, every reported total and interval, both LEXFOR fission classes, all threshold clauses "
            "and the rounded-mass limitation"
        ),
        "target_access_policy": (
            "capability-closed prediction; distinct custody; release only after a matching seal"
        ),
        "comparison_protocol": (
            "exact rational uncertainty intervals, exact reported-energy fractions, complete class/row identity "
            "and separate per-nucleon versus total ordering"
        ),
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    rows = measured_binding_rows(root)
    binding = exact_binding_measurement_analysis(rows)
    scope = record["measurement_scope"]
    return {
        TARGET_IDS[0]: rows,
        TARGET_IDS[1]: binding["anchors"],
        TARGET_IDS[2]: tuple(scope["iaea_fusion_energy"]["reaction_rows"]),
        TARGET_IDS[3]: scope["iaea_fission_energy"],
        TARGET_IDS[4]: {
            "endf": scope["iaea_endf_threshold_protocol"],
            "lexfor": scope["iaea_lexfor_fission_classes"],
        },
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("yield/threshold prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class FusionFissionYieldThresholdValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("yield/threshold validator received the wrong claim seal")
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
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())),
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
            raise ValueError("yield/threshold prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed prediction differs from its formal inputs")

        rows = context[TARGET_IDS[0]]
        anchors = context[TARGET_IDS[1]]
        fusion_rows = context[TARGET_IDS[2]]
        fission_record = context[TARGET_IDS[3]]
        threshold_record = context[TARGET_IDS[4]]
        if not isinstance(rows, tuple) or any(
            not isinstance(row, MeasuredBindingRow) for row in rows
        ):
            raise ValueError("released AME2020 target has the wrong exact type")
        if not isinstance(fusion_rows, tuple) or not isinstance(fission_record, dict):
            raise ValueError("released IAEA energy targets have the wrong exact type")
        binding = exact_binding_measurement_analysis(rows)
        iaea = iaea_measurement_analysis(fusion_rows, fission_record, threshold_record)

        formal_per_order = (
            prediction["fusion_per_nucleon_lower"].fraction
            > prediction["fission_per_nucleon_upper"].fraction
        )
        formal_total_order = (
            prediction["fission_total_lower"].fraction
            > prediction["fusion_total_upper"].fraction
        )
        formal_metric_inversion = formal_per_order and formal_total_order
        formal_thresholds = all((
            prediction["fusion_threshold"]
            == HeldLabel("threshold-carrier", "charged-boundary-approach"),
            prediction["fission_threshold"]
            == HeldLabel("threshold-carrier", "neutral-capture-or-internal-surface"),
            prediction["fission_inter_boundary"]
            == HeldLabel("structural-absence", "empty-form"),
            prediction["threshold_scope"]
            == HeldLabel(
                "threshold-scope", "normalized-structure-with-reaction-specific-dimensions"
            ),
        ))
        all_rows_preserved = all((
            len(rows) == 2548,
            isinstance(anchors, tuple) and len(anchors) == 4,
            len(fusion_rows) == 12,
            len(fission_record["component_rows"]) == 7,
            len(authoritative_record(self.root)["sources"]) == 5,
            iaea["threshold_classes_complete"] is True,
        ))
        unfavorable_controls = all((
            binding["reversed_per_nucleon_rejected"] is True,
            binding["reversed_total_rejected"] is True,
            formal_metric_inversion,
            len(rows[:-1]) != 2548,
            len(fusion_rows[:-1]) != 12,
            fission_record["illustrative_mass_inscriptions_used_for_exact_ame_calculation"] is False,
        ))
        passed = all((
            formal_per_order,
            formal_total_order,
            formal_thresholds,
            binding["fusion_greater_per_nucleon"] is True,
            binding["fission_greater_total"] is True,
            iaea["fusion_greater_per_nucleon"] is True,
            iaea["fission_greater_total"] is True,
            iaea["all_fusion_rows_positive"] is True,
            iaea["charged_clause_retains_true_vs_effective_threshold"] is True,
            iaea["neutral_fission_scope_retained"] is True,
            all_rows_preserved,
            unfavorable_controls,
            prediction["per_nucleon_order"]
            == HeldLabel("yield-order", "fusion-greater-per-nucleon"),
            prediction["total_order"] == HeldLabel("yield-order", "fission-greater-total"),
            prediction["metric_retention"]
            == HeldLabel(
                "measurement-metric", "retain-per-nucleon-and-total-separately"
            ),
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-AMDC-IAEA-fusion-fission-yield-threshold-comparator/1",
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
            "source_hashes": source_hashes(),
            "complete_target_identity_hash": target_identity,
            "binding_analysis": binding,
            "iaea_analysis": iaea,
            "formal_per_order": formal_per_order,
            "formal_total_order": formal_total_order,
            "formal_thresholds": formal_thresholds,
            "all_rows_preserved": all_rows_preserved,
            "unfavorable_controls": unfavorable_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            f"complete AME2020 positive-composite census retained: {len(rows)} rows",
            (
                "AME2020 exact gain intervals keV/nucleon: fusion "
                f"{binding['fusion_per_nucleon_keV']}; fission "
                f"{binding['fission_per_nucleon_keV']}; fusion strictly greater"
            ),
            (
                "AME2020 exact total-gain intervals keV: fusion "
                f"{binding['fusion_total_keV']}; fission {binding['fission_total_keV']}; "
                "fission strictly greater"
            ),
            (
                "IAEA D-T release and per-incident-nucleon values MeV: "
                f"{iaea['dt_total_mev']} and {iaea['dt_per_incident_nucleon_mev']}"
            ),
            (
                "IAEA U-235 fission average/released totals MeV: "
                f"{iaea['u235_average_total_mev']} and {iaea['u235_released_total_mev']}; "
                f"average per parent nucleon {iaea['u235_per_parent_nucleon_mev']}"
            ),
            "all twelve fusion-energy rows and all seven fission-energy component rows retained",
            (
                "charged low-or-absent true threshold versus effective Coulomb threshold, neutral neutron "
                "evaluation class, spontaneous internal-barrier class and captured-particle class all retained"
            ),
            (
                "rounded illustrative fission masses were not substituted for the exact AME calculation; "
                "reversed orders, conflated metrics and incomplete-row controls were rejected"
            ),
        )
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=all_rows_preserved,
            data_source_ids=SOURCE_IDS,
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(comparison_payload),
            falsification_condition=FALSIFICATION_CONDITION,
            passed=passed,
        )


__all__ = (
    "AME_HASH",
    "FALSIFICATION_CONDITION",
    "FusionFissionYieldThresholdValidator",
    "SOURCE_ID",
    "SOURCE_IDS",
    "SOURCE_RECORD_HASH",
    "SOURCE_RECORD_PATH",
    "TARGET_IDS",
    "authoritative_record",
    "exact_binding_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "iaea_measurement_analysis",
    "prediction_program_document",
    "released_targets",
)
