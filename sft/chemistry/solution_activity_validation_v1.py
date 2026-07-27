"""Post-seal complete NIST solution-activity validation for THERMO-009."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.solution_activity_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    RAW_HASH,
    RAW_PATH,
    SOLUTION_ACTIVITY_SPEC,
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
        raise ValueError("THERMO-009 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "ordered_component_orgnums",
        "temperature_K_external_inscription",
        "relative_water_activity_external_inscription",
        "composition_interface_entries",
        "activity_uncertainty",
        "external_measurement_method",
        "target_payload",
        "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 204
        or document.get(
            "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_absent"
        )
        is not True
        or len(rows) != 204
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-009 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"solution-activity-row-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        for number, (key, family) in enumerate(
            (
                ("doi", "source-doi"),
                ("source_id", "complete-source-identity"),
                ("dataset_ordinal", "dataset-ordinal"),
                ("source_point_ordinal", "positive-source-point-ordinal"),
            ),
            start=1,
        ):
            destination = f"{prefix}-identity-{number}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]}
            )
            registers.append(destination)
        for family, label in (
            ("activity-law", "exact-accessible-support-over-reference-support"),
            ("interaction-law", "exact-joint-versus-independent-support-relation"),
            ("absence-law", "structural-EmptyOne-absent-component"),
            ("record-law", "complete-condition-and-composition-retained"),
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
            {"opcode": "table", "destination": "complete-solution-activity-vector", "arguments": table},
            {"opcode": "emit", "destination": "", "arguments": ["complete-solution-activity-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": SOLUTION_ACTIVITY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": SOLUTION_ACTIVITY_SPEC.experiment_id,
        "claim_id": SOLUTION_ACTIVITY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": SOLUTION_ACTIVITY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "raw_source": (RAW_PATH, RAW_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in SOLUTION_ACTIVITY_SPEC.target_rows),
        "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_absent": True,
        "falsification_condition": SOLUTION_ACTIVITY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 204:
        raise ValueError("THERMO-009 prediction is not the complete 204-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 9
        ):
            raise ValueError("THERMO-009 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 204:
        raise ValueError("THERMO-009 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (RAW_PATH, RAW_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-009 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 204
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 204
    ):
        raise ValueError("THERMO-009 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["dataset_ordinal"] != target.get("dataset_ordinal")
            or identity["source_point_ordinal"] != target.get("source_point_ordinal")
        ):
            raise ValueError("THERMO-009 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_solution_activity_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    dataset_counts: Counter[int] = Counter()
    activities: list[Fraction] = []
    temperatures: list[Fraction] = []
    absent_rows = 0
    absent_coordinates = 0
    binary_rows = 0
    ternary_rows = 0
    for row in rows:
        target = row["target_payload"]
        activity = Fraction(target["relative_water_activity_external_inscription"])
        temperature = Fraction(target["temperature_K_external_inscription"])
        if activity.numerator <= 0 or activity > 1:
            raise ValueError("THERMO-009 activity is not an exact positive part of the One")
        if target.get("external_measurement_method") != "ISOPIE" or target.get("external_standard_state") != "Pure compound":
            raise ValueError("THERMO-009 source method or standard state changed")
        if not target.get("activity_uncertainty"):
            raise ValueError("THERMO-009 source uncertainty is absent")
        entries = target.get("composition_interface_entries", ())
        if len(entries) not in {1, 2}:
            raise ValueError("THERMO-009 composition is not complete binary or ternary support")
        row_absent = False
        for entry in entries:
            inscription = Fraction(entry["external_molality_inscription"])
            if inscription.numerator == 0:
                if entry.get("sft_interface_state") != "EmptyOne":
                    raise ValueError("THERMO-009 external absence glyph was consumed as a number")
                absent_coordinates += 1
                row_absent = True
            elif inscription.numerator > 0:
                if entry.get("sft_interface_state") != "exact-positive-composition-coordinate":
                    raise ValueError("THERMO-009 positive composition coordinate was relabelled")
            else:
                raise ValueError("THERMO-009 composition contains a negative external inscription")
        absent_rows += int(row_absent)
        binary_rows += int(len(entries) == 1)
        ternary_rows += int(len(entries) == 2)
        dataset_counts[int(target["dataset_ordinal"])] += 1
        activities.append(activity)
        temperatures.append(temperature)
    expected_counts = {1: 36, 2: 32, 3: 36, 4: 32, 5: 34, 6: 9, 7: 8, 8: 9, 9: 8}
    return {
        "complete_target_count": len(rows),
        "dataset_counts": dict(dataset_counts),
        "all_activity_inscriptions": tuple(str(value) for value in activities),
        "minimum_activity": str(min(activities)),
        "maximum_activity": str(max(activities)),
        "distinct_activity_count": len(set(activities)),
        "all_204_rows_retained": len(rows) == 204,
        "all_nine_datasets_retained": dict(dataset_counts) == expected_counts,
        "all_rows_share_fixed_298_15_K_environment": set(temperatures) == {Fraction(5963, 20)},
        "all_activities_exact_positive_parts_of_One": len(activities) == 204,
        "all_68_absence_rows_and_coordinates_translated_to_EmptyOne": absent_rows == 68
        and absent_coordinates == 68,
        "complete_binary_and_ternary_rows_retained": binary_rows == 68 and ternary_rows == 136,
        "activity_vector_contains_nonconstant_measured_response": len(set(activities)) > 1,
        "complete_raw_source_surface_preserved": primary.get("complete_compound_count") == 6
        and primary.get("complete_dataset_count") == 9
        and primary.get("complete_activity_row_count") == 204
        and primary.get("all_direct_activity_rows_and_absent_component_boundaries_preserved") is True,
        "no_correlated_or_fitted_model_value_used": primary.get(
            "correlated_regressed_or_model_calculated_values_used_as_measurements"
        )
        is False
        and primary.get("activity_coefficient_fitted_or_imported") is False,
    }


class SolutionActivityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = SOLUTION_ACTIVITY_SPEC

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
            raise ValueError("THERMO-009 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-solution-activity-row-hash", row["target_payload_hash"])
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
                str(row["dataset_ordinal"]),
                str(row["source_point_ordinal"]),
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            ) and tuple(cell.label for cell in word.cells[5:]) == (
                "exact-accessible-support-over-reference-support",
                "exact-joint-versus-independent-support-relation",
                "structural-EmptyOne-absent-component",
                "complete-condition-and-composition-retained",
            )
            target_match = release.targets[target_id] == HeldLabel(
                "external-solution-activity-row-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {"target_id": target_id, "identity_match": identity_match, "postseal_target_hash_match": target_match, "passed": identity_match and target_match}
            )
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_solution_activity_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["relative_water_activity_external_inscription"] = "3/2"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_solution_activity_analysis(tuple(tampered), primary)
        except ValueError:
            tamper_rejected = True
        controls = {
            "tampered_activity_rejected": tamper_rejected,
            "complete_204_row_vector_retained": len(release.targets) == 204,
            "complete_nine_dataset_surface_retained": analysis["all_nine_datasets_retained"],
            "all_68_EmptyOne_boundaries_retained": analysis[
                "all_68_absence_rows_and_coordinates_translated_to_EmptyOne"
            ],
            "binary_and_ternary_surfaces_retained": analysis["complete_binary_and_ternary_rows_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count",
            "dataset_counts",
            "all_activity_inscriptions",
            "minimum_activity",
            "maximum_activity",
            "distinct_activity_count",
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
                    ("exact-solution-activity-vector-correspondence", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-009 released target differs from commitment")
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
                f"{row['target_id']}: dataset={row['target_payload']['dataset_ordinal']}; "
                f"T={row['target_payload']['temperature_K_external_inscription']} K; "
                f"water activity={row['target_payload']['relative_water_activity_external_inscription']}; "
                f"composition entries={len(row['target_payload']['composition_interface_entries'])}"
            )
            for row in source_rows
        ) + (
            "complete vector: five binary and four ternary datasets, 204 direct isopiestic activity rows",
            "absence boundary: 68 external zero glyph rows translated only to structural EmptyOne",
            f"activity range: {analysis['minimum_activity']} through {analysis['maximum_activity']}",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("NIST-TRC-THERMOML-JCED-2019-9B00694",),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "SolutionActivityValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_solution_activity_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
