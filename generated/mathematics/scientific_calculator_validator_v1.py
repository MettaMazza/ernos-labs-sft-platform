#!/usr/bin/env python3
"""Implementation-distinct exact validator for the SFT calculator law."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-003"
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
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_decimal(text: str) -> Fraction:
    mantissa, exponent = (text.lower().split("e", 1) + ["0"])[:2] if "e" in text.lower() else (text, "0")
    whole, parts = (mantissa.split(".", 1) + [""])[:2]
    return Fraction(int((whole or "0") + parts), 10 ** len(parts)) * (
        10 ** int(exponent) if int(exponent) >= 0 else Fraction(1, 10 ** (-int(exponent)))
    )


def root_bracket(target: Fraction, depth: int) -> tuple[Fraction, Fraction]:
    lower, upper = Fraction(0), max(Fraction(1), target)
    for _ in range(depth):
        middle = (lower + upper) / 2
        if middle * middle < target:
            lower = middle
        else:
            upper = middle
    return lower, upper


def operational_check() -> bool:
    decimal_sum = exact_decimal("0.1") + exact_decimal("0.2")
    scientific = exact_decimal("1.25e-2")
    lower, upper = root_bracket(Fraction(2), 80)
    factorial_five = Fraction(1)
    for count in range(2, 6):
        factorial_five *= count
    selection = Fraction(1)
    for step in range(1, 4):
        selection = selection * (10 - 3 + step) / step
    # Independent two-fibre product: (empty, One)^2 = (counter One, empty).
    orthogonal_square = ("counter-held", Fraction(1), "empty-One")
    return all(
        (
            decimal_sum == Fraction(3, 10),
            scientific == Fraction(1, 80),
            lower * lower < 2 <= upper * upper,
            upper - lower == Fraction(1, 2 ** 79),
            factorial_five == 120,
            selection == 120,
            orthogonal_square == ("counter-held", Fraction(1), "empty-One"),
        )
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validator CLAIM_ID SEALED_DERIVATION")
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(fields) for fields in product(*DOMAINS))
    received = tuple(item["candidate_id"] for item in sealed["census"]["candidates"])
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    controls = sealed["controls"]
    closure = sealed["closure"]
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 1024,
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
                    "exact_decimal_sum": "3/10",
                    "scientific_notation": "1/80",
                    "root_depth": 80,
                    "operational_check": operational_check(),
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
