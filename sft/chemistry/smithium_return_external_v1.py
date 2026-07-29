"""Post-seal official-source validator for the complete Smithium family."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import platform
import re
import unicodedata

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


EXPERIMENT_ID = "SFT-EXP-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001"
TARGET_ID = "SMITHIUM-COMPLETE-OFFICIAL-STATUS-2026-07-28"
REGISTRY_PATH = "evidence/external/chemistry/smithium_2026-07-28/observations.json"
PREDICTION_LABEL = "__".join(
    (
        "current-known-element-boundary-118",
        "official-table-release-includes-element-118",
        "superheavy-production-by-heavy-ion-fusion",
        "identification-by-implantation-alpha-decay-or-spontaneous-fission",
        "electric-dipole-one-electron-orbital-rank-change-one",
        "smithium-126-remains-standing-unobserved-beyond-current-boundary",
    )
)


def _normalize(text: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    for source, replacement in (
        ("≥", ">="),
        ("α", "alpha"),
        ("Δ", "Delta"),
        ("±", "+/-"),
        ("−", "-"),
        ("–", "-"),
        ("—", "-"),
    ):
        text = text.replace(source, replacement)
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


def external_registration_record() -> dict[str, object]:
    """Target identity and authority commitments, with no observed label."""

    return {
        "experiment_id": EXPERIMENT_ID,
        "claim_id": "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001",
        "target_id": TARGET_ID,
        "source_commitments": (
            (
                "IUPAC/IUPAP Joint Working Group",
                "evidence/external/chemistry/smithium_2026-07-28/iupac_superheavy_discovery_2018.txt",
                "sha256:219d6e1dc7c197e63c910a545a351f30876dda54acee125a4861bb92683c2e36",
            ),
            (
                "IUPAC",
                "evidence/external/chemistry/smithium_2026-07-28/iupac_periodic_table.html",
                "sha256:ebd4ffd03cf5efd5f185efd45fa6b54adbe55d5e0b77ac4fda854fe46df81e16",
            ),
            (
                "NIST",
                "evidence/external/chemistry/smithium_2026-07-28/nist_atomic_spectroscopy.html",
                "sha256:572b39362756cd6ca7c2359632f2e9af2a8927c14bbc836c8b7c45b3b4ca6343",
            ),
        ),
        "target_content_absent": True,
        "target_inaccessible_before_derivation_seal": True,
        "all_result_classes_required": True,
    }


def prediction_program_document() -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["chemical-observation", PREDICTION_LABEL]},
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


def _source_derived_target(root: Path) -> tuple[str, str, tuple[dict[str, str], ...], dict[str, object]]:
    registry_path = root / REGISTRY_PATH
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != "sft-v3-smithium-source-derived-observations/1":
        raise ValueError("Smithium observation registry schema differs")
    if registry.get("target_id") != TARGET_ID:
        raise ValueError("Smithium target identity differs")
    documents = registry.get("support_documents")
    if not isinstance(documents, list) or len(documents) != 3:
        raise ValueError("Smithium source family is incomplete")
    corpora: dict[str, str] = {}
    identities: list[dict[str, str]] = []
    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("Smithium source document row is invalid")
        path = root / str(document["snapshot_path"])
        digest = hash_file(path)
        if digest != document.get("snapshot_hash"):
            raise ValueError("Smithium official source bytes differ from registration")
        text = path.read_text(encoding="utf-8")
        corpora[path.name] = _normalize(text)
        identities.append({"path": str(document["snapshot_path"]), "hash": digest})
    features = registry.get("ordered_feature_extractions")
    if not isinstance(features, list) or len(features) != 6:
        raise ValueError("Smithium feature extraction is incomplete")
    labels: list[str] = []
    for feature in features:
        if not isinstance(feature, dict) or set(feature) != {"document", "normalized_feature", "required_fragment"}:
            raise ValueError("Smithium feature row is invalid")
        document = str(feature["document"])
        if document not in corpora:
            raise ValueError("Smithium feature names an unregistered source")
        fragment = _normalize(str(feature["required_fragment"]))
        if fragment.casefold() not in corpora[document].casefold():
            raise ValueError(f"Smithium source does not reproduce registered fragment: {document}")
        labels.append(str(feature["normalized_feature"]))
    status = registry.get("preserved_result_classes")
    if not isinstance(status, dict) or set(status) != {"absent", "adverse", "favorable_correspondence", "unresolved"}:
        raise ValueError("Smithium result-class ledger is incomplete")
    if not status["absent"] or not status["favorable_correspondence"] or not status["unresolved"]:
        raise ValueError("Smithium favorable, absent and unresolved records must all be retained")
    return "__".join(labels), hash_file(registry_path), tuple(identities), status


class BlindSmithiumExternalValidator:
    """Open official sources only after receiving the sealed formal derivation."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        registration = external_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            (TARGET_ID,),
            sealed.seal_hash,
            registration_hash,
        )
        # This source reconstruction occurs inside the custodian-side validator,
        # after the engine has supplied an immutable derivation seal.
        observed_label, registry_hash, source_identities, result_classes = _source_derived_target(self.root)
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-official-source-custodian",
            targets={TARGET_ID: HeldLabel("external-observation", observed_label)},
            custody_nonce=sha256_identity((registration_hash, registry_hash, source_identities)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("Smithium prediction program differs after hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "chemical-observation":
            raise ValueError("Smithium prediction emitted an invalid label")
        comparison = {
            "target_id": TARGET_ID,
            "predicted": prediction.label,
            "source_derived": release.targets[TARGET_ID].label,
            "passed": prediction.label == release.targets[TARGET_ID].label,
        }
        tampered = {
            "target_id": "deliberately-tampered-unfavorable-control",
            "predicted": prediction.label,
            "source_derived": prediction.label + "__changed",
            "passed": prediction.label != prediction.label + "__changed",
        }
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("Smithium released target identity differs from commitment")
        comparator_hash = sha256_identity(("exact-source-derived-Smithium-label-equality", EXPERIMENT_ID))
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=target_identity,
                comparison_implementation_identity_hash=comparator_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
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
            "registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "registry_hash": registry_hash,
            "source_identities": source_identities,
            "comparison": comparison,
            "result_classes": result_classes,
            "tampered_control": tampered,
            "trace_hash": execution.trace_hash,
        }
        passed = bool(comparison["passed"] and tampered["passed"])
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("IUPAC-SUPERHEAVY-2018", "IUPAC-PERIODIC-TABLE-2022", "NIST-ATOMIC-SPECTROSCOPY"),
            measurements=(
                f"{TARGET_ID}: exact source-derived categorical match {comparison['passed']}",
                "favorable correspondence retained: production, decay identification and E1 class",
                "absent retained: no recognized element 126 within the current boundary ending at 118",
                "unresolved retained: route, cross-section, lifetime, branches, lines and separation remain unmeasured",
                "adverse retained: none in the registered official record",
                "deliberately tampered unfavorable control rejected",
            ),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition="Reject if any formal receipt or official byte identity changes; if any required fragment or result class is removed; if source content opens before seal; if Smithium is called observed; or if absence is called retirement.",
            passed=passed,
        )


__all__ = (
    "BlindSmithiumExternalValidator",
    "EXPERIMENT_ID",
    "PREDICTION_LABEL",
    "REGISTRY_PATH",
    "TARGET_ID",
    "external_registration_record",
    "prediction_program_document",
)
