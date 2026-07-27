"""Fold-native activity and non-ideal composition law for THERMO-009."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class SolutionCompositionCoordinate:
    component_identity: HeldLabel
    coordinate: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.component_identity, HeldLabel) or self.component_identity.family != "chemical-component":
            raise InadmissibleExactValue("solution coordinate lost its component identity")
        if not isinstance(self.coordinate, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("solution coordinate must be exact positive or structural absence")


@dataclass(frozen=True)
class SolutionActivityAccount:
    component_identity: HeldLabel
    phase_identity: HeldLabel
    environment_identity: HeldLabel
    composition: tuple[SolutionCompositionCoordinate, ...]
    accessible_exchange_support: PositiveCount
    reference_exchange_support: PositiveCount
    independently_composed_support: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.component_identity, "chemical-component"),
            (self.phase_identity, "chemical-phase"),
            (self.environment_identity, "chemical-environment"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("solution activity account lost a held identity")
        if not self.composition or any(not isinstance(row, SolutionCompositionCoordinate) for row in self.composition):
            raise InadmissibleExactValue("solution activity account requires the complete composition")
        identities = tuple(row.component_identity for row in self.composition)
        if len(set(identities)) != len(identities):
            raise InadmissibleExactValue("solution composition duplicated a component")
        counts = (
            self.accessible_exchange_support,
            self.reference_exchange_support,
            self.independently_composed_support,
        )
        if any(not isinstance(value, PositiveCount) for value in counts):
            raise InadmissibleExactValue("solution activity account requires exact positive support counts")
        if self.accessible_exchange_support.value > self.reference_exchange_support.value:
            raise InadmissibleExactValue("accessible exchange support exceeds the held reference support")


@dataclass(frozen=True)
class NonIdealCompositionResult:
    relation: HeldLabel
    support_separation: PositiveCount | EmptyOne


def exact_relative_activity(account: SolutionActivityAccount) -> PositiveRatio:
    if not isinstance(account, SolutionActivityAccount):
        raise InadmissibleExactValue("relative activity requires a complete solution account")
    return PositiveRatio.from_pair(
        account.accessible_exchange_support.value,
        account.reference_exchange_support.value,
    )


def nonideal_composition_relation(account: SolutionActivityAccount) -> NonIdealCompositionResult:
    if not isinstance(account, SolutionActivityAccount):
        raise InadmissibleExactValue("non-ideal relation requires a complete solution account")
    actual = account.accessible_exchange_support.value
    independent = account.independently_composed_support.value
    if actual == independent:
        return NonIdealCompositionResult(HeldLabel("solution-composition", "independent"), EmptyOne())
    relation = "interaction-restricted" if actual < independent else "interaction-expanded"
    return NonIdealCompositionResult(
        HeldLabel("solution-composition", relation), PositiveCount(abs(actual - independent))
    )


def replicated_support_preserves_activity_and_relation(
    account: SolutionActivityAccount, replication: PositiveCount
) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("support successor requires an exact positive replication count")
    prior_activity = exact_relative_activity(account)
    prior_relation = nonideal_composition_relation(account).relation
    replicated = SolutionActivityAccount(
        account.component_identity,
        account.phase_identity,
        account.environment_identity,
        account.composition,
        PositiveCount(account.accessible_exchange_support.value * replication.value),
        PositiveCount(account.reference_exchange_support.value * replication.value),
        PositiveCount(account.independently_composed_support.value * replication.value),
    )
    return (
        exact_relative_activity(replicated).fraction == prior_activity.fraction
        and nonideal_composition_relation(replicated).relation == prior_relation
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-MIXTURE-001",
    "SFT-CHEM-STOICH-SOLUTION-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "bulk-answer-or-unbound-activity-number",
        "An unbound number erases the component exchange support it measures.",
        "complete-component-exchange-support-account",
        "Activity remains bound to one component, phase, environment and complete support account.",
    ),
    dimension(
        "composition",
        "selected-or-erased-composition-and-condition",
        "Erasing composition or condition makes distinct solution states indistinguishable.",
        "complete-held-condition-and-component-coordinates",
        "Every component coordinate and the finite environment remain held.",
    ),
    dimension(
        "activity",
        "logarithm-fugacity-or-fitted-coefficient",
        "A logarithm, fugacity model or fitted coefficient imports an unforced scalar model.",
        "exact-accessible-support-over-reference-support",
        "Relative activity is the exact positive accessible-support count over reference-support count.",
    ),
    dimension(
        "interaction",
        "ideal-mixture-prior-or-target-derived-correction",
        "Assumed ideality or a target-derived correction selects the relation externally.",
        "exact-joint-versus-independent-support-relation",
        "Non-ideality is the exact held relation between joint accessible and independently composed support.",
    ),
    dimension(
        "absence",
        "numerical-zero-component-coordinate",
        "Numerical zero would introduce a non-SFT number for an absent component.",
        "structural-EmptyOne-absent-component",
        "An externally absent component becomes structural EmptyOne while its source glyph is retained.",
    ),
    dimension(
        "prediction",
        "activity-composition-or-condition-readable-before-seal",
        "Withheld values could select the support relation.",
        "complete-value-free-204-row-identity-seal",
        "All 204 source-row identities seal before compounds, composition, condition or activity open.",
    ),
    dimension(
        "record",
        "selected-system-or-deleted-absence-boundary",
        "Selecting a solution or dropping absent-component rows hides the complete evidence surface.",
        "complete-nine-dataset-204-row-vector-with-68-EmptyOne-boundaries",
        "All nine datasets, 204 rows and 68 structural-absence boundaries are retained.",
    ),
    dimension(
        "extension",
        "refit-after-support-replication",
        "Refitting after exact replication destroys the count relation.",
        "depth-independent-exact-support-replication",
        "Common exact replication preserves activity and the non-ideal relation at every finite depth.",
    ),
)


EXACT_RESULT = (
    "complete-component-exchange-support-account__complete-held-condition-and-component-coordinates__"
    "exact-accessible-support-over-reference-support__exact-joint-versus-independent-support-relation__"
    "structural-EmptyOne-absent-component__complete-value-free-204-row-identity-seal__"
    "complete-nine-dataset-204-row-vector-with-68-EmptyOne-boundaries__"
    "depth-independent-exact-support-replication"
)


def _account(accessible: int, reference: int, independent: int) -> SolutionActivityAccount:
    return SolutionActivityAccount(
        HeldLabel("chemical-component", "water"),
        HeldLabel("chemical-phase", "liquid-solution"),
        HeldLabel("chemical-environment", "held-environment"),
        (
            SolutionCompositionCoordinate(
                HeldLabel("chemical-component", "solute-a"), PositiveRatio.from_pair(3, 2)
            ),
            SolutionCompositionCoordinate(HeldLabel("chemical-component", "solute-b"), EmptyOne()),
        ),
        PositiveCount(accessible),
        PositiveCount(reference),
        PositiveCount(independent),
    )


def _witnesses():
    restricted = _account(6, 10, 8)
    independent = _account(8, 10, 8)
    expanded = _account(9, 10, 8)
    return (
        (
            "exact-relative-activity",
            "Accessible support over reference support is an exact positive fraction.",
            exact_relative_activity(restricted).fraction == PositiveRatio.from_pair(3, 5).fraction,
        ),
        (
            "three-composition-relations",
            "Exact comparison distinguishes restricted, independent and expanded joint support.",
            nonideal_composition_relation(restricted).relation.label == "interaction-restricted"
            and nonideal_composition_relation(independent).relation.label == "independent"
            and nonideal_composition_relation(expanded).relation.label == "interaction-expanded",
        ),
        (
            "structural-absence",
            "Absent solute is retained as EmptyOne rather than numerical zero.",
            isinstance(restricted.composition[1].coordinate, EmptyOne),
        ),
        (
            "replication-successor",
            "Exact support replication preserves activity and relation.",
            replicated_support_preserves_activity_and_relation(restricted, PositiveCount(7)),
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "NonIdealCompositionResult",
    "OPERATIONAL_WITNESSES",
    "SolutionActivityAccount",
    "SolutionCompositionCoordinate",
    "exact_relative_activity",
    "nonideal_composition_relation",
    "replicated_support_preserves_activity_and_relation",
)
