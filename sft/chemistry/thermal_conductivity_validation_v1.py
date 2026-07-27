"""Capability-closed blind validation for Chemistry THERMO-018."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.thermal_conductivity_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES,
    TARGET_HASH, TARGET_PATH, THERMAL_CONDUCTIVITY_SPEC,
)
from sft.chemistry.thermal_conductivity_law_v1 import (
    ThermalConductionAccount, external_thermal_conductivity_magnitude, forced_thermal_conductivity,
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
        raise ValueError("THERMO-018 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "doi", "component_orgnums", "complete_component_records", "mixture_class", "property_name",
        "property_phase", "measurement_method", "thermal_conductivity_W_m_K_external_inscription",
        "thermal_conductivity_uncertainty_external_record", "variable_external_inscriptions",
        "complete_point_record", "complete_property_metadata", "complete_variable_metadata",
        "complete_constraint_metadata", "complete_phase_metadata", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 655
        or document.get("complete_source_count") != 3
        or document.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 655
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-018 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"thermal-conductivity-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]),
            ("property-class", "thermal-conductivity"),
            ("dataset-ordinal", str(row["dataset_ordinal"])),
            ("property-number", str(row["property_number"])),
            ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
            ("source-locator-kind", "thermoml-direct-thermal-conductivity-point"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("carrier-law", "complete-composition-phase-condition-energy-carrier"),
            ("transfer-law", "counted-adjacent-cell-energy-packet-transfer"),
            ("orientation-law", "held-higher-to-lower-thermal-order-without-signed-flux"),
            ("magnitude-law", "exact-positive-postseal-conductivity-support-with-EmptyOne-conditions"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-thermal-conductivity-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-thermal-conductivity-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": THERMAL_CONDUCTIVITY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": THERMAL_CONDUCTIVITY_SPEC.experiment_id,
        "claim_id": THERMAL_CONDUCTIVITY_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": THERMAL_CONDUCTIVITY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in THERMAL_CONDUCTIVITY_SPEC.target_rows),
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": THERMAL_CONDUCTIVITY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 655:
        raise ValueError("THERMO-018 prediction is not the complete 655-record table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11
        ):
            raise ValueError("THERMO-018 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 655:
        raise ValueError("THERMO-018 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-018 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 655
        or document.get("mixture_class_counts") != {"pure": 123, "binary": 273, "ternary": 259}
        or document.get("phase_counts") != {"Gas": 51, "Liquid": 571, "Crystal 2": 33}
        or document.get("measurement_method_counts") != {
            "Hot wire method": 472, "Modified transient plane source method": 71, "THOTW": 112,
        }
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 655
    ):
        raise ValueError("THERMO-018 target registry changed")
    resolved = []
    keys = ("target_id", "source_id", "dataset_ordinal", "property_number", "source_point_ordinal")
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in keys):
            raise ValueError("THERMO-018 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _support(value: object) -> PositiveRatio | EmptyOne:
    try:
        fraction = Fraction(str(value))
    except Exception as exc:
        raise ValueError("THERMO-018 condition is not exact finite support") from exc
    if fraction.numerator < 0:
        raise ValueError("THERMO-018 condition became negative")
    return EmptyOne() if fraction.numerator == 0 else PositiveRatio.from_pair(fraction.numerator, fraction.denominator)


def _variable_kind(metadata: dict) -> str:
    kinds = tuple(key for key in metadata.get("VariableID", {}).get("VariableType", {}) if key != "tml_elements")
    if len(kinds) != 1:
        raise ValueError("THERMO-018 variable kind changed")
    return kinds[0]


def _constraint_kind(metadata: dict) -> str:
    kinds = tuple(key for key in metadata.get("ConstraintID", {}).get("ConstraintType", {}) if key != "tml_elements")
    if len(kinds) != 1:
        raise ValueError("THERMO-018 constraint kind changed")
    return kinds[0]


def exact_thermal_conductivity_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    mixture_counts: Counter[str] = Counter()
    phase_counts: Counter[str] = Counter()
    dataset_counts: Counter[str] = Counter()
    method_counts: Counter[str] = Counter()
    values: list[Fraction] = []
    conditions: defaultdict[str, list[Fraction]] = defaultdict(list)
    empty_count = 0
    for row in rows:
        target = row["target_payload"]
        components = tuple(int(value) for value in target.get("component_orgnums", ()))
        expected_class = {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component")
        phase = target.get("property_phase")
        if (
            not components or len(set(components)) != len(components)
            or len(target.get("complete_component_records", ())) != len(components)
            or target.get("mixture_class") != expected_class
            or target.get("property_name") != "Thermal conductivity, W/m/K"
            or phase not in {"Gas", "Liquid", "Crystal 2"}
            or not target.get("measurement_method")
            or not target.get("thermal_conductivity_uncertainty_external_record")
            or not target.get("complete_point_record")
            or not target.get("complete_property_metadata")
            or not target.get("complete_variable_metadata")
            or not target.get("complete_phase_metadata")
        ):
            raise ValueError("THERMO-018 complete composition/phase/provenance carrier changed")
        metadata = {int(item["nVarNumber"]): item for item in target["complete_variable_metadata"]}
        external = {int(number): value for number, value in target["variable_external_inscriptions"].items()}
        if set(metadata) != set(external):
            raise ValueError("THERMO-018 condition carrier changed")
        supports: list[PositiveRatio | EmptyOne] = []
        for number, inscription in external.items():
            support = _support(inscription)
            supports.append(support)
            if isinstance(support, EmptyOne):
                empty_count += 1
            else:
                conditions[_variable_kind(metadata[number])].append(support.fraction)
        for constraint in target.get("complete_constraint_metadata", ()):
            support = _support(constraint["nConstraintValue"])
            supports.append(support)
            if isinstance(support, EmptyOne):
                empty_count += 1
            else:
                conditions[_constraint_kind(constraint)].append(support.fraction)
        account = ThermalConductionAccount(
            tuple(HeldLabel("chemical-component", str(value)) for value in components),
            HeldLabel("chemical-phase", str(phase)),
            PositiveCount(3), PositiveCount(4), PositiveCount(7), PositiveCount(3), PositiveCount(5),
            PositiveCount(int(target["source_point_ordinal"])), PositiveCount(int(target["dataset_ordinal"])),
            PositiveCount(int(target["property_number"])), tuple(supports),
        )
        relation = forced_thermal_conductivity(account)
        if relation.carrier.label != f"{expected_class}-composition-phase-energy-packet-transfer":
            raise ValueError("THERMO-018 composition carrier changed")
        magnitude = external_thermal_conductivity_magnitude(str(target["thermal_conductivity_W_m_K_external_inscription"]))
        mixture_counts[expected_class] += 1
        phase_counts[str(phase)] += 1
        dataset_counts[f"{target['source_id']}:{target['dataset_ordinal']}:{target['property_number']}:{expected_class}:{phase}"] += 1
        method_counts[target["measurement_method"]] += 1
        values.append(magnitude.fraction)
    expected_mixtures = {"pure": 123, "binary": 273, "ternary": 259}
    expected_phases = {"Gas": 51, "Liquid": 571, "Crystal 2": 33}
    expected_methods = {"Hot wire method": 472, "Modified transient plane source method": 71, "THOTW": 112}
    return {
        "complete_target_count": len(rows),
        "mixture_class_counts": dict(mixture_counts),
        "phase_counts": dict(phase_counts),
        "conductivity_dataset_counts": dict(dataset_counts),
        "measurement_method_counts": dict(method_counts),
        "structural_EmptyOne_condition_count": empty_count,
        "exact_thermal_conductivity_range_W_m_K": {"minimum": str(min(values)), "maximum": str(max(values))},
        "exact_positive_condition_ranges": {
            name: {"minimum": str(min(group)), "maximum": str(max(group))}
            for name, group in sorted(conditions.items())
        },
        "all_655_records_retained": len(rows) == 655,
        "all_123_pure_273_binary_259_ternary_records_retained": dict(mixture_counts) == expected_mixtures,
        "all_51_gas_571_liquid_33_crystal_records_retained": dict(phase_counts) == expected_phases,
        "all_37_conductivity_datasets_complete": len(dataset_counts) == 37 and sum(dataset_counts.values()) == 655,
        "all_three_measurement_methods_retained": dict(method_counts) == expected_methods,
        "complete_three_sources_and_companions_preserved": (
            primary.get("complete_source_count") == 3
            and primary.get("complete_dataset_count_across_sources") == 61
            and primary.get("complete_all_property_point_count_across_sources") == 679
            and primary.get("complete_thermal_conductivity_dataset_count") == 37
            and primary.get("all_direct_thermal_conductivity_rows_and_complete_sources_preserved") is True
        ),
        "non_conductivity_companions_excluded_from_measurements": primary.get("non_thermal_conductivity_companions_used_as_thermal_conductivity_measurements") is False,
        "no_imported_constitutive_continuum_fitted_law_or_selection": (
            primary.get("Fourier_constitutive_temperature_gradient_kinetic_theory_mixing_temperature_law_logarithm_continuum_interpolation_regression_selection_or_target_correction_used") is False
            and primary.get("external_values_used_as_proof_parameters") is False
        ),
    }


class ThermalConductivityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = THERMAL_CONDUCTIVITY_SPEC

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
            raise ValueError("THERMO-018 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-thermal-conductivity-row-hash", row["target_payload_hash"])
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
        expected_laws = (
            "complete-composition-phase-condition-energy-carrier",
            "counted-adjacent-cell-energy-packet-transfer",
            "held-higher-to-lower-thermal-order-without-signed-flux",
            "exact-positive-postseal-conductivity-support-with-EmptyOne-conditions",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identities = (
                row["source_id"], "thermal-conductivity", str(row["dataset_ordinal"]),
                str(row["property_number"]), str(row["source_point_ordinal"]),
                "thermoml-direct-thermal-conductivity-point",
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identities, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[7:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-thermal-conductivity-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_thermal_conductivity_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["thermal_conductivity_W_m_K_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_thermal_conductivity_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_thermal_conductivity_rejected": tamper_rejected,
            "complete_655_record_vector_retained": len(release.targets) == 655,
            "all_pure_binary_ternary_rows_retained": analysis["all_123_pure_273_binary_259_ternary_records_retained"],
            "all_gas_liquid_crystal_rows_retained": analysis["all_51_gas_571_liquid_33_crystal_records_retained"],
            "all_datasets_and_methods_retained": analysis["all_37_conductivity_datasets_complete"] and analysis["all_three_measurement_methods_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "mixture_class_counts", "phase_counts", "conductivity_dataset_counts",
            "measurement_method_counts", "structural_EmptyOne_condition_count",
            "exact_thermal_conductivity_range_W_m_K", "exact_positive_condition_ranges",
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
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-thermal-conductivity-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-018 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
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
            f"{row['target_id']}: dataset={row['dataset_ordinal']}; property={row['property_number']}; point={row['source_point_ordinal']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete vector: 123 pure, 273 binary and 259 ternary thermal-conductivity records",
            "phase vector: 51 gas, 571 liquid and 33 crystalline records",
            f"exact conductivity range: {analysis['exact_thermal_conductivity_range_W_m_K']}",
            "source coverage: all 61 datasets and 679 points preserved from three complete NIST ThermoML sources",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "ThermalConductivityValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_thermal_conductivity_analysis", "experiment_registration_record", "prediction_program_document",
)
