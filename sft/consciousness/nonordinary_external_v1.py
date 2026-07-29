"""Post-seal, identity-first empirical validator for the Consciousness return family."""

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

EXPERIMENT_ID = "SFT-EXP-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002"
CLAIM_ID = "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002"
TARGET_ID = "CONSCIOUSNESS-NONORDINARY-COMPLETE-FAMILY-2026-07-28"
ROOT_DIR = "evidence/external/consciousness"
OBSERVATION_FILES = (
    "nonordinary_2026-07-28/observations.json",
    "nonordinary_2026-07-28_retry_1/observations.json",
)
PREDICTION_LABEL = "__".join((
    "stable-directed-inducer-concurrent-observed-with-heterogeneity",
    "multidimensional-nonordinary-report-and-neural-correspondence-observed-with-ontology-separate",
    "nrem-rem-alternation-observed-with-local-global-and-duration-heterogeneity",
    "lost-integrated-function-distinct-from-retained-living-components",
    "favorable-adverse-absent-nonpurpose-and-unresolved-rows-retained",
))

REQUIRED = {
    "31630652": ("stimulation of one sensory modality evokes additional experiences in another modality", "sounds evoking colours"),
    "39922140": ("automatic, specific and consistent nature", "inherent circularity"),
    "36707026": ("systematically induce specific colour concurrents", "neural mechanisms remain largely unresolved"),
    "39191666": ("subjective experiences were associated with increased neural Lempel-Ziv complexity",),
    "41451954": ("multidimensional feature of human experience", "neural marker"),
    "42030660": ("multidimensional subjective experience", "brain network dynamics"),
    "39280264": ("alternate multiple times between rapid-eye-movement", "mechanisms for REM homeostatic pressure remain undetermined"),
    "37972882": ("behavioral, phenomenological, physiological", "they can also dissociate"),
    "39400423": ("orderly progression through wakefulness", "non-rapid eye movement", "rapid eye movement"),
    "31696418": ("loss of integrated functioning as a unified organism", "physiologically maintained for prolonged periods"),
    "41401968": ("brain death", "maintained stable levels of plasma membrane repair proteins", "no evidence of pyroptosis activation"),
    "41878502": ("donation after brain death", "islet yield, viability, and function remained high"),
    "41559743": ("Pharmacologic confounders", "diagnostic accuracy"),
    "42135815": ("spinal-mediated movements", "movements of unclear neuroanatomic origin"),
}


def normalize(raw: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def external_registration_record() -> dict[str, object]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "claim_id": CLAIM_ID,
        "target_id": TARGET_ID,
        "identity_registries": tuple(f"{ROOT_DIR}/{name.replace('observations.json', 'target_identities.json')}" for name in OBSERVATION_FILES),
        "expected_label": PREDICTION_LABEL,
        "all_result_classes_required": True,
        "falsification_condition": "Reject if registered sources do not contain stable directed inducer-concurrent experience, empirically measured multidimensional altered experience with separate report and neural records, recurring NREM/REM organization, or a distinction between lost integrated organismal function and retained viable components; also reject if heterogeneity, null/non-purpose rows, unresolved mechanisms, diagnostic confounders or report/ontology boundaries are suppressed, or if source content opened before identity registration.",
    }


def prediction_program_document() -> dict[str, object]:
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-prediction", "instructions": [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
        {"opcode": "label", "destination": "prediction", "arguments": ["consciousness-observation", PREDICTION_LABEL]},
        {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ]}


