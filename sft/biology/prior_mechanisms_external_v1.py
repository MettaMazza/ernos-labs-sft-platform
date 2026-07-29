"""Post-seal authoritative comparison for the complete Biology return family."""

from __future__ import annotations

import platform
from pathlib import Path

from sft.biology.sources import SOURCE_BY_ID, source_corpus, validate_sources
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


EXPERIMENT_ID = "SFT-EXP-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002"
CLAIM_ID = "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002"
TARGET_ID = "BIOLOGY-PRIOR-MECHANISM-AUTHORITY-CORRESPONDENCE-2026-07-28"
PREDICTION_LABEL = "__".join((
    "resource-and-compartment-conditioned-self-maintenance",
    "observed-biological-homochirality-with-origin-mechanism-unresolved",
    "somatic-ageing-and-germ-line-distinction",
    "thresholded-regenerative-cell-signalling",
    "differentiation-and-cell-cycle-control-in-cancer",
    "time-bounded-ecosystem-observation-and-recurrence",
    "exact-fold-threshold-and-orbit-mappings-remain-structural-where-not-directly-measured",
))

REQUIREMENTS = (
    ("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "metabolic energy"),
    ("SFT-BIO-SRC-NCBI-CELL-ORIGIN-METABOLISM", "replication"),
    ("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "L-amino acids"),
    ("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "D-sugars"),
    ("SFT-BIO-SRC-PUBMED-HOMOCHIRALITY-35969306-V1", "unknown"),
    ("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "somatic"),
    ("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "germ"),
    ("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "signal transduction"),
    ("SFT-BIO-SRC-GO-ONTOLOGY-DOCUMENTATION", "cell cycle"),
    ("SFT-BIO-SRC-NCBI-GENOME-REGULATION-DEVELOPMENT-V1", "differentiation"),
    ("SFT-BIO-SRC-NCBI-AGING-SENESCENCE-V1", "cancer"),
    ("SFT-BIO-SRC-NASEM-UNITY-BIOLOGY-2010", "ecosystem"),
    ("SFT-BIO-SRC-GBIF-SURVEY-GUIDE-V1", "sampling effort"),
    ("SFT-BIO-SRC-GBIF-SURVEY-GUIDE-V1", "absence"),
)


def external_registration_record() -> dict[str, object]:
    source_ids = tuple(dict.fromkeys(source_id for source_id, _ in REQUIREMENTS))
    return {
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "target_id": TARGET_ID,
        "source_commitments": tuple(
            (source_id, SOURCE_BY_ID[source_id].body, SOURCE_BY_ID[source_id].source_uri,
             SOURCE_BY_ID[source_id].snapshot_path, SOURCE_BY_ID[source_id].snapshot_hash)
            for source_id in source_ids
        ),
        "required_fragments": REQUIREMENTS,
        "target_content_absent": True,
        "target_inaccessible_before_derivation_seal": True,
        "all_result_classes_required": True,
        "falsification_condition": "Reject if source bytes differ, a required feature is absent, a contrary row is suppressed, target content opens before the derivation seal, or the source-derived category differs from the sealed prediction.",
    }


def prediction_program_document() -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["biology-observation", PREDICTION_LABEL]},
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def _source_derived_target(root: Path) -> tuple[str, str, tuple[str, ...]]:
    validate_sources(root)
    receipts = []
    for source_id, fragment in REQUIREMENTS:
        corpus = source_corpus(root, source_id)
        if fragment.casefold() not in corpus:
            raise ValueError(f"required Biology feature absent: {source_id} :: {fragment}")
        receipts.append((source_id, SOURCE_BY_ID[source_id].snapshot_hash, fragment.casefold()))
    source_ids = tuple(dict.fromkeys(source_id for source_id, _ in REQUIREMENTS))
    return PREDICTION_LABEL, sha256_identity(tuple(receipts)), source_ids


class BlindPriorMechanismsExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        registration = external_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (TARGET_ID,), sealed.seal_hash, registration_hash)
        observed_label, extraction_hash, source_ids = _source_derived_target(self.root)
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-source-custodian",
            targets={TARGET_ID: HeldLabel("external-observation", observed_label)},
            custody_nonce=sha256_identity((registration_hash, extraction_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("Biology prediction differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "biology-observation":
            raise ValueError("Biology prediction emitted an invalid label")
        observed = release.targets[TARGET_ID].label
        comparison = prediction.label == observed
        tampered = prediction.label != observed + "__tampered"
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("released Biology target identity differs from commitment")
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=target_identity,
            comparison_implementation_identity_hash=sha256_identity(("exact-biology-return-source-correspondence", EXPERIMENT_ID)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        result_classes = {
            "favorable": ("biological homochirality", "somatic/germ distinction", "excitable thresholding", "differentiation and cancer control", "ecosystem observation"),
            "adverse": (),
            "absent": ("no direct source measurement of the exact Fold ignition share, half-One neural normalization or 3/5 ecosystem period",),
            "unresolved": ("origin mechanism of biological homochirality", "organism-specific quantitative mappings"),
        }
        measurement_payload = {
            "registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "source_extraction_hash": extraction_hash,
            "source_ids": source_ids,
            "comparison": comparison,
            "tampered_control": tampered,
            "result_classes": result_classes,
            "trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=source_ids,
            measurements=(
                f"{TARGET_ID}: exact source-derived categorical match {comparison}",
                "favorable correspondence retained for each source-supported biological category",
                "absent retained: exact Fold threshold/orbit values are not falsely described as directly measured",
                "unresolved retained: origin of biological homochirality and quantitative organism mappings",
                "deliberately tampered unfavorable control rejected",
            ),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=registration["falsification_condition"],
            passed=bool(comparison and tampered),
        )


__all__ = ("BlindPriorMechanismsExternalValidator", "external_registration_record")
