"""Post-seal complete NIST molecular electron-affinity validation for PROP-008."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import platform
import re

from sft.chemistry.molecular_electron_affinity_batch_v1 import (
    CATALOG_HASH,
    CATALOG_PATH,
    GUIDE_HASH,
    GUIDE_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_ELECTRON_AFFINITY_SPEC,
    PAGE_MANIFEST_HASH,
    PAGE_MANIFEST_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
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


VALUE_PATTERN = re.compile(
    r"Experimental Electron Affinity is\s*([+-]?)([0-9]+(?:\.[0-9]+)?)"
    r"(?:\s*(?:&plusmn;|±)\s*([0-9]+(?:\.[0-9]+)?))?\s*eV",
    re.IGNORECASE,
)


def _pair(value: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(value["numerator"]), int(value["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-008 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "source_orientation_glyph", "fold_state_order_orientation", "magnitude_inscription",
        "exact_positive_magnitude", "uncertainty_inscription", "exact_positive_uncertainty",
        "display_magnitude_lower", "display_magnitude_upper",
    }
    if (
        document.get("schema") != "sft-v3-molecular-electron-affinity-identities/1"
        or document.get("all_values_and_state_order_orientations_absent") is not True
        or document.get("complete_row_count") != 96
        or len(rows) != 96
        or any(
            row.get("target_value_and_orientation_absent") is not True or forbidden.intersection(row)
            for row in rows
        )
    ):
        raise ValueError("PROP-008 value-and-orientation-free identity boundary changed")
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
        ("resulting_anion_state", "resulting-anion-state"),
        ("gained_carrier", "gained-carrier"),
        ("gain_path", "electron-gain-path"),
        ("condition", "measurement-condition"),
        ("units", "measurement-unit"),
        ("source_id", "source-identity"),
        ("source_locator", "source-locator"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"electron-affinity-row-{ordinal}"
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
            ("held-gain-orientation", "neutral-plus-one-electron-to-retained-anion"),
            ("affinity-state-law", "held-order-and-positive-higher-Take-lower"),
            ("affinity-absence-law", "coincident-state-distinction-is-structural-EmptyOne"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "molecular-electron-affinity-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["molecular-electron-affinity-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MOLECULAR_ELECTRON_AFFINITY_SPEC.experiment_id + "-value-and-orientation-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": MOLECULAR_ELECTRON_AFFINITY_SPEC.experiment_id,
        "claim_id": MOLECULAR_ELECTRON_AFFINITY_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": MOLECULAR_ELECTRON_AFFINITY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_measurement_registry": (TARGET_PATH, TARGET_HASH),
        "catalog_source": (CATALOG_PATH, CATALOG_HASH),
        "definition_source": (GUIDE_PATH, GUIDE_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "value_free_source_page_manifest": (PAGE_MANIFEST_PATH, PAGE_MANIFEST_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MOLECULAR_ELECTRON_AFFINITY_SPEC.target_rows),
        "all_96_values_and_state_order_orientations_absent_from_prediction": True,
        "falsification_condition": MOLECULAR_ELECTRON_AFFINITY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 96:
        raise ValueError("PROP-008 prediction is not the complete 96-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-008 prediction lost target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 15:
            raise ValueError("PROP-008 prediction lost complete carrier and law custody")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 96:
        raise ValueError("PROP-008 prediction duplicated a target identity")
    return resolved


def _target_word(row: dict[str, object]) -> FoldWord:
    uncertainty = row.get("exact_positive_uncertainty")
    return FoldWord((
        HeldLabel("electron-affinity-state-order", str(row["fold_state_order_orientation"])),
        _pair(row["exact_positive_magnitude"]),
        _pair(uncertainty) if isinstance(uncertainty, dict) else EMPTY_ONE,
    ))


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (CATALOG_PATH, CATALOG_HASH),
        (GUIDE_PATH, GUIDE_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
        (PAGE_MANIFEST_PATH, PAGE_MANIFEST_HASH),
        (TARGET_PATH, TARGET_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-008 registered source changed: {path}")
    catalog_text = " ".join(unescape((root / CATALOG_PATH).read_text(encoding="utf-8", errors="replace")).split())
    guide_text = " ".join(unescape((root / GUIDE_PATH).read_text(encoding="utf-8", errors="replace")).split())
    if (
        "By convention a positive electron affinity indicates a bound species".casefold() not in catalog_text.casefold()
        or "negative ion is higher in energy than the neutral".casefold() not in guide_text.casefold()
        or "spontaneous loss of the electron".casefold() not in guide_text.casefold()
    ):
        raise ValueError("PROP-008 NIST definition or state-order boundary changed")
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    page_manifest = json.loads((root / PAGE_MANIFEST_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(targets.get("rows", ()))
    pages = tuple(primary.get("molecular_pages", ()))
    if (
        primary.get("schema") != "sft-v3-nist-cccbdb-molecular-electron-affinity-primary-records/1"
        or primary.get("catalog_row_count") != 192
        or primary.get("atomic_rows_excluded_by_value_free_formula_structure") != 30
        or primary.get("molecular_catalog_row_count") != 162
        or primary.get("molecular_rows_with_explicit_experimental_ea") != 96
        or primary.get("all_catalog_pages_preserved") is not True
        or len(pages) != 162
        or primary.get("rows") != list(rows)
        or page_manifest.get("schema") != "sft-v3-molecular-electron-affinity-source-page-manifest/1"
        or page_manifest.get("catalog_row_count") != 192
        or page_manifest.get("atomic_rows_excluded") != 30
        or page_manifest.get("molecular_page_count") != 162
        or page_manifest.get("all_measurement_values_and_orientations_absent") is not True
        or page_manifest.get("pages") != list(pages)
        or targets.get("schema") != "sft-v3-molecular-electron-affinity-withheld-measurements/1"
        or targets.get("release_requires_prediction_seal") is not True
        or targets.get("all_rows_preserved") is not True
        or targets.get("complete_row_count") != 96
        or len(rows) != 96
    ):
        raise ValueError("PROP-008 complete source surface changed")
    for page in pages:
        if hash_file(root / str(page["snapshot_path"])) != page["snapshot_hash"]:
            raise ValueError("PROP-008 molecular source page changed")
    identities = _identities(root)
    resolved = []
    for identity, row in zip(identities, rows):
        path = root / str(row["snapshot_path"])
        match = VALUE_PATTERN.search(unescape(path.read_text(encoding="utf-8", errors="replace")))
        if match is None:
            raise ValueError("PROP-008 source affinity is absent")
        sign, magnitude, uncertainty = match.groups()
        orientation = "anion-above-neutral-unbound-autodetachment" if sign == "-" else "anion-below-neutral-bound-attachment"
        if (
            identity.get("target_id") != row.get("target_id")
            or identity.get("formula") != row.get("formula")
            or identity.get("initial_molecular_state") != row.get("initial_molecular_state")
            or identity.get("resulting_anion_state") != row.get("resulting_anion_state")
            or row.get("magnitude_inscription") != magnitude
            or row.get("uncertainty_inscription") != uncertainty
            or row.get("fold_state_order_orientation") != orientation
            or _pair(row["exact_positive_magnitude"]).fraction <= 0
        ):
            raise ValueError(f"PROP-008 source reconstruction differs: {row.get('target_id')}")
        resolved.append({**row, "vault_word": _target_word(row)})
    return tuple(resolved)


class MolecularElectronAffinityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MOLECULAR_ELECTRON_AFFINITY_SPEC

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
            raise ValueError("PROP-008 prediction package changed")
        predicted = _prediction_map(execution.output)

        source_rows = _source_rows(self.root)  # First target orientation and magnitude access: after prediction seal.
        target_values = {str(row["target_id"]): row["vault_word"] for row in source_rows}
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
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["casno"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["initial_molecular_state"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["resulting_anion_state"]
                and isinstance(word.cells[8], HeldLabel) and word.cells[8].label == row["condition"]
                and isinstance(word.cells[9], HeldLabel) and word.cells[9].label == row["units"]
            )
            exact_target = isinstance(released, FoldWord) and released == row["vault_word"]
            comparisons.append({
                "target_id": target_id,
                "formula": row["formula"],
                "source_orientation_glyph": row["source_orientation_glyph"],
                "fold_state_order_orientation": row["fold_state_order_orientation"],
                "magnitude_inscription_eV": row["magnitude_inscription"],
                "uncertainty_inscription_eV": row["uncertainty_inscription"],
                "exact_positive_or_EmptyOne_representation": exact_target,
                "identity_match": identity_match,
                "passed": exact_target and identity_match,
            })
        first = source_rows[0]
        first_word = first["vault_word"]
        first_magnitude = first_word.cells[1]
        tampered_magnitude = PositiveRatio.from_pair(
            first_magnitude.numerator.value + first_magnitude.denominator.value,
            first_magnitude.denominator.value,
        )
        controls = {
            "tampered_magnitude_rejected": tampered_magnitude != first_magnitude,
            "flipped_orientation_rejected": HeldLabel("electron-affinity-state-order", "anion-above-neutral-unbound-autodetachment") != first_word.cells[0],
            "complete_catalog_and_molecular_pages_preserved": len(source_rows) == 96,
            "all_bound_and_unbound_rows_preserved": sum(row["fold_state_order_orientation"].startswith("anion-below") for row in source_rows) == 93 and sum(row["fold_state_order_orientation"].startswith("anion-above") for row in source_rows) == 3,
            "all_explicit_uncertainties_preserved": sum(row["uncertainty_inscription"] is not None for row in source_rows) == 89,
            "source_minus_glyphs_are_not_negative_numbers": all(isinstance(row["vault_word"].cells[1], PositiveRatio) for row in source_rows),
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
            comparison_implementation_identity_hash=sha256_identity(("exact-NIST-molecular-electron-affinity-vector", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-008 released target differs from commitment")
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
                "NIST-CCCBDB-COMPLETE-ELECTRON-AFFINITY-CATALOG",
                "NIST-CCCBDB-EXPERIMENTAL-MOLECULAR-ELECTRON-AFFINITY",
                "NIST-WEBBOOK-SRD69-GAS-PHASE-ION-THERMOCHEMISTRY",
            ),
            measurements=tuple(
                f"{row['target_id']}: source {row['source_orientation_glyph']} glyph, {row['magnitude_inscription_eV']} eV positive magnitude, {row['fold_state_order_orientation']}; exact state-bound {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "MolecularElectronAffinityValidator", "experiment_registration_record", "prediction_program_document",
)
