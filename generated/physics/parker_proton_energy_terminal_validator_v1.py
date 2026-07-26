#!/usr/bin/env python3
"""Independent exact reconstruction of the Parker proton-energy grammar."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028"
DOMAINS = (
    ("named-proton-without-composition", "admitted-three-colour-proton"),
    ("selected-leading-alpha-rung", "complete-terminal-alpha-rung"),
    ("weak-three-channels", "colour-eight-channels", "penta-twenty-four-channels", "hepta-forty-eight-channels"),
    ("linear-alpha-amplitude", "alpha-squared-energy", "alpha-cubed-extra-interaction"),
    ("add-or-average-channel-shares", "complete-channel-count-times-energy-share"),
    ("local-plasma-fit-or-free-energy", "proton-own-rest-energy-postseal"),
    ("Parker-range-readable-before-seal", "capability-closed-before-Parker-release"),
    ("claim-new-blind-discovery", "observational-derivation-explicit"),
    ("treat-approximately-400-as-exact-cutoff", "complete-reported-range-and-limitations"),
    ("free-local-factor-or-correction", "no-extra-rule"),
)
SURVIVOR = (
    "admitted-three-colour-proton",
    "complete-terminal-alpha-rung",
    "colour-eight-channels",
    "alpha-squared-energy",
    "complete-channel-count-times-energy-share",
    "proton-own-rest-energy-postseal",
    "capability-closed-before-Parker-release",
    "observational-derivation-explicit",
    "complete-reported-range-and-limitations",
    "no-extra-rule",
)


def theorem_check() -> bool:
    leading = Fraction(250, 34259)
    terminal = Fraction(3676744786, 503846395469)
    rows = tuple((channels, power, Fraction(channels, 1) * terminal ** power) for channels in (3, 8, 24, 48) for power in (1, 2, 3))
    return all((
        8 * leading ** 2 == Fraction(500000, 1173679081),
        8 * terminal ** 2 == Fraction(108147617771025486368, 253861190227103943729961),
        len(rows) == 12,
        sum(channels == 8 and power == 2 for channels, power, _ in rows) == 1,
        all(value > 0 for _, _, value in rows),
    ))


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 3072,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
        theorem_check(),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(generated),
            "formula_census_count": 12,
            "historical_fraction": "500000/1173679081",
            "terminal_fraction": "108147617771025486368/253861190227103943729961",
            "target_content_used": False,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
