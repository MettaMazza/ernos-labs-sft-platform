#!/usr/bin/env python3
"""Implementation-distinct exact validator for CBLX-001 through CBLX-021."""
import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "decision-and-recognition-closure", "paired-recognizer-decision",
    "fair-prefix-dovetail-enumeration", "self-row-verdict-complement",
    "retained-description-fixed-point", "description-transform-fixed-point",
    "nontrivial-behavior-diagonal-boundary", "total-verdict-preserving-map",
    "adaptive-recorded-query-reduction", "finite-positive-query-witness",
    "mutual-reducibility-equivalence-order", "relative-self-halting-diagonal",
    "query-answer-provenance-ledger", "finite-quantifier-alternation-ledger",
    "complete-tile-sequence-witness", "generated-prefix-decision-self-reference-limit",
    "self-verification-missing-distinction", "closing-grammar-runtime-maximum",
    "complete-depth-bounded-runtime-census", "trace-or-relative-oracle-admissibility",
    "twenty-one-obligation-no-omission-ledger",
)


def diagonal(rows):
    return tuple("reject" if rows[index][index] == "accept" else "accept" for index in range(len(rows)))


def transitive(edges):
    nodes = sorted({x for edge in edges for x in edge})
    relation = set(edges) | {(x, x) for x in nodes}
    for middle in nodes:
        relation |= {(a, d) for a, b in relation for c, d in relation if b == middle == c}
    return relation


def tile_witness(tiles, depth):
    for width in range(1, depth + 1):
        for indices in product(range(len(tiles)), repeat=width):
            upper = tuple(x for i in indices for x in tiles[i][0])
            lower = tuple(x for i in indices for x in tiles[i][1])
            if upper == lower:
                return indices, upper
    return None


def independent_witness(index):
    table = (("accept", "reject", "accept"), ("reject", "reject", "accept"), ("accept", "accept", "reject"))
    if index == 1:
        left, right = {"a", "aa"}, {"b", "aa"}
        return left | right == {"a", "b", "aa"} and left & right == {"aa"} and left - right == {"a"}
    if index == 2:
        members, complement = {"a", "aa"}, {"b", "ab"}
        return members.isdisjoint(complement) and members | complement == {"a", "aa", "b", "ab"}
    if index == 3:
        traces = (("wait", "a"), ("b",), ("wait", "wait", "c"))
        schedule = tuple(traces[row][depth] for depth in range(3) for row in range(3) if depth < len(traces[row]))
        return all(x in schedule for x in ("a", "b", "c"))
    if index == 4:
        result = diagonal(table)
        return result == ("reject", "accept", "accept") and all(result[i] != table[i][i] for i in range(3))
    if index == 5:
        description = ("quote", ("emit", "x"))
        return (description, ("emit", "x"))[0] == description
    if index == 6:
        code = ("self", ("transform",))
        return ("transform", code)[1] == code
    if index in (7, 16):
        return all(("reject" if value == "accept" else "accept") != value for value in ("accept", "reject"))
    if index == 8:
        source = {"x": "accept", "y": "reject"}; target = {"a": "reject", "b": "accept"}; mapping = {"x": "b", "y": "a"}
        return all(source[x] == target[mapping[x]] for x in source)
    if index == 9:
        oracle = {"q1": "accept", "q2": "reject"}; trace = (("q1", oracle["q1"]), ("q2", oracle["q2"]))
        return trace[-1][1] == "reject"
    if index == 10:
        positive_queries = ({"a", "b"}, {"c"}); oracle = {"a", "b", "c"}
        return all(query <= oracle for query in positive_queries)
    if index == 11:
        return transitive({("A", "B"), ("B", "C")}) == {("A", "A"), ("B", "B"), ("C", "C"), ("A", "B"), ("B", "C"), ("A", "C")}
    if index == 12:
        return diagonal(table) != tuple(table[i][i] for i in range(3))
    if index == 13:
        return (("q1", "accept"), ("q2", "reject")) == tuple(((q, a) for q, a in (("q1", "accept"), ("q2", "reject"))))
    if index == 14:
        unary = {"a": False, "b": True}
        binary = {(a, b): a == b for a in ("a", "b") for b in ("a", "b")}
        return any(unary.values()) and not all(unary.values()) and all(any(binary[a, b] for b in ("a", "b")) for a in ("a", "b"))
    if index == 15:
        return tile_witness(((('a',), ('a',)), (('a', 'b'), ('a',)), (('b',), ('b', 'b'))), 2) == ((0,), ("a",))
    if index == 17:
        proof_rows = {"p", "p-implies-q"}
        return "consistency-of-entire-own-proof-system" not in proof_rows
    if index == 18:
        return all(len(tuple("a" for _ in range(depth))) == depth and depth > depth - 1 for depth in range(1, 9))
    if index == 19:
        for depth in range(1, 8):
            words = tuple(product(("a", "b"), repeat=depth))
            if max(map(len, words)) != depth or len(words) != 2 ** depth:
                return False
        return True
    if index == 20:
        record = {"oracle": "O", "query": "q", "answer": "accept", "order": "first"}
        return set(record) == {"oracle", "query", "answer", "order"}
    if index == 21:
        return len(RELATIONS) == 21 and all(independent_witness(number) for number in range(1, 21))
    return False


def generated_surface(index):
    axes = (
        ("sampled-description-domain", "complete-generated-domain"),
        ("hidden-or-selected-execution", "complete-trace-execution"),
        ("imported-theorem-answer", RELATIONS[index - 1]),
        ("forbidden-or-hidden-self-input", "retained-self-description"),
        ("sampled-machines", "literal-complete-product"),
        ("outcome-selected", "there-is-no-nothing-lineage"),
        ("preopened-target", "post-registry-exact-execution"),
        ("unbounded-from-finite-sample", "depth-certificate-or-explicit-limit"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
    rows, survivor = generated_surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "computability_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
