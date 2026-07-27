"""Fold-native finite one-component phase-boundary law for THERMO-012."""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.phase_rule_law_v1 import PhaseRuleAccount, independent_degree_support
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class OneComponentCoexistencePoint:
    component_identity: HeldLabel
    first_phase_identity: HeldLabel
    second_phase_identity: HeldLabel
    temperature_support: PositiveCount
    pressure_support: PositiveCount
    first_phase_exchange_support: PositiveCount
    second_phase_exchange_support: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.component_identity, "chemical-component"),
            (self.first_phase_identity, "chemical-phase"),
            (self.second_phase_identity, "chemical-phase"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("coexistence point lost its held component or phase identity")
        if self.first_phase_identity == self.second_phase_identity:
            raise InadmissibleExactValue("coexistence requires two distinct held phases")
        supports = (
            self.temperature_support,
            self.pressure_support,
            self.first_phase_exchange_support,
            self.second_phase_exchange_support,
        )
        if any(not isinstance(value, PositiveCount) for value in supports):
            raise InadmissibleExactValue("coexistence point requires exact positive support")


@dataclass(frozen=True)
class ExchangeBalanceResult:
    relation: HeldLabel
    separation: PositiveCount | EmptyOne


def coexistence_exchange_balance(point: OneComponentCoexistencePoint) -> ExchangeBalanceResult:
    if not isinstance(point, OneComponentCoexistencePoint):
        raise InadmissibleExactValue("exchange balance requires a complete coexistence point")
    first = point.first_phase_exchange_support.value
    second = point.second_phase_exchange_support.value
    if first == second:
        return ExchangeBalanceResult(HeldLabel("phase-exchange", "balanced"), EmptyOne())
    if first < second:
        return ExchangeBalanceResult(HeldLabel("phase-exchange", "second-expanded"), PositiveCount(second - first))
    return ExchangeBalanceResult(HeldLabel("phase-exchange", "first-expanded"), PositiveCount(first - second))


def one_component_two_phase_degree_support_is_one(point: OneComponentCoexistencePoint) -> bool:
    account = PhaseRuleAccount(
        (point.component_identity,),
        (point.first_phase_identity, point.second_phase_identity),
        (
            HeldLabel("phase-environment-coordinate", "temperature"),
            HeldLabel("phase-environment-coordinate", "pressure"),
        ),
    )
    support = independent_degree_support(account)
    return isinstance(support.count, PositiveCount) and support.count.value == 1


def is_ordered_coexistence_successor(
    prior: OneComponentCoexistencePoint,
    successor: OneComponentCoexistencePoint,
) -> bool:
    if not isinstance(prior, OneComponentCoexistencePoint) or not isinstance(successor, OneComponentCoexistencePoint):
        raise InadmissibleExactValue("coexistence succession requires two complete points")
    if (
        prior.component_identity != successor.component_identity
        or prior.first_phase_identity != successor.first_phase_identity
        or prior.second_phase_identity != successor.second_phase_identity
    ):
        raise InadmissibleExactValue("coexistence succession changed its component or phase pair")
    if coexistence_exchange_balance(prior).relation.label != "balanced" or coexistence_exchange_balance(successor).relation.label != "balanced":
        raise InadmissibleExactValue("coexistence succession requires exact exchange balance at both points")
    return (
        successor.temperature_support.value > prior.temperature_support.value
        and successor.pressure_support.value > prior.pressure_support.value
    )


@dataclass(frozen=True)
class FiniteOneComponentBoundary:
    points: tuple[OneComponentCoexistencePoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise InadmissibleExactValue("a finite coexistence boundary requires positive point support")
        if any(coexistence_exchange_balance(point).relation.label != "balanced" for point in self.points):
            raise InadmissibleExactValue("every phase-boundary point must preserve exact exchange balance")
        if any(not one_component_two_phase_degree_support_is_one(point) for point in self.points):
            raise InadmissibleExactValue("one-component two-phase boundary lost its single degree support")
        if any(not is_ordered_coexistence_successor(prior, successor) for prior, successor in zip(self.points, self.points[1:])):
            raise InadmissibleExactValue("finite coexistence points are not exact ordered successors")


def append_coexistence_successor(
    boundary: FiniteOneComponentBoundary,
    successor: OneComponentCoexistencePoint,
) -> FiniteOneComponentBoundary:
    if not isinstance(boundary, FiniteOneComponentBoundary):
        raise InadmissibleExactValue("coexistence extension requires a finite boundary")
    return FiniteOneComponentBoundary(boundary.points + (successor,))


def common_support_replication_preserves_boundary(
    boundary: FiniteOneComponentBoundary,
    replication: PositiveCount,
) -> bool:
    if not isinstance(boundary, FiniteOneComponentBoundary) or not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("boundary replication requires exact positive support")
    factor = replication.value
    replicated = FiniteOneComponentBoundary(tuple(
        OneComponentCoexistencePoint(
            point.component_identity,
            point.first_phase_identity,
            point.second_phase_identity,
            PositiveCount(point.temperature_support.value * factor),
            PositiveCount(point.pressure_support.value * factor),
            PositiveCount(point.first_phase_exchange_support.value * factor),
            PositiveCount(point.second_phase_exchange_support.value * factor),
        )
        for point in boundary.points
    ))
    return len(replicated.points) == len(boundary.points)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-MIXTURE-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
    "SFT-CHEM-PHASE-RULE-STRUCTURAL-011",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "unbound-temperature-pressure-pair", "A detached pair erases the component, phases and exchange support that make it a boundary point.", "complete-one-component-two-phase-point", "Each point retains component, two phases, exact supports and both held coordinates."),
    dimension("phase", "single-phase-state-or-erased-phase-pair", "A single phase does not define a coexistence boundary.", "two-distinct-held-coexisting-phases", "The phase pair remains distinct and held at every point."),
    dimension("balance", "assumed-equilibrium-or-target-derived-equality", "Assumption or target adjustment does not force coexistence.", "exact-component-exchange-support-balance", "Coexistence is exact equality of the component exchange supports across the phase pair."),
    dimension("degree", "free-two-coordinate-continuum", "A free plane contradicts the single remaining carrier forced by one component and two phases.", "one-independent-held-coordinate-support", "The admitted phase-rule cancellation leaves exactly one independent carrier."),
    dimension("response", "imported-differential-equation-or-fitted-slope", "A differential equation or fitted slope imports a continuum model.", "exact-positive-temperature-pressure-co-order", "A stable liquid-vapor boundary successor retains exact positive increase in both held coordinates."),
    dimension("boundary", "interpolated-continuum-curve", "Interpolation invents unmeasured points and an unenumerated continuum.", "finite-ordered-coexistence-word", "The boundary is exactly the generated finite word of measured coexistence points."),
    dimension("prediction", "coexistence-values-readable-before-seal", "Readable temperatures or pressures could select the relation.", "complete-value-free-15-point-identity-seal", "All fifteen source identities seal before compounds, phases, temperatures or pressures open."),
    dimension("extension", "refit-after-appending-or-replication", "Refitting destroys exact succession and support provenance.", "depth-independent-append-and-common-replication", "Appending one ordered balanced point or commonly replicating support preserves the finite boundary law."),
)


