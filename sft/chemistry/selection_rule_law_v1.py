"""Fold-native chemical observation and selection-rule law for ELEC-010."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


DIRECT = HeldLabel("selection-observation-class", "direct-one-fold-observation")
MEDIATED = HeldLabel("selection-observation-class", "mediated-multi-fold-observation")
COUPLED = HeldLabel("selection-observation-class", "coupled-without-direction")
CLOSED = HeldLabel("selection-observation-class", "closed-observation-coordinate")
UNRESOLVED = HeldLabel("selection-observation-class", "endpoint-signature-not-source-resolved")

AXIS_NEIGHBOURS = {
    ("Σ", "Σ"), ("Σ", "Π"), ("Π", "Σ"), ("Π", "Π"),
    ("Π", "Δ"), ("Δ", "Π"), ("Δ", "Δ"),
    ("Δ", "Φ"), ("Φ", "Δ"), ("Φ", "Φ"),
}


@dataclass(frozen=True)
class StateSignature:
    state: HeldLabel
    multiplicity: PositiveCount
    inversion: HeldLabel
    axis: HeldLabel

    def __post_init__(self) -> None:
        if self.state.family != "molecular-state":
            raise InadmissibleExactValue("selection signature requires one retained molecular state")
        if self.inversion.family != "inversion-fibre" or self.axis.family != "axis-support":
            raise InadmissibleExactValue("selection signature requires held inversion and axis labels")


@dataclass(frozen=True)
class SelectionRecord:
    initial: Optional[StateSignature]
    terminal: Optional[StateSignature]
    observation_class: HeldLabel
    mediator_or_absence: object
    retained_record: HeldLabel

    def __post_init__(self) -> None:
        if self.retained_record.family != "selection-record":
            raise InadmissibleExactValue("selection result requires its exact observation record")
        if self.observation_class == CLOSED:
            if self.initial is None or self.terminal is not None or self.mediator_or_absence is not EMPTY_ONE:
                raise InadmissibleExactValue("closed observation must retain its source and structural EmptyOne")
        elif self.observation_class == COUPLED:
            if self.initial is None or self.terminal is None or self.mediator_or_absence is not EMPTY_ONE:
                raise InadmissibleExactValue("coupling retains two states without a transition mediator")
        elif self.observation_class == UNRESOLVED:
            if (self.initial is None) == (self.terminal is None):
                raise InadmissibleExactValue("an unresolved endpoint record retains exactly one known signature")
        elif self.observation_class == DIRECT:
            if self.initial is None or self.terminal is None or self.mediator_or_absence is not EMPTY_ONE:
                raise InadmissibleExactValue("direct observation retains two signatures and no mediator")
            if not direct_observation_allowed(self.initial, self.terminal):
                raise InadmissibleExactValue("closed distinction cannot pass as a direct observation")
        elif self.observation_class == MEDIATED:
            if self.initial is None or self.terminal is None:
                raise InadmissibleExactValue("mediated observation retains both endpoint signatures")
            if not isinstance(self.mediator_or_absence, HeldLabel) or self.mediator_or_absence.family != "mediating-record":
                raise InadmissibleExactValue("a non-direct observation requires an explicit retained mediator")
        else:
            raise InadmissibleExactValue("selection observation class was not generated")


def signature(state: str, multiplicity: int, inversion: str, axis: str) -> StateSignature:
    return StateSignature(
        HeldLabel("molecular-state", state),
        PositiveCount(multiplicity),
        HeldLabel("inversion-fibre", inversion),
        HeldLabel("axis-support", axis),
    )


def direct_observation_allowed(initial: StateSignature, terminal: StateSignature) -> bool:
    if initial.multiplicity != terminal.multiplicity:
        return False
    if (initial.axis.label, terminal.axis.label) not in AXIS_NEIGHBOURS:
        return False
    known = {"g", "u"}
    if initial.inversion.label in known and terminal.inversion.label in known:
        return initial.inversion.label != terminal.inversion.label
    return True


def classify_observation(
    initial: Optional[StateSignature],
    terminal: Optional[StateSignature],
    record: str,
    *,
    observed: bool = True,
    coupled: bool = False,
    mediator: Optional[str] = None,
) -> SelectionRecord:
    held_record = HeldLabel("selection-record", record)
    if not observed:
        return SelectionRecord(initial, None, CLOSED, EMPTY_ONE, held_record)
    if coupled:
        return SelectionRecord(initial, terminal, COUPLED, EMPTY_ONE, held_record)
    if initial is None or terminal is None:
        return SelectionRecord(initial, terminal, UNRESOLVED, EMPTY_ONE, held_record)
    if direct_observation_allowed(initial, terminal):
        return SelectionRecord(initial, terminal, DIRECT, EMPTY_ONE, held_record)
    if mediator is None:
        raise InadmissibleExactValue("observed non-direct relation must not erase its mediator requirement")
    return SelectionRecord(initial, terminal, MEDIATED, HeldLabel("mediating-record", mediator), held_record)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-QUANTUM-MEASUREMENT-001",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "answer-only-rule", "A selection answer without state endpoints erases the chemical carrier.", "retained-endpoint-signatures", "Every decision retains the exact endpoint signatures available to observation."),
    dimension("observation", "channel-independent-permission", "One universal yes/no label erases which observation operation was applied.", "declared-observation-class", "Direct, mediated, coupled and closed observations remain distinct."),
    dimension("multiplicity", "untracked-spin-support", "Changing a retained support count in one direct Fold action erases a distinction.", "direct-multiplicity-retention", "A direct observation retains the positive spin-support count."),
    dimension("inversion", "same-fibre-direct-image", "When both inversion fibres are known, an unchanged fibre supplies no direct observation distinction.", "known-inversion-fibre-change", "Known g/u endpoints occupy complementary held fibres in a direct observation."),
    dimension("axis", "arbitrary-axis-jump", "One observation action cannot cross more than one generated axis recurrence.", "same-or-neighbour-axis-support", "Direct observation changes axis support by at most one Fold successor."),
    dimension("mediation", "exception-erases-law", "Calling every observed exception direct destroys the closed distinction.", "non-direct-requires-retained-mediator", "A non-direct observed relation remains lawful only with its mediator or alternate channel retained."),
    dimension("absence", "numerical-zero-or-universal-forbidden", "An empty source cell is neither a number nor a universal prohibition.", "channel-closed-EmptyOne", "Absence closes only the declared observation coordinate as structural EmptyOne."),
    dimension("record", "selected-success-only", "Keeping only ordinary transitions hides couplings, absences and mediated cases.", "complete-adverse-inclusive-vector", "All direct, mediated, coupled, unresolved and closed records are retained."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    sg = signature("G", 1, "g", "Σ")
    pu = signature("C", 1, "u", "Π")
    dg = signature("J", 1, "g", "Δ")
    direct = classify_observation(sg, pu, "G-to-C")
    mediated = classify_observation(dg, signature("B", 1, "u", "Σ"), "J-to-B", mediator="uncoupling")
    closed = classify_observation(sg, None, "emission-closed", observed=False)
    erased_mediator_rejected = False
    try:
        classify_observation(dg, signature("B", 1, "u", "Σ"), "invalid-direct")
    except InadmissibleExactValue:
        erased_mediator_rejected = True
    return (
        ("direct", "One-step support change with retained multiplicity and complementary known inversion is direct.", direct.observation_class == DIRECT),
        ("mediated", "A two-step axis change retains the mediator and is not relabelled direct.", mediated.observation_class == MEDIATED),
        ("closed", "A channel-absent terminal is structural EmptyOne.", closed.mediator_or_absence is EMPTY_ONE),
        ("adverse", "Erasing the required mediator rejects.", erased_mediator_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "retained-endpoint-signatures__declared-observation-class__direct-multiplicity-retention__known-inversion-fibre-change__same-or-neighbour-axis-support__non-direct-requires-retained-mediator__channel-closed-EmptyOne__complete-adverse-inclusive-vector"


__all__ = (
    "CLOSED", "COUPLED", "DEPENDENCIES", "DIMENSIONS", "DIRECT", "EXACT_RESULT",
    "MEDIATED", "OPERATIONAL_WITNESSES", "SelectionRecord", "StateSignature", "UNRESOLVED",
    "classify_observation", "direct_observation_allowed", "signature",
)
