"""Post-seal complete NIST real-gas equilibrium validation for THERMO-010."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.real_gas_exchange_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    RAW_HASH,
    RAW_PATH,
    REAL_GAS_EXCHANGE_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldTable,
    FoldWord,
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


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-010 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "ordered_component_orgnums",
        "complete_component_records",
        "pressure_kPa_external_inscription",
        "gas_component_mole_fraction_external_inscription",
        "condition_and_liquid_composition_coordinates",
        "pressure_uncertainty",
        "gas_composition_uncertainty",
        "target_payload",
        "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 94
        or document.get(
            "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_absent"
        )
        is not True
        or len(rows) != 94
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-010 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"real-gas-equilibrium-row-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        for number, (key, family) in enumerate(
            (
                ("doi", "source-doi"),
                ("source_id", "complete-source-identity"),
                ("pressure_dataset_ordinal", "pressure-dataset-ordinal"),
                ("pressure_point_ordinal", "positive-source-point-ordinal"),
                ("composition_companion_class", "composition-companion-class"),
            ),
            start=1,
        ):
            destination = f"{prefix}-identity-{number}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]}
            )
            registers.append(destination)
        for family, label in (
            ("fugacity-equivalent-law", "exact-accessible-over-reference-support-relation"),
            ("interaction-law", "exact-joint-versus-independent-support-relation"),
            ("equilibrium-law", "exact-component-exchange-support-balance"),
            ("record-law", "complete-pressure-temperature-composition-state-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": [family, label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-real-gas-equilibrium-vector", "arguments": table},
            {"opcode": "emit", "destination": "", "arguments": ["complete-real-gas-equilibrium-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": REAL_GAS_EXCHANGE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": REAL_GAS_EXCHANGE_SPEC.experiment_id,
        "claim_id": REAL_GAS_EXCHANGE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": REAL_GAS_EXCHANGE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "raw_source": (RAW_PATH, RAW_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in REAL_GAS_EXCHANGE_SPEC.target_rows),
        "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": REAL_GAS_EXCHANGE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 94:
        raise ValueError("THERMO-010 prediction is not the complete 94-state table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 10
        ):
            raise ValueError("THERMO-010 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 94:
        raise ValueError("THERMO-010 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (RAW_PATH, RAW_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-010 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 94
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 94
    ):
        raise ValueError("THERMO-010 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["pressure_dataset_ordinal"] != target.get("pressure_dataset_ordinal")
            or identity["pressure_point_ordinal"] != target.get("pressure_point_ordinal")
            or (identity["composition_companion_class"] == "present")
            != (target.get("composition_dataset_ordinal") is not None)
        ):
            raise ValueError("THERMO-010 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_real_gas_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    dataset_counts: Counter[str] = Counter()
    component_pairs: set[tuple[str, str]] = set()
    pressures: list[Fraction] = []
    temperatures: list[Fraction] = []
    gas_compositions: list[Fraction] = []
    matched_states = 0
    pressure_only_states = 0
    liquid_coordinate_count = 0
    for row in rows:
        target = row["target_payload"]
        if target.get("external_phase_classification") != "binary-real-gas-vapor-liquid-equilibrium":
            raise ValueError("THERMO-010 external equilibrium classification changed")
        components = tuple(target.get("ordered_component_orgnums", ()))
        if len(components) != 2 or len(target.get("complete_component_records", ())) != 2:
            raise ValueError("THERMO-010 component support is incomplete")
        component_pairs.add(components)
        pressure = Fraction(target["pressure_kPa_external_inscription"])
        if pressure.numerator <= 0:
            raise ValueError("THERMO-010 pressure is not an exact positive external inscription")
        if not target.get("pressure_uncertainty"):
            raise ValueError("THERMO-010 pressure uncertainty is absent")
        coordinates = target.get("condition_and_liquid_composition_coordinates", ())
        if len(coordinates) != 2:
            raise ValueError("THERMO-010 did not retain temperature and liquid composition")
        row_temperature = None
        row_liquid_coordinates = 0
        for coordinate in coordinates:
            value = Fraction(coordinate["external_inscription"])
            name = coordinate["coordinate_name"]
            if name == "temperature_K":
                if value.numerator <= 0 or coordinate.get("sft_interface_state") != "exact-positive-coordinate":
                    raise ValueError("THERMO-010 temperature is not exact positive")
                row_temperature = value
            elif name.startswith("liquid_mole_fraction_component_"):
                row_liquid_coordinates += 1
                liquid_coordinate_count += 1
                if value.numerator == 0:
                    if coordinate.get("sft_interface_state") != "EmptyOne":
                        raise ValueError("THERMO-010 external absence glyph became a number")
                elif value.numerator > 0 and value <= 1:
                    if coordinate.get("sft_interface_state") != "exact-positive-coordinate":
                        raise ValueError("THERMO-010 positive liquid composition was relabelled")
                else:
                    raise ValueError("THERMO-010 liquid composition is outside the One")
            else:
                raise ValueError("THERMO-010 unregistered state coordinate")
        if row_temperature is None or row_liquid_coordinates != 1:
            raise ValueError("THERMO-010 state coordinates are incomplete")
        gas_inscription = target.get("gas_component_mole_fraction_external_inscription")
        if gas_inscription is None:
            if (
                target.get("composition_dataset_ordinal") is not None
                or target.get("gas_composition_interface_state") != "unreported"
                or row.get("composition_companion_class") != "EmptyOne"
            ):
                raise ValueError("THERMO-010 pressure-only state was altered")
            pressure_only_states += 1
        else:
            gas = Fraction(gas_inscription)
            if gas.numerator <= 0 or gas > 1:
                raise ValueError("THERMO-010 gas composition is not an exact positive part of the One")
            if (
                target.get("gas_composition_interface_state") != "exact-phase-part"
                or not target.get("gas_composition_uncertainty")
                or row.get("composition_companion_class") != "present"
            ):
                raise ValueError("THERMO-010 paired gas composition record is incomplete")
            matched_states += 1
            gas_compositions.append(gas)
        dataset_counts[str(target["pressure_dataset_ordinal"])] += 1
        pressures.append(pressure)
        temperatures.append(row_temperature)
    expected_counts = {"12": 8, "14": 5, "15": 24, "17": 9, "18": 9, "19": 27, "21": 12}
    expected_pairs = {("1", "3"), ("2", "4"), ("2", "5")}
    return {
        "complete_target_count": len(rows),
        "dataset_counts": dict(dataset_counts),
        "component_pairs": tuple(sorted(component_pairs)),
        "minimum_pressure_kPa": str(min(pressures)),
        "maximum_pressure_kPa": str(max(pressures)),
        "minimum_temperature_K": str(min(temperatures)),
        "maximum_temperature_K": str(max(temperatures)),
        "distinct_temperature_count": len(set(temperatures)),
        "minimum_gas_component_mole_fraction": str(min(gas_compositions)),
        "maximum_gas_component_mole_fraction": str(max(gas_compositions)),
        "all_94_equilibrium_states_retained": len(rows) == 94,
        "all_seven_pressure_datasets_retained": dict(dataset_counts) == expected_counts,
        "all_three_binary_component_pairs_retained": component_pairs == expected_pairs,
        "all_pressures_exact_positive": len(pressures) == 94,
        "all_temperatures_exact_positive": len(temperatures) == 94,
        "all_liquid_composition_coordinates_retained": liquid_coordinate_count == 94,
        "all_59_paired_gas_compositions_retained": matched_states == 59 and len(gas_compositions) == 59,
        "all_35_pressure_only_states_retained": pressure_only_states == 35,
        "measured_pressure_vector_is_nonconstant": len(set(pressures)) > 1,
        "measured_gas_composition_vector_is_nonconstant": len(set(gas_compositions)) > 1,
        "complete_raw_source_surface_preserved": primary.get("complete_compound_count") == 5
        and primary.get("complete_source_dataset_count") == 21
        and primary.get("complete_source_point_count") == 176
        and primary.get("complete_equilibrium_state_count") == 94
        and primary.get("all_direct_equilibrium_states_and_complete_raw_source_preserved") is True,
        "no_correlated_fitted_or_imported_model_value_used": primary.get(
            "correlated_regressed_or_model_calculated_values_used_as_measurements"
        )
        is False
        and primary.get("equation_of_state_fugacity_or_compressibility_fit_imported") is False
        and primary.get("external_values_used_as_proof_parameters") is False,
    }


class RealGasExchangeValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = REAL_GAS_EXCHANGE_SPEC

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
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-010 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-real-gas-equilibrium-row-hash", row["target_payload_hash"])
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
        for row in source_rows:
            target_id = row["target_id"]
            word = predicted[target_id]
            identity_values = (
                row["doi"],
                row["source_id"],
                str(row["pressure_dataset_ordinal"]),
                str(row["pressure_point_ordinal"]),
                row["composition_companion_class"],
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            ) and tuple(cell.label for cell in word.cells[6:]) == (
                "exact-accessible-over-reference-support-relation",
                "exact-joint-versus-independent-support-relation",
                "exact-component-exchange-support-balance",
                "complete-pressure-temperature-composition-state-retained",
            )
            target_match = release.targets[target_id] == HeldLabel(
                "external-real-gas-equilibrium-row-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {
                    "target_id": target_id,
                    "identity_match": identity_match,
                    "postseal_target_hash_match": target_match,
                    "passed": identity_match and target_match,
                }
            )
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_real_gas_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["pressure_kPa_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_real_gas_analysis(tuple(tampered), primary)
        except ValueError:
            tamper_rejected = True
        controls = {
            "tampered_pressure_rejected": tamper_rejected,
            "complete_94_state_vector_retained": len(release.targets) == 94,
            "complete_21_dataset_176_point_source_retained": analysis["complete_raw_source_surface_preserved"],
            "all_59_paired_states_retained": analysis["all_59_paired_gas_compositions_retained"],
            "all_35_pressure_only_states_retained": analysis["all_35_pressure_only_states_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count",
            "dataset_counts",
            "component_pairs",
            "minimum_pressure_kPa",
            "maximum_pressure_kPa",
            "minimum_temperature_K",
            "maximum_temperature_K",
            "distinct_temperature_count",
            "minimum_gas_component_mole_fraction",
            "maximum_gas_component_mole_fraction",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("exact-real-gas-equilibrium-vector-correspondence", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-010 released target differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = tuple(
            (
                f"{row['target_id']}: pressure dataset={row['target_payload']['pressure_dataset_ordinal']}; "
                f"P={row['target_payload']['pressure_kPa_external_inscription']} kPa; "
                f"gas composition={row['target_payload']['gas_component_mole_fraction_external_inscription'] or 'unreported'}; "
                f"coordinates={len(row['target_payload']['condition_and_liquid_composition_coordinates'])}"
            )
            for row in source_rows
        ) + (
            "complete source: five compounds, 21 datasets and 176 raw points",
            "complete equilibrium vector: 94 states, 59 paired vapor compositions and 35 pressure-only states",
            f"pressure range: {analysis['minimum_pressure_kPa']} through {analysis['maximum_pressure_kPa']} kPa",
            f"temperature range: {analysis['minimum_temperature_K']} through {analysis['maximum_temperature_K']} K",
            f"reported vapor-composition range: {analysis['minimum_gas_component_mole_fraction']} through {analysis['maximum_gas_component_mole_fraction']}",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("NIST-TRC-THERMOML-FPE-2019-485-145-152",),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "RealGasExchangeValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_real_gas_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
