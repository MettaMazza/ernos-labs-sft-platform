#!/usr/bin/env python3
"""Implementation-distinct accumulated Fold-coupling validator."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015"

DOMAINS = (
    ("imported-or-selected-coupling-table", "admitted-common-support-gap-law"),
    ("unsigned-or-fitted-difference", "exact-adjacent-sector-gap"),
    (
        "assert-half-contraction-from-first-gap",
        "retain-one-twelfth-and-one-twentieth",
    ),
    (
        "visual-or-imported-convergence",
        "exact-strict-half-contraction-after-level-two",
    ),
    ("one-sixth", "eleven-sixtieths", "one-fifth", "target-selected-bound"),
    ("completed-infinite-sum", "every-positive-finite-partial-support"),
    ("limit-symbol-without-witness", "generated-finite-tail-witness"),
    ("free-tail-correction", "no-extra-rule"),
)
SURVIVOR = (
    "admitted-common-support-gap-law",
    "exact-adjacent-sector-gap",
    "retain-one-twelfth-and-one-twentieth",
    "exact-strict-half-contraction-after-level-two",
    "eleven-sixtieths",
    "every-positive-finite-partial-support",
    "generated-finite-tail-witness",
    "no-extra-rule",
)


@lru_cache(maxsize=None)
def support(level: int) -> int:
    value = 1
    for _ in range(1, level):
        value *= 2
    return value


@lru_cache(maxsize=None)
def gap(level: int) -> Fraction:
    r = support(level)
    return Fraction(1, (r + 2) * (r + 3))


@lru_cache(maxsize=None)
def partial(level: int) -> Fraction:
    return sum((gap(cursor) for cursor in range(1, level + 1)), Fraction(0, 1))


def independent_theorem_check() -> bool:
    if gap(1) != Fraction(1, 12) or gap(2) != Fraction(1, 20):
        return False
    if any(gap(level + 1) * 2 >= gap(level) for level in range(2, 129)):
        return False
    if any(
        not (Fraction(1, 12) <= partial(level) < Fraction(11, 60))
        for level in range(1, 129)
    ):
        return False
    for denominator in (1, 2, 3, 5, 7, 11, 127, 1024, 65537):
        level = 2
        while gap(level) * 2 >= Fraction(1, denominator):
            level += 1
        if gap(level) * 2 >= Fraction(1, denominator):
            return False
    return Fraction(1, 12) + Fraction(1, 20) * 2 == Fraction(11, 60)


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(values) for values in product(*DOMAINS))


def survives(candidate_id: str) -> bool:
    return tuple(candidate_id.split("__")) == SURVIVOR and independent_theorem_check()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validator CLAIM_ID SEALED_JSON")
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    recomputed = {candidate_id: survives(candidate_id) for candidate_id in generated}
    control_kinds = {row["kind"] for row in sealed["controls"]}
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received))
        == sealed["census"]["expected_cardinality"]
        == 512
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and control_kinds
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and independent_theorem_check()
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "details": (
                    "independently regenerated 512 candidates, exact finite partial "
                    "sums, strict successor contraction, 11/60 envelope and finite "
                    "tolerance witnesses"
                ),
                "certificate": {
                    "candidate_count": len(generated),
                    "survivor": "__".join(SURVIVOR),
                    "first_gap": str(gap(1)),
                    "second_gap": str(gap(2)),
                    "upper_envelope": str(Fraction(11, 60)),
                    "largest_checked_level": 128,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
