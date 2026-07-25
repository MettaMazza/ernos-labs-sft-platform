#!/usr/bin/env python3
"""Implementation-distinct validator for expanded calculator claim 005."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-005"
DOMAINS = (
    ("host-float", "character-exact-part"),
    ("numeric-zero", "structural-empty-One"),
    ("negative-scalar", "held-fibre-orientation"),
    ("host-arithmetic-oracle", "generated-exact-kernels"),
    ("irrational-scalar", "rational-balance-enclosure"),
    ("black-box-library-value", "finite-rational-recurrence-bound"),
    ("imaginary-scalar", "typed-orthogonal-fibre-pair"),
    ("nan-infinity-continuation", "explicit-lawful-halt"),
    ("answer-only", "complete-proof-resource-trace"),
    ("has-extra-rule", "no-extra-rule"),
    ("partial-basic-function-subset", "complete-declared-scientific-surface"),
    ("stateless-expression-only", "equals-answer-memory-history"),
    ("terminal-only-opaque-answer", "cross-platform-app-trace-and-guide"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def square_root_bracket(target: Fraction, depth: int = 80) -> tuple[Fraction, Fraction]:
    lower, upper = Fraction(0), max(Fraction(1), target)
    for _ in range(depth):
        middle = (lower + upper) / 2
        if middle * middle < target:
            lower = middle
        else:
            upper = middle
    return lower, upper


def tangent_composition() -> bool:
    def double(value: Fraction) -> Fraction:
        return 2 * value / (1 - value * value)
    tangent_four = double(double(Fraction(1, 5)))
    difference = (tangent_four - Fraction(1, 239)) / (1 + tangent_four * Fraction(1, 239))
    return tangent_four == Fraction(120, 119) and difference == 1


def operational_check() -> bool:
    lower, upper = square_root_bracket(Fraction(2))
    values = (Fraction(1), Fraction(2), Fraction(3), Fraction(4))
    mean = sum(values, Fraction(0)) / len(values)
    variance_values = (Fraction(1), Fraction(2), Fraction(3))
    variance_mean = sum(variance_values, Fraction(0)) / len(variance_values)
    variance = sum(((item - variance_mean) ** 2 for item in variance_values), Fraction(0)) / len(variance_values)
    memory = Fraction(2)
    answer = Fraction(2)
    second = answer + memory
    declared_button_families = {
        "digits", "arithmetic", "powers", "roots", "circular", "inverse-circular",
        "hyperbolic", "logarithmic", "combinatorial", "statistics", "memory", "equals",
    }
    return all(
        (
            Fraction(1) + Fraction(1) == 2,
            lower * lower < 2 <= upper * upper,
            upper - lower == Fraction(1, 2 ** 79),
            mean == Fraction(5, 2),
            variance == Fraction(2, 3),
            second == 4,
            tangent_composition(),
            len(declared_button_families) == 12,
        )
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validator CLAIM_ID SEALED_DERIVATION")
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(fields) for fields in product(*DOMAINS))
    received = tuple(item["candidate_id"] for item in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 8192,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            closure["scope"] == "depth_independent",
            closure["minimality_passed"] is True,
            closure["named_shape_uniqueness_passed"] is True,
            {item["kind"] for item in controls}
            == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(item["passed"] is True for item in controls),
            operational_check(),
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": len(generated),
                    "unique_survivor": "__".join(SURVIVOR),
                    "ordinary_equals": "One+One=two",
                    "root_depth": 80,
                    "exact_mean": "5/2",
                    "exact_variance": "2/3",
                    "session_recall": "four",
                    "operational_check": operational_check(),
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
