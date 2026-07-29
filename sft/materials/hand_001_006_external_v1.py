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
from sft.materials.hand_001_006_laws_v1 import REGISTRY, REGISTRY_FILE_HASH

VECTOR = "experiments/external_sources/materials/hand_001_006_complete_handoff_vector_v1.json"
VECTOR_FILE_HASH = "sha256:03c5cc6fb63a530cfb11a9b27cce9da3177ac1a3b284a0331f26a374e7b1aa5d"


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def load_surface(root):
    registry_path = root / "census/materials_hand_001_006_dependency_registry_v1.json"
    vector_path = root / VECTOR
    if hash_file(registry_path) != REGISTRY_FILE_HASH or hash_file(vector_path) != VECTOR_FILE_HASH:
        raise ValueError("Materials HAND frozen files changed")
    registry = json.loads(registry_path.read_text())
    vector = json.loads(vector_path.read_text())
    rb = dict(registry); ri = rb.pop("registry_identity")
    vb = dict(vector); vi = vb.pop("complete_vector_identity")
    if canonical(rb) != ri or canonical(vb) != vi or vector["registry_identity"] != ri:
        raise ValueError("Materials HAND frozen identities changed")
    return registry, vector


def check(root, spec):
    registry, vector = load_surface(root)
    summaries = []
    sources = []
    if spec.number == "006":
        graph = registry["complete_owner_dependency_graph"]
        ids = tuple(row["claim_id"] for row in graph)
        if len(graph) != registry["base_claim_count"] or len(set(ids)) != len(ids) or registry["root_reachable_claim_count"] != len(graph):
            raise ValueError("HAND-006 complete owner graph changed")
        edge_count = 0
        for row in graph:
            path = root / row["registration_path"]
            if hash_file(path) != row["registration_sha256"]:
                raise ValueError("HAND-006 registration changed: " + row["claim_id"])
            edge_count += len(row["dependencies"])
        if edge_count != registry["dependency_edge_count"]:
            raise ValueError("HAND-006 dependency graph incomplete")
        summaries.append(f"complete owner graph: {len(graph)} unique owners; {edge_count} dependency edges; {registry['cross_branch_dependency_edge_count']} cross-branch edges; all root-traced")
        for rows in vector["paired_records"].values():
            for row in rows:
                sources.extend(row["source_ids"])
    else:
        rows = vector["paired_records"][spec.number]
        if tuple(row["claim_id"] for row in rows) != spec.paired_claim_ids:
            raise ValueError("Materials HAND pair changed")
        if tuple(row["owner"] for row in rows) != tuple(registry["paired_owner_vectors"][spec.number]):
            raise ValueError("Materials HAND owner vector changed")
        for row in rows:
            for name in ("registration", "certificate", "controls", "empirical_validation", "receipt"):
                path = root / row[name + "_path"]
                if hash_file(path) != row[name + "_sha256"]:
                    raise ValueError(f"HAND {name} changed for {row['claim_id']}")
            if not row["all_rows_preserved"]:
                raise ValueError("HAND external rows omitted")
            sources.extend(row["source_ids"])
            summaries.append(f"{row['owner']} owns {row['claim_id']}; sources={len(row['source_ids'])}; evidence-lines={row['measurement_line_count']}; receipt={row['receipt_hash']}")
    return registry, vector, tuple(summaries), tuple(dict.fromkeys(sources))


def registration(spec):
    return {
        "experiment_id": f"SFT-EXP-MAT-HAND-{spec.number}-V1",
        "claim_id": spec.claim_id,
        "target_id": f"MATERIALS-HAND-{spec.number}-EXACT-OWNER-BOUNDARY-V1",
        "identity_registry": "census/materials_hand_001_006_dependency_registry_v1.json",
        "expected_label": f"complete-materials-hand-{spec.number}-retained",
        "falsification_condition": "Reject if any registered owner, paired receipt, external record, registration, dependency edge, root trace, control or extension boundary is missing, duplicated, changed or opened before the value-free owner registry.",
    }


def document(spec):
    return {"schema": "sft-v3-fold-program/1", "program_id": f"SFT-EXP-MAT-HAND-{spec.number}-V1-prediction", "instructions": [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]},
        {"opcode": "label", "destination": "prediction", "arguments": ["materials-handoff", f"complete-materials-hand-{spec.number}-retained"]},
        {"opcode": "pair", "destination": "bound", "arguments": ["premise", "prediction"]},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ]}


class MaterialsHandoffValidator:
    def __init__(self, root, spec): self.root = root.resolve(); self.spec = spec
    def validate(self, sealed):
        self.spec.validate()
        registry, vector, summaries, sources = check(self.root, self.spec)
        reg = registration(self.spec); rh = sha256_identity(reg); doc = document(self.spec); program = fold_program_from_mapping(doc)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        target = reg["target_id"]
        envelope = PredictionEnvelope(reg["experiment_id"], {"registered-premise": sha256_identity(inputs["registered-premise"])}, (target,), sealed.seal_hash, rh)
        vault = TargetVault(experiment_id=reg["experiment_id"], custodian_id=reg["experiment_id"] + "-custodian", targets={target: HeldLabel("external-observation", reg["expected_label"])}, custody_nonce=sha256_identity((rh, vector["complete_vector_identity"], self.spec.number)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(doc, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("HAND capability audit failed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        matched = isinstance(execution.output, HeldLabel) and execution.output.label == release.targets[target].label
        omission_rejected = bool((len(self.spec.paired_claim_ids) if self.spec.number != "006" else registry["base_claim_count"]) > 1)
        tid = target_identity_from_release(release)
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=reg["experiment_id"] + "-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=tid, comparison_implementation_identity_hash=sha256_identity(("materials-hand-v1", self.spec.claim_id)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=rh, registered_target_identity_hash=tid, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        measurements = (f"HAND-{self.spec.number}: value-free owner registry preceded outcome access", f"frozen graph: {registry['base_claim_count']} claims, {registry['dependency_edge_count']} dependency edges, {registry['cross_branch_dependency_edge_count']} cross-branch uses", f"paired external surface: {vector['paired_record_count']} records, {vector['source_identity_occurrence_count']} source identities, {vector['measurement_line_count']} evidence lines", f"all selected evidence rows preserved; omission control rejected {omission_rejected}") + summaries
        payload = {"claim": self.spec.claim_id, "seal": sealed.seal_hash, "registry": registry["registry_identity"], "vector": vector["complete_vector_identity"], "match": matched, "omission": omission_rejected}
        return EmpiricalValidation(sealed.seal_hash, rh, isolation, custody, True, True, True, sources or ("SFT-V3-COMPLETE-OWNER-DEPENDENCY-GRAPH",), measurements, sha256_identity(payload), reg["falsification_condition"], bool(matched and omission_rejected))
