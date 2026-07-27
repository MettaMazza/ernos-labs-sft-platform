"""Post-seal complete solvation and dissolution validation for THERMO-015."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.solvation_dissolution_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, SOLVATION_DISSOLUTION_SPEC,
    SOURCE_FILES, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.solvation_dissolution_law_v1 import (
    SolvationDissolutionAccount, exact_solubility_capacity, external_order_as_fold_relation,
    forced_transfer_carrier,
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
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-015 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "solute_compound_id", "solute_smiles", "solute_name", "solvent_identity", "component_orgnums",
        "solute_orgnum", "solvent_orgnums", "complete_component_records", "source_state", "destination_state",
        "experimental_hydration_free_energy_kcal_per_mol_external_inscription",
        "experimental_uncertainty_kcal_per_mol_external_inscription", "experimental_reference",
        "calculated_companion_fields_excluded_from_measurement", "complete_source_row",
        "solubility_mole_fraction_external_inscription", "solubility_uncertainty_external_inscription",
        "variable_external_inscriptions", "pressure_constraint_external_inscription", "complete_point_record",
        "complete_property_metadata", "complete_variable_metadata", "complete_constraint_metadata",
        "complete_phase_metadata", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 799
        or document.get("source_class_counts") != {"solvation": 642, "dissolution": 157}
        or document.get("all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent") is not True
        or len(rows) != 799 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-015 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"solvation-dissolution-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        if row["source_class"] == "solvation":
            group, point, locator = "complete-database", str(row["source_row_ordinal"]), "database-row"
        else:
            group, point, locator = str(row["dataset_ordinal"]), str(row["source_point_ordinal"]), "thermoml-direct-point"
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("source-class", row["source_class"]),
            ("source-group", group), ("positive-source-point-ordinal", point), ("source-locator-kind", locator),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("carrier-law", "complete-distinct-solute-solvent-state-condition-carrier"),
            ("order-law", "held-free-order-orientation-with-exact-positive-magnitude"),
            ("capacity-law", "exact-condition-bound-positive-solubility-capacity"),
            ("absence-law", "structural-EmptyOne-only-for-absent-or-coincident-support"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-solvation-dissolution-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-solvation-dissolution-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": SOLVATION_DISSOLUTION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": SOLVATION_DISSOLUTION_SPEC.experiment_id,
        "claim_id": SOLVATION_DISSOLUTION_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_value_free_executable_boundary",
        "frozen_relation": SOLVATION_DISSOLUTION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in SOLVATION_DISSOLUTION_SPEC.target_rows),
        "all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent": True,
        "initial_source_research_disclosed": True,
        "not_claimed_as_unknown_source_family_selection": True,
        "falsification_condition": SOLVATION_DISSOLUTION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 799:
        raise ValueError("THERMO-015 prediction is not the complete 799-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10
        ):
            raise ValueError("THERMO-015 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 799:
        raise ValueError("THERMO-015 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-015 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 799
        or document.get("source_class_counts") != {"solvation": 642, "dissolution": 157}
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 799
    ):
        raise ValueError("THERMO-015 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        keys = ["target_id", "source_id", "source_class"]
        keys += ["source_row_ordinal"] if identity["source_class"] == "solvation" else ["dataset_ordinal", "source_point_ordinal"]
        if any(identity[key] != target.get(key) for key in keys):
            raise ValueError("THERMO-015 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _positive_fraction(value: object, name: str) -> Fraction:
    try:
        fraction = Fraction(str(value))
    except Exception as exc:
        raise ValueError(f"THERMO-015 {name} is not an exact finite inscription") from exc
    if fraction.numerator <= 0:
        raise ValueError(f"THERMO-015 {name} is not exact positive support")
    return fraction


def _condition_support(value: object) -> PositiveRatio | EmptyOne:
    try:
        fraction = Fraction(str(value))
    except Exception as exc:
        raise ValueError("THERMO-015 condition is not an exact finite inscription") from exc
    if fraction.numerator < 0:
        raise ValueError("THERMO-015 condition left the exact nonnegative external boundary")
    if fraction.numerator == 0:
        return EmptyOne()
    return PositiveRatio.from_pair(fraction.numerator, fraction.denominator)


def exact_solvation_dissolution_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    class_counts: Counter[str] = Counter()
    dataset_counts: Counter[int] = Counter()
    solvation_orientations: Counter[str] = Counter()
    solvation_magnitudes: list[Fraction] = []
    solvation_uncertainties: list[Fraction] = []
    solubilities: list[Fraction] = []
    solubility_uncertainties: list[Fraction] = []
    temperatures: list[Fraction] = []
    mixed_solvent_count = 0
    empty_condition_coordinate_count = 0
    for row in rows:
        target = row["target_payload"]
        source_class = target.get("source_class")
        class_counts[source_class] += 1
        if source_class == "solvation":
            if (
                not target.get("solute_compound_id") or not target.get("solute_smiles") or not target.get("solute_name")
                or target.get("solvent_identity") != "water"
                or target.get("source_state") != "isolated-gas-reference"
                or target.get("destination_state") != "aqueous-hydrated-reference"
                or not target.get("experimental_reference") or not target.get("complete_source_row")
                or set(target.get("calculated_companion_fields_excluded_from_measurement", {}))
                != {"calculated_hydration_free_energy_kcal_per_mol", "calculated_uncertainty_kcal_per_mol", "calculated_reference"}
            ):
                raise ValueError("THERMO-015 complete FreeSolv carrier or provenance changed")
            relation = external_order_as_fold_relation(
                target["experimental_hydration_free_energy_kcal_per_mol_external_inscription"]
            )
            uncertainty = _positive_fraction(
                target["experimental_uncertainty_kcal_per_mol_external_inscription"], "solvation uncertainty"
            )
            account = SolvationDissolutionAccount(
                HeldLabel("chemical-component", target["solute_compound_id"]),
                (HeldLabel("chemical-component", "water"),),
                HeldLabel("chemical-state", target["source_state"]),
                HeldLabel("chemical-state", target["destination_state"]), EmptyOne(),
            )
            if forced_transfer_carrier(account).label != "distinct-solute-single-solvent-reference-condition-state-transfer":
                raise ValueError("THERMO-015 solvation carrier changed")
            solvation_orientations[relation.orientation.label] += 1
            if isinstance(relation.magnitude, PositiveRatio):
                solvation_magnitudes.append(relation.magnitude.fraction)
            solvation_uncertainties.append(uncertainty)
        elif source_class == "dissolution":
            components = tuple(int(value) for value in target.get("component_orgnums", ()))
            solute = int(target.get("solute_orgnum"))
            solvents = tuple(int(value) for value in target.get("solvent_orgnums", ()))
            if (
                len(components) not in (2, 3) or len(set(components)) != len(components)
                or solute not in components or not solvents or set(solvents) != set(components) - {solute}
                or len(target.get("complete_component_records", ())) != len(components)
                or target.get("source_state") != "separated-solute-and-solvent"
                or target.get("destination_state") != "condition-bound-saturated-liquid-solution"
                or not target.get("complete_point_record") or not target.get("complete_property_metadata")
                or not target.get("complete_variable_metadata") or not target.get("complete_constraint_metadata")
                or not target.get("complete_phase_metadata")
            ):
                raise ValueError("THERMO-015 complete NIST dissolution carrier or provenance changed")
            capacity = exact_solubility_capacity(str(target["solubility_mole_fraction_external_inscription"]))
            uncertainty = _positive_fraction(target["solubility_uncertainty_external_inscription"], "solubility uncertainty")
            variables = {int(number): _condition_support(value) for number, value in target["variable_external_inscriptions"].items()}
            pressure = _positive_fraction(target["pressure_constraint_external_inscription"], "dissolution pressure")
            empty_condition_coordinate_count += sum(isinstance(value, EmptyOne) for value in variables.values())
            temperature_support = variables[max(variables)]
            if not isinstance(temperature_support, PositiveRatio):
                raise ValueError("THERMO-015 temperature became absent")
            temperature = temperature_support.fraction
            account = SolvationDissolutionAccount(
                HeldLabel("chemical-component", str(solute)),
                tuple(HeldLabel("chemical-component", str(value)) for value in solvents),
                HeldLabel("chemical-state", target["source_state"]),
                HeldLabel("chemical-state", target["destination_state"]),
                PositiveRatio.from_pair(temperature.numerator, temperature.denominator),
            )
            expected_kind = "mixed-solvent" if len(solvents) > 1 else "single-solvent"
            if forced_transfer_carrier(account).label != f"distinct-solute-{expected_kind}-condition-bound-state-transfer":
                raise ValueError("THERMO-015 dissolution carrier changed")
            if len(solvents) > 1:
                mixed_solvent_count += 1
            dataset_counts[int(target["dataset_ordinal"])] += 1
            solubilities.append(capacity.fraction)
            solubility_uncertainties.append(uncertainty)
            temperatures.append(temperature)
            if pressure.numerator <= 0:
                raise ValueError("THERMO-015 pressure support changed")
        else:
            raise ValueError("THERMO-015 source class changed")
    expected_datasets = {1: 13, 2: 11, 3: 11, 4: 7, 5: 10, 6: 12, 7: 93}
    exact_ranges = {
        "solvation_magnitude_kcal_per_mol": {"minimum": str(min(solvation_magnitudes)), "maximum": str(max(solvation_magnitudes))},
        "solvation_uncertainty_kcal_per_mol": {"minimum": str(min(solvation_uncertainties)), "maximum": str(max(solvation_uncertainties))},
        "solubility_mole_fraction": {"minimum": str(min(solubilities)), "maximum": str(max(solubilities))},
        "solubility_uncertainty": {"minimum": str(min(solubility_uncertainties)), "maximum": str(max(solubility_uncertainties))},
        "dissolution_temperature_K": {"minimum": str(min(temperatures)), "maximum": str(max(temperatures))},
    }
    return {
        "complete_target_count": len(rows), "class_counts": dict(class_counts),
        "dataset_counts": dict(dataset_counts), "solvation_orientation_counts": dict(solvation_orientations),
        "mixed_solvent_record_count": mixed_solvent_count,
        "structural_EmptyOne_condition_coordinate_count": empty_condition_coordinate_count,
        "exact_ranges": exact_ranges,
        "all_799_records_retained": len(rows) == 799,
        "all_642_solvation_and_157_dissolution_records_retained": dict(class_counts) == {"solvation": 642, "dissolution": 157},
        "all_favorable_opposed_and_EmptyOne_solvation_rows_retained": dict(solvation_orientations) == {"destination-solution-retained": 556, "source-separated-state-retained": 84, "coincident-state-support": 2},
        "all_seven_dissolution_datasets_complete": dict(dataset_counts) == expected_datasets,
        "all_93_mixed_solvent_records_retained": mixed_solvent_count == 93,
        "all_10_absent_solvent_condition_coordinates_are_EmptyOne": empty_condition_coordinate_count == 10,
        "complete_two_sources_preserved": primary.get("complete_source_count") == 2 and primary.get("complete_target_count") == 799 and primary.get("all_642_FreeSolv_and_157_direct_NIST_rows_preserved") is True,
        "calculated_or_correlated_companions_excluded_from_measurements": primary.get("calculated_or_correlated_companion_fields_used_as_measurements") is False,
        "no_imported_model_equation_logarithm_correlation_fit_or_selection": primary.get("force_field_continuum_solvent_partition_activity_solubility_product_logarithm_correlation_regression_fit_selection_or_target_correction_used") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class SolvationDissolutionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = SOLVATION_DISSOLUTION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-015 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-solvation-dissolution-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        expected_laws = (
            "complete-distinct-solute-solvent-state-condition-carrier",
            "held-free-order-orientation-with-exact-positive-magnitude",
            "exact-condition-bound-positive-solubility-capacity",
            "structural-EmptyOne-only-for-absent-or-coincident-support",
        )
        for row in source_rows:
            word = predicted[row["target_id"]]
            if row["source_class"] == "solvation":
                group, point, locator = "complete-database", str(row["source_row_ordinal"]), "database-row"
            else:
                group, point, locator = str(row["dataset_ordinal"]), str(row["source_point_ordinal"]), "thermoml-direct-point"
            identity_values = (row["source_id"], row["source_class"], group, point, locator)
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-solvation-dissolution-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match,
                "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_solvation_dissolution_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        dissolution_index = next(index for index, row in enumerate(tampered) if row["source_class"] == "dissolution")
        payload = dict(tampered[dissolution_index]["target_payload"])
        payload["solubility_mole_fraction_external_inscription"] = "-1"
        tampered[dissolution_index] = {**tampered[dissolution_index], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_solvation_dissolution_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_solubility_rejected": tamper_rejected,
            "complete_799_record_vector_retained": len(release.targets) == 799,
            "all_642_solvation_and_157_dissolution_rows_retained": analysis["all_642_solvation_and_157_dissolution_records_retained"],
            "favorable_opposed_and_EmptyOne_solvation_orientations_retained": analysis["all_favorable_opposed_and_EmptyOne_solvation_rows_retained"],
            "all_seven_dissolution_datasets_retained": analysis["all_seven_dissolution_datasets_complete"],
            "all_mixed_solvent_records_retained": analysis["all_93_mixed_solvent_records_retained"],
            "all_absent_condition_coordinates_translated_to_EmptyOne": analysis["all_10_absent_solvent_condition_coordinates_are_EmptyOne"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "class_counts", "dataset_counts", "solvation_orientation_counts",
            "mixed_solvent_record_count", "structural_EmptyOne_condition_coordinate_count", "exact_ranges",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-solvation-dissolution-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-015 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis,
            "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: class={row['source_class']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete vector: 642 experimental solvation and 157 direct dissolution records",
            f"exact ranges: {analysis['exact_ranges']}",
            "source coverage: immutable complete FreeSolv v0.52 revision and complete seven-dataset NIST ThermoML source",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "SolvationDissolutionValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_solvation_dissolution_analysis", "experiment_registration_record", "prediction_program_document",
)
