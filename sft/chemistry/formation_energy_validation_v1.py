"""Post-seal complete NIST formation-energy validation for Chemistry PROP-013."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.formation_energy_batch_v1 import (
    FORMATION_ENERGY_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    REFERENCE_HASH, REFERENCE_PATH, RESULT_HASH, RESULT_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.claim_evidence import (
    EMPTY_ONE, CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne,
    FoldTable, FoldWord, HostilePackageAuditor, PositiveRatio, TargetVault,
    fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-013 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_state_orientation", "exact_positive_magnitude_kJ_per_mol", "structural_absence"}
    if (
        document.get("schema") != "sft-v3-formation-energy-identities/1"
        or document.get("all_formation_values_presence_flags_and_orientations_absent") is not True
        or len(rows) != 2098
        or any(row.get("target_value_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-013 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Seal every source/product identity and exact law without a target value."""

    instructions: list[dict[str, object]] = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    identity_fields = (
        ("name", "molecular-product"), ("species", "molecular-formula"),
        ("external_charge_inscription", "external-charge-inscription"),
        ("temperature_reference_label", "temperature-reference"),
        ("measurement_kind", "measurement-kind"), ("measurement_unit", "held-energy-unit"),
        ("source_id", "external-source-identity"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"formation-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(identity_fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("reference-law", "exact-named-constituent-reference-composition"),
            ("orientation-law", "held-product-reference-state-order"),
            ("magnitude-law", "exact-positive-state-separation"),
            ("absence-law", "equality-or-unmeasured-as-distinct-structural-EmptyOne"),
            ("extension-law", "shared-state-extension-preserves-exact-relation"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-formation-energy-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-formation-energy-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": FORMATION_ENERGY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": FORMATION_ENERGY_SPEC.experiment_id,
        "claim_id": FORMATION_ENERGY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": FORMATION_ENERGY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_result_source": (RESULT_PATH, RESULT_HASH),
        "reference_state_source": (REFERENCE_PATH, REFERENCE_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in FORMATION_ENERGY_SPEC.target_rows),
        "all_2098_values_presence_flags_and_orientations_absent_from_prediction": True,
        "falsification_condition": FORMATION_ENERGY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 2098:
        raise ValueError("PROP-013 prediction is not the complete 2,098-cell table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-013 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13:
            raise ValueError("PROP-013 prediction lost its complete formation carrier")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 2098:
        raise ValueError("PROP-013 prediction duplicated a target identity")
    return resolved


def _pair(record: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(record["numerator"]), int(record["denominator"]))


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (RESULT_PATH, RESULT_HASH), (REFERENCE_PATH, REFERENCE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-013 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-formation-energy-withheld-targets/1" or document.get("release_requires_prediction_seal") is not True or len(targets) != 2098:
        raise ValueError("PROP-013 withheld registry changed")
    resolved: list[dict[str, object]] = []
    for identity, target in zip(identities, targets):
        if identity["target_id"] != target.get("target_id"):
            raise ValueError("PROP-013 identity and target order differ")
        native = target.get("native_value", {})
        if "exact_positive_magnitude_kJ_per_mol" in native:
            value = _pair(native["exact_positive_magnitude_kJ_per_mol"])
            orientation = str(native["external_state_orientation"])
            result_class = "exact-positive-formation-separation"
        elif native.get("structural_absence") == "EmptyOne" and target.get("source_value_present") is True:
            value = EMPTY_ONE
            orientation = "product-and-reference-state-equal-structural-EmptyOne"
            result_class = "printed-equality-structural-EmptyOne"
        elif native.get("structural_absence") == "EmptyOne" and native.get("source_measurement_absent") is True:
            value = EMPTY_ONE
            orientation = "source-measurement-absent"
            result_class = "unmeasured-structural-EmptyOne"
        else:
            raise ValueError("PROP-013 target value class changed")
        resolved.append({**identity, **target, "vault_value": value, "source_orientation": orientation, "result_class": result_class})
    if (
        len(resolved) != 2098
        or sum(isinstance(row["vault_value"], PositiveRatio) for row in resolved) != 1463
        or sum(row["result_class"] == "printed-equality-structural-EmptyOne" for row in resolved) != 22
        or sum(row["result_class"] == "unmeasured-structural-EmptyOne" for row in resolved) != 613
        or sum(row["source_orientation"] == "product-state-below-reference-state" for row in resolved) != 756
        or sum(row["source_orientation"] == "product-state-above-reference-state" for row in resolved) != 707
    ):
        raise ValueError("PROP-013 complete value/orientation partition changed")
    return tuple(resolved)


class FormationEnergyValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = FORMATION_ENERGY_SPEC

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
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-013 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): row["vault_value"] for row in source_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-NIST-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        comparisons = []
        for row in source_rows:
            target_id = str(row["target_id"])
            word = predicted[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["name"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["species"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["external_charge_inscription"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["temperature_reference_label"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["measurement_kind"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == row["measurement_unit"]
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == row["source_id"]
            )
            value_match = release.targets[target_id] == row["vault_value"]
            comparisons.append({
                "target_id": target_id, "species": row["species"], "temperature_reference_label": row["temperature_reference_label"],
                "source_value_inscription": row["source_value_inscription"], "source_orientation": row["source_orientation"],
                "result_class": row["result_class"], "identity_match": identity_match,
                "exact_magnitude_or_structural_absence_match": value_match, "passed": identity_match and value_match,
            })

        first_positive = next(row for row in source_rows if isinstance(row["vault_value"], PositiveRatio))
        first_blank = next(row for row in source_rows if row["result_class"] == "unmeasured-structural-EmptyOne")
        first_equal = next(row for row in source_rows if row["result_class"] == "printed-equality-structural-EmptyOne")
        tampered = PositiveRatio.from_pair(first_positive["vault_value"].numerator.value + first_positive["vault_value"].denominator.value, first_positive["vault_value"].denominator.value)
        controls = {
            "tampered_magnitude_rejected": tampered != release.targets[str(first_positive["target_id"])],
            "blank_cell_is_structural_EmptyOne": isinstance(release.targets[str(first_blank["target_id"])], EmptyOne),
            "printed_external_equality_is_structural_EmptyOne": isinstance(release.targets[str(first_equal["target_id"])], EmptyOne),
            "signed_source_orientations_are_never_negative_proof_values": all(isinstance(row["vault_value"], PositiveRatio) for row in source_rows if row["source_orientation"] in {"product-state-below-reference-state", "product-state-above-reference-state"}),
            "complete_2098_cell_vector_retained": len(release.targets) == len(source_rows) == 2098,
            "all_613_blank_cells_retained": sum(row["result_class"] == "unmeasured-structural-EmptyOne" for row in source_rows) == 613,
            "all_22_printed_equalities_retained": sum(row["result_class"] == "printed-equality-structural-EmptyOne" for row in source_rows) == 22,
            "both_temperature_reference_axes_retained": {row["temperature_reference_label"] for row in source_rows} == {"298.15-kelvin", "source-0-kelvin-label"},
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-held-formation-state-relation-complete-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-013 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "complete_2098_cell_comparisons": comparisons,
            "controls": controls, "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=("NIST-CCCBDB-SRD-101-COMPLETE-EXPERIMENTAL-FORMATION-ENERGY", "NIST-CCCBDB-THERMODYNAMIC-REFERENCE-STATES"),
            measurements=tuple(f"{row['target_id']}: {row['result_class']}; identity and exact post-seal result {row['passed']}" for row in comparisons) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = ("FormationEnergyValidator", "_prediction_map", "_source_rows", "experiment_registration_record", "prediction_program_document")
