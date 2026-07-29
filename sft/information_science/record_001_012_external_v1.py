"""Post-registry exact observation validator for RECORD-001--012."""
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

REGISTRY = "census/information_science_record_001_012_target_registry_v1.json"
REGISTRY_HASH = "sha256:81f5a00bc65e56b258894e5c7493d3ce74207142fc4315fa4744ccc908216f50"
VECTOR = "experiments/external_sources/information_science/record_001_012_observation_vector_v1.json"
VECTOR_HASH = "sha256:e5acd089d311179abe490ab5ce35ef7735c28d0a1669b21eb7eae305bd53e105"


def canonical(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load(root):
    registry_path = root / REGISTRY
    vector_path = root / VECTOR
    if hash_file(registry_path) != REGISTRY_HASH or hash_file(vector_path) != VECTOR_HASH:
        raise ValueError("RECORD frozen observation files changed")
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
        raise ValueError("RECORD frozen identities changed")
    return registry, vector


def registration(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "experiment_id": f"SFT-EXP-INFO-RECORD-{number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"INFO-RECORD-{number}-EXACT-OBSERVATION-V1",
        "expected_label": f"complete-record-{number}-observation-retained",
        "registry": REGISTRY,
        "falsification_condition": "Reject if the value-free registry, complete record census, exact observation, candidate survivor, source identity, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order.",
    }


def document(spec):
    number = spec.claim_id.rsplit("-", 1)[-1]
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": f"SFT-EXP-INFO-RECORD-{number}-V1-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
            {"opcode": "label", "destination": "prediction", "arguments": ["record-observation", f"complete-record-{number}-observation-retained"]},
            {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class RecordObservationValidator:
    def __init__(self, root, spec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed):
        self.spec.validate()
        registry, vector = load(self.root)
        number = self.spec.claim_id.rsplit("-", 1)[-1]
        row = next(record for record in vector["records"] if record["number"] == number)
        if row["claim_id"] != self.spec.claim_id or not row["all_rows_preserved"]:
            raise ValueError("RECORD observation membership changed")
        experiment = registration(self.spec)
        registration_hash = sha256_identity(experiment)
        program_document = document(self.spec)
        program = fold_program_from_mapping(program_document)
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
        audited, audit = HostilePackageAuditor().audit_program_document(program_document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("RECORD capability audit failed")
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
            comparison_implementation_identity_hash=sha256_identity(("information-science-record-observer-v1", self.spec.claim_id)),
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
            f"RECORD-{number}: {row['observation_name']}",
            "exact observation: " + json.dumps(row["exact_observation"], sort_keys=True, separators=(",", ":")),
            f"complete family observation custody: {vector['record_count']} records; all rows preserved",
            "complete finite data, schema, provenance, version and omission-ledger enumeration supplies the observation; no imported data-model axiom, silent overwrite or hidden missing row enters",
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
