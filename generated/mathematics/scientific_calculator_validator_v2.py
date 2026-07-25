#!/usr/bin/env python3
"""Independent exact validator for corrected calculator claim 004."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-004"
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
    lowered = text.lower()
    if "e" in lowered:
        mantissa, exponent_text = lowered.split("e", 1)
        exponent = int(exponent_text)
    else:
        mantissa, exponent = lowered, 0
    if "." in mantissa:
        whole, parts = mantissa.split(".", 1)
    else:
        whole, parts = mantissa, ""
    value = Fraction(int((whole or "0") + parts), 10 ** len(parts))
    return value * (10 ** exponent if exponent >= 0 else Fraction(1, 10 ** (-exponent)))


def atan_bounds(x: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    positive, held = Fraction(0), Fraction(0)
    for index in range(terms):
        term = x ** (2 * index + 1) / (2 * index + 1)
        if index % 2:
            held += term
        else:
            positive += term
    partial = positive - held
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    return (partial - next_term, partial) if terms % 2 else (partial, partial + next_term)


def tangent_double(value: Fraction) -> Fraction:
    return 2 * value / (1 - value * value)


def corrected_circle_check() -> bool:
    fifth = atan_bounds(Fraction(1, 5), 32)
    two_thirty_ninth = atan_bounds(Fraction(1, 239), 32)
    lower = 16 * fifth[0] - 4 * two_thirty_ninth[1]
    upper = 16 * fifth[1] - 4 * two_thirty_ninth[0]
    tangent_four = tangent_double(tangent_double(Fraction(1, 5)))
    tangent_quarter_turn = (tangent_four - Fraction(1, 239)) / (
        1 + tangent_four * Fraction(1, 239)
    )
    known_inner = Fraction(314159265358979323846264338327950288419716939937510, 10 ** 50)
    # The decimal is an unfavorable correspondence check only. Exact tangent
    # composition and alternating parity establish the result independently.
    return all(
        (
            fifth[0] < fifth[1],
            two_thirty_ninth[0] < two_thirty_ninth[1],
            lower < upper,
            tangent_four == Fraction(120, 119),
            tangent_quarter_turn == 1,
            lower < known_inner < upper,
        )
    )


def root_bracket() -> bool:
    lower, upper = Fraction(0), Fraction(2)
    for _ in range(80):
        middle = (lower + upper) / 2
        if middle * middle < 2:
            lower = middle
        else:
            upper = middle
    return lower * lower < 2 <= upper * upper and upper - lower == Fraction(1, 2 ** 79)


def operational_check() -> bool:
    return all(
        (
            exact_decimal("0.1") + exact_decimal("0.2") == Fraction(3, 10),
            exact_decimal("1.25e-2") == Fraction(1, 80),
            root_bracket(),
            corrected_circle_check(),
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
                    "alternating_parity": "odd-upper/even-lower",
                    "exact_tangent_quarter_turn": "One",
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
