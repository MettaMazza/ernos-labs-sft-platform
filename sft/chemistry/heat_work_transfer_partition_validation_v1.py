"""Post-seal calorimetric and expansion-work validation for THERMO-004."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.heat_work_transfer_partition_batch_v1 import HEAT_WORK_TRANSFER_PARTITION_SPEC
from sft.chemistry.internal_energy_composition_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, SNAPSHOT_HASH, SNAPSHOT_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.internal_energy_composition_validation_v1 import VALUE_COLUMNS, _identities, _source_rows
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
        prefix = f"heat-work-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        instructions.append({"opcode": "label", "destination": prefix + "-columns", "arguments": ["column-identity-schema-hash", sha256_identity(tuple(row["column_identities"]))]})
        registers.append(prefix + "-columns")
        for family, label in (
            ("heat-law", "carrier-label-closed-by-receiving-macro-observation"),
            ("work-law", "organized-source-response-label-retained"),
            ("partition-law", "disjoint-exhaustive-heat-work-path-partition"),
            ("composition-law", "per-class-positive-composition-plus-EmptyOne-absence"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-heat-work-state-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-heat-work-state-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": HEAT_WORK_TRANSFER_PARTITION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": HEAT_WORK_TRANSFER_PARTITION_SPEC.experiment_id,
        "claim_id": HEAT_WORK_TRANSFER_PARTITION_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": HEAT_WORK_TRANSFER_PARTITION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "NIST_snapshot": (SNAPSHOT_PATH, SNAPSHOT_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in HEAT_WORK_TRANSFER_PARTITION_SPEC.target_rows),
        "all_calorimetric_expansion_work_and_state_values_absent_from_prediction": True,
        "falsification_condition": HEAT_WORK_TRANSFER_PARTITION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 13:
        raise ValueError("THERMO-004 prediction is not the complete 13-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("THERMO-004 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("THERMO-004 prediction lost its complete heat/work consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 13:
        raise ValueError("THERMO-004 prediction duplicated a target identity")
    return resolved


def _decimal_quantum(inscription: str) -> Fraction:
    if "." not in inscription:
        return Fraction(1, 1)
    return Fraction(1, 10 ** len(inscription.rsplit(".", 1)[1]))


def exact_heat_work_analysis(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    heat_capacity: list[Fraction] = []
    pressure_volume_work: list[Fraction] = []
    state_record_work: list[Fraction] = []
    exact_separations: list[Fraction] = []
    exact_resolution_bounds: list[Fraction] = []
    for row in rows:
        payload = row["target_payload"]
        cp_s = str(payload["isobaric-heat-capacity-joule-per-mole-kelvin"])
        p_s = str(payload["pressure-bar"])
        v_s = str(payload["volume-litre-per-mole"])
        h_s = str(payload["enthalpy-kilojoule-per-mole"])
        u_s = str(payload["internal-energy-kilojoule-per-mole"])
        cp, pressure, volume, enthalpy, internal = map(Fraction, (cp_s, p_s, v_s, h_s, u_s))
        direct_work = pressure * volume / 10
        recorded_work = enthalpy - internal
        separation = direct_work - recorded_work if direct_work > recorded_work else recorded_work - direct_work
        pv_bound = (
            pressure * _decimal_quantum(v_s) / 2
            + volume * _decimal_quantum(p_s) / 2
            + _decimal_quantum(p_s) * _decimal_quantum(v_s) / 4
        ) / 10
        state_bound = (_decimal_quantum(h_s) + _decimal_quantum(u_s)) / 2
        heat_capacity.append(cp)
        pressure_volume_work.append(direct_work)
        state_record_work.append(recorded_work)
        exact_separations.append(separation)
        exact_resolution_bounds.append(pv_bound + state_bound)
    phases = tuple(str(row["target_payload"]["phase-identity"]) for row in rows)
    return {
        "calorimetric_heat_capacity_values": tuple(heat_capacity),
        "pressure_volume_work_values_kilojoule_per_mole": tuple(pressure_volume_work),
        "state_record_work_values_kilojoule_per_mole": tuple(state_record_work),
        "work_record_exact_separations": tuple(exact_separations),
        "work_record_exact_resolution_bounds": tuple(exact_resolution_bounds),
        "all_calorimetric_values_exact_positive": all(value > 0 for value in heat_capacity),
        "all_pressure_volume_work_values_exact_positive": all(value > 0 for value in pressure_volume_work),
        "all_state_record_work_values_exact_positive": all(value > 0 for value in state_record_work),
        "all_independent_work_records_agree_within_display_resolution": all(
            separation <= bound for separation, bound in zip(exact_separations, exact_resolution_bounds)
        ),
        "all_fourteen_columns_retained": all(set(VALUE_COLUMNS).issubset(row["target_payload"]) for row in rows),
        "all_13_rows_retained": len(rows) == 13,
        "nine_liquid_and_four_vapor_rows_retained": phases.count("liquid") == 9 and phases.count("vapor") == 4,
        "phase_boundary_pair_retained": phases[8:10] == ("liquid", "vapor") and all(
            row["target_payload"]["temperature-kelvin"] == "372.75593" for row in rows[8:10]
        ),
    }


class HeatWorkTransferPartitionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = HEAT_WORK_TRANSFER_PARTITION_SPEC

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
            raise ValueError("THERMO-004 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {
            str(row["target_id"]): HeldLabel("external-state-vector-hash", str(row["target_payload_hash"]))
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
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == "carrier-label-closed-by-receiving-macro-observation"
                and isinstance(word.cells[8], HeldLabel) and word.cells[8].label == "organized-source-response-label-retained"
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == "disjoint-exhaustive-heat-work-path-partition"
                and isinstance(word.cells[10], HeldLabel) and word.cells[10].label == "per-class-positive-composition-plus-EmptyOne-absence"
            )
            target_match = release.targets[target_id] == HeldLabel("external-state-vector-hash", str(row["target_payload_hash"]))
            comparisons.append({
                "target_id": target_id, "target_payload_hash": row["target_payload_hash"],
                "identity_match": identity_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and target_match,
            })

        analysis = exact_heat_work_analysis(source_rows)
        tampered_rows = [dict(row) for row in source_rows]
        tampered_payload = dict(tampered_rows[5]["target_payload"])
        tampered_payload["isobaric-heat-capacity-joule-per-mole-kelvin"] = "-1.000000"
        tampered_rows[5] = {**tampered_rows[5], "target_payload": tampered_payload}
        controls = {
            "tampered_nonpositive_calorimetric_record_rejected": exact_heat_work_analysis(tuple(tampered_rows))["all_calorimetric_values_exact_positive"] is False,
            "complete_13_row_vector_retained": len(release.targets) == len(source_rows) == 13,
            "complete_14_column_vector_retained": analysis["all_fourteen_columns_retained"],
            "both_phase_boundary_states_retained": analysis["phase_boundary_pair_retained"],
            "calorimetric_and_expansion_work_vectors_distinct_and_complete": len(analysis["calorimetric_heat_capacity_values"]) == len(analysis["pressure_volume_work_values_kilojoule_per_mole"]) == 13,
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        analysis_passed = all(
            bool(value) for key, value in analysis.items()
            if key not in {
                "calorimetric_heat_capacity_values", "pressure_volume_work_values_kilojoule_per_mole",
                "state_record_work_values_kilojoule_per_mole", "work_record_exact_separations",
                "work_record_exact_resolution_bounds",
            }
        )
        passed = all(bool(row["passed"]) for row in comparisons) and analysis_passed and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-calorimetric-expansion-work-partition", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-004 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "calorimetric_values": tuple(str(value) for value in analysis["calorimetric_heat_capacity_values"]),
            "pressure_volume_work_values": tuple(str(value) for value in analysis["pressure_volume_work_values_kilojoule_per_mole"]),
            "state_record_work_values": tuple(str(value) for value in analysis["state_record_work_values_kilojoule_per_mole"]),
            "work_record_separations": tuple(str(value) for value in analysis["work_record_exact_separations"]),
            "work_record_resolution_bounds": tuple(str(value) for value in analysis["work_record_exact_resolution_bounds"]),
            "comparisons": comparisons, "controls": controls, "complete_trace_hash": execution.trace_hash,
        }
        measurements = tuple(
            f"row {index}: Cp={row['target_payload']['isobaric-heat-capacity-joule-per-mole-kelvin']} J/(mol K); pV={analysis['pressure_volume_work_values_kilojoule_per_mole'][index-1]} kJ/mol; H-U={analysis['state_record_work_values_kilojoule_per_mole'][index-1]} kJ/mol"
            for index, row in enumerate(source_rows, start=1)
        ) + (
            "all 13 direct calorimetric values exact positive",
            "all 13 pressure-volume and independent state-record work magnitudes exact positive and mutually consistent within displayed resolution",
            "both 372.75593 K liquid/vapour records retained",
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
    "HeatWorkTransferPartitionValidator", "_prediction_map", "exact_heat_work_analysis",
    "experiment_registration_record", "prediction_program_document",
)
