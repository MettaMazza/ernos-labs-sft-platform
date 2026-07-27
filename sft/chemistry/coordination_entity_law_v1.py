"""Fold-native coordination entity and retained central-ligand identity for INORG-001."""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class RetainedCoordinationAttachment:
    source_occurrence: PositiveCount
    central_occurrence: HeldLabel
    ligand_occurrence: HeldLabel
    ligand_group_identity: HeldLabel
    attachment_trace: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("coordination attachment occurrence must be exact positive")
        if not isinstance(self.central_occurrence, HeldLabel) or self.central_occurrence.family != "coordination-central-occurrence":
            raise InadmissibleExactValue("coordination attachment must retain its central occurrence")
        if not isinstance(self.ligand_occurrence, HeldLabel) or self.ligand_occurrence.family != "coordination-ligand-occurrence":
            raise InadmissibleExactValue("coordination attachment must retain its ligand occurrence")
        if not isinstance(self.ligand_group_identity, HeldLabel) or self.ligand_group_identity.family != "coordination-ligand-group":
            raise InadmissibleExactValue("coordination attachment must retain its ligand group identity")
        if not isinstance(self.attachment_trace, HeldLabel) or self.attachment_trace.family != "positive-coordination-incidence":
            raise InadmissibleExactValue("coordination attachment requires a positive incidence trace")


@dataclass(frozen=True)
class CompleteCoordinationEntity:
    entity_identity: HeldLabel
    central_element_identity: HeldLabel
    central_occurrence: HeldLabel
    ordered_attachments: tuple[RetainedCoordinationAttachment, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.entity_identity, HeldLabel) or self.entity_identity.family != "coordination-entity":
            raise InadmissibleExactValue("coordination entity must retain one complete entity identity")
        if not isinstance(self.central_element_identity, HeldLabel) or self.central_element_identity.family != "coordination-central-element":
            raise InadmissibleExactValue("coordination entity must retain the central element identity")
        if not isinstance(self.central_occurrence, HeldLabel) or self.central_occurrence.family != "coordination-central-occurrence":
            raise InadmissibleExactValue("coordination entity must retain the central occurrence")
        if not self.ordered_attachments:
            raise InadmissibleExactValue("a coordination entity requires positive ligand attachment support")
        if any(not isinstance(row, RetainedCoordinationAttachment) for row in self.ordered_attachments):
            raise InadmissibleExactValue("coordination support contains an unregistered attachment")
        if tuple(row.source_occurrence.value for row in self.ordered_attachments) != tuple(range(1, len(self.ordered_attachments) + 1)):
            raise InadmissibleExactValue("coordination attachment support must be complete and gap-free")
        if any(row.central_occurrence != self.central_occurrence for row in self.ordered_attachments):
            raise InadmissibleExactValue("every ligand attachment must retain the same central occurrence")
        if len({row.ligand_occurrence for row in self.ordered_attachments}) != len(self.ordered_attachments):
            raise InadmissibleExactValue("distinct ligand occurrences cannot be collapsed")
        if len({row.attachment_trace for row in self.ordered_attachments}) != len(self.ordered_attachments):
            raise InadmissibleExactValue("distinct central-ligand incidences cannot be collapsed")


@dataclass(frozen=True)
class ExactCoordinationIdentityRecord:
    entity_identity: HeldLabel
    central_element_identity: HeldLabel
    central_occurrence: HeldLabel
    ordered_ligand_occurrences: tuple[HeldLabel, ...]
    ordered_ligand_group_identities: tuple[HeldLabel, ...]
    ordered_attachment_traces: tuple[HeldLabel, ...]


def forced_coordination_entity_identity_law(entity: CompleteCoordinationEntity) -> ExactCoordinationIdentityRecord:
    if not isinstance(entity, CompleteCoordinationEntity):
        raise InadmissibleExactValue("coordination identity law requires a complete entity")
    return ExactCoordinationIdentityRecord(
        entity.entity_identity,
        entity.central_element_identity,
        entity.central_occurrence,
        tuple(row.ligand_occurrence for row in entity.ordered_attachments),
        tuple(row.ligand_group_identity for row in entity.ordered_attachments),
        tuple(row.attachment_trace for row in entity.ordered_attachments),
    )


