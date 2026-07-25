#!/usr/bin/env python3
"""Implementation-distinct validator for the terminal deuteron law.

This process imports neither the claimant nor any measurement adapter.  It
reconstructs the four held exchange classes, complete pair ledger, quarter
residual comparison and full candidate product from declared exact inputs.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006"
PRESERVING = "exchange-preserving"
ALTERNATING = "exchange-alternating"
PAIR_CLASSES = ("proton-neutron", "proton-proton", "neutron-neutron")

EXCHANGE_PARTITIONS = (
    "three-preserving-one-alternating",
    "two-preserving-two-alternating",
    "one-preserving-three-alternating",
)
GROUND_EXCHANGE_LEDGERS = (
    "pn-preserving-spin-ppnn-alternating-spin",
    "pn-alternating-spin-ppnn-preserving-spin",
    "all-pairs-preserving-spin",
)
RESIDUAL_DISCRIMINATORS = (
    "preserving-leaves-half-alternating-empty",
    "quarter-act-binds-both-spin-hands",
    "neither-spin-hand-retains-support",
)
BINDING_TABLES = (
    "pn-only-bound",
    "all-pairs-bound",
    "no-pair-bound",
    "identical-pairs-only-bound",
)
COMPOSITE_SPINS = (
    "complete-One-with-three-readings",
    "empty-spin-with-one-reading",
    "spin-unresolved",
)
CHARGED_PAIR_ROLES = (
    "pp-positive-opposition-secondary-to-singlet-exclusion",
    "charged-path-selects-both-identical-outcomes",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")


def exchange_classes() -> tuple[tuple[str, str], ...]:
    return (
        ("first-first", PRESERVING),
        ("preserving-mixed", PRESERVING),
        ("second-second", PRESERVING),
        ("alternating-mixed", ALTERNATING),
    )


def exchange_partition() -> dict[str, tuple[str, ...]]:
    rows = exchange_classes()
    return {
        hand: tuple(name for name, observed in rows if observed == hand)
        for hand in (PRESERVING, ALTERNATING)
    }


def support(hand: str) -> Fraction:
    return Fraction(len(exchange_partition()[hand]), len(exchange_classes()))


def compose(*hands: str) -> str:
    result = PRESERVING
    for hand in hands:
        result = PRESERVING if result == hand else ALTERNATING
    return result


def charge_hand(pair: str) -> str:
    return ALTERNATING if pair == "proton-neutron" else PRESERVING


def ground_spin(pair: str) -> str:
    possible = tuple(
        spin
        for spin in (PRESERVING, ALTERNATING)
        if compose(PRESERVING, charge_hand(pair), spin) == ALTERNATING
    )
    if len(possible) != 1:
        raise ValueError("independent exchange ledger failed uniqueness")
    return possible[0]


def remainder(hand: str):
    channel = support(hand)
    residual = Fraction(1, 4)
    if channel > residual:
        return channel - residual
    if channel == residual:
        return ()
    raise ValueError("independent channel fell below residual support")


def pair_rows() -> dict[str, dict[str, object]]:
    return {
        pair: {
            "charge_hand": charge_hand(pair),
            "spin_hand": ground_spin(pair),
            "total_hand": compose(PRESERVING, charge_hand(pair), ground_spin(pair)),
            "spin_support": support(ground_spin(pair)),
            "remainder": remainder(ground_spin(pair)),
            "binds": remainder(ground_spin(pair)) != (),
            "charge_path": Fraction(1, 1) if pair == "proton-proton" else (),
        }
        for pair in PAIR_CLASSES
    }


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            EXCHANGE_PARTITIONS,
            GROUND_EXCHANGE_LEDGERS,
            RESIDUAL_DISCRIMINATORS,
            BINDING_TABLES,
            COMPOSITE_SPINS,
            CHARGED_PAIR_ROLES,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(candidate_id: str) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 8:
        return False
    exchange, ground, residual, binding, spin, charged, target, extension = fields
    partition = exchange_partition()
    rows = pair_rows()

    exchange_expected = {
        "three-preserving-one-alternating": (3, 1),
        "two-preserving-two-alternating": (2, 2),
        "one-preserving-three-alternating": (1, 3),
    }
    exchange_passed = exchange in exchange_expected and exchange_expected[exchange] == (
        len(partition[PRESERVING]), len(partition[ALTERNATING])
    )

    ground_expected = {
        "pn-preserving-spin-ppnn-alternating-spin": {
            "proton-neutron": PRESERVING,
            "proton-proton": ALTERNATING,
            "neutron-neutron": ALTERNATING,
        },
        "pn-alternating-spin-ppnn-preserving-spin": {
            "proton-neutron": ALTERNATING,
            "proton-proton": PRESERVING,
            "neutron-neutron": PRESERVING,
        },
        "all-pairs-preserving-spin": {pair: PRESERVING for pair in PAIR_CLASSES},
    }
    observed_ground = {pair: row["spin_hand"] for pair, row in rows.items()}
    ground_passed = ground in ground_expected and observed_ground == ground_expected[ground]

    observed_remainders = {
        PRESERVING: remainder(PRESERVING),
        ALTERNATING: remainder(ALTERNATING),
    }
    if residual == "preserving-leaves-half-alternating-empty":
        residual_passed = observed_remainders == {
            PRESERVING: Fraction(1, 2), ALTERNATING: ()
        }
    elif residual == "quarter-act-binds-both-spin-hands":
        residual_passed = all(value != () for value in observed_remainders.values())
    elif residual == "neither-spin-hand-retains-support":
        residual_passed = all(value == () for value in observed_remainders.values())
    else:
        residual_passed = False

    binding_expected = {
        "pn-only-bound": {
            "proton-neutron": True, "proton-proton": False, "neutron-neutron": False
        },
        "all-pairs-bound": {pair: True for pair in PAIR_CLASSES},
        "no-pair-bound": {pair: False for pair in PAIR_CLASSES},
        "identical-pairs-only-bound": {
            "proton-neutron": False, "proton-proton": True, "neutron-neutron": True
        },
    }
    observed_binding = {pair: row["binds"] for pair, row in rows.items()}
    binding_passed = binding in binding_expected and observed_binding == binding_expected[binding]

    if spin == "complete-One-with-three-readings":
        spin_passed = (
            Fraction(1, 2) + Fraction(1, 2) == Fraction(1, 1)
            and len(partition[PRESERVING]) == 3
            and rows["proton-neutron"]["spin_hand"] == PRESERVING
        )
    elif spin == "empty-spin-with-one-reading":
        spin_passed = rows["proton-neutron"]["spin_hand"] == ALTERNATING
    else:
        spin_passed = False

    if charged == "pp-positive-opposition-secondary-to-singlet-exclusion":
        charged_passed = (
            rows["proton-proton"]["charge_path"] == Fraction(1, 1)
            and rows["neutron-neutron"]["charge_path"] == ()
            and rows["proton-proton"]["spin_hand"] == rows["neutron-neutron"]["spin_hand"] == ALTERNATING
            and not rows["proton-proton"]["binds"]
            and not rows["neutron-neutron"]["binds"]
        )
    elif charged == "charged-path-selects-both-identical-outcomes":
        charged_passed = rows["proton-proton"]["charge_path"] == rows["neutron-neutron"]["charge_path"]
    else:
        charged_passed = False

    return all((
        exchange_passed,
        ground_passed,
        residual_passed,
        binding_passed,
        spin_passed,
        charged_passed,
        target == "sealed-before-release",
        extension == "empty-extension",
    ))


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)

    generated = generated_ids()
    expected_decisions = {candidate_id: form_survives(candidate_id) for candidate_id in generated}
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    control_kinds = {row["kind"] for row in sealed["controls"]}
    rows = pair_rows()
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 2592
        and decisions == expected_decisions
        and sum(expected_decisions.values()) == 1
        and support(PRESERVING) == Fraction(3, 4)
        and support(ALTERNATING) == Fraction(1, 4)
        and remainder(PRESERVING) == Fraction(1, 2)
        and remainder(ALTERNATING) == ()
        and rows["proton-neutron"]["binds"] is True
        and rows["proton-proton"]["binds"] is False
        and rows["neutron-neutron"]["binds"] is False
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and control_kinds == {
            "false_premise", "tampered_source", "tampered_artifact", "boundary"
        }
        and all(row["passed"] is True for row in sealed["controls"])
    )
    surviving_ids = tuple(
        candidate_id for candidate_id, survives in expected_decisions.items() if survives
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": surviving_ids,
            "exchange_partition": {
                PRESERVING: list(exchange_partition()[PRESERVING]),
                ALTERNATING: list(exchange_partition()[ALTERNATING]),
            },
            "preserving_support": str(support(PRESERVING)),
            "alternating_support": str(support(ALTERNATING)),
            "residual_boundary": "1/4",
            "preserving_remainder": str(remainder(PRESERVING)),
            "alternating_remainder_is_empty_form": remainder(ALTERNATING) == (),
            "pair_binding": {pair: row["binds"] for pair, row in rows.items()},
            "pair_spin_hands": {pair: row["spin_hand"] for pair, row in rows.items()},
            "target_value_accessed": False,
            "implementation": (
                "independent held-exchange enumeration, positive rational residual comparison and complete "
                "spatial-spin-charge ledger reconstruction"
            ),
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
