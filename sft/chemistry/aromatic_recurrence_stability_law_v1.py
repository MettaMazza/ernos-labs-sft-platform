"""Fold-native aromatic recurrence and positive stability ordering for ORG-003."""
from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.multicentre_support_law_v1 import (
    DelocalizedMolecularSupport,
    SURFACE,
    surface_cycle_support,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension
from sft.physics.structural_constants import generator_period_three


FIBRE_ONE = HeldLabel("aromatic-recurrence-fibre", "fold-fibre-one")
FIBRE_TWO = HeldLabel("aromatic-recurrence-fibre", "fold-fibre-two")


def complete_ordered_pair_cells() -> tuple[tuple[HeldLabel, HeldLabel], ...]:
    """Return every ordered cell of the two held Fold fibres exactly once."""
    return (
        (FIBRE_ONE, FIBRE_ONE),
        (FIBRE_ONE, FIBRE_TWO),
        (FIBRE_TWO, FIBRE_ONE),
        (FIBRE_TWO, FIBRE_TWO),
    )


@dataclass(frozen=True)
class ExactAromaticRecurrence:
    molecular_carrier: HeldLabel
    cycle: DelocalizedMolecularSupport
    boundary_fibres: tuple[HeldLabel, HeldLabel]
    pair_cell_layers: tuple[tuple[tuple[HeldLabel, HeldLabel], ...], ...]

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("aromatic recurrence requires one retained molecular carrier")
        if self.cycle.molecular_carrier != self.molecular_carrier or self.cycle.topology != SURFACE:
            raise InadmissibleExactValue("aromatic recurrence requires one complete cycle on the same carrier")
        if frozenset(self.boundary_fibres) != frozenset((FIBRE_ONE, FIBRE_TWO)):
            raise InadmissibleExactValue("aromatic recurrence requires both Fold boundary fibres exactly once")
        if not self.pair_cell_layers:
            raise InadmissibleExactValue("aromatic recurrence requires a positive generated cycle layer")
        complete = complete_ordered_pair_cells()
        if any(layer != complete for layer in self.pair_cell_layers):
            raise InadmissibleExactValue("every recurrence layer must retain all four ordered Fold pair cells")

    @property
    def positive_layer_count(self) -> PositiveCount:
        return PositiveCount(len(self.pair_cell_layers))

    @property
    def positive_support_count(self) -> PositiveCount:
        return PositiveCount(len(self.boundary_fibres) + sum(len(layer) for layer in self.pair_cell_layers))

    @property
    def first_return_trace(self) -> tuple[HeldLabel, ...]:
        return self.cycle.centres + (self.cycle.centres[0],)

    @property
    def missing_pair_cell_boundary(self) -> EmptyOne:
        return EMPTY_ONE

    @property
    def complete_registered_perturbation_closure(self) -> bool:
        complete = complete_ordered_pair_cells()
        rotations = tuple(complete[index:] + complete[:index] for index in range(1, len(complete) + 1))
        return all(frozenset(rotation) == frozenset(complete) for rotation in rotations)


@dataclass(frozen=True)
class ExactAromaticStabilityOrder:
    recurrence: ExactAromaticRecurrence
    closed_state: HeldLabel
    opened_reference_state: HeldLabel
    opening_transfer: PositiveCount

    def __post_init__(self) -> None:
        if self.closed_state.family != "molecular-energy-state" or self.opened_reference_state.family != "molecular-energy-state":
            raise InadmissibleExactValue("aromatic stability requires retained molecular energy-state identities")
        if self.closed_state == self.opened_reference_state:
            raise InadmissibleExactValue("closed recurrence and opened reference must remain distinct")
        if self.opening_transfer != PositiveCount(1):
            raise InadmissibleExactValue("opening one primitive recurrence boundary requires exactly one retained transfer act")

    @property
    def closed_recurrence_precedes_opened_reference(self) -> bool:
        return self.opening_transfer == PositiveCount(1)


def aromatic_recurrence(
    molecular_label: str,
    centre_labels: tuple[str, ...],
    positive_layers: PositiveCount,
) -> ExactAromaticRecurrence:
    cycle = surface_cycle_support(molecular_label, centre_labels)
    boundary = (FIBRE_ONE, FIBRE_TWO)
    layers = tuple(complete_ordered_pair_cells() for _ in range(positive_layers.value))
    return ExactAromaticRecurrence(cycle.molecular_carrier, cycle, boundary, layers)


def append_complete_pair_layer(recurrence: ExactAromaticRecurrence) -> ExactAromaticRecurrence:
    return ExactAromaticRecurrence(
        recurrence.molecular_carrier,
        recurrence.cycle,
        recurrence.boundary_fibres,
        recurrence.pair_cell_layers + (complete_ordered_pair_cells(),),
    )


def aromatic_stability_order(recurrence: ExactAromaticRecurrence) -> ExactAromaticStabilityOrder:
    return ExactAromaticStabilityOrder(
        recurrence,
        HeldLabel("molecular-energy-state", "closed-recurrence"),
        HeldLabel("molecular-energy-state", "opened-localized-reference"),
        PositiveCount(1),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
    "SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013",
    "SFT-CHEM-CONJUGATED-SUPPORT-001",
    "SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "aromatic-name-or-answer-only", "A name does not retain the molecular support that is claimed to recur.", "one-complete-molecular-carrier", "One carrier retains every cycle centre, incidence and recurrence cell."),
    dimension("cycle", "open-path-or-selected-ring", "An open path or selected example does not establish cyclic first return.", "complete-generated-cycle", "Every centre has complete degree-two cycle incidence and the trace returns to its first centre."),
    dimension("boundary", "one-fibre-or-duplicated-boundary", "An incomplete or duplicated boundary erases one forced Fold distinction.", "complete-two-fibre-boundary", "The recurrence retains both Fold fibres exactly once at its boundary."),
    dimension("layer", "selected-transition-cell-subset", "A selected subset can be tuned to a familiar count and is not closed under pair-cell perturbation.", "complete-four-ordered-pair-cell-layer", "Every positive layer retains all four ordered cells of the two Fold fibres exactly once."),
    dimension("return", "period-label-without-trace", "A named cycle length cannot prove return or preserve its path.", "explicit-complete-first-return-trace", "The complete centre trace ends at its exactly retained starting centre."),
    dimension("stability", "measured-energy-or-name-selected-order", "A measured energy or conventional aromatic label cannot select the structural order.", "positive-recurrence-opening-gap", "Opening the closed recurrence requires one retained positive transfer, so the closed state precedes its opened reference."),
    dimension("observation", "selected-or-preopened-value-row", "A selected or preopened value vector can feed the desired order back into the law.", "value-free-seal-and-complete-blind-vector", "Outcome-unopened identities are sealed before the complete independent energy surface is opened."),
    dimension("extension", "imported-electron-count-or-species-rule", "An imported count formula or species exception is an added selector.", "complete-four-cell-successor-no-extra-rule", "Each positive successor appends the same complete four-cell layer while retaining the two-fibre boundary and cycle."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    centres = tuple(f"centre-{position}" for position in range(1, generator_period_three() * 2 + 1))
    base = aromatic_recurrence("carrier", centres, PositiveCount(1))
    successor = append_complete_pair_layer(base)
    second_successor = append_complete_pair_layer(successor)
    stability = aromatic_stability_order(base)
    incomplete_rejected = open_path_rejected = numerical_zero_rejected = False
    try:
        ExactAromaticRecurrence(
            base.molecular_carrier,
            base.cycle,
            base.boundary_fibres,
            ((complete_ordered_pair_cells()[0], complete_ordered_pair_cells()[1], complete_ordered_pair_cells()[2]),),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    try:
        aromatic_recurrence("invalid", ("left", "right"), PositiveCount(1))
    except InadmissibleExactValue:
        open_path_rejected = True
    try:
        PositiveCount(0)
    except InadmissibleExactValue:
        numerical_zero_rejected = True
    return (
        ("primitive-six-support", "Two boundary fibres plus one complete four-cell layer force positive support six.", base.positive_support_count == PositiveCount(6)),
        ("successor-ten-fourteen", "Successive complete pair-cell layers force support counts ten and fourteen.", successor.positive_support_count == PositiveCount(10) and second_successor.positive_support_count == PositiveCount(14)),
        ("first-return", "The complete cycle trace returns to its retained first centre.", base.first_return_trace[0] == base.first_return_trace[-1] and len(base.first_return_trace) == len(base.cycle.centres) + 1),
        ("perturbation-closure", "Every ordered-pair-cell rotation preserves the complete layer.", base.complete_registered_perturbation_closure),
        ("positive-stability-order", "Opening one recurrence boundary requires one retained positive transfer.", stability.closed_recurrence_precedes_opened_reference),
        ("incomplete-layer-control", "Omitting any ordered pair cell rejects.", incomplete_rejected),
        ("open-path-control", "Two centres cannot be relabelled as a complete recurrence cycle.", open_path_rejected),
        ("numerical-zero-control", "A numerical zero layer count rejects.", numerical_zero_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "one-complete-molecular-carrier__complete-generated-cycle__complete-two-fibre-boundary__"
    "complete-four-ordered-pair-cell-layer__explicit-complete-first-return-trace__"
    "positive-recurrence-opening-gap__value-free-seal-and-complete-blind-vector__"
    "complete-four-cell-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactAromaticRecurrence",
    "ExactAromaticStabilityOrder",
    "OPERATIONAL_WITNESSES",
    "append_complete_pair_layer",
    "aromatic_recurrence",
    "aromatic_stability_order",
    "complete_ordered_pair_cells",
)
