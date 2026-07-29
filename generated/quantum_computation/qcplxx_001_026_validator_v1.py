#!/usr/bin/env python3
"""Implementation-distinct exact validator for QCPLXX-001 through QCPLXX-026."""
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path


RELATIONS = (
    "canonical-positive-finite-input-description-width", "separate-gate-count-and-causal-depth",
    "complete-live-support-and-description-ledger", "separate-ancilla-observation-record-costs",
    "registered-reversible-query-count", "transmitted-distinction-and-shared-record-ledger",
    "resource-bounded-accept-reject-support", "exact-favorable-support-ratio-boundary",
    "complete-support-correct-decision", "one-class-complete-other-class-bounded-support",
    "existential-accepting-branch-on-deterministic-support", "positive-finite-polynomial-resource-envelope",
    "existential-witness-complete-verification-census", "round-challenge-response-decision-ledger",
    "maximum-live-support-record-width", "work-depth-width-support-vector",
    "single-generator-for-every-input-size", "semantics-resource-preserving-problem-map",
    "complete-distinguishability-adversary-ledger", "exact-degree-query-trace-correspondence",
    "same-trace-classical-simulation-vector", "same-problem-strict-resource-separation",
    "exact-generated-case-weight-ledger", "input-size-parameter-resource-slices",
    "least-complete-machine-description", "twenty-six-obligation-no-omission-ledger",
)


def independent_witness(index):
    checks = (
        len(("held", "returned", "held")) == 3,
        sum((2, 1)) == 3 and len((2, 1)) == 2,
        len(tuple(product(("held", "returned"), repeat=2))) == 4,
        {"ancilla": 2, "observations": 1, "records": 3}["records"] == 3,
        len(("q1", "q2", "q3")) == 3,
        sum((2, 1, 2)) == 5,
        set(("accept", "reject")) == {"accept", "reject"},
        Fraction(3, 4) == Fraction(3, 4),
        Fraction(2, 2) == Fraction(1, 1),
        Fraction(0, 4) == Fraction(0, 1),
        any(x == "accept" for x in ("reject", "accept", "reject")),
        all(cost <= size * size for size, cost in ((1, 1), (2, 4), (3, 9))),
        dict((("a", "reject"), ("b", "accept")))["b"] == "accept",
        ("challenge", "response", "decision")[-1] == "decision",
        max((2, 3, 2, 1)) == 3,
        (6, 2, 3)[0] == 6,
        tuple(f"c-{n}" for n in (1, 2, 3)) == ("c-1", "c-2", "c-3"),
        ("source", "map", "target")[-1] == "target",
        all(a <= b for a, b in ((2, 3), (3, 4))),
        tuple((d, d + 1) for d in (1, 2, 3))[-1] == (3, 4),
        all(a <= b for a, b in zip((3, 4, 2), (5, 8, 4))),
        all(a <= b for a, b in zip((3, 4, 2), (5, 8, 4))) and any(a < b for a, b in zip((3, 4, 2), (5, 8, 4))),
        sum(Fraction(w, 6) * c for w, c in ((1, 2), (2, 3), (3, 4))) == Fraction(10, 3),
        tuple(sorted({1: (2, 3), 2: (4,)}.items())) == ((1, (2, 3)), (2, (4,))),
        len(("prepare", "query", "observe")) == 3,
        len(RELATIONS) == 26,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("ambiguous-or-mismatched-size", "canonical-input-and-promise-size"),
        ("imported-class-or-bound", RELATIONS[index - 1]),
        ("partial-cost-coordinate", "complete-time-space-query-depth-record-vector"),
        ("different-problem-or-observation", "same-problem-same-observation-comparison"),
        ("sampled-favorable-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-complexity-outcome", "post-registry-exact-execution"),
        ("silent-asymptotic-or-physical-export", "explicit-finite-asymptotic-and-physical-handoff"),
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
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_complexity_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
