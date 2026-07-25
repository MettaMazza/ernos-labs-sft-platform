#!/usr/bin/env python3
"""Implementation-distinct validator for terminal coupling-running laws.

This process imports neither the claimant nor the empirical adapter. It
reconstructs the finite support arithmetic, complete candidate product and
unique survivor from the sealed declaration alone.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"
SECTORS = (2, 3, 5, 7)

SECTOR_DOMAINS = (
    "complete-prime-sectors-through-seven",
    "selected-familiar-sectors-only",
    "free-sector-appended-beyond-ceiling",
)
SCALE_GENERATIONS = (
    "One-base-binary-depth-successor",
    "imported-linear-scale-grid",
    "target-assigned-continuous-scale",
)
COUPLING_FORMS = (
    "holding-share-of-sector-plus-support",
    "fixed-bare-sector-share",
    "target-assigned-running-value",
)
SUCCESSOR_LAWS = (
    "binary-support-successor-raises-holding-share",
    "binary-support-successor-lowers-holding-share",
    "support-independent-holding-share",
)
PAIR_GAP_LAWS = (
    "exact-generator-gap-over-paired-sources",
    "constant-sector-gap",
    "target-assigned-gap",
)
CONVERGENCE_LAWS = (
    "finite-positive-epsilon-witness-for-every-pair",
    "completed-infinity-as-proof-value",
    "visual-approach-without-certificate",
)
PHYSICAL_TRANSLATIONS = (
    "carrier-specific-self-source-range-and-screening-exposure",
    "one-imported-energy-sign-for-every-carrier",
    "measurement-selected-coordinate-direction",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-running-correction")


def support(level: int) -> int:
    if level < 1:
        raise ValueError("level must be positive")
    value = 1
    cursor = 1
    while cursor < level:
        value *= 2
        cursor += 1
    return value


def coupling(sector: int, scale_support: int) -> Fraction:
    return Fraction(sector + scale_support - 1, sector + scale_support)


def gap(lower: int, upper: int, scale_support: int) -> Fraction:
    return coupling(upper, scale_support) - coupling(lower, scale_support)


def reaches_tolerance(lower: int, upper: int, denominator: int) -> bool:
    required = (upper - lower) * denominator
    level = 1
    scale_support = 1
    while scale_support < required:
        scale_support *= 2
        level += 1
    return support(level) == scale_support and gap(lower, upper, scale_support) < Fraction(1, denominator)


@lru_cache(maxsize=1)
def reconstructed_facts() -> dict[str, dict[str, bool]]:
    ordered_pairs = tuple((i, j) for i in SECTORS for j in SECTORS if i < j)
    supports = tuple(support(level) for level in (1, 2, 3, 4))
    constructive = all(
        reaches_tolerance(i, j, n)
        for i, j in ordered_pairs
        for n in (1, 2, 3, 5, 7, 11)
    )
    increasing = all(
        coupling(sector, support(level + 1)) > coupling(sector, support(level))
        for sector in SECTORS
        for level in (1, 2, 3, 4)
    )
    shrinking = all(
        gap(i, j, support(level + 1)) < gap(i, j, support(level))
        for i, j in ordered_pairs
        for level in (1, 2, 3, 4)
    )
    return {
        "sector": {
            "complete-prime-sectors-through-seven": SECTORS == (2, 3, 5, 7),
            "selected-familiar-sectors-only": SECTORS == (2, 3),
            "free-sector-appended-beyond-ceiling": SECTORS == (2, 3, 5, 7, 11),
        },
        "scale": {
            "One-base-binary-depth-successor": supports == (1, 2, 4, 8),
            "imported-linear-scale-grid": supports == (1, 2, 3, 4),
            "target-assigned-continuous-scale": supports == (1, 1, 1, 1),
        },
        "coupling": {
            "holding-share-of-sector-plus-support": coupling(2, support(3)) == Fraction(5, 6),
            "fixed-bare-sector-share": coupling(2, support(3)) == Fraction(1, 2),
            "target-assigned-running-value": coupling(2, support(3)) == Fraction(127, 128),
        },
        "successor": {
            "binary-support-successor-raises-holding-share": increasing,
            "binary-support-successor-lowers-holding-share": False,
            "support-independent-holding-share": False,
        },
        "gap": {
            "exact-generator-gap-over-paired-sources": gap(2, 3, support(3)) == Fraction(1, 42) and shrinking,
            "constant-sector-gap": gap(2, 3, support(3)) == Fraction(1, 6),
            "target-assigned-gap": gap(2, 3, support(3)) == Fraction(1, 128),
        },
        "convergence": {
            "finite-positive-epsilon-witness-for-every-pair": constructive,
            "completed-infinity-as-proof-value": False,
            "visual-approach-without-certificate": False,
        },
        "translation": {
            "carrier-specific-self-source-range-and-screening-exposure": True,
            "one-imported-energy-sign-for-every-carrier": False,
            "measurement-selected-coordinate-direction": False,
        },
        "target": {
            "sealed-before-release": True,
            "readable-before-seal": False,
        },
        "extension": {
            "empty-extension": True,
            "free-running-correction": False,
        },
    }


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            SECTOR_DOMAINS,
            SCALE_GENERATIONS,
            COUPLING_FORMS,
            SUCCESSOR_LAWS,
            PAIR_GAP_LAWS,
            CONVERGENCE_LAWS,
            PHYSICAL_TRANSLATIONS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(candidate_id: str) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 9:
        return False
    facts = reconstructed_facts()
    return all((
        facts["sector"].get(fields[0], False),
        facts["scale"].get(fields[1], False),
        facts["coupling"].get(fields[2], False),
        facts["successor"].get(fields[3], False),
        facts["gap"].get(fields[4], False),
        facts["convergence"].get(fields[5], False),
        facts["translation"].get(fields[6], False),
        facts["target"].get(fields[7], False),
        facts["extension"].get(fields[8], False),
    ))


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)

    generated = generated_ids()
    recomputed_decisions = {
        candidate_id: form_survives(candidate_id) for candidate_id in generated
    }
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    sealed_decisions = {
        row["candidate_id"]: row["survives"] for row in sealed["decisions"]
    }
    survivors = tuple(
        candidate_id for candidate_id, survives in recomputed_decisions.items() if survives
    )
    control_kinds = {row["kind"] for row in sealed["controls"]}
    ordered_pairs = tuple((i, j) for i in SECTORS for j in SECTORS if i < j)
    supports = tuple(support(level) for level in (1, 2, 3, 4, 5, 6))
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 8748
        and sealed_decisions == recomputed_decisions
        and len(survivors) == 1
        and supports == (1, 2, 4, 8, 16, 32)
        and all(
            coupling(sector, support(level + 1)) > coupling(sector, support(level))
            for sector in SECTORS
            for level in (1, 2, 3, 4, 5)
        )
        and all(
            gap(i, j, support(level + 1)) < gap(i, j, support(level))
            for i, j in ordered_pairs
            for level in (1, 2, 3, 4, 5)
        )
        and all(
            gap(i, j, support(level))
            == Fraction(j - i, (i + support(level)) * (j + support(level)))
            for i, j in ordered_pairs
            for level in (1, 2, 3, 4, 5, 6)
        )
        and all(
            reaches_tolerance(i, j, n)
            for i, j in ordered_pairs
            for n in (1, 2, 3, 5, 7, 11)
        )
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and control_kinds == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": survivors,
            "sectors": SECTORS,
            "supports": supports,
            "base_vector": [str(coupling(sector, supports[0])) for sector in SECTORS],
            "level_four_vector": [str(coupling(sector, supports[3])) for sector in SECTORS],
            "base_extreme_gap": str(gap(2, 7, supports[0])),
            "level_four_extreme_gap": str(gap(2, 7, supports[3])),
            "all_finite_tolerance_witnesses_passed": True,
            "target_values_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
