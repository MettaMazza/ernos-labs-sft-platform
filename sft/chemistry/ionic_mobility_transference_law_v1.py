"""Fold-native ionic mobility and transference partition law (ECHEM-008)."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import ExactPart, HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class IonicMobilityAccount:
    species: HeldLabel
    direction: HeldLabel
    composition: HeldLabel
    condition: HeldLabel
    path: HeldLabel
    traversals: PositiveCount
    carriers: PositiveCount
    path_resource: PositiveCount

    def __post_init__(self) -> None:
        required = ((self.species, "ionic-species"), (self.direction, "transport-direction"), (self.composition, "electrolyte-composition"), (self.condition, "transport-condition"), (self.path, "transport-path"))
        if any(row.family != family for row, family in required):
            raise InadmissibleExactValue("mobility account lost species, direction, composition, condition or path")
        if not all(isinstance(row, PositiveCount) for row in (self.traversals, self.carriers, self.path_resource)):
            raise InadmissibleExactValue("mobility counts and resource must be positive exact values")

    @property
    def mobility(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.traversals.value, self.carriers.value * self.path_resource.value)

    @property
    def contribution(self) -> Fraction:
        return self.mobility.fraction * self.carriers.value


@dataclass(frozen=True)
class TransferenceRow:
    species: HeldLabel
    direction: HeldLabel
    mobility: PositiveRatio
    transference: ExactPart


@dataclass(frozen=True)
class MobilityTransferenceResult:
    rows: tuple[TransferenceRow, ...]
    complete_partition: ExactPart
    composition: HeldLabel
    condition: HeldLabel


def mobility_and_transference(accounts: tuple[IonicMobilityAccount, ...]) -> MobilityTransferenceResult:
    if not accounts:
        raise InadmissibleExactValue("mobility partition requires at least one ionic species")
    first = accounts[0]
    if any((row.composition, row.condition, row.path) != (first.composition, first.condition, first.path) for row in accounts):
        raise InadmissibleExactValue("mobility accounts must share composition, condition and path")
    if len({row.species for row in accounts}) != len(accounts):
        raise InadmissibleExactValue("every species must have exactly one mobility account")
    total = sum((row.contribution for row in accounts), Fraction(0, 1))
    rows = tuple(TransferenceRow(row.species, row.direction, row.mobility, ExactPart(row.contribution / total)) for row in accounts)
    partition = ExactPart(sum((row.transference.value for row in rows), Fraction(0, 1)))
    return MobilityTransferenceResult(rows, partition, first.composition, first.condition)


def absent_species_transference() -> EmptyOne:
    return EMPTY_ONE


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONDITIONAL-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019", "SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("identity", "anonymous-mobile-charge", "Anonymous charge loses chemical carrier identity.", "complete-held-ionic-species-identity", "Every mobile species remains named and distinct."),
    dimension("direction", "signed-mobility", "A sign imports negative proof magnitude.", "held-species-mobility-direction", "Direction is held separately from positive magnitude."),
    dimension("mobility", "continuum-velocity-field-quotient", "A continuum derivative is not a counted transport proof.", "exact-traversal-per-carrier-resource-ratio", "Mobility is an exact ratio of counted traversals, carriers and path resource."),
    dimension("composition", "isolated-ion-answer", "An isolated answer loses the complete electrolyte.", "common-composition-condition-path", "Every species shares the same held experimental support."),
    dimension("partition", "independent-fitted-transport-numbers", "Independent fits need not conserve the whole current.", "exact-species-contribution-partition", "Each transference part is its exact contribution divided by the complete total."),
    dimension("whole", "approximately-normalized-sum", "Approximate normalization can hide lost current.", "transference-parts-sum-exactly-to-One", "The complete finite partition reconstructs exactly One."),
    dimension("absence", "numerical-zero-absent-ion", "Numerical zero conflates absence with a measured response.", "structural-EmptyOne-absent-species", "An unregistered carrier is structurally absent."),
    dimension("record", "selected-transport-number", "A selected result can hide concentration change and anomalies.", "complete-mobility-transference-vector", "Every registered species, concentration, method, value and adverse row remains downstream."),
)

EXACT_RESULT = "complete-held-ionic-species-identity__held-species-mobility-direction__exact-traversal-per-carrier-resource-ratio__common-composition-condition-path__exact-species-contribution-partition__transference-parts-sum-exactly-to-One__structural-EmptyOne-absent-species__complete-mobility-transference-vector"


def _row(name: str, direction: str, traversals: int) -> IonicMobilityAccount:
    return IonicMobilityAccount(HeldLabel("ionic-species", name), HeldLabel("transport-direction", direction), HeldLabel("electrolyte-composition", "test"), HeldLabel("transport-condition", "held"), HeldLabel("transport-path", "path"), PositiveCount(traversals), PositiveCount(1), PositiveCount(2))


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    result = mobility_and_transference((_row("cation", "toward-terminal", 3), _row("anion", "toward-source", 1)))
    duplicate = False
    try:
        mobility_and_transference((_row("cation", "toward-terminal", 3), _row("cation", "toward-source", 1)))
    except InadmissibleExactValue:
        duplicate = True
    return (
        ("species", "Both species identities remain held.", len(result.rows) == 2),
        ("mobility", "Mobility is an exact positive ratio.", all(isinstance(row.mobility, PositiveRatio) for row in result.rows)),
        ("partition", "Contributions partition as three-quarters and one-quarter.", tuple(row.transference.value for row in result.rows) == (Fraction(3, 4), Fraction(1, 4))),
        ("whole", "Transference contributions sum exactly to One.", result.complete_partition.value == 1),
        ("direction", "Opposed species directions remain held.", result.rows[0].direction != result.rows[1].direction),
        ("composition", "Common composition remains held.", result.composition.family == "electrolyte-composition"),
        ("absence", "An absent species is structural EmptyOne.", absent_species_transference() == EMPTY_ONE),
        ("duplicate-control", "Duplicate species custody halts.", duplicate),
    )


OPERATIONAL_WITNESSES = _witnesses()

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "IonicMobilityAccount", "MobilityTransferenceResult", "OPERATIONAL_WITNESSES", "TransferenceRow", "absent_species_transference", "mobility_and_transference")
