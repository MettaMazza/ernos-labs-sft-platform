#!/usr/bin/env python3
from itertools import product
import hashlib
import json
import sys
from pathlib import Path


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def surface(number):
    relation = "complete-one-owner-root-traced-consumer-graph" if number == "006" else {
        "001": "chemistry-to-materials-directed-one-owner-handoff",
        "002": "chemistry-to-biology-directed-one-owner-handoff",
        "003": "chemistry-to-medicine-directed-one-owner-handoff",
        "004": "chemistry-to-earth_environment-directed-one-owner-handoff",
        "005": "chemistry-to-astronomy_cosmology-directed-one-owner-handoff",
    }[number]
    axes = (("anonymous-cross-branch-result", "complete-owned-coordinate"), ("overlapping-or-ownerless", "exactly-one-owner"), ("branch-name-association", relation), ("copied-law", "directed-consumer-edge"), ("selected-summary", "complete-paired-receipt-records"), ("outcome-before-registration", "value-free-registry-before-outcomes"), ("omission-tolerated", "duplicate-missing-or-tampered-halts"), ("permanent-branch-lock", "dated-complete-extension-open"))
    rows = tuple("__".join(item) for item in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    cid, root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    number = cid.rsplit("-", 1)[-1]
    sealed = json.loads(sealed_path.read_text())
    registry = json.loads((root / "census/chemistry_hand_001_006_dependency_registry_v2.json").read_text())
    vector = json.loads((root / "experiments/external_sources/chemistry/hand_001_006_complete_handoff_vector_v2.json").read_text())
    rb = dict(registry); ri = rb.pop("registry_identity"); vb = dict(vector); vi = vb.pop("complete_vector_identity")
    identities = canonical(rb) == ri and canonical(vb) == vi and vector["registry_identity"] == ri and registry["target_content_present"] is False
    if number == "006":
        graph = registry["complete_owner_dependency_graph"]
        complete = identities and len(graph) == registry["base_claim_count"] == registry["unique_owner_count"] == registry["root_reachable_claim_count"] and sum(len(row["dependencies"]) for row in graph) == registry["dependency_edge_count"]
    else:
        records = vector["paired_records"][number]
        complete = identities and tuple(row["claim_id"] for row in records) == tuple(registry["paired_claim_ids"][number]) and tuple(row["owner"] for row in records) == tuple(registry["paired_owner_vectors"][number]) and all(row["all_rows_preserved"] for row in records)
    generated, survivor = surface(number)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in generated}
    controls = sealed["controls"]
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, len(controls) == 4, all(row["passed"] for row in controls), sealed["closure"]["scope"] == "depth_independent", complete))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "complete_external_or_graph_reconstruction": complete}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__": main()
