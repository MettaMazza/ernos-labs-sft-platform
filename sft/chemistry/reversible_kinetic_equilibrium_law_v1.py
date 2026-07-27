"""Fold-native reversible kinetic-equilibrium correspondence for Chemistry KIN-009."""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class RetainedDirectedTransition:
    transition_identity: HeldLabel
    entry_state: HeldLabel
    exit_state: HeldLabel
    orientation: HeldLabel
    condition_boundary: HeldLabel
    observation_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.transition_identity, HeldLabel) or self.transition_identity.family != "registered-reversible-transition":
            raise InadmissibleExactValue("reversible correspondence requires a registered directed transition")
        if (
            not isinstance(self.entry_state, HeldLabel) or self.entry_state.family != "registered-reversible-state"
            or not isinstance(self.exit_state, HeldLabel) or self.exit_state.family != "registered-reversible-state"
            or self.entry_state == self.exit_state
        ):
            raise InadmissibleExactValue("a directed transition must retain two distinct registered states")
        if not isinstance(self.orientation, HeldLabel) or self.orientation.family != "held-transition-orientation":
            raise InadmissibleExactValue("transition direction is a held orientation, not a signed quantity")
        if not isinstance(self.condition_boundary, HeldLabel) or self.condition_boundary.family != "held-reversible-condition":
            raise InadmissibleExactValue("the reversible condition boundary must remain held")
        if not isinstance(self.observation_status, HeldLabel) or self.observation_status.family != "held-reversible-status":
            raise InadmissibleExactValue("favorable, adverse and unresolved status must remain held")


@dataclass(frozen=True)
class CompleteReversiblePairGraph:
    pair_identity: HeldLabel
    first_state: HeldLabel
    second_state: HeldLabel
    forward_transition: RetainedDirectedTransition
    reverse_transition: RetainedDirectedTransition

    def __post_init__(self) -> None:
        if not isinstance(self.pair_identity, HeldLabel) or self.pair_identity.family != "registered-reversible-pair":
            raise InadmissibleExactValue("reversible correspondence requires one registered state pair")
        if (
            not isinstance(self.first_state, HeldLabel) or self.first_state.family != "registered-reversible-state"
            or not isinstance(self.second_state, HeldLabel) or self.second_state.family != "registered-reversible-state"
            or self.first_state == self.second_state
        ):
            raise InadmissibleExactValue("a reversible pair requires two distinct registered states")
        if (
            self.forward_transition.entry_state != self.first_state
            or self.forward_transition.exit_state != self.second_state
            or self.reverse_transition.entry_state != self.second_state
            or self.reverse_transition.exit_state != self.first_state
        ):
            raise InadmissibleExactValue("forward and reverse edges must close the same exact two-state graph")
        if self.forward_transition.orientation == self.reverse_transition.orientation:
            raise InadmissibleExactValue("forward and reverse held orientations must remain distinguishable")
        if self.forward_transition.condition_boundary != self.reverse_transition.condition_boundary:
            raise InadmissibleExactValue("kinetic-equilibrium correspondence requires one exact held condition boundary")


@dataclass(frozen=True)
class ExactKineticEquilibriumCorrespondence:
    pair_identity: HeldLabel
    recurrence_support: tuple[HeldLabel, HeldLabel]
    directed_transition_word: tuple[RetainedDirectedTransition, RetainedDirectedTransition]
    graph_edge_count: PositiveCount
    correspondence_identity: HeldLabel


def forced_reversible_kinetic_equilibrium_correspondence(
    graph: CompleteReversiblePairGraph,
) -> ExactKineticEquilibriumCorrespondence:
    if not isinstance(graph, CompleteReversiblePairGraph):
        raise InadmissibleExactValue("correspondence requires one complete reversible pair graph")
    return ExactKineticEquilibriumCorrespondence(
        pair_identity=graph.pair_identity,
        recurrence_support=(graph.first_state, graph.second_state),
        directed_transition_word=(graph.forward_transition, graph.reverse_transition),
        graph_edge_count=PositiveCount(2),
        correspondence_identity=HeldLabel(
            "exact-kinetic-equilibrium-correspondence",
            "one-closed-pair-graph-supplies-directed-kinetic-occurrences-and-equilibrium-recurrence-support",
        ),
    )


@dataclass(frozen=True)
class RegisteredReversiblePair:
    source_occurrence: PositiveCount
    graph: CompleteReversiblePairGraph

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("reversible pair occurrence must be a positive count")
        if not isinstance(self.graph, CompleteReversiblePairGraph):
            raise InadmissibleExactValue("reversible family requires complete pair graphs")


@dataclass(frozen=True)
class CompleteReversibleFamily:
    ordered_pairs: tuple[RegisteredReversiblePair, ...]

    def __post_init__(self) -> None:
        if not self.ordered_pairs or any(not isinstance(row, RegisteredReversiblePair) for row in self.ordered_pairs):
            raise InadmissibleExactValue("a reversible family requires at least one complete pair")
        if tuple(row.source_occurrence.value for row in self.ordered_pairs) != tuple(range(1, len(self.ordered_pairs) + 1)):
            raise InadmissibleExactValue("reversible pair occurrences must be complete and gap-free")
        if len({row.graph.pair_identity for row in self.ordered_pairs}) != len(self.ordered_pairs):
            raise InadmissibleExactValue("reversible pair identities must remain distinct")


