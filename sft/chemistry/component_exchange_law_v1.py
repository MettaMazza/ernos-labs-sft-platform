"""Fold-native chemical-potential-equivalent component law for THERMO-008."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class ComponentAdditionAccount:
    """Complete exact marginal account for adding one held component to one phase."""

    component_identity: HeldLabel
    phase_identity: HeldLabel
    environment_identity: HeldLabel
    retained_energy_increment: PositiveRatio
    closed_distinction_increment: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.component_identity, "chemical-component"),
            (self.phase_identity, "chemical-phase"),
            (self.environment_identity, "chemical-environment"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("component-addition account lost a held identity")
        if not isinstance(self.retained_energy_increment, PositiveRatio) or not isinstance(
            self.closed_distinction_increment, PositiveCount
        ):
            raise InadmissibleExactValue("component-addition account requires exact positive increments")


@dataclass(frozen=True)
class ComponentExchangeResult:
    orientation: HeldLabel
    energy_separation: PositiveRatio | EmptyOne
    distinction_separation: PositiveCount | EmptyOne


def component_exchange_relation(
    first_phase: ComponentAdditionAccount,
    second_phase: ComponentAdditionAccount,
) -> ComponentExchangeResult:
    """Order one component's complete addition accounts at one held environment."""

    if not isinstance(first_phase, ComponentAdditionAccount) or not isinstance(
        second_phase, ComponentAdditionAccount
    ):
        raise InadmissibleExactValue("component exchange requires two complete phase accounts")
    if first_phase.component_identity != second_phase.component_identity:
        raise InadmissibleExactValue("component exchange changed component identity")
    if first_phase.environment_identity != second_phase.environment_identity:
        raise InadmissibleExactValue("component exchange changed the fixed environment")
    if first_phase.phase_identity == second_phase.phase_identity:
        raise InadmissibleExactValue("component exchange requires distinct phases")
    first_energy = first_phase.retained_energy_increment.fraction
    second_energy = second_phase.retained_energy_increment.fraction
    first_distinctions = first_phase.closed_distinction_increment.value
    second_distinctions = second_phase.closed_distinction_increment.value
    if first_energy == second_energy and first_distinctions == second_distinctions:
        return ComponentExchangeResult(
            HeldLabel("component-exchange", "equilibrium"), EmptyOne(), EmptyOne()
        )
    first_no_greater = first_energy <= second_energy and first_distinctions <= second_distinctions
    second_no_greater = second_energy <= first_energy and second_distinctions <= first_distinctions
    if first_no_greater and (first_energy < second_energy or first_distinctions < second_distinctions):
        orientation = "toward-first-phase"
    elif second_no_greater and (second_energy < first_energy or second_distinctions < first_distinctions):
        orientation = "toward-second-phase"
    else:
        raise InadmissibleExactValue(
            "crossed component-addition accounts do not force a scalar chemical potential"
        )
    energy = (
        EmptyOne()
        if first_energy == second_energy
        else _ratio(abs(first_energy - second_energy))
    )
    distinctions = (
        EmptyOne()
        if first_distinctions == second_distinctions
        else PositiveCount(abs(first_distinctions - second_distinctions))
    )
    return ComponentExchangeResult(
        HeldLabel("component-exchange", orientation), energy, distinctions
    )


