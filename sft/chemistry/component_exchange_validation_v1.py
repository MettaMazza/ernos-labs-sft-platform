"""Post-seal complete multicomponent-equilibrium validation for THERMO-008."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.component_exchange_batch_v1 import (
    COMPONENT_EXCHANGE_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    RAW_HASH,
    RAW_PATH,
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
        raise ValueError("THERMO-008 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "ordered_component_orgnums",
        "complete_component_records",
        "variable_component_orgnum",
        "complementary_component_orgnum",
        "pressure_kPa_external_inscription",
        "temperature_K_external_inscription",
        "liquid_variable_component_part_external_inscription",
        "gas_variable_component_part_external_inscription",
        "external_phase_classification",
        "target_payload",
        "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 74
        or document.get(
            "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_absent"
        )
        is not True
        or len(rows) != 74
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-008 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"component-exchange-row-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        fields = (
            ("doi", "source-doi"),
            ("source_id", "complete-source-identity"),
            ("system_ordinal", "positive-system-ordinal"),
            ("temperature_dataset_ordinal", "temperature-dataset-ordinal"),
            ("composition_dataset_ordinal", "composition-dataset-ordinal"),
            ("common_interior_point_ordinal", "positive-common-point-ordinal"),
        )
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]}
            )
            registers.append(destination)
        for family, label in (
            ("component-law", "same-held-component-across-distinct-phases"),
            ("environment-law", "one-fixed-finite-environment"),
            ("marginal-law", "exact-positive-energy-and-distinction-addition-account"),
            ("relation-law", "strict-product-order-with-EmptyOne-equilibrium"),
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
            {"opcode": "table", "destination": "complete-component-exchange-vector", "arguments": table},
            {"opcode": "emit", "destination": "", "arguments": ["complete-component-exchange-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COMPONENT_EXCHANGE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COMPONENT_EXCHANGE_SPEC.experiment_id,
        "claim_id": COMPONENT_EXCHANGE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": COMPONENT_EXCHANGE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "raw_source": (RAW_PATH, RAW_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COMPONENT_EXCHANGE_SPEC.target_rows),
        "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_absent": True,
        "falsification_condition": COMPONENT_EXCHANGE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 74:
        raise ValueError("THERMO-008 prediction is not the complete 74-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("THERMO-008 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 74:
        raise ValueError("THERMO-008 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
        (RAW_PATH, RAW_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-008 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 74
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 74
    ):
        raise ValueError("THERMO-008 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["system_ordinal"] != target.get("system_ordinal")
            or identity["temperature_dataset_ordinal"] != target.get("temperature_dataset_ordinal")
            or identity["composition_dataset_ordinal"] != target.get("composition_dataset_ordinal")
        ):
            raise ValueError("THERMO-008 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_component_exchange_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    systems: Counter[int] = Counter()
    pressures: list[Fraction] = []
    temperatures: list[Fraction] = []
    liquid_parts: list[Fraction] = []
    gas_parts: list[Fraction] = []
    relation_labels: list[str] = []
    for row in rows:
        target = row["target_payload"]
        liquid = Fraction(target["liquid_variable_component_part_external_inscription"])
        liquid_complement = Fraction(target["liquid_complement_component_part_external_inscription"])
        gas = Fraction(target["gas_variable_component_part_external_inscription"])
        gas_complement = Fraction(target["gas_complement_component_part_external_inscription"])
        pressure = Fraction(target["pressure_kPa_external_inscription"])
        temperature = Fraction(target["temperature_K_external_inscription"])
        if liquid + liquid_complement != 1 or gas + gas_complement != 1:
            raise ValueError("THERMO-008 phase composition does not exhaust the One")
        if not (0 < liquid < 1 and 0 < liquid_complement < 1 and 0 < gas < 1 and 0 < gas_complement < 1):
            raise ValueError("THERMO-008 multicomponent phase has an absent or overfull component")
        if target.get("external_phase_classification") != "binary-vapor-liquid-equilibrium":
            raise ValueError("THERMO-008 target lost its equilibrium classification")
        if len(target.get("complete_component_records", ())) != 2:
            raise ValueError("THERMO-008 target lost a component record")
        if not target.get("temperature_uncertainty") or not target.get("gas_composition_uncertainty"):
            raise ValueError("THERMO-008 target lost a reported uncertainty")
        systems[int(target["system_ordinal"])] += 1
        pressures.append(pressure)
        temperatures.append(temperature)
        liquid_parts.append(liquid)
        gas_parts.append(gas)
        relation_labels.append("gas-greater" if gas > liquid else "liquid-greater" if liquid > gas else "equal")
    system_one = relation_labels[:20]
    crossings = tuple(
        index for index, (left, right) in enumerate(zip(system_one, system_one[1:]), start=1) if left != right
    )
    return {
        "complete_target_count": len(rows),
        "system_counts": dict(systems),
        "all_pressure_inscriptions": tuple(str(value) for value in pressures),
        "all_temperature_inscriptions": tuple(str(value) for value in temperatures),
        "all_liquid_parts": tuple(str(value) for value in liquid_parts),
        "all_gas_parts": tuple(str(value) for value in gas_parts),
        "external_phase_composition_relation_vector": tuple(relation_labels),
        "all_74_rows_retained": len(rows) == 74,
        "all_four_systems_retained": dict(systems) == {1: 20, 2: 18, 3: 18, 4: 18},
        "all_rows_share_fixed_101_3_kPa_environment": set(pressures) == {Fraction(1013, 10)},
        "all_phase_compositions_are_exact_positive_parts_of_One": len(liquid_parts) == 74,
        "equal_component_account_does_not_require_equal_bulk_composition": all(
            liquid != gas for liquid, gas in zip(liquid_parts, gas_parts)
        ),
        "both_external_enrichment_orientations_retained": relation_labels.count("gas-greater") == 66
        and relation_labels.count("liquid-greater") == 8,
        "system_one_composition_crossing_retained": crossings == (8,),
        "all_eight_unmatched_source_endpoints_preserved": primary.get(
            "complete_unmatched_temperature_endpoint_count"
        )
        == 8
        and len(primary.get("unmatched_temperature_endpoints", ())) == 8,
        "complete_raw_source_surface_preserved": primary.get("complete_source_compound_count") == 5
        and primary.get("complete_source_dataset_count") == 13
        and primary.get("all_direct_equilibrium_rows_and_unpaired_source_endpoints_preserved") is True,
    }


class ComponentExchangeValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COMPONENT_EXCHANGE_SPEC

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
            raise ValueError("THERMO-008 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-multicomponent-row-hash", row["target_payload_hash"])
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
                str(row["system_ordinal"]),
                str(row["temperature_dataset_ordinal"]),
                str(row["composition_dataset_ordinal"]),
                str(row["common_interior_point_ordinal"]),
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            ) and tuple(cell.label for cell in word.cells[7:]) == (
                "same-held-component-across-distinct-phases",
                "one-fixed-finite-environment",
                "exact-positive-energy-and-distinction-addition-account",
                "strict-product-order-with-EmptyOne-equilibrium",
            )
            target_match = release.targets[target_id] == HeldLabel(
                "external-multicomponent-row-hash", row["target_payload_hash"]
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
        analysis = exact_component_exchange_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["gas_complement_component_part_external_inscription"] = "1/2"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_component_exchange_analysis(tuple(tampered), primary)
        except ValueError:
            tamper_rejected = True
        controls = {
            "tampered_complement_rejected": tamper_rejected,
            "complete_74_row_vector_retained": len(release.targets) == 74,
            "complete_four_system_surface_retained": analysis["all_four_systems_retained"],
            "eight_unpaired_endpoints_retained": analysis["all_eight_unmatched_source_endpoints_preserved"],
            "both_external_composition_relations_retained": analysis[
                "both_external_enrichment_orientations_retained"
            ],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH
            not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count",
            "system_counts",
            "all_pressure_inscriptions",
            "all_temperature_inscriptions",
            "all_liquid_parts",
            "all_gas_parts",
            "external_phase_composition_relation_vector",
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
                    ("exact-component-exchange-VLE-correspondence", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-008 released target differs from commitment")
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
                f"{row['target_id']}: system={row['target_payload']['system_ordinal']}; "
                f"T={row['target_payload']['temperature_K_external_inscription']} K; "
                f"P={row['target_payload']['pressure_kPa_external_inscription']} kPa; "
                f"x={row['target_payload']['liquid_variable_component_part_external_inscription']}; "
                f"y={row['target_payload']['gas_variable_component_part_external_inscription']}"
            )
            for row in source_rows
        ) + (
            "complete vector: four binary systems and 74 matched multicomponent equilibrium rows",
            "source boundary: eight unmatched pure-component temperature endpoints retained",
            "phase relation vector: 66 gas-greater and 8 liquid-greater rows; one system-one crossing retained",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("NIST-TRC-THERMOML-JCED-2019-9B00414",),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "ComponentExchangeValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_component_exchange_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
