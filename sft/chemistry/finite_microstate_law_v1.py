"""Fold-native finite chemical microstate-support law for THERMO-001.

The law generates a complete finite support of held chemical states, partitions
that support into disjoint macro-observation fibres, and derives multiplicity
and statistical weight by exact counting.  It contains no continuum ensemble,
partition-function prior, fitted distribution, temperature target, or measured
population.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ChemicalMicrostate:
    state_id: HeldLabel
    composition: HeldLabel
    phase: HeldLabel
    condition: HeldLabel
    internal_state: HeldLabel

    def __post_init__(self) -> None:
        required = (
            (self.state_id, "chemical-microstate"),
            (self.composition, "chemical-composition"),
            (self.phase, "phase-identity"),
            (self.condition, "observation-condition"),
            (self.internal_state, "internal-state-identity"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("chemical microstate lost a required held identity")


@dataclass(frozen=True)
class MacroObservationFibre:
    macrostate_id: HeldLabel
    microstates: tuple[ChemicalMicrostate, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.macrostate_id, HeldLabel) or self.macrostate_id.family != "chemical-macrostate":
            raise InadmissibleExactValue("macro-observation requires a held chemical macrostate")
        if not isinstance(self.microstates, tuple) or not self.microstates:
            raise InadmissibleExactValue("macro-observation fibre must be finite and nonempty")
        if any(not isinstance(state, ChemicalMicrostate) for state in self.microstates):
            raise InadmissibleExactValue("macro-observation fibre contains a non-chemical state")
        if len(set(self.microstates)) != len(self.microstates):
            raise InadmissibleExactValue("macro-observation fibre duplicates a microstate")


@dataclass(frozen=True)
class FiniteChemicalSupport:
    microstates: tuple[ChemicalMicrostate, ...]
    fibres: tuple[MacroObservationFibre, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.microstates, tuple) or not self.microstates:
            raise InadmissibleExactValue("chemical support must be generated, finite and nonempty")
        if any(not isinstance(state, ChemicalMicrostate) for state in self.microstates):
            raise InadmissibleExactValue("chemical support contains a non-chemical state")
        if len(set(self.microstates)) != len(self.microstates):
            raise InadmissibleExactValue("chemical support duplicates a microstate")
        if not isinstance(self.fibres, tuple) or not self.fibres:
            raise InadmissibleExactValue("chemical support requires a finite observation partition")
        if len({fibre.macrostate_id for fibre in self.fibres}) != len(self.fibres):
            raise InadmissibleExactValue("chemical support duplicates a macro-observation identity")
        flattened = tuple(state for fibre in self.fibres for state in fibre.microstates)
        if len(flattened) != len(set(flattened)) or set(flattened) != set(self.microstates):
            raise InadmissibleExactValue("observation fibres must partition the complete support exactly once")


def finite_multiplicity(fibre: MacroObservationFibre) -> PositiveCount:
    """Return the exact positive number of generated predecessors in one fibre."""

    if not isinstance(fibre, MacroObservationFibre):
        raise InadmissibleExactValue("multiplicity requires one finite macro-observation fibre")
    return PositiveCount(len(fibre.microstates))


def exact_statistical_weight(
    support: FiniteChemicalSupport,
    macrostate_id: HeldLabel,
) -> PositiveRatio:
    """Return fibre count over complete support count with no distribution prior."""

    if not isinstance(support, FiniteChemicalSupport):
        raise InadmissibleExactValue("statistical weight requires complete finite chemical support")
    matches = tuple(fibre for fibre in support.fibres if fibre.macrostate_id == macrostate_id)
    if len(matches) != 1:
        raise InadmissibleExactValue("macro-observation identity is absent or non-unique")
    return PositiveRatio.from_pair(len(matches[0].microstates), len(support.microstates))


def append_generated_microstate(
    support: FiniteChemicalSupport,
    state: ChemicalMicrostate,
    macrostate_id: HeldLabel,
) -> FiniteChemicalSupport:
    """Append one generated state and its named fibre while preserving all prior assignments."""

    if state in support.microstates:
        raise InadmissibleExactValue("finite successor must add a new microstate")
    if any(fibre.macrostate_id == macrostate_id for fibre in support.fibres):
        raise InadmissibleExactValue("this successor certificate requires a new macro-observation class")
    return FiniteChemicalSupport(
        support.microstates + (state,),
        support.fibres + (MacroObservationFibre(macrostate_id, (state,)),),
    )


def finite_successor_preserves_prior_assignments(
    support: FiniteChemicalSupport,
    state: ChemicalMicrostate,
    macrostate_id: HeldLabel,
) -> bool:
    extended = append_generated_microstate(support, state, macrostate_id)
    return (
        extended.microstates[:-1] == support.microstates
        and extended.fibres[:-1] == support.fibres
        and extended.microstates[-1] == state
        and extended.fibres[-1].microstates == (state,)
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-THERMO-MICRO-MACRO-001",
    "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001",
    "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-or-completed-infinite-state-set", "A selected or completed-infinite set is neither generated nor exhaustible.", "complete-generated-finite-chemical-support", "Every admitted microstate is explicitly generated and retained once."),
    dimension("identity", "answer-only-state-count", "A bare count erases composition, phase, condition and internal-state identity.", "complete-held-chemical-microstate-identity", "Each state retains every chemical identity required to distinguish it."),
    dimension("partition", "overlapping-or-omitting-observation-classes", "Overlap duplicates predecessors and omission deletes them.", "disjoint-exhaustive-macro-observation-partition", "Every microstate occurs in exactly one named observation fibre."),
    dimension("multiplicity", "floating-or-assumed-degeneracy", "An assumed degeneracy imports an ungenerated statistical parameter.", "exact-positive-fibre-count", "Multiplicity is the exact positive census of one generated fibre."),
    dimension("weight", "imported-distribution-or-partition-function", "An imported distribution lets a prior select state weights.", "exact-fibre-count-over-complete-support-count", "Weight is forced by two exact finite counts."),
    dimension("prediction", "population-temperature-or-calorimetric-target-readable-before-seal", "Target access can select the state support or partition.", "complete-value-free-state-and-calorimetric-identity-seal", "All external identities seal without measured values."),
    dimension("record", "selected-population-or-calorimetric-showcase", "A selected example cannot establish complete source custody.", "complete-387-row-external-structure-custody", "All 330 direct state and 57 calorimetric rows remain explicit."),
    dimension("extension", "continuum-or-completed-infinity-closure", "A completed continuum is not a finite generated successor.", "depth-independent-one-state-finite-successor", "One new state and fibre append without changing prior assignments."),
)


EXACT_RESULT = (
    "complete-generated-finite-chemical-support__complete-held-chemical-microstate-identity__"
    "disjoint-exhaustive-macro-observation-partition__exact-positive-fibre-count__"
    "exact-fibre-count-over-complete-support-count__complete-value-free-state-and-calorimetric-identity-seal__"
    "complete-387-row-external-structure-custody__depth-independent-one-state-finite-successor"
)


def _state(label: str) -> ChemicalMicrostate:
    return ChemicalMicrostate(
        HeldLabel("chemical-microstate", label),
        HeldLabel("chemical-composition", "held-composition"),
        HeldLabel("phase-identity", "held-phase"),
        HeldLabel("observation-condition", "held-condition"),
        HeldLabel("internal-state-identity", label + "-internal"),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first, second, third, fourth = (_state(label) for label in ("first", "second", "third", "fourth"))
    low = MacroObservationFibre(HeldLabel("chemical-macrostate", "low-class"), (first, second))
    high = MacroObservationFibre(HeldLabel("chemical-macrostate", "high-class"), (third,))
    support = FiniteChemicalSupport((first, second, third), (low, high))
    overlap_rejected = False
    try:
        FiniteChemicalSupport((first, second, third), (low, MacroObservationFibre(high.macrostate_id, (second, third))))
    except InadmissibleExactValue:
        overlap_rejected = True
    return (
        ("complete-partition", "Every generated state occurs in exactly one fibre.", len(support.microstates) == 3),
        ("exact-multiplicity", "The first observation has exactly two predecessors.", finite_multiplicity(low).value == 2),
        ("exact-count-weight", "The two fibres have exact weights two-thirds and one-third.", exact_statistical_weight(support, low.macrostate_id) == PositiveRatio.from_pair(2, 3) and exact_statistical_weight(support, high.macrostate_id) == PositiveRatio.from_pair(1, 3)),
        ("overlap-rejected", "A predecessor cannot occur in two observation fibres.", overlap_rejected),
        ("finite-successor", "Appending one state preserves all prior assignments.", finite_successor_preserves_prior_assignments(support, fourth, HeldLabel("chemical-macrostate", "successor-class"))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "ChemicalMicrostate", "FiniteChemicalSupport", "MacroObservationFibre",
    "append_generated_microstate", "exact_statistical_weight", "finite_multiplicity",
    "finite_successor_preserves_prior_assignments",
)
