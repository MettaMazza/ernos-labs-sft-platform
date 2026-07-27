"""Fold-native reaction-dynamics scattering and product-state law for KIN-013."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class RetainedIncomingReactionChannel:
    channel_identity: HeldLabel
    reaction_identity: HeldLabel
    ordered_incoming_carriers: tuple[HeldLabel, ...]
    preparation_identity: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.channel_identity, HeldLabel) or self.channel_identity.family != "registered-incoming-reaction-channel":
            raise InadmissibleExactValue("incoming reaction channel must be registered")
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "held-scattering-reaction-identity":
            raise InadmissibleExactValue("reaction identity must remain held")
        if len(self.ordered_incoming_carriers) < 2 or any(
            not isinstance(carrier, HeldLabel) or carrier.family != "held-incoming-channel-carrier"
            for carrier in self.ordered_incoming_carriers
        ):
            raise InadmissibleExactValue("scattering requires finite retained incoming carrier support")
        if len(set(self.ordered_incoming_carriers)) != len(self.ordered_incoming_carriers):
            raise InadmissibleExactValue("incoming channel carriers must remain distinct and ordered")
        if not isinstance(self.preparation_identity, HeldLabel) or self.preparation_identity.family != "held-incoming-preparation":
            raise InadmissibleExactValue("incoming preparation must remain held")


@dataclass(frozen=True)
class RetainedOutgoingProductState:
    source_occurrence: PositiveCount
    channel_identity: HeldLabel
    reaction_identity: HeldLabel
    ordered_product_carriers: tuple[HeldLabel, ...]
    ordered_product_states: tuple[HeldLabel, ...]
    orientation_to_incoming: HeldLabel
    completed_events: PositiveCount
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("product-state occurrence must be exact positive")
        if not isinstance(self.channel_identity, HeldLabel) or self.channel_identity.family != "registered-outgoing-product-channel":
            raise InadmissibleExactValue("outgoing product channel must be registered")
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "held-scattering-reaction-identity":
            raise InadmissibleExactValue("outgoing reaction identity must remain held")
        if len(self.ordered_product_carriers) < 2 or len(self.ordered_product_carriers) != len(self.ordered_product_states):
            raise InadmissibleExactValue("outgoing channel requires a complete joint product-state tuple")
        if any(
            not isinstance(carrier, HeldLabel) or carrier.family != "held-outgoing-product-carrier"
            for carrier in self.ordered_product_carriers
        ) or any(
            not isinstance(state, HeldLabel) or state.family != "held-outgoing-product-state"
            for state in self.ordered_product_states
        ):
            raise InadmissibleExactValue("outgoing product carriers and states must remain held")
        if len(set(self.ordered_product_carriers)) != len(self.ordered_product_carriers):
            raise InadmissibleExactValue("outgoing product carriers must remain distinct and ordered")
        if not isinstance(self.orientation_to_incoming, HeldLabel) or self.orientation_to_incoming.family != "held-incoming-outgoing-orientation":
            raise InadmissibleExactValue("scattering orientation must remain a held relation")
        if not isinstance(self.completed_events, PositiveCount):
            raise InadmissibleExactValue("retained product-state events must be exact positive")
        if not isinstance(self.evidence_status, HeldLabel) or self.evidence_status.family != "held-scattering-evidence-status":
            raise InadmissibleExactValue("product-state evidence status must remain held")


@dataclass(frozen=True)
class CompleteFiniteProductStateSupport:
    incoming_channel: RetainedIncomingReactionChannel
    ordered_outgoing_states: tuple[RetainedOutgoingProductState, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.incoming_channel, RetainedIncomingReactionChannel):
            raise InadmissibleExactValue("scattering support requires one retained incoming channel")
        if not self.ordered_outgoing_states or any(
            not isinstance(state, RetainedOutgoingProductState) for state in self.ordered_outgoing_states
        ):
            raise InadmissibleExactValue("scattering support requires finite positive outgoing support")
        if tuple(state.source_occurrence.value for state in self.ordered_outgoing_states) != tuple(
            range(1, len(self.ordered_outgoing_states) + 1)
        ):
            raise InadmissibleExactValue("outgoing product-state support must be complete and gap-free")
        if any(state.reaction_identity != self.incoming_channel.reaction_identity for state in self.ordered_outgoing_states):
            raise InadmissibleExactValue("incoming and outgoing channels must retain one reaction identity")
        state_words = tuple(
            (state.channel_identity, state.ordered_product_carriers, state.ordered_product_states, state.orientation_to_incoming)
            for state in self.ordered_outgoing_states
        )
        if len(set(state_words)) != len(state_words):
            raise InadmissibleExactValue("complete outgoing support cannot duplicate a joint product-state orientation")


@dataclass(frozen=True)
class ExactProductStateScatteringRecord:
    incoming_channel_identity: HeldLabel
    outgoing_channel_identity: HeldLabel
    ordered_product_carriers: tuple[HeldLabel, ...]
    ordered_product_states: tuple[HeldLabel, ...]
    orientation_to_incoming: HeldLabel
    exact_event_share: Fraction
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.exact_event_share, Fraction) or self.exact_event_share <= 0:
            raise InadmissibleExactValue("product-state scattering share must be exact positive")


def forced_reaction_scattering_product_state_law(
    support: CompleteFiniteProductStateSupport,
) -> tuple[ExactProductStateScatteringRecord, ...]:
    if not isinstance(support, CompleteFiniteProductStateSupport):
        raise InadmissibleExactValue("reaction scattering law requires complete finite channel support")
    total_events = sum(state.completed_events.value for state in support.ordered_outgoing_states)
    return tuple(
        ExactProductStateScatteringRecord(
            support.incoming_channel.channel_identity,
            state.channel_identity,
            state.ordered_product_carriers,
            state.ordered_product_states,
            state.orientation_to_incoming,
            Fraction(state.completed_events.value, total_events),
            state.evidence_status,
        )
        for state in support.ordered_outgoing_states
    )


@dataclass(frozen=True)
class RegisteredScatteringOccurrence:
    source_occurrence: PositiveCount
    support: CompleteFiniteProductStateSupport

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("scattering occurrence must be exact positive")
        forced_reaction_scattering_product_state_law(self.support)


@dataclass(frozen=True)
class CompleteScatteringFamily:
    ordered_occurrences: tuple[RegisteredScatteringOccurrence, ...]

    def __post_init__(self) -> None:
        if not self.ordered_occurrences or any(
            not isinstance(row, RegisteredScatteringOccurrence) for row in self.ordered_occurrences
        ):
            raise InadmissibleExactValue("scattering family requires at least one complete occurrence")
        if tuple(row.source_occurrence.value for row in self.ordered_occurrences) != tuple(
            range(1, len(self.ordered_occurrences) + 1)
        ):
            raise InadmissibleExactValue("scattering occurrences must be complete and gap-free")


def append_scattering_occurrence_preserves_complete_family(
    family: CompleteScatteringFamily,
    successor: RegisteredScatteringOccurrence,
) -> bool:
    if successor.source_occurrence.value != len(family.ordered_occurrences) + 1:
        raise InadmissibleExactValue("scattering successor must be the next positive occurrence")
    prior = tuple(forced_reaction_scattering_product_state_law(row.support) for row in family.ordered_occurrences)
    extended = CompleteScatteringFamily(family.ordered_occurrences + (successor,))
    results = tuple(forced_reaction_scattering_product_state_law(row.support) for row in extended.ordered_occurrences)
    return results[: len(prior)] == prior and len(results) == len(prior) + 1


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ROVIBRONIC-COMPOSITION-001",
    "SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013",
    "SFT-CHEM-MOLECULAR-QUANTUM-MEASUREMENT-REDUCTION-014",
    "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007",
    "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
    "SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011",
    "SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("incoming", "incoming-carriers-erased-or-replaced-by-continuum-beam", "Erased or continuous input cannot retain which finite reaction channel was prepared.", "finite-held-incoming-channel-and-preparation", "Every incoming carrier, reaction and preparation identity remains held."),
    dimension("outgoing", "selected-product-or-continuous-outgoing-distribution", "A selected or continuous outcome erases finite alternative product states.", "complete-finite-distinct-outgoing-product-state-support", "Every retained outgoing product-state channel remains distinct and source ordered."),
    dimension("composition", "coproduct-states-separated-or-marginalized", "Marginal product states erase which coproduct pair occurred together.", "joint-ordered-coproduct-state-word", "Each outgoing event retains the complete ordered joint product-state tuple."),
    dimension("quantity", "imported-cross-section-probability-amplitude-or-fitted-density", "An imported or fitted distribution can select the answer.", "completed-state-events-per-complete-positive-event-support", "Finite positive event counts force exact positive state shares."),
    dimension("orientation", "signed-angle-continuum-or-numerical-zero-direction", "A continuum angle or signed scalar imports forbidden numerical structure.", "held-incoming-outgoing-orientation-relation", "Direction remains a held relation with no negative or zero proof number."),
    dimension("observation", "selected-normalized-or-favorable-product-vector", "Selection or normalization can erase weak, absent, adverse or discrepant channels.", "complete-51-record-36-page-14-worksheet-978591-cell-vector", "The complete source surface and 6,408 key state-resolved cells remain bound."),
    dimension("provenance", "experimental-theoretical-fitted-estimated-and-tentative-records-mixed", "Mixed provenance lets a model or correction masquerade as observation.", "experiment-theory-fit-estimate-tentative-control-and-review-status-separated", "Every measurement, model, correction, limitation and reviewer challenge remains separately classified."),
    dimension("prediction", "product-values-workbook-or-target-readable-before-seal", "Target access can select the channel or orientation law.", "value-free-51-record-identity-seal-and-depth-independent-scattering-successor", "All identities seal before values and occurrence extension preserves prior results."),
)


EXACT_RESULT = (
    "finite-held-incoming-channel-and-preparation__complete-finite-distinct-outgoing-product-state-support__"
    "joint-ordered-coproduct-state-word__completed-state-events-per-complete-positive-event-support__"
    "held-incoming-outgoing-orientation-relation__complete-51-record-36-page-14-worksheet-978591-cell-vector__"
    "experiment-theory-fit-estimate-tentative-control-and-review-status-separated__"
    "value-free-51-record-identity-seal-and-depth-independent-scattering-successor"
)


def _incoming(label: str = "incoming-a") -> RetainedIncomingReactionChannel:
    return RetainedIncomingReactionChannel(
        HeldLabel("registered-incoming-reaction-channel", label),
        HeldLabel("held-scattering-reaction-identity", "reaction-a"),
        tuple(HeldLabel("held-incoming-channel-carrier", carrier) for carrier in ("reactant-a", "reactant-b")),
        HeldLabel("held-incoming-preparation", "preparation-a"),
    )


def _outgoing(occurrence: int, orientation: str, events: int) -> RetainedOutgoingProductState:
    return RetainedOutgoingProductState(
        PositiveCount(occurrence),
        HeldLabel("registered-outgoing-product-channel", f"outgoing-{occurrence}"),
        HeldLabel("held-scattering-reaction-identity", "reaction-a"),
        tuple(HeldLabel("held-outgoing-product-carrier", carrier) for carrier in ("product-a", "product-b")),
        tuple(HeldLabel("held-outgoing-product-state", state) for state in (f"state-a-{occurrence}", f"state-b-{occurrence}")),
        HeldLabel("held-incoming-outgoing-orientation", orientation),
        PositiveCount(events),
        HeldLabel("held-scattering-evidence-status", "retained"),
    )


_BASE_SUPPORT = CompleteFiniteProductStateSupport(
    _incoming(),
    (_outgoing(1, "same-oriented", 3), _outgoing(2, "transverse-oriented", 2), _outgoing(3, "opposed-oriented", 1)),
)
_BASE_RESULT = forced_reaction_scattering_product_state_law(_BASE_SUPPORT)
_BASE_FAMILY = CompleteScatteringFamily((RegisteredScatteringOccurrence(PositiveCount(1), _BASE_SUPPORT),))
OPERATIONAL_WITNESSES = (
    ("finite-channel-support", "One finite incoming channel retains every distinct outgoing joint product-state word.", len(_BASE_RESULT) == 3 and len({row.ordered_product_states for row in _BASE_RESULT}) == 3),
    ("exact-state-shares", "Positive event counts force exact positive product-state shares.", tuple(row.exact_event_share for row in _BASE_RESULT) == (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))),
    ("held-orientation", "Incoming/outgoing direction remains held without an angle continuum or signed proof scalar.", tuple(row.orientation_to_incoming.label for row in _BASE_RESULT) == ("same-oriented", "transverse-oriented", "opposed-oriented")),
    ("successor", "Appending the next complete scattering occurrence preserves every prior result.", append_scattering_occurrence_preserves_complete_family(_BASE_FAMILY, RegisteredScatteringOccurrence(PositiveCount(2), _BASE_SUPPORT))),
)


__all__ = (
    "CompleteFiniteProductStateSupport",
    "CompleteScatteringFamily",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactProductStateScatteringRecord",
    "OPERATIONAL_WITNESSES",
    "RegisteredScatteringOccurrence",
    "RetainedIncomingReactionChannel",
    "RetainedOutgoingProductState",
    "append_scattering_occurrence_preserves_complete_family",
    "forced_reaction_scattering_product_state_law",
)
