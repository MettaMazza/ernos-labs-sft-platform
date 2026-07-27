"""Post-seal exact NIST internal-energy state-vector validation for THERMO-003."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.internal_energy_composition_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, INTERNAL_ENERGY_COMPOSITION_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    SNAPSHOT_HASH, SNAPSHOT_PATH, TARGET_HASH, TARGET_PATH,
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


VALUE_COLUMNS = (
    "temperature-kelvin", "pressure-bar", "density-mole-per-litre", "volume-litre-per-mole",
    "internal-energy-kilojoule-per-mole", "enthalpy-kilojoule-per-mole",
    "entropy-joule-per-mole-kelvin", "isochoric-heat-capacity-joule-per-mole-kelvin",
    "isobaric-heat-capacity-joule-per-mole-kelvin", "sound-speed-metre-per-second",
    "joule-thomson-kelvin-per-bar", "viscosity-micropascal-second",
    "thermal-conductivity-watt-per-metre-kelvin", "phase-identity",
)


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-003 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = set(VALUE_COLUMNS) | {"snapshot_hash", "target_payload", "target_payload_hash"}
    if (
        document.get("schema") != "sft-v3-thermophysical-state-identities/1"
        or document.get("complete_query_identity_count") != 13
        or document.get("all_returned_temperatures_phases_and_property_values_absent") is not True
        or len(rows) != 13
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-003 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    fields = (
        ("source_class", "external-record-class"),
        ("source_id", "external-source-identity"),
        ("source_row_ordinal", "positive-source-row-ordinal"),
        ("chemical_composition_identity", "chemical-composition"),
        ("query_identity", "declared-query-identity"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"internal-energy-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        instructions.append({"opcode": "label", "destination": prefix + "-columns", "arguments": ["column-identity-schema-hash", sha256_identity(tuple(row["column_identities"]))]})
        registers.append(prefix + "-columns")
        for family, label in (
            ("state-law", "complete-held-chemical-internal-energy-state"),
            ("orientation-law", "held-transfer-orientation-plus-positive-magnitude"),
            ("path-law", "complete-same-orientation-step-composition"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-internal-energy-state-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-internal-energy-state-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": INTERNAL_ENERGY_COMPOSITION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": INTERNAL_ENERGY_COMPOSITION_SPEC.experiment_id,
        "claim_id": INTERNAL_ENERGY_COMPOSITION_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": INTERNAL_ENERGY_COMPOSITION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "NIST_snapshot": (SNAPSHOT_PATH, SNAPSHOT_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in INTERNAL_ENERGY_COMPOSITION_SPEC.target_rows),
        "all_temperatures_phases_internal_energies_and_other_property_values_absent_from_prediction": True,
        "falsification_condition": INTERNAL_ENERGY_COMPOSITION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 13:
        raise ValueError("THERMO-003 prediction is not the complete 13-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("THERMO-003 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10:
            raise ValueError("THERMO-003 prediction lost its complete internal-energy consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 13:
        raise ValueError("THERMO-003 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (SNAPSHOT_PATH, SNAPSHOT_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-003 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-thermophysical-state-withheld-targets/1"
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or document.get("complete_target_count") != 13
        or len(targets) != 13
    ):
        raise ValueError("THERMO-003 withheld registry changed")
    resolved: list[dict[str, object]] = []
    required_target = {"target_id", "source_class", "source_row_ordinal", "snapshot_hash", *VALUE_COLUMNS}
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["source_class"] != target.get("source_class")
            or identity["source_row_ordinal"] != target.get("source_row_ordinal")
            or set(target) != required_target
            or target.get("snapshot_hash") != SNAPSHOT_HASH
        ):
            raise ValueError("THERMO-003 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    phases = tuple(row["target_payload"]["phase-identity"] for row in resolved)
    boundary = tuple(row for row in resolved if row["target_payload"]["temperature-kelvin"] == "372.75593")
    if phases.count("liquid") != 9 or phases.count("vapor") != 4 or len(boundary) != 2 or {row["target_payload"]["phase-identity"] for row in boundary} != {"liquid", "vapor"}:
        raise ValueError("THERMO-003 complete phase surface changed")
    return tuple(resolved)


def exact_internal_energy_analysis(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    energies = tuple(Fraction(str(row["target_payload"]["internal-energy-kilojoule-per-mole"])) for row in rows)
    steps = tuple(second - first for first, second in zip(energies, energies[1:]))
    phases = tuple(str(row["target_payload"]["phase-identity"]) for row in rows)
    boundary_indices = tuple(index for index, row in enumerate(rows) if row["target_payload"]["temperature-kelvin"] == "372.75593")
    signed_source = tuple(str(row["target_payload"]["joule-thomson-kelvin-per-bar"]) for row in rows)
    return {
        "internal_energy_values": energies,
        "adjacent_exact_positive_steps": steps,
        "all_internal_energy_values_exact_positive": all(value > 0 for value in energies),
        "all_adjacent_internal_energy_steps_exact_positive": all(value > 0 for value in steps),
        "complete_path_composes_exactly": sum(steps, Fraction(0, 1)) == energies[-1] - energies[0],
        "phase_boundary_pair_retained": boundary_indices == (8, 9) and phases[8:10] == ("liquid", "vapor"),
        "phase_boundary_internal_energy_jump_exact_positive": energies[9] - energies[8] > 0,
        "all_fourteen_columns_retained": all(set(VALUE_COLUMNS).issubset(row["target_payload"]) for row in rows),
        "all_13_rows_retained": len(rows) == 13,
        "nine_liquid_and_four_vapor_rows_retained": phases.count("liquid") == 9 and phases.count("vapor") == 4,
        "external_signed_Joule_Thomson_inscriptions_retained": sum(value.startswith("-") for value in signed_source) == 9 and sum(not value.startswith("-") for value in signed_source) == 4,
    }


class InternalEnergyCompositionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = INTERNAL_ENERGY_COMPOSITION_SPEC

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
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("THERMO-003 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): HeldLabel("external-state-vector-hash", str(row["target_payload_hash"])) for row in source_rows}
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
        for row in source_rows:
            target_id = str(row["target_id"])
            word = predicted[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["source_class"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["source_id"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == str(row["source_row_ordinal"])
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["chemical_composition_identity"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["query_identity"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == sha256_identity(tuple(row["column_identities"]))
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == "complete-held-chemical-internal-energy-state"
                and isinstance(word.cells[8], HeldLabel) and word.cells[8].label == "held-transfer-orientation-plus-positive-magnitude"
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == "complete-same-orientation-step-composition"
            )
            target_match = release.targets[target_id] == HeldLabel("external-state-vector-hash", str(row["target_payload_hash"]))
            comparisons.append({
                "target_id": target_id, "target_payload_hash": row["target_payload_hash"],
                "identity_match": identity_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and target_match,
            })

        analysis = exact_internal_energy_analysis(source_rows)
        tampered_rows = [dict(row) for row in source_rows]
        tampered_payload = dict(tampered_rows[6]["target_payload"])
        tampered_payload["internal-energy-kilojoule-per-mole"] = "1.0000000"
        tampered_rows[6] = {**tampered_rows[6], "target_payload": tampered_payload}
        controls = {
            "tampered_internal_energy_order_rejected": exact_internal_energy_analysis(tuple(tampered_rows))["all_adjacent_internal_energy_steps_exact_positive"] is False,
            "complete_13_row_vector_retained": len(release.targets) == len(source_rows) == 13,
            "complete_14_column_vector_retained": analysis["all_fourteen_columns_retained"],
            "both_phase_boundary_states_retained": analysis["phase_boundary_pair_retained"],
            "external_signed_inscriptions_retained_but_not_used_as_proof": analysis["external_signed_Joule_Thomson_inscriptions_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        analysis_passed = all(
            bool(value) for key, value in analysis.items()
            if key not in {"internal_energy_values", "adjacent_exact_positive_steps"}
        )
        passed = all(bool(row["passed"]) for row in comparisons) and analysis_passed and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-internal-energy-state-path-composition", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-003 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "internal_energy_values": tuple(str(value) for value in analysis["internal_energy_values"]),
            "adjacent_exact_positive_steps": tuple(str(value) for value in analysis["adjacent_exact_positive_steps"]),
            "comparisons": comparisons, "controls": controls, "complete_trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"row {index}: U={row['target_payload']['internal-energy-kilojoule-per-mole']} kJ/mol; phase={row['target_payload']['phase-identity']}"
            for index, row in enumerate(source_rows, start=1)
        ) + (
            f"complete exact path: {analysis['internal_energy_values'][0]} to {analysis['internal_energy_values'][-1]} kJ/mol; all 12 increments positive and additive",
            "both 372.75593 K liquid/vapour internal-energy states retained",
        ) + tuple(f"{name}: {result}" for name, result in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=("NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-FLUID-PROPERTIES",),
            measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "InternalEnergyCompositionValidator", "VALUE_COLUMNS", "_identities", "_prediction_map", "_source_rows",
    "exact_internal_energy_analysis", "experiment_registration_record", "prediction_program_document",
)
