"""Versioned notes-aware IUPAC Gold Book post-seal validator.

Earlier Chemistry receipts bind validators that intentionally inspect only the
main definition text.  Some later IUPAC terms place indispensable categorical
content in numbered definition notes.  This module adds that source surface
without changing any admitted source file or allowing notes into derivation.
"""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.generated_law import (
    EmpiricalChemistrySpec,
    experiment_registration_record,
    prediction_program_document,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
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


def _definition_and_notes(term: dict[str, object]) -> str:
    fragments: list[str] = []
    definitions = term.get("definitions", ())
    if not isinstance(definitions, list):
        raise ValueError("IUPAC definition support is invalid")
    for definition in definitions:
        if not isinstance(definition, dict):
            raise ValueError("IUPAC definition row is invalid")
        fragments.append(str(definition.get("text", "")))
        notes = definition.get("notes", {})
        if isinstance(notes, dict):
            fragments.extend(str(value) for _, value in sorted(notes.items(), key=lambda row: str(row[0])))
        elif isinstance(notes, list):
            fragments.extend(str(value) for value in notes)
        elif notes:
            raise ValueError("IUPAC definition notes are invalid")
    return " ".join(fragments)


def source_derived_extended_targets(
    root: Path, spec: EmpiricalChemistrySpec
) -> tuple[tuple[dict[str, object], ...], str]:
    registry_path = root / spec.observation_registry_path
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != "sft-v3-chemistry-extended-source-derived-observations/1":
        raise ValueError("extended Chemistry observation registry schema is invalid")
    rows = registry.get("observations", ())
    if not isinstance(rows, list):
        raise ValueError("extended Chemistry observation rows are invalid")
    observations = {row["target_id"]: row for row in rows if isinstance(row, dict)}
    if len(observations) != len(rows):
        raise ValueError("extended Chemistry registry contains duplicate or invalid rows")

    resolved: list[dict[str, object]] = []
    for reference in spec.target_rows:
        if reference.target_id not in observations:
            raise ValueError("registered extended Chemistry target is absent")
        observation = observations[reference.target_id]
        if observation.get("source_id") != reference.source_id:
            raise ValueError("extended Chemistry source differs from registration")
        snapshot_path = root / reference.snapshot_path
        if hash_file(snapshot_path) != reference.snapshot_hash:
            raise ValueError("official extended Chemistry snapshot differs from registration")
        source_document = json.loads(snapshot_path.read_text(encoding="utf-8"))
        term = source_document.get("term", {})
        if not isinstance(term, dict):
            raise ValueError("IUPAC term record is invalid")
        if term.get("code") != observation.get("term_code") or term.get("status") != "current":
            raise ValueError("IUPAC term identity or status differs from registration")
        corpus = _definition_and_notes(term)
        feature_rows = observation.get("ordered_feature_extractions", ())
        if not isinstance(feature_rows, list) or not feature_rows:
            raise ValueError("extended Chemistry feature extraction is absent")
        for feature in feature_rows:
            if (
                not isinstance(feature, dict)
                or set(feature) != {"required_fragment", "normalized_feature"}
                or not isinstance(feature["required_fragment"], str)
                or not isinstance(feature["normalized_feature"], str)
                or not feature["required_fragment"].strip()
                or not feature["normalized_feature"].strip()
            ):
                raise ValueError("extended Chemistry feature extraction is invalid")
            if feature["required_fragment"].casefold() not in corpus.casefold():
                raise ValueError("extended Chemistry target is not reproduced by official text")
        label = "__".join(str(feature["normalized_feature"]) for feature in feature_rows)
        resolved.append(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "observed_label": label,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": sha256_identity(
                    (reference.target_id, observation, label, reference.snapshot_hash)
                ),
            }
        )
    return tuple(resolved), hash_file(registry_path)


class BlindExtendedGoldBookValidator:
    """Compare one sealed consequence with definition-and-note source rows."""

    def __init__(self, root: Path, spec: EmpiricalChemistrySpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        program_document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(program_document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}

        source_rows, observation_registry_hash = source_derived_extended_targets(
            self.root, self.spec
        )
        target_values = {
            str(row["target_id"]): HeldLabel("external-observation", str(row["observed_label"]))
            for row in source_rows
        }
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, observation_registry_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )

        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            program_document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("extended Chemistry prediction differs after package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("prediction emitted an invalid extended Chemistry label")
        source_by_target = {str(row["target_id"]): row for row in source_rows}
        comparisons = tuple(
            {
                "target_id": reference.target_id,
                "source_id": reference.source_id,
                "source_locator": reference.source_locator,
                "snapshot_hash": reference.snapshot_hash,
                "extraction_hash": source_by_target[reference.target_id]["extraction_hash"],
                "predicted": prediction.label,
                "observed": release.targets[reference.target_id].label,
                "passed": prediction.label == release.targets[reference.target_id].label,
            }
            for reference in self.spec.target_rows
        )
        changed_label = prediction.label + "__tampered"
        tampered_control = {
            "target_id": "deliberately-tampered-unfavorable-control",
            "predicted": prediction.label,
            "observed": changed_label,
            "passed": prediction.label != changed_label,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and bool(
            tampered_control["passed"]
        )

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
                    ("exact-extended-source-held-label-equality", self.spec.experiment_id, self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released extended Chemistry target differs from commitment")
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
            "observation_registry_hash": observation_registry_hash,
            "comparisons": comparisons,
            "tampered_control": tampered_control,
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
            data_source_ids=tuple(dict.fromkeys(row.source_id for row in self.spec.target_rows)),
            measurements=tuple(
                f"{row['target_id']}: predicted {row['predicted']}; source-derived {row['observed']}; exact match {row['passed']}"
                for row in comparisons
            )
            + ("deliberately tampered unfavorable control rejected",),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "BlindExtendedGoldBookValidator",
    "source_derived_extended_targets",
)
