"""Fold-native molecular support composition and occupancy law (ELEC-003).

Conventional orbital symbols are deliberately absent from the native objects.
They are introduced only by the post-seal correspondence function.  Native
support is a molecular carrier, a positive radial recurrence, structural empty
One or a positive axis recurrence, one of two joining-phase fibres and optional
held symmetry observations.  Occupancy is empty One, one held occurrence, or
one complementary spin pair; it is never a numerical-zero or signed scalar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


AxisRank = Union[EmptyOne, PositiveCount]


@dataclass(frozen=True)
class MolecularSupportCell:
    molecular_carrier: HeldLabel
    radial_recurrence: PositiveCount
    axis_recurrence: AxisRank
    joining_phase: HeldLabel
    exchange_observation: HeldLabel | EmptyOne
    reflection_observation: HeldLabel | EmptyOne

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("support cell requires one identified molecular carrier")
        if self.joining_phase.family != "joining-phase" or self.joining_phase.label not in {
            "fibre-a",
            "fibre-b",
        }:
            raise InadmissibleExactValue("joined support has exactly two held phase fibres")
        if not isinstance(self.axis_recurrence, (EmptyOne, PositiveCount)):
            raise InadmissibleExactValue("axis support is structural empty One or a positive recurrence")
        if isinstance(self.exchange_observation, HeldLabel) and self.exchange_observation.family != "nuclear-exchange":
            raise InadmissibleExactValue("exchange observation has an invalid family")
        if isinstance(self.reflection_observation, HeldLabel) and self.reflection_observation.family != "axis-reflection":
            raise InadmissibleExactValue("reflection observation has an invalid family")


@dataclass(frozen=True)
class OccupiedMolecularSupport:
    cell: MolecularSupportCell
    electron_occurrences: tuple[HeldLabel, ...]
    spin_fibres: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if not self.electron_occurrences or len(self.electron_occurrences) > 2:
            raise InadmissibleExactValue("one spatial support cell holds one occurrence or one complementary pair")
        if len(self.electron_occurrences) != len(self.spin_fibres):
            raise InadmissibleExactValue("every occupied support occurrence requires one spin fibre")
        if len(set(self.electron_occurrences)) != len(self.electron_occurrences):
            raise InadmissibleExactValue("electron occurrence cannot occupy the same support twice")
        if any(label.family != "electron-occurrence" for label in self.electron_occurrences):
            raise InadmissibleExactValue("support occupancy contains an invalid electron occurrence")
        if any(label.family != "electron-spin" for label in self.spin_fibres):
            raise InadmissibleExactValue("support occupancy contains an invalid spin fibre")
        labels = tuple(label.label for label in self.spin_fibres)
        if any(label not in {"fibre-a", "fibre-b"} for label in labels):
            raise InadmissibleExactValue("support occupancy left the generated spin pair")
        if len(labels) == 2 and set(labels) != {"fibre-a", "fibre-b"}:
            raise InadmissibleExactValue("double occupancy requires complementary spin fibres")

    @property
    def occupancy_count(self) -> PositiveCount:
        return PositiveCount(len(self.electron_occurrences))


@dataclass(frozen=True)
class CompleteMolecularSupport:
    molecular_carrier: HeldLabel
    exact_electron_count: PositiveCount
    occupied_cells: tuple[OccupiedMolecularSupport, ...]

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier" or not self.occupied_cells:
            raise InadmissibleExactValue("complete support requires an identified carrier and positive occupied cells")
        if any(row.cell.molecular_carrier != self.molecular_carrier for row in self.occupied_cells):
            raise InadmissibleExactValue("every support cell must remain bound to the same molecule")
        occurrences = tuple(label for row in self.occupied_cells for label in row.electron_occurrences)
        if len(occurrences) != self.exact_electron_count.value or len(set(occurrences)) != len(occurrences):
            raise InadmissibleExactValue("occupied cells must exhaust every electron occurrence exactly once")
        cell_coordinates = tuple(
            (
                row.cell.radial_recurrence,
                row.cell.axis_recurrence,
                row.cell.joining_phase,
                row.cell.exchange_observation,
                row.cell.reflection_observation,
            )
            for row in self.occupied_cells
        )
        if len(set(cell_coordinates)) != len(cell_coordinates):
            raise InadmissibleExactValue("a complete support cannot duplicate a spatial cell coordinate")


def joined_phase_pair(
    molecular_label: str,
    radial_recurrence: PositiveCount,
    axis_recurrence: AxisRank,
) -> tuple[MolecularSupportCell, MolecularSupportCell]:
    carrier = HeldLabel("molecular-carrier", molecular_label)
    return tuple(
        MolecularSupportCell(
            carrier,
            radial_recurrence,
            axis_recurrence,
            HeldLabel("joining-phase", phase),
            EMPTY_ONE,
            EMPTY_ONE,
        )
        for phase in ("fibre-a", "fibre-b")
    )  # type: ignore[return-value]


def axis_rank_from_positive_ordinal(ordinal: PositiveCount) -> AxisRank:
    """First conventional class is the invariant boundary, not numerical zero."""

    return EMPTY_ONE if ordinal.value == 1 else PositiveCount(ordinal.value - 1)


def axis_rank_label(rank: AxisRank) -> HeldLabel:
    if rank == EMPTY_ONE:
        return HeldLabel("axis-support-rank", "structural-empty-One")
    if rank.value == 1:
        return HeldLabel("axis-support-rank", "first-recurrence")
    if rank.value == 2:
        return HeldLabel("axis-support-rank", "second-recurrence")
    if rank.value == 3:
        return HeldLabel("axis-support-rank", "third-recurrence")
    return HeldLabel("axis-support-rank", f"positive-recurrence-{rank.value}")


def conventional_support_correspondence(symbol: str) -> AxisRank:
    """Downstream comparison only; never called by the candidate generator."""

    mapping = {
        "Σ": axis_rank_from_positive_ordinal(PositiveCount(1)),
        "Π": axis_rank_from_positive_ordinal(PositiveCount(2)),
        "Δ": axis_rank_from_positive_ordinal(PositiveCount(3)),
        "Φ": axis_rank_from_positive_ordinal(PositiveCount(4)),
        "σ": axis_rank_from_positive_ordinal(PositiveCount(1)),
        "π": axis_rank_from_positive_ordinal(PositiveCount(2)),
        "δ": axis_rank_from_positive_ordinal(PositiveCount(3)),
        "φ": axis_rank_from_positive_ordinal(PositiveCount(4)),
    }
    try:
        return mapping[symbol]
    except KeyError as exc:
        raise InadmissibleExactValue("conventional support symbol is outside the declared comparison boundary") from exc


def occupied_support_from_source_assignment(
    molecular_label: str,
    radial_recurrence: PositiveCount,
    support_symbol: str,
    occupancy: PositiveCount,
) -> OccupiedMolecularSupport:
    if occupancy.value > 2:
        raise InadmissibleExactValue("one molecular spatial support cannot hold more than the complementary spin pair")
    cell = MolecularSupportCell(
        HeldLabel("molecular-carrier", molecular_label),
        radial_recurrence,
        conventional_support_correspondence(support_symbol),
        HeldLabel("joining-phase", "fibre-a"),
        EMPTY_ONE,
        EMPTY_ONE,
    )
    occurrences = tuple(
        HeldLabel("electron-occurrence", f"electron-{position}")
        for position in range(1, occupancy.value + 1)
    )
    spins = (
        (HeldLabel("electron-spin", "fibre-a"),)
        if occupancy.value == 1
        else (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b"))
    )
    return OccupiedMolecularSupport(cell, occurrences, spins)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-QUANTUM-STATE-COMPOSITION-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "free-orbital-name", "A free orbital name is detached from the molecule and its derivation.", "molecule-bound-support-cell", "Every support coordinate remains bound to one admitted molecular carrier."),
    dimension("joining", "unjoined-atomic-support-list", "An unjoined list cannot express the two generated molecular phase relations.", "two-held-joining-phases", "Joining generates exactly the two Fold phase fibres without a fitted splitting rule."),
    dimension("axis", "continuum-angular-coordinate", "A continuum angular coordinate imports an ungenerated state space.", "empty-One-or-positive-axis-recurrence", "Axis-invariant support is structural empty One; every further class is a counted positive recurrence."),
    dimension("symmetry", "unsigned-erased-symmetry", "Erasing exchange and reflection distinctions merges spectroscopically distinct support.", "held-exchange-and-reflection-labels", "Applicable nuclear exchange and axis reflection distinctions remain held labels."),
    dimension("occupancy", "signed-or-unbounded-occupation", "Signed, numerical-zero or unbounded fermion occupation violates the exact domain and exclusion.", "empty-One-single-or-complementary-pair", "A spatial support is empty One, singly occupied, or occupied by one complementary pair."),
    dimension("spin", "same-fibre-double-occupation", "Same-fibre doubling has no distinct admissible preimage under exclusion.", "complementary-spin-double-occupation", "The only double occupation retains both complementary spin fibres."),
    dimension("completeness", "selected-support-fragment", "A selected fragment cannot reconstruct the molecular electronic state or electron census.", "complete-electron-support-partition", "Every electron occurrence appears exactly once across molecule-bound occupied cells."),
    dimension("extension", "species-or-symbol-exception", "A species lookup or conventional symbol exception lets the target select the law.", "no-extra-rule", "The same generated support and occupancy law extends to every positive recurrence and molecule."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    sigma_pair = occupied_support_from_source_assignment("H2", PositiveCount(1), "σ", PositiveCount(2))
    sigma_single = occupied_support_from_source_assignment("H2+", PositiveCount(1), "σ", PositiveCount(1))
    pi_single = occupied_support_from_source_assignment("H2-excited", PositiveCount(2), "π", PositiveCount(1))
    phases = joined_phase_pair("molecule", PositiveCount(1), EMPTY_ONE)
    triple_rejected = False
    try:
        occupied_support_from_source_assignment("tampered", PositiveCount(1), "σ", PositiveCount(3))
    except InadmissibleExactValue:
        triple_rejected = True
    same_spin_rejected = False
    try:
        OccupiedMolecularSupport(
            phases[0],
            (HeldLabel("electron-occurrence", "one"), HeldLabel("electron-occurrence", "two")),
            (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-a")),
        )
    except InadmissibleExactValue:
        same_spin_rejected = True
    return (
        ("joining-phase-pair", "One joined support coordinate forces exactly two distinct held phase fibres.", len(phases) == 2 and phases[0] != phases[1]),
        ("axis-boundary-and-successor", "Sigma support maps to structural empty One and pi support to the first positive recurrence.", sigma_pair.cell.axis_recurrence == EMPTY_ONE and pi_single.cell.axis_recurrence == PositiveCount(1)),
        ("single-and-pair-occupation", "One-electron and complementary-pair support remain exact and distinct.", sigma_single.occupancy_count == PositiveCount(1) and sigma_pair.occupancy_count == PositiveCount(2)),
        ("triple-occupation-control", "A third fermion in one spatial support rejects.", triple_rejected),
        ("same-spin-control", "Two identical spin fibres in one spatial support reject.", same_spin_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "molecule-bound-support-cell__two-held-joining-phases__empty-One-or-positive-axis-recurrence__held-exchange-and-reflection-labels__empty-One-single-or-complementary-pair__complementary-spin-double-occupation__complete-electron-support-partition__no-extra-rule"


__all__ = (
    "AxisRank",
    "CompleteMolecularSupport",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "MolecularSupportCell",
    "OPERATIONAL_WITNESSES",
    "OccupiedMolecularSupport",
    "axis_rank_from_positive_ordinal",
    "axis_rank_label",
    "conventional_support_correspondence",
    "joined_phase_pair",
    "occupied_support_from_source_assignment",
)
