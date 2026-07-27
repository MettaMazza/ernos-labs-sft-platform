"""Exact Fold law for molecular electron count and held-spin organization.

No signed charge, numerical-zero occupation, orbital model, Hamiltonian,
measured state term or fitted parameter enters this derivation.  A neutral
carrier holds structural empty-One charge.  A charged carrier holds a positive
electron-transfer count and one of two directed actions: adjoin or remove.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class NuclearPopulation:
    element_symbol: HeldLabel
    atomic_number: PositiveCount
    occurrence_count: PositiveCount

    def __post_init__(self) -> None:
        if self.element_symbol.family != "element-symbol":
            raise InadmissibleExactValue("nuclear population requires a retained element symbol")


@dataclass(frozen=True)
class HeldChargeTransfer:
    action: HeldLabel
    count: PositiveCount | EmptyOne

    def __post_init__(self) -> None:
        if self.action.family != "electron-transfer":
            raise InadmissibleExactValue("charge requires a held electron-transfer action")
        if self.action.label == "empty-One":
            if self.count != EMPTY_ONE:
                raise InadmissibleExactValue("neutral charge is structural empty One")
        elif self.action.label in {"adjoin-electron", "remove-electron"}:
            if not isinstance(self.count, PositiveCount):
                raise InadmissibleExactValue("directed charge requires a positive transfer count")
        else:
            raise InadmissibleExactValue("charge action is outside the generated Fold pair")


@dataclass(frozen=True)
class SpinCell:
    cell_id: HeldLabel
    occupants: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.cell_id.family != "electron-support-cell" or not self.occupants:
            raise InadmissibleExactValue("a spin cell requires named positive support")
        if any(label.family != "electron-spin" for label in self.occupants):
            raise InadmissibleExactValue("spin occupants must remain held fibre labels")
        labels = tuple(label.label for label in self.occupants)
        if len(set(labels)) != len(labels) or len(labels) > 2:
            raise InadmissibleExactValue("same-cell same-fibre doubling violates exclusion")
        if any(label not in {"fibre-a", "fibre-b"} for label in labels):
            raise InadmissibleExactValue("electron spin has exactly two generated fibre labels")


@dataclass(frozen=True)
class MolecularElectronOrganization:
    molecular_id: HeldLabel
    electron_count: PositiveCount
    electron_occurrence_ids: tuple[HeldLabel, ...]
    cells: tuple[SpinCell, ...]
    complementary_pair_count: PositiveCount | EmptyOne
    unmatched_fibre_count: PositiveCount | EmptyOne
    spin_width: PositiveCount

    def __post_init__(self) -> None:
        if self.molecular_id.family != "molecular-carrier":
            raise InadmissibleExactValue("electron organization requires one molecular carrier")
        if len(self.electron_occurrence_ids) != self.electron_count.value:
            raise InadmissibleExactValue("electron count must equal complete occurrence support")
        if len(set(self.electron_occurrence_ids)) != len(self.electron_occurrence_ids):
            raise InadmissibleExactValue("electron occurrence identities must be unique")
        if any(label.family != "electron-occurrence" for label in self.electron_occurrence_ids):
            raise InadmissibleExactValue("electron support contains an invalid occurrence identity")
        occupied = sum(len(cell.occupants) for cell in self.cells)
        if occupied != self.electron_count.value:
            raise InadmissibleExactValue("every electron occurrence must occupy exactly one held-spin cell")
        pair_count = self.complementary_pair_count.value if isinstance(self.complementary_pair_count, PositiveCount) else 0
        unmatched_count = self.unmatched_fibre_count.value if isinstance(self.unmatched_fibre_count, PositiveCount) else 0
        if pair_count * 2 + unmatched_count != self.electron_count.value:
            raise InadmissibleExactValue("pair-plus-held decomposition does not exhaust electron support")
        if self.spin_width.value != unmatched_count + 1:
            raise InadmissibleExactValue("spin width must be one successor beyond unmatched fibre count")
        pairs = sum(tuple(label.label for label in cell.occupants) == ("fibre-a", "fibre-b") for cell in self.cells)
        singles = sum(len(cell.occupants) == 1 for cell in self.cells)
        if pairs != pair_count or singles != unmatched_count:
            raise InadmissibleExactValue("cell support differs from exact pair-plus-held decomposition")


def exact_electron_count(
    populations: tuple[NuclearPopulation, ...],
    transfer: HeldChargeTransfer,
) -> PositiveCount:
    if not populations:
        raise InadmissibleExactValue("molecular nuclear support must be positive and finite")
    neutral_count = sum(row.atomic_number.value * row.occurrence_count.value for row in populations)
    if transfer.action.label == "empty-One":
        result = neutral_count
    elif transfer.action.label == "adjoin-electron":
        assert isinstance(transfer.count, PositiveCount)
        result = neutral_count + transfer.count.value
    else:
        assert isinstance(transfer.count, PositiveCount)
        if transfer.count.value >= neutral_count:
            raise InadmissibleExactValue("electron removal cannot erase or exceed positive molecular support")
        result = neutral_count - transfer.count.value
    return PositiveCount(result)


def required_spin_width_parity(electron_count: PositiveCount) -> HeldLabel:
    """Parity forced by N = two-times-pairs + d and width = d successor One."""

    return HeldLabel(
        "spin-width-parity",
        "odd-positive-width" if electron_count.value % 2 == 0 else "even-positive-width",
    )


def build_complete_spin_organization(
    molecular_label: str,
    electron_count: PositiveCount,
    spin_width: PositiveCount,
) -> MolecularElectronOrganization:
    unmatched = spin_width.value - 1
    if unmatched > electron_count.value or (electron_count.value - unmatched) % 2:
        raise InadmissibleExactValue("spin width is incompatible with exact electron support")
    pair_count = (electron_count.value - unmatched) // 2
    cells = tuple(
        SpinCell(
            HeldLabel("electron-support-cell", f"pair-{index}"),
            (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")),
        )
        for index in range(1, pair_count + 1)
    ) + tuple(
        SpinCell(
            HeldLabel("electron-support-cell", f"held-{index}"),
            (HeldLabel("electron-spin", "fibre-a"),),
        )
        for index in range(1, unmatched + 1)
    )
    occurrences = tuple(
        HeldLabel("electron-occurrence", f"electron-{index}")
        for index in range(1, electron_count.value + 1)
    )
    return MolecularElectronOrganization(
        HeldLabel("molecular-carrier", molecular_label),
        electron_count,
        occurrences,
        cells,
        PositiveCount(pair_count) if pair_count else EMPTY_ONE,
        PositiveCount(unmatched) if unmatched else EMPTY_ONE,
        spin_width,
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-QUANTUM-STATE-COMPOSITION-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
    "SFT-CHEM-ELEM-ION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("nuclear_support", "formula-name-only", "A formula name does not enumerate the positive nuclear support that forces electron count.", "atomic-number-occurrence-support", "Every nucleus retains its admitted atomic number and exact occurrence count."),
    dimension("charge", "signed-charge-scalar", "A signed scalar imports negative quantity and conflates direction with magnitude.", "held-directed-electron-transfer", "Neutrality is empty One; cation and anion are held remove/adjoin actions with positive counts."),
    dimension("electron_count", "asserted-electron-number", "An asserted number is neither generated nor reconstructible.", "complete-electron-occurrence-census", "Electron count is the exact cardinality after the held transfer acts on nuclear support."),
    dimension("spin", "signed-spin-magnitude", "A signed magnitude imports a forbidden negative coordinate and loses fibre identity.", "two-held-spin-fibres", "Every electron occurrence carries exactly one of the two admitted held spin labels."),
    dimension("occupation", "same-fibre-cell-duplication", "Doubled same-fibre occupation violates admitted indistinguishability and exclusion.", "complementary-cell-occupation", "A cell retains at most one occurrence of each complementary fibre."),
    dimension("decomposition", "unstructured-spin-list", "An unstructured list cannot reconstruct pairs, surplus or width.", "complete-pairs-plus-held-surplus", "Every finite support decomposes exactly into complementary pairs and unmatched held fibres."),
    dimension("observation", "state-width-detached-from-support", "A detached multiplicity can contradict the complete electron support.", "support-compatible-spin-width", "Width is the successor of unmatched support and must preserve the exact parity relation."),
    dimension("extension", "species-specific-exception", "An exception or fitted table can select a measured state.", "no-extra-rule", "The same support, transfer, exclusion and decomposition law applies to every generated molecule."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    co_count = exact_electron_count(
        (
            NuclearPopulation(HeldLabel("element-symbol", "C"), PositiveCount(6), PositiveCount(1)),
            NuclearPopulation(HeldLabel("element-symbol", "O"), PositiveCount(8), PositiveCount(1)),
        ),
        HeldChargeTransfer(HeldLabel("electron-transfer", "empty-One"), EMPTY_ONE),
    )
    oxygen_anion_count = exact_electron_count(
        (NuclearPopulation(HeldLabel("element-symbol", "O"), PositiveCount(8), PositiveCount(2)),),
        HeldChargeTransfer(HeldLabel("electron-transfer", "adjoin-electron"), PositiveCount(1)),
    )
    co = build_complete_spin_organization("CO", co_count, PositiveCount(1))
    oxygen_anion = build_complete_spin_organization("O2-", oxygen_anion_count, PositiveCount(2))
    same_fibre_rejected = False
    try:
        SpinCell(
            HeldLabel("electron-support-cell", "tampered"),
            (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-a")),
        )
    except InadmissibleExactValue:
        same_fibre_rejected = True
    incompatible_width_rejected = False
    try:
        build_complete_spin_organization("tampered", PositiveCount(14), PositiveCount(2))
    except InadmissibleExactValue:
        incompatible_width_rejected = True
    return (
        ("neutral-electron-census", "C and O nuclear support forces fourteen electron occurrences without a charge scalar.", co.electron_count.value == 14),
        ("anion-electron-census", "O2 with one held adjoin action forces seventeen electron occurrences.", oxygen_anion.electron_count.value == 17),
        ("pair-held-decomposition", "Singlet and doublet widths reconstruct complete complementary-pair and held-surplus support.", len(co.cells) == 7 and len(oxygen_anion.cells) == 9),
        ("same-fibre-exclusion-control", "A cell containing the same held fibre twice rejects.", same_fibre_rejected),
        ("width-parity-control", "An even electron support with even spin width rejects.", incompatible_width_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "atomic-number-occurrence-support__held-directed-electron-transfer__complete-electron-occurrence-census__two-held-spin-fibres__complementary-cell-occupation__complete-pairs-plus-held-surplus__support-compatible-spin-width__no-extra-rule"


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "HeldChargeTransfer",
    "MolecularElectronOrganization",
    "NuclearPopulation",
    "OPERATIONAL_WITNESSES",
    "SpinCell",
    "build_complete_spin_organization",
    "exact_electron_count",
    "required_spin_width_parity",
)
