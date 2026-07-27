"""Fold-native exact finite ordering of molecular electronic states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


OrderPosition = Union[EmptyOne, PositiveCount]


@dataclass(frozen=True)
class OrderedMolecularState:
    molecular_carrier: HeldLabel
    state_identity: HeldLabel
    order_position: OrderPosition
    support_identity: HeldLabel

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("ordered state requires one molecular carrier")
        if self.state_identity.family != "molecular-electronic-state":
            raise InadmissibleExactValue("ordered state requires retained electronic-state identity")
        if not isinstance(self.order_position, (EmptyOne, PositiveCount)):
            raise InadmissibleExactValue("state position is structural least One or a positive successor")
        if self.support_identity.family != "molecular-support":
            raise InadmissibleExactValue("state order must retain its complete molecular support")


@dataclass(frozen=True)
class ExactFiniteStateOrder:
    molecular_carrier: HeldLabel
    states: tuple[OrderedMolecularState, ...]

    def __post_init__(self) -> None:
        if not self.states or any(row.molecular_carrier != self.molecular_carrier for row in self.states):
            raise InadmissibleExactValue("finite state order requires positive support on one molecule")
        identities = tuple(row.state_identity for row in self.states)
        if len(set(identities)) != len(identities):
            raise InadmissibleExactValue("state order cannot duplicate a state identity")
        grounds = tuple(row for row in self.states if row.order_position == EMPTY_ONE)
        if len(grounds) != 1:
            raise InadmissibleExactValue("finite molecular state order requires one structural least state")
        successors = sorted(
            row.order_position.value
            for row in self.states
            if isinstance(row.order_position, PositiveCount)
        )
        if successors != list(range(1, len(self.states))):
            raise InadmissibleExactValue("excited states must exhaust the positive successor positions exactly once")

    @property
    def ground_state(self) -> OrderedMolecularState:
        return next(row for row in self.states if row.order_position == EMPTY_ONE)


def build_exact_state_order(molecular_label: str, ordered_state_labels: tuple[str, ...]) -> ExactFiniteStateOrder:
    if not ordered_state_labels:
        raise InadmissibleExactValue("state order requires positive finite support")
    carrier = HeldLabel("molecular-carrier", molecular_label)
    rows = tuple(
        OrderedMolecularState(
            carrier,
            HeldLabel("molecular-electronic-state", label),
            EMPTY_ONE if position == 1 else PositiveCount(position - 1),
            HeldLabel("molecular-support", label + "-support"),
        )
        for position, label in enumerate(ordered_state_labels, start=1)
    )
    return ExactFiniteStateOrder(carrier, rows)


def precedes(left: OrderedMolecularState, right: OrderedMolecularState) -> bool:
    if left.molecular_carrier != right.molecular_carrier:
        raise InadmissibleExactValue("state comparison requires the same molecular carrier")
    if left.order_position == EMPTY_ONE:
        return right.order_position != EMPTY_ONE
    if right.order_position == EMPTY_ONE:
        return False
    return left.order_position.value < right.order_position.value


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "cross-molecule-state-list", "States from different carriers have no common declared molecular order.", "one-molecule-state-support", "Every ordered state retains the same declared molecular composition and geometry."),
    dimension("identity", "energy-only-anonymous-row", "An anonymous energy cannot preserve which electronic support carries it.", "state-and-support-identity", "Every order position retains exact state and molecular-support identities."),
    dimension("least", "numerical-zero-ground", "Numerical zero imports a forbidden proof magnitude and does not establish structural leastness.", "structural-empty-One-ground", "The unique least state is the structural empty-One boundary of the finite order."),
    dimension("excitation", "signed-energy-displacement", "A signed displacement imports negative proof quantities.", "positive-successor-excitation", "Every excited state is a positive successor beyond the structural least state."),
    dimension("order", "partial-selected-comparison", "Selected comparisons cannot establish a complete finite state order.", "complete-finite-total-order", "Every distinct state pair is comparable exactly once at the declared boundary."),
    dimension("gap", "unretained-transition-gap", "Erasing the positive separation loses transition and reconstruction information.", "retained-positive-order-gap", "Every higher/lower pair retains a positive counted separation."),
    dimension("record", "ordered-labels-without-trace", "A label list without support and observation trace cannot reproduce the order.", "complete-state-order-record", "Carrier, state identity, support, positions and comparisons remain auditable."),
    dimension("extension", "species-energy-lookup-rule", "A species lookup or measured energy in generation lets the target select the law.", "no-extra-rule", "The same least-plus-positive-successor law applies to every finite molecular state support."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    order = build_exact_state_order("molecule", ("ground", "first-excited", "second-excited"))
    duplicate_ground_rejected = False
    try:
        carrier = HeldLabel("molecular-carrier", "bad")
        ExactFiniteStateOrder(
            carrier,
            (
                OrderedMolecularState(carrier, HeldLabel("molecular-electronic-state", "a"), EMPTY_ONE, HeldLabel("molecular-support", "a")),
                OrderedMolecularState(carrier, HeldLabel("molecular-electronic-state", "b"), EMPTY_ONE, HeldLabel("molecular-support", "b")),
            ),
        )
    except InadmissibleExactValue:
        duplicate_ground_rejected = True
    missing_successor_rejected = False
    try:
        carrier = HeldLabel("molecular-carrier", "bad")
        ExactFiniteStateOrder(
            carrier,
            (
                OrderedMolecularState(carrier, HeldLabel("molecular-electronic-state", "a"), EMPTY_ONE, HeldLabel("molecular-support", "a")),
                OrderedMolecularState(carrier, HeldLabel("molecular-electronic-state", "b"), PositiveCount(2), HeldLabel("molecular-support", "b")),
            ),
        )
    except InadmissibleExactValue:
        missing_successor_rejected = True
    return (
        ("unique-structural-ground", "Exactly one state occupies the structural least boundary.", order.ground_state.state_identity.label == "ground"),
        ("positive-excitation-order", "Each excited state occupies the next positive successor position.", precedes(order.states[0], order.states[1]) and precedes(order.states[1], order.states[2])),
        ("duplicate-ground-control", "A second structural least state rejects.", duplicate_ground_rejected),
        ("missing-successor-control", "A finite order with a skipped successor rejects.", missing_successor_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-molecule-state-support__state-and-support-identity__structural-empty-One-ground__positive-successor-excitation__complete-finite-total-order__retained-positive-order-gap__complete-state-order-record__no-extra-rule"


__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactFiniteStateOrder", "OPERATIONAL_WITNESSES", "OrderedMolecularState", "build_exact_state_order", "precedes")
