#!/usr/bin/env python3
from itertools import product
import hashlib
import json
from pathlib import Path
import sys


CLAIM_ID = "SFT-PHYS-VALIDATION-GRAND-LOCK-076"
SOURCE_HASH = "sha256:e233cd761aa874893d2c2a4e2b09f071297aee1204d531fce3d93429948177a3"
DOMAINS = (
    ("answer-only-scalar", "complete-fold-carrier"),
    ("imported-or-fitted-relation", "complete-Physics-empirical-vector-with-all-adverse-and-scope-boundary-records-retained"),
    ("unbound-provenance", "source-bound-proof-trace"),
    ("target-readable-prediction", "capability-closed-prediction"),
    ("proof-measurement-conflation", "separate-measurement-record"),
    ("selected-favourable-rows", "complete-registered-rows"),
    ("finite-answer-lookup", "one-successor-closure"),
    ("free-extra-rule", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def digest(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_record(record, root):
    rows = tuple(record["empirical_claims"])
    ids = tuple(row["claim_id"] for row in rows)
    sources = tuple(record["unique_external_source_ids"])
    adverse = tuple(record["unfavorable_or_scope_boundary_ids"])
    legacy = tuple(record["legacy_empirical_materialization_without_separate_measurement_receipt"])
    boundary = record["methodological_boundary"]
    if not (len(ids) == len(set(ids)) == record["empirical_claim_count"] == 234):
        return False
    if not (len(sources) == len(set(sources)) == record["unique_external_source_id_count"] == 147):
        return False
    if not (len(adverse) == len(set(adverse)) == 14 and set(adverse).issubset(set(record["physics_claim_ids"]))):
        return False
    missing = {row["claim_id"] for row in rows if not row.get("measurement_receipt_hash")}
    if missing != set(legacy) or len(legacy) != 6:
        return False
    if not all(row.get("empirical_validation_hash") and row.get("external_validation_hash") for row in rows):
        return False
    for row in rows:
        if digest(root / row["receipt_path"]) != row["receipt_file_sha256"]:
            return False
        if digest(root / row["certificate_path"]) != row["certificate_sha256"]:
            return False
    formal = record["formal_grand_lock"]
    if digest(root / formal["receipt_path"]) != formal["receipt_file_sha256"]:
        return False
    if digest(root / record["prelock_input_path"]) != record["prelock_input_sha256"]:
        return False
    if boundary.get("measurements_select_formal_survivor") is not False:
        return False
    return all(value is True for key, value in boundary.items() if key != "measurements_select_formal_survivor")


def main():
    source_path, root, sealed_path = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    record = json.loads(source_path.read_text(encoding="utf-8"))
    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        digest(source_path) == SOURCE_HASH,
        verify_record(record, root),
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 256,
            "empirical_claim_count": 234,
            "external_source_id_count": 147,
            "adverse_or_scope_boundary_count": 14,
            "legacy_receipt_shape_count": 6,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
