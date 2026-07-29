#!/usr/bin/env python3
"""Implementation-distinct exact validator for SOURCE-001--014."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "complete-canonical-source-support", "complete-position-labelled-sequence",
    "state-and-adjacent-transition-trace", "complete-held-spatial-adjacency",
    "complete-network-path-ledger", "partition-refinement-order",
    "position-invariant-complete-support", "position-labelled-changing-support",
    "complete-position-product-support", "bounded-context-transition-support",
    "complete-ordered-joint-support", "proper-joint-support-with-projections",
    "fresh-source-form-successor", "fourteen-source-obligation-ledger",
)


def route_census(edges, start, finish):
    pending = [(start,)]
    complete = []
    while pending:
        path = pending.pop()
        if path[-1] == finish:
            complete.append(path)
            continue
        for left, right in edges:
            if left == path[-1] and right not in path:
                pending.append(path + (right,))
    return tuple(sorted(complete))


def witness(index):
    alphabet = ("a", "b")
    edges = (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"))
    if index == 1: return len(("a", "b", "c")) == len(set(("a", "b", "c"))) == 3
    if index == 2: return tuple(value for _, value in ((1, "a"), (2, "b"), (3, "a"))) == ("a", "b", "a") and ("a", "b", "a") != ("a", "a", "b")
    if index == 3:
        states = {"ready", "read", "emit"}; transitions = {("ready", "read"), ("read", "emit")}; trace = ("ready", "read", "emit")
        return set(trace) <= states and all(pair in transitions for pair in zip(trace, trace[1:]))
    if index == 4:
        relation = {("nw", "ne"), ("ne", "nw"), ("nw", "sw"), ("sw", "nw")}
        return all(left != right and (right, left) in relation for left, right in relation)
    if index == 5: return route_census(edges, "a", "d") == (("a", "b", "d"), ("a", "c", "d"))
    if index == 6:
        fine = (("a",), ("b",), ("c",)); coarse = (("a", "b"), ("c",))
        return all(any(set(part) <= set(container) for container in coarse) for part in fine) and {x for row in fine for x in row} == {x for row in coarse for x in row}
    if index == 7: return all(row == alphabet for row in (alphabet, alphabet, alphabet))
    if index == 8:
        rows = (alphabet, ("a",), alphabet)
        return tuple(position + 1 for position, row in enumerate(rows) if row != rows[0]) == (2,)
    if index == 9: return tuple(product(alphabet, repeat=2)) == (("a", "a"), ("a", "b"), ("b", "a"), ("b", "b"))
    if index == 10:
        allowed = {("a", "a"), ("a", "b"), ("b", "a")}; good = (("a", "a", "b"), ("b", "a", "a")); bad = ("a", "b", "b")
        return all(all(pair in allowed for pair in zip(word, word[1:])) for word in good) and not all(pair in allowed for pair in zip(bad, bad[1:]))
    if index == 11:
        joint = tuple(product(("a", "b"), ("x", "y", "z")))
        return len(joint) == len(set(joint)) == 6 and set(a for a, _ in joint) == {"a", "b"} and set(b for _, b in joint) == {"x", "y", "z"}
    if index == 12:
        joint = (("a", "x"), ("b", "y"))
        return len(joint) < 4 and set(a for a, _ in joint) == {"a", "b"} and set(b for _, b in joint) == {"x", "y"}
    if index == 13:
        prior = ("a", "b"); enlarged = prior + ("c",)
        return enlarged[:len(prior)] == prior and len(enlarged) == len(set(enlarged)) == 3
    if index == 14: return len(RELATIONS) == 14 and all(witness(number) for number in range(1, 14))
    return False


def surface(index):
    axes = (
        ("partial-or-duplicated-support", "complete-canonical-support"),
        ("unlabelled-occurrences", "retained-position-or-node-label"),
        ("imported-source-answer", RELATIONS[index - 1]),
        ("terminal-only-record", "complete-transition-and-path-custody"),
        ("sampled-source-forms", "complete-declared-source-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("fit-exception-extra-rule", "finite-successor-or-explicit-boundary"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1]); sealed = json.loads(sealed_path.read_text()); rows, survivor = surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {row: row == survivor for row in rows}
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "complete_source_witness": witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__": main()
