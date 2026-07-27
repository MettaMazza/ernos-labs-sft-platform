"""Fold-native complex spin-state ordering and crossover law (INORG-007).

The native law contains no ligand-field parameter, pairing-energy parameter,
Hamiltonian, signed spin number, numerical-zero occupation, measured crossover
temperature or dimensional bond length.  It exhausts the admissible occupancy
signatures of the already forced three-plus-two split support.  High and low
spin are the two exact extrema of that finite support.  Their order is the
counted composition of pair-closure paths and retained split-crossing paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


ExactCount = Union[EmptyOne, PositiveCount]
InteractionRecurrence = Union[EmptyOne, PositiveCount]


def _exact_count(value: int) -> ExactCount:
    return EMPTY_ONE if value == 0 else PositiveCount(value)


def _count_value(value: ExactCount) -> int:
    return 0 if isinstance(value, EmptyOne) else value.value


@dataclass(frozen=True)
class SplitSupportCapacity:
    """The two exact blocks already forced by INORG-006."""

    lower_width: PositiveCount
    upper_width: PositiveCount

    def __post_init__(self) -> None:
        if (self.lower_width.value, self.upper_width.value) != (3, 2):
            raise InadmissibleExactValue("INORG-007 requires the forced three-plus-two split support")


@dataclass(frozen=True)
class SpinOccupancySignature:
    """Symmetry-quotiented complete occupation of the two split blocks."""

    electron_count: PositiveCount
    lower_pairs: ExactCount
    lower_singles: ExactCount
    upper_pairs: ExactCount
    upper_singles: ExactCount

    def __post_init__(self) -> None:
        components = (self.lower_pairs, self.lower_singles, self.upper_pairs, self.upper_singles)
        if any(not isinstance(value, (EmptyOne, PositiveCount)) for value in components):
            raise InadmissibleExactValue("occupancy components are structural EmptyOne or positive counts")
        lp, ls, up, us = tuple(_count_value(value) for value in components)
        if lp + ls > 3 or up + us > 2:
            raise InadmissibleExactValue("occupancy exceeds the forced split-block support")
        if 2 * (lp + up) + ls + us != self.electron_count.value:
            raise InadmissibleExactValue("pair and single support must exhaust every electron occurrence")

    @property
    def pair_closure_count(self) -> ExactCount:
        return _exact_count(_count_value(self.lower_pairs) + _count_value(self.upper_pairs))

    @property
    def unmatched_fibre_count(self) -> ExactCount:
        return _exact_count(_count_value(self.lower_singles) + _count_value(self.upper_singles))

    @property
    def split_crossing_count(self) -> ExactCount:
        return _exact_count(2 * _count_value(self.upper_pairs) + _count_value(self.upper_singles))

    @property
    def spin_width(self) -> PositiveCount:
        return PositiveCount(_count_value(self.unmatched_fibre_count) + 1)


def enumerate_complete_spin_signatures(
    electron_count: PositiveCount,
    capacity: SplitSupportCapacity = SplitSupportCapacity(PositiveCount(3), PositiveCount(2)),
) -> tuple[SpinOccupancySignature, ...]:
    """Exhaust every symmetry-distinct pair/single allocation of the split support."""

    rows = []
    for lower_pairs, lower_singles, upper_pairs, upper_singles in product(range(4), range(4), range(3), range(3)):
        if lower_pairs + lower_singles > capacity.lower_width.value:
            continue
        if upper_pairs + upper_singles > capacity.upper_width.value:
            continue
        if 2 * (lower_pairs + upper_pairs) + lower_singles + upper_singles != electron_count.value:
            continue
        rows.append(
            SpinOccupancySignature(
                electron_count,
                _exact_count(lower_pairs),
                _exact_count(lower_singles),
                _exact_count(upper_pairs),
                _exact_count(upper_singles),
            )
        )
    if not rows or len(set(rows)) != len(rows):
        raise InadmissibleExactValue("complete spin-state enumeration must be positive and duplicate-free")
    return tuple(rows)


def _least_key(value: ExactCount) -> tuple[int, int]:
    return (0, 0) if isinstance(value, EmptyOne) else (1, value.value)


def forced_low_spin_state(rows: tuple[SpinOccupancySignature, ...]) -> SpinOccupancySignature:
    """The unique state minimizing split crossings and then unmatched support."""

    if not rows:
        raise InadmissibleExactValue("low-spin selection requires the complete positive census")
    ordered = sorted(rows, key=lambda row: (_least_key(row.split_crossing_count), _least_key(row.unmatched_fibre_count)))
    key = (_least_key(ordered[0].split_crossing_count), _least_key(ordered[0].unmatched_fibre_count))
    survivors = tuple(row for row in ordered if (_least_key(row.split_crossing_count), _least_key(row.unmatched_fibre_count)) == key)
    if len(survivors) != 1:
        raise InadmissibleExactValue("low-spin extremum is not unique in the complete quotient census")
    return survivors[0]


def forced_high_spin_state(rows: tuple[SpinOccupancySignature, ...]) -> SpinOccupancySignature:
    """The unique state maximizing unmatched support, then minimizing split crossings."""

    if not rows:
        raise InadmissibleExactValue("high-spin selection requires the complete positive census")
    maximum_unmatched = max(_count_value(row.unmatched_fibre_count) for row in rows)
    candidates = tuple(row for row in rows if _count_value(row.unmatched_fibre_count) == maximum_unmatched)
    minimum_crossing = min(_count_value(row.split_crossing_count) for row in candidates)
    survivors = tuple(row for row in candidates if _count_value(row.split_crossing_count) == minimum_crossing)
    if len(survivors) != 1:
        raise InadmissibleExactValue("high-spin extremum is not unique in the complete quotient census")
    return survivors[0]


def counted_state_path_cost(
    state: SpinOccupancySignature,
    interaction_recurrence: InteractionRecurrence,
) -> ExactCount:
    """Compose pair closures with retained split crossings using exact counts only."""

    pair_paths = _count_value(state.pair_closure_count)
    crossings = _count_value(state.split_crossing_count)
    if isinstance(interaction_recurrence, EmptyOne):
        return _exact_count(pair_paths)
    return _exact_count(pair_paths + interaction_recurrence.value * crossings)


@dataclass(frozen=True)
class ExactSpinStateOrder:
    interaction_recurrence: InteractionRecurrence
    high_state: SpinOccupancySignature
    low_state: SpinOccupancySignature
    high_cost: ExactCount
    low_cost: ExactCount
    order: HeldLabel

    def __post_init__(self) -> None:
        if self.order.family != "complex-spin-state-order" or self.order.label not in {
            "high-precedes-low", "crossover-coincidence", "low-precedes-high"
        }:
            raise InadmissibleExactValue("complex spin-state order is outside the generated trichotomy")


def forced_spin_state_order(
    high_state: SpinOccupancySignature,
    low_state: SpinOccupancySignature,
    interaction_recurrence: InteractionRecurrence,
) -> ExactSpinStateOrder:
    if high_state.electron_count != low_state.electron_count:
        raise InadmissibleExactValue("spin-state comparison requires one retained electron support")
    high_cost = counted_state_path_cost(high_state, interaction_recurrence)
    low_cost = counted_state_path_cost(low_state, interaction_recurrence)
    high_value, low_value = _count_value(high_cost), _count_value(low_cost)
    label = (
        "high-precedes-low" if high_value < low_value
        else "low-precedes-high" if low_value < high_value
        else "crossover-coincidence"
    )
    return ExactSpinStateOrder(
        interaction_recurrence,
        high_state,
        low_state,
        high_cost,
        low_cost,
        HeldLabel("complex-spin-state-order", label),
    )


def forced_six_electron_order_vector() -> tuple[ExactSpinStateOrder, ExactSpinStateOrder, ExactSpinStateOrder]:
    rows = enumerate_complete_spin_signatures(PositiveCount(6))
    high = forced_high_spin_state(rows)
    low = forced_low_spin_state(rows)
    return (
        forced_spin_state_order(high, low, EMPTY_ONE),
        forced_spin_state_order(high, low, PositiveCount(1)),
        forced_spin_state_order(high, low, PositiveCount(2)),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
    "SFT-CHEM-LIGAND-STATE-SPLITTING-006",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "cross-complex-state-mixture", "States from different carriers do not share one exact order.", "one-complex-electron-support", "Both extrema retain one complex and one complete electron census."),
    dimension("split", "imported-orbital-or-field-table", "A conventional table would select the state grammar.", "forced-three-plus-two-support", "INORG-006 supplies the exact three-plus-two support without a field parameter."),
    dimension("enumeration", "selected-configurations", "Selected configurations cannot establish an extremum.", "complete-pair-single-occupancy-census", "Every symmetry-distinct pair/single allocation is generated exactly once."),
    dimension("low", "named-low-spin-assumption", "A name does not force an occupancy.", "least-crossing-then-least-unmatched-extremum", "Low spin is the unique complete-census minimum of split crossings then unmatched fibres."),
    dimension("high", "named-high-spin-assumption", "A name does not force an occupancy.", "greatest-unmatched-then-least-crossing-extremum", "High spin is the unique complete-census maximum of unmatched fibres, then minimum crossing."),
    dimension("cost", "fitted-pairing-or-field-energy", "A fitted energy imports a free parameter and target choice.", "counted-pair-closure-plus-split-crossing-paths", "Order cost composes only exact closure and retained crossing paths."),
    dimension("order", "asserted-ground-state-label", "An asserted label does not compare both generated extrema.", "complete-weak-boundary-strong-trichotomy", "Exact comparison forces high-first, coincidence, or low-first at the three recurrence classes."),
    dimension("extension", "species-temperature-or-distance-fit", "A species fit can manufacture a crossover.", "monotone-dilution-with-no-extra-rule", "Admitted dilution changes only retained interaction recurrence and preserves the same exact order law."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    rows = enumerate_complete_spin_signatures(PositiveCount(6))
    high = forced_high_spin_state(rows)
    low = forced_low_spin_state(rows)
    vector = forced_six_electron_order_vector()
    invalid_support_rejected = False
    try:
        SplitSupportCapacity(PositiveCount(2), PositiveCount(3))
    except InadmissibleExactValue:
        invalid_support_rejected = True
    invalid_occupancy_rejected = False
    try:
        SpinOccupancySignature(PositiveCount(6), PositiveCount(3), PositiveCount(1), EMPTY_ONE, EMPTY_ONE)
    except InadmissibleExactValue:
        invalid_occupancy_rejected = True
    return (
        ("complete-six-electron-census", "Every symmetry-distinct six-electron allocation is generated once.", len(rows) == 10 and len(set(rows)) == 10),
        ("forced-low-extremum", "The low extremum pairs all three lower supports and crosses no split boundary.", _count_value(low.lower_pairs) == 3 and isinstance(low.split_crossing_count, EmptyOne) and low.spin_width.value == 1),
        ("forced-high-extremum", "The high extremum retains four unmatched fibres and exactly two upper crossings.", _count_value(high.lower_pairs) == 1 and _count_value(high.lower_singles) == 2 and _count_value(high.upper_singles) == 2 and high.spin_width.value == 5),
        ("exact-order-trichotomy", "Weak, first-retained and second-retained recurrence force high-first, coincidence and low-first.", tuple(row.order.label for row in vector) == ("high-precedes-low", "crossover-coincidence", "low-precedes-high")),
        ("capacity-control", "Reversing the forced split widths rejects.", invalid_support_rejected),
        ("occupancy-control", "Overfilling the lower support rejects.", invalid_occupancy_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-complex-electron-support__forced-three-plus-two-support__complete-pair-single-occupancy-census__least-crossing-then-least-unmatched-extremum__greatest-unmatched-then-least-crossing-extremum__counted-pair-closure-plus-split-crossing-paths__complete-weak-boundary-strong-trichotomy__monotone-dilution-with-no-extra-rule"


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactSpinStateOrder", "OPERATIONAL_WITNESSES",
    "SpinOccupancySignature", "SplitSupportCapacity", "counted_state_path_cost",
    "enumerate_complete_spin_signatures", "forced_high_spin_state", "forced_low_spin_state",
    "forced_six_electron_order_vector", "forced_spin_state_order",
)
