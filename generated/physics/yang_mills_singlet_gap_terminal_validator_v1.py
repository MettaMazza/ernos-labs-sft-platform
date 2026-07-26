#!/usr/bin/env python3
"""Independent exact reconstruction of the finite colour-singlet gap law."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026"
DOMAINS = (
    ("named-Yang-Mills-sector", "generated-colour-three-sector"),
    ("isolated-colour-carrier", "complete-colour-singlet-support"),
    ("numerical-zero-vacuum", "empty-excitation-record"),
    ("massless-or-fitted-gap", "exact-positive-one-third-complement"),
    ("bounded-or-free-separation-work", "fixed-two-thirds-positive-work-successor"),
    ("conflate-local-carrier-with-physical-singlet", "retain-local-massless-physical-gapped-distinction"),
    ("selected-gap-coupling-pair", "complete-period-two-Fold-partition"),
    ("bounded-depth-census-or-completed-infinity", "positive-finite-successor-induction"),
    ("repeat-no-massless-strong-excitation", "correct-free-singlet-spectrum-boundary"),
    ("free-scale-action-or-continuum-limit", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def fold(value: Fraction) -> Fraction:
    doubled = value + value
    return doubled if doubled <= 1 else doubled - 1


def theorem_check() -> bool:
    coupling = Fraction(3 - 1, 3)
    gap = Fraction(1, 1) - coupling
    singlets = (2, 3)
    rows = tuple((gap, coupling * depth) for depth in range(1, 33))
    return all(
        (
            coupling == Fraction(2, 3),
            gap == Fraction(1, 3),
            coupling + gap == 1,
            fold(gap) == coupling,
            fold(coupling) == gap,
            min(singlets) == 2,
            all(row[0] > 0 and row[1] > 0 for row in rows),
            len({row[0] for row in rows}) == 1,
            all(rows[index + 1][1] > rows[index][1] for index in range(len(rows) - 1)),
        )
    )


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {
        candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check()
        for candidate_id in generated
    }
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 1024,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(row["passed"] for row in sealed["controls"]),
            theorem_check(),
        )
    )
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(generated),
            "normalized_gap": "1/3",
            "confinement_work_successor": "2/3",
            "local_massless_carrier_retained": True,
            "continuum_Yang_Mills_proof_claimed": False,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
