#!/usr/bin/env python3
"""Implementation-distinct validator for terminal decay-width laws.

This process imports neither the claimant nor the empirical adapter. It
reconstructs the exact channel arithmetic, complete candidate product and
unique survivor from declared sealed inputs.
"""

from __future__ import annotations

from fractions import Fraction
from functools import reduce
from itertools import product
import json
from operator import add
import sys


CLAIM_ID = "SFT-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006"

PARTIAL_WIDTH_CARRIERS = (
    "paired-transition-weight-times-output-support-per-action",
    "unpaired-transition-leg-times-output-support",
    "target-assigned-partial-width",
)
CHANNEL_DOMAINS = (
    "positive-open-channels-closed-as-empty",
    "numeric-null-closed-channels",
    "indistinguishable-overlapping-channel-list",
)
TOTAL_WIDTH_LAWS = (
    "ordered-positive-sum-of-partial-widths",
    "largest-partial-width-only",
    "arithmetic-mean-of-partial-widths",
)
BRANCHING_LAWS = (
    "partial-width-over-total-width",
    "total-width-over-partial-width",
    "unnormalized-partial-width",
)
PARTITION_LAWS = (
    "complete-exclusive-partition-of-one",
    "incomplete-open-channel-subset",
    "overlapping-double-counted-channels",
)
LIFETIME_LAWS = (
    "action-over-total-width",
    "total-width-over-action",
    "action-times-total-width",
)
ORDERING_LAWS = (
    "greater-width-shorter-lifetime",
    "greater-width-longer-lifetime",
    "width-independent-lifetime",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")


def partial(overlap: Fraction, support: Fraction, action: Fraction) -> Fraction:
    return overlap * overlap * support / action


def total(widths: tuple[Fraction, ...]) -> Fraction:
    if not widths or any(width.numerator < 1 for width in widths):
        raise ValueError("independent total requires a positive nonempty family")
    return reduce(add, widths[1:], widths[0])


def branches(widths: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    whole = total(widths)
    return tuple(width / whole for width in widths)


def lifetime(action: Fraction, width: Fraction) -> Fraction:
    return action / width


def sample() -> tuple[Fraction, ...]:
    action = Fraction(1, 2)
    return (
        partial(Fraction(1, 2), Fraction(1, 2), action),
        partial(Fraction(1, 2), Fraction(1, 1), action),
        partial(Fraction(1, 1), Fraction(5, 8), action),
    )


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            PARTIAL_WIDTH_CARRIERS,
            CHANNEL_DOMAINS,
            TOTAL_WIDTH_LAWS,
            BRANCHING_LAWS,
            PARTITION_LAWS,
            LIFETIME_LAWS,
            ORDERING_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(candidate_id: str) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 9:
        return False
    (
        partial_law,
        domain,
        total_law,
        branch_law,
        partition_law,
        lifetime_law,
        ordering_law,
        target,
        extension,
    ) = fields

    observed_partial = partial(Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    partial_passed = {
        "paired-transition-weight-times-output-support-per-action": observed_partial
        == Fraction(3, 16),
        "unpaired-transition-leg-times-output-support": observed_partial == Fraction(3, 8),
        "target-assigned-partial-width": False,
    }.get(partial_law, False)

    widths = sample()
    domain_passed = {
        "positive-open-channels-closed-as-empty": all(width.numerator >= 1 for width in widths),
        "numeric-null-closed-channels": False,
        "indistinguishable-overlapping-channel-list": False,
    }.get(domain, False)

    observed_total = total(widths)
    total_passed = {
        "ordered-positive-sum-of-partial-widths": observed_total == Fraction(2, 1),
        "largest-partial-width-only": observed_total == Fraction(5, 4),
        "arithmetic-mean-of-partial-widths": observed_total == Fraction(2, 3),
    }.get(total_law, False)

    observed_branches = branches(widths)
    branch_passed = {
        "partial-width-over-total-width": observed_branches
        == (Fraction(1, 8), Fraction(1, 4), Fraction(5, 8)),
        "total-width-over-partial-width": observed_branches
        == (Fraction(8, 1), Fraction(4, 1), Fraction(8, 5)),
        "unnormalized-partial-width": observed_branches == widths,
    }.get(branch_law, False)

    partition_passed = {
        "complete-exclusive-partition-of-one": total(observed_branches) == Fraction(1, 1),
        "incomplete-open-channel-subset": total(observed_branches[:-1]) == Fraction(1, 1),
        "overlapping-double-counted-channels": total(observed_branches + (observed_branches[0],))
        == Fraction(1, 1),
    }.get(partition_law, False)

    observed_lifetime = lifetime(Fraction(1, 1), observed_total)
    lifetime_passed = {
        "action-over-total-width": observed_lifetime == Fraction(1, 2),
        "total-width-over-action": observed_lifetime == Fraction(2, 1),
        "action-times-total-width": observed_lifetime == Fraction(2, 1),
    }.get(lifetime_law, False)

    vector = tuple(
        (width, lifetime(Fraction(1, 1), width))
        for width in (Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
    )
    ordering_passed = {
        "greater-width-shorter-lifetime": all(
            left_width < right_width and left_duration > right_duration
            for (left_width, left_duration), (right_width, right_duration)
            in zip(vector, vector[1:])
        ),
        "greater-width-longer-lifetime": all(
            left_duration < right_duration
            for (_, left_duration), (_, right_duration) in zip(vector, vector[1:])
        ),
        "width-independent-lifetime": len({duration for _, duration in vector}) == 1,
    }.get(ordering_law, False)

    return all((
        partial_passed,
        domain_passed,
        total_passed,
        branch_passed,
        partition_passed,
        lifetime_passed,
        ordering_passed,
        target == "sealed-before-release",
        extension == "empty-extension",
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
    widths = sample()
    parts = branches(widths)
    successor_widths = (
        Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1)
    )
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 8748
        and sealed_decisions == recomputed_decisions
        and len(survivors) == 1
        and widths == (Fraction(1, 4), Fraction(1, 2), Fraction(5, 4))
        and total(widths) == Fraction(2, 1)
        and parts == (Fraction(1, 8), Fraction(1, 4), Fraction(5, 8))
        and total(parts) == Fraction(1, 1)
        and all(total(branches(widths + (item,))) == Fraction(1, 1) for item in successor_widths)
        and lifetime(Fraction(1, 1), Fraction(1, 2)) == Fraction(2, 1)
        and lifetime(Fraction(1, 1), Fraction(2, 1)) == Fraction(1, 2)
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
            "sample_partial_widths": [str(value) for value in widths],
            "sample_total_width": str(total(widths)),
            "sample_branching_parts": [str(value) for value in parts],
            "sample_partition": str(total(parts)),
            "sample_lifetime": str(lifetime(Fraction(1, 1), total(widths))),
            "closed_channel": [],
            "target_values_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
