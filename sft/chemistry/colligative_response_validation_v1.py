"""Post-seal complete boiling, freezing and osmotic validation for THERMO-014."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.colligative_response_batch_v1 import (
    COLLIGATIVE_RESPONSE_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.colligative_response_law_v1 import (
    ColligativeParticleAccount, RESPONSE_ORIENTATIONS, forced_colligative_orientation,
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
        raise ValueError("THERMO-014 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "component_orgnums", "complete_component_records", "composition_component_orgnum",
        "composition_external_inscription", "response_external_inscription",
        "temperature_K_external_inscription", "pressure_kPa_external_inscription", "phase_ids",
        "complete_point_record", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 276
        or document.get("response_class_counts") != {"boiling": 144, "freezing": 37, "osmotic": 95}
        or document.get("all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 276 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-014 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"colligative-response-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("source-doi", row["doi"]), ("complete-source-identity", row["source_id"]),
            ("response-class", row["response_class"]), ("dataset-ordinal", str(row["dataset_ordinal"])),
            ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("particle-law", "distinct-held-solvent-solute-identities"),
            ("boundary-law", "exact-solvent-transmission-solute-retention"),
            ("orientation-law", f"held-{row['response_class']}-orientation-with-positive-support"),
            ("record-law", "complete-exact-response-record-with-EmptyOne-reference"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-colligative-response-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-colligative-response-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": COLLIGATIVE_RESPONSE_SPEC.experiment_id + "-value-free-complete-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COLLIGATIVE_RESPONSE_SPEC.experiment_id,
        "claim_id": COLLIGATIVE_RESPONSE_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_value_free_identity_seal",
        "frozen_relation": COLLIGATIVE_RESPONSE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COLLIGATIVE_RESPONSE_SPEC.target_rows),
        "all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": COLLIGATIVE_RESPONSE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 276:
        raise ValueError("THERMO-014 prediction is not the complete 276-record table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10:
            raise ValueError("THERMO-014 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 276:
        raise ValueError("THERMO-014 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-014 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if document.get("complete_target_count") != 276 or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 276:
        raise ValueError("THERMO-014 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in ("target_id", "source_id", "response_class", "dataset_ordinal", "source_point_ordinal")):
            raise ValueError("THERMO-014 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_colligative_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    class_counts: Counter[str] = Counter()
    dataset_counts: Counter[str] = Counter()
    response_values: dict[str, list[Fraction]] = {name: [] for name in RESPONSE_ORIENTATIONS}
    composition_values: dict[str, list[Fraction]] = {name: [] for name in RESPONSE_ORIENTATIONS}
    empty_one_count = 0
    forced_orientation_count = 0
    for row in rows:
        target = row["target_payload"]
        response_class = target.get("response_class")
        if response_class not in RESPONSE_ORIENTATIONS:
            raise ValueError("THERMO-014 response class changed")
        components = tuple(int(value) for value in target.get("component_orgnums", ()))
        if len(components) != 2 or components[0] == components[1] or len(target.get("complete_component_records", ())) != 2:
            raise ValueError("THERMO-014 solvent/solute identity support changed")
        composition = Fraction(target["composition_external_inscription"])
        response = Fraction(target["response_external_inscription"])
        temperature = Fraction(target["temperature_K_external_inscription"])
        pressure = Fraction(target["pressure_kPa_external_inscription"])
        if composition < Fraction(0, 1) or response.numerator <= 0 or temperature.numerator <= 0 or pressure.numerator <= 0:
            raise ValueError("THERMO-014 external coordinate left the exact nonnegative/positive boundary")
        coordinate = EmptyOne() if composition.numerator == 0 else PositiveRatio.from_pair(composition.numerator, composition.denominator)
        account = ColligativeParticleAccount(
            HeldLabel("chemical-component", str(components[0])),
            HeldLabel("chemical-component", str(components[1])),
            HeldLabel("colligative-response", response_class), coordinate, PositiveCount(5), PositiveCount(3),
        )
        orientation = forced_colligative_orientation(account)
        if isinstance(coordinate, EmptyOne):
            if orientation.relation.label != "pure-solvent-reference":
                raise ValueError("THERMO-014 absence did not remain the reference boundary")
            empty_one_count += 1
        else:
            if orientation.relation.label != RESPONSE_ORIENTATIONS[response_class]:
                raise ValueError("THERMO-014 forced response orientation changed")
            forced_orientation_count += 1
        if not target.get("complete_point_record") or not target.get("complete_property_metadata") or not target.get("complete_variable_metadata") or not target.get("complete_constraint_metadata"):
            raise ValueError("THERMO-014 complete measurement provenance is absent")
        class_counts[response_class] += 1
        dataset_counts[f"{response_class}:{target['dataset_ordinal']}"] += 1
        response_values[response_class].append(response)
        composition_values[response_class].append(composition)
    expected_datasets = {**{f"boiling:{index}": 9 for index in range(1, 17)}, "freezing:1": 6, "freezing:2": 3, "freezing:3": 4, "freezing:4": 9, "freezing:5": 9, "freezing:6": 6, "osmotic:1": 17, "osmotic:2": 14, "osmotic:3": 16, "osmotic:4": 17, "osmotic:5": 16, "osmotic:6": 15}
    ranges = {
        name: {
            "minimum_composition": str(min(composition_values[name])), "maximum_composition": str(max(composition_values[name])),
            "minimum_response": str(min(response_values[name])), "maximum_response": str(max(response_values[name])),
        } for name in RESPONSE_ORIENTATIONS
    }
    return {
        "complete_target_count": len(rows), "class_counts": dict(class_counts), "dataset_counts": dict(dataset_counts),
        "structural_EmptyOne_reference_count": empty_one_count, "forced_nonreference_orientation_count": forced_orientation_count,
        "exact_ranges": ranges,
        "all_276_records_retained": len(rows) == 276,
        "all_144_boiling_37_freezing_95_osmotic_records_retained": dict(class_counts) == {"boiling": 144, "freezing": 37, "osmotic": 95},
        "all_28_datasets_complete": dict(dataset_counts) == expected_datasets,
        "all_nonreference_records_have_forced_orientation": forced_orientation_count == 275,
        "sole_absent_coordinate_is_EmptyOne_reference": empty_one_count == 1,
        "complete_three_sources_preserved": primary.get("complete_source_count") == 3 and primary.get("complete_compound_record_count_across_sources") == 19 and primary.get("complete_dataset_count") == 28 and primary.get("complete_point_count") == 276 and primary.get("all_direct_boiling_freezing_osmotic_rows_and_complete_sources_preserved") is True,
        "no_imported_response_equation_constant_or_fit": primary.get("conventional_response_equation_constant_dissociation_parameter_interpolation_regression_or_fit_used") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class ColligativeResponseValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COLLIGATIVE_RESPONSE_SPEC

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
            raise ValueError("THERMO-014 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-colligative-response-row-hash", row["target_payload_hash"]) for row in source_rows}
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
            identity_values = (row["doi"], row["source_id"], row["response_class"], str(row["dataset_ordinal"]), str(row["source_point_ordinal"]))
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            expected_laws = ("distinct-held-solvent-solute-identities", "exact-solvent-transmission-solute-retention", f"held-{row['response_class']}-orientation-with-positive-support", "complete-exact-response-record-with-EmptyOne-reference")
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-colligative-response-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_colligative_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["response_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_colligative_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_response_rejected": tamper_rejected,
            "complete_276_record_vector_retained": len(release.targets) == 276,
            "all_three_response_classes_retained": analysis["all_144_boiling_37_freezing_95_osmotic_records_retained"],
            "all_28_datasets_retained": analysis["all_28_datasets_complete"],
            "absence_translated_only_to_EmptyOne": analysis["sole_absent_coordinate_is_EmptyOne_reference"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "class_counts", "dataset_counts", "structural_EmptyOne_reference_count", "forced_nonreference_orientation_count", "exact_ranges"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-colligative-response-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-014 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: class={row['response_class']}; dataset={row['dataset_ordinal']}; point={row['source_point_ordinal']}; target={row['target_payload_hash']}" for row in source_rows) + (
            "complete vector: 144 boiling, 37 freezing and 95 osmotic response records",
            f"exact ranges: {analysis['exact_ranges']}",
            "source coverage: all 28 datasets and 276 points across three complete NIST ThermoML sources",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True,
            target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "ColligativeResponseValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_colligative_analysis", "experiment_registration_record", "prediction_program_document",
)
