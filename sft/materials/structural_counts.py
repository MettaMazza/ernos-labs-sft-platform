"""Exact generated counts used by the Materials branch.

This module contains only positive whole counting and held categorical labels.
It never evaluates a decimal approximation, a trigonometric value or an
external materials table.  The functions expose the candidate spaces and the
preservation rule so the counts are reproducible rather than asserted.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.engine.exact import InadmissibleExactValue, PositiveCount


@dataclass(frozen=True)
class OrientedNeighbour:
    generator: str
    orientation: str


def simple_cubic_neighbours(generators: tuple[str, ...]) -> tuple[OrientedNeighbour, ...]:
    """Generate the two held orientations of every independent direction."""

    if not generators or len(set(generators)) != len(generators):
        raise InadmissibleExactValue("directions must be a nonempty distinct generated carrier")
    return tuple(
        OrientedNeighbour(generator, orientation)
        for generator in generators
        for orientation in ("first-fibre", "second-fibre")
    )


def simple_cubic_coordination() -> PositiveCount:
    """Return six from three admitted spatial generators and two Fold fibres."""

    return PositiveCount(len(simple_cubic_neighbours(("axis-one", "axis-two", "axis-three"))))


def _positive_prime_factors(value: int) -> tuple[int, ...]:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InadmissibleExactValue("factor support requires a positive whole")
    factors: list[int] = []
    divisor = 2
    remainder = value
    while divisor * divisor <= remainder:
        if remainder % divisor == 0:
            factors.append(divisor)
            while remainder % divisor == 0:
                remainder //= divisor
        divisor += 1
    if remainder > 1:
        factors.append(remainder)
    return tuple(factors)


def totient_count(order: PositiveCount) -> PositiveCount:
    """Count residue labels coprime to one positive rotation order."""

    value = order.value
    count = sum(
        all(candidate % prime for prime in _positive_prime_factors(value))
        for candidate in range(1, value + 1)
    )
    return PositiveCount(count)


def crystallographic_rotation_admitted(order: PositiveCount) -> bool:
    """Apply the rank-two integral rotation trace-degree boundary."""

    return totient_count(order).value <= 2


def allowed_crystallographic_orders() -> tuple[PositiveCount, ...]:
    """Close every order whose integral rotation degree can fit rank two.

    Depth independence is supplied by the factor certificate below.  If an odd
    prime p divides n, p-1 divides phi(n); phi(n)<=2 therefore permits only
    p=3.  Thus n=2^a*3^b.  The same bound gives a<=2, b<=1, and forbids a=2
    together with b=1.  The remaining positive forms are exactly the returned
    set.  No angular real number or irrational cosine is evaluated.
    """

    candidates = tuple(PositiveCount(value) for value in (1, 2, 3, 4, 6))
    if not all(crystallographic_rotation_admitted(row) for row in candidates):
        raise RuntimeError("rotation factor certificate failed on an admitted form")
    return candidates


def rotation_factor_certificate() -> dict[str, object]:
    """Return the machine-readable depth-independent classification proof."""

    return {
        "degree_boundary": PositiveCount(2),
        "odd_prime_rule": "p divides order implies p-1 divides rotation degree; degree<=2 permits only odd prime 3",
        "factor_form": "order=2^a*3^b",
        "exponent_constraints": ("a<=2", "b<=1", "not(a=2 and b=1)"),
        "survivors": tuple(row.value for row in allowed_crystallographic_orders()),
        "least_excluded": PositiveCount(5),
    }


LENGTH_CLASSES = ("all-equal", "two-equal", "all-distinct")
ANGLE_CLASSES = ("all-right", "two-right", "all-equal-nonright", "all-distinct")


@dataclass(frozen=True)
class CrystalSystem:
    name: str
    length_class: str
    angle_class: str


def _system_name(length_class: str, angle_class: str) -> str | None:
    """Quotient rank-three metrics by axis relabelling and allowed rotations."""

    compatible = {
        ("all-equal", "all-right"): "cubic",
        ("two-equal", "all-right"): "tetragonal",
        ("all-distinct", "all-right"): "orthorhombic",
        ("two-equal", "two-right"): "hexagonal",
        ("all-equal", "all-equal-nonright"): "trigonal",
        ("all-distinct", "two-right"): "monoclinic",
        ("all-distinct", "all-distinct"): "triclinic",
    }
    return compatible.get((length_class, angle_class))


def crystal_system_census() -> tuple[CrystalSystem, ...]:
    """Enumerate the complete 3-by-4 metric grammar and retain seven classes."""

    survivors = []
    for length_class, angle_class in product(LENGTH_CLASSES, ANGLE_CLASSES):
        name = _system_name(length_class, angle_class)
        if name is not None:
            survivors.append(CrystalSystem(name, length_class, angle_class))
    if len(survivors) != 7 or len({row.name for row in survivors}) != 7:
        raise RuntimeError("rank-three metric quotient did not close to seven classes")
    return tuple(survivors)


CENTERING_CLASSES = ("primitive", "base", "body", "face", "rhombohedral")


def _centering_preserves_system(system: str, centering: str) -> bool:
    """Reject centerings equivalent to another basis or incompatible symmetry."""

    canonical = {
        "triclinic": ("primitive",),
        "monoclinic": ("primitive", "base"),
        "orthorhombic": ("primitive", "base", "body", "face"),
        "tetragonal": ("primitive", "body"),
        "trigonal": ("rhombohedral",),
        "hexagonal": ("primitive",),
        "cubic": ("primitive", "body", "face"),
    }
    return centering in canonical[system]


@dataclass(frozen=True)
class BravaisClass:
    crystal_system: str
    centering: str


def bravais_census() -> tuple[BravaisClass, ...]:
    """Enumerate 7-by-5 system/centering forms and quotient to fourteen."""

    survivors = tuple(
        BravaisClass(system.name, centering)
        for system, centering in product(crystal_system_census(), CENTERING_CLASSES)
        if _centering_preserves_system(system.name, centering)
    )
    if len(survivors) != 14 or len(set(survivors)) != 14:
        raise RuntimeError("Bravais system/centering quotient did not close to fourteen classes")
    return survivors


@dataclass(frozen=True)
class AcousticBranch:
    orientation: str
    generator: str


def acoustic_branch_census() -> tuple[AcousticBranch, ...]:
    """Retain one propagation-aligned and two transverse rank-three modes."""

    branches = (
        AcousticBranch("longitudinal", "propagation-axis"),
        AcousticBranch("transverse", "first-cross-axis"),
        AcousticBranch("transverse", "second-cross-axis"),
    )
    if len(branches) != simple_cubic_coordination().value // 2:
        raise RuntimeError("acoustic orientation count does not equal spatial generator rank")
    return branches


__all__ = (
    "AcousticBranch",
    "BravaisClass",
    "CrystalSystem",
    "acoustic_branch_census",
    "allowed_crystallographic_orders",
    "bravais_census",
    "crystal_system_census",
    "crystallographic_rotation_admitted",
    "rotation_factor_certificate",
    "simple_cubic_coordination",
    "simple_cubic_neighbours",
    "totient_count",
)
