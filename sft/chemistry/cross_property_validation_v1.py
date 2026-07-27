"""Post-seal complete 13-family cross-property validation for PROP-014."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform

from sft.chemistry.cross_property_batch_v1 import (
    CROSS_PROPERTY_SPEC, IDENTITY_HASH, IDENTITY_PATH, MANIFEST_HASH, MANIFEST_PATH,
    SUMMARY_HASH, SUMMARY_PATH, TARGET_HASH, TARGET_PATH,
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
        raise ValueError("PROP-014 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"source_target_payload", "source_target_payload_hash", "withheld_target_hash", "source_value_inscription", "native_value", "measurement_present", "external_measurement_absence"}
    if (
        document.get("schema") != "sft-v3-cross-property-identities/1"
        or document.get("complete_property_family_count") != 13
        or document.get("complete_source_identity_row_count") != 9025
        or document.get("complete_structural_carrier_count") != 1104
        or document.get("multi_property_structural_carrier_count") != 676
        or document.get("all_target_values_presence_flags_and_source_orientations_absent") is not True
        or len(rows) != 9025
        or any(row.get("target_value_presence_and_orientation_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-014 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Seal all 9,025 identities and shared-carrier projections without target hashes."""

    instructions: list[dict[str, object]] = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    fields = (
        ("structural_carrier_id", "structural-molecular-carrier"),
        ("property_family", "molecular-property-family"),
        ("property_label", "molecular-property-label"),
        ("source_target_id", "source-target-identity"),
        ("source_identity_hash", "source-identity-hash"),
        ("carrier_derivation_rule", "carrier-derivation-rule"),
        ("registered_property_family_count_for_carrier", "positive-property-family-count"),
        ("complete_registered_row_count_for_carrier", "positive-carrier-row-count"),
        ("cross_property_overlap", "cross-property-overlap-class"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"cross-property-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", str(row["cross_property_target_id"])]})
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("projection-law", "named-admitted-relation-projection"),
            ("parameter-law", "zero-parameter-shared-carrier-projection"),
            ("extension-law", "append-only-extension-preserves-existing-projections"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-cross-property-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-cross-property-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": CROSS_PROPERTY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": CROSS_PROPERTY_SPEC.experiment_id, "claim_id": CROSS_PROPERTY_SPEC.claim_id,
        "provenance": "observational_derivation", "frozen_relation": CROSS_PROPERTY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "identity_only_source_manifest": (MANIFEST_PATH, MANIFEST_HASH), "overlap_summary": (SUMMARY_PATH, SUMMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in CROSS_PROPERTY_SPEC.target_rows),
        "all_9025_target_payloads_hashes_presence_flags_and_orientations_absent_from_prediction": True,
        "falsification_condition": CROSS_PROPERTY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 9025:
        raise ValueError("PROP-014 prediction is not the complete 9,025-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-014 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13:
            raise ValueError("PROP-014 prediction lost its complete shared-carrier projection")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 9025:
        raise ValueError("PROP-014 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (MANIFEST_PATH, MANIFEST_HASH), (SUMMARY_PATH, SUMMARY_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-014 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-cross-property-withheld-targets/1"
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_seal") != IDENTITY_HASH
        or len(document.get("source_target_files_first_opened_after_identity_seal", ())) != 13
        or len(targets) != 9025
    ):
        raise ValueError("PROP-014 withheld registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["cross_property_target_id"] != target.get("cross_property_target_id")
            or identity["structural_carrier_id"] != target.get("structural_carrier_id")
            or identity["property_family"] != target.get("property_family")
            or identity["source_target_id"] != target.get("source_target_id")
            or _canonical_payload_hash(target.get("source_target_payload")) != target.get("source_target_payload_hash")
        ):
            raise ValueError("PROP-014 source identity/target binding changed")
        resolved.append({
            **identity,
            "source_target_payload": target["source_target_payload"],
            "source_target_payload_hash": target["source_target_payload_hash"],
            "vault_value": HeldLabel("source-target-payload-hash", str(target["source_target_payload_hash"])),
        })
    if (
        len(resolved) != 9025
        or len({row["cross_property_target_id"] for row in resolved}) != 9025
        or len({row["structural_carrier_id"] for row in resolved}) != 1104
        or len({row["structural_carrier_id"] for row in resolved if row["cross_property_overlap"]}) != 676
        or sum(bool(row["cross_property_overlap"]) for row in resolved) != 6676
        or len({row["property_family"] for row in resolved}) != 13
    ):
        raise ValueError("PROP-014 complete carrier/property partition changed")
    return tuple(resolved)


class CrossPropertyValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = CROSS_PROPERTY_SPEC

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
            raise ValueError("PROP-014 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)
        target_values = {str(row["cross_property_target_id"]): row["vault_value"] for row in source_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        comparisons = []
        for row in source_rows:
            target_id = str(row["cross_property_target_id"])
            word = predicted[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["structural_carrier_id"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["property_family"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["property_label"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["source_target_id"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["source_identity_hash"]
                and isinstance(word.cells[7], HeldLabel) and word.cells[7].label == str(row["registered_property_family_count_for_carrier"])
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == str(row["cross_property_overlap"])
            )
            target_match = release.targets[target_id] == row["vault_value"]
            comparisons.append({
                "cross_property_target_id": target_id, "structural_carrier_id": row["structural_carrier_id"],
                "property_family": row["property_family"], "source_target_id": row["source_target_id"],
                "source_target_payload_hash": row["source_target_payload_hash"],
                "identity_match": identity_match, "postseal_target_payload_hash_match": target_match,
                "passed": identity_match and target_match,
            })

        first = source_rows[0]
        tampered = HeldLabel("source-target-payload-hash", "sha256:" + "f" * 64)
        h2 = tuple(row for row in source_rows if row["structural_carrier_id"] == "exact-formula:H2")
        controls = {
            "tampered_target_payload_hash_rejected": tampered != release.targets[str(first["cross_property_target_id"])],
            "complete_13_property_families_retained": len({row["property_family"] for row in source_rows}) == 13,
            "complete_9025_source_rows_retained": len(release.targets) == len(source_rows) == 9025,
            "complete_1104_structural_carriers_retained": len({row["structural_carrier_id"] for row in source_rows}) == 1104,
            "all_676_multi_property_carriers_retained": len({row["structural_carrier_id"] for row in source_rows if row["cross_property_overlap"]}) == 676,
            "all_6676_overlap_rows_retained": sum(bool(row["cross_property_overlap"]) for row in source_rows) == 6676,
            "maximum_eight_family_H2_carrier_retained": len({row["property_family"] for row in h2}) == 8,
            "nonjoined_rows_not_guessed_into_formula_carriers": all(not str(row["structural_carrier_id"]).startswith("exact-formula:") for row in source_rows if row["carrier_derivation_rule"] in {"no-explicit-species-formula-in-registered-diatomic-PDF-cell", "source-species-label-not-formula-normalized", "bound-composite-not-conflated-with-constituent-molecule"}),
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("complete-shared-carrier-cross-property-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-014 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "complete_9025_row_comparisons": comparisons,
            "controls": controls, "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=tuple("SFT-V3-ADMITTED-PROP-" + f"{number:03d}" for number in range(1, 14)),
            measurements=tuple(f"{row['cross_property_target_id']}: {row['property_family']} on {row['structural_carrier_id']}; post-seal payload identity {row['passed']}" for row in comparisons) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = ("CrossPropertyValidator", "_identities", "_prediction_map", "_source_rows", "experiment_registration_record", "prediction_program_document")
