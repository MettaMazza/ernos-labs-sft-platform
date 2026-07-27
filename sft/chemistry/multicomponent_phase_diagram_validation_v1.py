"""Post-seal complete NIST binary/ternary coexistence validation for THERMO-013."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.multicomponent_phase_diagram_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, LANDING_HASH, LANDING_PATH, MULTICOMPONENT_PHASE_DIAGRAM_SPEC,
    PRIMARY_HASH, PRIMARY_PATH, RAW_HASH, RAW_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.multicomponent_phase_diagram_law_v1 import (
    ComponentExchangeSupport, ExactPhaseCompositionWord, MulticomponentCoexistencePoint,
    PhaseCompositionCoordinate, multicomponent_two_phase_degree_support,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-013 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "component_orgnums", "complete_component_records", "phase_ids",
        "temperature_K_external_inscription", "pressure_kPa_external_inscription",
        "liquid_reported_mole_fraction_external_inscription", "gas_reported_mole_fraction_external_inscription",
        "liquid_component_1_mole_fraction_external_inscription", "liquid_component_2_mole_fraction_external_inscription",
        "gas_component_1_mole_fraction_external_inscription", "gas_component_2_mole_fraction_external_inscription",
        "complete_point_record", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 116
        or document.get("binary_target_count") != 65
        or document.get("ternary_target_count") != 51
        or document.get("all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 116
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-013 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"multicomponent-phase-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        identity_values = (
            ("source-doi", row["doi"]),
            ("complete-source-identity", row["source_id"]),
            ("dataset-class", row["dataset_class"]),
            ("dataset-ordinals", ",".join(str(value) for value in row["dataset_ordinals"])),
            ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
        )
        for number, (family, label) in enumerate(identity_values, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("composition-law", "complete-exact-phase-composition-pair"),
            ("exchange-law", "componentwise-exchange-support-balance"),
            ("degree-law", "exact-phase-rule-component-count-support"),
            ("record-law", "finite-source-ordered-record-with-EmptyOne-boundary"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-multicomponent-phase-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-multicomponent-phase-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MULTICOMPONENT_PHASE_DIAGRAM_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": MULTICOMPONENT_PHASE_DIAGRAM_SPEC.experiment_id,
        "claim_id": MULTICOMPONENT_PHASE_DIAGRAM_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_value_free_identity_seal",
        "frozen_relation": MULTICOMPONENT_PHASE_DIAGRAM_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_raw_source": (RAW_PATH, RAW_HASH),
        "source_landing_record": (LANDING_PATH, LANDING_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MULTICOMPONENT_PHASE_DIAGRAM_SPEC.target_rows),
        "all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": MULTICOMPONENT_PHASE_DIAGRAM_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 116:
        raise ValueError("THERMO-013 prediction is not the complete 116-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10
        ):
            raise ValueError("THERMO-013 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 116:
        raise ValueError("THERMO-013 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (RAW_PATH, RAW_HASH), (LANDING_PATH, LANDING_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-013 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 116
    ):
        raise ValueError("THERMO-013 target count changed")
    if document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 116:
        raise ValueError("THERMO-013 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["dataset_class"] != target.get("dataset_class")
            or identity["dataset_ordinals"] != target.get("dataset_ordinals")
            or identity["source_point_ordinal"] != target.get("source_point_ordinal")
        ):
            raise ValueError("THERMO-013 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _coordinate(component: int, value: Fraction) -> PhaseCompositionCoordinate:
    if value < Fraction(0, 1) or value > Fraction(1, 1):
        raise ValueError("THERMO-013 external composition is outside the exact One boundary")
    coordinate = EmptyOne() if value.numerator == 0 else PositiveRatio.from_pair(value.numerator, value.denominator)
    return PhaseCompositionCoordinate(HeldLabel("chemical-component", str(component)), coordinate)


def _phase_word(phase: str, components: tuple[int, ...], values: tuple[Fraction, ...]) -> ExactPhaseCompositionWord:
    if len(components) != len(values):
        raise ValueError("THERMO-013 component-coordinate support is incomplete")
    return ExactPhaseCompositionWord(
        HeldLabel("chemical-phase", phase),
        tuple(_coordinate(component, value) for component, value in zip(components, values)),
    )


def exact_multicomponent_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    dataset_pair_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    temperatures: list[Fraction] = []
    pressures: list[Fraction] = []
    all_coordinates: list[Fraction] = []
    empty_one_count = 0
    equal_binary_phase_coordinate_count = 0
    binary_phase_rank_count = 0
    ternary_phase_rank_count = 0
    for row in rows:
        target = row["target_payload"]
        dataset_class = target.get("dataset_class")
        components = tuple(int(value) for value in target.get("component_orgnums", ()))
        if dataset_class not in ("binary", "ternary") or len(components) != (2 if dataset_class == "binary" else 3):
            raise ValueError("THERMO-013 component class changed")
        if len(target.get("complete_component_records", ())) != len(components) or len(target.get("phase_ids", ())) != 2:
            raise ValueError("THERMO-013 component or phase provenance is incomplete")
        phases = {value.get("ePhase") for value in target["phase_ids"]}
        if phases != {"Liquid", "Gas"}:
            raise ValueError("THERMO-013 liquid-gas phase pair changed")
        temperature = Fraction(target["temperature_K_external_inscription"])
        pressure = Fraction(target["pressure_kPa_external_inscription"])
        if temperature.numerator <= 0 or pressure.numerator <= 0:
            raise ValueError("THERMO-013 external environment is not exact positive")
        temperatures.append(temperature)
        pressures.append(pressure)
        if dataset_class == "binary":
            x_first = Fraction(target["liquid_reported_mole_fraction_external_inscription"])
            y_first = Fraction(target["gas_reported_mole_fraction_external_inscription"])
            liquid_values = (x_first, Fraction(1, 1) - x_first)
            gas_values = (y_first, Fraction(1, 1) - y_first)
            if x_first == y_first:
                equal_binary_phase_coordinate_count += 1
        else:
            x_first = Fraction(target["liquid_component_1_mole_fraction_external_inscription"])
            x_second = Fraction(target["liquid_component_2_mole_fraction_external_inscription"])
            y_first = Fraction(target["gas_component_1_mole_fraction_external_inscription"])
            y_second = Fraction(target["gas_component_2_mole_fraction_external_inscription"])
            liquid_values = (x_first, x_second, Fraction(1, 1) - x_first - x_second)
            gas_values = (y_first, y_second, Fraction(1, 1) - y_first - y_second)
        liquid = _phase_word("liquid", components, liquid_values)
        gas = _phase_word("gas", components, gas_values)
        exchange = tuple(ComponentExchangeSupport(
            coordinate.component_identity, PositiveCount(ordinal), PositiveCount(ordinal)
        ) for ordinal, coordinate in enumerate(liquid.coordinates, start=1))
        point = MulticomponentCoexistencePoint(
            liquid, gas,
            PositiveRatio.from_pair(temperature.numerator, temperature.denominator),
            PositiveRatio.from_pair(pressure.numerator, pressure.denominator),
            exchange,
        )
        rank = multicomponent_two_phase_degree_support(point).value
        if rank == 2:
            binary_phase_rank_count += 1
        elif rank == 3:
            ternary_phase_rank_count += 1
        else:
            raise ValueError("THERMO-013 two-phase degree rank changed")
        coordinates = liquid_values + gas_values
        if any(value < Fraction(0, 1) or value > Fraction(1, 1) for value in coordinates):
            raise ValueError("THERMO-013 exact complement left the One boundary")
        empty_one_count += sum(isinstance(value.coordinate, EmptyOne) for value in liquid.coordinates + gas.coordinates)
        all_coordinates.extend(coordinates)
        pair_key = ",".join(str(value) for value in target["dataset_ordinals"])
        dataset_pair_counts[pair_key] += 1
        class_counts[dataset_class] += 1
        required_records = (
            target.get("complete_pressure_record"), target.get("complete_component_records"),
        )
        if not all(required_records):
            raise ValueError("THERMO-013 complete measurement provenance is absent")
    expected_pairs = {"7,8": 1, "9,10": 21, "11,12": 1, "13,14": 21, "15,16": 21, "17": 51}
    return {
        "complete_target_count": len(rows),
        "class_counts": dict(class_counts),
        "dataset_pair_counts": dict(dataset_pair_counts),
        "complete_composition_coordinate_count": len(all_coordinates),
        "structural_EmptyOne_coordinate_count": empty_one_count,
        "equal_binary_phase_coordinate_count": equal_binary_phase_coordinate_count,
        "binary_phase_rank_count": binary_phase_rank_count,
        "ternary_phase_rank_count": ternary_phase_rank_count,
        "minimum_temperature_K": str(min(temperatures)),
        "maximum_temperature_K": str(max(temperatures)),
        "minimum_pressure_kPa": str(min(pressures)),
        "maximum_pressure_kPa": str(max(pressures)),
        "minimum_composition_external_inscription": str(min(all_coordinates)),
        "maximum_composition_external_inscription": str(max(all_coordinates)),
        "all_116_records_retained": len(rows) == 116,
        "all_65_binary_and_51_ternary_records_retained": dict(class_counts) == {"binary": 65, "ternary": 51},
        "all_five_binary_pairs_and_complete_ternary_surface_retained": dict(dataset_pair_counts) == expected_pairs,
        "all_566_exact_phase_coordinates_close_to_One": len(all_coordinates) == 566,
        "all_12_absent_coordinates_are_EmptyOne": empty_one_count == 12,
        "all_binary_and_ternary_phase_rule_ranks_retained": binary_phase_rank_count == 65 and ternary_phase_rank_count == 51,
        "all_8_equal_binary_phase_coordinates_retained": equal_binary_phase_coordinate_count == 8,
        "complete_parent_source_preserved": primary.get("complete_source_compound_count") == 3
        and primary.get("complete_source_dataset_count") == 17
        and primary.get("complete_source_point_count") == 187
        and primary.get("complete_companion_pure_dataset_count") == 6
        and primary.get("all_direct_binary_and_ternary_points_and_complete_source_preserved") is True,
        "no_imported_phase_geometry_eos_interpolation_or_fit": primary.get("lever_rule_tie_line_equation_gibbs_triangle_convex_hull_eos_continuum_interpolation_regression_or_fit_used") is False
        and primary.get("external_values_used_as_proof_parameters") is False,
    }


class MulticomponentPhaseDiagramValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MULTICOMPONENT_PHASE_DIAGRAM_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-013 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-multicomponent-coexistence-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        expected_laws = (
            "complete-exact-phase-composition-pair", "componentwise-exchange-support-balance",
            "exact-phase-rule-component-count-support", "finite-source-ordered-record-with-EmptyOne-boundary",
        )
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (
                row["doi"], row["source_id"], row["dataset_class"],
                ",".join(str(value) for value in row["dataset_ordinals"]), str(row["source_point_ordinal"]),
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-multicomponent-coexistence-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_multicomponent_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        ternary_index = next(index for index, row in enumerate(tampered) if row["dataset_class"] == "ternary")
        payload = dict(tampered[ternary_index]["target_payload"])
        payload["liquid_component_2_mole_fraction_external_inscription"] = "2"
        tampered[ternary_index] = {**tampered[ternary_index], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_multicomponent_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_ternary_composition_rejected": tamper_rejected,
            "complete_116_record_vector_retained": len(release.targets) == 116,
            "all_binary_and_ternary_records_retained": analysis["all_65_binary_and_51_ternary_records_retained"],
            "all_dataset_pairs_retained": analysis["all_five_binary_pairs_and_complete_ternary_surface_retained"],
            "all_compositions_close_to_One": analysis["all_566_exact_phase_coordinates_close_to_One"],
            "all_absence_boundaries_are_EmptyOne": analysis["all_12_absent_coordinates_are_EmptyOne"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "class_counts", "dataset_pair_counts", "complete_composition_coordinate_count",
            "structural_EmptyOne_coordinate_count", "equal_binary_phase_coordinate_count", "binary_phase_rank_count",
            "ternary_phase_rank_count", "minimum_temperature_K", "maximum_temperature_K", "minimum_pressure_kPa",
            "maximum_pressure_kPa", "minimum_composition_external_inscription", "maximum_composition_external_inscription",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-finite-multicomponent-coexistence-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-013 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "analysis": analysis, "comparisons": comparisons, "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: class={row['dataset_class']}; datasets={','.join(str(value) for value in row['dataset_ordinals'])}; source-point={row['source_point_ordinal']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete vector: 65 binary and 51 ternary coexistence records",
            "complete phase support: 566 exact component coordinates with 12 EmptyOne boundaries",
            "source coverage: five binary dataset pairs, one complete ternary dataset, six companion pure datasets",
            f"temperature range: {analysis['minimum_temperature_K']} through {analysis['maximum_temperature_K']} K",
            f"pressure range: {analysis['minimum_pressure_kPa']} through {analysis['maximum_pressure_kPa']} kPa",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("NIST-TRC-THERMOML-JCT-2012-47-260-266",),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "MulticomponentPhaseDiagramValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_multicomponent_analysis", "experiment_registration_record", "prediction_program_document",
)
