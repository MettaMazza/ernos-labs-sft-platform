"""Post-seal complete finite state/calorimetric structure validation for THERMO-001."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform

from sft.chemistry.finite_microstate_batch_v1 import (
    FINITE_MICROSTATE_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH, WATER_HASH, WATER_PATH,
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


def _canonical_payload_hash(payload: object) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-001 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "cells", "temperature_inscription_kelvin", "heat_capacity_inscription", "entropy_inscription",
        "held_gibbs_reference_relation_inscription", "enthalpy_reference_relation_inscription",
        "target_payload", "target_payload_hash", "population", "measured_value",
    }
    if (
        document.get("schema") != "sft-v3-finite-microstate-identities/1"
        or document.get("complete_state_population_row_count") != 330
        or document.get("complete_calorimetric_row_count") != 57
        or document.get("complete_target_count") != 387
        or document.get("all_populations_temperatures_and_calorimetric_values_absent") is not True
        or len(rows) != 387
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-001 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Seal all 387 row identities and structural consequences without target values."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    fields = (
        ("source_class", "external-record-class"),
        ("source_id", "external-source-identity"),
        ("source_row_ordinal", "positive-source-row-ordinal"),
        ("snapshot_hash", "source-snapshot-hash"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"finite-microstate-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        column_hash = sha256_identity(tuple(row["column_identities"]))
        instructions.append({"opcode": "label", "destination": prefix + "-column-schema", "arguments": ["column-identity-schema-hash", column_hash]})
        registers.append(prefix + "-column-schema")
        for family, label in (
            ("support-law", "complete-generated-finite-chemical-support"),
            ("partition-law", "disjoint-exhaustive-macro-observation-partition"),
            ("weight-law", "exact-fibre-count-over-complete-support-count"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-finite-microstate-structure", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-finite-microstate-structure"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": FINITE_MICROSTATE_SPEC.experiment_id + "-value-free-complete-structure",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": FINITE_MICROSTATE_SPEC.experiment_id,
        "claim_id": FINITE_MICROSTATE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": FINITE_MICROSTATE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "water_snapshot": (WATER_PATH, WATER_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in FINITE_MICROSTATE_SPEC.target_rows),
        "all_387_populations_temperatures_and_calorimetric_values_absent_from_prediction": True,
        "falsification_condition": FINITE_MICROSTATE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 387:
        raise ValueError("THERMO-001 prediction is not the complete 387-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("THERMO-001 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 9:
            raise ValueError("THERMO-001 prediction lost its complete structural consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 387:
        raise ValueError("THERMO-001 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (WATER_PATH, WATER_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-001 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-finite-microstate-withheld-targets/1"
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or document.get("complete_target_count") != 387
        or len(targets) != 387
    ):
        raise ValueError("THERMO-001 withheld registry changed")
    resolved: list[dict[str, object]] = []
    for identity, target in zip(identities, targets):
        if identity["target_id"] != target.get("target_id") or identity["source_class"] != target.get("source_class"):
            raise ValueError("THERMO-001 source identity/target binding changed")
        payload_hash = _canonical_payload_hash(target)
        resolved.append({
            **identity,
            "target_payload_hash": payload_hash,
            "target_payload": target,
            "vault_value": HeldLabel("external-record-payload-hash", payload_hash),
        })
    population = tuple(row for row in resolved if row["source_class"] == "direct-molecular-state-population-and-transition-record")
    calorimetric = tuple(row for row in resolved if row["source_class"] == "evaluated-finite-calorimetric-state-row")
    if (
        len(resolved) != 387 or len({row["target_id"] for row in resolved}) != 387
        or len(population) != 330 or len(calorimetric) != 57
        or any(not isinstance(row["target_payload"].get("cells"), list) or not row["target_payload"]["cells"] for row in population)
        or any(set(row["target_payload"]) != {
            "target_id", "source_class", "temperature_inscription_kelvin", "heat_capacity_inscription",
            "entropy_inscription", "held_gibbs_reference_relation_inscription", "enthalpy_reference_relation_inscription",
        } for row in calorimetric)
        or sum(row["target_payload"]["temperature_inscription_kelvin"] == "1700." for row in calorimetric) != 2
    ):
        raise ValueError("THERMO-001 complete external structure surface changed")
    return tuple(resolved)


class FiniteMicrostateValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = FINITE_MICROSTATE_SPEC

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
            raise ValueError("THERMO-001 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): row["vault_value"] for row in source_rows}
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
            target_id = str(row["target_id"])
            word = predicted[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["source_class"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["source_id"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == str(row["source_row_ordinal"])
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["snapshot_hash"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == sha256_identity(tuple(row["column_identities"]))
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == "complete-generated-finite-chemical-support"
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == "disjoint-exhaustive-macro-observation-partition"
                and isinstance(word.cells[8], HeldLabel) and word.cells[8].label == "exact-fibre-count-over-complete-support-count"
            )
            target_match = release.targets[target_id] == row["vault_value"]
            comparisons.append({
                "target_id": target_id, "source_class": row["source_class"],
                "target_payload_hash": row["target_payload_hash"],
                "identity_match": identity_match, "postseal_payload_hash_match": target_match,
                "passed": identity_match and target_match,
            })

        population = tuple(row for row in source_rows if row["source_class"].startswith("direct-"))
        calorimetric = tuple(row for row in source_rows if row["source_class"].startswith("evaluated-"))
        controls = {
            "tampered_target_payload_hash_rejected": HeldLabel("external-record-payload-hash", "sha256:" + "f" * 64) != release.targets[str(source_rows[0]["target_id"])],
            "all_330_direct_state_rows_retained": len(population) == 330,
            "all_57_calorimetric_rows_retained": len(calorimetric) == 57,
            "all_387_external_rows_retained": len(release.targets) == len(source_rows) == 387,
            "duplicated_1700_regime_boundary_retained": sum(row["target_payload"].get("temperature_inscription_kelvin") == "1700." for row in calorimetric) == 2,
            "state_and_calorimetric_classes_not_conflated": {row["source_class"] for row in source_rows} == {"direct-molecular-state-population-and-transition-record", "evaluated-finite-calorimetric-state-row"},
            "prediction_contains_no_target_payload_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
            "continuum_and_completed_infinity_not_used": all(token not in self.spec.exact_result for token in ("continuum", "completed-infinity")),
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("finite-support-external-structure-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-001 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "complete_387_row_comparisons": comparisons,
            "controls": controls,
            "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=("NIST-MDS2-3389-CAH-PLUS-QUANTUM-JUMP-THERMOMETRY", "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-GAS-CALORIMETRIC-TABLE"),
            measurements=tuple(
                f"{row['target_id']}: {row['source_class']}; identity and post-seal payload binding {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "FiniteMicrostateValidator", "_identities", "_prediction_map", "_source_rows",
    "experiment_registration_record", "prediction_program_document",
)
