#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
from math import comb, prod
import json
import sys


CLAIM_ID = "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045"
DOMAINS = (
    ("named-particle-species", "preserving-versus-alternating-held-trace"),
    ("selected-occupancy-cap", "one-cell-distinction-exclusion"),
    ("finite-selected-ceiling", "every-positive-finite-multiplicity-admitted"),
    ("continuum-statistical-distribution", "complete-exact-dyadic-occupation-census"),
    ("imaginary-signed-phase", "typed-one-turn-two-turn-held-orbits"),
    ("independent-boson-postulate", "alternating-pair-preserves-exchange"),
    ("measured-or-fitted-temperature", "first-exact-crossing-of-forced-m-minus-one-over-m-share"),
    ("asserted-macroscopic-ground-mode", "unique-minimum-throw-shared-ground-word"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def occupations(particles, levels, alternating):
    cap = 1 if alternating else particles
    rows = []

    def walk(prefix, remaining, index):
        if index == levels - 1:
            if remaining <= cap:
                rows.append(prefix + (remaining,))
            return
        for occupied in range(min(cap, remaining) + 1):
            walk(prefix + (occupied,), remaining - occupied, index + 1)

    walk((), particles, 0)
    return tuple(rows)


def ground_share(particles, levels, depth):
    rows = occupations(particles, levels, False)
    raw = tuple(2 ** (levels - index - 1) for index in range(levels))
    scores = tuple(prod(raw[index] ** (depth * occupied) for index, occupied in enumerate(row)) for row in rows)
    total = sum(scores)
    ground = (particles,) + (0,) * (levels - 1)
    return Fraction(scores[rows.index(ground)], total)


def check():
    for levels in range(1, 7):
        for particles in range(1, 7):
            bosons = occupations(particles, levels, False)
            fermions = occupations(particles, levels, True)
            if len(bosons) != comb(particles + levels - 1, particles):
                return False
            if len(fermions) != (comb(levels, particles) if particles <= levels else 0):
                return False
            energies = tuple((row, sum((index + 1) * occupied for index, occupied in enumerate(row))) for row in bosons)
            least = min(value for _, value in energies)
            if tuple(row for row, value in energies if value == least) != ((particles,) + (0,) * (levels - 1),):
                return False
    for factor in range(2, 6):
        threshold = Fraction(factor - 1, factor)
        for levels in range(2, 6):
            for particles in range(2, 7):
                forms = occupations(particles, levels, False)
                depth = 1
                while 2 ** depth < max(1, (len(forms) - 1) * (factor - 1)):
                    depth += 1
                shares = tuple(ground_share(particles, levels, d) for d in range(1, depth + 2))
                crossings = tuple(index + 1 for index, share in enumerate(shares) if share >= threshold)
                if not crossings:
                    return False
                first = crossings[0]
                if first > 1 and not shares[first - 2] < threshold:
                    return False
    return True


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    valid = check()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            seal["claim_id"] == CLAIM_ID,
            recorded == generated,
            len(set(recorded)) == seal["census"]["expected_cardinality"] == 256,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            seal["closure"]["scope"] == "depth_independent",
            {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(row["passed"] for row in seal["controls"]),
            valid,
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": seal["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": 256,
                    "two_spin_census": {"preserving": 3, "alternating": 1},
                    "binary_lock_share": "1/2",
                    "survivor": "__".join(SURVIVOR),
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
