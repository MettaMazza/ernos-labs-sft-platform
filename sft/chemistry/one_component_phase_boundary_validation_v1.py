"""Post-seal complete NIST one-component coexistence validation for THERMO-012."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.one_component_phase_boundary_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, ONE_COMPONENT_PHASE_BOUNDARY_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    RAW_HASH, RAW_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-012 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "component_orgnum", "complete_component_record", "temperature_K_external_inscription",
        "pressure_kPa_external_inscription", "phase_boundary_class", "pressure_uncertainty",
        "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 15
        or document.get("all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 15
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-012 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"one-component-boundary-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (key, family) in enumerate((
            ("doi", "source-doi"), ("source_id", "complete-source-identity"),
            ("dataset_ordinal", "dataset-ordinal"), ("source_point_ordinal", "positive-source-point-ordinal"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        succession = "least-coexistence-point" if int(row["source_point_ordinal"]) == 1 else "exact-ordered-coexistence-successor"
        for family, label in (
            ("exchange-law", "exact-component-exchange-support-balance"),
            ("degree-law", "one-independent-held-coordinate-support"),
            ("boundary-law", succession),
            ("record-law", "complete-held-temperature-pressure-point"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-one-component-boundary-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-one-component-boundary-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ONE_COMPONENT_PHASE_BOUNDARY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": ONE_COMPONENT_PHASE_BOUNDARY_SPEC.experiment_id,
        "claim_id": ONE_COMPONENT_PHASE_BOUNDARY_SPEC.claim_id,
        "provenance": "observational_derivation_reusing_prior_byte_sealed_authority",
        "frozen_relation": ONE_COMPONENT_PHASE_BOUNDARY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "parent_raw_source": (RAW_PATH, RAW_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in ONE_COMPONENT_PHASE_BOUNDARY_SPEC.target_rows),
        "all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": ONE_COMPONENT_PHASE_BOUNDARY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 15:
        raise ValueError("THERMO-012 prediction is not the complete fifteen-point table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 9
        ):
            raise ValueError("THERMO-012 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 15:
        raise ValueError("THERMO-012 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (RAW_PATH, RAW_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-012 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if document.get("complete_target_count") != 15 or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 15:
        raise ValueError("THERMO-012 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["dataset_ordinal"] != target.get("dataset_ordinal")
            or identity["source_point_ordinal"] != target.get("source_point_ordinal")
        ):
            raise ValueError("THERMO-012 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_phase_boundary_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    dataset_counts: Counter[str] = Counter()
    component_counts: Counter[str] = Counter()
    by_dataset: defaultdict[str, list[tuple[int, Fraction, Fraction]]] = defaultdict(list)
    temperatures = []
    pressures = []
    for row in rows:
        target = row["target_payload"]
        if target.get("phase_boundary_class") != "one-component-liquid-vapor-coexistence":
            raise ValueError("THERMO-012 phase-boundary class changed")
        temperature = Fraction(target["temperature_K_external_inscription"])
        pressure = Fraction(target["pressure_kPa_external_inscription"])
        if temperature.numerator <= 0 or pressure.numerator <= 0:
            raise ValueError("THERMO-012 external coexistence coordinate is not exact positive")
        if not target.get("pressure_uncertainty") or not target.get("complete_component_record"):
            raise ValueError("THERMO-012 uncertainty or component record is absent")
        property_metadata = target.get("complete_property_metadata", ())
        variable_metadata = target.get("complete_variable_metadata", ())
        if len(property_metadata) != 1 or len(variable_metadata) != 1:
            raise ValueError("THERMO-012 complete property or variable metadata is absent")
        property_group = property_metadata[0]["Property-MethodID"]["PropertyGroup"].get("VaporPBoilingTAzeotropTandP", {})
        if (
            property_group.get("ePropName") != "Vapor or sublimation pressure, kPa"
            or property_group.get("sMethodName") != "Closed cell (Static) method"
            or variable_metadata[0]["VariableID"]["VariableType"].get("eTemperature") != "Temperature, K"
        ):
            raise ValueError("THERMO-012 direct measurement method or coordinate changed")
        dataset = str(target["dataset_ordinal"])
        point = int(target["source_point_ordinal"])
        component = str(target["component_orgnum"])
        dataset_counts[dataset] += 1
        component_counts[component] += 1
        by_dataset[dataset].append((point, temperature, pressure))
        temperatures.append(temperature)
        pressures.append(pressure)
    ordered_edge_count = 0
    for dataset, points in by_dataset.items():
        points.sort()
        if [row[0] for row in points] != [1, 2, 3, 4, 5]:
            raise ValueError(f"THERMO-012 dataset {dataset} lost source succession")
        for prior, successor in zip(points, points[1:]):
            if successor[1] <= prior[1] or successor[2] <= prior[2]:
                raise ValueError("THERMO-012 coexistence succession lost temperature-pressure co-order")
            ordered_edge_count += 1
    expected_datasets = {"5": 5, "8": 5, "11": 5}
    return {
        "complete_target_count": len(rows),
        "dataset_counts": dict(dataset_counts),
        "component_counts": dict(component_counts),
        "ordered_successor_edge_count": ordered_edge_count,
        "minimum_temperature_K": str(min(temperatures)),
        "maximum_temperature_K": str(max(temperatures)),
        "minimum_pressure_kPa": str(min(pressures)),
        "maximum_pressure_kPa": str(max(pressures)),
        "all_15_points_retained": len(rows) == 15,
        "all_three_complete_datasets_retained": dict(dataset_counts) == expected_datasets,
        "both_compounds_and_parallel_component_four_datasets_retained": dict(component_counts) == {"4": 10, "5": 5},
        "all_12_adjacent_successions_exactly_coordered": ordered_edge_count == 12,
        "all_coordinates_exact_positive": len(temperatures) == 15 and len(pressures) == 15,
        "complete_parent_source_preserved": primary.get("complete_parent_compound_count") == 5
        and primary.get("complete_parent_dataset_count") == 21
        and primary.get("complete_parent_point_count") == 176
        and primary.get("all_direct_one_component_points_and_complete_parent_source_preserved") is True,
        "no_imported_curve_equation_interpolation_or_fit": primary.get("clausius_clapeyron_eos_interpolation_regression_or_model_value_used") is False
        and primary.get("external_values_used_as_proof_parameters") is False,
    }


class OneComponentPhaseBoundaryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ONE_COMPONENT_PHASE_BOUNDARY_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-012 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-one-component-coexistence-row-hash", row["target_payload_hash"]) for row in source_rows}
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
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (row["doi"], row["source_id"], str(row["dataset_ordinal"]), str(row["source_point_ordinal"]))
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            expected_succession = "least-coexistence-point" if int(row["source_point_ordinal"]) == 1 else "exact-ordered-coexistence-successor"
            law_match = tuple(cell.label for cell in word.cells[5:]) == (
                "exact-component-exchange-support-balance", "one-independent-held-coordinate-support",
                expected_succession, "complete-held-temperature-pressure-point",
            )
            target_match = release.targets[row["target_id"]] == HeldLabel("external-one-component-coexistence-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_phase_boundary_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["pressure_kPa_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_phase_boundary_analysis(tuple(tampered), primary)
        except ValueError:
            tamper_rejected = True
        controls = {
            "tampered_pressure_rejected": tamper_rejected,
            "complete_15_point_vector_retained": len(release.targets) == 15,
            "all_three_datasets_retained": analysis["all_three_complete_datasets_retained"],
            "both_compounds_and_parallel_dataset_retained": analysis["both_compounds_and_parallel_component_four_datasets_retained"],
            "all_12_successions_coordered": analysis["all_12_adjacent_successions_exactly_coordered"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "dataset_counts", "component_counts", "ordered_successor_edge_count", "minimum_temperature_K", "maximum_temperature_K", "minimum_pressure_kPa", "maximum_pressure_kPa"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-finite-one-component-coexistence-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-012 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(
            f"{row['target_id']}: dataset={row['target_payload']['dataset_ordinal']}; T={row['target_payload']['temperature_K_external_inscription']} K; P={row['target_payload']['pressure_kPa_external_inscription']} kPa"
            for row in source_rows
        ) + (
            "complete vector: three direct one-component datasets and fifteen coexistence points",
            "ordered boundary: all twelve adjacent source successions increase in exact temperature and pressure",
            f"temperature range: {analysis['minimum_temperature_K']} through {analysis['maximum_temperature_K']} K",
            f"pressure range: {analysis['minimum_pressure_kPa']} through {analysis['maximum_pressure_kPa']} kPa",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True,
            target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=("NIST-TRC-THERMOML-FPE-2019-485-145-152",), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "OneComponentPhaseBoundaryValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_phase_boundary_analysis", "experiment_registration_record", "prediction_program_document",
)
