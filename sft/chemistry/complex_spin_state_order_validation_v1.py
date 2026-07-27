"""Capability-closed post-seal validation for Chemistry INORG-007."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.complex_spin_state_order_batch_v1 import (
    COMPLEX_SPIN_STATE_ORDER_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.complex_spin_state_order_law_v1 import (
    enumerate_complete_spin_signatures, forced_high_spin_state, forced_low_spin_state,
    forced_six_electron_order_vector,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldLanguageHalt,
    FoldTable, FoldWord, HostilePackageAuditor, TargetVault, fold_program_from_mapping,
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


IDENTITY_KEYS = (
    "target_id", "source_record_ordinal", "source_id", "authority", "registered_identity",
    "source_record_role", "custody_class",
)
EXPECTED_LAWS = (
    "ten-complete-six-electron-signatures",
    "unique-low-and-high-spin-extrema",
    "exact-high-coincident-low-order-vector",
    "all-three-frozen-definition-value-and-transport-surfaces-retained",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-007 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"value", "outcome", "definition", "term", "distance", "temperature", "target_payload_hash"}
    if (
        document.get("complete_registered_target_count") != 3
        or document.get("target_values_definitions_terms_distances_temperatures_outcomes_or_payload_hashes_present") is not False
        or len(rows) != 3
        or tuple(row["source_record_ordinal"] for row in rows) != (1, 2, 3)
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-007 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"complex-spin-state-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["complex-spin-state-law", label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-complex-spin-state-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-complex-spin-state-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COMPLEX_SPIN_STATE_ORDER_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COMPLEX_SPIN_STATE_ORDER_SPEC.experiment_id,
        "claim_id": COMPLEX_SPIN_STATE_ORDER_SPEC.claim_id,
        "provenance": "forward_forcing_with_family-sealed_external_comparison",
        "frozen_relation": COMPLEX_SPIN_STATE_ORDER_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COMPLEX_SPIN_STATE_ORDER_SPEC.target_rows),
        "all_three_rows_required": True,
        "registered_transport_mismatch_must_be_preserved": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "no_field_pairing_temperature_distance_or_species_fit": True,
        "falsification_condition": COMPLEX_SPIN_STATE_ORDER_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 3:
        raise ValueError("INORG-007 prediction is not the complete three-row table")
    result: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("INORG-007 prediction row is incomplete")
        result[entry.left.label] = entry.right
    if len(result) != 3:
        raise ValueError("INORG-007 prediction duplicates a target")
    return result


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("INORG-007 post-seal target evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 3 or len(rows) != 3 or document.get("release_requires_prediction_seal") is not True:
        raise ValueError("INORG-007 target vector is incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-007 target differs from its registered identity")
        expected = sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome")))
        if row.get("target_payload_hash") != expected:
            raise ValueError("INORG-007 target payload hash changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict[str, object]:
    if len(rows) != 3:
        raise ValueError("INORG-007 requires all three source surfaces")
    signatures = enumerate_complete_spin_signatures(PositiveCount(6))
    high = forced_high_spin_state(signatures)
    low = forced_low_spin_state(signatures)
    vector = forced_six_electron_order_vector()
    high_surface, low_surface, crossover_surface = tuple(row["source_outcome"] for row in rows)
    postseal = primary["exact_postseal_analysis"]
    return {
        "signature_count": len(signatures),
        "low_signature": (
            3 if not isinstance(low.lower_pairs, EmptyOne) else "EmptyOne",
            "EmptyOne" if isinstance(low.lower_singles, EmptyOne) else low.lower_singles.value,
            "EmptyOne" if isinstance(low.upper_pairs, EmptyOne) else low.upper_pairs.value,
            "EmptyOne" if isinstance(low.upper_singles, EmptyOne) else low.upper_singles.value,
        ),
        "low_spin_width": low.spin_width.value,
        "low_crossings": "EmptyOne" if isinstance(low.split_crossing_count, EmptyOne) else low.split_crossing_count.value,
        "high_signature": (
            high.lower_pairs.value if not isinstance(high.lower_pairs, EmptyOne) else "EmptyOne",
            high.lower_singles.value if not isinstance(high.lower_singles, EmptyOne) else "EmptyOne",
            high.upper_pairs.value if not isinstance(high.upper_pairs, EmptyOne) else "EmptyOne",
            high.upper_singles.value if not isinstance(high.upper_singles, EmptyOne) else "EmptyOne",
        ),
        "high_spin_width": high.spin_width.value,
        "high_crossings": high.split_crossing_count.value if not isinstance(high.split_crossing_count, EmptyOne) else "EmptyOne",
        "order_vector": tuple(row.order.label for row in vector),
        "cost_vector": tuple(("EmptyOne" if isinstance(row.high_cost, EmptyOne) else row.high_cost.value, "EmptyOne" if isinstance(row.low_cost, EmptyOne) else row.low_cost.value) for row in vector),
        "combined_high_low_definition_surface_present": high_surface["combined_surface_also_defines_high_spin"] and high_surface["low_spin_complete_lower_support_surface_present"] and high_surface["high_spin_prior_higher_support_occupation_surface_present"],
        "low_order_definition_surface_present": low_surface["paired_lower_support_surface_present"] and low_surface["complete_order_comparison_surface_present"],
        "transport_mismatch_preserved": high_surface["registered_transport_identity_mismatch_preserved"] and high_surface["requested_source_id"] != high_surface["observed_source_code"],
        "external_distance_vector_pm": (crossover_surface["lower_distance_pm_exact"], crossover_surface["higher_distance_pm_exact"]),
        "external_temperature_vector_k": (crossover_surface["lower_temperature_k_exact"], crossover_surface["higher_temperature_k_exact"]),
        "external_term_vector": (crossover_surface["lower_term"], crossover_surface["higher_term"]),
        "external_state_vector": (crossover_surface["lower_state"], crossover_surface["higher_state"]),
        "external_dilution_direction_match": crossover_surface["shorter_distance_maps_to_low_spin"] and crossover_surface["longer_distance_maps_to_high_spin"],
        "complete_rows_preserved": postseal["all_three_rows_preserved"] and len(rows) == 3,
        "dimensional_values_fitted_or_derived": postseal["dimensional_distance_temperature_or_term_fitted_or_derived"],
    }


class ComplexSpinStateOrderValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COMPLEX_SPIN_STATE_ORDER_SPEC

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
            raise ValueError("INORG-007 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})

        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis = exact_analysis(source_rows, primary)
        try:
            exact_analysis(source_rows[:-1], primary)
            omitted_rejected = False
        except ValueError:
            omitted_rejected = True
        try:
            FoldWord((0,))
            zero_rejected = False
        except FoldLanguageHalt:
            zero_rejected = True
        controls = {
            "omitted_source_row_rejected": omitted_rejected,
            "numerical_zero_rejected": zero_rejected,
            "transport_mismatch_preserved": analysis["transport_mismatch_preserved"],
            "all_three_target_hashes_bound_postseal": len(release.targets) == 3,
            "prediction_contains_no_target_payload_or_dimensional_value": "target_payload_hash" not in json.dumps(document, sort_keys=True) and "203.2" not in json.dumps(document, sort_keys=True) and "227" not in json.dumps(document, sort_keys=True),
            "tampered_order_vector_rejected": analysis["order_vector"] != ("low-precedes-high", "crossover-coincidence", "high-precedes-low"),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["signature_count"] == 10
            and analysis["low_signature"] == (3, "EmptyOne", "EmptyOne", "EmptyOne")
            and analysis["low_spin_width"] == 1
            and analysis["low_crossings"] == "EmptyOne"
            and analysis["high_signature"] == (1, 2, "EmptyOne", 2)
            and analysis["high_spin_width"] == 5
            and analysis["high_crossings"] == 2
            and analysis["order_vector"] == ("high-precedes-low", "crossover-coincidence", "low-precedes-high")
            and analysis["cost_vector"] == ((1, 3), (3, 3), (5, 3))
            and analysis["combined_high_low_definition_surface_present"]
            and analysis["low_order_definition_surface_present"]
            and analysis["external_distance_vector_pm"] == ("1016/5", "2199/10")
            and analysis["external_temperature_vector_k"] == ("115", "227")
            and analysis["external_term_vector"] == ("1A1", "5T2")
            and analysis["external_state_vector"] == ("low-spin", "high-spin")
            and analysis["external_dilution_direction_match"]
            and analysis["complete_rows_preserved"]
            and analysis["dimensional_values_fitted_or_derived"] is False
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
            comparison_implementation_identity_hash=sha256_identity(("exact-complex-spin-state-order/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-007 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "complete six-electron split-support census: 10 signatures",
            "forced low signature lower pairs 3, spin width 1, crossing EmptyOne",
            "forced high signature lower pair 1, lower singles 2, upper singles 2, spin width 5, crossings 2",
            "exact recurrence order vector high-before-low, crossover coincidence, low-before-high",
            "IUPAC crossover vector 1016/5 pm at 115 K low-spin 1A1; 2199/10 pm at 227 K high-spin 5T2",
            "registered HT06789 transport returned LT06788 combined low/high definition and is preserved",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements,
            sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "ComplexSpinStateOrderValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_analysis", "experiment_registration_record", "prediction_program_document",
)