def append_ligand_preserves_coordination_identity(
    entity: CompleteCoordinationEntity,
    successor: RetainedCoordinationAttachment,
) -> bool:
    if successor.source_occurrence.value != len(entity.ordered_attachments) + 1:
        raise InadmissibleExactValue("coordination successor must be the next positive occurrence")
    if successor.central_occurrence != entity.central_occurrence:
        raise InadmissibleExactValue("coordination successor cannot replace the central occurrence")
    prior = forced_coordination_entity_identity_law(entity)
    extended = CompleteCoordinationEntity(
        entity.entity_identity,
        entity.central_element_identity,
        entity.central_occurrence,
        entity.ordered_attachments + (successor,),
    )
    result = forced_coordination_entity_identity_law(extended)
    width = len(prior.ordered_ligand_occurrences)
    return (
        result.entity_identity == prior.entity_identity
        and result.central_element_identity == prior.central_element_identity
        and result.central_occurrence == prior.central_occurrence
        and result.ordered_ligand_occurrences[:width] == prior.ordered_ligand_occurrences
        and result.ordered_ligand_group_identities[:width] == prior.ordered_ligand_group_identities
        and result.ordered_attachment_traces[:width] == prior.ordered_attachment_traces
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001",
    "SFT-CHEM-ELEM-ELEMENT-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-MULTICENTRE-DELOCALIZED-SUPPORT-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "formula-or-name-only", "A name does not retain the entity's generated constituents.", "complete-coordination-entity-carrier", "One entity retains its complete central and ligand support."),
    dimension("role", "conventional-central-and-ligand-names-imported", "Imported role names cannot force which occurrence is common to every incidence.", "incidence-forced-central-and-surrounding-roles", "The common incident occurrence is central and each attached occurrence is surrounding support."),
    dimension("identity", "element-or-ligand-occurrences-collapsed", "Collapsing repeated labels erases distinct occurrences.", "central-and-every-ligand-occurrence-retained", "The central occurrence and every ligand occurrence remain distinguishable."),
    dimension("attachment", "proximity-or-continuum-distance-only", "Proximity alone does not retain a generated attachment.", "positive-central-ligand-incidence-trace", "Every attachment is one explicit positive incidence trace."),
    dimension("composition", "selected-or-average-ligand-support", "Selection or averaging erases members of the coordination entity.", "complete-gap-free-ligand-support", "Every registered ligand occurrence and attachment remains present exactly once."),
    dimension("absence", "numerical-zero-or-negative-vacancy", "Numerical zero and signed vacancy are not Fold-native forms.", "structural-EmptyOne-only", "Any absent attachment is structural EmptyOne and is not admitted into positive support."),
    dimension("observation", "source-structure-visible-before-seal", "Observed structures could select the law.", "complete-20-record-identity-sealed-structure-vector", "Twenty value-free identities seal before all authoritative records open."),
    dimension("extension", "successor-replaces-central-or-prior-ligand", "Replacement destroys retained identity.", "next-ligand-preserves-entire-prior-entity", "Appending the next complete attachment preserves the entire prior entity."),
)


EXACT_RESULT = (
    "complete-coordination-entity-carrier__incidence-forced-central-and-surrounding-roles__"
    "central-and-every-ligand-occurrence-retained__positive-central-ligand-incidence-trace__"
    "complete-gap-free-ligand-support__structural-EmptyOne-only__"
    "complete-20-record-identity-sealed-structure-vector__next-ligand-preserves-entire-prior-entity"
)


def _attachment(number: int, central: HeldLabel, group: str) -> RetainedCoordinationAttachment:
    return RetainedCoordinationAttachment(
        PositiveCount(number), central,
        HeldLabel("coordination-ligand-occurrence", f"ligand-{number}"),
        HeldLabel("coordination-ligand-group", group),
        HeldLabel("positive-coordination-incidence", f"central-to-ligand-{number}"),
    )


_CENTRAL = HeldLabel("coordination-central-occurrence", "Fe-one")
_BASE = CompleteCoordinationEntity(
    HeldLabel("coordination-entity", "example-entity"),
    HeldLabel("coordination-central-element", "Fe"),
    _CENTRAL,
    (_attachment(1, _CENTRAL, "ligand-group-a"), _attachment(2, _CENTRAL, "ligand-group-a")),
)
_RESULT = forced_coordination_entity_identity_law(_BASE)
_MISMATCH_REJECTED = False
try:
    CompleteCoordinationEntity(
        _BASE.entity_identity,
        _BASE.central_element_identity,
        _BASE.central_occurrence,
        (_attachment(1, HeldLabel("coordination-central-occurrence", "different-central"), "ligand-group-a"),),
    )
except InadmissibleExactValue:
    _MISMATCH_REJECTED = True


OPERATIONAL_WITNESSES = (
    ("retained-central", "Every attachment retains the same central occurrence.", _RESULT.central_occurrence == _CENTRAL),
    ("retained-ligands", "Repeated ligand group labels do not collapse distinct ligand occurrences.", len(set(_RESULT.ordered_ligand_occurrences)) == 2),
    ("positive-incidences", "Every attachment remains a distinct positive incidence trace.", len(set(_RESULT.ordered_attachment_traces)) == 2),
    ("central-mismatch-control", "An attachment to a different centre cannot enter the entity.", _MISMATCH_REJECTED),
    ("successor", "The next ligand preserves the complete prior coordination identity.", append_ligand_preserves_coordination_identity(_BASE, _attachment(3, _CENTRAL, "ligand-group-b"))),
)


__all__ = (
    "CompleteCoordinationEntity", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactCoordinationIdentityRecord", "OPERATIONAL_WITNESSES", "RetainedCoordinationAttachment",
    "append_ligand_preserves_coordination_identity", "forced_coordination_entity_identity_law",
)
