"""Fold-native conditioned conformer population and ordering law for ORG-006."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union

from sft.chemistry.conformer_generation_equivalence_law_v1 import (
    ExactConformerAssignment,
    ExactConformerCensus,
    butane_four_site_census,
)
from sft.claim_evidence import PositiveRatio
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


ExactPopulation = Union[EmptyOne, PositiveRatio]
ExactRelativeEnergy = Union[EmptyOne, PositiveRatio]


def ordered_positive_take(higher: ExactRelativeEnergy, lower: ExactRelativeEnergy) -> PositiveRatio:
    if higher is EMPTY_ONE or not isinstance(higher, PositiveRatio):
        raise InadmissibleExactValue("higher conformer energy must retain a positive exact magnitude")
    if lower is EMPTY_ONE:
        return higher
    if not isinstance(lower, PositiveRatio) or higher.fraction <= lower.fraction:
        raise InadmissibleExactValue("energy Take requires a strictly lower retained conformer state")
    gap = higher.fraction - lower.fraction
    return PositiveRatio.from_pair(gap.numerator, gap.denominator)


@dataclass(frozen=True)
class ConditionedConformerObservation:
    condition: HeldLabel
    observation_boundary: PositiveCount
    trace: tuple[ExactConformerAssignment, ...]

    def __post_init__(self) -> None:
        if self.condition.family != "observation-condition":
            raise InadmissibleExactValue("conformer population requires one retained observation condition")
        if not isinstance(self.observation_boundary, PositiveCount) or len(self.trace) != self.observation_boundary.value:
            raise InadmissibleExactValue("observation boundary must equal the complete positive trace length")


@dataclass(frozen=True)
class ConformerPopulationRow:
    equivalence_class: tuple[ExactConformerAssignment, ...]
    occurrence_count: Union[EmptyOne, PositiveCount]
    population: ExactPopulation
    relative_energy: ExactRelativeEnergy

    def __post_init__(self) -> None:
        if not self.equivalence_class:
            raise InadmissibleExactValue("population row requires one complete conformer equivalence class")
        if self.occurrence_count is EMPTY_ONE:
            if self.population is not EMPTY_ONE:
                raise InadmissibleExactValue("unobserved class population is structural EmptyOne")
        elif not isinstance(self.occurrence_count, PositiveCount) or not isinstance(self.population, PositiveRatio):
            raise InadmissibleExactValue("observed class population requires positive exact count and ratio")
        if not isinstance(self.relative_energy, (EmptyOne, PositiveRatio)):
            raise InadmissibleExactValue("relative energy must be structural least-state EmptyOne or positive exact magnitude")


@dataclass(frozen=True)
class ExactConditionedPopulationCensus:
    conformers: ExactConformerCensus
    observation: ConditionedConformerObservation
    rows: tuple[ConformerPopulationRow, ...]

    def __post_init__(self) -> None:
        if len(self.rows) != len(self.conformers.equivalence_classes):
            raise InadmissibleExactValue("population census requires every conformer class exactly once")
        if tuple(row.equivalence_class for row in self.rows) != self.conformers.equivalence_classes:
            raise InadmissibleExactValue("population rows changed or reordered the conformer quotient")
        allowed = set(self.conformers.generated_assignments)
        if any(state not in allowed for state in self.observation.trace):
            raise InadmissibleExactValue("observation trace contains an ungenerated conformer assignment")
        total = sum(row.occurrence_count.value for row in self.rows if isinstance(row.occurrence_count, PositiveCount))
        if total != self.observation.observation_boundary.value:
            raise InadmissibleExactValue("population counts do not exhaust the complete observation boundary")
        for row in self.rows:
            observed = sum(state in row.equivalence_class for state in self.observation.trace)
            if observed < 1:
                if row.occurrence_count is not EMPTY_ONE or row.population is not EMPTY_ONE:
                    raise InadmissibleExactValue("structurally absent observations must remain EmptyOne")
            else:
                expected = PositiveRatio.from_pair(observed, self.observation.observation_boundary.value)
                if row.occurrence_count != PositiveCount(observed) or row.population != expected:
                    raise InadmissibleExactValue("population must equal exact class occurrences over the retained boundary")

    def population_order(self) -> tuple[tuple[ExactConformerAssignment, ...], ...]:
        def key(row: ConformerPopulationRow) -> Fraction:
            return Fraction(0, 1) if row.population is EMPTY_ONE else row.population.fraction
        return tuple(row.equivalence_class for row in sorted(self.rows, key=key, reverse=True))

    def energy_order(self) -> tuple[tuple[ExactConformerAssignment, ...], ...]:
        def key(row: ConformerPopulationRow) -> Fraction:
            return Fraction(0, 1) if row.relative_energy is EMPTY_ONE else row.relative_energy.fraction
        return tuple(row.equivalence_class for row in sorted(self.rows, key=key))


def conditioned_population_census(
    conformers: ExactConformerCensus,
    condition: HeldLabel,
    trace: tuple[ExactConformerAssignment, ...],
    relative_energies: tuple[ExactRelativeEnergy, ...],
) -> ExactConditionedPopulationCensus:
    if not trace or len(relative_energies) != len(conformers.equivalence_classes):
        raise InadmissibleExactValue("complete trace and one energy record per conformer class are required")
    boundary = PositiveCount(len(trace))
    rows = []
    for group, energy in zip(conformers.equivalence_classes, relative_energies):
        count = sum(state in group for state in trace)
        occurrence = EMPTY_ONE if count < 1 else PositiveCount(count)
        population = EMPTY_ONE if count < 1 else PositiveRatio.from_pair(count, boundary.value)
        rows.append(ConformerPopulationRow(group, occurrence, population, energy))
    return ExactConditionedPopulationCensus(
        conformers,
        ConditionedConformerObservation(condition, boundary, trace),
        tuple(rows),
    )


def append_observation(
    census: ExactConditionedPopulationCensus,
    assignment: ExactConformerAssignment,
) -> ExactConditionedPopulationCensus:
    return conditioned_population_census(
        census.conformers,
        census.observation.condition,
        census.observation.trace + (assignment,),
        tuple(row.relative_energy for row in census.rows),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
    "SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-conformer-name", "A selected name omits the complete derived equivalence quotient.", "complete-conformer-equivalence-census", "Every ORG-005 conformer class remains retained exactly once."),
    dimension("condition", "condition-erased-population", "Population without physical condition conflates distinct deterministic traces.", "held-observation-condition", "Every population vector retains its exact condition identity."),
    dimension("boundary", "infinite-or-unspecified-average", "An unspecified limit imports continuum or unbounded averaging.", "positive-finite-observation-boundary", "The complete positive finite trace length is retained exactly."),
    dimension("population", "random-or-fitted-probability", "A random law or fitted distribution is not forced by the observed process.", "exact-recurrence-count-ratio", "Each population is its exact deterministic class count over the retained boundary."),
    dimension("absence", "numerical-zero-population", "Numerical zero is not a native Fold form.", "unobserved-class-EmptyOne", "A class absent from the finite trace retains structural EmptyOne."),
    dimension("order", "signed-energy-difference-or-imported-distribution", "A signed difference or imported exponential law adds forbidden arithmetic.", "positive-Take-energy-and-count-orders", "Energy uses ordered positive Take; population order compares exact count ratios."),
    dimension("observation", "target-readable-condition-or-value", "External temperature, duration, energy or population could select the law.", "value-free-conditioned-vector-seal", "Law, condition slots and exact comparison operations seal before target values open."),
    dimension("extension", "recomputed-history-or-extra-rule", "Discarding history or adding a smoothing rule changes the declared population.", "one-observation-successor-no-extra-rule", "Each successor retains the trace and appends exactly one generated observation."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    conformers = butane_four_site_census()
    anti = conformers.generated_assignments[0]
    gauche_forward, gauche_reverse = conformers.generated_assignments[1:]
    census = conditioned_population_census(
        conformers,
        HeldLabel("observation-condition", "fixed-condition-and-timescale"),
        (anti, anti, gauche_forward, anti),
        (EMPTY_ONE, PositiveRatio.from_pair(3, 1)),
    )
    successor = append_observation(census, gauche_reverse)
    reverse_take_rejected = foreign_trace_rejected = False
    try:
        ordered_positive_take(PositiveRatio.from_pair(1, 1), PositiveRatio.from_pair(3, 1))
    except InadmissibleExactValue:
        reverse_take_rejected = True
    try:
        conditioned_population_census(
            conformers,
            HeldLabel("observation-condition", "fixed-condition-and-timescale"),
            (ExactConformerAssignment((HeldLabel("torsion-state", "foreign"),)),),
            (EMPTY_ONE, PositiveRatio.from_pair(3, 1)),
        )
    except InadmissibleExactValue:
        foreign_trace_rejected = True
    return (
        ("exact-populations", "Three anti and one gauche observations force exact populations three-fourths and one-fourth.", tuple(row.population.fraction for row in census.rows if isinstance(row.population, PositiveRatio)) == (Fraction(3, 4), Fraction(1, 4))),
        ("complete-class-census", "Both conformer classes remain present exactly once.", len(census.rows) == 2),
        ("energy-order", "Structural least-state EmptyOne precedes one exact positive-energy class.", census.energy_order() == (census.rows[0].equivalence_class, census.rows[1].equivalence_class)),
        ("population-order", "Exact recurrence counts force anti before gauche at this retained condition and boundary.", census.population_order() == (census.rows[0].equivalence_class, census.rows[1].equivalence_class)),
        ("observation-successor", "Appending one generated observation retains history and updates exact ratios to three-fifths and two-fifths.", tuple(row.population.fraction for row in successor.rows if isinstance(row.population, PositiveRatio)) == (Fraction(3, 5), Fraction(2, 5))),
        ("reverse-Take-control", "Reversing energy Take halts instead of creating a negative magnitude.", reverse_take_rejected),
        ("foreign-trace-control", "An ungenerated conformer assignment in the trace halts.", foreign_trace_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-conformer-equivalence-census__held-observation-condition__positive-finite-observation-boundary__"
    "exact-recurrence-count-ratio__unobserved-class-EmptyOne__positive-Take-energy-and-count-orders__"
    "value-free-conditioned-vector-seal__one-observation-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactConditionedPopulationCensus",
    "OPERATIONAL_WITNESSES", "append_observation", "conditioned_population_census",
    "ordered_positive_take",
)
