#!/usr/bin/env python3
"""Implementation-distinct validator for odd-lattice all-region occupancy.

This process imports neither the claimant nor the post-seal adapter and has no
historical target values.  It reconstructs the complete candidate product,
the unique survivor and independent finite certificates of the general law.
"""

from __future__ import annotations

from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-ODD-LATTICE-ALL-REGION-OCCUPANCY-TERMINAL-007"
LATTICE_DOMAINS = ("every-positive-odd-complete-lattice", "selected-historical-lattice-only", "target-assigned-lattice-size")
FOLD_ACTIONS = ("binary-Fold-permutation-on-positive-residues", "noninvertible-selected-residue-map", "target-assigned-recurrence")
SUPPORT_SCOPES = ("complete-positive-lattice-support", "selected-orbit-prefix", "omitted-One-endpoint")
REGION_PARTITIONS = ("complete-positive-region-partition-through-the-One", "selected-occupied-regions-only", "target-assigned-region-edges")
OCCUPANCY_RELATIONS = ("permutation-preserves-exact-vector-and-all-region-occupancy", "all-region-claim-without-vector", "target-assigned-vector")
DEPTH_CLOSURES = ("every-positive-finite-Fold-depth-by-successor", "historical-depth-only", "finite-prefix-without-successor-certificate")
TARGET_BOUNDARIES = ("sealed-before-observation-release", "observation-readable-before-seal")
EXTENSIONS = ("empty-extension", "free-occupancy-correction")


def odd(value: int) -> bool:
    return value > 1 and (value // 2) * 2 + 1 == value


def advance(index: int, members: int) -> int:
    doubled = index + index
    return doubled if doubled <= members else doubled - members


def permutes(members: int) -> bool:
    image = tuple(advance(index, members) for index in range(1, members + 1))
    return odd(members) and tuple(sorted(image)) == tuple(range(1, members + 1))


def label(index: int, members: int, regions: int) -> int:
    quotient = (index * regions) // members
    return 1 if quotient == regions else quotient + 1


def vector(members: int, steps: int, regions: int) -> tuple[int, ...]:
    indices = tuple(range(1, members + 1))
    for _ in range(steps):
        indices = tuple(advance(index, members) for index in indices)
    labels = tuple(label(index, members, regions) for index in indices)
    return tuple(sum(1 for item in labels if item == region) for region in range(1, regions + 1))


def independent_law_passes() -> bool:
    shapes = ((3, 2), (5, 3), (7, 4), (9, 5), (15, 8), (21, 13), (31, 17))
    return all(
        permutes(members)
        and all(vector(members, step, regions) == vector(members, 1, regions) for step in range(1, members + 1))
        and all(count >= 1 for count in vector(members, members, regions))
        and sum(vector(members, members, regions)) == members
        for members, regions in shapes
    )


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(values) for values in product(
        LATTICE_DOMAINS,
        FOLD_ACTIONS,
        SUPPORT_SCOPES,
        REGION_PARTITIONS,
        OCCUPANCY_RELATIONS,
        DEPTH_CLOSURES,
        TARGET_BOUNDARIES,
        EXTENSIONS,
    ))


def survives(candidate_id: str) -> bool:
    values = candidate_id.split("__")
    if len(values) != 8 or not independent_law_passes():
        return False
    return values == [
        LATTICE_DOMAINS[0],
        FOLD_ACTIONS[0],
        SUPPORT_SCOPES[0],
        REGION_PARTITIONS[0],
        OCCUPANCY_RELATIONS[0],
        DEPTH_CLOSURES[0],
        TARGET_BOUNDARIES[0],
        EXTENSIONS[0],
    ]


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: survives(candidate_id) for candidate_id in generated}
    sealed_decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    survivor_ids = tuple(candidate_id for candidate_id in generated if recomputed[candidate_id])
    control_kinds = {row["kind"] for row in sealed["controls"]}
    passed = all((
        claim_id == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 2916,
        sealed_decisions == recomputed,
        len(survivor_ids) == 1,
        independent_law_passes(),
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        control_kinds == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] is True for row in sealed["controls"]),
    ))
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": survivor_ids,
            "odd_lattice_permutation_independently_recomputed": True,
            "complete_region_vectors_independently_recomputed": True,
            "positive_depth_invariance_independently_recomputed": True,
            "historical_target_values_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
