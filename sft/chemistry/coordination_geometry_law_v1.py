"""Fold-native coordination geometry for Chemistry INORG-004."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.chemistry.coordination_entity_law_v1 import (
    CompleteCoordinationEntity,
    RetainedCoordinationAttachment,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


OrientationCell = Union[HeldLabel, EmptyOne]


@dataclass(frozen=True)
class HeldCoordinationPosition:
    """One direct ligand occurrence held in the three generated Fold axes."""

    attachment_ordinal: PositiveCount
    ligand_occurrence: HeldLabel
    orientation_word: tuple[OrientationCell, OrientationCell, OrientationCell]

    def __post_init__(self) -> None:
        if self.ligand_occurrence.family != "coordination-ligand-occurrence":
            raise InadmissibleExactValue("coordination position requires one retained ligand occurrence")
        if len(self.orientation_word) != 3:
            raise InadmissibleExactValue("coordination orientation requires exactly three generated axes")
        if any(
            not isinstance(cell, (HeldLabel, EmptyOne))
            or (isinstance(cell, HeldLabel) and cell.family != "fold-orientation-fibre")
            for cell in self.orientation_word
        ):
            raise InadmissibleExactValue("orientation cells must be held Fold fibres or structural EmptyOne")
        if all(isinstance(cell, EmptyOne) for cell in self.orientation_word):
            raise InadmissibleExactValue("a ligand occurrence cannot occupy the central EmptyOne position")


@dataclass(frozen=True)
class HeldCoordinationAdjacency:
    first_ligand_occurrence: HeldLabel
    second_ligand_occurrence: HeldLabel
    adjacency_trace: HeldLabel

    def __post_init__(self) -> None:
        if (
            self.first_ligand_occurrence.family != "coordination-ligand-occurrence"
            or self.second_ligand_occurrence.family != "coordination-ligand-occurrence"
            or self.first_ligand_occurrence == self.second_ligand_occurrence
        ):
            raise InadmissibleExactValue("coordination adjacency requires two distinct ligand occurrences")
        if self.adjacency_trace.family != "coordination-boundary-adjacency":
            raise InadmissibleExactValue("coordination adjacency requires a retained boundary trace")


@dataclass(frozen=True)
class CompleteCoordinationGeometry:
    central_occurrence: HeldLabel
    ordered_positions: tuple[HeldCoordinationPosition, ...]
    ordered_adjacencies: tuple[HeldCoordinationAdjacency, ...]

    def __post_init__(self) -> None:
        if self.central_occurrence.family != "coordination-central-occurrence":
            raise InadmissibleExactValue("coordination geometry requires one retained central occurrence")
        if not self.ordered_positions:
            raise InadmissibleExactValue("coordination geometry requires positive direct-position support")
        ordinals = tuple(row.attachment_ordinal.value for row in self.ordered_positions)
        if ordinals != tuple(range(1, len(self.ordered_positions) + 1)):
            raise InadmissibleExactValue("coordination positions require complete successor order")
        ligands = tuple(row.ligand_occurrence for row in self.ordered_positions)
        if len(set(ligands)) != len(ligands):
            raise InadmissibleExactValue("coordination position occurrences cannot collapse")
        if len({row.orientation_word for row in self.ordered_positions}) != len(self.ordered_positions):
            raise InadmissibleExactValue("distinct ligand occurrences require distinct held orientations")
        permitted = set(ligands)
        unordered_pairs = []
        for edge in self.ordered_adjacencies:
            if edge.first_ligand_occurrence not in permitted or edge.second_ligand_occurrence not in permitted:
                raise InadmissibleExactValue("boundary adjacency cannot name an occurrence outside the geometry")
            unordered_pairs.append(frozenset((edge.first_ligand_occurrence, edge.second_ligand_occurrence)))
        if len(set(unordered_pairs)) != len(unordered_pairs):
            raise InadmissibleExactValue("coordination boundary adjacencies cannot duplicate an edge")


@dataclass(frozen=True)
class ExactCoordinationGeometryRecord:
    central_occurrence: HeldLabel
    positive_coordination_count: PositiveCount
    ordered_positions: tuple[HeldCoordinationPosition, ...]
    ordered_adjacencies: tuple[HeldCoordinationAdjacency, ...]
    generated_space_rank: PositiveCount
    boundary_rank: PositiveCount
    exact_geometry_signature: tuple[object, ...]


def forced_coordination_geometry(
    entity: CompleteCoordinationEntity,
    geometry: CompleteCoordinationGeometry,
) -> ExactCoordinationGeometryRecord:
    """Force geometry from the complete held direct-position relation."""

    if not isinstance(entity, CompleteCoordinationEntity):
        raise InadmissibleExactValue("coordination geometry requires an admitted coordination entity")
    if not isinstance(geometry, CompleteCoordinationGeometry):
        raise InadmissibleExactValue("coordination geometry requires a complete held geometry")
    if entity.central_occurrence != geometry.central_occurrence:
        raise InadmissibleExactValue("coordination geometry cannot change the retained centre")
    entity_ligands = tuple(row.ligand_occurrence for row in entity.ordered_attachments)
    geometry_ligands = tuple(row.ligand_occurrence for row in geometry.ordered_positions)
    if geometry_ligands != entity_ligands:
        raise InadmissibleExactValue("coordination geometry must retain every direct ligand occurrence once")

    signature = (
        tuple(
            (
                row.attachment_ordinal.value,
                row.ligand_occurrence,
                row.orientation_word,
            )
            for row in geometry.ordered_positions
        ),
        tuple(
            (
                edge.first_ligand_occurrence,
                edge.second_ligand_occurrence,
                edge.adjacency_trace,
            )
            for edge in geometry.ordered_adjacencies
        ),
    )
    return ExactCoordinationGeometryRecord(
        central_occurrence=geometry.central_occurrence,
        positive_coordination_count=PositiveCount(len(geometry.ordered_positions)),
        ordered_positions=geometry.ordered_positions,
        ordered_adjacencies=geometry.ordered_adjacencies,
        generated_space_rank=PositiveCount(3),
        boundary_rank=PositiveCount(2),
        exact_geometry_signature=signature,
    )


def append_position_preserves_prior_geometry(
    entity_after: CompleteCoordinationEntity,
    geometry_before: CompleteCoordinationGeometry,
    new_position: HeldCoordinationPosition,
    new_adjacencies: tuple[HeldCoordinationAdjacency, ...],
) -> bool:
    prior_width = len(geometry_before.ordered_positions)
    entity_before = CompleteCoordinationEntity(
        entity_after.entity_identity,
        entity_after.central_element_identity,
        entity_after.central_occurrence,
        entity_after.ordered_attachments[:prior_width],
    )
    before = forced_coordination_geometry(entity_before, geometry_before)
    after_geometry = CompleteCoordinationGeometry(
        geometry_before.central_occurrence,
        geometry_before.ordered_positions + (new_position,),
        geometry_before.ordered_adjacencies + new_adjacencies,
    )
    after = forced_coordination_geometry(entity_after, after_geometry)
    return (
        after.central_occurrence == before.central_occurrence
        and after.positive_coordination_count.value == before.positive_coordination_count.value + 1
        and after.ordered_positions[:prior_width] == before.ordered_positions
        and after.ordered_adjacencies[: len(before.ordered_adjacencies)] == before.ordered_adjacencies
        and after.generated_space_rank == before.generated_space_rank == PositiveCount(3)
        and after.boundary_rank == before.boundary_rank == PositiveCount(2)
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
    "SFT-PHYS-SPACE-DIMENSION-THREE-001",
    "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-MOLECULAR-BOND-ANGLE-003",
    "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
    "SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002",
    "SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "chemical-formula-only", "A formula does not retain the central or ligand occurrences.", "one-retained-centre-and-every-direct-ligand-occurrence", "Geometry belongs to one centre and every direct ligand occurrence remains distinct."),
    dimension("incidence", "coordination-number-alone-selects-shape", "Equal counts can carry different orientations and adjacency; count alone cannot select geometry.", "complete-direct-incidence-support", "Every and only direct centre-ligand incidence enters the geometry."),
    dimension("orientation", "imported-shape-name-or-continuum-coordinate", "A conventional name or continuum coordinate imports the result.", "three-generated-axis-held-orientation-word", "Each direct ligand position is a three-axis Fold word of held fibres and structural EmptyOne."),
    dimension("adjacency", "selected-or-inferred-neighbour-pairs", "Selecting neighbours omits part of the boundary relation.", "complete-generated-boundary-adjacency-trace", "Every generated boundary adjacency and its occurrence endpoints remain explicit."),
    dimension("identity", "orientation-or-occurrence-collapse", "Collapsing an occurrence or orientation destroys a distinguishable geometry.", "exact-complete-position-adjacency-signature", "The complete occurrence, orientation and adjacency signature is the geometry."),
    dimension("rank", "free-dimensional-or-polyhedral-rank", "A free rank imports geometric structure.", "forced-generator-three-and-boundary-rank-two", "The admitted generator-three and boundary-rank-two laws fix the computational geometry ranks."),
    dimension("observation", "selected-favourable-geometry-rows", "Selected rows cannot test the full source boundary.", "sealed-complete-authority-surfaces-including-adverse-identity-rows", "All IUPAC, NIST, absent and target-mismatch rows remain present after value-free sealing."),
    dimension("extension", "new-position-replaces-or-recounts-prior-geometry", "Replacement erases the prior geometry.", "next-position-preserves-prior-and-adds-its-complete-relations", "The next direct ligand preserves every prior position and adjacency and adds only its generated relations."),
)


EXACT_RESULT = (
    "one-retained-centre-and-every-direct-ligand-occurrence__complete-direct-incidence-support__"
    "three-generated-axis-held-orientation-word__complete-generated-boundary-adjacency-trace__"
    "exact-complete-position-adjacency-signature__forced-generator-three-and-boundary-rank-two__"
    "sealed-complete-authority-surfaces-including-adverse-identity-rows__"
    "next-position-preserves-prior-and-adds-its-complete-relations"
)


def _entity(width: int) -> CompleteCoordinationEntity:
    centre = HeldLabel("coordination-central-occurrence", "centre-one")
    return CompleteCoordinationEntity(
        HeldLabel("coordination-entity", f"geometry-entity-{width}"),
        HeldLabel("coordination-central-element", "central-element"),
        centre,
        tuple(
            RetainedCoordinationAttachment(
                PositiveCount(number),
                centre,
                HeldLabel("coordination-ligand-occurrence", f"ligand-{number}"),
                HeldLabel("coordination-ligand-group", "ligand-group"),
                HeldLabel("positive-coordination-incidence", f"centre-ligand-{number}"),
            )
            for number in range(1, width + 1)
        ),
    )


def _word(first: str, second: str | None = None, third: str | None = None) -> tuple[OrientationCell, OrientationCell, OrientationCell]:
    return (
        HeldLabel("fold-orientation-fibre", first),
        EmptyOne() if second is None else HeldLabel("fold-orientation-fibre", second),
        EmptyOne() if third is None else HeldLabel("fold-orientation-fibre", third),
    )


_ENTITY_TWO = _entity(2)
_GEOMETRY_TWO = CompleteCoordinationGeometry(
    _ENTITY_TWO.central_occurrence,
    (
        HeldCoordinationPosition(PositiveCount(1), _ENTITY_TWO.ordered_attachments[0].ligand_occurrence, _word("fibre-one")),
        HeldCoordinationPosition(PositiveCount(2), _ENTITY_TWO.ordered_attachments[1].ligand_occurrence, _word("fibre-two")),
    ),
    (
        HeldCoordinationAdjacency(
            _ENTITY_TWO.ordered_attachments[0].ligand_occurrence,
            _ENTITY_TWO.ordered_attachments[1].ligand_occurrence,
            HeldLabel("coordination-boundary-adjacency", "edge-one-two"),
        ),
    ),
)
_RECORD_TWO = forced_coordination_geometry(_ENTITY_TWO, _GEOMETRY_TWO)
_ENTITY_THREE = _entity(3)
_THIRD_POSITION = HeldCoordinationPosition(
    PositiveCount(3),
    _ENTITY_THREE.ordered_attachments[2].ligand_occurrence,
    _word("fibre-one", "fibre-two"),
)
_THIRD_EDGES = (
    HeldCoordinationAdjacency(
        _ENTITY_THREE.ordered_attachments[1].ligand_occurrence,
        _ENTITY_THREE.ordered_attachments[2].ligand_occurrence,
        HeldLabel("coordination-boundary-adjacency", "edge-two-three"),
    ),
    HeldCoordinationAdjacency(
        _ENTITY_THREE.ordered_attachments[2].ligand_occurrence,
        _ENTITY_THREE.ordered_attachments[0].ligand_occurrence,
        HeldLabel("coordination-boundary-adjacency", "edge-three-one"),
    ),
)


OPERATIONAL_WITNESSES = (
    ("positive-count", "Two retained direct ligand positions force positive coordination count two.", _RECORD_TWO.positive_coordination_count == PositiveCount(2)),
    ("three-axis-rank", "Every exact position belongs to the forced three-axis Fold support.", _RECORD_TWO.generated_space_rank == PositiveCount(3)),
    ("boundary-rank", "The coordination boundary retains the forced rank two.", _RECORD_TWO.boundary_rank == PositiveCount(2)),
    ("count-not-shape", "The exact signature retains orientation and adjacency in addition to count.", len(_RECORD_TWO.exact_geometry_signature) == 2 and bool(_RECORD_TWO.ordered_adjacencies)),
    ("successor", "Appending the next position preserves the prior exact geometry and adds its relations.", append_position_preserves_prior_geometry(_ENTITY_THREE, _GEOMETRY_TWO, _THIRD_POSITION, _THIRD_EDGES)),
)


__all__ = (
    "CompleteCoordinationGeometry",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactCoordinationGeometryRecord",
    "HeldCoordinationAdjacency",
    "HeldCoordinationPosition",
    "OPERATIONAL_WITNESSES",
    "append_position_preserves_prior_geometry",
    "forced_coordination_geometry",
)
