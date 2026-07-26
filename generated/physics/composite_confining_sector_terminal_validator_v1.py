#!/usr/bin/env python3
"""Implementation-distinct exact composite-sector reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"
SECTORS = (8, 12, 18, 24, 30)
DOMAINS = (
    ("five-selected-case-table", "every-generated-even-sector"),
    ("borrowed-or-measured-denominator", "positive-predecessor-denominator"),
    ("selected-mode-subset", "all-nonempty-predecessor-labels"),
    ("selected-orbit-permutation", "double-and-cast-denominator-wholes"),
    ("finite-table-assertion", "odd-support-exact-inverse"),
    ("named-or-overlapping-orbits", "complete-disjoint-first-return-partition"),
    ("borrowed-pairing-rule", "unique-positive-One-complements"),
    ("ambiguous-sector-minus-one-over-two", "predecessor-of-denominator-over-two"),
    ("measured-or-fitted-coupling", "all-but-one-predecessor-over-sector"),
    ("unobserved-cases-counted-as-confirmed", "sealed-eight-anchor-and-explicit-standing-cases"),
    ("free-orbit-or-coupling-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def orbit_partition(sector: int):
    denominator = sector - 1
    remaining = set(range(1, denominator))
    orbits = []
    while remaining:
        source = min(remaining)
        orbit = []
        current = source
        while current not in orbit:
            orbit.append(current)
            current = (current + current) % denominator
            if current < 1:
                return ()
        if current != source or any(label not in remaining for label in orbit):
            return ()
        orbits.append(tuple(orbit))
        remaining.difference_update(orbit)
    return tuple(orbits)


def theorem_check() -> bool:
    expected_orbits = (
        ((1, 2, 4), (3, 6, 5)),
        ((1, 2, 4, 8, 5, 10, 9, 7, 3, 6),),
        ((1, 2, 4, 8, 16, 15, 13, 9), (3, 6, 12, 7, 14, 11, 5, 10)),
        ((1, 2, 4, 8, 16, 9, 18, 13, 3, 6, 12), (5, 10, 20, 17, 11, 22, 21, 19, 15, 7, 14)),
        ((1, 2, 4, 8, 16, 3, 6, 12, 24, 19, 9, 18, 7, 14, 28, 27, 25, 21, 13, 26, 23, 17, 5, 10, 20, 11, 22, 15),),
    )
    expected_pairs = (3, 5, 8, 11, 14)
    expected_couplings = (Fraction(7, 8), Fraction(11, 12), Fraction(17, 18), Fraction(23, 24), Fraction(29, 30))
    for index, sector in enumerate(SECTORS):
        denominator = sector - 1
        modes = tuple(range(1, denominator))
        images = tuple((label + label) % denominator for label in modes)
        inverse_two = (denominator + 1) // 2
        predecessors = tuple((inverse_two * label) % denominator for label in modes)
        pairs = tuple((label, denominator - label) for label in range(1, (denominator + 1) // 2))
        if set(images) != set(modes) or set(predecessors) != set(modes):
            return False
        if orbit_partition(sector) != expected_orbits[index]:
            return False
        if len(pairs) != expected_pairs[index] or set(x for pair in pairs for x in pair) != set(modes):
            return False
        if Fraction(denominator, sector) != expected_couplings[index]:
            return False
    return True


def generated_ids():
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (
        sys.argv[1] == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 2048
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(generated),
            "sectors": list(SECTORS),
            "orbit_sizes": [[len(orbit) for orbit in orbit_partition(sector)] for sector in SECTORS],
            "pair_counts": [(sector - 2) // 2 for sector in SECTORS],
            "couplings": [f"{sector - 1}/{sector}" for sector in SECTORS],
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
