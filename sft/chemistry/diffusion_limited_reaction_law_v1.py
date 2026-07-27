"""Fold-native diffusion-limited reaction boundary for Chemistry KIN-011."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True, order=True)
class ExactPositiveCompletionRatio:
    value: Fraction

    @classmethod
    def from_counts(cls, completed_reactions: PositiveCount, observation_parts: PositiveCount) -> "ExactPositiveCompletionRatio":
        if not isinstance(completed_reactions, PositiveCount) or not isinstance(observation_parts, PositiveCount):
            raise InadmissibleExactValue("diffusion-limited completion relation requires exact positive counts")
        return cls(Fraction(completed_reactions.value, observation_parts.value))

    def __post_init__(self) -> None:
        if not isinstance(self.value, Fraction) or self.value <= 0:
            raise InadmissibleExactValue("completion relation must be exact and positive")


@dataclass(frozen=True)
class RetainedTransportState:
    state_identity: HeldLabel
    transported_identity: HeldLabel
    path_position: PositiveCount
    state_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.state_identity, HeldLabel) or self.state_identity.family != "registered-transport-reaction-state":
            raise InadmissibleExactValue("transport state identity must remain registered")
        if not isinstance(self.transported_identity, HeldLabel) or self.transported_identity.family != "held-transported-reactant":
            raise InadmissibleExactValue("transported reactant identity must remain held")
        if not isinstance(self.path_position, PositiveCount):
            raise InadmissibleExactValue("transport path position must be positive")
        if not isinstance(self.state_status, HeldLabel) or self.state_status.family != "held-transport-state-status":
            raise InadmissibleExactValue("transport state status must remain held")


@dataclass(frozen=True)
class RetainedTransportTransition:
    transition_identity: HeldLabel
    entry_state: HeldLabel
    exit_state: HeldLabel
    condition_boundary: HeldLabel
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.transition_identity, HeldLabel) or self.transition_identity.family != "registered-transport-transition":
            raise InadmissibleExactValue("transport transition identity must remain registered")
        if (
            not isinstance(self.entry_state, HeldLabel) or self.entry_state.family != "registered-transport-reaction-state"
            or not isinstance(self.exit_state, HeldLabel) or self.exit_state.family != "registered-transport-reaction-state"
            or self.entry_state == self.exit_state
        ):
            raise InadmissibleExactValue("transport transition requires distinct registered states")
        if not isinstance(self.condition_boundary, HeldLabel) or self.condition_boundary.family != "held-transport-reaction-condition":
            raise InadmissibleExactValue("transport condition boundary must remain held")
        if not isinstance(self.evidence_status, HeldLabel) or self.evidence_status.family != "held-transport-transition-status":
            raise InadmissibleExactValue("transport evidence status must remain held")


@dataclass(frozen=True)
class CompleteFiniteTransportPath:
    path_identity: HeldLabel
    ordered_states: tuple[RetainedTransportState, ...]
    ordered_transitions: tuple[RetainedTransportTransition, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.path_identity, HeldLabel) or self.path_identity.family != "registered-finite-transport-path":
            raise InadmissibleExactValue("finite transport path identity must remain registered")
        if len(self.ordered_states) < 2 or len(self.ordered_transitions) != len(self.ordered_states) - 1:
            raise InadmissibleExactValue("finite transport path requires every state and adjacent transition")
        if any(not isinstance(state, RetainedTransportState) for state in self.ordered_states):
            raise InadmissibleExactValue("transport path contains an unregistered state")
        if any(not isinstance(edge, RetainedTransportTransition) for edge in self.ordered_transitions):
            raise InadmissibleExactValue("transport path contains an unregistered transition")
        if tuple(state.path_position.value for state in self.ordered_states) != tuple(range(1, len(self.ordered_states) + 1)):
            raise InadmissibleExactValue("transport path positions must be complete and gap-free")
        transported = self.ordered_states[0].transported_identity
        if any(state.transported_identity != transported for state in self.ordered_states):
            raise InadmissibleExactValue("the same reactant identity must be retained through transport")
        condition = self.ordered_transitions[0].condition_boundary
        for position, transition in enumerate(self.ordered_transitions):
            if (
                transition.entry_state != self.ordered_states[position].state_identity
                or transition.exit_state != self.ordered_states[position + 1].state_identity
            ):
                raise InadmissibleExactValue("each transport transition must join its adjacent retained states")
            if transition.condition_boundary != condition:
                raise InadmissibleExactValue("one transport path requires one exact held condition boundary")

    @property
    def exit_state(self) -> HeldLabel:
        return self.ordered_states[-1].state_identity


@dataclass(frozen=True)
class RetainedReactionOccurrence:
    reaction_identity: HeldLabel
    encounter_entry_state: HeldLabel
    product_state: HeldLabel
    condition_boundary: HeldLabel
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction-occurrence":
            raise InadmissibleExactValue("reaction occurrence must remain registered")
        if (
            not isinstance(self.encounter_entry_state, HeldLabel) or self.encounter_entry_state.family != "registered-transport-reaction-state"
            or not isinstance(self.product_state, HeldLabel) or self.product_state.family != "registered-transport-reaction-state"
            or self.encounter_entry_state == self.product_state
        ):
            raise InadmissibleExactValue("reaction occurrence requires distinct encounter and product states")
        if not isinstance(self.condition_boundary, HeldLabel) or self.condition_boundary.family != "held-transport-reaction-condition":
            raise InadmissibleExactValue("reaction condition boundary must remain held")
        if not isinstance(self.evidence_status, HeldLabel) or self.evidence_status.family != "held-reaction-status":
            raise InadmissibleExactValue("reaction evidence status must remain held")


@dataclass(frozen=True)
class ExactDiffusionLimitedReactionBoundary:
    transport_path_identity: HeldLabel
    transported_identity: HeldLabel
    complete_transport_word: tuple[RetainedTransportTransition, ...]
    encounter_state: HeldLabel
    reaction_occurrence: RetainedReactionOccurrence
    completed_reaction_count: PositiveCount
    boundary_identity: HeldLabel


def forced_diffusion_limited_reaction_boundary(
    transport_path: CompleteFiniteTransportPath,
    reaction: RetainedReactionOccurrence,
) -> ExactDiffusionLimitedReactionBoundary:
    if not isinstance(transport_path, CompleteFiniteTransportPath) or not isinstance(reaction, RetainedReactionOccurrence):
        raise InadmissibleExactValue("diffusion-limited boundary requires complete transport and reaction objects")
    if transport_path.exit_state != reaction.encounter_entry_state:
        raise InadmissibleExactValue("transport exit must be the exact reaction encounter entry")
    if transport_path.ordered_transitions[-1].condition_boundary != reaction.condition_boundary:
        raise InadmissibleExactValue("transport and reaction must share the exact held condition boundary")
    return ExactDiffusionLimitedReactionBoundary(
        transport_path_identity=transport_path.path_identity,
        transported_identity=transport_path.ordered_states[0].transported_identity,
        complete_transport_word=transport_path.ordered_transitions,
        encounter_state=transport_path.exit_state,
        reaction_occurrence=reaction,
        completed_reaction_count=PositiveCount(1),
        boundary_identity=HeldLabel(
            "exact-diffusion-limited-reaction-boundary",
            "reaction-occurrence-is-admissible-only-after-complete-finite-transport-word-closes-on-encounter",
        ),
    )


@dataclass(frozen=True)
class RegisteredTransportReactionOccurrence:
    source_occurrence: PositiveCount
    transport_path: CompleteFiniteTransportPath
    reaction: RetainedReactionOccurrence
    observation_parts: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("transport-reaction source occurrence must be positive")
        forced_diffusion_limited_reaction_boundary(self.transport_path, self.reaction)
        if not isinstance(self.observation_parts, PositiveCount):
            raise InadmissibleExactValue("transport-reaction observation interval must be positive")


@dataclass(frozen=True)
class CompleteTransportReactionFamily:
    ordered_occurrences: tuple[RegisteredTransportReactionOccurrence, ...]

    def __post_init__(self) -> None:
        if not self.ordered_occurrences or any(not isinstance(row, RegisteredTransportReactionOccurrence) for row in self.ordered_occurrences):
            raise InadmissibleExactValue("transport-reaction family requires at least one complete occurrence")
        if tuple(row.source_occurrence.value for row in self.ordered_occurrences) != tuple(range(1, len(self.ordered_occurrences) + 1)):
            raise InadmissibleExactValue("transport-reaction occurrences must be complete and gap-free")


def append_transport_reaction_preserves_complete_family(
    family: CompleteTransportReactionFamily,
    successor: RegisteredTransportReactionOccurrence,
) -> bool:
    if successor.source_occurrence.value != len(family.ordered_occurrences) + 1:
        raise InadmissibleExactValue("transport-reaction successor must be the next positive occurrence")
    prior = tuple(forced_diffusion_limited_reaction_boundary(row.transport_path, row.reaction) for row in family.ordered_occurrences)
    extended = CompleteTransportReactionFamily(family.ordered_occurrences + (successor,))
    results = tuple(forced_diffusion_limited_reaction_boundary(row.transport_path, row.reaction) for row in extended.ordered_occurrences)
    ExactPositiveCompletionRatio.from_counts(
        PositiveCount(len(extended.ordered_occurrences)),
        PositiveCount(sum(row.observation_parts.value for row in extended.ordered_occurrences)),
    )
    return results[: len(prior)] == prior and len(results) == len(prior) + 1


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016", "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003", "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005", "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007", "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
    "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
    "SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-initial-encounter-or-product-endpoint", "Endpoints erase the path that limits reaction entry.", "complete-finite-transport-state-and-transition-word", "Every transport occurrence remains explicit."),
    dimension("composition", "transport-and-reaction-treated-as-unrelated-processes", "Unrelated processes do not establish a limiting boundary.", "transport-exit-is-exact-reaction-encounter-entry", "The two paths compose on one exact state."),
    dimension("limitation", "imported-Fick-Smoluchowski-continuum-or-collision-law", "An imported diffusion premise selects the boundary.", "reaction-admissible-only-after-complete-transport-word", "The reaction waits structurally on transport completion."),
    dimension("rate", "fitted-diffusion-coefficient-rate-constant-or-continuum-time", "A fit or continuum quantity cannot define the exact completion relation.", "completed-reaction-occurrences-per-exact-positive-observation-parts", "Rate correspondence is an exact counted relation downstream of closure."),
    dimension("path", "solvation-transport-encounter-or-product-stage-omitted-or-collapsed", "Omission destroys the complete transport-reaction word.", "all-separated-solvation-transport-encounter-and-product-stages-retained", "Every structurally distinct stage remains held."),
    dimension("status", "simulation-measurement-discrepancy-large-droplet-deviation-or-nonencounter-question-omitted", "Omission falsely regularizes the evidence.", "all-favorable-adverse-control-and-unresolved-statuses-retained", "Every discrepancy and limitation remains visible."),
    dimension("provenance", "selected-fit-rate-table-or-trajectory", "A selected excerpt cannot establish complete source custody.", "complete-251-record-article-supplements-movies-and-dual-archive-ledger", "All pages, frames and archive members remain bound."),
    dimension("prediction", "distance-time-velocity-yield-rate-fit-or-target-readable-before-seal", "Target access can select the law.", "value-free-251-record-identity-seal-and-depth-independent-path-successor", "All identities seal before values and path extension preserves prior results."),
)


EXACT_RESULT = (
    "complete-finite-transport-state-and-transition-word__transport-exit-is-exact-reaction-encounter-entry__"
    "reaction-admissible-only-after-complete-transport-word__"
    "completed-reaction-occurrences-per-exact-positive-observation-parts__"
    "all-separated-solvation-transport-encounter-and-product-stages-retained__"
    "all-favorable-adverse-control-and-unresolved-statuses-retained__"
    "complete-251-record-article-supplements-movies-and-dual-archive-ledger__"
    "value-free-251-record-identity-seal-and-depth-independent-path-successor"
)


def _path(label: str, transported: str = "reactant-a") -> CompleteFiniteTransportPath:
    states = tuple(
        RetainedTransportState(
            HeldLabel("registered-transport-reaction-state", f"{label}-state-{position}"),
            HeldLabel("held-transported-reactant", transported), PositiveCount(position),
            HeldLabel("held-transport-state-status", "retained"),
        )
        for position in range(1, 5)
    )
    transitions = tuple(
        RetainedTransportTransition(
            HeldLabel("registered-transport-transition", f"{label}-edge-{position + 1}"),
            states[position].state_identity, states[position + 1].state_identity,
            HeldLabel("held-transport-reaction-condition", "held-condition"),
            HeldLabel("held-transport-transition-status", "retained"),
        )
        for position in range(len(states) - 1)
    )
    return CompleteFiniteTransportPath(HeldLabel("registered-finite-transport-path", label), states, transitions)


def _reaction(path: CompleteFiniteTransportPath, label: str = "reaction-a") -> RetainedReactionOccurrence:
    return RetainedReactionOccurrence(
        HeldLabel("registered-reaction-occurrence", label), path.exit_state,
        HeldLabel("registered-transport-reaction-state", f"{label}-product"),
        path.ordered_transitions[-1].condition_boundary, HeldLabel("held-reaction-status", "retained"),
    )


_BASE_PATH = _path("path-a")
_BASE_REACTION = _reaction(_BASE_PATH)
_BASE_RESULT = forced_diffusion_limited_reaction_boundary(_BASE_PATH, _BASE_REACTION)
_BASE_FAMILY = CompleteTransportReactionFamily((
    RegisteredTransportReactionOccurrence(PositiveCount(1), _BASE_PATH, _BASE_REACTION, PositiveCount(7)),
))
_NEXT_PATH = _path("path-b", "reactant-b")
OPERATIONAL_WITNESSES = (
    ("complete-path", "Every finite transport transition is retained in order.", len(_BASE_RESULT.complete_transport_word) == len(_BASE_PATH.ordered_states) - 1),
    ("exact-boundary", "Transport exit is the exact reaction encounter entry.", _BASE_RESULT.encounter_state == _BASE_REACTION.encounter_entry_state),
    ("completion-relation", "Completed reactions per held observation parts form an exact positive relation.", ExactPositiveCompletionRatio.from_counts(PositiveCount(3), PositiveCount(2)).value == Fraction(3, 2)),
    ("successor", "Appending the next complete transport-reaction occurrence preserves every prior result.", append_transport_reaction_preserves_complete_family(_BASE_FAMILY, RegisteredTransportReactionOccurrence(PositiveCount(2), _NEXT_PATH, _reaction(_NEXT_PATH, "reaction-b"), PositiveCount(5)))),
)


__all__ = (
    "CompleteFiniteTransportPath", "CompleteTransportReactionFamily", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactDiffusionLimitedReactionBoundary", "ExactPositiveCompletionRatio", "OPERATIONAL_WITNESSES",
    "RegisteredTransportReactionOccurrence", "RetainedReactionOccurrence", "RetainedTransportState",
    "RetainedTransportTransition", "append_transport_reaction_preserves_complete_family",
    "forced_diffusion_limited_reaction_boundary",
)
