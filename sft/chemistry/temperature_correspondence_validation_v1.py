"""Post-seal exact thermometric equilibrium validation for Chemistry THERMO-002."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.temperature_correspondence_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PHYSICS_RECORD_HASH, PHYSICS_RECORD_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, TARGET_HASH, TARGET_PATH,
    TEMPERATURE_CORRESPONDENCE_SPEC,
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


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-002 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "exact_si_common_carrier_scaled_numerator", "common_scale_denominator",
        "measured_center_scaled_numerator", "measured_standard_uncertainty_scaled_numerator",
        "measured_interval_lower_scaled_numerator", "measured_interval_upper_scaled_numerator",
        "relative_standard_uncertainty_parts_per_million", "relative_combined_uncertainty_parts_per_million",
        "temperature_measures_average_kinetic_energy", "noise_power_depends_on_resistance_and_temperature",
        "reported_relation_accuracy_parts_per_million",
    }
    if (
        document.get("schema") != "sft-v3-chemical-temperature-identities/1"
        or document.get("complete_target_count") != 3
        or document.get("complete_physically_distinct_route_count") != 2
        or document.get("all_values_uncertainties_intervals_and_relation_flags_absent") is not True
        or len(rows) != 3
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-002 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    fields = (
        ("source_class", "external-record-class"),
        ("source_id", "external-source-identity"),
        ("route_identity", "thermometric-route"),
        ("chemical_composition_identity", "chemical-composition"),
        ("phase_identity", "phase-identity"),
        ("equilibrium_reference_identity", "thermal-equilibrium-reference"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"chemical-temperature-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            value = str(row.get(key, "held-not-applicable-to-common-carrier-definition"))
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, value]})
            registers.append(destination)
        for family, label in (
            ("authority-law", "chemistry-consumes-admitted-physics-temperature-carrier"),
            ("correspondence-law", "identity-preserving-temperature-correspondence"),
            ("equilibrium-law", "one-common-carrier-across-equilibrated-routes"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-chemical-temperature-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-chemical-temperature-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": TEMPERATURE_CORRESPONDENCE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": TEMPERATURE_CORRESPONDENCE_SPEC.experiment_id,
        "claim_id": TEMPERATURE_CORRESPONDENCE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": TEMPERATURE_CORRESPONDENCE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "physics_source_record": (PHYSICS_RECORD_PATH, PHYSICS_RECORD_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in TEMPERATURE_CORRESPONDENCE_SPEC.target_rows),
        "all_values_uncertainties_intervals_and_relation_flags_absent_from_prediction": True,
        "falsification_condition": TEMPERATURE_CORRESPONDENCE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 3:
        raise ValueError("THERMO-002 prediction is not the complete three-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("THERMO-002 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10:
            raise ValueError("THERMO-002 prediction lost its complete correspondence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 3:
        raise ValueError("THERMO-002 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
        (PHYSICS_RECORD_PATH, PHYSICS_RECORD_HASH), *SOURCE_FILES,
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-002 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-chemical-temperature-withheld-targets/1"
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or document.get("complete_target_count") != 3
        or document.get("measurement_routes_physically_distinct") is not True
        or document.get("all_registered_rows_retained") is not True
        or len(targets) != 3
    ):
        raise ValueError("THERMO-002 withheld target registry changed")
    resolved: list[dict[str, object]] = []
    for identity, target in zip(identities, targets):
        if identity["target_id"] != target.get("target_id") or identity["source_class"] != target.get("source_class"):
            raise ValueError("THERMO-002 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    if (
        resolved[1]["target_payload"].get("chemical_composition_identity") != "argon"
        or resolved[1]["target_payload"].get("phase_identity") != "gas"
        or resolved[1]["target_payload"].get("equilibrium_reference_identity") != "triple-point-of-water"
    ):
        raise ValueError("THERMO-002 acoustic chemical context changed")
    return tuple(resolved)


def exact_temperature_analysis(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    common, acoustic, electronic = (row["target_payload"] for row in rows)
    exact = int(common["exact_si_common_carrier_scaled_numerator"])
    denominator = int(common["common_scale_denominator"])
    acoustic_interval = (
        int(acoustic["measured_interval_lower_scaled_numerator"]),
        int(acoustic["measured_interval_upper_scaled_numerator"]),
    )
    electronic_interval = (
        int(electronic["measured_interval_lower_scaled_numerator"]),
        int(electronic["measured_interval_upper_scaled_numerator"]),
    )
    positive = (
        exact, denominator, *acoustic_interval, *electronic_interval,
        int(acoustic["measured_center_scaled_numerator"]),
        int(acoustic["measured_standard_uncertainty_scaled_numerator"]),
        int(electronic["measured_center_scaled_numerator"]),
        int(electronic["measured_standard_uncertainty_scaled_numerator"]),
    )
    return {
        "exact_common_carrier_scaled_numerator": exact,
        "common_scale_denominator": denominator,
        "acoustic_interval": acoustic_interval,
        "electronic_interval": electronic_interval,
        "all_external_magnitudes_exact_positive": all(value > 0 for value in positive),
        "acoustic_contains_exact_common_carrier": acoustic_interval[0] <= exact <= acoustic_interval[1],
        "electronic_contains_exact_common_carrier": electronic_interval[0] <= exact <= electronic_interval[1],
        "acoustic_center_and_uncertainty_reconstruct_interval": (
            int(acoustic["measured_center_scaled_numerator"]) - int(acoustic["measured_standard_uncertainty_scaled_numerator"]) == acoustic_interval[0]
            and int(acoustic["measured_center_scaled_numerator"]) + int(acoustic["measured_standard_uncertainty_scaled_numerator"]) == acoustic_interval[1]
        ),
        "electronic_center_and_uncertainty_reconstruct_interval": (
            int(electronic["measured_center_scaled_numerator"]) - int(electronic["measured_standard_uncertainty_scaled_numerator"]) == electronic_interval[0]
            and int(electronic["measured_center_scaled_numerator"]) + int(electronic["measured_standard_uncertainty_scaled_numerator"]) == electronic_interval[1]
        ),
        "argon_gas_TPW_context_retained": (
            acoustic["chemical_composition_identity"] == "argon"
            and acoustic["phase_identity"] == "gas"
            and acoustic["equilibrium_reference_identity"] == "triple-point-of-water"
        ),
        "kinetic_temperature_relation_retained": acoustic["temperature_measures_average_kinetic_energy"] is True,
        "Johnson_temperature_response_retained": electronic["noise_power_depends_on_resistance_and_temperature"] is True,
        "Johnson_one_ppm_relation_record_retained": int(electronic["reported_relation_accuracy_parts_per_million"]) == 1,
    }


class TemperatureCorrespondenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = TEMPERATURE_CORRESPONDENCE_SPEC

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
            raise ValueError("THERMO-002 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): row["target_payload"] for row in source_rows}
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
            expected_reference = str(row.get("equilibrium_reference_identity", "held-not-applicable-to-common-carrier-definition"))
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["source_class"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["source_id"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["route_identity"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["chemical_composition_identity"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["phase_identity"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == expected_reference
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == "chemistry-consumes-admitted-physics-temperature-carrier"
                and isinstance(word.cells[8], HeldLabel) and word.cells[8].label == "identity-preserving-temperature-correspondence"
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == "one-common-carrier-across-equilibrated-routes"
            )
            target_match = release.targets[target_id] == row["target_payload"]
            comparisons.append({
                "target_id": target_id, "source_class": row["source_class"],
                "target_payload_hash": row["target_payload_hash"],
                "identity_match": identity_match, "postseal_target_match": target_match,
                "passed": identity_match and target_match,
            })

        analysis = exact_temperature_analysis(source_rows)
        tampered = [dict(row) for row in source_rows]
        tampered_acoustic = dict(tampered[1]["target_payload"])
        tampered_acoustic["measured_interval_lower_scaled_numerator"] = 13000000
        tampered_acoustic["measured_interval_upper_scaled_numerator"] = 13000001
        tampered[1] = {**tampered[1], "target_payload": tampered_acoustic}
        controls = {
            "tampered_acoustic_interval_rejected": exact_temperature_analysis(tuple(tampered))["acoustic_contains_exact_common_carrier"] is False,
            "complete_three_target_rows_retained": len(release.targets) == len(source_rows) == 3,
            "two_physically_distinct_routes_retained": len({row["route_identity"] for row in source_rows[1:]}) == 2,
            "all_exact_interval_relations_pass": all(bool(value) for key, value in analysis.items() if key not in {"exact_common_carrier_scaled_numerator", "common_scale_denominator", "acoustic_interval", "electronic_interval"}),
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-chemical-temperature-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-002 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "comparisons": comparisons, "exact_analysis": analysis, "controls": controls,
            "complete_trace_hash": execution.trace_hash,
        }
        measurements = (
            "Exact SI common carrier: 13806490/10^30 joule per kelvin.",
            "Acoustic argon interval: [13806456,13806512]/10^30 joule per kelvin; exact carrier contained.",
            "Johnson-noise interval: [13806340,13806680]/10^30 joule per kelvin; exact carrier contained.",
            "Acoustic composition/condition: pure argon gas at the triple point of water retained.",
            "Acoustic kinetic-temperature and electronic Johnson temperature-response relations retained.",
        ) + tuple(f"{name}: {result}" for name, result in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=("NIST-CODATA-2022-BOLTZMANN", "NIM-NIST-ACOUSTIC-BOLTZMANN-2017", "NIST-JOHNSON-NOISE-BOLTZMANN-2011"),
            measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "TemperatureCorrespondenceValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_temperature_analysis", "experiment_registration_record", "prediction_program_document",
)
