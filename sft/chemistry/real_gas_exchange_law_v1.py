"""Fold-native fugacity-equivalent gas-mixture law for THERMO-010."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class GasCompositionCoordinate:
    component_identity: HeldLabel
    coordinate: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.component_identity, HeldLabel) or self.component_identity.family != "chemical-component":
            raise InadmissibleExactValue("gas coordinate lost its component identity")
        if not isinstance(self.coordinate, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("gas coordinate must be an exact positive part or structural absence")
        if isinstance(self.coordinate, PositiveRatio) and self.coordinate.fraction > 1:
            raise InadmissibleExactValue("gas composition coordinate exceeds the One")


@dataclass(frozen=True)
class GasComponentExchangeAccount:
    component_identity: HeldLabel
    gas_phase_identity: HeldLabel
    environment_identity: HeldLabel
    composition: tuple[GasCompositionCoordinate, ...]
    accessible_exchange_support: PositiveCount
    reference_exchange_support: PositiveCount
    independently_composed_support: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.component_identity, "chemical-component"),
            (self.gas_phase_identity, "chemical-phase"),
            (self.environment_identity, "chemical-environment"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("gas exchange account lost a held identity")
        if not self.composition or any(not isinstance(row, GasCompositionCoordinate) for row in self.composition):
            raise InadmissibleExactValue("gas exchange account requires the complete composition")
        identities = tuple(row.component_identity for row in self.composition)
        if len(set(identities)) != len(identities):
            raise InadmissibleExactValue("gas composition duplicated a component")
        counts = (
            self.accessible_exchange_support,
            self.reference_exchange_support,
            self.independently_composed_support,
        )
        if any(not isinstance(value, PositiveCount) for value in counts):
            raise InadmissibleExactValue("gas exchange support must be exact positive counts")
        if self.accessible_exchange_support.value > self.reference_exchange_support.value:
            raise InadmissibleExactValue("accessible gas support exceeds its complete reference support")


@dataclass(frozen=True)
class GasInteractionResult:
    relation: HeldLabel
    support_separation: PositiveCount | EmptyOne


@dataclass(frozen=True)
class PhaseExchangeResult:
    relation: HeldLabel
    support_separation: PositiveCount | EmptyOne


def exact_fugacity_equivalent(account: GasComponentExchangeAccount) -> PositiveRatio:
    """Return the exact accessible/reference exchange-support relation."""

    if not isinstance(account, GasComponentExchangeAccount):
        raise InadmissibleExactValue("fugacity-equivalent relation requires a complete gas exchange account")
    return PositiveRatio.from_pair(
        account.accessible_exchange_support.value,
        account.reference_exchange_support.value,
    )


def real_gas_interaction_relation(account: GasComponentExchangeAccount) -> GasInteractionResult:
    """Compare joint accessible support with independently composed support."""

    if not isinstance(account, GasComponentExchangeAccount):
        raise InadmissibleExactValue("real-gas relation requires a complete gas exchange account")
    actual = account.accessible_exchange_support.value
    independent = account.independently_composed_support.value
    if actual == independent:
        return GasInteractionResult(HeldLabel("gas-mixture", "independent-support"), EmptyOne())
    if actual < independent:
        return GasInteractionResult(
            HeldLabel("gas-mixture", "interaction-restricted-support"),
            PositiveCount(independent - actual),
        )
    return GasInteractionResult(
        HeldLabel("gas-mixture", "interaction-expanded-support"),
        PositiveCount(actual - independent),
    )


def phase_exchange_relation(
    gas_account: GasComponentExchangeAccount,
    partner_phase_exchange_support: PositiveCount,
) -> PhaseExchangeResult:
    """Resolve equilibrium from exact component-exchange support equality."""

    if not isinstance(gas_account, GasComponentExchangeAccount) or not isinstance(
        partner_phase_exchange_support, PositiveCount
    ):
        raise InadmissibleExactValue("phase exchange requires complete gas and partner support")
    gas = gas_account.accessible_exchange_support.value
    partner = partner_phase_exchange_support.value
    if gas == partner:
        return PhaseExchangeResult(HeldLabel("phase-exchange", "balanced"), EmptyOne())
    if gas < partner:
        return PhaseExchangeResult(
            HeldLabel("phase-exchange", "partner-expanded"), PositiveCount(partner - gas)
        )
    return PhaseExchangeResult(
        HeldLabel("phase-exchange", "gas-expanded"), PositiveCount(gas - partner)
    )


def replicated_support_preserves_gas_law(
    account: GasComponentExchangeAccount,
    partner_phase_exchange_support: PositiveCount,
    replication: PositiveCount,
) -> bool:
    """Prove the common exact-support successor preserves every relation."""

    if not isinstance(replication, PositiveCount) or not isinstance(partner_phase_exchange_support, PositiveCount):
        raise InadmissibleExactValue("gas-law successor requires exact positive counts")
    prior_ratio = exact_fugacity_equivalent(account).fraction
    prior_interaction = real_gas_interaction_relation(account).relation
    prior_phase = phase_exchange_relation(account, partner_phase_exchange_support).relation
    factor = replication.value
    replicated = GasComponentExchangeAccount(
        account.component_identity,
        account.gas_phase_identity,
        account.environment_identity,
        account.composition,
        PositiveCount(account.accessible_exchange_support.value * factor),
        PositiveCount(account.reference_exchange_support.value * factor),
        PositiveCount(account.independently_composed_support.value * factor),
    )
    return (
        exact_fugacity_equivalent(replicated).fraction == prior_ratio
        and real_gas_interaction_relation(replicated).relation == prior_interaction
        and phase_exchange_relation(
            replicated, PositiveCount(partner_phase_exchange_support.value * factor)
        ).relation
        == prior_phase
    )


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
    "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "unbound-fugacity-number",
        "An unbound scalar erases the component exchange support and gas state it names.",
        "complete-gas-component-exchange-account",
        "The carrier retains component, phase, environment, composition and every support count.",
    ),
    dimension(
        "state",
        "erased-pressure-temperature-or-composition",
        "Erasing a held coordinate merges distinguishable real-gas states.",
        "complete-held-pressure-temperature-composition-state",
        "Every finite pressure, temperature and composition record remains held.",
    ),
    dimension(
        "component",
        "bulk-mixture-answer-without-component-identity",
        "A bulk answer cannot preserve which component exchanges across the phase boundary.",
        "held-component-resolved-exchange-support",
        "Each relation is attached to one held component and complete mixture support.",
    ),
    dimension(
        "relation",
        "imported-fugacity-eos-or-fitted-correction",
        "An imported equation or fitted correction lets an external model select the answer.",
        "exact-accessible-over-reference-support-relation",
        "The fugacity-equivalent relation is the exact accessible/reference support fraction.",
    ),
    dimension(
        "equilibrium",
        "assumed-ideal-gas-or-target-derived-balance",
        "Assumed ideality or target-derived adjustment does not force phase exchange.",
        "exact-component-exchange-support-balance",
        "Phase equilibrium is exact equality of the component exchange-support accounts.",
    ),
    dimension(
        "prediction",
        "real-gas-values-readable-before-seal",
        "Readable values could select or tune the generated law.",
        "complete-value-free-94-state-identity-seal",
        "All 94 equilibrium identities seal before compounds, conditions, pressures or compositions open.",
    ),
    dimension(
        "record",
        "selected-mixture-or-deleted-pressure-only-state",
        "Selection would hide the complete favorable, adverse and incomplete-measurement surface.",
        "complete-21-dataset-176-point-94-state-record",
        "All raw datasets and points, 94 equilibrium states, 59 paired and 35 pressure-only states remain.",
    ),
    dimension(
        "extension",
        "refit-after-exact-support-replication",
        "Refitting after replication destroys the exact support relation.",
        "depth-independent-common-support-replication",
        "Common exact replication preserves fugacity-equivalent, interaction and phase-balance relations.",
    ),
)


EXACT_RESULT = (
    "complete-gas-component-exchange-account__complete-held-pressure-temperature-composition-state__"
    "held-component-resolved-exchange-support__exact-accessible-over-reference-support-relation__"
    "exact-component-exchange-support-balance__complete-value-free-94-state-identity-seal__"
    "complete-21-dataset-176-point-94-state-record__depth-independent-common-support-replication"
)


def _account(accessible: int, reference: int, independent: int) -> GasComponentExchangeAccount:
    return GasComponentExchangeAccount(
        HeldLabel("chemical-component", "component-a"),
        HeldLabel("chemical-phase", "gas-mixture"),
        HeldLabel("chemical-environment", "held-temperature-pressure"),
        (
            GasCompositionCoordinate(HeldLabel("chemical-component", "component-a"), PositiveRatio.from_pair(3, 5)),
            GasCompositionCoordinate(HeldLabel("chemical-component", "component-b"), PositiveRatio.from_pair(2, 5)),
        ),
        PositiveCount(accessible),
        PositiveCount(reference),
        PositiveCount(independent),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    account = _account(6, 10, 8)
    return (
        (
            "exact-fugacity-equivalent",
            "Accessible gas exchange support over reference support is an exact positive fraction.",
            exact_fugacity_equivalent(account).fraction == PositiveRatio.from_pair(3, 5).fraction,
        ),
        (
            "real-gas-interaction",
            "Joint and independently composed support are compared without an equation of state.",
            real_gas_interaction_relation(account).relation.label == "interaction-restricted-support",
        ),
        (
            "phase-exchange-balance",
            "Equal component exchange supports produce structural balance with EmptyOne separation.",
            phase_exchange_relation(account, PositiveCount(6)).relation.label == "balanced"
            and isinstance(phase_exchange_relation(account, PositiveCount(6)).support_separation, EmptyOne),
        ),
        (
            "replication-successor",
            "Common exact support replication preserves every gas-mixture relation.",
            replicated_support_preserves_gas_law(account, PositiveCount(6), PositiveCount(7)),
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "GasComponentExchangeAccount",
    "GasCompositionCoordinate",
    "GasInteractionResult",
    "OPERATIONAL_WITNESSES",
    "PhaseExchangeResult",
    "exact_fugacity_equivalent",
    "phase_exchange_relation",
    "real_gas_interaction_relation",
    "replicated_support_preserves_gas_law",
)
