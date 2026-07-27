"""Fold-native exact dihedral and torsional-state law for Chemistry PROP-004.

A dihedral is an ordered four-site carrier on a generated periodic cycle.  Its
direction is a held orientation, never a signed proof number.  At an ``n``
sector observation boundary, the first path position is structural EmptyOne;
each successor retains one further positive sector part; and the terminal
successor is the recurrent One.  Torsional conformers and barriers are forced
by complete cyclic neighbour order.  Barrier magnitude is ordered positive
Take from a barrier state to an adjacent conformer minimum.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union

from sft.claim_evidence import PositiveRatio
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


ExactCoordinate = Union[EmptyOne, PositiveRatio]
ExactHeight = Union[EmptyOne, PositiveRatio]


def generated_dihedral_coordinate(
    path_position: PositiveCount,
    sector_count: PositiveCount,
) -> ExactCoordinate:
    """Generate an exact path coordinate without installing numerical zero."""

    if not isinstance(path_position, PositiveCount) or not isinstance(sector_count, PositiveCount):
        raise InadmissibleExactValue("dihedral position and sector support must be positive generated counts")
    terminal_position = sector_count.value + 1
    if path_position.value > terminal_position:
        raise InadmissibleExactValue("dihedral position exceeds the complete registered recurrence")
    if path_position.value == 1:
        return EMPTY_ONE
    predecessor_count = path_position.value - 1
    return PositiveRatio.from_pair(predecessor_count, sector_count.value)


def ordered_positive_barrier_take(higher: ExactHeight, lower: ExactHeight) -> PositiveRatio:
    """Take a lower torsional state from a higher one without signed residue."""

    if higher is EMPTY_ONE or not isinstance(higher, PositiveRatio):
        raise InadmissibleExactValue("a torsional barrier must be an exact positive height")
    if lower is EMPTY_ONE:
        return higher
    if not isinstance(lower, PositiveRatio) or not higher.fraction > lower.fraction:
        raise InadmissibleExactValue("barrier Take requires a strictly lower retained state")
    difference = higher.fraction - lower.fraction
    return PositiveRatio.from_pair(difference.numerator, difference.denominator)


@dataclass(frozen=True)
class DihedralCarrier:
    molecule: HeldLabel
    molecular_state: HeldLabel
    ordered_atoms: tuple[HeldLabel, HeldLabel, HeldLabel, HeldLabel]
    rotor_type: HeldLabel
    orientation: HeldLabel

    def __post_init__(self) -> None:
        if self.molecule.family != "molecular-carrier" or self.molecular_state.family != "molecular-state":
            raise InadmissibleExactValue("dihedral carrier must retain molecule and molecular state")
        if len(self.ordered_atoms) != 4 or any(atom.family != "ordered-torsion-atom" for atom in self.ordered_atoms):
            raise InadmissibleExactValue("dihedral carrier requires exactly four ordered atom labels")
        if len(set(self.ordered_atoms)) != 4:
            raise InadmissibleExactValue("dihedral carrier atom positions must remain distinguishable")
        if self.rotor_type.family != "rotor-type" or self.orientation.family != "held-orientation":
            raise InadmissibleExactValue("rotor type and orientation must remain held")


@dataclass(frozen=True)
class TorsionNode:
    carrier: DihedralCarrier
    path_position: PositiveCount
    coordinate: ExactCoordinate
    height: ExactHeight
    record: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.coordinate, (EmptyOne, PositiveRatio)):
            raise InadmissibleExactValue("torsion coordinate must be EmptyOne or an exact positive part")
        if not isinstance(self.height, (EmptyOne, PositiveRatio)):
            raise InadmissibleExactValue("torsion height must be EmptyOne or an exact positive ratio")
        if self.record.family != "torsion-record":
            raise InadmissibleExactValue("torsion node must retain its source record")


def _less(left: ExactHeight, right: ExactHeight) -> bool:
    if left is EMPTY_ONE:
        return right is not EMPTY_ONE
    if right is EMPTY_ONE:
        return False
    return left.fraction < right.fraction


@dataclass(frozen=True)
class TorsionCycle:
    sector_count: PositiveCount
    nodes: tuple[TorsionNode, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.sector_count, PositiveCount):
            raise InadmissibleExactValue("torsion cycle requires positive sector support")
        if len(self.nodes) != self.sector_count.value + 1:
            raise InadmissibleExactValue("torsion cycle must include every sector and one recurrence endpoint")
        if len({node.carrier for node in self.nodes}) != 1:
            raise InadmissibleExactValue("one torsion cycle requires one retained ordered carrier")
        for expected_position, node in enumerate(self.nodes, start=1):
            if node.path_position != PositiveCount(expected_position):
                raise InadmissibleExactValue("torsion path position is missing or displaced")
            if node.coordinate != generated_dihedral_coordinate(node.path_position, self.sector_count):
                raise InadmissibleExactValue("torsion coordinate does not follow the generated cycle")
        if self.nodes[0].coordinate is not EMPTY_ONE:
            raise InadmissibleExactValue("torsion cycle must begin at structural EmptyOne")
        if not isinstance(self.nodes[-1].coordinate, PositiveRatio) or self.nodes[-1].coordinate.fraction != Fraction(1, 1):
            raise InadmissibleExactValue("torsion cycle must terminate at the recurrent One")
        if self.nodes[-1].height != self.nodes[0].height:
            raise InadmissibleExactValue("recurrent torsion endpoint must retain the initial state height")

    @property
    def unique_nodes(self) -> tuple[TorsionNode, ...]:
        return self.nodes[:-1]

    def local_conformer_positions(self) -> tuple[PositiveCount, ...]:
        unique = self.unique_nodes
        result = []
        for index, node in enumerate(unique):
            left, right = unique[(index - 1) % len(unique)], unique[(index + 1) % len(unique)]
            if _less(node.height, left.height) and _less(node.height, right.height):
                result.append(node.path_position)
        return tuple(result)

    def local_barrier_positions(self) -> tuple[PositiveCount, ...]:
        unique = self.unique_nodes
        result = []
        for index, node in enumerate(unique):
            left, right = unique[(index - 1) % len(unique)], unique[(index + 1) % len(unique)]
            if _less(left.height, node.height) and _less(right.height, node.height):
                result.append(node.path_position)
        return tuple(result)

    def barrier_transitions(self) -> tuple[tuple[PositiveCount, PositiveCount, PositiveRatio], ...]:
        unique = self.unique_nodes
        conformer_indices = {
            position.value - 1 for position in self.local_conformer_positions()
        }
        transitions = []
        for barrier_position in self.local_barrier_positions():
            barrier_index = barrier_position.value - 1
            for direction in (-1, 1):
                cursor = barrier_index
                for _ in range(len(unique)):
                    cursor = (cursor + direction) % len(unique)
                    if cursor in conformer_indices:
                        transitions.append((
                            barrier_position, unique[cursor].path_position,
                            ordered_positive_barrier_take(unique[barrier_index].height, unique[cursor].height),
                        ))
                        break
                else:
                    raise InadmissibleExactValue("torsional barrier has no adjacent conformer minimum")
        return tuple(transitions)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-MOLECULAR-BOND-ANGLE-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "unordered-or-three-site-angle", "A dihedral cannot be identified without four ordered sites.",
        "named-ordered-four-site-carrier", "Molecule, state, rotor and all four ordered atom sites remain held.",
    ),
    dimension(
        "orientation", "signed-conventional-angle", "A signed scalar imports negative proof magnitude.",
        "held-cycle-orientation", "Direction is a retained label on one exact periodic path.",
    ),
    dimension(
        "coordinate", "continuum-rotation-coordinate", "A continuum coordinate imports ungenerated positions.",
        "generated-sector-successor-coordinate", "EmptyOne, positive sector successors and recurrent One exhaust the registered cycle.",
    ),
    dimension(
        "state", "named-conformer-without-neighbours", "A conformer name without complete neighbours cannot force local stability.",
        "complete-neighbour-conformer-state", "A conformer is lower than both retained neighbouring generated states.",
    ),
    dimension(
        "barrier", "imported-saddle-or-signed-difference", "An imported saddle equation or signed residue is outside the exact domain.",
        "local-barrier-and-ordered-positive-Take", "A barrier is higher than both neighbours and Takes each adjacent conformer height positively.",
    ),
    dimension(
        "recurrence", "duplicated-terminal-configuration", "Treating the complete turn endpoint as new duplicates one state.",
        "terminal-One-identifies-anchor-class", "The recurrent One retains the anchor configuration and height.",
    ),
    dimension(
        "prediction", "angle-or-energy-target-readable", "Readable source values could select the coordinate or state result.",
        "value-free-coordinate-and-operation-seal", "Only identities, sector structure and exact operations seal before values open.",
    ),
    dimension(
        "record", "selected-extrema-or-one-rotor", "A selected subset hides ordinary, adverse or second-rotor rows.",
        "complete-two-rotor-fifty-row-vector", "Both ordered rotors and every source row remain in the empirical surface.",
    ),
)


EXACT_RESULT = (
    "named-ordered-four-site-carrier__held-cycle-orientation__generated-sector-successor-coordinate__"
    "complete-neighbour-conformer-state__local-barrier-and-ordered-positive-Take__"
    "terminal-One-identifies-anchor-class__value-free-coordinate-and-operation-seal__"
    "complete-two-rotor-fifty-row-vector"
)


def _synthetic_carrier() -> DihedralCarrier:
    return DihedralCarrier(
        HeldLabel("molecular-carrier", "synthetic-cycle"), HeldLabel("molecular-state", "witness-state"),
        tuple(HeldLabel("ordered-torsion-atom", label) for label in ("A", "B", "C", "D")),
        HeldLabel("rotor-type", "witness-rotor"), HeldLabel("held-orientation", "forward-cycle"),
    )


def _witness_cycle() -> TorsionCycle:
    carrier = _synthetic_carrier()
    heights: tuple[ExactHeight, ...] = (
        EMPTY_ONE, PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(5, 1),
        EMPTY_ONE, PositiveRatio.from_pair(3, 1), PositiveRatio.from_pair(6, 1), EMPTY_ONE,
    )
    sectors = PositiveCount(6)
    nodes = tuple(
        TorsionNode(
            carrier, PositiveCount(position), generated_dihedral_coordinate(PositiveCount(position), sectors),
            height, HeldLabel("torsion-record", f"witness-{position}"),
        )
        for position, height in enumerate(heights, start=1)
    )
    return TorsionCycle(sectors, nodes)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    cycle = _witness_cycle()
    reverse_rejected = False
    try:
        ordered_positive_barrier_take(PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(5, 1))
    except InadmissibleExactValue:
        reverse_rejected = True
    return (
        ("coordinate-cycle", "Six positive sectors generate EmptyOne, exact parts and the recurrent One.",
         cycle.nodes[0].coordinate is EMPTY_ONE and cycle.nodes[-1].coordinate.fraction == Fraction(1, 1)),
        ("conformer-barrier-order", "Complete cyclic neighbours force two conformers and two barriers.",
         len(cycle.local_conformer_positions()) == 2 and len(cycle.local_barrier_positions()) == 2),
        ("barrier-transitions", "Each barrier Takes its two adjacent conformer heights exactly.",
         len(cycle.barrier_transitions()) == 4 and all(item[2].fraction > 0 for item in cycle.barrier_transitions())),
        ("orientation", "Reversing ordered Take halts instead of creating a negative magnitude.", reverse_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "DihedralCarrier", "EXACT_RESULT", "ExactCoordinate", "ExactHeight",
    "OPERATIONAL_WITNESSES", "TorsionCycle", "TorsionNode", "generated_dihedral_coordinate",
    "ordered_positive_barrier_take",
)
