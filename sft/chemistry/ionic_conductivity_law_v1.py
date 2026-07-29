"""Fold-native species-resolved ionic conductivity law (ECHEM-007)."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value: Fraction) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class IonicTransportContribution:
    species: HeldLabel
    direction: HeldLabel
    composition: HeldLabel
    condition: HeldLabel
    path: HeldLabel
    carried_distinctions: PositiveCount
    counted_path_resource: PositiveCount

    def __post_init__(self) -> None:
        required = ((self.species, "ionic-species"), (self.direction, "transport-direction"), (self.composition, "electrolyte-composition"), (self.condition, "transport-condition"), (self.path, "transport-path"))
        if any(row.family != family for row, family in required):
            raise InadmissibleExactValue("ionic transport requires species, direction, composition, condition and path custody")
        if not isinstance(self.carried_distinctions, PositiveCount) or not isinstance(self.counted_path_resource, PositiveCount):
            raise InadmissibleExactValue("ionic transport counts and resource must be exact and positive")

    @property
    def exact_response(self) -> Fraction:
        return Fraction(self.carried_distinctions.value, self.counted_path_resource.value)


@dataclass(frozen=True)
class IonicConductivityResult:
    exact_total_response: PositiveRatio
    species_contributions: tuple[IonicTransportContribution, ...]
    composition: HeldLabel
    condition: HeldLabel
    path: HeldLabel


def ionic_conductivity(contributions: tuple[IonicTransportContribution, ...]) -> IonicConductivityResult:
    if not contributions:
        raise InadmissibleExactValue("conductivity requires at least one observed ionic carrier")
    first = contributions[0]
    if any((row.composition, row.condition, row.path) != (first.composition, first.condition, first.path) for row in contributions):
        raise InadmissibleExactValue("species contributions must share composition, condition and path")
    if len({row.species for row in contributions}) != len(contributions):
        raise InadmissibleExactValue("each ionic species must have exactly one retained contribution")
    return IonicConductivityResult(_ratio(sum((row.exact_response for row in contributions), Fraction(0, 1))), contributions, first.composition, first.condition, first.path)


def append_species(contributions: tuple[IonicTransportContribution, ...], successor: IonicTransportContribution) -> bool:
    prior = ionic_conductivity(contributions)
    extended = ionic_conductivity(contributions + (successor,))
    return extended.exact_total_response.fraction > prior.exact_total_response.fraction


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-RESOURCE-LAW-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019",
    "SFT-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "bulk-conductance-number", "A bulk number loses the transporting ions.", "complete-species-resolved-carrier-vector", "Every ionic species remains separately held."),
    dimension("direction", "signed-flux-premise", "Signed flux imports negative proof magnitude.", "held-species-transport-direction", "Direction is a held label for each positive contribution."),
    dimension("composition", "composition-free-conductivity", "Conductivity without composition is not chemically identified.", "complete-held-electrolyte-composition", "Electrolyte composition remains explicit."),
    dimension("condition", "mixed-temperature-response", "Mixed conditions cannot form one conductivity.", "one-common-held-condition", "All contributions share one condition."),
    dimension("path", "continuum-gradient-premise", "A continuum gradient hides counted transport support.", "finite-held-path-resource-account", "Transport occurs over a held finite path with positive resource count."),
    dimension("aggregation", "fitted-mixture-coefficient", "A fitted coefficient adds an unforced parameter.", "exact-sum-of-species-responses", "The total is the exact sum of all retained species contributions."),
    dimension("record", "selected-conductivity-value", "A selected value can hide composition, temperature and uncertainty.", "complete-traceable-conductivity-vector", "Every registered certificate value, unit, uncertainty and method row remains downstream."),
    dimension("extension", "fixed-species-count", "A fixed count cannot extend to new admitted carriers.", "positive-species-successor-increases-response", "Appending a positive distinct contribution increases the exact total."),
)

EXACT_RESULT = "complete-species-resolved-carrier-vector__held-species-transport-direction__complete-held-electrolyte-composition__one-common-held-condition__finite-held-path-resource-account__exact-sum-of-species-responses__complete-traceable-conductivity-vector__positive-species-successor-increases-response"


def _row(name: str, count: int, resource: int = 2, condition: str = "held") -> IonicTransportContribution:
    return IonicTransportContribution(HeldLabel("ionic-species", name), HeldLabel("transport-direction", "toward-terminal"), HeldLabel("electrolyte-composition", "test-solution"), HeldLabel("transport-condition", condition), HeldLabel("transport-path", "test-path"), PositiveCount(count), PositiveCount(resource))


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first, second = _row("cation", 3), _row("anion", 1)
    total = ionic_conductivity((first, second))
    mismatch = False
    try:
        ionic_conductivity((first, _row("other", 1, condition="changed")))
    except InadmissibleExactValue:
        mismatch = True
    empty = False
    try:
        ionic_conductivity(())
    except InadmissibleExactValue:
        empty = True
    return (
        ("species", "Both ionic species remain present.", len(total.species_contributions) == 2),
        ("exact-sum", "Three-halves plus one-half yields exact two.", total.exact_total_response.fraction == 2),
        ("positive", "Total response is positive exact.", isinstance(total.exact_total_response, PositiveRatio)),
        ("composition", "Composition remains held.", total.composition == first.composition),
        ("condition", "Condition remains held.", total.condition == first.condition),
        ("extension", "A positive species successor increases response.", append_species((first,), second)),
        ("mixed-control", "Mixed conditions halt.", mismatch),
        ("empty-control", "Carrier-free response halts.", empty),
    )


OPERATIONAL_WITNESSES = _witnesses()

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "IonicConductivityResult", "IonicTransportContribution", "OPERATIONAL_WITNESSES", "append_species", "ionic_conductivity")
