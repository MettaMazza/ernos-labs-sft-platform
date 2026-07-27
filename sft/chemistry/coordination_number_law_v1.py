"""Fold-native coordination-number law for INORG-002."""
from __future__ import annotations
from dataclasses import dataclass

from sft.chemistry.coordination_entity_law_v1 import CompleteCoordinationEntity, RetainedCoordinationAttachment
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ExactCoordinationNumberRecord:
    entity_identity: HeldLabel
    central_occurrence: HeldLabel
    positive_direct_incidence_count: PositiveCount
    ordered_incidence_traces: tuple[HeldLabel, ...]


def forced_coordination_number(entity: CompleteCoordinationEntity) -> ExactCoordinationNumberRecord:
    if not isinstance(entity, CompleteCoordinationEntity):
        raise InadmissibleExactValue("coordination number requires an admitted complete coordination entity")
    traces = tuple(row.attachment_trace for row in entity.ordered_attachments)
    if len(set(traces)) != len(traces):
        raise InadmissibleExactValue("coordination incidence traces must remain distinct")
    return ExactCoordinationNumberRecord(entity.entity_identity, entity.central_occurrence, PositiveCount(len(traces)), traces)


def append_incidence_increments_coordination_number(
    entity: CompleteCoordinationEntity,
    successor: RetainedCoordinationAttachment,
) -> bool:
    if successor.source_occurrence.value != len(entity.ordered_attachments) + 1 or successor.central_occurrence != entity.central_occurrence:
        raise InadmissibleExactValue("coordination-number successor must be the next incidence on the retained centre")
    before = forced_coordination_number(entity)
    after = forced_coordination_number(CompleteCoordinationEntity(entity.entity_identity, entity.central_element_identity, entity.central_occurrence, entity.ordered_attachments + (successor,)))
    return after.positive_direct_incidence_count.value == before.positive_direct_incidence_count.value + 1 and after.ordered_incidence_traces[:-1] == before.ordered_incidence_traces


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "formula-or-central-name-only", "A name does not expose complete incident support.", "admitted-complete-coordination-entity", "Count begins only from an admitted complete coordination entity."),
    dimension("membership", "nearby-or-selected-ligands", "Proximity or selection does not retain the entity's direct incidence boundary.", "every-distinct-direct-central-incidence", "Every and only distinct direct incidences on the retained centre enter."),
    dimension("quantity", "imported-coordination-number-table", "A conventional table selects the answer.", "positive-count-of-generated-incidence-traces", "The support itself forces its exact positive cardinality."),
    dimension("identity", "repeated-ligand-labels-merged", "Merging equal group labels undercounts distinct occurrences.", "occurrence-distinct-incidences-counted-once", "Each distinct ligand occurrence contributes its distinct incidence exactly once."),
    dimension("absence", "numerical-zero-or-negative-vacancy", "Numerical zero and signed vacancy are forbidden proof forms.", "structural-EmptyOne-outside-positive-support", "Absence is structural and never counted as a positive incidence."),
    dimension("observation", "observed-counts-readable-before-seal", "Observed 3, 4 or 5 could select a counting rule.", "complete-23-record-value-free-identity-seal", "All 23 identities seal before term and structure values open."),
    dimension("boundary", "general-crystal-pi-and-sigma-senses-mixed", "Mixing distinct source senses makes the count ambiguous.", "direct-inorganic-incidence-sense-held", "General, inorganic sigma, pi-exclusion and crystal-sense records remain distinct."),
    dimension("extension", "next-ligand-recounts-or-replaces-support", "Replacement does not preserve the prior count proof.", "next-incidence-preserves-prior-and-adds-one", "The next direct incidence preserves all prior traces and adds exactly one."),
)

EXACT_RESULT = "admitted-complete-coordination-entity__every-distinct-direct-central-incidence__positive-count-of-generated-incidence-traces__occurrence-distinct-incidences-counted-once__structural-EmptyOne-outside-positive-support__complete-23-record-value-free-identity-seal__direct-inorganic-incidence-sense-held__next-incidence-preserves-prior-and-adds-one"

def _entity(width: int) -> CompleteCoordinationEntity:
    central=HeldLabel("coordination-central-occurrence","central")
    rows=tuple(RetainedCoordinationAttachment(PositiveCount(n),central,HeldLabel("coordination-ligand-occurrence",f"L-{n}"),HeldLabel("coordination-ligand-group","L"),HeldLabel("positive-coordination-incidence",f"edge-{n}")) for n in range(1,width+1))
    return CompleteCoordinationEntity(HeldLabel("coordination-entity",f"entity-{width}"),HeldLabel("coordination-central-element","M"),central,rows)

_BASE=_entity(3)
_NEXT=RetainedCoordinationAttachment(PositiveCount(4),_BASE.central_occurrence,HeldLabel("coordination-ligand-occurrence","L-4"),HeldLabel("coordination-ligand-group","L"),HeldLabel("positive-coordination-incidence","edge-4"))
OPERATIONAL_WITNESSES=(
    ("three-incidence-count","Three generated direct incidences force positive count three.",forced_coordination_number(_BASE).positive_direct_incidence_count==PositiveCount(3)),
    ("four-incidence-count","Four generated direct incidences force positive count four.",forced_coordination_number(_entity(4)).positive_direct_incidence_count==PositiveCount(4)),
    ("five-incidence-count","Five generated direct incidences force positive count five.",forced_coordination_number(_entity(5)).positive_direct_incidence_count==PositiveCount(5)),
    ("successor","The next direct incidence preserves every prior trace and adds one.",append_incidence_increments_coordination_number(_BASE,_NEXT)),
)

__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","ExactCoordinationNumberRecord","OPERATIONAL_WITNESSES","append_incidence_increments_coordination_number","forced_coordination_number")
