"""Fold-native catalytic turnover and cycle-frequency law for Chemistry KIN-010."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True, order=True)
class ExactPositiveRatio:
    """Exact completed-cycle count per exact positive observation partition."""

    value: Fraction

    @classmethod
    def from_counts(cls, completed_cycles: PositiveCount, interval_parts: PositiveCount) -> "ExactPositiveRatio":
        if not isinstance(completed_cycles, PositiveCount) or not isinstance(interval_parts, PositiveCount):
            raise InadmissibleExactValue("cycle frequency requires two exact positive counts")
        return cls(Fraction(completed_cycles.value, interval_parts.value))

    def __post_init__(self) -> None:
        if not isinstance(self.value, Fraction) or self.value <= 0:
            raise InadmissibleExactValue("cycle frequency must be an exact positive whole/fractional relation")


@dataclass(frozen=True)
class RetainedCatalystState:
    state_identity: HeldLabel
    catalyst_identity: HeldLabel
    cycle_position: PositiveCount
    observation_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.state_identity, HeldLabel) or self.state_identity.family != "registered-catalytic-state":
            raise InadmissibleExactValue("catalytic state identity must remain registered")
        if not isinstance(self.catalyst_identity, HeldLabel) or self.catalyst_identity.family != "held-catalyst-identity":
            raise InadmissibleExactValue("catalyst identity must remain held through the cycle")
        if not isinstance(self.cycle_position, PositiveCount):
            raise InadmissibleExactValue("catalytic state position must be a positive occurrence")
        if not isinstance(self.observation_status, HeldLabel) or self.observation_status.family != "held-catalytic-state-status":
            raise InadmissibleExactValue("observed, structural and unresolved state status must remain held")


@dataclass(frozen=True)
class RetainedCatalyticTransition:
    transition_identity: HeldLabel
    entry_state: HeldLabel
    exit_state: HeldLabel
    process_identity: HeldLabel
    condition_boundary: HeldLabel
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.transition_identity, HeldLabel) or self.transition_identity.family != "registered-catalytic-transition":
            raise InadmissibleExactValue("catalytic transition identity must remain registered")
        if (
            not isinstance(self.entry_state, HeldLabel) or self.entry_state.family != "registered-catalytic-state"
            or not isinstance(self.exit_state, HeldLabel) or self.exit_state.family != "registered-catalytic-state"
            or self.entry_state == self.exit_state
        ):
            raise InadmissibleExactValue("catalytic transition requires two distinct registered states")
        if not isinstance(self.process_identity, HeldLabel) or self.process_identity.family != "held-catalytic-process":
            raise InadmissibleExactValue("catalytic process identity must remain held")
        if not isinstance(self.condition_boundary, HeldLabel) or self.condition_boundary.family != "held-catalytic-condition":
            raise InadmissibleExactValue("catalytic condition boundary must remain held")
        if not isinstance(self.evidence_status, HeldLabel) or self.evidence_status.family != "held-catalytic-transition-status":
            raise InadmissibleExactValue("catalytic transition evidence status must remain held")


@dataclass(frozen=True)
class CompleteCatalyticCycle:
    cycle_identity: HeldLabel
    ordered_states: tuple[RetainedCatalystState, ...]
    ordered_transitions: tuple[RetainedCatalyticTransition, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.cycle_identity, HeldLabel) or self.cycle_identity.family != "registered-catalytic-cycle":
            raise InadmissibleExactValue("catalytic cycle identity must remain registered")
        if len(self.ordered_states) < 2 or len(self.ordered_transitions) != len(self.ordered_states):
            raise InadmissibleExactValue("a complete catalytic cycle requires every state and closing transition")
        if any(not isinstance(state, RetainedCatalystState) for state in self.ordered_states):
            raise InadmissibleExactValue("catalytic cycle contains an unregistered state")
        if any(not isinstance(edge, RetainedCatalyticTransition) for edge in self.ordered_transitions):
            raise InadmissibleExactValue("catalytic cycle contains an unregistered transition")
        if tuple(state.cycle_position.value for state in self.ordered_states) != tuple(range(1, len(self.ordered_states) + 1)):
            raise InadmissibleExactValue("catalytic cycle positions must be complete and gap-free")
        if len({state.state_identity for state in self.ordered_states}) != len(self.ordered_states):
            raise InadmissibleExactValue("catalytic state occurrences must remain distinguishable")
        catalyst = self.ordered_states[0].catalyst_identity
        if any(state.catalyst_identity != catalyst for state in self.ordered_states):
            raise InadmissibleExactValue("the same exact catalyst identity must traverse every cycle state")
        condition = self.ordered_transitions[0].condition_boundary
        for position, transition in enumerate(self.ordered_transitions):
            entry = self.ordered_states[position].state_identity
            exit_state = self.ordered_states[(position + 1) % len(self.ordered_states)].state_identity
            if transition.entry_state != entry or transition.exit_state != exit_state:
                raise InadmissibleExactValue("every catalytic transition must join the next exact state and close on entry")
            if transition.condition_boundary != condition:
                raise InadmissibleExactValue("one complete cycle requires one exact held condition boundary")

    @property
    def catalyst_identity(self) -> HeldLabel:
        return self.ordered_states[0].catalyst_identity


@dataclass(frozen=True)
class ExactCatalyticTurnover:
    cycle_identity: HeldLabel
    catalyst_identity: HeldLabel
    ordered_transition_word: tuple[RetainedCatalyticTransition, ...]
    completed_cycle_count: PositiveCount
    exact_return_state: HeldLabel
    turnover_identity: HeldLabel


def forced_catalytic_turnover(cycle: CompleteCatalyticCycle) -> ExactCatalyticTurnover:
    if not isinstance(cycle, CompleteCatalyticCycle):
        raise InadmissibleExactValue("turnover requires one complete catalyst-return cycle")
    return ExactCatalyticTurnover(
        cycle_identity=cycle.cycle_identity,
        catalyst_identity=cycle.catalyst_identity,
        ordered_transition_word=cycle.ordered_transitions,
        completed_cycle_count=PositiveCount(1),
        exact_return_state=cycle.ordered_states[0].state_identity,
        turnover_identity=HeldLabel(
            "exact-catalytic-turnover",
            "one-complete-transition-word-returns-the-held-catalyst-to-its-entry-state",
        ),
    )


@dataclass(frozen=True)
class ExactCatalyticCycleFrequency:
    completed_cycle_count: PositiveCount
    exact_interval_parts: PositiveCount
    cycle_frequency: ExactPositiveRatio
    frequency_identity: HeldLabel


def forced_cycle_frequency(
    completed_cycle_count: PositiveCount,
    exact_interval_parts: PositiveCount,
) -> ExactCatalyticCycleFrequency:
    return ExactCatalyticCycleFrequency(
        completed_cycle_count=completed_cycle_count,
        exact_interval_parts=exact_interval_parts,
        cycle_frequency=ExactPositiveRatio.from_counts(completed_cycle_count, exact_interval_parts),
        frequency_identity=HeldLabel(
            "exact-catalytic-cycle-frequency",
            "completed-catalyst-return-words-per-exact-held-observation-partition",
        ),
    )


@dataclass(frozen=True)
class RegisteredCatalyticCycleOccurrence:
    source_occurrence: PositiveCount
    cycle: CompleteCatalyticCycle
    exact_interval_parts: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("catalytic source occurrence must be positive")
        if not isinstance(self.cycle, CompleteCatalyticCycle):
            raise InadmissibleExactValue("catalytic family requires complete cycles")
        if not isinstance(self.exact_interval_parts, PositiveCount):
            raise InadmissibleExactValue("catalytic observation interval must be exact and positive")


@dataclass(frozen=True)
class CompleteCatalyticCycleFamily:
    ordered_occurrences: tuple[RegisteredCatalyticCycleOccurrence, ...]

    def __post_init__(self) -> None:
        if not self.ordered_occurrences or any(
            not isinstance(row, RegisteredCatalyticCycleOccurrence) for row in self.ordered_occurrences
        ):
            raise InadmissibleExactValue("catalytic family requires at least one complete cycle occurrence")
        if tuple(row.source_occurrence.value for row in self.ordered_occurrences) != tuple(
            range(1, len(self.ordered_occurrences) + 1)
        ):
            raise InadmissibleExactValue("catalytic cycle occurrences must be complete and gap-free")


def append_complete_cycle_preserves_turnover_family(
    family: CompleteCatalyticCycleFamily,
    successor: RegisteredCatalyticCycleOccurrence,
) -> bool:
    if successor.source_occurrence.value != len(family.ordered_occurrences) + 1:
        raise InadmissibleExactValue("catalytic successor must be the next positive source occurrence")
    prior_turnovers = tuple(forced_catalytic_turnover(row.cycle) for row in family.ordered_occurrences)
    prior_frequency = forced_cycle_frequency(PositiveCount(len(family.ordered_occurrences)), PositiveCount(
        sum(row.exact_interval_parts.value for row in family.ordered_occurrences)
    ))
    extended = CompleteCatalyticCycleFamily(family.ordered_occurrences + (successor,))
    extended_turnovers = tuple(forced_catalytic_turnover(row.cycle) for row in extended.ordered_occurrences)
    extended_frequency = forced_cycle_frequency(PositiveCount(len(extended.ordered_occurrences)), PositiveCount(
        sum(row.exact_interval_parts.value for row in extended.ordered_occurrences)
    ))
    return (
        extended_turnovers[: len(prior_turnovers)] == prior_turnovers
        and len(extended_turnovers) == len(prior_turnovers) + 1
        and prior_frequency.completed_cycle_count.value + 1 == extended_frequency.completed_cycle_count.value
    )


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
    "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("catalyst", "selected-participant-or-renamed-product", "A selected participant does not establish catalyst persistence.", "same-held-catalyst-identity-at-entry-through-every-state-and-return", "One exact catalyst identity traverses and closes the cycle."),
    dimension("cycle", "endpoint-pair-or-incomplete-intermediate-path", "An open path is not a catalytic cycle.", "complete-ordered-state-and-transition-word-closing-on-entry", "Every intermediate and transition occurrence is retained through exact return."),
    dimension("turnover", "imported-turnover-rate-equation-or-product-total", "An imported rate or product total cannot define a completed cycle.", "one-complete-catalyst-return-word-is-one-turnover", "Turnover is forced by exact cycle closure."),
    dimension("frequency", "fitted-continuum-rate-steady-state-or-stochastic-weight", "A fit or stochastic premise imports the frequency law.", "completed-return-words-per-exact-positive-observation-partition", "Frequency is the exact positive count relation of closed cycles to held interval parts."),
    dimension("state", "four-observed-conductance-levels-substituted-for-five-structural-states", "Collapsing the structural intermediate breaks the complete transition word.", "five-structural-states-with-four-separately-observed-statuses-distinguished", "Structural and observational status remain separate held labels."),
    dimension("status", "deactivation-insufficient-fit-control-or-unresolved-record-omitted", "Omission regularizes the source surface.", "all-favorable-adverse-control-and-unresolved-records-retained", "Every status remains explicit without selection or averaging."),
    dimension("provenance", "selected-turnover-table-plot-or-fitted-answer", "A selected excerpt cannot establish complete custody.", "complete-497-record-article-supplement-movie-archive-ledger", "All source pages, frames and archive members remain bound."),
    dimension("prediction", "cycle-value-rate-frequency-condition-or-target-readable-before-seal", "Target access can select the law.", "value-free-497-record-identity-seal-and-depth-independent-cycle-successor", "All identities seal before values and complete-cycle extension preserves prior results."),
)


EXACT_RESULT = (
    "same-held-catalyst-identity-at-entry-through-every-state-and-return__"
    "complete-ordered-state-and-transition-word-closing-on-entry__"
    "one-complete-catalyst-return-word-is-one-turnover__"
    "completed-return-words-per-exact-positive-observation-partition__"
    "five-structural-states-with-four-separately-observed-statuses-distinguished__"
    "all-favorable-adverse-control-and-unresolved-records-retained__"
    "complete-497-record-article-supplement-movie-archive-ledger__"
    "value-free-497-record-identity-seal-and-depth-independent-cycle-successor"
)


def _state(position: int, label: str, catalyst: str = "catalyst-a", status: str = "retained") -> RetainedCatalystState:
    return RetainedCatalystState(
        HeldLabel("registered-catalytic-state", label), HeldLabel("held-catalyst-identity", catalyst),
        PositiveCount(position), HeldLabel("held-catalytic-state-status", status),
    )


def _transition(entry: str, exit_state: str, process: str, condition: str = "held-condition") -> RetainedCatalyticTransition:
    return RetainedCatalyticTransition(
        HeldLabel("registered-catalytic-transition", f"{entry}-to-{exit_state}"),
        HeldLabel("registered-catalytic-state", entry), HeldLabel("registered-catalytic-state", exit_state),
        HeldLabel("held-catalytic-process", process), HeldLabel("held-catalytic-condition", condition),
        HeldLabel("held-catalytic-transition-status", "retained"),
    )


def _cycle(label: str, catalyst: str = "catalyst-a") -> CompleteCatalyticCycle:
    states = tuple(_state(position, f"{label}-state-{position}", catalyst) for position in range(1, 6))
    processes = ("entry-process", "second-process", "third-process", "fourth-process", "return-process")
    transitions = tuple(
        _transition(states[position].state_identity.label, states[(position + 1) % len(states)].state_identity.label, process)
        for position, process in enumerate(processes)
    )
    return CompleteCatalyticCycle(HeldLabel("registered-catalytic-cycle", label), states, transitions)


_BASE_CYCLE = _cycle("cycle-a")
_BASE_TURNOVER = forced_catalytic_turnover(_BASE_CYCLE)
_BASE_FAMILY = CompleteCatalyticCycleFamily((
    RegisteredCatalyticCycleOccurrence(PositiveCount(1), _BASE_CYCLE, PositiveCount(7)),
))
OPERATIONAL_WITNESSES = (
    ("identity-return", "The exact catalyst identity is unchanged through all states and return.", _BASE_TURNOVER.catalyst_identity == _BASE_CYCLE.ordered_states[-1].catalyst_identity and _BASE_TURNOVER.exact_return_state == _BASE_CYCLE.ordered_states[0].state_identity),
    ("complete-word", "Every transition joins the next state and the last returns to the first.", len(_BASE_TURNOVER.ordered_transition_word) == len(_BASE_CYCLE.ordered_states) and _BASE_TURNOVER.ordered_transition_word[-1].exit_state == _BASE_CYCLE.ordered_states[0].state_identity),
    ("frequency", "Cycle frequency is an exact positive count relation.", forced_cycle_frequency(PositiveCount(3), PositiveCount(2)).cycle_frequency.value == Fraction(3, 2)),
    ("successor", "Appending the next complete cycle preserves every prior turnover.", append_complete_cycle_preserves_turnover_family(_BASE_FAMILY, RegisteredCatalyticCycleOccurrence(PositiveCount(2), _cycle("cycle-b", "catalyst-b"), PositiveCount(5)))),
)


__all__ = (
    "CompleteCatalyticCycle", "CompleteCatalyticCycleFamily", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactCatalyticCycleFrequency", "ExactCatalyticTurnover", "ExactPositiveRatio", "OPERATIONAL_WITNESSES",
    "RegisteredCatalyticCycleOccurrence", "RetainedCatalystState", "RetainedCatalyticTransition",
    "append_complete_cycle_preserves_turnover_family", "forced_catalytic_turnover", "forced_cycle_frequency",
)
