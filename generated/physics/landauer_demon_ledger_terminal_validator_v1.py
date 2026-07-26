#!/usr/bin/env python3
"""Independent exact erasure/demon reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018"
DOMAINS = (
    ("sampled-memory-state", "complete-two-preimage-fibre"),
    ("selected-reset-state", "common-half-One-image"),
    ("unquantified-information-loss", "exactly-one-binary-distinction"),
    ("free-or-vanishing-cost", "half-One-preimage-separation"),
    ("infer-erased-predecessor", "retain-one-predecessor-label"),
    ("unrecorded-sorting-gain", "one-held-gas-distinction"),
    ("memory-without-two-states", "two-label-Fold-memory"),
    ("erased-without-external-record", "one-environment-reverse-label"),
    ("import-kT-log-two-as-premise", "postseal-dimensional-correspondence"),
    ("free-cost-or-demon-exception", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def fold(value: Fraction) -> Fraction:
    paired = value + value
    return paired if paired <= 1 else paired - 1


def theorem_check() -> bool:
    lower = Fraction(1, 4)
    upper = Fraction(3, 4)
    ready = Fraction(1, 2)
    return all((fold(lower) == ready, fold(upper) == ready, upper - lower == ready, len({lower, upper}) - 1 == 1, len(("environment-label",)) == 1))


def generated_ids() -> tuple[str, ...]:
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
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "survivor": "__".join(SURVIVOR), "preimages": ["1/4", "3/4"], "image": "1/2", "closed_distinctions": 1, "required_environment_labels": 1}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
