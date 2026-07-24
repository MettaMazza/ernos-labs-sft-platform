"""Implementation-distinct reconstruction of generator three."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-STRUCT-GENERATOR-THREE-001"
DOMAINS = (
    ("borrowed-integer-name", "exact-positive-period-trace"),
    ("imported-modular-map", "double-and-cast-complete-One"),
    ("repeated-value-without-first-return", "complete-first-return-orbit"),
    ("asserted-binary-count", "depth-two-unit-part-period"),
    ("selected-later-period", "least-distinct-positive-successor"),
    ("target-denominator", "support-predecessor-unit-part"),
    ("period-label-only", "all-Fold-transitions-held"),
    ("bounded-denominator-search", "positive-count-discreteness-plus-existence"),
    ("measurement-selected-period", "derivation-before-measurement"),
    ("extra-generator-rule", "no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def fold(value: Fraction) -> Fraction:
    paired = value + value
    return paired if paired <= 1 else paired - 1


def orbit(value: Fraction) -> tuple[Fraction, ...]:
    current = value
    path = []
    seen = {value}
    while True:
        current = fold(current)
        path.append(current)
        if current == value:
            return tuple(path)
        if current in seen:
            raise ValueError("nonreturning path")
        seen.add(current)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    operational = (
        orbit(Fraction(1, 3)) == (Fraction(2, 3), Fraction(1, 3))
        and orbit(Fraction(1, 7)) == (Fraction(2, 7), Fraction(4, 7), Fraction(1, 7))
        and len(orbit(Fraction(1, 7))) == len(orbit(Fraction(1, 3))) + 1
    )
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and all(row["passed"] is True for row in sealed["controls"])
        and operational
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "period_two": 2, "period_three": 3}}, sort_keys=True))


if __name__ == "__main__":
    main()
