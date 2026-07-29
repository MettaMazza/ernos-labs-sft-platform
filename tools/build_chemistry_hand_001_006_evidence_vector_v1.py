#!/usr/bin/env python3
"""Open and freeze the receipt-bound HAND-001--006 evidence after registry freeze."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/chemistry_hand_001_006_dependency_registry_v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/hand_001_006_complete_handoff_vector_v1.json"


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
        raise SystemExit("Chemistry HAND evidence vector already frozen")
    registry = read(REGISTRY)
    body = dict(registry)
    registered_identity = body.pop("registry_identity")
    if canonical(body) != registered_identity or registry["target_content_present"]:
        raise SystemExit("HAND value-free registry changed")
    census_path = ROOT / "census/claims.json"
    census = read(census_path)
    rows = {row["claim_id"]: row for row in census["claims"]}
    evidence = {}
    source_count = measurement_count = 0
    for number, ids in registry["paired_claim_ids"].items():
        records = []
        for cid in ids:
            row = rows[cid]
            package = ROOT / "claims" / cid
            registration = package / "registration.json"
            controls = package / "controls.json"
            empirical = package / "empirical_validation.json"
            receipt = ROOT / row["receipt_path"]
            certificate = current_certificate(package, row["receipt_hash"])
            for path in (registration, controls, empirical, receipt, certificate):
                if not path.is_file():
                    raise SystemExit(f"missing HAND evidence: {path.relative_to(ROOT)}")
            e = read(empirical)
            c = read(controls).get("controls", ())
            r = read(receipt)
            if not (e.get("passed") is True and e.get("all_rows_preserved") is True and e.get("target_opened_after_seal") is True):
                raise SystemExit(f"incomplete empirical custody: {cid}")
            if not c or not all(item.get("passed") for item in c) or not r.get("model_admitted") or r.get("receipt_hash") != row["receipt_hash"]:
                raise SystemExit(f"incomplete engine/control custody: {cid}")
            sources = tuple(map(str, e.get("data_source_ids", ())))
            measurements = tuple(map(str, e.get("measurements", ())))
            if not sources or not measurements:
                raise SystemExit(f"empty external surface: {cid}")
            source_count += len(sources)
            measurement_count += len(measurements)
            records.append({
                "claim_id": cid,
                "owner": row["branch"],
                "receipt_hash": row["receipt_hash"],
                "receipt_path": receipt.relative_to(ROOT).as_posix(),
                "receipt_file_sha256": digest(receipt),
                "registration_path": registration.relative_to(ROOT).as_posix(),
                "registration_sha256": digest(registration),
                "certificate_path": certificate.relative_to(ROOT).as_posix(),
                "certificate_sha256": digest(certificate),
                "controls_path": controls.relative_to(ROOT).as_posix(),
                "controls_sha256": digest(controls),
                "empirical_validation_path": empirical.relative_to(ROOT).as_posix(),
                "empirical_validation_sha256": digest(empirical),
                "source_ids": sources,
                "measurement_line_count": len(measurements),
                "all_rows_preserved": True,
            })
        evidence[number] = records
    payload = {
        "schema": "sft-v3-chemistry-hand-001-006-evidence-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": registered_identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "paired_records": evidence,
        "paired_record_count": sum(map(len, evidence.values())),
        "source_identity_occurrence_count": source_count,
        "measurement_line_count": measurement_count,
        "complete_owner_graph_claim_count": registry["base_claim_count"],
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
        "identity": payload["complete_vector_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