def append_reversible_pair_preserves_complete_family(
    family: CompleteReversibleFamily,
    successor: RegisteredReversiblePair,
) -> bool:
    if successor.source_occurrence.value != len(family.ordered_pairs) + 1:
        raise InadmissibleExactValue("reversible successor must be the next positive source occurrence")
    prior = tuple(forced_reversible_kinetic_equilibrium_correspondence(row.graph) for row in family.ordered_pairs)
    extended = CompleteReversibleFamily(family.ordered_pairs + (successor,))
    result = tuple(forced_reversible_kinetic_equilibrium_correspondence(row.graph) for row in extended.ordered_pairs)
    return result[: len(prior)] == prior and len(result) == len(prior) + 1


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004", "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002", "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003",
    "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004", "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005",
    "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006", "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007",
    "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-forward-or-reverse-direction", "One direction cannot establish a reversible pair.", "both-held-directional-transition-occurrences", "Both directed occurrences remain explicit."),
    dimension("graph", "separate-unrelated-forward-and-reverse-graphs", "Unrelated paths cannot supply one kinetic-equilibrium correspondence.", "same-exact-two-state-closed-transition-graph", "Both edges close the same retained state pair."),
    dimension("kinetics", "endpoint-rate-fit-or-aggregate-only", "A fit or endpoint erases ordered directed transition occurrences.", "exact-ordered-directed-transition-word", "Kinetics is the retained directed edge word."),
    dimension("equilibrium", "imported-equilibrium-constant-steady-state-or-balance-law", "An imported equilibrium premise selects the correspondence.", "closed-graph-recurrence-support", "Equilibrium support is the state support of the same closed graph."),
    dimension("composition", "terminal-compositions-collapsed-or-averaged", "Averaging hides direction-specific observations.", "every-initial-terminal-composition-retained-separately", "Every observed composition remains an exact separate record."),
    dimension("status", "direction-label-disagreement-or-adverse-row-omitted", "Omission falsely regularizes the source.", "all-favorable-adverse-and-disagreement-records-retained", "Every adverse and internally inconsistent source label remains visible."),
    dimension("provenance", "selected-kinetic-pages-or-answer-table", "A selected excerpt cannot prove complete source custody.", "complete-article-supplement-movie-and-archive-ledger", "All 164 sealed source records remain bound."),
    dimension("prediction", "state-time-composition-energy-or-target-readable-before-seal", "Target access can select the graph.", "value-free-164-record-identity-seal-and-depth-independent-pair-successor", "All identities seal before values and pair extension preserves prior correspondences."),
)


EXACT_RESULT = (
    "both-held-directional-transition-occurrences__same-exact-two-state-closed-transition-graph__"
    "exact-ordered-directed-transition-word__closed-graph-recurrence-support__"
    "every-initial-terminal-composition-retained-separately__"
    "all-favorable-adverse-and-disagreement-records-retained__"
    "complete-article-supplement-movie-and-archive-ledger__"
    "value-free-164-record-identity-seal-and-depth-independent-pair-successor"
)


def _transition(label: str, entry: str, exit: str, orientation: str, condition: str = "held-condition") -> RetainedDirectedTransition:
    return RetainedDirectedTransition(
        HeldLabel("registered-reversible-transition", label),
        HeldLabel("registered-reversible-state", entry), HeldLabel("registered-reversible-state", exit),
        HeldLabel("held-transition-orientation", orientation), HeldLabel("held-reversible-condition", condition),
        HeldLabel("held-reversible-status", "retained"),
    )


def _graph(label: str, first: str, second: str) -> CompleteReversiblePairGraph:
    return CompleteReversiblePairGraph(
        HeldLabel("registered-reversible-pair", label),
        HeldLabel("registered-reversible-state", first), HeldLabel("registered-reversible-state", second),
        _transition(label + "-forward", first, second, "first-to-second"),
        _transition(label + "-reverse", second, first, "second-to-first"),
    )


_BASE_GRAPH = _graph("pair-ab", "state-a", "state-b")
_BASE_RESULT = forced_reversible_kinetic_equilibrium_correspondence(_BASE_GRAPH)
_BASE_FAMILY = CompleteReversibleFamily((RegisteredReversiblePair(PositiveCount(1), _BASE_GRAPH),))
OPERATIONAL_WITNESSES = (
    ("same-graph", "Forward and reverse transitions close the same two-state graph.", _BASE_RESULT.directed_transition_word[0].entry_state == _BASE_RESULT.directed_transition_word[1].exit_state and _BASE_RESULT.directed_transition_word[0].exit_state == _BASE_RESULT.directed_transition_word[1].entry_state),
    ("kinetics", "The two held orientations remain explicit ordered transition occurrences.", len(_BASE_RESULT.directed_transition_word) == 2 and _BASE_RESULT.directed_transition_word[0].orientation != _BASE_RESULT.directed_transition_word[1].orientation),
    ("equilibrium", "The recurrence support is exactly the two retained graph states.", _BASE_RESULT.recurrence_support == (_BASE_GRAPH.first_state, _BASE_GRAPH.second_state)),
    ("successor", "Appending the next reversible pair retains every prior correspondence.", append_reversible_pair_preserves_complete_family(_BASE_FAMILY, RegisteredReversiblePair(PositiveCount(2), _graph("pair-cd", "state-c", "state-d")))),
)


__all__ = (
    "CompleteReversibleFamily", "CompleteReversiblePairGraph", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactKineticEquilibriumCorrespondence", "OPERATIONAL_WITNESSES", "RegisteredReversiblePair",
    "RetainedDirectedTransition", "append_reversible_pair_preserves_complete_family",
    "forced_reversible_kinetic_equilibrium_correspondence",
)
