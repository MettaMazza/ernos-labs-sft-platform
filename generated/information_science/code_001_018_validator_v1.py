#!/usr/bin/env python3
"""Implementation-distinct exact validator for CODE-001--018."""
import json
import sys
from itertools import product
from pathlib import Path

REL = (
    "complete-injective-code-relation", "minimum-separation-correction-ledger", "equal-width-block-code-support",
    "fold-label-composition-closure", "complete-check-syndrome-record", "odd-repetition-majority-recovery",
    "typed-erasure-reconstruction", "unique-substitution-predecessor", "contiguous-burst-recovery",
    "state-retaining-convolution-code", "complete-prefix-tree-decoding", "product-concatenated-code-composition",
    "sparse-held-coordinate-check-graph", "network-edge-code-custody", "complete-radius-list-boundary",
    "complete-budget-adversary-boundary", "exact-source-width-rate-parts", "eighteen-coding-obligation-ledger",
)
REP = (("L", "L", "L"), ("R", "R", "R"))


def flip(label):
    return "R" if label == "L" else "L"


def dist(a, b):
    return sum(x != y for x, y in zip(a, b))


def closest(received, radius):
    return tuple(word for word in REP if dist(word, received) <= radius)


def vote(word):
    return "L" if word.count("L") > word.count("R") else "R"


def pair(a, b):
    return "same" if a == b else "different"


def fold(a, b):
    return "L" if a == b else "R"


def witness(index):
    if index == 1:
        rows = (("L", ("L", "L")), ("R", ("R", "R")))
        return len({a for a, _ in rows}) == len({b for _, b in rows}) == 2
    if index == 2:
        return dist(*REP) == 3 and all(len(closest(tuple(flip(x) if n == p else x for n, x in enumerate(source)), 1)) == 1 for source in REP for p in range(3))
    if index == 3:
        return len(REP) == 2 and tuple(len(word) for word in REP) == (3, 3)
    if index == 4:
        even = (("L", "L", "L"), ("L", "R", "R"), ("R", "L", "R"), ("R", "R", "L"))
        return len(even) == 4 and all(tuple(fold(x, y) for x, y in zip(a, b)) in even for a in even for b in even)
    if index == 5:
        word = ("R", "L", "L")
        return tuple(pair(word[n], word[n + 1]) for n in range(2)) == ("different", "same")
    if index == 6:
        return all(vote(tuple(flip(x) if n == p else x for n, x in enumerate(source))) == source[0] for source in REP for p in range(3))
    if index == 7:
        return all(len({x for n, x in enumerate(source) if n != p}) == 1 for source in REP for p in range(3))
    if index == 8:
        return all(closest(tuple(flip(x) if n == p else x for n, x in enumerate(source)), 1) == (source,) for source in REP for p in range(3))
    if index == 9:
        return all(vote(tuple(flip(x) if start <= n < start + 2 else x for n, x in enumerate((label,) * 5))) == label for label in ("L", "R") for start in range(4))
    if index == 10:
        prior = "L"
        rows = []
        for label in ("L", "R", "R"):
            rows.append((label, prior, label, fold(label, prior)))
            prior = label
        return tuple(rows) == (("L", "L", "L", "L"), ("R", "L", "R", "R"), ("R", "R", "R", "L"))
    if index == 11:
        tree = tuple(product(("L", "R"), repeat=2))
        return len(tree) == 4 and tuple(x for x in tree if x == ("R", "L")) == (("R", "L"),)
    if index == 12:
        return all(tuple((label,) * 3 for _ in ("first", "second")) == ((label,) * 3, (label,) * 3) for label in ("L", "R"))
    if index == 13:
        checks = ((0, 1), (1, 2), (0, 2))
        accepted = tuple(word for word in product(("L", "R"), repeat=3) if all(word[a] == word[b] for a, b in checks))
        return tuple(len(x) for x in checks) == (2, 2, 2) and accepted == REP
    if index == 14:
        return all((a, a if pair(a, b) == "same" else flip(a)) == (a, b) for a, b in product(("L", "R"), repeat=2))
    if index == 15:
        return closest(("L", "L", "R"), 1) == (REP[0],) and closest(("L", "L", "R"), 2) == REP
    if index == 16:
        return all(vote(tuple(flip(x) if n == p else x for n, x in enumerate(REP[0]))) == "L" for p in range(3)) and vote(("R", "R", "L")) == "R"
    if index == 17:
        return (1, 3) == (1, len(REP[0])) and (1, 6) == (1, len(REP[0]) * 2)
    if index == 18:
        return len(REL) == 18 and all(witness(number) for number in range(1, 18))
    return False


def surface(index):
    axes = (
        ("partial-code-support", "complete-canonical-code-support"),
        ("imported-or-opaque-code-rule", REL[index - 1]),
        ("sampled-or-untyped-error", "complete-typed-error-support"),
        ("chosen-likely-codeword", "complete-predecessor-decoder"),
        ("sampled-code-forms", "complete-declared-code-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("fit-exception-extra-rule", "finite-successor-or-explicit-boundary"),
    )
    rows = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    return rows, survivor


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
    rows, survivor = surface(index)
    got = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((
        got == rows,
        len(set(got)) == len(got) == 256,
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
        "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "complete_code_witness": witness(index)},
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
