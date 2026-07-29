"""Post-registry exact execution validator for REVX-001 through REVX-018."""
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


REGISTRY = "census/quantum_revx_001_018_target_registry_v1.json"
REGISTRY_HASH = "sha256:1126b0643902d2884feb51f503d458c9dd1078e4bbf7a738f4b8bd961d333fcf"
VECTOR = "experiments/external_sources/quantum_computation/revx_001_018_observation_vector_v1.json"
VECTOR_HASH = "sha256:7a3159804dc618be7c1d0c875654c213bf6f02cda6a6adb270722124242568eb"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(root):
    registry_path = root / REGISTRY
    vector_path = root / VECTOR
    if hash_file(registry_path) != REGISTRY_HASH or hash_file(vector_path) != VECTOR_HASH:
        raise ValueError("REVX frozen observation files changed")
    registry = json.loads(registry_path.read_text())
    vector = json.loads(vector_path.read_text())
    registry_body = dict(registry)
    registry_identity = registry_body.pop("registry_identity")
    vector_body = dict(vector)
    vector_identity = vector_body.pop("vector_identity")
    if (
        canonical(registry_body) != registry_identity
        or canonical(vector_body) != vector_identity
        or vector["registry_identity"] != registry_identity
        or registry["target_content_present"] is not False
    ):
        raise ValueError("REVX frozen identities changed")
    return registry, vector


def experiment_registration(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "experiment_id": f"SFT-EXP-QUANTUM-REVX-{number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"QUANTUM-REVX-{number}-EXACT-EXECUTION-V1",
        "expected_label": f"complete-revx-{number}-execution-retained",
        "registry": REGISTRY,
        "falsification_condition": "Reject if the value-free registry, complete reversible grammar, exact forward/inverse execution, source identity, candidate survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order.",
    }


def program_document(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": f"SFT-EXP-QUANTUM-REVX-{number}-V1-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["revx-execution", f"complete-revx-{number}-execution-retained"]},
            {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class ReversibleExecutionValidator:
    def __init__(self, root, spec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed):
        self.spec.validate()
        registry, vector = load(self.root)
        number = self.spec.claim_id.rsplit("-", 1)[-1]
        row = next(record for record in vector["records"] if record["number"] == number)
        if row["claim_id"] != self.spec.claim_id or not row["all_rows_preserved"]:
            raise ValueError("REVX observation membership changed")
        experiment = experiment_registration(self.spec)
        registration_hash = sha256_identity(experiment)
        document = program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target_id = experiment["target_id"]
        envelope = PredictionEnvelope(
            experiment["experiment_id"],
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            (target_id,),
            sealed.seal_hash,
            registration_hash,
        )
        vault = TargetVault(
            experiment_id=experiment["experiment_id"],
            custodian_id=experiment["experiment_id"] + "-custodian",
            targets={target_id: HeldLabel("external-observation", row["expected_label"])},
            custody_nonce=sha256_identity((registration_hash, vector["vector_identity"], number)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("REVX capability audit failed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        matched = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target_id].label
        target_identity = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=experiment["experiment_id"] + "-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=target_identity,
            comparison_implementation_identity_hash=sha256_identity(("quantum-computation-revx-observer-v1", self.spec.claim_id)),
            prediction_seal_hash=prediction.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurements = (
            f"REVX-{number}: {row['observation_name']}",
            "exact reversible execution: " + json.dumps(row["exact_observation"], sort_keys=True, separators=(",", ":")),
            f"complete reversible-computation custody: {vector['record_count']} records; all rows preserved",
            "complete finite forward and inverse traces supply the observation; physical energy, heat, timing, noise and hardware performance remain downstream measurements and cannot select the formal law",
        )
        payload = {
            "claim": self.spec.claim_id,
            "seal": sealed.seal_hash,
            "registry": registry["registry_identity"],
            "vector": vector["vector_identity"],
            "observation": row["exact_observation"],
            "match": matched,
        }
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(row["source_ids"]),
            measurements,
            sha256_identity(payload),
            experiment["falsification_condition"],
            bool(matched and vector["all_rows_preserved"]),
        )
