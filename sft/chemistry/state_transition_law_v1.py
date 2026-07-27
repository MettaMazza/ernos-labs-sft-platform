"""Fold-native molecular-state transformation law for ELEC-009."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence import FoldWord
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


FORWARD = HeldLabel("transition-orientation", "forward-held")
REVERSE = HeldLabel("transition-orientation", "reverse-held")
BIDIRECTIONAL = HeldLabel("transition-orientation", "bidirectional-held")
COUPLED = HeldLabel("transition-orientation", "coupled-without-direction")
ABSENT = HeldLabel("transition-orientation", "structurally-absent")


@dataclass(frozen=True)
class MolecularStateTransition:
    molecular_carrier: HeldLabel
    initial_state: HeldLabel
    terminal_state_or_absence: Union[HeldLabel, EmptyOne]
    orientation: HeldLabel
    retained_record: HeldLabel

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier" or self.initial_state.family != "molecular-state":
            raise InadmissibleExactValue("state transformation requires retained carrier and initial state")
        if self.retained_record.family != "transition-record":
            raise InadmissibleExactValue("state transformation requires one retained observation record")
        if self.orientation == ABSENT:
            if self.terminal_state_or_absence is not EMPTY_ONE:
                raise InadmissibleExactValue("absent transition must close its terminal coordinate structurally")
        else:
            if self.orientation not in (FORWARD, REVERSE, BIDIRECTIONAL, COUPLED):
                raise InadmissibleExactValue("state transformation orientation is not generated")
            if not isinstance(self.terminal_state_or_absence, HeldLabel) or self.terminal_state_or_absence.family != "molecular-state":
                raise InadmissibleExactValue("observed transformation requires a retained terminal state")
            if self.terminal_state_or_absence == self.initial_state:
                raise InadmissibleExactValue("a transformation must retain a state distinction")

    @property
    def is_observed(self) -> bool:
        return self.orientation != ABSENT


def observed_transition(molecule: str, initial: str, terminal: str, orientation: HeldLabel, record: str) -> MolecularStateTransition:
    return MolecularStateTransition(HeldLabel("molecular-carrier", molecule), HeldLabel("molecular-state", initial), HeldLabel("molecular-state", terminal), orientation, HeldLabel("transition-record", record))


def absent_transition(molecule: str, initial: str, record: str) -> MolecularStateTransition:
    return MolecularStateTransition(HeldLabel("molecular-carrier", molecule), HeldLabel("molecular-state", initial), EMPTY_ONE, ABSENT, HeldLabel("transition-record", record))


def compose_transition_path(first: MolecularStateTransition, second: MolecularStateTransition) -> FoldWord:
    if first.molecular_carrier != second.molecular_carrier or not first.is_observed or not second.is_observed:
        raise InadmissibleExactValue("transition composition requires two observed transformations on one carrier")
    if first.terminal_state_or_absence != second.initial_state:
        raise InadmissibleExactValue("transition path endpoints do not compose")
    return FoldWord((first.molecular_carrier, first.initial_state, first.terminal_state_or_absence, second.terminal_state_or_absence, first.orientation, second.orientation))


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-QUANTUM-MEASUREMENT-001", "SFT-CHEM-STATE-ENERGY-ORDER-004", "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005", "SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "transition-label-alone", "A label alone erases the transforming molecular carrier.", "retained-molecular-carrier", "One carrier persists through the transformation."),
    dimension("endpoints", "unbound-final-answer", "An answer without endpoints cannot identify a state transformation.", "distinct-initial-and-terminal-states", "Every observed transformation retains both distinct state identities."),
    dimension("orientation", "signed-or-unoriented-change", "A sign or erased orientation loses the observed direction class.", "held-forward-reverse-bidirectional-or-coupled", "Orientation is an exact held label, never a signed proof magnitude."),
    dimension("absence", "absence-treated-as-number", "Numerical absence violates the Fold domain.", "closed-terminal-EmptyOne", "An unobserved transition closes the terminal coordinate structurally."),
    dimension("trace", "endpoint-only-lookup", "Endpoints alone erase the transition record and provenance.", "complete-state-transition-trace", "Carrier, endpoints, orientation and record remain composed."),
    dimension("composition", "nonmatching-path-concatenation", "Transitions with unequal adjacent endpoints cannot form one path.", "matching-endpoint-composition", "Exact endpoint equality alone permits path composition."),
    dimension("record", "selected-present-transition", "Selecting only observed rows cannot test absence or coupling records.", "complete-presence-coupling-absence-vector", "Every registered directional, coupled and absent source row is retained."),
    dimension("extension", "species-selection-rule-premise", "A selection rule at this stage imports the next obligation.", "finite-path-successor-with-no-extra-rule", "Every matching successor extends the exact path without a species exception."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first = observed_transition("H2", "B", "C", BIDIRECTIONAL, "B-C")
    second = observed_transition("H2", "C", "X", FORWARD, "C-X")
    missing = absent_transition("H2", "X", "source-empty-transition-cell")
    mismatch_rejected = self_rejected = False
    try: compose_transition_path(first, observed_transition("H2", "E", "F", FORWARD, "E-F"))
    except InadmissibleExactValue: mismatch_rejected = True
    try: observed_transition("H2", "B", "B", FORWARD, "invalid")
    except InadmissibleExactValue: self_rejected = True
    return (("observed-transition", "Distinct endpoints and held orientation form one exact transformation.", first.is_observed), ("composed-path", "Matching terminal and initial states compose without a new rule.", len(compose_transition_path(first, second).cells) == 6), ("absent-coordinate", "A source-absent transition closes as EmptyOne rather than numerical zero.", missing.terminal_state_or_absence is EMPTY_ONE and not missing.is_observed), ("mismatch-control", "Nonmatching endpoints reject.", mismatch_rejected), ("self-transition-control", "An erased endpoint distinction rejects.", self_rejected))


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "retained-molecular-carrier__distinct-initial-and-terminal-states__held-forward-reverse-bidirectional-or-coupled__closed-terminal-EmptyOne__complete-state-transition-trace__matching-endpoint-composition__complete-presence-coupling-absence-vector__finite-path-successor-with-no-extra-rule"


__all__ = ("ABSENT", "BIDIRECTIONAL", "COUPLED", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "FORWARD", "MolecularStateTransition", "OPERATIONAL_WITNESSES", "REVERSE", "absent_transition", "compose_transition_path", "observed_transition")
