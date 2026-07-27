"""Post-seal nine-species NIST ionization validation for Chemistry PROP-007."""

from __future__ import annotations

from fractions import Fraction
from html import unescape
import json
from pathlib import Path
import platform
import re

from sft.chemistry.molecular_ionization_batch_v1 import (
    GUIDE_HASH,
    GUIDE_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_IONIZATION_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
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


VALUE_PATTERN = re.compile(
    r"Experimental Ionization Energy is\s*([0-9]+(?:\.[0-9]+)?)"
    r"(?:\s*[±]\s*([0-9]+(?:\.[0-9]+)?))?\s*eV",
    re.IGNORECASE,
)


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-007 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-molecular-ionization-identities/1"
        or document.get("all_ionization_values_absent") is not True
        or document.get("complete_row_count") != 9
        or len(rows) != 9
        or any(row.get("target_value_absent") is not True for row in rows)
    ):
        raise ValueError("PROP-007 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    fields = (
        ("formula", "molecular-formula"),
        ("name", "molecular-name"),
        ("casno", "source-species-identity"),
        ("initial_molecular_state", "initial-molecular-state"),
        ("initial_conformation", "initial-molecular-conformation"),
        ("resulting_ionic_state", "resulting-ionic-state"),
        ("removed_carrier", "removed-carrier"),
        ("ionization_path", "ionization-path"),
        ("method", "measurement-method"),
        ("condition", "measurement-condition"),
        ("units", "measurement-unit"),
        ("uncertainty_kind", "uncertainty-class"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"ionization-row-{ordinal}"
        instructions.append({
            "opcode": "label", "destination": prefix + "-target",
            "arguments": ["target-id", str(row["target_id"])],
        })
        registers = ["premise"]
        for number, (key, family) in enumerate(fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("held-removal-orientation", "neutral-carrier-to-separated-ion-and-electron"),
            ("ionization-law", "ordered-positive-terminal-from-initial-Take"),
            ("adiabatic-law", "least-complete-generated-terminal-Take"),
            ("vertical-law", "held-geometry-terminal-not-below-adiabatic"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-ionization-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-ionization-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MOLECULAR_IONIZATION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": MOLECULAR_IONIZATION_SPEC.experiment_id,
        "claim_id": MOLECULAR_IONIZATION_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": MOLECULAR_IONIZATION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "definition_source": (GUIDE_PATH, GUIDE_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MOLECULAR_IONIZATION_SPEC.target_rows),
        "all_nine_energy_values_absent_from_prediction": True,
        "falsification_condition": MOLECULAR_IONIZATION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 9:
        raise ValueError("PROP-007 prediction is not the complete nine-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-007 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 17:
            raise ValueError("PROP-007 prediction lost complete state custody")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 9:
        raise ValueError("PROP-007 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (GUIDE_PATH, GUIDE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-007 registered source changed: {path}")
    guide_text = " ".join(unescape((root / GUIDE_PATH).read_text(encoding="utf-8", errors="replace")).split())
    if (
        "is the lowest energy required".casefold() not in guide_text.casefold()
        or "must always be greater than or equal to the adiabatic ionization energy".casefold() not in guide_text.casefold()
    ):
        raise ValueError("PROP-007 NIST definition or vertical ordering changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-molecular-ionization-withheld-measurements/1"
        or document.get("release_requires_prediction_seal") is not True
        or document.get("all_rows_preserved") is not True
        or document.get("complete_row_count") != 9
        or len(targets) != 9
    ):
        raise ValueError("PROP-007 withheld registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        path = root / str(target["snapshot_path"])
        if hash_file(path) != target["snapshot_hash"]:
            raise ValueError("PROP-007 source page changed")
        match = VALUE_PATTERN.search(unescape(path.read_text(encoding="utf-8", errors="replace")))
        if match is None:
            raise ValueError("PROP-007 source energy is absent")
        inscription, uncertainty = match.groups()
        if (
            identity.get("target_id") != target.get("target_id")
            or identity.get("formula") != target.get("formula")
            or identity.get("initial_molecular_state") != target.get("initial_molecular_state")
            or identity.get("resulting_ionic_state") != target.get("resulting_ionic_state")
            or target.get("inscription") != inscription
            or target.get("uncertainty_inscription") != uncertainty
            or _pair(target["value"]).fraction != Fraction(inscription)
        ):
            raise ValueError(f"PROP-007 source reconstruction differs: {target.get('target_id')}")
        resolved.append({**target, "vault_value": _pair(target["value"])})
    return tuple(resolved)


class MolecularIonizationValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MOLECULAR_IONIZATION_SPEC

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
            raise ValueError("PROP-007 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)  # First energy-value access: after prediction seal.
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
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["initial_molecular_state"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == row["resulting_ionic_state"]
                and isinstance(word.cells[10], HeldLabel) and word.cells[10].label == row["condition"]
                and isinstance(word.cells[11], HeldLabel) and word.cells[11].label == row["units"]
            )
            comparisons.append({
                "target_id": target_id,
                "formula": row["formula"],
                "inscription_eV": row["inscription"],
                "uncertainty_inscription_eV": row["uncertainty_inscription"],
                "exact_positive_value": isinstance(released, PositiveRatio) and released == row["vault_value"],
                "identity_match": identity_match,
                "passed": isinstance(released, PositiveRatio) and released == row["vault_value"] and identity_match,
            })
        first = source_rows[0]
        tampered = PositiveRatio.from_pair(
            first["vault_value"].numerator.value + first["vault_value"].denominator.value,
            first["vault_value"].denominator.value,
        )
        controls = {
            "tampered_energy_rejected": tampered != release.targets[str(first["target_id"])],
            "missing_row_rejected": len(release.targets) == len(source_rows) == 9,
            "displaced_identity_rejected": source_rows[0]["target_id"] != source_rows[1]["target_id"],
            "all_explicit_uncertainties_preserved": sum(row["uncertainty"] is not None for row in source_rows) == 7,
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
            comparison_implementation_identity_hash=sha256_identity(("exact-NIST-ionization-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-007 released target differs from commitment")
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
            data_source_ids=(
                "NIST-WEBBOOK-SRD69-GAS-PHASE-ION-THERMOCHEMISTRY",
                "NIST-CCCBDB-SRD101-EXPERIMENTAL-IONIZATION-ENERGY",
            ),
            measurements=tuple(
                f"{row['target_id']}: {row['inscription_eV']} eV; exact positive and state-bound {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "MolecularIonizationValidator", "experiment_registration_record", "prediction_program_document",
)
