"""Fold-native metal--carbon organometallic bond law (INORG-010)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class DirectMetalCarbonIncidence:
    centre: HeldLabel
    carbon_occurrence: HeldLabel
    electron_support: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.centre.family != "organometallic-centre-occurrence":
            raise InadmissibleExactValue("organometallic incidence requires one retained centre occurrence")
        if self.carbon_occurrence.family != "carbon-occurrence":
            raise InadmissibleExactValue("organometallic incidence requires one retained carbon occurrence")
        if not self.electron_support or any(row.family != "held-bond-electron" for row in self.electron_support):
            raise InadmissibleExactValue("direct metal-carbon incidence requires complete positive held electron support")
        if len(set(self.electron_support)) != len(self.electron_support):
            raise InadmissibleExactValue("held bond-electron support cannot duplicate an occurrence")


@dataclass(frozen=True)
class ExactOrganometallicBondTopology:
    entity: HeldLabel
    incidences: tuple[DirectMetalCarbonIncidence, ...]
    direct_incidence_count: PositiveCount
    classification: HeldLabel

    def __post_init__(self) -> None:
        if self.entity.family != "chemical-entity":
            raise InadmissibleExactValue("organometallic topology requires one retained chemical entity")
        if not self.incidences or self.direct_incidence_count.value != len(self.incidences):
            raise InadmissibleExactValue("organometallic count must equal complete positive direct incidence support")
        keys = tuple((row.centre, row.carbon_occurrence) for row in self.incidences)
        if len(set(keys)) != len(keys):
            raise InadmissibleExactValue("metal-carbon direct incidences cannot be duplicated")
        if self.classification != HeldLabel("chemical-class", "organometallic"):
            raise InadmissibleExactValue("positive direct metal-carbon support uniquely forces organometallic class")


OrganometallicSupport = Union[EmptyOne, ExactOrganometallicBondTopology]


def direct_incidence(centre: str, carbon: str, electron_count: PositiveCount) -> DirectMetalCarbonIncidence:
    return DirectMetalCarbonIncidence(
        HeldLabel("organometallic-centre-occurrence", centre),
        HeldLabel("carbon-occurrence", carbon),
        tuple(HeldLabel("held-bond-electron", f"{centre}-{carbon}-{index}") for index in range(1, electron_count.value + 1)),
    )


def forced_organometallic_bond(entity: str, incidences: Union[EmptyOne, tuple[DirectMetalCarbonIncidence, ...]]) -> OrganometallicSupport:
    if isinstance(incidences, EmptyOne):
        return EMPTY_ONE
    if not incidences:
        raise InadmissibleExactValue("host empty tuple is not structural EmptyOne")
    return ExactOrganometallicBondTopology(
        HeldLabel("chemical-entity", entity), incidences, PositiveCount(len(incidences)), HeldLabel("chemical-class", "organometallic")
    )


def append_direct_incidence(topology: ExactOrganometallicBondTopology, incidence: DirectMetalCarbonIncidence) -> ExactOrganometallicBondTopology:
    return forced_organometallic_bond(topology.entity.label, topology.incidences + (incidence,))


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001", "SFT-CHEM-ELEM-ELEMENT-001", "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-ORDER-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002", "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001", "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "free-compound-name", "A name does not retain the bonded entity.", "one-retained-chemical-entity", "Every incidence belongs to one retained chemical entity."),
    dimension("centre", "imported-conventional-metal-list", "A conventional list imports the classification boundary.", "retained-admitted-centre-occurrence", "The centre is a retained admitted element occurrence."),
    dimension("carbon", "selected-formula-fragment", "A selected formula fragment need not be a bonded carbon occurrence.", "retained-carbon-occurrence", "Every classified incidence retains its carbon occurrence."),
    dimension("topology", "proximity-or-name-association", "Proximity or naming does not force a bond.", "direct-centre-carbon-incidence", "A direct generated adjacency forces the bond topology."),
    dimension("electrons", "assumed-valence-number", "An assumed valence number loses the bond support.", "complete-held-bond-electron-support", "Every incidence retains complete positive held electron support."),
    dimension("multiplicity", "single-selected-bond", "Selecting one bond loses additional incidences.", "complete-positive-direct-incidence-support", "All distinct direct incidences are retained and counted exactly."),
    dimension("classification", "species-or-name-lookup", "A lookup lets the observed label choose the law.", "positive-support-organometallic-EmptyOne-otherwise", "Positive direct support forces organometallic; structural absence remains EmptyOne."),
    dimension("extension", "fitted-species-exception", "A species exception destroys zero-parameter closure.", "direct-incidence-successor-no-extra-rule", "Each fresh direct incidence appends once without rewriting prior support."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    absent = forced_organometallic_bond("absent", EMPTY_ONE)
    first = forced_organometallic_bond("one", (direct_incidence("M1", "C1", PositiveCount(2)),))
    second = append_direct_incidence(first, direct_incidence("M1", "C2", PositiveCount(2)))
    duplicate_rejected = False
    try:
        row = direct_incidence("M1", "C1", PositiveCount(2)); forced_organometallic_bond("bad", (row, row))
    except InadmissibleExactValue:
        duplicate_rejected = True
    return (
        ("structural-absence", "No direct incidence remains structural EmptyOne.", isinstance(absent, EmptyOne)),
        ("first-direct-incidence", "One direct incidence forces count one and organometallic class.", first.direct_incidence_count.value == 1 and first.classification.label == "organometallic"),
        ("direct-successor", "A fresh direct incidence increments the exact count once.", second.direct_incidence_count.value == 2),
        ("duplicate-control", "A duplicated direct incidence rejects.", duplicate_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-retained-chemical-entity__retained-admitted-centre-occurrence__retained-carbon-occurrence__direct-centre-carbon-incidence__complete-held-bond-electron-support__complete-positive-direct-incidence-support__positive-support-organometallic-EmptyOne-otherwise__direct-incidence-successor-no-extra-rule"


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "DirectMetalCarbonIncidence",
    "ExactOrganometallicBondTopology", "append_direct_incidence", "direct_incidence", "forced_organometallic_bond",
)
