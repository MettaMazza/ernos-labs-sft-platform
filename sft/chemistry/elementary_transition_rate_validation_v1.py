"""Capability-closed post-seal validation for Chemistry KIN-001."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.elementary_transition_rate_batch_v1 import (
    ELEMENTARY_TRANSITION_RATE_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.elementary_transition_rate_law_v1 import (
    ElementaryTransitionAccount, external_rate_magnitude, forced_elementary_transition_rate,
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
        raise ValueError("KIN-001 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "complete_source_metadata", "reaction", "reaction_order", "temperature_K_external_inscription",
        "rate_external_inscription", "rate_unit_external_inscription", "rate_expression", "target_payload",
        "target_payload_hash", "method", "condition",
    }
    if (
        document.get("complete_source_count") != 4 or document.get("complete_target_count") != 46
        or document.get("all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent") is not True
        or len(rows) != 46 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-001 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"elementary-rate-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("record-identity", row["record_id"]),
            ("positive-source-row-ordinal", str(row["source_row_ordinal"])),
            ("source-locator-kind", "nist-srd17-complete-rate-table-row"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("carrier-law", "registered-elementary-reaction-with-distinct-molecular-endpoints"),
            ("resource-law", "positive-completed-transition-per-positive-tick-and-observation-support"),
            ("condition-law", "complete-held-condition-record-with-structural-EmptyOne"),
            ("magnitude-law", "exact-positive-postseal-rate-support-without-imported-rate-law"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-elementary-rate-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-elementary-rate-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ELEMENTARY_TRANSITION_RATE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": ELEMENTARY_TRANSITION_RATE_SPEC.experiment_id,
        "claim_id": ELEMENTARY_TRANSITION_RATE_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": ELEMENTARY_TRANSITION_RATE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_raw_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in ELEMENTARY_TRANSITION_RATE_SPEC.target_rows),
        "all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent": True,
        "falsification_condition": ELEMENTARY_TRANSITION_RATE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 46:
        raise ValueError("KIN-001 prediction is not the complete 46-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 9
        ):
            raise ValueError("KIN-001 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 46:
        raise ValueError("KIN-001 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-001 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_source_count") != 4 or document.get("complete_target_count") != 46
        or document.get("source_declared_order_row_counts") != {"1": 4, "2": 24, "3": 18}
        or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 46
    ):
        raise ValueError("KIN-001 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in ("target_id", "source_id", "record_id", "source_row_ordinal")):
            raise ValueError("KIN-001 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_elementary_rate_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    order_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    rates: dict[str, list[Fraction]] = defaultdict(list)
    temperatures: dict[str, list[Fraction]] = defaultdict(list)
    for row in rows:
        target = row["target_payload"]
        metadata = target.get("complete_source_metadata", {})
        if (
            metadata.get("Category") != "Experiment" or "measured" not in metadata.get("Data type", "").lower()
            or not metadata.get("Reaction") or not metadata.get("Rate expression")
            or target.get("source_reported_rate_is_arrhenius_tabulation_of_direct_experimental_record") is not True
            or target.get("raw_event_count_claimed") is not False
        ):
            raise ValueError("KIN-001 complete external experimental provenance changed")
        order = metadata.get("Reaction order")
        if order not in {"1", "2", "3"}:
            raise ValueError("KIN-001 source-declared external order class changed")
        rate = external_rate_magnitude(str(target.get("rate_external_inscription", ""))).fraction
        temperature = Fraction(str(target.get("temperature_K_external_inscription", "")))
        if temperature <= 0 or not target.get("rate_unit_external_inscription"):
            raise ValueError("KIN-001 external condition or unit changed")
        account = ElementaryTransitionAccount(
            HeldLabel("registered-elementary-reaction", row["record_id"]),
            HeldLabel("molecular-state", "source-bound-reactant-state"),
            HeldLabel("molecular-state", "source-bound-product-state"),
            PositiveCount(int(row["source_row_ordinal"])), PositiveCount(1), PositiveCount(1),
            (PositiveRatio.from_pair(temperature.numerator, temperature.denominator), EmptyOne()),
        )
        if forced_elementary_transition_rate(account).carrier.label != row["record_id"]:
            raise ValueError("KIN-001 registered elementary carrier changed")
        order_counts[order] += 1
        source_counts[row["source_id"]] += 1
        rates[order].append(rate)
        temperatures[order].append(temperature)
    return {
        "complete_target_count": len(rows), "source_declared_order_row_counts": dict(order_counts),
        "complete_source_row_counts": dict(source_counts),
        "exact_rate_ranges_by_source_declared_order": {
            key: {"minimum": str(min(values)), "maximum": str(max(values))} for key, values in sorted(rates.items())
        },
        "exact_temperature_ranges_K_by_source_declared_order": {
            key: {"minimum": str(min(values)), "maximum": str(max(values))} for key, values in sorted(temperatures.items())
        },
        "all_46_rows_retained": len(rows) == 46,
        "all_declared_order_classes_retained": dict(order_counts) == {"1": 4, "2": 24, "3": 18},
        "all_four_complete_sources_retained": len(source_counts) == 4 and sum(source_counts.values()) == 46,
        "all_sources_direct_experiment_records": True,
        "arrhenius_tabulations_disclosed_not_raw_event_counts": all(row["target_payload"]["raw_event_count_claimed"] is False for row in rows),
        "no_imported_rate_law_fit_or_selection": (
            primary.get("mass_action_rate_equation_reaction_order_arrhenius_logarithm_concentration_derivative_continuum_selection_fit_or_target_correction_used_in_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
        ),
    }


class ElementaryTransitionRateValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ELEMENTARY_TRANSITION_RATE_SPEC

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
            raise ValueError("KIN-001 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-elementary-rate-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "registered-elementary-reaction-with-distinct-molecular-endpoints",
            "positive-completed-transition-per-positive-tick-and-observation-support",
            "complete-held-condition-record-with-structural-EmptyOne",
            "exact-positive-postseal-rate-support-without-imported-rate-law",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (row["source_id"], row["record_id"], str(row["source_row_ordinal"]), "nist-srd17-complete-rate-table-row")
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[5:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-elementary-rate-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_elementary_rate_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["rate_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        try:
            exact_elementary_rate_analysis(tuple(tampered), primary)
            tamper_rejected = False
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_rate_rejected": tamper_rejected,
            "complete_46_record_vector_retained": len(release.targets) == 46,
            "all_declared_order_classes_retained": analysis["all_declared_order_classes_retained"],
            "all_four_sources_retained": analysis["all_four_complete_sources_retained"],
            "arrhenius_tabulations_not_mislabeled_as_raw_counts": analysis["arrhenius_tabulations_disclosed_not_raw_event_counts"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "source_declared_order_row_counts", "complete_source_row_counts", "exact_rate_ranges_by_source_declared_order", "exact_temperature_ranges_K_by_source_declared_order"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-elementary-rate-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-001 released target differs from commitment")
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
            f"{row['target_id']}: source={row['source_id']}; row={row['source_row_ordinal']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete vector: 4 source-declared first-order, 24 second-order and 18 third-order tabulated rate rows",
            f"exact rate ranges by source-declared order: {analysis['exact_rate_ranges_by_source_declared_order']}",
            "source boundary: four complete NIST SRD 17 direct-experiment records; tabulations are source-calculated, not raw event counts",
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
    "ElementaryTransitionRateValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_elementary_rate_analysis", "experiment_registration_record", "prediction_program_document",
)
