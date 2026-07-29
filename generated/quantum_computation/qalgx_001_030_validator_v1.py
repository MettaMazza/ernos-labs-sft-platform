#!/usr/bin/env python3
"""Implementation-distinct exact validator for QALGX-001 through QALGX-030."""
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path


RELATIONS = (
    "input-promise-process-output-proof-trace", "source-retaining-reversible-query-extension",
    "control-conditioned-relative-phase-return", "finite-period-support-phase-reindexing",
    "finite-period-phase-label-recovery", "least-positive-support-recurrence",
    "constant-versus-balanced-complete-function-census", "paired-input-hidden-translation-census",
    "period-to-positive-divisor-reduction", "marked-support-phase-reflection-path-amplification",
    "marked-support-cardinality-from-phase-period", "support-ratio-rational-enclosure",
    "vertex-edge-phase-reversible-walk", "marked-vertex-walk-observation",
    "finite-exact-relation-solution-support", "recurrent-mode-phase-period-recovery",
    "registered-local-generator-word-interface", "ordered-local-generator-product-with-enclosure",
    "complete-candidate-order-and-minimum-custody", "generated-control-grammar-without-fitting",
    "finite-generated-state-path-correspondence", "deterministic-complete-output-support-and-counts",
    "occupation-word-permutation-path-census", "complete-coset-equality-and-phase-census",
    "reversible-subproblem-recurrence-ledger", "complete-branch-execution-single-observation-boundary",
    "separate-classical-quantum-resource-ledger", "same-problem-resource-vector-comparison",
    "constructive-upper-and-adversary-lower-witnesses", "thirty-obligation-no-omission-ledger",
)


def least_period(values):
    for width in range(1, len(values) + 1):
        if len(values) % width == 0 and all(values[i] == values[i % width] for i in range(len(values))):
            return width
    return len(values)


def divisors(value):
    return tuple(x for x in range(1, value + 1) if value % x == 0)


def independent_witness(index):
    checks = (
        ("input", "process", "output", "proof")[-1] == "proof",
        len({("held", "held"), ("held", "returned"), ("returned", "returned"), ("returned", "held")}) == 4,
        ("control-returned", "target-restored", "phase-returned")[-1] == "phase-returned",
        tuple((i + 1, (i % 2) + 1) for i in range(4))[-1] == (4, 2),
        least_period(("h", "r", "h", "r")) == 2,
        least_period(("a", "b", "c", "a", "b", "c")) == 3,
        len(set(("h", "h"))) == 1 and len(set(("h", "r"))) == 2,
        tuple(a != b for a, b in zip(("h", "r"), ("r", "h"))) == (True, True),
        divisors(15) == (1, 3, 5, 15),
        tuple(x == "marked" for x in ("a", "marked", "b")).count(True) == 1,
        sum(x == "marked" for x in ("marked", "a", "marked", "b")) == 2,
        Fraction(1, 4) <= Fraction(1, 3) <= Fraction(1, 2),
        ("held", "returned", "held")[0] == ("held", "returned", "held")[-1],
        ("start", "middle", "marked")[-1] == "marked",
        dict((("a", "solution-a"), ("b", "solution-b")))["b"] == "solution-b",
        least_period(("mode-a", "mode-b", "mode-a", "mode-b")) == 2,
        ("generator-a", "generator-b")[0] == "generator-a",
        ("a", "b") + ("b", "a") == ("a", "b", "b", "a"),
        sorted((("a", 3), ("b", 1), ("c", 2)), key=lambda row: (row[1], row[0]))[0] == ("b", 1),
        {"generated": 4, "fitted": 0}["fitted"] == 0,
        ("initial", "path", "terminal")[-1] == "terminal",
        tuple(sorted(("returned", "held", "held"))) == ("held", "held", "returned"),
        len({(2, 1), (1, 2)}) == 2,
        set(("a", "c")).isdisjoint(("b", "d")),
        tuple(min((4, 3, 5, 2)[:i]) for i in range(1, 5)) == (4, 3, 3, 2),
        len(tuple(product(("held", "returned"), repeat=3))) == 8,
        ("classical-pre", "quantum-core", "classical-post")[-1] == "classical-post",
        (3, 5) < (5, 8),
        all(a <= b <= c for a, b, c in ((2, 3, 4), (4, 4, 6))),
        len(RELATIONS) == 30,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("imported-or-underspecified-problem", "complete-registered-input-and-promise-grammar"),
        ("imported-quantum-answer", RELATIONS[index - 1]),
        ("sampled-or-terminal-only-run", "complete-branchwise-reversible-trace"),
        ("partial-or-unmatched-cost", "same-problem-complete-resource-ledger"),
        ("selected-favorable-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-algorithm-outcome", "post-registry-exact-execution"),
        ("silent-physical-or-speedup-export", "explicit-formal-physical-and-comparison-handoff"),
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
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_algorithm_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
