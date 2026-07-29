"""Post-registry authoritative correspondence for Materials NANO-001--010."""

import hashlib
import json
import platform

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
from sft.materials.nano_001_010_laws_v1 import SPECS

REGISTRY = "census/materials_nano_001_010_target_registry_v1.json"
MANIFEST = "experiments/external_sources/materials/nano_001_010_v1/source_custody_manifest.json"
VECTOR = "experiments/external_sources/materials/nano_001_010_v1/complete_evidence_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_identity(root, relative, field):
    value = json.loads((root / relative).read_text())
    identity = value.pop(field)
    if canonical(value) != identity:
        raise ValueError(relative + " identity changed")
    return value, identity


def load_complete_vector(root):
    registry, registry_identity = load_identity(root, REGISTRY, "registry_identity")
    manifest, manifest_identity = load_identity(root, MANIFEST, "manifest_identity")
    if registry["target_content_present"] is not False or registry["target_count"] != len(SPECS) or manifest["target_registry_identity"] != registry_identity:
        raise ValueError("NANO target custody changed")
    for source in manifest["documents"]:
        if hash_file(root / source["snapshot_path"]) != source["snapshot_hash"]:
            raise ValueError("NANO source changed")
    vector, vector_identity = load_identity(root, VECTOR, "complete_vector_identity")
    if vector["source_custody_manifest_identity"] != manifest_identity or vector["target_registry_identity"] != registry_identity:
        raise ValueError("NANO evidence custody changed")
    for row in vector["claims"]:
        for comparison in row["comparisons"]:
            if hash_file(root / comparison["snapshot_path"]) != comparison["snapshot_hash"]:
                raise ValueError("NANO comparison source changed")
            if "text_reconstruction_path" in comparison and hash_file(root / comparison["text_reconstruction_path"]) != comparison["text_reconstruction_hash"]:
                raise ValueError("NANO text reconstruction changed")
    vector.update(complete_vector_identity=vector_identity, source_custody_manifest_identity=manifest_identity, target_registry_identity=registry_identity)
    return vector


def experiment_registration(spec):
    return {
        "experiment_id": f"SFT-EXP-MAT-NANO-{spec.number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"MATERIALS-NANO-{spec.number}-COMPLETE-EXTERNAL-RECORD",
        "target_identity_registry": REGISTRY,
        "expected_observation_label": spec.exact_result,
        "falsification_condition": "Reject if any registered source, fragment, condition, path, seal, custody identity, candidate, control or independent reconstruction is missing or changed.",
    }


def prediction_document(spec):
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": f"SFT-EXP-MAT-NANO-{spec.number}-V1-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["materials nanomaterials", spec.exact_result]},
            {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class NanoExternalValidator:
    def __init__(self, root, spec):
        self.root, self.spec = root.resolve(), spec

    def validate(self, sealed):
        self.spec.validate()
        vector = load_complete_vector(self.root)
        row = {item["claim_id"]: item for item in vector["claims"]}[self.spec.claim_id]
        if vector["claim_count"] != len(SPECS) or not row["all_comparisons_preserved"] or not row["all_registered_fragments_present"]:
            raise ValueError("NANO evidence incomplete")
        sources = tuple(dict.fromkeys(comparison["source_id"] for comparison in row["comparisons"]))
        measurements = tuple(f"{comparison['source_id']}: {'; '.join(comparison['registered_fragments'])}" for comparison in row["comparisons"])
        registration, document = experiment_registration(self.spec), prediction_document(self.spec)
        registration_hash = sha256_identity(registration)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target_id = registration["target_id"]
        envelope = PredictionEnvelope(registration["experiment_id"], {"registered-premise": sha256_identity(inputs["registered-premise"])}, (target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(
            experiment_id=registration["experiment_id"],
            custodian_id=registration["experiment_id"] + "-custodian",
            targets={target_id: HeldLabel("external-observation", registration["expected_observation_label"])},
            custody_nonce=sha256_identity((vector["complete_vector_identity"], self.spec.claim_id, measurements)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("NANO capability audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        match = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label
        omission_rejected = len(row["comparisons"][:-1]) != row["comparison_count"]
        target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=registration["experiment_id"] + "-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=target_identity,
            comparison_implementation_identity_hash=sha256_identity(("materials-nano-external-v1", self.spec.claim_id)),
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
        payload = {"claim_id": self.spec.claim_id, "seal": sealed.seal_hash, "vector": vector["complete_vector_identity"], "comparisons": row["comparisons"], "match": match, "omission_rejected": omission_rejected}
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=sources,
            measurements=(f"NANO-{self.spec.number}: {row['comparison_count']} comparisons", f"family sources: {vector['captured_source_count']}", f"exact correspondence: {match}; omission rejected: {omission_rejected}") + measurements,
            measurement_receipt_hash=sha256_identity(payload),
            falsification_condition=registration["falsification_condition"],
            passed=bool(match and omission_rejected and row["all_registered_fragments_present"]),
        )


__all__ = ("NanoExternalValidator", "REGISTRY", "MANIFEST", "VECTOR", "load_complete_vector", "experiment_registration")

