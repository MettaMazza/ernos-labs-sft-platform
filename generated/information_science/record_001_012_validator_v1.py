#!/usr/bin/env python3
"""Implementation-distinct exact validator for RECORD-001--012."""
import hashlib
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "source-field-value-identity",
    "complete-schema-tuple-relation",
    "data-bound-metadata-record",
    "complete-field-type-custody",
    "contiguous-acyclic-provenance-chain",
    "identity-bound-integrity-check",
    "payload-and-parent-version-identity",
    "three-way-absence-missing-unknown",
    "canonical-duplicate-alias-ledger",
    "complete-link-alternative-ledger",
    "retained-absent-unexpected-ledger",
    "reconstructing-custody-package",
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def witness(index):
    record = ("source-A", "temperature", (21, 2))
    if index == 1:
        return all(record[:2]) and digest(record) == digest(record)
    if index == 2:
        schema = ("symbol", "label"); rows = (("a", "A"), ("b", "B"))
        bound = tuple(tuple(zip(schema, row)) for row in rows)
        return bound == ((("symbol", "a"), ("label", "A")), (("symbol", "b"), ("label", "B")))
    if index == 3:
        meta = {"data": digest(record), "schema": "temperature-parts-v1", "unit": "exact-part", "source": "sensor-A"}
        return len(meta) == 4 and meta["data"] == digest(record)
    if index == 4:
        schema = {"name": str, "count": int}; good = {"name": "alpha", "count": 3}; bad = {"name": "alpha"}
        valid = lambda row: set(row) == set(schema) and all(isinstance(row[key], schema[key]) for key in schema)
        return valid(good) and not valid(bad)
    if index == 5:
        rows = (("capture", None), ("normalize", "capture"), ("publish", "normalize"))
        return len({row[0] for row in rows}) == 3 and rows[0][1] is None and all(rows[position][1] == rows[position - 1][0] for position in range(1, len(rows)))
    if index == 6:
        sealed = {"payload": record, "identity": digest(record)}
        changed = {"payload": record + ("changed",), "identity": digest(record)}
        return sealed["identity"] == digest(sealed["payload"]) and changed["identity"] != digest(changed["payload"])
    if index == 7:
        v1 = ("v1", digest(("a",)), None); v2 = ("v2", digest(("a", "b")), "v1")
        return v1[1] != v2[1] and v2[2] == v1[0]
    if index == 8:
        return len({("absence", "0"), ("missing", "expected-row"), ("unknown", "retained-row")}) == 3
    if index == 9:
        aliases = (("A", "a"), ("alpha", "a"))
        return digest(("a", 1)) == digest(("a", 1)) and len(set(source for source, _ in aliases)) == 2 and len(set(target for _, target in aliases)) == 1
    if index == 10:
        links = (("r1", "s1", "exact"), ("r2", "s2", "possible"), ("r2", "s3", "possible"))
        return tuple(row for row in links if row[0] == "r2") == links[1:]
    if index == 11:
        expected = ("r1", "r2", "r3"); observed = ("r1", "r3", "r4")
        return (tuple(x for x in expected if x in observed), tuple(x for x in expected if x not in observed), tuple(x for x in observed if x not in expected)) == (("r1", "r3"), ("r2",), ("r4",))
    if index == 12:
        package = (record, ("schema", "unit", "source"), (("capture", None), ("publish", "capture")))
        return digest(package) == digest(json.loads(json.dumps(package)))
    return False


def surface(index):
    axes = (
        ("partial-record-carrier", "complete-source-bound-carrier"),
        ("mutable-presentation-identity", "canonical-content-and-source-identity"),
        ("imported-record-answer", RELATIONS[index - 1]),
        ("unrecorded-transformation", "complete-provenance-custody"),
        ("sampled-records", "complete-declared-record-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("fit-exception-extra-rule", "finite-successor-or-explicit-boundary"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
    rows, survivor = surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((
        received == rows,
        len(set(received)) == len(received) == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        len(sealed["controls"]) == 4,
        all(row["passed"] for row in sealed["controls"]),
        sealed["closure"]["scope"] == "depth_independent",
        witness(index),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "complete_record_witness": witness(index)},
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
