#!/usr/bin/env python3
"""Freeze value-free ownership identities for Chemistry HAND-001--006."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/chemistry_hand_001_006_dependency_registry_v1.json"
PAIRS = {
    "001": (
        "SFT-CHEM-POLYMER-MATERIALS-HANDOFF-013",
        "SFT-MAT-MEAS-COMPOSITION-001",
        "SFT-MAT-MEAS-PROPERTY-001",
    ),
    "002": (
        "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001",
        "SFT-BIO-PROTEIN-FUNCTION-001",
        "SFT-BIO-METABOLIC-TRANSFORMATION-001",
    ),
    "003": (
        "SFT-CHEM-MEAS-SUBSTANCE-001",
        "SFT-MED-INTERVENTION-001",
        "SFT-MED-DOSE-001",
        "SFT-MED-RESPONSE-001",
    ),
    "004": (
        "SFT-CHEM-MEAS-SUBSTANCE-001",
        "SFT-CHEM-RXN-IDENTITY-001",
        "SFT-EARTH-ENVIRONMENTAL-TRANSFORMATION-001",
        "SFT-EARTH-ENVIRONMENTAL-TRANSPORT-001",
    ),
    "005": (
        "SFT-CHEM-SPEC-ROT-VIB-001",
        "SFT-ASTRO-SPECTRUM-001",
        "SFT-ASTRO-SOURCE-001",
    ),
}
EXPECTED_BRANCHES = {
    "001": ("chemistry", "materials", "materials"),
    "002": ("chemistry", "biology", "biology"),
    "003": ("chemistry", "medicine", "medicine", "medicine"),
    "004": ("chemistry", "chemistry", "earth_environment", "earth_environment"),
    "005": ("chemistry", "astronomy_cosmology", "astronomy_cosmology"),
}


def identity(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    if OUTPUT.exists():
        raise SystemExit("Chemistry HAND registry already frozen")
    rows = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    by_id = {row["claim_id"]: row for row in rows}
    if len(rows) != len(by_id):
        raise SystemExit("duplicate claim ownership identity")
    for number, ids in PAIRS.items():
        branches = tuple(by_id[cid]["branch"] for cid in ids)
        if branches != EXPECTED_BRANCHES[number]:
            raise SystemExit(f"HAND-{number} owner boundary changed: {branches}")
    graph = []
    edge_count = 0
    cross_branch_edges = 0
    for row in sorted(rows, key=lambda item: item["claim_id"]):
        dependencies = tuple(row.get("dependencies", ()))
        missing = tuple(cid for cid in dependencies if cid not in by_id)
        if missing:
            raise SystemExit(f"missing dependency identities for {row['claim_id']}: {missing}")
        edge_count += len(dependencies)
        cross_branch_edges += sum(by_id[cid]["branch"] != row["branch"] for cid in dependencies)
        graph.append({"claim_id": row["claim_id"], "owner": row["branch"], "dependencies": dependencies})
    payload = {
        "schema": "sft-v3-chemistry-hand-001-006-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_empirical_outcome_access": True,
        "target_content_present": False,
        "base_claim_count": len(rows),
        "unique_owner_count": len(by_id),
        "dependency_edge_count": edge_count,
        "cross_branch_dependency_edge_count": cross_branch_edges,
        "paired_claim_ids": PAIRS,
        "paired_owner_vectors": EXPECTED_BRANCHES,
        "complete_owner_dependency_graph": graph,
    }
    payload["registry_identity"] = identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "path": OUTPUT.relative_to(ROOT).as_posix(),
        "base_claim_count": len(rows),
        "dependency_edge_count": edge_count,
        "cross_branch_dependency_edge_count": cross_branch_edges,
        "identity": payload["registry_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
