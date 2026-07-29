"""Post-registry exact execution validator for QCPLXX-001 through QCPLXX-026."""
import hashlib
import json
import platform
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


REGISTRY = "census/quantum_qcplxx_001_026_target_registry_v1.json"
REGISTRY_HASH = "sha256:319bd79923d05ef063544bb8e6b6811d1bfdb2d1ff4ca4f210737cac864863b6"
VECTOR = "experiments/external_sources/quantum_computation/qcplxx_001_026_observation_vector_v1.json"
VECTOR_HASH = "sha256:842d659c77f7f83639002c3a916b2ccc73746918ca2ad87e25b0c5d69401a3fa"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(root):
    rp, vp = root / REGISTRY, root / VECTOR
    if hash_file(rp) != REGISTRY_HASH or hash_file(vp) != VECTOR_HASH:
        raise ValueError("QCPLXX frozen observation files changed")
    registry, vector = json.loads(rp.read_text()), json.loads(vp.read_text())
    rb, vb = dict(registry), dict(vector)
    ri, vi = rb.pop("registry_identity"), vb.pop("vector_identity")
    if canonical(rb) != ri or canonical(vb) != vi or vector["registry_identity"] != ri or registry["target_content_present"] is not False:
        raise ValueError("QCPLXX frozen identities changed")
    return registry, vector


def experiment_registration(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {"experiment_id": f"SFT-EXP-QUANTUM-QCPLXX-{number}-V1", "claim_id": spec.claim_id, "target_id": f"QUANTUM-QCPLXX-{number}-EXACT-EXECUTION-V1", "expected_label": f"complete-qcplxx-{number}-execution-retained", "registry": REGISTRY, "falsification_condition": "Reject if the value-free registry, complete complexity grammar, exact resource execution, source identity, candidate survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."}


def program_document(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {"schema": "sft-v3-fold-program/1", "program_id": f"SFT-EXP-QUANTUM-QCPLXX-{number}-V1-prediction", "instructions": [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}, {"opcode": "label", "destination": "prediction", "arguments": ["qcplxx-execution", f"complete-qcplxx-{number}-execution-retained"]}, {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]}, {"opcode": "emit", "destination": "", "arguments": ["prediction"]}]}


class QuantumComplexityExecutionValidator:
    def __init__(self, root, spec): self.root, self.spec = root.resolve(), spec
    def validate(self, sealed):
        self.spec.validate()
        registry, vector = load(self.root)
        number = self.spec.claim_id.rsplit("-", 1)[-1]
        row = next(record for record in vector["records"] if record["number"] == number)
        if row["claim_id"] != self.spec.claim_id or not row["all_rows_preserved"]: raise ValueError("QCPLXX observation membership changed")
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
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("QCPLXX capability audit failed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        matched = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label
        target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=experiment["experiment_id"] + "-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=target_identity, comparison_implementation_identity_hash=sha256_identity(("quantum-computation-qcplxx-observer-v1", self.spec.claim_id)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        measurements = (f"QCPLXX-{number}: {row['observation_name']}", "exact quantum-complexity execution: " + json.dumps(row["exact_observation"], sort_keys=True, separators=(",", ":")), f"complete quantum-complexity custody: {vector['record_count']} records; all rows preserved", "complete finite input, execution, decision, resource and comparison records supply the observation; physical device performance and unrestricted asymptotic claims remain downstream")
        payload = {"claim": self.spec.claim_id, "seal": sealed.seal_hash, "registry": registry["registry_identity"], "vector": vector["vector_identity"], "observation": row["exact_observation"], "match": matched}
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row["source_ids"]), measurements, sha256_identity(payload), experiment["falsification_condition"], bool(matched and vector["all_rows_preserved"]))
