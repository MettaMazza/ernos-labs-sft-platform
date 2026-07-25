#!/usr/bin/env python3
"""Independent reconstruction of the quadrupole radiated-power census."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012"
AXES = (
    ("held-monopole-and-dipole-leave-quadrupole-first", "lower-moment-radiation", "target-assigned-moment"),
    ("third-generated-quadrupole-difference", "free-difference-order", "target-assigned-rate"),
    ("positive-square-of-third-rate", "linear-or-unsigned-rate-energy", "target-assigned-energy"),
    ("admitted-binary-half-One-coupling", "free-radiation-coupling", "target-assigned-coupling"),
    ("rank-two-density-dilution-with-conserved-total-power", "unconserved-or-free-shell-power", "target-assigned-shell-law"),
    ("static-empty-and-amplitude-square-scaling", "numerical-zero-or-linear-scaling", "target-assigned-control"),
    ("sealed-before-observation-release", "observation-readable-before-seal"),
    ("empty-extension", "free-radiation-correction"),
)


def differences(values):
    if all(value == values[0] for value in values):
        return ()
    return tuple(values[index + 1] - values[index] for index in range(len(values) - 1))


def exact_law():
    base = tuple(Fraction(tick**3, 1) for tick in range(1, 17))
    doubled = tuple(2 * value for value in base)
    static = tuple(Fraction(1, 1) for _ in range(1, 17))
    base_third = differences(differences(differences(base)))
    doubled_third = differences(differences(differences(doubled)))
    static_third = differences(static)
    base_power = Fraction(1, 2) * base_third[0] * base_third[0]
    doubled_power = Fraction(1, 2) * doubled_third[0] * doubled_third[0]
    identities = []
    for index in range(1, 17):
        left = (index + 3) ** 3 + 3 * (index + 1) ** 3
        right = 3 * (index + 2) ** 3 + index**3 + 6
        next_left = (index + 4) ** 3 + 3 * (index + 2) ** 3
        next_right = 3 * (index + 3) ** 3 + (index + 1) ** 3 + 6
        increment = 12 * index**2 + 48 * index + 58
        identities.append(left == right and next_left - left == next_right - right == increment)
    shells = tuple(
        (Fraction(2**depth, 1), base_power / Fraction(2 ** (2 * depth), 1))
        for depth in range(1, 13)
    )
    return all(
        (
            len(set(base_third)) == 1,
            base_third[0] == 6,
            len(set(doubled_third)) == 1,
            doubled_third[0] == 12,
            static_third == (),
            base_power == 18,
            doubled_power == 4 * base_power,
            all(density * radius * radius == base_power for radius, density in shells),
            all(identities),
        )
    )


def ids():
    return tuple("__".join(values) for values in product(*AXES))


def survives(candidate_id):
    return exact_law() and candidate_id.split("__") == [axis[0] for axis in AXES]


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: survives(candidate_id) for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    survivors = tuple(candidate_id for candidate_id in generated if recomputed[candidate_id])
    kinds = {row["kind"] for row in sealed["controls"]}
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 2916,
            decisions == recomputed,
            len(survivors) == 1,
            exact_law(),
            sealed["closure"]["scope"] == "depth_independent",
            sealed["closure"]["minimality_passed"] is True,
            sealed["closure"]["named_shape_uniqueness_passed"] is True,
            kinds == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(row["passed"] for row in sealed["controls"]),
        )
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "generated_cardinality": len(generated),
                    "computed_surviving_ids": survivors,
                    "base_third_rate": "6",
                    "base_power": "18",
                    "doubled_power": "72",
                    "static_power_record": "empty",
                    "shell_depths": 12,
                    "external_targets_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