EXACT_RESULT = (
    "complete-one-component-two-phase-point__two-distinct-held-coexisting-phases__"
    "exact-component-exchange-support-balance__one-independent-held-coordinate-support__"
    "exact-positive-temperature-pressure-co-order__finite-ordered-coexistence-word__"
    "complete-value-free-15-point-identity-seal__depth-independent-append-and-common-replication"
)


def _point(temperature: int, pressure: int, exchange: int) -> OneComponentCoexistencePoint:
    return OneComponentCoexistencePoint(
        HeldLabel("chemical-component", "component-a"),
        HeldLabel("chemical-phase", "liquid"),
        HeldLabel("chemical-phase", "vapor"),
        PositiveCount(temperature),
        PositiveCount(pressure),
        PositiveCount(exchange),
        PositiveCount(exchange),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first = _point(3, 2, 5)
    second = _point(5, 4, 7)
    boundary = FiniteOneComponentBoundary((first, second))
    third = _point(8, 7, 9)
    return (
        ("exchange-balance", "Equal component exchange supports produce structural EmptyOne separation.", isinstance(coexistence_exchange_balance(first).separation, EmptyOne)),
        ("single-degree-support", "One component and two phases leave exactly one held coordinate carrier.", one_component_two_phase_degree_support_is_one(first)),
        ("ordered-successor", "The next stable coexistence point increases both exact held supports.", is_ordered_coexistence_successor(first, second)),
        ("append-and-replicate", "Ordered append and common exact replication preserve the finite boundary.", len(append_coexistence_successor(boundary, third).points) == 3 and common_support_replication_preserves_boundary(boundary, PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExchangeBalanceResult", "FiniteOneComponentBoundary",
    "OPERATIONAL_WITNESSES", "OneComponentCoexistencePoint", "append_coexistence_successor",
    "coexistence_exchange_balance", "common_support_replication_preserves_boundary",
    "is_ordered_coexistence_successor", "one_component_two_phase_degree_support_is_one",
)
