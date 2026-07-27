"""Fold-native aromatic/antiaromatic/nonaromatic distinction for ORG-004."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.chemistry.aromatic_recurrence_stability_law_v1 import (
    ExactAromaticRecurrence,
    append_complete_pair_layer,
    aromatic_recurrence,
    complete_ordered_pair_cells,
)
from sft.chemistry.multicentre_support_law_v1 import DelocalizedMolecularSupport, surface_cycle_support
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


COMPLETE_PLANE = HeldLabel("cycle-geometry-state", "complete-common-plane")
BROKEN_PLANE = HeldLabel("cycle-geometry-state", "out-of-plane-break")
COMPLETE_CONJUGATION = HeldLabel("cycle-support-state", "complete-conjugated-support")
BROKEN_CONJUGATION = HeldLabel("cycle-support-state", "broken-conjugated-support")
AROMATIC = HeldLabel("same-cycle-class", "closed-aromatic-recurrence")
ANTIAROMATIC = HeldLabel("same-cycle-class", "frustrated-antiaromatic-recurrence")
NONAROMATIC = HeldLabel("same-cycle-class", "broken-nonaromatic-recurrence")


RecurrenceSupport = Union[EmptyOne, PositiveCount]


@dataclass(frozen=True)
class ExactSameCycleAlternative:
    molecular_carrier: HeldLabel
    cycle: DelocalizedMolecularSupport
    geometry_state: HeldLabel
    support_state: HeldLabel
    recurrence_class: HeldLabel
    recurrence_support: RecurrenceSupport
    complete_pair_cell_layers: tuple[tuple[tuple[HeldLabel, HeldLabel], ...], ...]

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier" or self.cycle.molecular_carrier != self.molecular_carrier:
            raise InadmissibleExactValue("same-cycle classification requires one retained molecular carrier")
        if self.geometry_state not in (COMPLETE_PLANE, BROKEN_PLANE):
            raise InadmissibleExactValue("same-cycle geometry state is invalid")
        if self.support_state not in (COMPLETE_CONJUGATION, BROKEN_CONJUGATION):
            raise InadmissibleExactValue("same-cycle conjugation state is invalid")
        complete = complete_ordered_pair_cells()
        if any(layer != complete for layer in self.complete_pair_cell_layers):
            raise InadmissibleExactValue("every retained recurrence layer must contain all four ordered pair cells")
        if self.recurrence_class == AROMATIC:
            if (
                self.geometry_state != COMPLETE_PLANE
                or self.support_state != COMPLETE_CONJUGATION
                or not self.complete_pair_cell_layers
                or not isinstance(self.recurrence_support, PositiveCount)
                or self.recurrence_support.value != 2 + 4 * len(self.complete_pair_cell_layers)
            ):
                raise InadmissibleExactValue("aromatic class requires complete planar recurrence and its two-fibre return")
        elif self.recurrence_class == ANTIAROMATIC:
            if (
                self.geometry_state != COMPLETE_PLANE
                or self.support_state != COMPLETE_CONJUGATION
                or not self.complete_pair_cell_layers
                or not isinstance(self.recurrence_support, PositiveCount)
                or self.recurrence_support.value != 4 * len(self.complete_pair_cell_layers)
            ):
                raise InadmissibleExactValue("antiaromatic class requires complete planar support with frustrated return")
        elif self.recurrence_class == NONAROMATIC:
            if (
                self.geometry_state == COMPLETE_PLANE
                and self.support_state == COMPLETE_CONJUGATION
            ) or self.recurrence_support != EMPTY_ONE or self.complete_pair_cell_layers:
                raise InadmissibleExactValue("nonaromatic class requires a broken planar or conjugated recurrence and structural EmptyOne")
        else:
            raise InadmissibleExactValue("same-cycle recurrence class is invalid")


@dataclass(frozen=True)
class ExactSameCycleStabilityOrder:
    aromatic: ExactSameCycleAlternative
    nonaromatic: ExactSameCycleAlternative
    antiaromatic: ExactSameCycleAlternative
    aromatic_to_nonaligned_transfer: PositiveCount
    nonaligned_to_frustrated_transfer: PositiveCount

    def __post_init__(self) -> None:
        if len({row.cycle for row in (self.aromatic, self.nonaromatic, self.antiaromatic)}) != 1:
            raise InadmissibleExactValue("stability comparison requires the exact same molecular cycle")
        if (
            self.aromatic.recurrence_class != AROMATIC
            or self.nonaromatic.recurrence_class != NONAROMATIC
            or self.antiaromatic.recurrence_class != ANTIAROMATIC
        ):
            raise InadmissibleExactValue("same-cycle stability order has a changed class identity")
        if self.aromatic_to_nonaligned_transfer != PositiveCount(1) or self.nonaligned_to_frustrated_transfer != PositiveCount(1):
            raise InadmissibleExactValue("each adjacent same-cycle order step requires one positive distinction transfer")

    @property
    def exact_order(self) -> tuple[HeldLabel, HeldLabel, HeldLabel]:
        return (AROMATIC, NONAROMATIC, ANTIAROMATIC)


def aromatic_alternative(recurrence: ExactAromaticRecurrence) -> ExactSameCycleAlternative:
    return ExactSameCycleAlternative(
        recurrence.molecular_carrier,
        recurrence.cycle,
        COMPLETE_PLANE,
        COMPLETE_CONJUGATION,
        AROMATIC,
        recurrence.positive_support_count,
        recurrence.pair_cell_layers,
    )


def antiaromatic_alternative(cycle: DelocalizedMolecularSupport, positive_layers: PositiveCount) -> ExactSameCycleAlternative:
    layers = tuple(complete_ordered_pair_cells() for _ in range(positive_layers.value))
    return ExactSameCycleAlternative(
        cycle.molecular_carrier,
        cycle,
        COMPLETE_PLANE,
        COMPLETE_CONJUGATION,
        ANTIAROMATIC,
        PositiveCount(4 * positive_layers.value),
        layers,
    )


def nonaromatic_alternative(
    cycle: DelocalizedMolecularSupport,
    *,
    break_plane: bool,
    break_conjugation: bool,
) -> ExactSameCycleAlternative:
    if not break_plane and not break_conjugation:
        raise InadmissibleExactValue("nonaromatic alternative must retain an exact structural break")
    return ExactSameCycleAlternative(
        cycle.molecular_carrier,
        cycle,
        BROKEN_PLANE if break_plane else COMPLETE_PLANE,
        BROKEN_CONJUGATION if break_conjugation else COMPLETE_CONJUGATION,
        NONAROMATIC,
        EMPTY_ONE,
        (),
    )


def same_cycle_census(molecular_label: str, centre_labels: tuple[str, ...]) -> tuple[ExactSameCycleAlternative, ...]:
    recurrence = aromatic_recurrence(molecular_label, centre_labels, PositiveCount(1))
    cycle = recurrence.cycle
    return (
        aromatic_alternative(recurrence),
        nonaromatic_alternative(cycle, break_plane=True, break_conjugation=False),
        antiaromatic_alternative(cycle, PositiveCount(1)),
    )


def same_cycle_stability_order(census: tuple[ExactSameCycleAlternative, ...]) -> ExactSameCycleStabilityOrder:
    if len(census) != 3:
        raise InadmissibleExactValue("same-cycle census requires exactly three forced alternatives")
    return ExactSameCycleStabilityOrder(census[0], census[1], census[2], PositiveCount(1), PositiveCount(1))


def append_complete_layer(alternative: ExactSameCycleAlternative) -> ExactSameCycleAlternative:
    if alternative.recurrence_class == AROMATIC:
        recurrence = aromatic_recurrence(
            alternative.molecular_carrier.label,
            tuple(row.label for row in alternative.cycle.centres),
            PositiveCount(len(alternative.complete_pair_cell_layers)),
        )
        return aromatic_alternative(append_complete_pair_layer(recurrence))
    if alternative.recurrence_class == ANTIAROMATIC:
        return antiaromatic_alternative(
            alternative.cycle,
            PositiveCount(len(alternative.complete_pair_cell_layers) + 1),
        )
    return alternative


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-CONJUGATED-SUPPORT-001",
    "SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "different-or-name-only-carriers", "Different carriers cannot establish alternatives of the same cycle.", "one-retained-same-cycle-carrier", "Every alternative retains one identical molecular carrier and cycle incidence graph."),
    dimension("census", "selected-favourable-category", "Selecting a familiar label omits lawful same-cycle alternatives.", "complete-three-class-census", "Closed, frustrated and structurally broken recurrence are all generated and retained."),
    dimension("geometry", "planarity-assumed-or-erased", "Erasing geometry merges a frustrated planar recurrence with a recurrence avoided by an out-of-plane break.", "held-planar-or-broken-geometry", "Complete-plane and out-of-plane-break remain exact held alternatives."),
    dimension("support", "conjugation-name-only", "A name does not distinguish complete support from a broken recurrence path.", "held-complete-or-broken-conjugation", "Every incidence either belongs to complete conjugated support or retains the exact break."),
    dimension("boundary", "electron-count-label-imported", "An imported count label does not derive return, frustration or structural absence.", "closed-frustrated-or-EmptyOne-return", "The boundary is a complete two-fibre return, a complete four-cell frustration, or structural EmptyOne after a break."),
    dimension("order", "measured-energy-selected-order", "Measured values cannot choose which structural alternative is stable.", "positive-two-step-stability-order", "Opening closure and then imposing frustration each require one positive distinction transfer."),
    dimension("observation", "selected-or-preopened-comparison", "A selected outcome can conceal an adverse same-cycle alternative.", "value-free-complete-comparative-seal", "Every terminology, geometry and energy surface is sealed by identity before outcome comparison."),
    dimension("extension", "named-ring-or-extra-count-rule", "A species exception or imported count recurrence adds a free selector.", "complete-four-cell-successors-no-extra-rule", "Aromatic and antiaromatic layers each add all four pair cells; broken recurrence remains structural EmptyOne."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    census = same_cycle_census("carrier", ("a", "b", "c", "d"))
    order = same_cycle_stability_order(census)
    aromatic_next = append_complete_layer(census[0])
    anti_next = append_complete_layer(census[2])
    inconsistent_rejected = missing_break_rejected = numerical_zero_rejected = False
    try:
        ExactSameCycleAlternative(
            census[2].molecular_carrier,
            census[2].cycle,
            BROKEN_PLANE,
            COMPLETE_CONJUGATION,
            ANTIAROMATIC,
            PositiveCount(4),
            (complete_ordered_pair_cells(),),
        )
    except InadmissibleExactValue:
        inconsistent_rejected = True
    try:
        nonaromatic_alternative(census[1].cycle, break_plane=False, break_conjugation=False)
    except InadmissibleExactValue:
        missing_break_rejected = True
    try:
        PositiveCount(0)
    except InadmissibleExactValue:
        numerical_zero_rejected = True
    return (
        ("complete-three-class-census", "Closed, broken and frustrated same-cycle alternatives are retained exactly once.", tuple(row.recurrence_class for row in census) == (AROMATIC, NONAROMATIC, ANTIAROMATIC)),
        ("exact-support-boundaries", "The base supports are six, structural EmptyOne and four without numerical zero.", census[0].recurrence_support == PositiveCount(6) and census[1].recurrence_support == EMPTY_ONE and census[2].recurrence_support == PositiveCount(4)),
        ("positive-stability-order", "Closed recurrence precedes broken recurrence, which precedes frustrated recurrence.", order.exact_order == (AROMATIC, NONAROMATIC, ANTIAROMATIC)),
        ("depth-independent-successor", "The complete four-cell successor advances six to ten and four to eight while broken recurrence stays EmptyOne.", aromatic_next.recurrence_support == PositiveCount(10) and anti_next.recurrence_support == PositiveCount(8) and append_complete_layer(census[1]).recurrence_support == EMPTY_ONE),
        ("inconsistent-class-control", "A broken plane cannot be relabelled antiaromatic.", inconsistent_rejected),
        ("missing-break-control", "Nonaromatic classification without a structural break rejects.", missing_break_rejected),
        ("numerical-zero-control", "Numerical zero cannot replace structural EmptyOne.", numerical_zero_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "one-retained-same-cycle-carrier__complete-three-class-census__held-planar-or-broken-geometry__"
    "held-complete-or-broken-conjugation__closed-frustrated-or-EmptyOne-return__"
    "positive-two-step-stability-order__value-free-complete-comparative-seal__"
    "complete-four-cell-successors-no-extra-rule"
)


__all__ = (
    "ANTIAROMATIC",
    "AROMATIC",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactSameCycleAlternative",
    "ExactSameCycleStabilityOrder",
    "NONAROMATIC",
    "OPERATIONAL_WITNESSES",
    "append_complete_layer",
    "same_cycle_census",
    "same_cycle_stability_order",
)
