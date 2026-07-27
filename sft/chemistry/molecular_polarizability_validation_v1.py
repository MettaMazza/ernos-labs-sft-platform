"""Post-seal complete NIST molecular-polarizability validation for PROP-006."""

from __future__ import annotations

from fractions import Fraction
from html.parser import HTMLParser
import json
from pathlib import Path
import platform

from sft.chemistry.molecular_polarizability_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_POLARIZABILITY_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
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


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, ...]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        lowered = tag.casefold()
        if lowered == "tr":
            self._row = []
        elif lowered in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            normalized = " ".join(data.split())
            if normalized:
                self._cell.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell))
            self._cell = None
        elif lowered == "tr" and self._row is not None:
            if self._row:
                self.rows.append(tuple(self._row))
            self._row = None
            self._cell = None


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-006 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-molecular-polarizability-identities/1"
        or document.get("all_polarizability_values_absent") is not True
        or document.get("complete_molecular_row_count") != 252
        or len(rows) != 252
        or any(row.get("target_value_absent") is not True for row in rows)
    ):
        raise ValueError("PROP-006 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Seal every row identity and one exact relation without alpha values."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    identity_fields = (
        ("formula", "molecular-formula"),
        ("name", "molecular-name"),
        ("molecular_state", "molecular-state"),
        ("conformation", "molecular-conformation"),
        ("response_kind", "response-kind"),
        ("component_definition", "polarizability-definition"),
        ("method", "measurement-method"),
        ("condition", "measurement-condition"),
        ("units", "measurement-unit"),
        ("reference", "source-reference"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"polarizability-row-{ordinal}"
        instructions.append({
            "opcode": "label", "destination": prefix + "-target",
            "arguments": ["target-id", str(row["target_id"])],
        })
        registers = ["premise"]
        for number, (key, family) in enumerate(identity_fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({
                "opcode": "label", "destination": destination,
                "arguments": [family, str(row[key])],
            })
            registers.append(destination)
        comment_destination = prefix + "-comment"
        if str(row.get("comment", "")):
            instructions.append({
                "opcode": "label", "destination": comment_destination,
                "arguments": ["source-comment", str(row["comment"])],
            })
        else:
            instructions.append({
                "opcode": "empty_one", "destination": comment_destination,
                "arguments": ["structural-empty-One"],
            })
        registers.append(comment_destination)
        for family, label in (
            ("external-electric-distinction", "registered-positive-static-field-distinction"),
            ("response-law", "exact-induced-dipole-distinction-over-electric-distinction"),
            ("composition-law", "exact-one-third-Junction-of-three-held-axis-responses"),
            ("successor-law", "equal-field-acts-preserve-response-ratio"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-polarizability-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-polarizability-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MOLECULAR_POLARIZABILITY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": MOLECULAR_POLARIZABILITY_SPEC.experiment_id,
        "claim_id": MOLECULAR_POLARIZABILITY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": MOLECULAR_POLARIZABILITY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "official_snapshot": (SNAPSHOT_PATH, SNAPSHOT_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MOLECULAR_POLARIZABILITY_SPEC.target_rows),
        "all_252_alpha_values_absent_from_prediction": True,
        "falsification_condition": MOLECULAR_POLARIZABILITY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 252:
        raise ValueError("PROP-006 prediction is not the complete 252-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-006 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 16:
            raise ValueError("PROP-006 prediction lost a complete molecular response word")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 252:
        raise ValueError("PROP-006 prediction duplicates a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH),
        (SNAPSHOT_PATH, SNAPSHOT_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-006 registered source changed: {path}")
    identities = _identities(root)
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    target_rows = tuple(targets.get("rows", ()))
    if (
        targets.get("schema") != "sft-v3-molecular-polarizability-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("all_molecular_rows_preserved") is not True
        or targets.get("complete_molecular_row_count") != 252
        or len(target_rows) != 252
    ):
        raise ValueError("PROP-006 withheld registry changed")
    parser = _TableParser()
    parser.feed((root / SNAPSHOT_PATH).read_text(encoding="utf-8", errors="replace"))
    all_source = tuple(
        row for row in parser.rows
        if len(row) == 7 and row[0] != "Molecule" and row[4].replace(".", "", 1).isdigit()
    )
    molecular_source = tuple(row for row in all_source if not row[1].casefold().endswith(" atom"))
    if len(all_source) != 276 or len(molecular_source) != 252:
        raise ValueError("PROP-006 complete source support changed")
    resolved = []
    for ordinal, (identity, target, source) in enumerate(zip(identities, target_rows, molecular_source), start=1):
        formula, name, state, conformation, inscription, reference, comment = source
        target_id = f"NIST-CCCBDB-PROP-006-MOLECULAR-{ordinal:03d}"
        exact = Fraction(inscription)
        if (
            identity.get("target_id") != target_id
            or target.get("target_id") != target_id
            or identity.get("source_row_ordinal") != ordinal
            or target.get("source_row_ordinal") != ordinal
            or tuple(identity.get(key) for key in ("formula", "name", "molecular_state", "conformation", "reference", "comment"))
            != (formula, name, state, conformation, reference, comment)
            or tuple(target.get(key) for key in ("formula", "name", "molecular_state", "conformation", "reference", "comment", "inscription"))
            != (formula, name, state, conformation, reference, comment, inscription)
            or _pair(target["value"]).fraction != exact
        ):
            raise ValueError(f"PROP-006 source reconstruction differs: {target_id}")
        value = _pair(target["value"])
        resolved.append({**target, "vault_value": value})
    return tuple(resolved)


class MolecularPolarizabilityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MOLECULAR_POLARIZABILITY_SPEC

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
            raise ValueError("PROP-006 prediction package changed")
        predicted = _prediction_map(execution.output)

        # First alpha-value access occurs only after the complete relation and identity seal.
        source_rows = _source_rows(self.root)
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
            released = release.targets[target_id]
            if not isinstance(released, PositiveRatio):
                raise ValueError("PROP-006 released alpha is outside the exact positive domain")
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["formula"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["name"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["molecular_state"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["conformation"]
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == row["units"]
                and isinstance(word.cells[10], HeldLabel) and word.cells[10].label == row["reference"]
            )
            comparisons.append({
                "target_id": target_id,
                "source_row_ordinal": row["source_row_ordinal"],
                "formula": row["formula"],
                "state": row["molecular_state"],
                "conformation": row["conformation"],
                "inscription_angstrom_cubed": row["inscription"],
                "exact_positive_value": released == row["vault_value"],
                "identity_match": identity_match,
                "passed": released == row["vault_value"] and identity_match,
            })

        first = source_rows[0]
        tampered_value = PositiveRatio.from_pair(
            first["vault_value"].numerator.value + first["vault_value"].denominator.value,
            first["vault_value"].denominator.value,
        )
        controls = {
            "tampered_value_rejected": tampered_value != release.targets[str(first["target_id"])],
            "missing_row_rejected": len(release.targets) == len(source_rows) == 252,
            "displaced_identity_rejected": source_rows[0]["target_id"] != source_rows[1]["target_id"],
            "complete_reference_cohorts_retained": len({str(row["reference"]) for row in source_rows}) == 10,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
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
                    ("exact-positive-NIST-alpha-vector-and-identity-comparison", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-006 released target differs from commitment")
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
            "complete_252_row_comparisons": comparisons,
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
            data_source_ids=("NIST-CCCBDB-SRD101-EXPERIMENTAL-POLARIZABILITIES",),
            measurements=tuple(
                f"{row['target_id']}: {row['inscription_angstrom_cubed']} A^3; exact positive and identity-bound {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "MolecularPolarizabilityValidator", "experiment_registration_record",
    "prediction_program_document",
)
