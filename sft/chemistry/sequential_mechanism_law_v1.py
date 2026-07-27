"""Fold-native exact sequential-mechanism composition law for Chemistry KIN-007."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class RetainedMechanismState:
    state_identity: HeldLabel
    occurrence: PositiveCount
    condition_identity: HeldLabel
    observation_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.state_identity, HeldLabel) or self.state_identity.family != "registered-mechanism-state":
            raise InadmissibleExactValue("sequential mechanism requires a registered state identity")
        if not isinstance(self.occurrence, PositiveCount):
            raise InadmissibleExactValue("sequential mechanism requires a positive state occurrence")
        if not isinstance(self.condition_identity, HeldLabel) or self.condition_identity.family != "held-state-condition":
            raise InadmissibleExactValue("sequential mechanism requires every state condition to remain held")
        if not isinstance(self.observation_status, HeldLabel) or self.observation_status.family != "held-observation-status":
            raise InadmissibleExactValue("sequential mechanism requires measured, adverse or unresolved status")


@dataclass(frozen=True)
class RetainedElementaryTransition:
    transition_identity: HeldLabel
    occurrence: PositiveCount
    entry_state_identity: HeldLabel
    exit_state_identity: HeldLabel
    condition_boundary: HeldLabel
    transition_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.transition_identity, HeldLabel) or self.transition_identity.family != "registered-elementary-transition":
            raise InadmissibleExactValue("sequential mechanism requires a registered transition identity")
        if not isinstance(self.occurrence, PositiveCount):
            raise InadmissibleExactValue("sequential mechanism requires a positive transition occurrence")
        if (
            not isinstance(self.entry_state_identity, HeldLabel)
            or self.entry_state_identity.family != "registered-mechanism-state"
            or not isinstance(self.exit_state_identity, HeldLabel)
            or self.exit_state_identity.family != "registered-mechanism-state"
        ):
            raise InadmissibleExactValue("transition boundaries require registered state identities")
        if self.entry_state_identity == self.exit_state_identity:
            raise InadmissibleExactValue("an elementary transition must retain a state distinction")
        if not isinstance(self.condition_boundary, HeldLabel) or self.condition_boundary.family != "held-transition-condition":
            raise InadmissibleExactValue("transition condition boundary must remain held")
        if not isinstance(self.transition_status, HeldLabel) or self.transition_status.family != "held-transition-status":
            raise InadmissibleExactValue("transition status must remain held")


@dataclass(frozen=True)
class CompleteSequentialMechanism:
    reaction_identity: HeldLabel
    ordered_states: tuple[RetainedMechanismState, ...]
    ordered_transitions: tuple[RetainedElementaryTransition, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("sequential mechanism requires a registered reaction")
        if len(self.ordered_states) < 2 or any(not isinstance(row, RetainedMechanismState) for row in self.ordered_states):
            raise InadmissibleExactValue("sequential mechanism requires at least two retained states")
        if len(self.ordered_transitions) != len(self.ordered_states) - 1:
            raise InadmissibleExactValue("every adjacent retained state requires one elementary transition")
        if any(not isinstance(row, RetainedElementaryTransition) for row in self.ordered_transitions):
            raise InadmissibleExactValue("sequential mechanism transition word changed")
        if tuple(row.occurrence.value for row in self.ordered_states) != tuple(range(1, len(self.ordered_states) + 1)):
            raise InadmissibleExactValue("state occurrence word must be complete and gap-free")
        if tuple(row.occurrence.value for row in self.ordered_transitions) != tuple(range(1, len(self.ordered_transitions) + 1)):
            raise InadmissibleExactValue("transition occurrence word must be complete and gap-free")
        for state_in, edge, state_out in zip(self.ordered_states, self.ordered_transitions, self.ordered_states[1:]):
            if edge.entry_state_identity != state_in.state_identity or edge.exit_state_identity != state_out.state_identity:
                raise InadmissibleExactValue("elementary transition does not meet its retained adjacent state boundaries")


@dataclass(frozen=True)
class ExactSequentialComposition:
    reaction_identity: HeldLabel
    initial_state: RetainedMechanismState
    terminal_state: RetainedMechanismState
    ordered_states: tuple[RetainedMechanismState, ...]
    ordered_transitions: tuple[RetainedElementaryTransition, ...]
    intermediate_states: tuple[RetainedMechanismState, ...]
    transition_count: PositiveCount
    intermediate_count: PositiveCount | EmptyOne
    composition_identity: HeldLabel


def forced_sequential_mechanism_composition(mechanism: CompleteSequentialMechanism) -> ExactSequentialComposition:
    if not isinstance(mechanism, CompleteSequentialMechanism):
        raise InadmissibleExactValue("sequential composition requires one complete mechanism word")
    intermediate_states = mechanism.ordered_states[1:-1]
    intermediate_count: PositiveCount | EmptyOne = (
        PositiveCount(len(intermediate_states)) if intermediate_states else EmptyOne()
    )
    return ExactSequentialComposition(
        reaction_identity=mechanism.reaction_identity,
        initial_state=mechanism.ordered_states[0],
        terminal_state=mechanism.ordered_states[-1],
        ordered_states=mechanism.ordered_states,
        ordered_transitions=mechanism.ordered_transitions,
        intermediate_states=intermediate_states,
        transition_count=PositiveCount(len(mechanism.ordered_transitions)),
        intermediate_count=intermediate_count,
        composition_identity=HeldLabel(
            "exact-sequential-composition",
            "every-state-edge-condition-status-and-shared-boundary-retained-once",
        ),
    )


def append_elementary_successor_preserves_complete_prefix(
    mechanism: CompleteSequentialMechanism,
    successor_state: RetainedMechanismState,
    successor_transition: RetainedElementaryTransition,
) -> bool:
    if successor_state.occurrence.value != len(mechanism.ordered_states) + 1:
        raise InadmissibleExactValue("successor state must be the next retained occurrence")
    if successor_transition.occurrence.value != len(mechanism.ordered_transitions) + 1:
        raise InadmissibleExactValue("successor transition must be the next retained occurrence")
    if (
        successor_transition.entry_state_identity != mechanism.ordered_states[-1].state_identity
        or successor_transition.exit_state_identity != successor_state.state_identity
    ):
        raise InadmissibleExactValue("successor transition does not meet the prior terminal state")
    prior = forced_sequential_mechanism_composition(mechanism)
    extended = CompleteSequentialMechanism(
        mechanism.reaction_identity,
        mechanism.ordered_states + (successor_state,),
        mechanism.ordered_transitions + (successor_transition,),
    )
    result = forced_sequential_mechanism_composition(extended)
    return (
        result.ordered_states[: len(prior.ordered_states)] == prior.ordered_states
        and result.ordered_transitions[: len(prior.ordered_transitions)] == prior.ordered_transitions
        and result.intermediate_states[: len(prior.intermediate_states)] == prior.intermediate_states
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-INFO-MUTUAL-CONDITIONAL-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-INTERMEDIATE-001",
    "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-CAT-PATHWAY-001", "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-STATE-ENERGY-ORDER-004", "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002", "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003",
    "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004", "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005",
    "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "endpoint-only-or-selected-snapshot-support", "Endpoints erase the mechanism path.", "complete-source-ordered-state-and-transition-support", "Every state and transition occurrence remains retained."),
    dimension("adjacency", "aggregate-start-to-finish-jump", "An aggregate jump does not prove its elementary boundaries.", "exact-entry-exit-boundary-matching-for-every-edge", "Every edge begins and ends at its registered adjacent states."),
    dimension("intermediate", "implicit-eliminated-or-fitted-intermediate", "An omitted intermediate cannot be reconstructed.", "every-intermediate-occurrence-retained-explicitly", "Every intermediate occurrence remains in the exact state word."),
    dimension("composition", "imported-differential-exponential-or-lifetime-law", "An imported evolution equation can select the answer.", "finite-exact-ordered-edge-composition", "Composition follows only the complete discrete edge word."),
    dimension("condition", "condition-time-or-dose-collapsed", "Collapsed conditions can join incompatible observations.", "held-state-and-transition-condition-boundaries", "Every state and edge preserves its condition identity."),
    dimension("status", "adverse-unresolved-or-parallel-record-omitted", "Removing an unfavorable record overstates the path.", "favorable-adverse-unresolved-and-parallel-status-retained", "Measured, adverse, unresolved and parallel records all remain held."),
    dimension("provenance", "structure-answer-without-source-custody", "An answer-only path cannot be independently audited.", "complete-article-supplement-PDB-raw-custody-and-control-record", "All source, coordinate, custody and control evidence remains bound."),
    dimension("prediction", "time-coordinate-occupancy-or-target-readable-before-seal", "Target access can select the sequence.", "value-free-seventeen-record-identity-seal-and-depth-independent-successor", "Seventeen identities seal first and every appended edge retains the complete prefix."),
)


EXACT_RESULT = (
    "complete-source-ordered-state-and-transition-support__"
    "exact-entry-exit-boundary-matching-for-every-edge__"
    "every-intermediate-occurrence-retained-explicitly__"
    "finite-exact-ordered-edge-composition__"
    "held-state-and-transition-condition-boundaries__"
    "favorable-adverse-unresolved-and-parallel-status-retained__"
    "complete-article-supplement-PDB-raw-custody-and-control-record__"
    "value-free-seventeen-record-identity-seal-and-depth-independent-successor"
)


def _state(label: str, occurrence: int) -> RetainedMechanismState:
    return RetainedMechanismState(
        HeldLabel("registered-mechanism-state", label), PositiveCount(occurrence),
        HeldLabel("held-state-condition", f"condition-{occurrence}"),
        HeldLabel("held-observation-status", "retained"),
    )


def _transition(label: str, occurrence: int, entry: str, exit: str) -> RetainedElementaryTransition:
    return RetainedElementaryTransition(
        HeldLabel("registered-elementary-transition", label), PositiveCount(occurrence),
        HeldLabel("registered-mechanism-state", entry), HeldLabel("registered-mechanism-state", exit),
        HeldLabel("held-transition-condition", f"boundary-{occurrence}"),
        HeldLabel("held-transition-status", "retained"),
    )


def _three_state_mechanism() -> CompleteSequentialMechanism:
    return CompleteSequentialMechanism(
        HeldLabel("registered-reaction", "reaction-a"),
        (_state("state-a", 1), _state("state-b", 2), _state("state-c", 3)),
        (_transition("edge-ab", 1, "state-a", "state-b"), _transition("edge-bc", 2, "state-b", "state-c")),
    )


_BASE = _three_state_mechanism()
_BASE_RESULT = forced_sequential_mechanism_composition(_BASE)
OPERATIONAL_WITNESSES = (
    ("complete-word", "All states and elementary transitions remain in exact source order.", len(_BASE_RESULT.ordered_states) == 3 and len(_BASE_RESULT.ordered_transitions) == 2),
    ("shared-boundary", "The first exit is exactly the second entry.", _BASE_RESULT.ordered_transitions[0].exit_state_identity == _BASE_RESULT.ordered_transitions[1].entry_state_identity),
    ("intermediate", "The internal state is retained exactly once as an intermediate occurrence.", _BASE_RESULT.intermediate_states == (_BASE.ordered_states[1],)),
    ("successor", "Appending one elementary successor retains every earlier state, edge and intermediate.", append_elementary_successor_preserves_complete_prefix(_BASE, _state("state-d", 4), _transition("edge-cd", 3, "state-c", "state-d"))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "CompleteSequentialMechanism",
    "ExactSequentialComposition", "RetainedElementaryTransition", "RetainedMechanismState",
    "append_elementary_successor_preserves_complete_prefix", "forced_sequential_mechanism_composition",
)
