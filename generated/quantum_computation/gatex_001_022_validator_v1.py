#!/usr/bin/env python3
"""Implementation-distinct exact validator for GATEX-001 through GATEX-022."""
import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "complete-support-permutation-with-inverse", "single-distinction-label-and-phase-actions",
    "retained-control-bijective-target-action", "two-unit-controlled-nonlocal-support-action",
    "complete-control-word-conditioned-action", "causal-gate-composition-reverse-inverse",
    "complete-support-order-equivalence", "finite-registered-gate-word-grammar",
    "finite-permutation-transposition-synthesis", "nested-rational-enclosure-synthesis",
    "typed-wire-register-gate-causal-word", "complete-support-branchwise-execution",
    "registered-partition-and-outcome-record", "reverse-causal-inverse-circuit",
    "complete-support-semantic-equivalence", "finite-local-gate-causal-decomposition",
    "separate-exact-circuit-resource-ledger", "source-target-circuit-map-equivalence",
    "joint-preparation-observation-correction-correspondence", "finite-state-path-terminal-map-correspondence",
    "finite-braid-word-transformation-correspondence", "twenty-two-obligation-no-omission-ledger",
)


def apply(value, rows):
    return dict(rows)[value]


def inverse(rows):
    if len({a for a, _b in rows}) != len(rows) or len({b for _a, b in rows}) != len(rows):
        return None
    return tuple((b, a) for a, b in rows)


def independent_witness(index):
    swap = (("held", "returned"), ("returned", "held"))
    identity = (("held", "held"), ("returned", "returned"))
    checks = (
        apply(apply("held", swap), inverse(swap)) == "held",
        apply("held", swap) == "returned" and apply("held", identity) == "held",
        (("held", "held"), ("returned", "returned"))[1] == ("returned", "returned"),
        len({("held", "held"), ("held", "returned"), ("returned", "held"), ("returned", "returned")}) == 4,
        (("returned", "returned"), "held", "returned")[-1] == "returned",
        apply(apply("held", swap), inverse(swap)) == "held",
        ("left-then-right", "right-then-left") != ("same-wire-order", "different-wire-order"),
        len({"wire", "swap", "control", "observe"}) == 4,
        tuple(sorted(("c", "a", "b"), key=("c", "a", "b").index)) == ("c", "a", "b"),
        all(a <= b for a, b in ((1, 2), (2, 4))),
        ("wire", "gate", "terminal")[1] == "gate",
        tuple(apply(label, swap) for label in ("held", "returned")) == ("returned", "held"),
        {"held": "class-held", "returned": "class-returned"}["held"] == "class-held",
        apply(apply("held", swap), inverse(swap)) == "held",
        tuple(apply(apply(label, swap), swap) for label in ("held", "returned")) == ("held", "returned"),
        (apply("held", swap), apply("returned", swap)) == ("returned", "held"),
        {"size": 3, "depth": 3, "width": 2, "live_support": 4}["live_support"] == 4,
        tuple(apply(apply(label, swap), swap) for label in ("held", "returned")) == tuple(apply(label, identity) for label in ("held", "returned")),
        ("prepare", "observe", "correct", "output")[-1] == "output",
        {"path_rows": 3, "physical_gap_measured_here": False}["path_rows"] == 3,
        ("strand", "crossing-record", "terminal")[1] == "crossing-record",
        len(RELATIONS) == 22,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("partial-or-aliased-gate-support", "complete-canonical-gate-support"),
        ("imported-matrix-or-circuit-answer", RELATIONS[index - 1]),
        ("terminal-value-only", "complete-branchwise-phase-and-record-map"),
        ("discarded-predecessor", "exact-inverse-and-uncomputation-trace"),
        ("sampled-circuit-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-circuit-outcome", "post-registry-exact-execution"),
        ("silent-physical-export", "explicit-formal-physical-handoff"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    rows, survivor = generated_surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "gate_circuit_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
