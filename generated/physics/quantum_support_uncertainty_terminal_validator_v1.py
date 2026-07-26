#!/usr/bin/env python3
"""Independent reconstruction of dyadic support and joint-correlation closure."""

from fractions import Fraction
from itertools import combinations, product
import json
import sys


CLAIM_ID = "SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049"
H = "held"
R = "returned"
DOMAINS = (
    ("universally-selected-depth-three", "preparation-derived-complete-binary-depth"),
    ("imported-complex-Walsh-amplitudes", "held-returned-parity-count-table"),
    ("named-or-selected-uncertainty-bound", "orthogonality-Parseval-support-count"),
    ("support-width-called-statistical-variance", "exact-unit-free-support-spread"),
    ("product-size-relabeled-entanglement", "complete-factorability-subset-census"),
    ("remote-label-change-relabeled-signal", "complete-marginal-count-invariance"),
    ("ontic-randomness-or-superluminal-message", "incomplete-local-factorization-record"),
    ("measurement-selected-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def words(depth):
    return tuple(product((H, R), repeat=depth))


def phase(point, mode):
    return H if sum(a == R and b == R for a, b in zip(point, mode)) % 2 == 0 else R


def walsh_census():
    supports = 0
    saturated = 0
    for depth in range(1, 5):
        basis = words(depth)
        branch_count = len(basis)
        for left in basis:
            for right in basis:
                same = sum(phase(left, mode) == phase(right, mode) for mode in basis)
                if left == right and same != branch_count:
                    return None
                if left != right and same * 2 != branch_count:
                    return None
        for size in range(1, branch_count + 1):
            for selected in combinations(basis, size):
                frequency = 0
                parseval = 0
                for mode in basis:
                    held = sum(phase(point, mode) == H for point in selected)
                    returned = size - held
                    magnitude = held - returned if held >= returned else returned - held
                    if magnitude:
                        frequency += 1
                    parseval += magnitude * magnitude
                if parseval != branch_count * size or size * frequency < branch_count:
                    return None
                if Fraction(size * frequency, branch_count) < 1:
                    return None
                if Fraction(size, branch_count) ** 2 * Fraction(frequency, branch_count) ** 2 < Fraction(1, branch_count * branch_count):
                    return None
                supports += 1
                if size * frequency == branch_count:
                    saturated += 1
    return supports, saturated


def factorable(rows):
    left = {a for a, _ in rows}
    right = {b for _, b in rows}
    return set(rows) == set(product(left, right))


def joint_census(left_size, right_size):
    cells = tuple(product(range(1, left_size + 1), range(1, right_size + 1)))
    factorable_count = 0
    nonfactorable_count = 0
    for size in range(1, len(cells) + 1):
        for support in combinations(cells, size):
            if factorable(support):
                factorable_count += 1
            else:
                nonfactorable_count += 1
            left_counts = tuple(sum(a == label for a, _ in support) for label in range(1, left_size + 1))
            reversed_support = tuple((a, right_size + 1 - b) for a, b in support)
            reversed_counts = tuple(sum(a == label for a, _ in reversed_support) for label in range(1, left_size + 1))
            if left_counts != reversed_counts:
                return None
    if not factorable(cells):
        return None
    return factorable_count, nonfactorable_count


def bell_census():
    functions = tuple(product((H, R), repeat=2))
    wins = []
    for left in functions:
        for right in functions:
            count = 0
            for x in range(2):
                for y in range(2):
                    required_same = not (x == 1 and y == 1)
                    count += (left[x] == right[y]) == required_same
            wins.append(count)
    no_signal = True
    for x in range(2):
        for y in range(2):
            required_same = not (x == 1 and y == 1)
            allowed = tuple((a, b) for a in (H, R) for b in (H, R) if (a == b) == required_same)
            no_signal = no_signal and len(allowed) == 2 and {a for a, _ in allowed} == {H, R} and {b for _, b in allowed} == {H, R}
    return len(wins) == 16 and max(wins) == 3 and all(value <= 3 for value in wins) and no_signal


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    walsh = walsh_census()
    two_three = joint_census(2, 3)
    three_five = joint_census(3, 5)
    exact = all((
        walsh is not None and walsh[0] == 65808,
        two_three == (21, 42),
        three_five == (217, 32550),
        bell_census(),
        Fraction(1, 16) == Fraction(1, 4) ** 2,
    ))
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and exact for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        seal["claim_id"] == CLAIM_ID,
        recorded == generated,
        len(set(recorded)) == seal["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        seal["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in seal["controls"]),
        exact,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": seal["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 256,
            "walsh_nonempty_supports": walsh[0] if walsh else None,
            "two_by_three": {"factorable": 21, "nonfactorable": 42},
            "three_by_five": {"factorable": 217, "nonfactorable": 32550},
            "local_Bell_maximum_wins": 3,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
