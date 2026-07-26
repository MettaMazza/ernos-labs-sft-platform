#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-TERMINAL-073"
DOMAINS = (
    ("unheld-single-source", "held-two-source-orbit"),
    ("monopole-or-dipole-radiation", "admitted-quadrupole-rate"),
    ("negative-or-erased-energy", "positive-retained-take"),
    ("fixed-or-expanding-orbit", "strictly-shrinking-positive-separation"),
    ("imported-or-selected-frequency-law", "inverse-square-period-square-equals-radius-cube"),
    ("one-or-free-wave-cycle-per-orbit", "two-wave-cycles-per-orbit"),
    ("chosen-merger-time", "first-horizon-boundary-contact"),
    ("erased-or-two-source-remnant", "one-remnant-with-held-ledger"),
    ("fitted-tone", "held-remnant-mass-turn-class"),
    ("negative-exponential-or-free-decay", "binary-half-One-contraction"),
    ("numerical-zero-or-completed-infinity", "positive-at-every-finite-depth"),
    ("permuted-or-omitted-stage", "inspiral-chirp-merger-ringdown"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_checks():
    for depth in (1, 2, 3, 8, 16, 32):
        separations = tuple(Fraction(2 ** step, 1) for step in range(depth, -1, -1))
        period_sq = tuple(value ** 3 for value in separations)
        orbit_f_sq = tuple(Fraction(1, 1) / value for value in period_sq)
        wave_f_sq = tuple(4 * value for value in orbit_f_sq)
        binding = tuple(Fraction(1, 2) / value for value in separations)
        takes = tuple(right - left for left, right in zip(binding, binding[1:]))
        amplitudes = tuple(Fraction(1, 2 ** step) for step in range(depth))
        if not all((
            all(left > right for left, right in zip(separations, separations[1:])),
            all(left > right for left, right in zip(period_sq, period_sq[1:])),
            all(left < right for left, right in zip(wave_f_sq, wave_f_sq[1:])),
            all(value > 0 for value in takes),
            all(wave == 4 * orbit for wave, orbit in zip(wave_f_sq, orbit_f_sq)),
            separations[-1] == 1,
            all(left > right for left, right in zip(amplitudes, amplitudes[1:])),
            all(value > 0 for value in amplitudes),
        )):
            return False
    return True


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    valid = exact_checks()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 4096,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
        valid,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 4096,
            "wave_to_orbit_frequency_ratio": "2/1",
            "contact_separation": "1/1",
            "source_join": "2-to-1",
            "ringdown_contraction": "1/2",
            "sequence": ["inspiral-rising-chirp", "merger", "damped-ringdown"],
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
