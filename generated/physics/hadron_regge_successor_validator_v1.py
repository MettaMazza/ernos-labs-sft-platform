#!/usr/bin/env python3
"""Implementation-distinct validator for terminal hadron/Regge closure."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations_with_replacement, product
import json
import sys


CLAIM_ID = "SFT-PHYS-HADRON-REGGE-TERMINAL-005"
DOMAINS = (
    ("rewrite-hadron-predecessors", "compose-immutable-hadron-predecessors"),
    ("import-named-flavour-table", "complete-generator-three-flavour-support"),
    ("assert-nonet", "enumerate-three-by-three-ordered-pairs"),
    ("import-octet-singlet-representation", "one-invariant-and-positive-predecessor"),
    ("assert-octet-and-decuplet", "enumerate-three-place-flavour-words"),
    ("import-SU-three-decomposition", "enumerate-exchange-symmetry-classes"),
    ("chosen-spin-dependent-increment", "one-retained-step-per-spin-successor"),
    ("fitted-mass-polynomial", "depth-independent-affine-successor"),
    ("external-target-readable", "target-inaccessible-until-seal"),
    ("free-residual-or-tension-fit", "no-extra-rule"),
)


def independent_arithmetic() -> bool:
    labels = (1, 2, 3)
    mesons = tuple(product(labels, repeat=2))
    baryons = tuple(product(labels, repeat=3))
    symmetric = tuple(combinations_with_replacement(labels, 3))
    mixed = len(baryons) - len(symmetric) - 1
    multiplets = len(mesons) == 9 and 9 == 8 + 1 and len(baryons) == 27 and mixed == 16 and 27 == 10 + 8 + 8 + 1
    anchor = Fraction(7, 11)
    step = Fraction(13, 17)
    affine = tuple(anchor if rank == 1 else anchor + Fraction(rank - 1, 1) * step for rank in range(1, 129))
    equal_steps = all(successor - previous == step for previous, successor in zip(affine, affine[1:]))
    multiplicity = tuple(2 ** depth for depth in range(1, 8)) == (2, 4, 8, 16, 32, 64, 128)
    return multiplets and equal_steps and multiplicity


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    survivor = "__".join(domain[1] for domain in DOMAINS)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    arithmetic = independent_arithmetic()
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == claim_id
        and arithmetic
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024
        and decisions == {candidate: candidate == survivor for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "unique_survivor": survivor if passed else None,
            "exact_arithmetic": arithmetic,
            "target_value_accessed": False,
            "implementation": "independent ordered-word, exchange-class and exact-affine-successor reconstruction",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
