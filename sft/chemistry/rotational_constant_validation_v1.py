"""Post-seal complete NIST rotational-constant validation for Chemistry PROP-010."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re

from sft.chemistry.rotational_constant_batch_v1 import (
    CHOICE_SNAPSHOT_HASH,
    CHOICE_SNAPSHOT_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    LIST_SNAPSHOT_HASH,
    LIST_SNAPSHOT_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    ROTATIONAL_CONSTANT_SPEC,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
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
        self.parts: list[str] = []
        self.current: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "td":
            self.in_cell = True
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == "td" and self.in_cell:
            self.current.append(" ".join("".join(self.parts).split()))
            self.in_cell = False
        elif lowered == "tr":
            if self.current:
                self.rows.append(tuple(self.current))
            self.current = []


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-010 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "measurement_present", "rotational_constant_inscription_cm_inverse",
        "exact_positive_axis_recurrence_ratio_per_centimeter", "external_measurement_absence",
    }
    if (
        document.get("schema") != "sft-v3-rotational-constant-identities/1"
        or document.get("all_rotational_constant_values_absent") is not True
        or document.get("complete_displayed_molecular_row_count") != 1005
        or document.get("complete_row_count") != 3015
        or len(rows) != 3015
        or any(row.get("target_value_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-010 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"rotational-constant-axis-{ordinal}"
        target = prefix + "-target"
        instructions.append({"opcode": "label", "destination": target, "arguments": ["target-id", str(row["target_id"])]})
        registers = ["premise"]
        label_fields = (
            ("name", "molecular-name"),
            ("species", "molecular-species"),
            ("external_charge_inscription", "external-charge-inscription"),
            ("axis_label", "rotational-axis"),
            ("measurement_kind", "measurement-kind"),
            ("measurement_unit", "measurement-unit"),
            ("source_id", "source-identity"),
            ("source_locator", "source-locator"),
        )
        for number, (key, family) in enumerate(label_fields, start=1):
            destination = f"{prefix}-label-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for number, key in enumerate(("displayed_molecular_row", "displayed_axis_ordinal"), start=1):
            destination = f"{prefix}-count-{number}"
            instructions.append({"opcode": "count", "destination": destination, "arguments": [str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("source-uncertainty-status", "source-row-does-not-display-uncertainty"),
            ("geometry-law", "finite-generated-molecular-geometry-with-held-axis"),
            ("rotational-constant-law", "positive-axis-recurrence-count-over-positive-interval-count"),
            ("rotational-ladder-law", "positive-JJplusOne-level-with-adjacent-2J-gap"),
            ("measurement-absence-law", "blank-axis-cell-is-structural-EmptyOne"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        word = prefix + "-word"
        instructions.append({"opcode": "word", "destination": word, "arguments": registers})
        table_arguments.extend((target, word))
    instructions.extend((
        {"opcode": "table", "destination": "rotational-constant-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["rotational-constant-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ROTATIONAL_CONSTANT_SPEC.experiment_id + "-value-free-complete-axis-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": ROTATIONAL_CONSTANT_SPEC.experiment_id,
        "claim_id": ROTATIONAL_CONSTANT_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": ROTATIONAL_CONSTANT_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "complete_species_list_snapshot": (LIST_SNAPSHOT_PATH, LIST_SNAPSHOT_HASH),
        "complete_choice_snapshot": (CHOICE_SNAPSHOT_PATH, CHOICE_SNAPSHOT_HASH),
        "complete_result_snapshot": (SNAPSHOT_PATH, SNAPSHOT_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in ROTATIONAL_CONSTANT_SPEC.target_rows),
        "all_3015_rotational_values_absent_from_prediction": True,
        "falsification_condition": ROTATIONAL_CONSTANT_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 3015:
        raise ValueError("PROP-010 prediction is not the complete 3015-axis table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-010 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 16:
            raise ValueError("PROP-010 prediction lost complete geometry, axis and law custody")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 3015:
        raise ValueError("PROP-010 prediction duplicated a target identity")
    return resolved


def _snapshot_rows(root: Path) -> tuple[tuple[str, str, str, str, str, str], ...]:
    parser = _TableRows()
    parser.feed((root / SNAPSHOT_PATH).read_text(encoding="utf-8", errors="replace"))
    rows = []
    numeric = re.compile(r"[0-9]+(?:\.[0-9]+)?")
    for cells in parser.rows:
        if len(cells) != 6:
            continue
        name, charge, species, axis_a, axis_b, axis_c = cells
        if not name or not species or not re.fullmatch(r"-?[0-9]+", charge):
            continue
        if any(value and not numeric.fullmatch(value) for value in (axis_a, axis_b, axis_c)):
            raise ValueError("PROP-010 source contains a non-exact rotational inscription")
        rows.append((name, charge, species, axis_a, axis_b, axis_c))
    if len(rows) != 1005:
        raise ValueError(f"PROP-010 displayed molecular-row count changed: {len(rows)}")
    return tuple(rows)


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (LIST_SNAPSHOT_PATH, LIST_SNAPSHOT_HASH), (CHOICE_SNAPSHOT_PATH, CHOICE_SNAPSHOT_HASH),
        (SNAPSHOT_PATH, SNAPSHOT_HASH), (PRIMARY_PATH, PRIMARY_HASH), (TARGET_PATH, TARGET_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-010 registered source changed: {path}")
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(targets.get("rows", ()))
    if (
        primary.get("schema") != "sft-v3-nist-cccbdb-rotational-constant-primary-records/1"
        or primary.get("complete_listed_species_count") != 2186
        or primary.get("complete_unique_formula_composition_query_count") != 1193
        or primary.get("complete_returned_charge_state_choice_count") != 1832
        or primary.get("complete_listed_composition_without_returned_choice_count") != 83
        or primary.get("complete_displayed_molecular_row_count") != 1005
        or primary.get("complete_displayed_axis_cell_count") != 3015
        or primary.get("experimental_measurement_present_count") != 1681
        or primary.get("experimental_measurement_absent_count") != 1334
        or primary.get("all_rows_and_axis_absences_preserved") is not True
        or len(primary.get("retrieval_batches", ())) != 6
        or primary.get("rows") != list(rows)
        or targets.get("schema") != "sft-v3-rotational-constant-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("all_rows_and_axis_absences_preserved") is not True
        or targets.get("complete_row_count") != 3015
        or len(rows) != 3015
    ):
        raise ValueError("PROP-010 complete source surface changed")
    identities = _identities(root)
    snapshot_rows = _snapshot_rows(root)
    resolved = []
    for molecular_ordinal, source in enumerate(snapshot_rows, start=1):
        name, charge, species, axis_a, axis_b, axis_c = source
        for axis_ordinal, (axis, inscription) in enumerate(zip(("A", "B", "C"), (axis_a, axis_b, axis_c)), start=1):
            index = (molecular_ordinal - 1) * 3 + axis_ordinal - 1
            identity, row = identities[index], rows[index]
            present = bool(inscription)
            value = _pair(row["exact_positive_axis_recurrence_ratio_per_centimeter"]) if present else EMPTY_ONE
            if (
                identity.get("target_id") != row.get("target_id")
                or int(identity["displayed_molecular_row"]) != molecular_ordinal
                or int(identity["displayed_axis_ordinal"]) != axis_ordinal
                or identity.get("name") != name
                or identity.get("species") != species
                or identity.get("external_charge_inscription") != charge
                or identity.get("axis_label") != axis
                or row.get("measurement_present") is not present
                or row.get("rotational_constant_inscription_cm_inverse") != (inscription if present else None)
                or (present and (not isinstance(value, PositiveRatio) or value.fraction <= 0))
                or (not present and not isinstance(value, EmptyOne))
            ):
                raise ValueError(f"PROP-010 source reconstruction differs: {row.get('target_id')}")
            resolved.append({**row, "vault_value": value})
    return tuple(resolved)


class RotationalConstantValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ROTATIONAL_CONSTANT_SPEC

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
            raise ValueError("PROP-010 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)  # First rotational-value access: after prediction seal.
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
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["name"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["species"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["external_charge_inscription"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["axis_label"]
                and word.cells[9].value == row["displayed_molecular_row"]
                and word.cells[10].value == row["displayed_axis_ordinal"]
            )
            exact_target = released == row["vault_value"]
            comparisons.append({
                "target_id": target_id,
                "displayed_molecular_row": row["displayed_molecular_row"],
                "name": row["name"],
                "species": row["species"],
                "external_charge_inscription": row["external_charge_inscription"],
                "axis_label": row["axis_label"],
                "measurement_present": row["measurement_present"],
                "rotational_constant_inscription_cm_inverse": row["rotational_constant_inscription_cm_inverse"],
                "exact_positive_ratio_or_structural_EmptyOne": exact_target,
                "identity_match": identity_match,
                "passed": exact_target and identity_match,
            })
        first_value = next(row["vault_value"] for row in source_rows if isinstance(row["vault_value"], PositiveRatio))
        tampered = PositiveRatio.from_pair(first_value.numerator.value + first_value.denominator.value, first_value.denominator.value)
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        controls = {
            "tampered_rotational_constant_rejected": tampered != first_value,
            "tampered_blank_axis_rejected": PositiveRatio.from_pair(1, 1) != EMPTY_ONE,
            "complete_axis_support_preserved": len(source_rows) == 3015 and len({row["target_id"] for row in source_rows}) == 3015,
            "complete_molecular_row_support_preserved": len({row["displayed_molecular_row"] for row in source_rows}) == 1005,
            "measured_and_absent_axis_cells_preserved": sum(row["measurement_present"] for row in source_rows) == 1681 and sum(not row["measurement_present"] for row in source_rows) == 1334,
            "complete_list_choice_query_boundary_preserved": primary["complete_listed_species_count"] == 2186 and primary["complete_unique_formula_composition_query_count"] == 1193 and primary["complete_returned_charge_state_choice_count"] == 1832,
            "unreturned_composition_boundary_preserved": primary["complete_listed_composition_without_returned_choice_count"] == 83,
            "all_measured_values_exact_and_positive": all(isinstance(row["vault_value"], PositiveRatio) and row["vault_value"].fraction > 0 for row in source_rows if row["measurement_present"]),
            "all_blank_axis_values_structural_EmptyOne": all(isinstance(row["vault_value"], EmptyOne) for row in source_rows if not row["measurement_present"]),
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
            comparison_implementation_identity_hash=sha256_identity(("exact-NIST-rotational-constant-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-010 released target differs from commitment")
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
            data_source_ids=("NIST-CCCBDB-COMPLETE-ROTATIONAL-CONSTANT-SURFACE",),
            measurements=tuple(
                f"{row['target_id']}: {row['rotational_constant_inscription_cm_inverse'] if row['measurement_present'] else 'structural EmptyOne'} per centimeter; exact and axis-bound {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "RotationalConstantValidator", "_prediction_map", "_source_rows",
    "experiment_registration_record", "prediction_program_document",
)
