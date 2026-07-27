"""Fold-native molecular exclusion and exchange organization for ELEC-006."""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


PRESERVING_EXCHANGE = HeldLabel("exchange-class", "preserving-exchange")
ALTERNATING_EXCHANGE = HeldLabel("exchange-class", "alternating-exchange")
SAME_CELL_ADMITTED = HeldLabel("same-cell-status", "same-cell-admitted")
SAME_CELL_EXCLUDED = HeldLabel("same-cell-status", "same-cell-excluded")


def exchange_product(left: HeldLabel, right: HeldLabel) -> HeldLabel:
    """Compose the complete two-fibre exchange table without signed scalars."""

    allowed = {PRESERVING_EXCHANGE, ALTERNATING_EXCHANGE}
    if left not in allowed or right not in allowed:
        raise InadmissibleExactValue("exchange composition requires one of the two generated held fibres")
    return PRESERVING_EXCHANGE if left == right else ALTERNATING_EXCHANGE


@dataclass(frozen=True)
class MolecularElectronPairState:
    molecular_carrier: HeldLabel
    state_identity: HeldLabel
    positive_spin_multiplicity: PositiveCount
    spin_exchange: HeldLabel
    spatial_exchange: HeldLabel
    total_exchange: HeldLabel
    same_cell_status: HeldLabel

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("electron-pair state requires one molecular carrier")
        if self.state_identity.family != "molecular-electronic-state":
            raise InadmissibleExactValue("electron-pair state requires a retained molecular-state identity")
        if self.positive_spin_multiplicity.value not in {1, 3}:
            raise InadmissibleExactValue("a two-electron spin support has exactly the generated One or threefold sector")
        required_spin = (
            ALTERNATING_EXCHANGE
            if self.positive_spin_multiplicity == PositiveCount(1)
            else PRESERVING_EXCHANGE
        )
        required_spatial = (
            PRESERVING_EXCHANGE
            if self.positive_spin_multiplicity == PositiveCount(1)
            else ALTERNATING_EXCHANGE
        )
        if self.spin_exchange != required_spin or self.spatial_exchange != required_spatial:
            raise InadmissibleExactValue("spin and spatial exchange fibres must be complementary")
        if exchange_product(self.spin_exchange, self.spatial_exchange) != ALTERNATING_EXCHANGE:
            raise InadmissibleExactValue("the total identical-electron word must remain alternating")
        if self.total_exchange != ALTERNATING_EXCHANGE:
            raise InadmissibleExactValue("the declared total exchange class differs from the forced composition")
        required_same_cell = (
            SAME_CELL_ADMITTED if self.spatial_exchange == PRESERVING_EXCHANGE else SAME_CELL_EXCLUDED
        )
        if self.same_cell_status != required_same_cell:
            raise InadmissibleExactValue("same-cell support is fixed by the spatial exchange fibre")


def pair_state_from_multiplicity(
    molecule: str,
    state_identity: str,
    positive_spin_multiplicity: PositiveCount,
) -> MolecularElectronPairState:
    if positive_spin_multiplicity == PositiveCount(1):
        spin_exchange = ALTERNATING_EXCHANGE
        spatial_exchange = PRESERVING_EXCHANGE
        same_cell = SAME_CELL_ADMITTED
    elif positive_spin_multiplicity == PositiveCount(3):
        spin_exchange = PRESERVING_EXCHANGE
        spatial_exchange = ALTERNATING_EXCHANGE
        same_cell = SAME_CELL_EXCLUDED
    else:
        raise InadmissibleExactValue("two-electron pair multiplicity is outside the complete four-word spin census")
    return MolecularElectronPairState(
        HeldLabel("molecular-carrier", molecule),
        HeldLabel("molecular-electronic-state", state_identity),
        positive_spin_multiplicity,
        spin_exchange,
        spatial_exchange,
        ALTERNATING_EXCHANGE,
        same_cell,
    )


def explicit_occupancy_compatible(
    state: MolecularElectronPairState,
    positive_occupancy: PositiveCount,
) -> bool:
    """Decide explicit one-or-pair orbital occupation at the declared support."""

    if positive_occupancy.value == 1:
        return True
    if positive_occupancy.value == 2:
        return state.same_cell_status == SAME_CELL_ADMITTED
    raise InadmissibleExactValue("one orbital support cannot retain a third identical-electron occurrence")


@dataclass(frozen=True)
class SameSupportExchangePair:
    molecular_carrier: HeldLabel
    support_identity: HeldLabel
    singlet_state: MolecularElectronPairState
    triplet_state: MolecularElectronPairState

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("exchange pair requires one molecular carrier")
        if self.support_identity.family != "molecular-orbital-support":
            raise InadmissibleExactValue("exchange pair requires one retained orbital support")
        if self.singlet_state.molecular_carrier != self.molecular_carrier or self.triplet_state.molecular_carrier != self.molecular_carrier:
            raise InadmissibleExactValue("exchange-paired states must retain one molecular carrier")
        if self.singlet_state.positive_spin_multiplicity != PositiveCount(1):
            raise InadmissibleExactValue("the One-width member must be the alternating spin sector")
        if self.triplet_state.positive_spin_multiplicity != PositiveCount(3):
            raise InadmissibleExactValue("the three-width member must be the preserving spin sector")
        if self.singlet_state.state_identity == self.triplet_state.state_identity:
            raise InadmissibleExactValue("complementary exchange sectors require distinct retained state identities")
        if self.singlet_state.spatial_exchange == self.triplet_state.spatial_exchange:
            raise InadmissibleExactValue("same-support exchange partners must retain complementary spatial fibres")