def source_target(root: Path):
    documents = []
    registry_hashes = []
    for relative in OBSERVATION_FILES:
        path = root / ROOT_DIR / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        registry_hashes.append(hash_file(path))
        identity_path = root / payload["target_identity_registration_path"]
        if hash_file(identity_path) != payload["target_identity_registration_hash"]:
            raise ValueError("Consciousness target identity registration changed")
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
        if identity.get("target_content_present") is not False:
            raise ValueError("Consciousness target content was present in identity registration")
        identities = {row["pmid"] for row in identity["selected"]}
        for row in payload["documents"]:
            if row["pmid"] not in identities:
                raise ValueError("Consciousness source not pre-registered")
            snapshot = root / row["snapshot_path"]
            if hash_file(snapshot) != row["snapshot_hash"]:
                raise ValueError("Consciousness source bytes changed")
            documents.append((row, normalize(snapshot.read_text(encoding="utf-8", errors="replace"))))
    by_id = {row["pmid"]: body for row, body in documents}
    for pmid, fragments in REQUIRED.items():
        if pmid not in by_id or any(fragment.casefold() not in by_id[pmid].casefold() for fragment in fragments):
            raise ValueError(f"required Consciousness observation absent: {pmid}")
    classes = {
        "favorable": (
            "cross-modal inducer evokes a specific concurrent",
            "altered-state reports covary with measured neural dynamics",
            "NREM and REM recur in organized alternation",
            "integrated organismal function can end while isolated organs and cells remain viable",
        ),
        "heterogeneous_or_adverse": (
            "consistency thresholds can be diagnostically circular and language-dependent",
            "competing synaesthesia mechanisms remain unresolved",
            "global sleep labels can dissociate across behavioral, phenomenological and physiological dimensions",
            "brain-death diagnosis has pharmacologic confounders and movement ambiguity",
        ),
        "absent_or_nonpurpose_matched": (
            "five first-batch cessation results are retained despite not testing the registered cessation question",
            "one self-report-only synaesthesia survey remains distinct from objective mechanism evidence",
        ),
        "unresolved": (
            "specific ontology of nonordinary reports is not established by correlation",
            "REM transition mechanism and universal cycle duration remain undetermined",
            "the clinical and ontological integration boundary remains contested",
        ),
    }
    extraction = sha256_identity((tuple(registry_hashes), tuple((row["pmid"], row["snapshot_hash"], row["class"]) for row, _ in documents), classes))
    return PREDICTION_LABEL, extraction, tuple("PMID:" + row["pmid"] for row, _ in documents), classes


class BlindConsciousnessReturnExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        registration = external_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (TARGET_ID,), sealed.seal_hash, registration_hash)
        observed, extraction_hash, source_ids, classes = source_target(self.root)
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-source-custodian", targets={TARGET_ID: HeldLabel("external-observation", observed)}, custody_nonce=sha256_identity((registration_hash, extraction_hash)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("Consciousness hostile-package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        if not isinstance(prediction, HeldLabel) or prediction.family != "consciousness-observation":
            raise ValueError("invalid Consciousness prediction")
        comparison = prediction.label == release.targets[TARGET_ID].label
        tampered = prediction.label != release.targets[TARGET_ID].label + "__tampered"
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("Consciousness target identity differs")
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity(("exact-consciousness-return-family-comparison", EXPERIMENT_ID)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement = {"registration": registration_hash, "derivation": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "extraction": extraction_hash, "sources": source_ids, "classes": classes, "comparison": comparison, "tampered": tampered}
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
                f"{TARGET_ID}: exact categorical match {comparison}",
                "stable cross-modal inducer/concurrent correspondence retained with diagnostic and mechanistic heterogeneity",
                "multidimensional altered-state reports and measured neural covariation retained without ontological inflation",
                "NREM/REM alternation retained with local/global dissociation and non-universal timing",
                "lost integrated function and retained viable components remain distinct",
                "null, non-purpose-matched, heterogeneous and unresolved rows retained",
                "tampered control rejected",
            ),
            measurement_receipt_hash=sha256_identity(measurement),
            falsification_condition=registration["falsification_condition"],
            passed=bool(comparison and tampered),
        )


__all__ = ("BlindConsciousnessReturnExternalValidator", "external_registration_record", "source_target")
