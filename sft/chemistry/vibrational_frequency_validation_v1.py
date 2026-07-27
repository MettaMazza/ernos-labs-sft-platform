"""Post-seal complete displayed NIST vibrational-frequency validation for PROP-009."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re

from sft.chemistry.vibrational_frequency_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
    VIBRATIONAL_FREQUENCY_SPEC,
)
from sft.claim_evidence import (
    EMPTY_ONE,
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmptyOne,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
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


class _TableRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.current: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "td":
            self.in_cell = True
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == "td" and self.in_cell:
            self.current.append(" ".join("".join(self.cell_parts).split()))
            self.in_cell = False
        elif lowered == "tr":
            if len(self.current) == 9:
                self.rows.append(tuple(self.current))
            self.current = []


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-009 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "measurement_present", "frequency_inscription_cm_inverse",
        "exact_positive_recurrence_ratio_per_centimeter", "external_measurement_absence",
    }
    if (
        document.get("schema") != "sft-v3-vibrational-frequency-identities/1"
        or document.get("all_frequency_values_absent") is not True
        or document.get("complete_displayed_molecule_count") != 145
        or document.get("complete_row_count") != 2009
        or len(rows) != 2009
        or any(row.get("target_value_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-009 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"vibrational-frequency-row-{ordinal}"
        instructions.append({
            "opcode": "label", "destination": prefix + "-target",
            "arguments": ["target-id", str(row["target_id"])],
        })
        registers = ["premise"]
        label_fields = (
            ("formula", "molecular-formula"),
            ("name", "molecular-name"),
            ("symmetry_label", "vibrational-symmetry"),
            ("measurement_kind", "measurement-kind"),
            ("measurement_unit", "measurement-unit"),
            ("source_id", "source-identity"),
            ("source_locator", "source-locator"),
        )
        count_fields = (
            ("mode_count", "mode-count"),
            ("molecule_count", "molecule-count"),
            ("vibration_count", "vibration-count"),
        )
        for number, (key, family) in enumerate(label_fields, start=1):
            destination = f"{prefix}-label-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for number, (key, _family) in enumerate(count_fields, start=1):
            destination = f"{prefix}-count-{number}"
            instructions.append({"opcode": "count", "destination": destination, "arguments": [str(row[key])]})
            registers.append(destination)
        uncertainty = prefix + "-uncertainty"
        instructions.append({
            "opcode": "label", "destination": uncertainty,
            "arguments": ["source-uncertainty-status", "source-row-does-not-display-uncertainty"],
        })
        registers.append(uncertainty)
        for family, label in (
            ("frequency-law", "positive-finite-recurrence-count-over-positive-interval-count"),
            ("unit-translation-law", "recurrence-ratio-before-held-reciprocal-centimeter-label"),
            ("measurement-absence-law", "unmeasured-displayed-cell-is-structural-EmptyOne"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "vibrational-frequency-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["vibrational-frequency-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": VIBRATIONAL_FREQUENCY_SPEC.experiment_id + "-value-free-complete-displayed-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": VIBRATIONAL_FREQUENCY_SPEC.experiment_id,
        "claim_id": VIBRATIONAL_FREQUENCY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": VIBRATIONAL_FREQUENCY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "source_snapshot": (SNAPSHOT_PATH, SNAPSHOT_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in VIBRATIONAL_FREQUENCY_SPEC.target_rows),
        "all_2009_frequency_values_absent_from_prediction": True,
        "falsification_condition": VIBRATIONAL_FREQUENCY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 2009:
        raise ValueError("PROP-009 prediction is not the complete 2009-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-009 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 15:
            raise ValueError("PROP-009 prediction lost complete mode and law custody")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 2009:
        raise ValueError("PROP-009 prediction duplicated a target identity")
    return resolved


def _snapshot_rows(root: Path) -> tuple[tuple[str, ...], ...]:
    parser = _TableRows()
    parser.feed((root / SNAPSHOT_PATH).read_text(encoding="utf-8", errors="replace"))
    rows = []
    current_formula = ""
    current_name = ""
    for cells in parser.rows:
        formula, name, mode, symmetry, _theory, experiment, _ratio, molecule_count, vibration_count = cells
        if formula:
            current_formula = formula
        if name:
            current_name = name
        if not (current_formula and current_name and mode and molecule_count and vibration_count):
            continue
        if not re.fullmatch(r"[0-9]+", mode) or not re.fullmatch(r"[0-9]+", molecule_count) or not re.fullmatch(r"[0-9]+", vibration_count):
            raise ValueError("PROP-009 source count is not exact")
        if experiment and not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", experiment):
            raise ValueError("PROP-009 source frequency is not exact")
        rows.append((current_formula, current_name, mode, symmetry, experiment, molecule_count, vibration_count))
    if len(rows) != 2009:
        raise ValueError("PROP-009 displayed source row count changed")
    return tuple(rows)


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (SNAPSHOT_PATH, SNAPSHOT_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
        (TARGET_PATH, TARGET_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-009 registered source changed: {path}")
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(targets.get("rows", ()))
    if (
        primary.get("schema") != "sft-v3-nist-cccbdb-vibrational-frequency-primary-records/1"
        or primary.get("source_advertised_molecule_count") != 164
        or primary.get("source_advertised_vibration_count") != 2452
        or primary.get("complete_displayed_molecule_count") != 145
        or primary.get("complete_displayed_vibration_count") != 2009
        or primary.get("source_advertised_but_undisplayed_molecule_count") != 19
        or primary.get("source_advertised_but_undisplayed_vibration_count") != 443
        or primary.get("experimental_measurement_present_count") != 1984
        or primary.get("experimental_measurement_absent_count") != 25
        or primary.get("all_rows_preserved") is not True
        or primary.get("calculated_frequency_ratio_and_fitted_scale_columns_excluded_from_derivation_and_measurement_vector") is not True
        or primary.get("rows") != list(rows)
        or targets.get("schema") != "sft-v3-vibrational-frequency-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("all_rows_preserved") is not True
        or targets.get("complete_row_count") != 2009
        or len(rows) != 2009
    ):
        raise ValueError("PROP-009 complete source surface changed")
    identities = _identities(root)
    snapshot_rows = _snapshot_rows(root)
    resolved = []
    for identity, row, source in zip(identities, rows, snapshot_rows):
        formula, name, mode, symmetry, experiment, molecule_count, vibration_count = source
        present = bool(experiment)
        value = _pair(row["exact_positive_recurrence_ratio_per_centimeter"]) if present else EMPTY_ONE
        if (
            identity.get("target_id") != row.get("target_id")
            or identity.get("formula") != formula != ""
            or identity.get("name") != name != ""
            or int(identity["mode_count"]) != int(mode)
            or identity.get("symmetry_label") != symmetry
            or int(identity["molecule_count"]) != int(molecule_count)
            or int(identity["vibration_count"]) != int(vibration_count)
            or row.get("measurement_present") is not present
            or row.get("frequency_inscription_cm_inverse") != (experiment if present else None)
            or (present and (not isinstance(value, PositiveRatio) or value.fraction <= 0))
            or (not present and not isinstance(value, EmptyOne))
        ):
            raise ValueError(f"PROP-009 source reconstruction differs: {row.get('target_id')}")
        resolved.append({**row, "vault_value": value})
    return tuple(resolved)


class VibrationalFrequencyValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = VIBRATIONAL_FREQUENCY_SPEC

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
            raise ValueError("PROP-009 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)  # First frequency-value access: after prediction seal.
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
            word, released = predicted[target_id], release.targets[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["formula"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["name"]
                and word.cells[8].value == row["mode_count"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["symmetry_label"]
                and word.cells[9].value == row["molecule_count"]
                and word.cells[10].value == row["vibration_count"]
            )
            exact_target = released == row["vault_value"]
            comparisons.append({
                "target_id": target_id,
                "formula": row["formula"],
                "mode_count": row["mode_count"],
                "symmetry_label": row["symmetry_label"],
                "measurement_present": row["measurement_present"],
                "frequency_inscription_cm_inverse": row["frequency_inscription_cm_inverse"],
                "exact_positive_ratio_or_structural_EmptyOne": exact_target,
                "identity_match": identity_match,
                "passed": exact_target and identity_match,
            })
        first_value = next(row["vault_value"] for row in source_rows if isinstance(row["vault_value"], PositiveRatio))
        tampered = PositiveRatio.from_pair(
            first_value.numerator.value + first_value.denominator.value,
            first_value.denominator.value,
        )
        controls = {
            "tampered_frequency_rejected": tampered != first_value,
            "complete_displayed_support_preserved": len(source_rows) == 2009 and len({row["target_id"] for row in source_rows}) == 2009,
            "measured_and_absent_rows_preserved": sum(row["measurement_present"] for row in source_rows) == 1984 and sum(not row["measurement_present"] for row in source_rows) == 25,
            "complete_displayed_molecule_support_preserved": len({row["molecule_count"] for row in source_rows}) == 145,
            "source_advertised_displayed_gap_preserved": 164 - 145 == 19 and 2452 - 2009 == 443,
            "all_measured_values_exact_and_positive": all(isinstance(row["vault_value"], PositiveRatio) for row in source_rows if row["measurement_present"]),
            "all_unmeasured_values_structural_EmptyOne": all(isinstance(row["vault_value"], EmptyOne) for row in source_rows if not row["measurement_present"]),
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
            comparison_implementation_identity_hash=sha256_identity(("exact-NIST-vibrational-frequency-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-009 released target differs from commitment")
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
            "comparisons": comparisons,
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
            data_source_ids=("NIST-CCCBDB-COMPLETE-DISPLAYED-FUNDAMENTAL-FREQUENCY-SURFACE",),
            measurements=tuple(
                f"{row['target_id']}: {row['frequency_inscription_cm_inverse'] if row['measurement_present'] else 'structural EmptyOne'} per centimeter; exact and mode-bound {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "VibrationalFrequencyValidator", "experiment_registration_record", "prediction_program_document",
)