def common_context_successor_preserves_exchange(
    first_phase: ComponentAdditionAccount,
    second_phase: ComponentAdditionAccount,
    energy_extension: PositiveRatio,
    distinction_extension: PositiveCount,
) -> bool:
    """A common exact context addition cannot change the component relation."""

    if not isinstance(energy_extension, PositiveRatio) or not isinstance(
        distinction_extension, PositiveCount
    ):
        raise InadmissibleExactValue("common successor requires exact positive additions")
    prior = component_exchange_relation(first_phase, second_phase)

    def extend(account: ComponentAdditionAccount) -> ComponentAdditionAccount:
        return ComponentAdditionAccount(
            account.component_identity,
            account.phase_identity,
            account.environment_identity,
            _ratio(account.retained_energy_increment.fraction + energy_extension.fraction),
            PositiveCount(account.closed_distinction_increment.value + distinction_extension.value),
        )

    return component_exchange_relation(extend(first_phase), extend(second_phase)).orientation == prior.orientation


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-MIXTURE-001",
    "SFT-CHEM-EQ-CHEMICAL-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-INTERFACE-TRANSFER-001",
    "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "accounts",
        "bulk-phase-value-or-answer-only-potential",
        "A bulk value or named answer does not identify the marginal component change.",
        "complete-distinct-phase-component-addition-accounts",
        "Each phase retains the complete account for adding one held component.",
    ),
    dimension(
        "identity",
        "changed-component-or-unheld-environment",
        "Changing the component or environment destroys the exchange comparison.",
        "same-held-component-and-fixed-environment",
        "The same component and finite environment are held across distinct phases.",
    ),
    dimension(
        "exchange",
        "created-erased-or-unpaired-component",
        "An unpaired move violates the admitted component carrier conservation.",
        "paired-one-component-exchange-conserving-total-carrier",
        "One departure and one arrival preserve the complete component carrier.",
    ),
    dimension(
        "support",
        "signed-logarithmic-or-fitted-chemical-potential",
        "A signed scalar, logarithm or fit imports an unforced chemical-potential model.",
        "exact-positive-energy-and-closed-distinction-increments",
        "The marginal account retains exact positive energy and distinction increments.",
    ),
    dimension(
        "relation",
        "weighted-sum-tie-break-or-equal-composition-rule",
        "A weight, tie-break or equal-composition premise adds content not forced by exchange.",
        "strict-product-order-with-EmptyOne-equilibrium",
        "Product order forces direction; exact account equality is equilibrium with EmptyOne separations.",
    ),
    dimension(
        "prediction",
        "compound-condition-or-composition-readable-before-seal",
        "Withheld mixture values could select the component relation.",
        "complete-value-free-74-row-identity-seal",
        "All 74 source-row identities seal before compounds, conditions or compositions open.",
    ),
    dimension(
        "record",
        "selected-mixture-row-or-deleted-endpoint",
        "Selecting a system or dropping a source boundary can hide adverse phase behavior.",
        "complete-four-system-74-row-VLE-vector-with-eight-endpoints",
        "All four systems, 74 matched interiors and eight unmatched endpoints are retained.",
    ),
    dimension(
        "extension",
        "refit-after-common-context-successor",
        "Refitting after a shared context destroys structural invariance.",
        "depth-independent-common-context-successor",
        "Adding the same exact positive context to both phase accounts preserves the relation.",
    ),
)


EXACT_RESULT = (
    "complete-distinct-phase-component-addition-accounts__same-held-component-and-fixed-environment__"
    "paired-one-component-exchange-conserving-total-carrier__exact-positive-energy-and-closed-distinction-increments__"
    "strict-product-order-with-EmptyOne-equilibrium__complete-value-free-74-row-identity-seal__"
    "complete-four-system-74-row-VLE-vector-with-eight-endpoints__depth-independent-common-context-successor"
)


def _account(phase: str, energy: int, distinctions: int) -> ComponentAdditionAccount:
    return ComponentAdditionAccount(
        HeldLabel("chemical-component", "held-component"),
        HeldLabel("chemical-phase", phase),
        HeldLabel("chemical-environment", "held-environment"),
        PositiveRatio.from_pair(energy, 3),
        PositiveCount(distinctions),
    )


def _witnesses():
    liquid = _account("liquid", 5, 2)
    gas = _account("gas", 8, 3)
    equilibrium = component_exchange_relation(_account("liquid", 5, 2), _account("gas", 5, 2))
    directed = component_exchange_relation(liquid, gas)
    incomparable = False
    try:
        component_exchange_relation(_account("liquid", 5, 4), _account("gas", 8, 2))
    except InadmissibleExactValue:
        incomparable = True
    return (
        (
            "component-marginal-order",
            "Lower complete marginal account forces component transfer toward that phase.",
            directed.orientation.label == "toward-first-phase",
        ),
        (
            "equilibrium-EmptyOne",
            "Equal phase-specific component accounts force equilibrium without equal bulk composition.",
            equilibrium.orientation.label == "equilibrium"
            and isinstance(equilibrium.energy_separation, EmptyOne)
            and isinstance(equilibrium.distinction_separation, EmptyOne),
        ),
        (
            "incomparable-halts",
            "Crossed accounts do not receive a fitted scalar trade-off.",
            incomparable,
        ),
        (
            "common-context-successor",
            "A common positive context preserves the exact component relation.",
            common_context_successor_preserves_exchange(
                liquid, gas, PositiveRatio.from_pair(7, 5), PositiveCount(2)
            ),
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "ComponentAdditionAccount",
    "ComponentExchangeResult",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "OPERATIONAL_WITNESSES",
    "common_context_successor_preserves_exchange",
    "component_exchange_relation",
)
