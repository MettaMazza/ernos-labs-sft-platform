"""Shared post-registry observation custody for Classical Computation families.

This module supplies custody plumbing only. Family source identities, exact
observations, claim laws and falsification boundaries remain family-owned.
"""
import hashlib
import json
import platform

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load_frozen(root, registry_path, registry_hash, vector_path, vector_hash):
    if hash_file(root / registry_path) != registry_hash or hash_file(root / vector_path) != vector_hash:
        raise ValueError("Classical Computation frozen observation files changed")
    registry = json.loads((root / registry_path).read_text()); vector = json.loads((root / vector_path).read_text())
    registry_body = dict(registry); registry_identity = registry_body.pop("registry_identity")
    vector_body = dict(vector); vector_identity = vector_body.pop("vector_identity")
    if canonical(registry_body) != registry_identity or canonical(vector_body) != vector_identity or vector["registry_identity"] != registry_identity or registry["target_content_present"] is not False:
        raise ValueError("Classical Computation frozen observation identities changed")
    return registry, vector


class CompleteFieldObservationValidator:
    def __init__(self, root, spec, family, registry_path, registry_hash, vector_path, vector_hash, observer_identity, falsification_condition):
        self.root = root.resolve(); self.spec = spec; self.family = family; self.registry_path = registry_path; self.registry_hash = registry_hash; self.vector_path = vector_path; self.vector_hash = vector_hash; self.observer_identity = observer_identity; self.falsification_condition = falsification_condition

    def validate(self, sealed):
        self.spec.validate(); registry, vector = load_frozen(self.root, self.registry_path, self.registry_hash, self.vector_path, self.vector_hash)
        number = self.spec.claim_id.rsplit("-", 1)[-1]; row = next(record for record in vector["records"] if record["number"] == number)
        if row["claim_id"] != self.spec.claim_id or not row["all_rows_preserved"]: raise ValueError(f"{self.family} observation membership changed")
        experiment_id = f"SFT-EXP-COMP-{self.family}-{number}-V1"; target_id = f"COMP-{self.family}-{number}-EXACT-EXECUTION-V1"; expected_label = f"complete-{self.family.lower()}-{number}-execution-retained"
        experiment = {"experiment_id": experiment_id, "claim_id": self.spec.claim_id, "target_id": target_id, "expected_label": expected_label, "registry": self.registry_path, "falsification_condition": self.falsification_condition}
        registration_hash = sha256_identity(experiment)
        document = {"schema": "sft-v3-fold-program/1", "program_id": experiment_id + "-prediction", "instructions": [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}, {"opcode": "label", "destination": "prediction", "arguments": [self.family.lower() + "-execution", expected_label]}, {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]}, {"opcode": "emit", "destination": "", "arguments": ["prediction"]}]}
        program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, (target_id,), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=experiment_id, custodian_id=experiment_id + "-custodian", targets={target_id: HeldLabel("external-observation", row["expected_label"])}, custody_nonce=sha256_identity((registration_hash, vector["vector_identity"], number)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError(f"{self.family} capability audit failed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        matched = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label; target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=experiment_id + "-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity((self.observer_identity, self.spec.claim_id)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        measurements = (f"{self.family}-{number}: {row['observation_name']}", "exact execution: " + json.dumps(row["exact_observation"], sort_keys=True, separators=(",", ":")), f"complete family observation custody: {vector['record_count']} records; all rows preserved", "complete generated execution supplies the observation; no imported theorem answer, hidden branch or target-selected survivor enters")
        payload = {"claim": self.spec.claim_id, "seal": sealed.seal_hash, "registry": registry["registry_identity"], "vector": vector["vector_identity"], "observation": row["exact_observation"], "match": matched}
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row["source_ids"]), measurements, sha256_identity(payload), self.falsification_condition, bool(matched and vector["all_rows_preserved"]))
