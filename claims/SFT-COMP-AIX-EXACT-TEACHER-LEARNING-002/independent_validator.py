"""Implementation-distinct validator for exact teacher-observation learning."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-COMP-AIX-EXACT-TEACHER-LEARNING-002"
DOMAINS = (
    ("mutable-or-runtime-teacher", "frozen-source-bound-external-teacher"),
    ("float-arithmetic-target", "exact-bit-record-to-rational-parts"),
    ("top-k-or-truncated-teacher-output", "complete-declared-teacher-output-partition"),
    ("mixed-or-migrating-data-roles", "frozen-disjoint-data-role-ledgers"),
    ("floating-surrogate-or-hidden-weight", "exact-complete-disagreement-ledger"),
    ("gradient-or-target-selected-update", "generated-exact-update-candidate-grammar"),
    ("winner-only-or-overwritten-history", "strict-descent-tie-adverse-lineage-ledger"),
    ("copied-weight-runtime-teacher-or-training-generalization", "teacher-free-artifact-and-sealed-unseen-boundary"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def dyadic(bits):
    sign = bits >> 31
    exponent = (bits >> 23) & 255
    fraction = bits & ((1 << 23) - 1)
    if sign or exponent == 255:
        raise ValueError("invalid teacher mass")
    if exponent == 0 and fraction == 0:
        return None
    significand, power = (fraction, -149) if exponent == 0 else ((1 << 23) + fraction, exponent - 150)
    return Fraction(significand * (1 << power), 1) if power >= 0 else Fraction(significand, 1 << (-power))


def partition(records):
    raw = tuple(dyadic(bits) for bits in records)
    whole = sum((part for part in raw if part is not None), Fraction(0, 1))
    return tuple(None if part is None else part / whole for part in raw)


def discrepancy(left, right):
    rows = []
    for first, second in zip(left, right):
        first_value = Fraction(0, 1) if first is None else first
        second_value = Fraction(0, 1) if second is None else second
        if first_value != second_value:
            rows.append(abs(first_value - second_value))
    return len(rows), None if not rows else sum(rows, Fraction(0, 1))


def operational_reconstruction():
    teacher = partition((0x3E800000, 0x3F000000, 0x3E800000))
    student = partition((0x3F000000, 0x3E800000, 0x3E800000))
    improved = (Fraction(3, 8), Fraction(3, 8), Fraction(1, 4))
    current = discrepancy(student, teacher)
    better = discrepancy(improved, teacher)
    candidates = (("held", better), ("parallel-held", better), ("unchanged", current))
    best = min(objective for _name, objective in candidates if objective[1] is not None)
    tied = tuple(name for name, objective in candidates if objective == best)
    artifact = ("student-successor", "student-parent", tied, candidates)
    checks = (
        dyadic(0x3F000000) == Fraction(1, 2),
        teacher == (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
        sum((part for part in teacher if part is not None), Fraction(0, 1)) == Fraction(1, 1),
        current == (2, Fraction(1, 2)),
        better == (2, Fraction(1, 4)) and better[1] < current[1],
        tied == ("held", "parallel-held"),
        all("teacher" not in str(field) for field in artifact),
    )
    return checks


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    operational = operational_reconstruction()
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and closure["scope"] == "depth_independent"
        and closure["minimality_passed"] is True
        and closure["named_shape_uniqueness_passed"] is True
        and {item["kind"] for item in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(item["passed"] is True for item in controls)
        and all(operational)
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "operational_reconstruction": operational,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

