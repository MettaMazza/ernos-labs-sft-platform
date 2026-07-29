#!/usr/bin/env python3
"""Freeze the value-free Materials HAND owner/dependency graph."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/materials_hand_001_006_dependency_registry_v1.json"
ROOT_CLAIM = "SFT-ROOT-THERE-IS-NO-NOTHING"
PAIRS = {
    "001": ("SFT-MAT-PROC-WINDOW-PROVENANCE-010", "SFT-ENG-PHYSICAL-HANDOFF-001"),
    "002": ("SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001", "SFT-BIO-CELL-ADHESION-001", "SFT-BIO-BIO-ASSAY-001"),
    "003": ("SFT-MAT-BIO-CONTROLLED-RELEASE-006", "SFT-MED-INTERVENTION-001", "SFT-MED-DOSE-001", "SFT-MED-RESPONSE-001"),
    "004": ("SFT-MAT-SUST-END-OF-LIFE-CUSTODY-009", "SFT-EARTH-POLLUTANT-IDENTITY-001", "SFT-EARTH-SOURCE-PATH-RECEPTOR-001"),
    "005": ("SFT-MAT-EXT-RADIATION-RESPONSE-007", "SFT-ASTRO-SPECTRUM-001", "SFT-ASTRO-SOURCE-001"),
}
EXPECTED_BRANCHES = {
    "001": ("materials", "engineering_translation"),
    "002": ("materials", "biology", "biology"),
    "003": ("materials", "medicine", "medicine", "medicine"),
    "004": ("materials", "earth_environment", "earth_environment"),
    "005": ("materials", "astronomy_cosmology", "astronomy_cosmology"),
}


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise SystemExit("Materials HAND v1 registry already frozen")
    rows = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    by_id = {row["claim_id"]: row for row in rows}
    if len(rows) != len(by_id):
        raise SystemExit("duplicate owner identity")
    for number, ids in PAIRS.items():
        if tuple(by_id[cid]["branch"] for cid in ids) != EXPECTED_BRANCHES[number]:
            raise SystemExit(f"HAND-{number} owner vector changed")
    graph = []
    dependency_map = {}
    edge_count = cross_count = 0
    for row in sorted(rows, key=lambda item: item["claim_id"]):
        path = ROOT / "claims" / row["claim_id"] / "registration.json"
        registration = json.loads(path.read_text())
        if registration.get("claim_id") != row["claim_id"] or registration.get("branch") != row["branch"]:
            raise SystemExit(f"registration owner changed: {row['claim_id']}")
        dependencies = tuple(registration.get("dependencies", ()))
        missing = tuple(cid for cid in dependencies if cid not in by_id)
        if missing:
            raise SystemExit(f"missing dependency for {row['claim_id']}: {missing}")
        dependency_map[row["claim_id"]] = dependencies
        edge_count += len(dependencies)
        cross_count += sum(by_id[cid]["branch"] != row["branch"] for cid in dependencies)
        graph.append({
            "claim_id": row["claim_id"],
            "owner": row["branch"],
            "registration_path": path.relative_to(ROOT).as_posix(),
            "registration_sha256": digest(path),
            "dependencies": dependencies,
        })
    visiting = set()
    resolved = {}
    def reaches_root(cid):
        if cid in resolved:
            return resolved[cid]
        if cid in visiting:
            raise SystemExit(f"dependency cycle at {cid}")
        visiting.add(cid)
        dependencies = dependency_map[cid]
        result = cid == ROOT_CLAIM or (bool(dependencies) and all(reaches_root(dep) for dep in dependencies))
        visiting.remove(cid)
        resolved[cid] = result
        return result
    for cid in dependency_map:
        reaches_root(cid)
    if not all(resolved.values()):
        raise SystemExit("not every frozen claim reaches the root theorem")
    payload = {
        "schema": "sft-v3-materials-hand-001-006-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_empirical_outcome_access": True,
        "target_content_present": False,
        "base_claim_count": len(rows),
        "unique_owner_count": len(by_id),
        "root_reachable_claim_count": sum(resolved.values()),
        "dependency_edge_count": edge_count,
        "cross_branch_dependency_edge_count": cross_count,
        "paired_claim_ids": PAIRS,
        "paired_owner_vectors": EXPECTED_BRANCHES,
        "complete_owner_dependency_graph": graph,
    }
    payload["registry_identity"] = canonical(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "path": OUTPUT.relative_to(ROOT).as_posix(),
        "base_claim_count": len(rows),
        "root_reachable_claim_count": sum(resolved.values()),
        "dependency_edge_count": edge_count,
        "cross_branch_dependency_edge_count": cross_count,
        "identity": payload["registry_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
