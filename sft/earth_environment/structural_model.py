"""Exact Fold structures used by the Earth and Environment foundation.

No conventional Earth-system equation, measured environmental value or fitted
coefficient occurs here. Host counts and containers organize finite evidence;
all derivational magnitudes are exact positive rational parts through the One.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import ExactPart, HeldLabel


ONE = ExactPart.from_pair(1, 1)
HALF = ExactPart.from_pair(1, 2)
QUARTER = ExactPart.from_pair(1, 4)
THREE_QUARTERS = ExactPart.from_pair(3, 4)


def fold(part: ExactPart) -> ExactPart:
    doubled = part.value * 2
    if doubled > 1:
        doubled -= 1
    return ExactPart(doubled)


def equal_reservoir_partition(depth: int) -> tuple[ExactPart, ...]:
    """Generate every equal stock in one complete depth partition."""
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 1:
        raise ValueError("a reservoir partition requires positive finite depth")
    count = 2**depth
    share = ExactPart.from_pair(1, count)
    result = tuple(share for _ in range(count))
    if sum((item.value for item in result), Fraction(0, 1)) != ONE.value:
        raise AssertionError("reservoir stocks do not close to the One")
    return result


@dataclass(frozen=True)
class Transfer:
    carrier: HeldLabel
    source: HeldLabel
    destination: HeldLabel
    amount: ExactPart


def boundary_transfer() -> Transfer:
    return Transfer(
        HeldLabel("earth-carrier", "registered-material"),
        HeldLabel("earth-reservoir", "source"),
        HeldLabel("earth-reservoir", "destination"),
        QUARTER,
    )


def transfer_is_two_sided(transfer: Transfer) -> bool:
    return (
        transfer.source != transfer.destination
        and transfer.amount.value > 0
        and transfer.amount.value <= ONE.value
        and transfer.carrier.family == "earth-carrier"
    )


def layer_order(depth: int) -> tuple[ExactPart, ...]:
    """A positive finite nested sequence; ordering is held, never subtracted."""
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 1:
        raise ValueError("a layer order requires positive finite depth")
    return tuple(ExactPart.from_pair(1, 2**position) for position in range(1, depth + 1))


def complementary_cycle() -> tuple[ExactPart, ExactPart]:
    lower = ExactPart.from_pair(1, 3)
    upper = ExactPart.from_pair(2, 3)
    if fold(lower) != upper or fold(upper) != lower:
        raise AssertionError("the complementary Earth-system cycle failed")
    return lower, upper


def coupled_three_reservoir_cycle() -> tuple[ExactPart, ExactPart, ExactPart]:
    states = (ExactPart.from_pair(1, 7), ExactPart.from_pair(2, 7), ExactPart.from_pair(4, 7))
    if tuple(fold(item) for item in states) != (states[1], states[2], states[0]):
        raise AssertionError("the coupled three-reservoir cycle failed")
    if sum((item.value for item in states), Fraction(0, 1)) != ONE.value:
        raise AssertionError("the coupled reservoirs do not partition the One")
    return states


def tipping_fibre() -> dict[str, object]:
    """Return the abstract two-basin witness without assigning a physical threshold."""
    return {
        "lower_basin": QUARTER,
        "upper_basin": THREE_QUARTERS,
        "shared_image": HALF,
        "basins_distinct": QUARTER != THREE_QUARTERS,
        "same_fold_image": fold(QUARTER) == fold(THREE_QUARTERS) == HALF,
        "physical_threshold_assigned": False,
    }


def magnitude_frequency_census(depth: int = 8) -> tuple[dict[str, object], ...]:
    """Generate the exact unit-exponent size-count relation at finite scales."""
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("a magnitude-frequency census requires at least two scales")
    rows = []
    for scale in range(1, depth + 1):
        size = ExactPart.from_pair(1, 2**scale)
        count = 2**scale
        rows.append({"scale": scale, "size": size, "count": count, "count_times_size": Fraction(count, 1) * size.value})
    if any(row["count_times_size"] != ONE.value for row in rows):
        raise AssertionError("unit size-count recurrence failed")
    return tuple(rows)


def unique_positive_exponent(depth: int = 8) -> int:
    """Enumerate the first three positive finite exponent forms."""
    rows = magnitude_frequency_census(depth)
    candidates = (1, 2, 3)
    survivors = []
    for exponent in candidates:
        products = tuple(Fraction(row["count"], 1) * (row["size"].value**exponent) for row in rows)
        if all(value == ONE.value for value in products):
            survivors.append(exponent)
    if survivors != [1]:
        raise AssertionError("the generated exponent census is not unique")
    return survivors[0]


def bounded_cavity_modes(count: int = 5) -> tuple[HeldLabel, ...]:
    """Generate distinguishable positive finite modes without a measured frequency."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("a cavity requires a positive finite mode count")
    return tuple(HeldLabel("bounded-cavity-mode", str(position)) for position in range(1, count + 1))


def observation_statuses() -> tuple[HeldLabel, ...]:
    return tuple(
        HeldLabel("earth-observation-status", label)
        for label in ("observed-present", "observed-absent", "non-detected", "censored", "missing", "outside-scope")
    )


def structural_witnesses() -> dict[str, bool]:
    partition = equal_reservoir_partition(3)
    cycle = complementary_cycle()
    coupled = coupled_three_reservoir_cycle()
    tipping = tipping_fibre()
    status = observation_statuses()
    return {
        "reservoir_partition_closes": sum((item.value for item in partition), Fraction(0, 1)) == ONE.value,
        "boundary_transfer_is_two_sided": transfer_is_two_sided(boundary_transfer()),
        "layers_are_positive_and_ordered": tuple(item.value for item in layer_order(5)) == tuple(Fraction(1, 2**position) for position in range(1, 6)),
        "complementary_cycle_recurs": fold(cycle[0]) == cycle[1] and fold(cycle[1]) == cycle[0],
        "coupled_cycle_recurs_and_closes": tuple(fold(item) for item in coupled) == (coupled[1], coupled[2], coupled[0]) and sum((item.value for item in coupled), Fraction(0, 1)) == ONE.value,
        "tipping_basins_share_image_without_physical_assignment": bool(tipping["basins_distinct"]) and bool(tipping["same_fold_image"]) and tipping["physical_threshold_assigned"] is False,
        "unit_exponent_is_uniquely_enumerated": unique_positive_exponent() == 1,
        "bounded_cavity_has_distinct_modes": len(set(bounded_cavity_modes())) == len(bounded_cavity_modes()),
        "observation_statuses_remain_distinct": len(set(status)) == len(status),
    }


if not all(structural_witnesses().values()):
    raise AssertionError("an Earth foundation structural witness failed")


__all__ = (
    "ONE", "HALF", "QUARTER", "THREE_QUARTERS", "Transfer", "fold",
    "equal_reservoir_partition", "boundary_transfer", "transfer_is_two_sided",
    "layer_order", "complementary_cycle", "coupled_three_reservoir_cycle",
    "tipping_fibre", "magnitude_frequency_census", "unique_positive_exponent",
    "bounded_cavity_modes", "observation_statuses", "structural_witnesses",
)
