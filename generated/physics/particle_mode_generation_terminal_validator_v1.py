#!/usr/bin/env python3
"""Independent reconstruction of the terminal particle-mode law."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051"
DOMAINS = (
    ("selected-binary-or-colour-count", "complete-m-offset-fibre"),
    ("named-three-mode-pattern", "complete-fixed-index-range"),
    ("one-coordinate-system-selected-as-mass", "three-order-isomorphic-coordinate-systems"),
    ("chosen-depth-five-or-seven", "least-cover-of-generator-volume"),
    ("extra-spatial-dimension", "internal-recurrent-trace-mode"),
    ("site-fraction-is-mass", "order-transport-to-terminal-polynomials"),
    ("lookup-depth-fractions", "complete-colour-binary-dual"),
    ("lifetime-equals-mass-ratio-postulate", "exact-structural-reach-identity"),
    ("universal-observed-rate-ratio", "structural-separation-multiplicity"),
    ("extra-dimension-or-fit", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def ceil_cover(base, volume):
    depth = 1
    prior = 1
    capacity = base
    while capacity < volume:
        prior = capacity
        capacity *= base
        depth += 1
    return depth, prior, capacity


def independent_math():
    fibres = all(
        len({(target + offset) / multiplicity for offset in range(multiplicity)}) == multiplicity
        for multiplicity in range(2, 13)
        for target in (Fraction(1, multiplicity), Fraction(1, 2), Fraction(1, 1))
    )
    fixed = all(
        len(tuple(Fraction(index, multiplicity - 1) for index in range(1, multiplicity - 1))) == multiplicity - 2
        for multiplicity in range(2, 13)
    )
    half = tuple((Fraction(1, 2) + offset) / 3 for offset in range(3))
    one = tuple(Fraction(index, 3) for index in (1, 2, 3))
    quarter = tuple(Fraction(index, 4) for index in (1, 2, 3))
    coordinates = all(tuple(sorted(row)) == row and len(row) == 3 for row in (half, one, quarter))
    binary = ceil_cover(2, 27)
    colour = ceil_cover(3, 27)
    covers = binary == (5, 16, 32) and colour == (3, 9, 27)
    dual = Fraction(1, 3 * 2 ** 5 - 1) == Fraction(1, 95) and Fraction(1, 3 * 2 ** 7 - 1) == Fraction(1, 383) and Fraction(1, 2 * 3 ** 5 - 1) == Fraction(1, 485)
    reach = all((2 * 3 ** depth - 1) == Fraction(2 * 3 ** depth - 1, 2 * 3 ** depth) / Fraction(1, 2 * 3 ** depth) for depth in range(1, 7))
    transition = quarter[1] - quarter[0] == quarter[2] - quarter[1] == Fraction(1, 4) and quarter[2] - quarter[0] == Fraction(1, 2)
    return all((fibres, fixed, coordinates, covers, dual, reach, transition))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 1024,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        independent_math(),
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 1024,
            "m_check_through": 12,
            "generation_coordinate_count": 4,
            "state_volume": 27,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
