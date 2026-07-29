#!/usr/bin/env python3
"""Implementation-distinct exact validator for VALID-001--012."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "base-symbol-representation-receipt-vector",
    "record-provenance-receipt-vector",
    "source-measure-receipt-vector",
    "signal-sampling-receipt-vector",
    "compression-distortion-receipt-vector",
    "channel-capacity-receipt-vector",
    "noise-coding-receipt-vector",
    "relational-coarse-receipt-vector",
    "retrieval-inference-receipt-vector",
    "privacy-thermal-correspondence-receipt-vector",
    "complete-adverse-disposition-vector",
    "frozen-information-science-validation-lock",
)
COUNTS = {"BASE": 12, "SYMREP": 14, "RECORD": 12, "SOURCE": 14, "MEASURE": 16, "SIGNAL": 14, "COMP": 14, "CHAN": 18, "NOISE": 12, "CODE": 18, "REL": 14, "COARSE": 12, "RETR": 12, "INFER": 14, "PRIV": 10, "THERM": 10, "CORR": 16, "SEM": 12}
GROUPS = (("BASE", "SYMREP"), ("RECORD",), ("SOURCE", "MEASURE"), ("SIGNAL",), ("COMP",), ("CHAN",), ("NOISE", "CODE"), ("REL", "COARSE"), ("RETR", "INFER"), ("PRIV", "THERM", "CORR"))


def repository_witness(root, index):
    reconciliation = json.loads((root / "census/information_science_discipline_current_reconciliation_v18.json").read_text())
    families = reconciliation["completed_families"]
    if reconciliation["current_closed_count"] != 244 or set(families) != set(COUNTS):
        return False
    if any(len(families[name]) != count for name, count in COUNTS.items()):
        return False
    if index <= 10:
        return sum(len(families[name]) for name in GROUPS[index - 1]) == sum(COUNTS[name] for name in GROUPS[index - 1])
    controls = 0
    for rows in families.values():
        for row in rows:
            claim = root / "claims" / row["claim_id"]
            certificate = json.loads((claim / "certificate.json").read_text())
            if certificate["engine_receipt_hash"] != row["receipt_hash"]:
                return False
            controls += len(json.loads((claim / "controls.json").read_text())["controls"])
    if index == 11:
        return controls == 976
    return len(families) == 18 and sum(len(rows) for rows in families.values()) == 244 and controls == 976


def surface(index):
    axes = (
        ("partial-validation-support", "complete-frozen-receipt-support"),
        ("asserted-validation-label", RELATIONS[index - 1]),
        ("stale-or-unbound-certificate", "current-receipt-certificate-binding"),
        ("favorable-only-selection", "complete-disposition-custody"),
        ("sampled-validation-rows", "complete-declared-validation-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("validator-edited-to-pass", "immutable-engine-authority"),
    )
    rows = tuple("__".join(choice) for choice in product(*axes))
    survivor = "__".join(choice[1] for choice in axes)
    return rows, survivor


def main():
    claim_id, root, path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(path.read_text())
    rows, survivor = surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    witness = repository_witness(root, index)
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", witness))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "complete_validation_witness": witness}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
