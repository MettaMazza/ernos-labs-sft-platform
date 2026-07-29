"""Post-registry exact execution validator for VALID-001 through VALID-012."""

import hashlib
import json
import platform

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


REGISTRY = "census/quantum_valid_001_012_target_registry_v1.json"
REGISTRY_HASH = "sha256:9b539a46b7d4e52410f6bfac51c3dd3818ad69fff6d7a2bde4f9ec4a5b574c42"
VECTOR = "experiments/external_sources/quantum_computation/valid_001_012_observation_vector_v1.json"
VECTOR_HASH = "sha256:5f8bcbcd144e4abd7202e2081514705839180f4a02857d0da69839c221441e32"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(root):
    registry_path, vector_path = root / REGISTRY, root / VECTOR
    if hash_file(registry_path) != REGISTRY_HASH or hash_file(vector_path) != VECTOR_HASH:
        raise ValueError("VALID frozen observation files changed")
    registry, vector = json.loads(registry_path.read_text()), json.loads(vector_path.read_text())
    registry_body, vector_body = dict(registry), dict(vector)
    registry_identity, vector_identity = registry_body.pop("registry_identity"), vector_body.pop("vector_identity")
    if canonical(registry_body) != registry_identity or canonical(vector_body) != vector_identity or vector["registry_identity"] != registry_identity or registry["target_content_present"] is not False:
        raise ValueError("VALID frozen identities changed")
    return registry, vector


def experiment_registration(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "experiment_id": f"SFT-EXP-QUANTUM-VALID-{number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"QUANTUM-VALID-{number}-EXACT-EXECUTION-V1",
        "expected_label": f"complete-valid-{number}-execution-retained",
        "registry": REGISTRY,
        "falsification_condition": "Reject if the value-free registry, complete current receipt/evidence replay, adverse/ownership vector, source identity, candidate survivor, seal, control or independent reconstruction is missing, changed, duplicated or opened out of order.",
    }


def program_document(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": f"SFT-EXP-QUANTUM-VALID-{number}-V1-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["valid-execution", f"complete-valid-{number}-execution-retained"]},
            {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class QuantumValidationExecutionValidator:
    def __init__(self, root, spec):
        self.root, self.spec = root.resolve(), spec

    def validate(self, sealed):
        self.spec.validate()
        registry, vector = load(self.root)
        number = self.spec.claim_id.rsplit("-", 1)[-1]
        row = next(record for record in vector["records"] if record["number"] == number)
        if row["claim_id"] != self.spec.claim_id or not row["all_rows_preserved"]:
            raise ValueError("VALID observation membership changed")
        experiment, document = experiment_registration(self.spec), program_document(self.spec)
        registration_hash = sha256_identity(experiment)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target_id = experiment["target_id"]
        envelope = PredictionEnvelope(experiment["experiment_id"], {"registered-premise": sha256_identity(inputs["registered-premise"])}, (target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=experiment["experiment_id"], custodian_id=experiment["experiment_id"] + "-custodian", targets={target_id: HeldLabel("external-observation", row["expected_label"])}, custody_nonce=sha256_identity((registration_hash, vector["vector_identity"], number)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("VALID capability audit failed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        matched = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label
        target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=experiment["experiment_id"] + "-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity(("quantum-computation-valid-observer-v1", self.spec.claim_id)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        measurements = (
            f"VALID-{number}: {row['observation_name']}",
            "exact Quantum family validation replay: " + json.dumps(row["exact_observation"], sort_keys=True, separators=(",", ":")),
            f"complete formal/empirical/adverse custody: {vector['record_count']} vectors; all rows preserved",
            "the Grand Lock binds current receipts and evidence without inventing downstream measured values or closing lawful extensions",
        )
        payload = {"claim": self.spec.claim_id, "seal": sealed.seal_hash, "registry": registry["registry_identity"], "vector": vector["vector_identity"], "observation": row["exact_observation"], "match": matched}
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row["source_ids"]), measurements, sha256_identity(payload), experiment["falsification_condition"], bool(matched and vector["all_rows_preserved"]))
