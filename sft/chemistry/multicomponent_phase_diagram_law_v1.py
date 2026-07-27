"""Fold-native finite multicomponent phase-diagram law for THERMO-013."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.chemistry.phase_rule_law_v1 import PhaseRuleAccount, independent_degree_support
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class PhaseCompositionCoordinate:
    component_identity: HeldLabel
    coordinate: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.component_identity, HeldLabel) or self.component_identity.family != "chemical-component":
            raise InadmissibleExactValue("phase composition lost its held component identity")
        if not isinstance(self.coordinate, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("phase composition requires an exact positive ratio or structural EmptyOne")


def _positive_coordinate_sum(coordinates: tuple[PhaseCompositionCoordinate, ...]) -> Fraction:
    positive = tuple(row.coordinate.fraction for row in coordinates if isinstance(row.coordinate, PositiveRatio))
    if not positive:
        raise InadmissibleExactValue("a phase composition cannot contain only structural absence")
    total = positive[0]
    for value in positive[1:]:
        total += value
    return total


@dataclass(frozen=True)
class ExactPhaseCompositionWord:
    phase_identity: HeldLabel
    coordinates: tuple[PhaseCompositionCoordinate, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.phase_identity, HeldLabel) or self.phase_identity.family != "chemical-phase":
            raise InadmissibleExactValue("composition word lost its held phase identity")
        if len(self.coordinates) < 2 or any(not isinstance(row, PhaseCompositionCoordinate) for row in self.coordinates):
            raise InadmissibleExactValue("multicomponent composition requires at least two complete coordinates")
        identities = tuple(row.component_identity for row in self.coordinates)
        if len(set(identities)) != len(identities):
            raise InadmissibleExactValue("phase composition duplicated a component")
        if _positive_coordinate_sum(self.coordinates) != Fraction(1, 1):
            raise InadmissibleExactValue("exact phase-composition support does not close to the One")


@dataclass(frozen=True)
class ComponentExchangeSupport:
    component_identity: HeldLabel
    first_phase_support: PositiveCount
    second_phase_support: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.component_identity, HeldLabel) or self.component_identity.family != "chemical-component":
            raise InadmissibleExactValue("exchange support lost component identity")
        if not isinstance(self.first_phase_support, PositiveCount) or not isinstance(self.second_phase_support, PositiveCount):
            raise InadmissibleExactValue("component exchange requires exact positive support")

    @property
    def balanced(self) -> bool:
        return self.first_phase_support.value == self.second_phase_support.value


@dataclass(frozen=True)
class MulticomponentCoexistencePoint:
    first_phase: ExactPhaseCompositionWord
    second_phase: ExactPhaseCompositionWord
    temperature_support: PositiveRatio
    pressure_support: PositiveRatio
    exchange_supports: tuple[ComponentExchangeSupport, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.first_phase, ExactPhaseCompositionWord) or not isinstance(self.second_phase, ExactPhaseCompositionWord):
            raise InadmissibleExactValue("coexistence requires two complete phase-composition words")
        if self.first_phase.phase_identity == self.second_phase.phase_identity:
            raise InadmissibleExactValue("coexistence requires two distinct held phases")
        first_components = tuple(row.component_identity for row in self.first_phase.coordinates)
        second_components = tuple(row.component_identity for row in self.second_phase.coordinates)
        exchange_components = tuple(row.component_identity for row in self.exchange_supports)
        if first_components != second_components or first_components != exchange_components:
            raise InadmissibleExactValue("coexisting phase words do not retain the same ordered component support")
        if any(not row.balanced for row in self.exchange_supports):
            raise InadmissibleExactValue("coexistence lost componentwise exchange-support balance")
        if not isinstance(self.temperature_support, PositiveRatio) or not isinstance(self.pressure_support, PositiveRatio):
            raise InadmissibleExactValue("coexistence requires exact positive environmental support")


def multicomponent_two_phase_degree_support(point: MulticomponentCoexistencePoint) -> PositiveCount:
    components = tuple(row.component_identity for row in point.first_phase.coordinates)
    support = independent_degree_support(PhaseRuleAccount(
        components,
        (point.first_phase.phase_identity, point.second_phase.phase_identity),
        (
            HeldLabel("phase-environment-coordinate", "temperature"),
            HeldLabel("phase-environment-coordinate", "pressure"),
        ),
    ))
    if not isinstance(support.count, PositiveCount) or support.count.value != len(components):
        raise InadmissibleExactValue("multicomponent two-phase support lost its exact component-count rank")
    return support.count


@dataclass(frozen=True)
class FiniteMulticomponentDiagram:
    points: tuple[MulticomponentCoexistencePoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise InadmissibleExactValue("a finite phase diagram requires positive point support")
        for point in self.points:
            multicomponent_two_phase_degree_support(point)


def append_coexistence_point(
    diagram: FiniteMulticomponentDiagram, point: MulticomponentCoexistencePoint
) -> FiniteMulticomponentDiagram:
    if not isinstance(diagram, FiniteMulticomponentDiagram):
        raise InadmissibleExactValue("phase-diagram extension requires a finite exact diagram")
    return FiniteMulticomponentDiagram(diagram.points + (point,))


def common_exchange_replication_preserves_point(
    point: MulticomponentCoexistencePoint, replication: PositiveCount
) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("exchange replication requires exact positive support")
    factor = replication.value
    replicated = MulticomponentCoexistencePoint(
        point.first_phase,
        point.second_phase,
        point.temperature_support,
        point.pressure_support,
        tuple(ComponentExchangeSupport(
            row.component_identity,
            PositiveCount(row.first_phase_support.value * factor),
            PositiveCount(row.second_phase_support.value * factor),
        ) for row in point.exchange_supports),
    )
    return all(row.balanced for row in replicated.exchange_supports)


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
    "SFT-CHEM-STOICH-SOLUTION-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    "SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
    "SFT-CHEM-PHASE-RULE-STRUCTURAL-011",
    "SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "unbound-coordinate-cloud", "Detached coordinates erase component, phase and coexistence identity.", "complete-multicomponent-two-phase-point", "Every point retains both phase words, all components and held environment."),
    dimension("composition", "selected-coordinate-or-unclosed-sum", "A selected coordinate or unclosed collection does not specify a composition.", "complete-exact-phase-words-closing-to-One", "Each phase retains every exact component coordinate and closes exactly to the One."),
    dimension("phase", "single-bulk-composition-or-erased-phase", "A bulk composition cannot identify two coexisting states.", "two-distinct-held-phase-composition-words", "Liquid and gas remain distinct held words over the same component ordering."),
    dimension("balance", "imported-lever-rule-or-target-derived-tie-line", "An imported construction or target correction does not force coexistence.", "componentwise-exact-exchange-support-balance", "Every component has equal exact exchange support across the two held phases."),
    dimension("degree", "free-continuum-diagram-plane", "A continuum plane imports unenumerated states and free coordinates.", "exact-phase-rule-component-count-support", "Two-phase degree support is the exact finite component-count carrier word."),
    dimension("absence", "numerical-zero-composition", "Numerical zero is not an SFT value.", "structural-EmptyOne-absent-coordinate", "A source zero glyph becomes structural EmptyOne while the inscription remains in provenance."),
    dimension("prediction", "coexistence-values-readable-before-seal", "Readable values could select the relation.", "complete-value-free-116-record-identity-seal", "All 65 binary and 51 ternary record identities seal before compounds, phases or values open."),
    dimension("extension", "redraw-refit-or-interpolate-after-extension", "Redrawing or fitting destroys exact finite provenance.", "depth-independent-append-and-exchange-replication", "Appending any complete balanced point and commonly replicating exchange support preserve the law."),
)


EXACT_RESULT = (
    "complete-multicomponent-two-phase-point__complete-exact-phase-words-closing-to-One__"
    "two-distinct-held-phase-composition-words__componentwise-exact-exchange-support-balance__"
    "exact-phase-rule-component-count-support__structural-EmptyOne-absent-coordinate__"
    "complete-value-free-116-record-identity-seal__depth-independent-append-and-exchange-replication"
)


def _coordinate(component: str, numerator: int, denominator: int) -> PhaseCompositionCoordinate:
    return PhaseCompositionCoordinate(
        HeldLabel("chemical-component", component), PositiveRatio.from_pair(numerator, denominator)
    )


def _point(component_count: int) -> MulticomponentCoexistencePoint:
    if component_count == 2:
        first = (_coordinate("a", 2, 5), _coordinate("b", 3, 5))
        second = (_coordinate("a", 3, 5), _coordinate("b", 2, 5))
    elif component_count == 3:
        first = (_coordinate("a", 1, 2), _coordinate("b", 1, 3), _coordinate("c", 1, 6))
        second = (_coordinate("a", 1, 3), _coordinate("b", 1, 2), _coordinate("c", 1, 6))
    else:
        raise InadmissibleExactValue("witness requires binary or ternary support")
    exchange = tuple(ComponentExchangeSupport(row.component_identity, PositiveCount(5), PositiveCount(5)) for row in first)
    return MulticomponentCoexistencePoint(
        ExactPhaseCompositionWord(HeldLabel("chemical-phase", "liquid"), first),
        ExactPhaseCompositionWord(HeldLabel("chemical-phase", "gas"), second),
        PositiveRatio.from_pair(7, 2), PositiveRatio.from_pair(9, 4), exchange,
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    binary, ternary = _point(2), _point(3)
    with_absence = ExactPhaseCompositionWord(
        HeldLabel("chemical-phase", "liquid"),
        (
            PhaseCompositionCoordinate(HeldLabel("chemical-component", "a"), EmptyOne()),
            _coordinate("b", 1, 1),
        ),
    )
    return (
        ("exact-composition-closure", "Binary and ternary phase words close exactly to the One.", _positive_coordinate_sum(binary.first_phase.coordinates) == Fraction(1, 1) and _positive_coordinate_sum(ternary.first_phase.coordinates) == Fraction(1, 1)),
        ("componentwise-exchange-balance", "Every component retains equal exchange support across both phases.", all(row.balanced for row in binary.exchange_supports + ternary.exchange_supports)),
        ("phase-rule-rank", "Two-phase binary and ternary words retain component-count degree support.", multicomponent_two_phase_degree_support(binary).value == 2 and multicomponent_two_phase_degree_support(ternary).value == 3),
        ("absence-and-extension", "EmptyOne boundary, append and common replication preserve the exact finite law.", isinstance(with_absence.coordinates[0].coordinate, EmptyOne) and len(append_coexistence_point(FiniteMulticomponentDiagram((binary,)), ternary).points) == 2 and common_exchange_replication_preserves_point(binary, PositiveCount(7))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ComponentExchangeSupport",
    "ExactPhaseCompositionWord", "FiniteMulticomponentDiagram", "MulticomponentCoexistencePoint",
    "OPERATIONAL_WITNESSES", "PhaseCompositionCoordinate", "append_coexistence_point",
    "common_exchange_replication_preserves_point", "multicomponent_two_phase_degree_support",
)
