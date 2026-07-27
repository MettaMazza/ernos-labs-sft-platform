"""Post-seal complete NIST molecular magnetic-response validation for PROP-012."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.magnetic_response_batch_v1 import (
    DIATOMIC_HOLDINGS_HASH, DIATOMIC_HOLDINGS_PATH, DIATOMIC_PDF_HASH, DIATOMIC_PDF_PATH,
    DIATOMIC_TEXT_HASH, DIATOMIC_TEXT_PATH, HYDROCARBON_HOLDINGS_HASH, HYDROCARBON_HOLDINGS_PATH,
    IDENTITY_HASH, IDENTITY_PATH, MAGNETIC_RESPONSE_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    RESOLUTION_HASH, RESOLUTION_PATH, TARGET_HASH, TARGET_PATH,
    TRIATOMIC_HOLDINGS_HASH, TRIATOMIC_HOLDINGS_PATH,
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
        raise ValueError("PROP-012 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_orientation"}
    if (
        document.get("schema") != "sft-v3-magnetic-response-identities/1"
        or document.get("all_magnetic_values_and_orientations_absent") is not True
        or document.get("complete_target_count") != 174
        or len(rows) != 174
        or any(row.get("target_value_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-012 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"molecular-magnetic-response-{ordinal}"
        target = prefix + "-target"
        instructions.append({"opcode": "label", "destination": target, "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        label_fields = (
            ("source_id", "source-identity"), ("database", "molecular-database"),
            ("section", "source-section"), ("magnetic_parameter", "magnetic-parameter"),
            ("measurement_kind", "measurement-kind"), ("source_locator", "source-locator"),
        )
        for number, (key, family) in enumerate(label_fields, start=1):
            destination = f"{prefix}-label-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        identity_context = prefix + "-identity-context"
        instructions.append({
            "opcode": "label", "destination": identity_context,
            "arguments": ["source-identity-context", " | ".join(str(value) for value in row["identity_context"]) or "held-source-cell"],
        })
        registers.append(identity_context)
        for number, key in enumerate(("table_ordinal", "row_ordinal", "column_ordinal"), start=1):
            destination = f"{prefix}-count-{number}"
            # PDF table ordinal is an external absence glyph; native proof position remains a held label.
            if int(row[key]) < 1:
                instructions.append({"opcode": "label", "destination": destination, "arguments": ["source-position-absence", "structural-EmptyOne"]})
            else:
                instructions.append({"opcode": "count", "destination": destination, "arguments": [str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("orientation-law", "opposed-directions-are-held-labels"),
            ("closure-law", "balanced-support-is-structural-EmptyOne"),
            ("moment-law", "positive-response-per-positive-angular-recurrence"),
            ("susceptibility-law", "positive-induced-response-per-positive-field-act"),
            ("extension-law", "equal-repetition-preserves-exact-response-ratio"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        word = prefix + "-word"
        instructions.append({"opcode": "word", "destination": word, "arguments": registers})
        table_arguments.extend((target, word))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-magnetic-response-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-magnetic-response-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MAGNETIC_RESPONSE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": MAGNETIC_RESPONSE_SPEC.experiment_id,
        "claim_id": MAGNETIC_RESPONSE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": MAGNETIC_RESPONSE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_holdings": (
            (DIATOMIC_HOLDINGS_PATH, DIATOMIC_HOLDINGS_HASH),
            (TRIATOMIC_HOLDINGS_PATH, TRIATOMIC_HOLDINGS_HASH),
            (HYDROCARBON_HOLDINGS_PATH, HYDROCARBON_HOLDINGS_HASH),
        ),
        "diatomic_reference_pdf": (DIATOMIC_PDF_PATH, DIATOMIC_PDF_HASH),
        "diatomic_extracted_text": (DIATOMIC_TEXT_PATH, DIATOMIC_TEXT_HASH),
        "constants_page_resolution": (RESOLUTION_PATH, RESOLUTION_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MAGNETIC_RESPONSE_SPEC.target_rows),
        "all_174_values_presence_flags_and_orientations_absent_from_prediction": True,
        "quadrupole_chi_excluded_from_susceptibility_vector": True,
        "falsification_condition": MAGNETIC_RESPONSE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 174:
        raise ValueError("PROP-012 prediction is not the complete 174-cell table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-012 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 16:
            raise ValueError("PROP-012 prediction lost complete response custody")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 174:
        raise ValueError("PROP-012 prediction duplicated target identity")
    return resolved


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (PRIMARY_PATH, PRIMARY_HASH), (TARGET_PATH, TARGET_HASH),
        (DIATOMIC_PDF_PATH, DIATOMIC_PDF_HASH), (DIATOMIC_TEXT_PATH, DIATOMIC_TEXT_HASH),
        (RESOLUTION_PATH, RESOLUTION_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-012 registered source changed: {path}")
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    targets_document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    primary_rows = tuple(primary.get("rows", ()))
    target_rows = tuple(targets_document.get("rows", ()))
    identities = _identities(root)
    if (
        primary.get("complete_target_cell_count") != 174
        or primary.get("source_value_present_count") != 136
        or primary.get("source_value_absent_count") != 38
        or primary.get("diatomic_reference_pdf_target_count") != 22
        or targets_document.get("schema") != "sft-v3-magnetic-response-withheld-targets/1"
        or targets_document.get("release_requires_prediction_seal") is not True
        or targets_document.get("complete_target_count") != 174
        or {len(primary_rows), len(target_rows), len(identities)} != {174}
    ):
        raise ValueError("PROP-012 complete source surface changed")
    resolved: list[dict[str, object]] = []
    for identity, target, primary_row in zip(identities, target_rows, primary_rows):
        if not (identity["target_id"] == target["target_id"] == primary_row["target_id"]):
            raise ValueError("PROP-012 source order or identity changed")
        if (
            target.get("source_value_present") != primary_row.get("source_value_present")
            or target.get("source_value_inscription") != primary_row.get("source_value_inscription")
            or target.get("native_value") != primary_row.get("native_value")
        ):
            raise ValueError("PROP-012 withheld and primary values differ")
        native = target["native_value"]
        if target["source_value_present"]:
            value = _pair(native["exact_positive_magnitude"])
            orientation = str(native["external_orientation"])
            result_class = "exact-positive-molecular-magnetic-magnitude-with-held-source-orientation"
        else:
            value = EMPTY_ONE
            orientation = "source-orientation-absent-with-blank-cell"
            result_class = "blank-source-cell-structural-EmptyOne"
        resolved.append({**identity, **target, "vault_value": value, "source_orientation": orientation, "result_class": result_class})
    if (
        len(resolved) != 174
        or sum(isinstance(row["vault_value"], PositiveRatio) for row in resolved) != 136
        or sum(isinstance(row["vault_value"], EmptyOne) for row in resolved) != 38
        or any(
            "χ" in str(row["magnetic_parameter"])
            and any(unit in str(row["magnetic_parameter"]).casefold() for unit in ("mhz", "khz", "cm^-1"))
            for row in resolved
        )
    ):
        raise ValueError("PROP-012 positive/absence or susceptibility classification changed")
    return tuple(resolved)


class MagneticResponseValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MAGNETIC_RESPONSE_SPEC

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
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-012 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)  # First target-value and orientation access: post-seal.
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
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["source_id"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["database"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["section"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["magnetic_parameter"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["measurement_kind"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == row["source_locator"]
            )
            value_match = release.targets[target_id] == row["vault_value"]
            comparisons.append({
                "target_id": target_id,
                "magnetic_parameter": row["magnetic_parameter"],
                "source_value_inscription": row["source_value_inscription"],
                "source_orientation": row["source_orientation"],
                "result_class": row["result_class"],
                "identity_match": identity_match,
                "exact_magnitude_or_structural_absence_match": value_match,
                "passed": identity_match and value_match,
            })

        first_positive = next(row for row in source_rows if isinstance(row["vault_value"], PositiveRatio))
        first_blank = next(row for row in source_rows if isinstance(row["vault_value"], EmptyOne))
        tampered = PositiveRatio.from_pair(
            first_positive["vault_value"].numerator.value + first_positive["vault_value"].denominator.value,
            first_positive["vault_value"].denominator.value,
        )
        controls = {
            "tampered_magnitude_rejected": tampered != release.targets[str(first_positive["target_id"])],
            "blank_cell_is_structural_EmptyOne": isinstance(release.targets[str(first_blank["target_id"])], EmptyOne),
            "signed_source_orientation_not_negative_proof_number": all(
                isinstance(row["vault_value"], PositiveRatio)
                for row in source_rows if row["source_orientation"] == "source-opposed"
            ),
            "complete_174_cell_vector_retained": len(release.targets) == len(source_rows) == 174,
            "all_38_blank_cells_retained": sum(isinstance(row["vault_value"], EmptyOne) for row in source_rows) == 38,
            "complete_diatomic_pdf_vector_retained": sum(row["database"] == "diatomic-reference-pdf" for row in source_rows) == 22,
            "quadrupole_chi_frequency_tensors_excluded": not any(
                "χ" in str(row["magnetic_parameter"])
                and any(unit in str(row["magnetic_parameter"]).casefold() for unit in ("mhz", "khz", "cm^-1"))
                for row in source_rows
            ),
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("held-orientation-exact-magnetic-response-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-012 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "complete_174_cell_comparisons": comparisons,
            "controls": controls,
            "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(
                "NIST-MOLECULAR-MICROWAVE-SPECTRAL-DATABASES-SRD-114-115-117",
                "NIST-JPCRD-3-609-1974-DIATOMIC-MICROWAVE-SPECTRAL-TABLES",
            ),
            measurements=tuple(
                f"{row['target_id']}: {row['result_class']}; identity and exact post-seal result {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "MagneticResponseValidator", "_prediction_map", "_source_rows",
    "experiment_registration_record", "prediction_program_document",
)
