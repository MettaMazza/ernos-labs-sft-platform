"""Fold-native complete parallel-mechanism composition law for Chemistry KIN-008."""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.sequential_mechanism_law_v1 import CompleteSequentialMechanism
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class RetainedParallelPath:
    path_identity: HeldLabel
    source_row: PositiveCount
    mechanism: CompleteSequentialMechanism
    path_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.path_identity, HeldLabel) or self.path_identity.family != "registered-parallel-path":
            raise InadmissibleExactValue("parallel composition requires a registered path identity")
        if not isinstance(self.source_row, PositiveCount):
            raise InadmissibleExactValue("parallel composition requires a positive source-row occurrence")
        if not isinstance(self.mechanism, CompleteSequentialMechanism):
            raise InadmissibleExactValue("parallel composition requires a complete sequential path word")
        if not isinstance(self.path_status, HeldLabel) or self.path_status.family != "held-path-status":
            raise InadmissibleExactValue("parallel composition retains favorable, weak, adverse or unresolved status")


@dataclass(frozen=True)
class CompleteParallelMechanism:
    reaction_identity: HeldLabel
    common_initial_state_identity: HeldLabel
    ordered_paths: tuple[RetainedParallelPath, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("parallel composition requires one registered reaction")
        if (
            not isinstance(self.common_initial_state_identity, HeldLabel)
            or self.common_initial_state_identity.family != "registered-mechanism-state"
        ):
            raise InadmissibleExactValue("parallel composition requires one retained common initial state")
        if len(self.ordered_paths) < 2 or any(not isinstance(path, RetainedParallelPath) for path in self.ordered_paths):
            raise InadmissibleExactValue("parallel composition requires at least two complete registered paths")
        if len({path.path_identity for path in self.ordered_paths}) != len(self.ordered_paths):
            raise InadmissibleExactValue("parallel path identities must remain distinct")
        if tuple(path.source_row.value for path in self.ordered_paths) != tuple(range(1, len(self.ordered_paths) + 1)):
            raise InadmissibleExactValue("parallel paths require complete source order without a gap")
        state_words = []
        for path in self.ordered_paths:
            if path.mechanism.reaction_identity != self.reaction_identity:
                raise InadmissibleExactValue("parallel paths cannot combine different registered reactions")
            if path.mechanism.ordered_states[0].state_identity != self.common_initial_state_identity:
                raise InadmissibleExactValue("every parallel path must meet the common initial boundary")
            state_words.append(tuple(state.state_identity for state in path.mechanism.ordered_states))
        if len(set(state_words)) != len(state_words):
            raise InadmissibleExactValue("duplicated state words are not distinct parallel paths")


@dataclass(frozen=True)
class ExactParallelComposition:
    reaction_identity: HeldLabel
    common_initial_state_identity: HeldLabel
    ordered_paths: tuple[RetainedParallelPath, ...]
    terminal_state_word: tuple[HeldLabel, ...]
    path_count: PositiveCount
    composition_identity: HeldLabel


def forced_parallel_mechanism_composition(mechanism: CompleteParallelMechanism) -> ExactParallelComposition:
    if not isinstance(mechanism, CompleteParallelMechanism):
        raise InadmissibleExactValue("parallel composition requires one complete parallel mechanism")
    return ExactParallelComposition(
        reaction_identity=mechanism.reaction_identity,
        common_initial_state_identity=mechanism.common_initial_state_identity,
        ordered_paths=mechanism.ordered_paths,
        terminal_state_word=tuple(path.mechanism.ordered_states[-1].state_identity for path in mechanism.ordered_paths),
        path_count=PositiveCount(len(mechanism.ordered_paths)),
        composition_identity=HeldLabel(
            "exact-parallel-composition",
            "every-path-state-edge-shared-boundary-condition-status-and-terminal-occurrence-retained",
        ),
    )


def append_parallel_path_preserves_complete_family(
    mechanism: CompleteParallelMechanism,
    successor: RetainedParallelPath,
) -> bool:
    if successor.source_row.value != len(mechanism.ordered_paths) + 1:
        raise InadmissibleExactValue("parallel successor must be the next complete source row")
    prior = forced_parallel_mechanism_composition(mechanism)
    extended = CompleteParallelMechanism(
        mechanism.reaction_identity,
        mechanism.common_initial_state_identity,
        mechanism.ordered_paths + (successor,),
    )
    result = forced_parallel_mechanism_composition(extended)
    return (
        result.ordered_paths[: len(prior.ordered_paths)] == prior.ordered_paths
        and result.terminal_state_word[: len(prior.terminal_state_word)] == prior.terminal_state_word
        and result.common_initial_state_identity == prior.common_initial_state_identity
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-INFO-MUTUAL-CONDITIONAL-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-INTERMEDIATE-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-CAT-PATHWAY-001", "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003", "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005", "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-dominant-or-favorable-path-subset", "Selecting one visible path erases competing mechanism support.", "complete-registered-parallel-path-support", "Every registered path remains in the exact family."),
    dimension("origin", "unrelated-or-collapsed-initial-boundary", "Paths without the same retained source do not form one parallel mechanism.", "exact-common-initial-state-boundary", "Every path meets the same registered initial state exactly."),
    dimension("path", "endpoint-only-path-summary", "Endpoints erase the states, edges and intermediates that distinguish paths.", "complete-state-edge-word-for-every-path", "Every path retains its complete sequential mechanism word."),
    dimension("composition", "imported-stochastic-weight-or-parallel-rate-equation", "An imported probability or rate equation can select a favored path.", "finite-source-ordered-parallel-path-composition", "Parallel composition is exactly the complete ordered family of generated path words."),
    dimension("sharing", "shared-prefix-terminal-or-occurrence-collapsed", "Collapsing a shared occurrence destroys path-local reconstruction.", "shared-boundaries-retained-in-every-path-occurrence", "Shared sources, prefixes and terminals remain explicit inside every path."),
    dimension("status", "weak-adverse-unresolved-or-unassigned-path-omitted", "Omission makes the remaining path family falsely complete.", "all-path-statuses-and-unresolved-records-retained", "Favorable, weak, adverse, absent, unresolved and unassigned records remain held."),
    dimension("provenance", "selected-plot-mean-or-answer-only-product-table", "A selected plot or aggregate cannot reconstruct the complete evidence surface.", "complete-article-supplement-and-twenty-eight-sheet-cell-ledger", "The article, supplement, source workbook, all worksheets, cells, replicates, formulas and controls remain bound."),
    dimension("prediction", "product-time-value-readable-before-seal-or-corrected-after-release", "Target access or correction can select a mechanism.", "value-free-twenty-eight-sheet-identity-seal-and-depth-independent-path-successor", "All worksheet identities seal before values open and each added path preserves the complete prior family."),
)


EXACT_RESULT = (
    "complete-registered-parallel-path-support__exact-common-initial-state-boundary__"
    "complete-state-edge-word-for-every-path__finite-source-ordered-parallel-path-composition__"
    "shared-boundaries-retained-in-every-path-occurrence__all-path-statuses-and-unresolved-records-retained__"
    "complete-article-supplement-and-twenty-eight-sheet-cell-ledger__"
    "value-free-twenty-eight-sheet-identity-seal-and-depth-independent-path-successor"
)


def _state(label: str, occurrence: int):
    from sft.chemistry.sequential_mechanism_law_v1 import RetainedMechanismState
    return RetainedMechanismState(
        HeldLabel("registered-mechanism-state", label), PositiveCount(occurrence),
        HeldLabel("held-state-condition", f"condition-{occurrence}"),
        HeldLabel("held-observation-status", "retained"),
    )


def _path(path_label: str, row: int, state_labels: tuple[str, ...]) -> RetainedParallelPath:
    from sft.chemistry.sequential_mechanism_law_v1 import RetainedElementaryTransition
    states = tuple(_state(label, ordinal) for ordinal, label in enumerate(state_labels, start=1))
    transitions = tuple(
        RetainedElementaryTransition(
            HeldLabel("registered-elementary-transition", f"{path_label}-edge-{ordinal}"), PositiveCount(ordinal),
            states[ordinal - 1].state_identity, states[ordinal].state_identity,
            HeldLabel("held-transition-condition", f"{path_label}-boundary-{ordinal}"),
            HeldLabel("held-transition-status", "retained"),
        )
        for ordinal in range(1, len(states))
    )
    mechanism = CompleteSequentialMechanism(HeldLabel("registered-reaction", "reaction-a"), states, transitions)
    return RetainedParallelPath(
        HeldLabel("registered-parallel-path", path_label), PositiveCount(row), mechanism,
        HeldLabel("held-path-status", "retained"),
    )


_BASE = CompleteParallelMechanism(
    HeldLabel("registered-reaction", "reaction-a"), HeldLabel("registered-mechanism-state", "source-a"),
    (_path("path-one", 1, ("source-a", "state-b", "terminal-d")),
     _path("path-two", 2, ("source-a", "state-c", "terminal-d"))),
)
_RESULT = forced_parallel_mechanism_composition(_BASE)
OPERATIONAL_WITNESSES = (
    ("complete-family", "Both generated parallel paths remain retained in source order.", len(_RESULT.ordered_paths) == 2),
    ("common-source", "Every path meets the exact common initial state boundary.", all(path.mechanism.ordered_states[0].state_identity == _RESULT.common_initial_state_identity for path in _RESULT.ordered_paths)),
    ("shared-terminal", "A shared terminal remains one explicit terminal occurrence per path.", _RESULT.terminal_state_word == (HeldLabel("registered-mechanism-state", "terminal-d"), HeldLabel("registered-mechanism-state", "terminal-d"))),
    ("successor", "Appending a third path retains every earlier path and terminal occurrence.", append_parallel_path_preserves_complete_family(_BASE, _path("path-three", 3, ("source-a", "state-e", "state-f", "terminal-d")))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "CompleteParallelMechanism",
    "ExactParallelComposition", "RetainedParallelPath", "append_parallel_path_preserves_complete_family",
    "forced_parallel_mechanism_composition",
)
