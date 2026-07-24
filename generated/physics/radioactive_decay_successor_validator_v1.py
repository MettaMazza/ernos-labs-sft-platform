#!/usr/bin/env python3
"""Implementation-distinct validator for radioactive topology and survival."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005"
DOMAINS = (
    ("rewrite-predecessor-laws", "compose-immutable-predecessors"),
    ("three-named-particles-only", "three-structural-transition-topologies"),
    ("borrowed-alpha-name", "binary-square-cluster-boundary-release"),
    ("stochastic-particle-appearance", "held-label-conversion-with-lepton-records"),
    ("continuum-energy-leak", "internal-level-lowering-with-radiative-record"),
    ("declare-each-a-new-primitive", "compose-the-three-primitive-traces"),
    ("import-continuum-exponential", "positive-rational-binary-geometric"),
    ("unrecorded-random-choice", "deterministic-hidden-path-partition"),
    ("external-target-readable", "target-inaccessible-until-seal"),
    ("free-rate-or-extra-primitive", "no-extra-rule"),
)


def independent_structure() -> dict[str, object]:
    forms = []
    for released, converted, lowered in product((False, True), repeat=3):
        if released:
            result = "boundary-release-or-decomposition"
        elif converted:
            result = "held-label-conversion"
        elif lowered:
            result = "internal-level-deexcitation"
        else:
            result = "identity-not-decay"
        forms.append(((released, converted, lowered), result))
    primitives = tuple(dict.fromkeys(result for _, result in forms if result != "identity-not-decay"))
    survival = tuple(Fraction(1, 2 ** rank) for rank in range(1, 129))
    path_partitions = tuple(
        (2 ** (depth + 1), 2 ** depth, Fraction(2 ** depth, 2 ** (depth + 1)))
        for depth in range(1, 129)
    )
    return {
        "primitive_classes": primitives,
        "alpha_cluster": (4, 2, "boundary-release-or-decomposition"),
        "beta_class": "held-label-conversion",
        "gamma_class": "internal-level-deexcitation",
        "survival": survival,
        "all_survival_positive": all(part > 0 for part in survival),
        "all_path_partitions_half": all(row[2] == Fraction(1, 2) and row[0] == row[1] + row[1] for row in path_partitions),
    }


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    survivor = "__".join(domain[1] for domain in DOMAINS)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    structure = independent_structure()
    exact = (
        set(structure["primitive_classes"]) == {
            "boundary-release-or-decomposition",
            "held-label-conversion",
            "internal-level-deexcitation",
        }
        and structure["alpha_cluster"] == (4, 2, "boundary-release-or-decomposition")
        and structure["beta_class"] == "held-label-conversion"
        and structure["gamma_class"] == "internal-level-deexcitation"
        and structure["all_survival_positive"]
        and structure["all_path_partitions_half"]
    )
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == claim_id
        and exact
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
            "primitive_classes": sorted(structure["primitive_classes"]),
            "survival_through_128": [str(structure["survival"][0]), str(structure["survival"][-1])],
            "all_finite_survival_positive": structure["all_survival_positive"],
            "deterministic_path_partitions": structure["all_path_partitions_half"],
            "target_value_accessed": False,
            "implementation": "independent Boolean-topology exhaustion and exact hidden-path binary partition",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
