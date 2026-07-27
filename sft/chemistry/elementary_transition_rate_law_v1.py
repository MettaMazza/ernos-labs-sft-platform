"""Fold-native exact elementary-transition rate law for KIN-001."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ElementaryTransitionAccount:
    reaction_identity: HeldLabel
    initial_state: HeldLabel
    terminal_state: HeldLabel
    completed_transitions: PositiveCount
    reference_ticks: PositiveCount
    observation_support: PositiveCount
    conditions: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-elementary-reaction":
            raise InadmissibleExactValue("elementary rate requires one registered reaction identity")
        if (
            not isinstance(self.initial_state, HeldLabel) or self.initial_state.family != "molecular-state"
            or not isinstance(self.terminal_state, HeldLabel) or self.terminal_state.family != "molecular-state"
            or self.initial_state == self.terminal_state
        ):
            raise InadmissibleExactValue("elementary rate requires distinct retained molecular endpoints")
        if any(not isinstance(row, PositiveCount) for row in (self.completed_transitions, self.reference_ticks, self.observation_support)):
            raise InadmissibleExactValue("elementary rate requires positive exact transition, tick and boundary counts")
        if not self.conditions or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.conditions):
            raise InadmissibleExactValue("elementary rate requires a complete exact condition carrier")


@dataclass(frozen=True)
class ExactElementaryTransitionRate:
    carrier: HeldLabel
    orientation: HeldLabel
    event_response: PositiveRatio


def forced_elementary_transition_rate(account: ElementaryTransitionAccount) -> ExactElementaryTransitionRate:
    if not isinstance(account, ElementaryTransitionAccount):
        raise InadmissibleExactValue("elementary rate requires a complete transition account")
    return ExactElementaryTransitionRate(
        HeldLabel("elementary-rate-carrier", account.reaction_identity.label),
        HeldLabel("transition-orientation", f"{account.initial_state.label}-to-{account.terminal_state.label}"),
        PositiveRatio.from_pair(
            account.completed_transitions.value,
            account.reference_ticks.value * account.observation_support.value,
        ),
    )


def external_rate_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("external elementary rate requires exact positive support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("external elementary rate is not exact positive finite support") from exc


def common_event_resource_replication_preserves_rate(account: ElementaryTransitionAccount, replication: PositiveCount) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("rate replication requires exact positive support")
    prior = forced_elementary_transition_rate(account)
    replicated = ElementaryTransitionAccount(
        account.reaction_identity, account.initial_state, account.terminal_state,
        PositiveCount(account.completed_transitions.value * replication.value),
        PositiveCount(account.reference_ticks.value * replication.value),
        account.observation_support, account.conditions,
    )
    successor = forced_elementary_transition_rate(replicated)
    return (
        successor.carrier == prior.carrier
        and successor.orientation == prior.orientation
        and successor.event_response.fraction == prior.event_response.fraction
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001", "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009", "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007", "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-KIN-RATE-001",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001", "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-rate-number-or-continuum-field", "A detached rate erases the transition that is counted.", "complete-registered-elementary-transition-carrier", "One registered elementary reaction and both molecular endpoints remain held."),
    dimension("state", "endpoint-erased-or-identity-change", "Without distinct retained endpoints no completed transition is identifiable.", "distinct-held-initial-and-terminal-molecular-states", "Initial and terminal molecular states are exact and distinct."),
    dimension("event", "continuous-change-primitive-or-uncounted-event", "An uncounted continuum change is not an exact rate resource.", "positive-completed-transition-count", "Every completed instance is counted as positive exact support."),
    dimension("recurrence", "clock-free-or-continuum-time-derivative", "A rate cannot be formed without exact recurrence support.", "positive-reference-tick-count", "Time is a positive counted recurrence, not a continuum derivative."),
    dimension("boundary", "condition-or-observation-support-erased", "Erased conditions or support make rate rows incomparable.", "complete-condition-and-positive-observation-support", "Conditions, observation support and source identity remain held."),
    dimension("magnitude", "imported-mass-action-order-arrhenius-fit-or-logarithm", "A conventional or fitted rate law could select the result.", "exact-transition-count-per-tick-and-observation-support", "The only native magnitude is the exact counted-event quotient."),
    dimension("prediction", "reaction-condition-method-or-value-readable-before-seal", "Readable target content could select the law.", "complete-value-free-46-record-identity-seal", "All four source identities and 46 row identities seal before target content opens."),
    dimension("extension", "refit-after-event-resource-replication-or-record-append", "Refitting destroys exact provenance.", "depth-independent-common-event-tick-replication-and-record-append", "Common event/tick replication and complete record append preserve the rate relation."),
)


EXACT_RESULT = (
    "complete-registered-elementary-transition-carrier__distinct-held-initial-and-terminal-molecular-states__"
    "positive-completed-transition-count__positive-reference-tick-count__complete-condition-and-positive-observation-support__"
    "exact-transition-count-per-tick-and-observation-support__complete-value-free-46-record-identity-seal__"
    "depth-independent-common-event-tick-replication-and-record-append"
)


def _account(reverse: bool = False) -> ElementaryTransitionAccount:
    return ElementaryTransitionAccount(
        HeldLabel("registered-elementary-reaction", "reaction-one"),
        HeldLabel("molecular-state", "products" if reverse else "reactants"),
        HeldLabel("molecular-state", "reactants" if reverse else "products"),
        PositiveCount(6), PositiveCount(4), PositiveCount(3),
        (PositiveRatio.from_pair(638, 1), EmptyOne()),
    )


OPERATIONAL_WITNESSES = (
    ("exact-counted-response", "Six completed transitions over four ticks and support three form one half exactly.", forced_elementary_transition_rate(_account()).event_response.fraction == Fraction(1, 2)),
    ("held-opposed-orientation", "Opposed directions are held labels rather than signed values.", forced_elementary_transition_rate(_account()).orientation != forced_elementary_transition_rate(_account(True)).orientation),
    ("structural-absence", "An absent condition is structural EmptyOne.", isinstance(_account().conditions[1], EmptyOne)),
    ("replication-successor", "Common event/tick replication preserves the exact rate.", common_event_resource_replication_preserves_rate(_account(), PositiveCount(7))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "ElementaryTransitionAccount",
    "ExactElementaryTransitionRate", "common_event_resource_replication_preserves_rate", "external_rate_magnitude",
    "forced_elementary_transition_rate",
)
