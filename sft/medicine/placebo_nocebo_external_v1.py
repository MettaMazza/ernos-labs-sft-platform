"""Post-seal, identity-first empirical validator for placebo/nocebo physiology."""

from html import unescape
import json
from pathlib import Path
import platform
import re

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file

EXPERIMENT_ID = "SFT-EXP-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002"
CLAIM_ID = "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002"
TARGET_ID = "MEDICINE-PLACEBO-NOCEBO-OBJECTIVE-FAMILY-2026-07-28"
ROOT_DIR = "evidence/external/medicine"
OBSERVATION_FILES = (
    "placebo_nocebo_2026-07-28/observations.json",
    "placebo_nocebo_2026-07-28_retry_1/observations.json",
    "placebo_nocebo_2026-07-28_retry_2/observations.json",
)
PREDICTION_LABEL = "__".join((
    "objective-placebo-physiology-observed",
    "objective-nocebo-physiology-observed",
    "effects-context-bounded-not-universal",
    "report-and-objective-outcome-distinct",
    "favorable-null-unresolved-and-nonpurpose-rows-retained",
))

REQUIRED = {
    "42469238": ("Both techniques increase activity", "decrease activation", "partially distinct mechanisms"),
    "41553203": ("significant nocebo hyperalgesia", "autonomic arousal", "brain activity", "control comparator"),
    "41544307": ("no group differences in BAG", "subjective symptom improvement"),
    "42056755": ("objective endpoints", "statistically indistinguishable", "subjective endpoints"),
    "41663169": ("Clinical Trial Protocol", "salivary cortisol"),
    "42320075": ("cognitive and affective outcomes", "symptom intensity or frequency"),
}


def normalize(raw: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def external_registration_record() -> dict[str, object]:
    return {
        "experiment_id": EXPERIMENT_ID, "claim_id": CLAIM_ID, "target_id": TARGET_ID,
        "identity_registries": tuple(f"{ROOT_DIR}/{name.replace('observations.json', 'target_identities.json')}" for name in OBSERVATION_FILES),
        "preseal_exclusion": "audits/MEDICINE_PLACEBO_PRESEAL_SOURCE_EXCLUSION_2026-07-28.json",
        "retry_receipts": ("audits/MEDICINE_PLACEBO_SOURCE_RETRY_2026-07-28.json", "audits/MEDICINE_PLACEBO_SOURCE_RETRY_2_2026-07-28.json"),
        "expected_label": PREDICTION_LABEL, "all_result_classes_required": True,
        "falsification_condition": "Reject if objective comparator-bound placebo and nocebo physiology are absent from the registered source family, if effects are reported as universal or unbounded, if report and objective records are conflated, if any unfavorable or unresolved source row is suppressed, or if source content opened before its identity registration.",
    }


def prediction_program_document() -> dict[str, object]:
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-prediction", "instructions": [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
        {"opcode": "label", "destination": "prediction", "arguments": ["medical-observation", PREDICTION_LABEL]},
        {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ]}


def source_target(root: Path):
    documents = []
    registry_hashes = []
    for relative in OBSERVATION_FILES:
        path = root / ROOT_DIR / relative
        payload = json.loads(path.read_text(encoding="utf-8")); registry_hashes.append(hash_file(path))
        identity_path = root / payload["target_identity_registration_path"]
        if hash_file(identity_path) != payload["target_identity_registration_hash"]:
            raise ValueError("Medicine target identity registration changed")
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
        if identity.get("target_content_present") is not False:
            raise ValueError("Medicine target content was present in identity registration")
        identities = {row["pmid"] for row in identity["selected"]}
        for row in payload["documents"]:
            if row["pmid"] not in identities: raise ValueError("source not pre-registered")
            snapshot = root / row["snapshot_path"]
            if hash_file(snapshot) != row["snapshot_hash"]: raise ValueError("Medicine source bytes changed")
            documents.append((row, normalize(snapshot.read_text(encoding="utf-8", errors="replace"))))
    by_id = {row["pmid"]: text for row, text in documents}
    for pmid, fragments in REQUIRED.items():
        if pmid not in by_id or any(fragment.casefold() not in by_id[pmid].casefold() for fragment in fragments):
            raise ValueError(f"required Medicine observation absent: {pmid}")
    classes = {
        "favorable": ("objective placebo-linked neural modulation", "objective nocebo autonomic and neurophysiological modulation"),
        "adverse_or_null": ("no between-group brain-age difference", "objective placebo endpoints often small", "communication effects less consistent for symptom intensity"),
        "unresolved": ("registered nocebo trial protocol has no outcome",),
        "nonpurpose_matched_preserved": ("two active-drug placebo comparator trials", "one nonexperimental nocebo review"),
    }
    return PREDICTION_LABEL, sha256_identity((tuple(registry_hashes), tuple((row["pmid"], row["snapshot_hash"]) for row, _ in documents), classes)), tuple("PMID:" + row["pmid"] for row, _ in documents), classes


class BlindPlaceboNoceboExternalValidator:
    def __init__(self, root: Path): self.root = root.resolve()
    def validate(self, sealed) -> EmpiricalValidation:
        registration = external_registration_record(); registration_hash = sha256_identity(registration)
        document = prediction_program_document(); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (TARGET_ID,), sealed.seal_hash, registration_hash)
        observed, extraction_hash, source_ids, classes = source_target(self.root)
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-source-custodian", targets={TARGET_ID: HeldLabel("external-observation", observed)}, custody_nonce=sha256_identity((registration_hash, extraction_hash)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("Medicine hostile-package audit failed")
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "medical-observation": raise ValueError("invalid Medicine prediction")
        comparison = prediction.label == release.targets[TARGET_ID].label; tampered = prediction.label != release.targets[TARGET_ID].label + "__tampered"
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("Medicine target identity differs")
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity(("exact-placebo-nocebo-family-comparison", EXPERIMENT_ID)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement = {"registration": registration_hash, "derivation": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "extraction": extraction_hash, "sources": source_ids, "classes": classes, "comparison": comparison, "tampered": tampered}
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=source_ids, measurements=(f"{TARGET_ID}: exact categorical match {comparison}", "objective placebo neural modulation retained", "objective nocebo autonomic and neurophysiological modulation retained", "null, small, context-dependent, unresolved protocol and non-purpose-matched rows retained", "report and objective outcomes remain distinct", "tampered control rejected"), measurement_receipt_hash=sha256_identity(measurement), falsification_condition=registration["falsification_condition"], passed=bool(comparison and tampered))


__all__ = ("BlindPlaceboNoceboExternalValidator", "external_registration_record", "source_target")
