"""Post-registry authoritative correspondence for Materials MICRO-001--009."""

import hashlib
import json
import platform
from pathlib import Path

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.materials.micro_001_009_laws_v1 import SPECS


REGISTRY = "census/materials_micro_001_009_target_registry_v1.json"
ADDENDUM = "census/materials_micro_coarsening_source_addendum_v1.json"
MANIFEST = "experiments/external_sources/materials/micro_001_009_v2/source_custody_manifest.json"
VECTOR = "experiments/external_sources/materials/micro_001_009_v2/complete_evidence_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _load_identity(root, relative, field):
    value = json.loads((root / relative).read_text())
    identity = value.pop(field)
    if canonical(value) != identity:
        raise ValueError(relative + " identity changed")
    return value, identity


def load_complete_vector(root: Path):
    registry, registry_identity = _load_identity(root, REGISTRY, "registry_identity")
    addendum, addendum_identity = _load_identity(root, ADDENDUM, "addendum_identity")
    manifest, manifest_identity = _load_identity(root, MANIFEST, "manifest_identity")
    if registry["target_content_present"] is not False or addendum["detailed_target_content_present"] is not False:
        raise ValueError("MICRO target registry contains target content")
    if manifest["target_registry_identity"] != registry_identity or manifest["source_addendum_identity"] != addendum_identity:
        raise ValueError("MICRO custody identities changed")
    for source in manifest["documents"]:
        if hash_file(root / source["snapshot_path"]) != source["snapshot_hash"]:
            raise ValueError("MICRO source changed: " + source["source_id"])
    vector, vector_identity = _load_identity(root, VECTOR, "complete_vector_identity")
    if vector["source_custody_manifest_identity"] != manifest_identity or vector["target_registry_identity"] != registry_identity or vector["source_addendum_identity"] != addendum_identity:
        raise ValueError("MICRO vector custody changed")
    for row in vector["pdf_text_reconstructions"]:
        if hash_file(root / row["text_path"]) != row["text_hash"]:
            raise ValueError("MICRO PDF reconstruction changed")
    vector["complete_vector_identity"] = vector_identity
    vector["source_custody_manifest_identity"] = manifest_identity
    vector["target_registry_identity"] = registry_identity
    vector["source_addendum_identity"] = addendum_identity
    return vector


def experiment_registration(spec):
    return {
        "experiment_id": f"SFT-EXP-MAT-MICRO-{spec.number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"MATERIALS-MICRO-{spec.number}-COMPLETE-EXTERNAL-RECORD",
        "target_identity_registry": REGISTRY,
        "source_identity_addendum": ADDENDUM,
        "expected_observation_label": spec.exact_result,
        "falsification_condition": "Reject if any registered source identity, available fragment, unavailable row, failed route, specimen/method/condition boundary, prediction seal, custody identity, candidate, control or independent reconstruction is missing or changed.",
    }


def prediction_document(spec):
    return {"schema": "sft-v3-fold-program/1", "program_id": f"SFT-EXP-MAT-MICRO-{spec.number}-V1-prediction", "instructions": [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}, {"opcode": "label", "destination": "prediction", "arguments": ["materials-microstructure", spec.exact_result]}, {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]}, {"opcode": "emit", "destination": "", "arguments": ["prediction"]}]}


class MicrostructureExternalValidator:
    def __init__(self, root: Path, spec):
        self.root, self.spec = root.resolve(), spec

    def validate(self, sealed):
        self.spec.validate()
        vector = load_complete_vector(self.root)
        rows = {row["claim_id"]: row for row in vector["claims"]}
        if self.spec.claim_id not in rows or vector["claim_count"] != len(SPECS):
            raise ValueError("MICRO family row missing")
        row = rows[self.spec.claim_id]
        if not row["all_comparisons_preserved"] or not row["all_available_fragments_present"]:
            raise ValueError("MICRO evidence row incomplete")
        sources = tuple(dict.fromkeys(item["source_id"] for item in row["comparisons"]))
        measurements = tuple(f"{item['source_id']}: {item['source_status']}; {item['first_registered_fragment']}; {item['second_registered_fragment']}; favourable-use={item['used_for_favourable_comparison']}" for item in row["comparisons"])
        registration = experiment_registration(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target_id = registration["target_id"]
        envelope = PredictionEnvelope(registration["experiment_id"], {"registered-premise": sha256_identity(inputs["registered-premise"])}, (target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=registration["experiment_id"], custodian_id=registration["experiment_id"] + "-custodian", targets={target_id: HeldLabel("external-observation", registration["expected_observation_label"])}, custody_nonce=sha256_identity((vector["complete_vector_identity"], self.spec.claim_id, measurements)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("MICRO capability audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        match = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label
        omission_rejected = len(row["comparisons"][:-1]) != row["comparison_count"]
        target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=registration["experiment_id"] + "-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity(("materials-micro-external-v1", self.spec.claim_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"claim_id": self.spec.claim_id, "sealed_derivation": sealed.seal_hash, "complete_vector": vector["complete_vector_identity"], "comparisons": row["comparisons"], "match": match, "omission_rejected": omission_rejected}
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=sources, measurements=(f"MICRO-{self.spec.number}: {row['comparison_count']} distinct comparisons retained", f"family custody: {vector['captured_source_count']} usable and {vector['unavailable_source_count']} unavailable sources", f"exact correspondence: {match}; omission rejected: {omission_rejected}") + measurements, measurement_receipt_hash=sha256_identity(payload), falsification_condition=registration["falsification_condition"], passed=bool(match and omission_rejected))


__all__ = ("MicrostructureExternalValidator", "REGISTRY", "ADDENDUM", "MANIFEST", "VECTOR", "load_complete_vector", "experiment_registration")
