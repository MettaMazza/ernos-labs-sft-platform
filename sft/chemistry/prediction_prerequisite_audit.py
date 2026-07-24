"""Exact audit of the prerequisites for the three Chemistry predictions.

This is not an admitted scientific claim and it intentionally contains no
g-block width, element-126 result, periodic endpoint, V2 answer or external
target value.  It asks whether the already admitted V3 dependency surface is
sufficient to select those results before a prediction is sealed.

The audit constructs two implementation-explicit witness families satisfying
the current finite-support, two-held-label and exclusion requirements.  Their
different capacities prove that those requirements do not yet identify one
subshell-width law.  It likewise constructs two strictly increasing finite
nuclear recurrence schedules satisfying the current qualitative nuclear-level
law.  Because both alternatives survive, uniqueness is absent and the single
admission engine must halt rather than admit a selected prediction.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, PositiveCount


FOLD_ORIENTATIONS = (
    HeldLabel("Fold orientation", "held-a"),
    HeldLabel("Fold orientation", "held-b"),
)


@dataclass(frozen=True)
class FiniteSupport:
    """A positive finite cell support carrying both forced Fold labels."""

    cells: tuple[str, ...]
    orientations: tuple[HeldLabel, ...] = FOLD_ORIENTATIONS

    def __post_init__(self) -> None:
        if not self.cells or len(self.cells) != len(set(self.cells)):
            raise ValueError("support cells must be a nonempty canonical family")
        if self.orientations != FOLD_ORIENTATIONS:
            raise ValueError("support must retain exactly the two forced Fold labels")

    @property
    def capacity(self) -> PositiveCount:
        return PositiveCount(len(self.cells) * len(self.orientations))

    @property
    def exclusion_preserving(self) -> bool:
        states = tuple(
            (cell, orientation.label)
            for cell in self.cells
            for orientation in self.orientations
        )
        return len(states) == len(set(states))


def linear_support(rank: PositiveCount) -> FiniteSupport:
    """One fresh cell per generated rank, with no terminal assumption."""

    return FiniteSupport(tuple(f"linear-cell-{position}" for position in range(1, rank.value + 1)))


def fold_doubling_support(rank: PositiveCount) -> FiniteSupport:
    """One cell whose complete support is doubled at each Fold extension."""

    cell_count = PositiveCount(2 ** (rank.value - 1))
    return FiniteSupport(tuple(f"fold-cell-{position}" for position in range(1, cell_count.value + 1)))


def capacity_witnesses(depth: PositiveCount) -> tuple[tuple[PositiveCount, ...], tuple[PositiveCount, ...]]:
    """Return two lawful but unequal capacity families through ``depth``."""

    ranks = tuple(PositiveCount(value) for value in range(1, depth.value + 1))
    linear = tuple(linear_support(rank).capacity for rank in ranks)
    doubled = tuple(fold_doubling_support(rank).capacity for rank in ranks)
    return linear, doubled


def recurrence_schedule(increments: tuple[PositiveCount, ...]) -> tuple[PositiveCount, ...]:
    """Build exact finite increasing recurrence closures from positive steps."""

    if not increments:
        raise ValueError("a recurrence schedule requires positive generated support")
    total = 0  # Host accumulator only; no numerical zero is emitted as an SFT value.
    closures: list[PositiveCount] = []
    for increment in increments:
        total += increment.value
        closures.append(PositiveCount(total))
    return tuple(closures)


@dataclass(frozen=True)
class PredictionPrerequisiteAudit:
    unique_subshell_capacity: bool
    unique_nuclear_closure: bool
    forced_terminal_coordinate: bool
    capacity_witnesses: tuple[tuple[PositiveCount, ...], tuple[PositiveCount, ...]]
    nuclear_witnesses: tuple[tuple[PositiveCount, ...], tuple[PositiveCount, ...]]
    unresolved_claim_ids: tuple[str, ...]

    @property
    def admissible(self) -> bool:
        return (
            self.unique_subshell_capacity
            and self.unique_nuclear_closure
            and self.forced_terminal_coordinate
        )


def run_prerequisite_audit() -> PredictionPrerequisiteAudit:
    """Execute the target-blind identifiability check.

    The two capacity families are finite, complete, two-label and
    exclusion-preserving at every generated rank.  The two nuclear schedules
    are finite and strictly increasing.  Existing V3 laws contain no admitted
    discriminator between either pair.  The recursive foundational grammar
    also has a successor certificate for every generated finite depth, so it
    does not supply a greatest element coordinate.
    """

    depth = PositiveCount(4)
    capacities = capacity_witnesses(depth)
    if capacities[0] == capacities[1]:
        raise AssertionError("audit witnesses must retain distinct capacity families")
    for rank in range(1, depth.value + 1):
        held_rank = PositiveCount(rank)
        if not linear_support(held_rank).exclusion_preserving:
            raise AssertionError("linear witness violated exclusion")
        if not fold_doubling_support(held_rank).exclusion_preserving:
            raise AssertionError("Fold-doubling witness violated exclusion")

    unit_steps = tuple(PositiveCount(1) for _ in range(1, depth.value + 1))
    growing_steps = tuple(PositiveCount(value) for value in range(1, depth.value + 1))
    nuclear = (recurrence_schedule(unit_steps), recurrence_schedule(growing_steps))
    if nuclear[0] == nuclear[1]:
        raise AssertionError("audit witnesses must retain distinct recurrence schedules")

    return PredictionPrerequisiteAudit(
        unique_subshell_capacity=False,
        unique_nuclear_closure=False,
        forced_terminal_coordinate=False,
        capacity_witnesses=capacities,
        nuclear_witnesses=nuclear,
        unresolved_claim_ids=(
            "SFT-CHEM-PRED-G-BLOCK-001",
            "SFT-CHEM-PRED-SMITHIUM-001",
            "SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
        ),
    )


__all__ = (
    "FOLD_ORIENTATIONS",
    "FiniteSupport",
    "PredictionPrerequisiteAudit",
    "capacity_witnesses",
    "linear_support",
    "fold_doubling_support",
    "recurrence_schedule",
    "run_prerequisite_audit",
)
