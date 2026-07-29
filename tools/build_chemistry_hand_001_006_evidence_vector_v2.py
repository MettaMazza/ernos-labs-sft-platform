#!/usr/bin/env python3
"""Freeze HAND paired empirical records against the corrected v2 registry."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/chemistry_hand_001_006_dependency_registry_v2.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/hand_001_006_complete_handoff_vector_v2.json"


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def current_certificate(package, receipt_hash):
    matches = [path for path in sorted(package.glob("certificate*.json")) if read(path).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1:
        raise SystemExit(f"{package.name} current certificate count {len(matches)}")
    return matches[0]


def main():
    if OUTPUT.exists():
        raise SystemExit("Chemistry HAND v2 vector already frozen")
    registry = read(REGISTRY)
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"]:
        raise SystemExit("HAND v2 registry changed")
    census_path = ROOT / "census/claims.json"
    rows = {row["claim_id"]: row for row in read(census_path)["claims"]}
    evidence = {}
    source_count = measurement_count = 0
    for number, ids in registry["paired_claim_ids"].items():
        records = []
        for cid in ids:
            row = rows[cid]
            package = ROOT / "claims" / cid
            paths = {
                "registration": package / "registration.json",
                "controls": package / "controls.json",
                "empirical_validation": package / "empirical_validation.json",
                "receipt": ROOT / row["receipt_path"],
                "certificate": current_certificate(package, row["receipt_hash"]),
            }
            if not all(path.is_file() for path in paths.values()):
                raise SystemExit(f"missing HAND evidence: {cid}")
            empirical = read(paths["empirical_validation"])
            controls = read(paths["controls"]).get("controls", ())
            receipt = read(paths["receipt"])
            if not (empirical.get("passed") is True and empirical.get("all_rows_preserved") is True and empirical.get("target_opened_after_seal") is True and empirical.get("evaluator_verified_seal") is True):
                raise SystemExit(f"incomplete empirical custody: {cid}")
            if not controls or not all(item.get("passed") for item in controls) or not receipt.get("model_admitted") or receipt.get("receipt_hash") != row["receipt_hash"]:
                raise SystemExit(f"incomplete engine/control custody: {cid}")
            sources = tuple(map(str, empirical.get("data_source_ids", ())))
            measurements = tuple(map(str, empirical.get("measurements", ())))
            if not sources or not measurements:
                raise SystemExit(f"empty external surface: {cid}")
            source_count += len(sources)
            measurement_count += len(measurements)
            record = {"claim_id": cid, "owner": row["branch"], "receipt_hash": row["receipt_hash"], "source_ids": sources, "measurement_line_count": len(measurements), "all_rows_preserved": True}
            for name, path in paths.items():
                record[name + "_path"] = path.relative_to(ROOT).as_posix()
                record[name + "_sha256"] = digest(path)
            records.append(record)
        evidence[number] = records
    payload = {
        "schema": "sft-v3-chemistry-hand-001-006-evidence-vector/2",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "paired_records": evidence,
        "paired_record_count": sum(map(len, evidence.values())),
        "source_identity_occurrence_count": source_count,
        "measurement_line_count": measurement_count,
        "complete_owner_graph_claim_count": registry["base_claim_count"],
        "complete_owner_graph_root_reachable_claim_count": registry["root_reachable_claim_count"],
        "complete_owner_graph_dependency_edge_count": registry["dependency_edge_count"],
        "complete_owner_graph_cross_branch_edge_count": registry["cross_branch_dependency_edge_count"],
        "complete_owner_graph_unique": registry["unique_owner_count"] == registry["base_claim_count"],
        "claims_census_path": census_path.relative_to(ROOT).as_posix(),
        "claims_census_sha256": digest(census_path),
        "all_selected_claims_model_admitted": True,
        "all_selected_external_rows_preserved": True,
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "path": OUTPUT.relative_to(ROOT).as_posix(),
        "paired_record_count": payload["paired_record_count"],
        "source_identity_occurrence_count": source_count,
        "measurement_line_count": measurement_count,
        "owner_graph_claim_count": registry["base_claim_count"],
        "owner_graph_edges": registry["dependency_edge_count"],
        "identity": payload["complete_vector_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