def build_same_support_pair(
    molecule: str,
    support_identity: str,
    singlet_state_identity: str,
    triplet_state_identity: str,
) -> SameSupportExchangePair:
    carrier = HeldLabel("molecular-carrier", molecule)
    return SameSupportExchangePair(
        carrier,
        HeldLabel("molecular-orbital-support", support_identity),
        pair_state_from_multiplicity(molecule, singlet_state_identity, PositiveCount(1)),
        pair_state_from_multiplicity(molecule, triplet_state_identity, PositiveCount(3)),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "cross-molecule-pair",
        "A cross-molecule word does not define one molecular exchange organization.",
        "one-molecule-electron-pair",
        "Every exchange comparison retains one molecular carrier and one pair of identical electrons.",
    ),
    dimension(
        "identity",
        "named-distinguishable-electrons",
        "Naming identical electrons imports a distinction absent from every observable exchange trace.",
        "exchange-equivalent-constituents",
        "The admitted indistinguishability law identifies the pair by exchange-equivalent complete traces.",
    ),
    dimension(
        "total",
        "free-total-exchange-label",
        "A freely chosen total exchange class violates the admitted identical-fermion law.",
        "alternating-total-word",
        "Every identical-electron pair retains the alternating total exchange class.",
    ),
    dimension(
        "spin",
        "imported-spin-sign-function",
        "A signed or continuum wavefunction is outside the exact Fold proof domain.",
        "complete-one-and-three-spin-sectors",
        "The complete two-label spin census forces one alternating and three preserving readings.",
    ),
    dimension(
        "composition",
        "independent-spin-and-space-labels",
        "Independent labels can compose to a preserving total word and violate fermionic exchange.",
        "complementary-spin-spatial-fibres",
        "Exactly one of spin and spatial exchange preserves while the other alternates.",
    ),
    dimension(
        "same_cell",
        "selected-occupancy-cap",
        "A selected cap is a free rule rather than an exclusion consequence.",
        "spatial-exchange-controlled-occupation",
        "Preserving spatial support admits the paired cell; alternating spatial support excludes it.",
    ),
    dimension(
        "record",
        "selected-favourable-spin-states",
        "Selected states cannot establish the complete molecular pair organization.",
        "complete-state-and-exchange-pair-record",
        "Every registered state, same-cell record, paired support and adverse ordering is retained.",
    ),
    dimension(
        "extension",
        "species-or-energy-order-exception",
        "A species lookup or fixed energy-order sign would add a target-selected rule.",
        "pairwise-successor-with-no-extra-rule",
        "The same complementary held-label law applies to every added identical-electron pair and support.",
    ),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    singlet = pair_state_from_multiplicity("H2", "singlet", PositiveCount(1))
    triplet = pair_state_from_multiplicity("H2", "triplet", PositiveCount(3))
    same_support = build_same_support_pair("H2", "2s-sigma", "singlet", "triplet")
    third_rejected = False
    try:
        explicit_occupancy_compatible(singlet, PositiveCount(3))
    except InadmissibleExactValue:
        third_rejected = True
    wrong_pair_rejected = not explicit_occupancy_compatible(triplet, PositiveCount(2))
    return (
        (
            "singlet-sector",
            "The One-width spin sector is alternating, its spatial complement preserves and same-cell pairing is admitted.",
            singlet.spin_exchange == ALTERNATING_EXCHANGE
            and singlet.spatial_exchange == PRESERVING_EXCHANGE
            and singlet.same_cell_status == SAME_CELL_ADMITTED,
        ),
        (
            "triplet-sector",
            "The three-width spin sector preserves, its spatial complement alternates and same-cell pairing is excluded.",
            triplet.spin_exchange == PRESERVING_EXCHANGE
            and triplet.spatial_exchange == ALTERNATING_EXCHANGE
            and triplet.same_cell_status == SAME_CELL_EXCLUDED,
        ),
        (
            "alternating-total",
            "Both complementary compositions retain the alternating total electron-pair word.",
            singlet.total_exchange == triplet.total_exchange == ALTERNATING_EXCHANGE,
        ),
        (
            "same-support-pair",
            "One support can retain distinct complementary singlet and triplet state identities.",
            same_support.singlet_state.state_identity != same_support.triplet_state.state_identity,
        ),
        (
            "same-cell-control",
            "An explicit paired cell is rejected in the alternating spatial sector.",
            wrong_pair_rejected,
        ),
        (
            "third-occurrence-control",
            "A third identical occurrence in one orbital support rejects.",
            third_rejected,
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "one-molecule-electron-pair__exchange-equivalent-constituents__alternating-total-word__"
    "complete-one-and-three-spin-sectors__complementary-spin-spatial-fibres__"
    "spatial-exchange-controlled-occupation__complete-state-and-exchange-pair-record__"
    "pairwise-successor-with-no-extra-rule"
)


__all__ = (
    "ALTERNATING_EXCHANGE",
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "MolecularElectronPairState",
    "OPERATIONAL_WITNESSES",
    "PRESERVING_EXCHANGE",
    "SAME_CELL_ADMITTED",
    "SAME_CELL_EXCLUDED",
    "SameSupportExchangePair",
    "build_same_support_pair",
    "exchange_product",
    "explicit_occupancy_compatible",
    "pair_state_from_multiplicity",
)
