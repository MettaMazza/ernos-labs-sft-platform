"""Exact structural witnesses for the Materials successor surface.

Only positive whole counts, exact positive parts and held labels occur here.
Structural absence is reported as a categorical label, never as a proof scalar.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


@dataclass(frozen=True)
class PopulationPair:
    first: PositiveCount
    second: PositiveCount


def substitution_populations(depth: PositiveCount) -> tuple[PopulationPair, ...]:
    """Generate exact A->AB, B->A population successors through ``depth``."""

    current = PopulationPair(PositiveCount(1), PositiveCount(1))
    rows = [current]
    for _ in range(1, depth.value):
        current = PopulationPair(
            PositiveCount(current.first.value + current.second.value),
            PositiveCount(current.first.value),
        )
        rows.append(current)
    return tuple(rows)


def rational_inflation_fixed_point_certificate() -> dict[str, object]:
    """Exclude every positive rational fixed scale of the substitution matrix.

    A positive rational scale p/q in lowest terms would satisfy p^2=pq+q^2.
    Hence q divides p^2 and p divides q^2. Coprimality forces p=q=1, which
    fails the equation.  The certificate is depth independent and does not
    evaluate the familiar irrational limit.
    """

    return {
        "recurrence": "(first,second)->(first+second,first)",
        "fixed_scale_equation": "p^2=p*q+q^2 for coprime positive wholes p,q",
        "coprime_divisibility": "q|p^2 and p|q^2 force p=q=1",
        "least_candidate": (PositiveCount(1), PositiveCount(1)),
        "least_candidate_rejected": 1 != 1 + 1,
        "positive_rational_fixed_scale": HeldLabel("existence", "structural-absence"),
    }


def rank_three_mode_count(width: PositiveCount) -> PositiveCount:
    return PositiveCount(width.value * width.value * width.value)


def displacement_mode_certificate() -> dict[str, object]:
    return {
        "uniform_shared_restoring_support": HeldLabel("support", "structural-absence"),
        "acoustic_class": HeldLabel("basis-displacement", "shared"),
        "optical_class": HeldLabel("basis-displacement", "opposed"),
        "directions_per_site": PositiveCount(3),
        "low_support_exponent": PositiveCount(3),
        "sample_cube_counts": tuple(rank_three_mode_count(PositiveCount(n)).value for n in (1, 2, 3, 4)),
    }


def rectification_certificate(barrier: PositiveCount, applied: PositiveCount) -> dict[str, object]:
    if applied.value < barrier.value:
        forward = PositiveCount(barrier.value - applied.value)
        forward_state: object = forward
    else:
        forward_state = HeldLabel("junction-access", "open")
    return {
        "forward_orientation": forward_state,
        "reverse_orientation": PositiveCount(barrier.value + applied.value),
        "orientations_distinct": True,
    }


def ferrimagnetic_gap(first: PositiveCount, second: PositiveCount) -> dict[str, object]:
    if first.value == second.value:
        return {"net_support": HeldLabel("moment", "structural-absence"), "order": "equal-opposed"}
    larger, smaller = (first, second) if first.value > second.value else (second, first)
    orientation = "first-sublattice" if first.value > second.value else "second-sublattice"
    return {
        "net_support": PositiveCount(larger.value - smaller.value),
        "orientation": HeldLabel("dominant-sublattice", orientation),
        "order": "opposed-unequal",
    }


def primary_fractional_hall_classes(max_denominator: PositiveCount) -> tuple[Fraction, ...]:
    return tuple(
        Fraction(numerator, denominator)
        for denominator in range(1, max_denominator.value + 1, 2)
        for numerator in range(1, denominator + 1)
        if gcd(numerator, denominator) == 1
    )


def topological_edge_count(first: PositiveCount, second: PositiveCount) -> dict[str, object]:
    if first.value == second.value:
        raise InadmissibleExactValue("edge count requires distinct adjacent winding classes")
    larger, smaller = (first, second) if first.value > second.value else (second, first)
    return {
        "count": PositiveCount(larger.value - smaller.value),
        "orientation": HeldLabel(
            "bulk-order", "first-to-second" if first.value < second.value else "second-to-first"
        ),
    }


def water_bulk_ledger_certificate() -> dict[str, object]:
    fields = (
        "molecular-network-identity", "specimen-identity", "phase-identity",
        "boiling-record", "solid-liquid-density-record", "heat-capacity-record",
        "conditions", "method", "uncertainty",
    )
    return {"required_fields": fields, "field_count": PositiveCount(len(fields)), "complete": True}


__all__ = (
    "PopulationPair", "displacement_mode_certificate", "ferrimagnetic_gap",
    "primary_fractional_hall_classes", "rank_three_mode_count",
    "rational_inflation_fixed_point_certificate", "rectification_certificate",
    "substitution_populations", "topological_edge_count", "water_bulk_ledger_certificate",
)
