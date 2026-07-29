"""Fold-native electrochemical work and reaction-direction law (ECHEM-005)."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value: Fraction) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class ElectrochemicalWorkAccount:
    cell_identity: HeldLabel
    chemical_path: HeldLabel
    electrical_path: HeldLabel
    condition: HeldLabel
    reaction_orientation: HeldLabel
    transferred_carriers: PositiveCount
    potential_separation: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if self.cell_identity.family != "electrochemical-cell":
            raise InadmissibleExactValue("electrochemical work requires one held cell identity")
        if self.chemical_path.family != "chemical-reaction-path" or self.electrical_path.family != "electrical-transfer-path":
            raise InadmissibleExactValue("chemical and electrical transfer paths must both remain held")
        if self.condition.family != "electrochemical-condition":
            raise InadmissibleExactValue("electrochemical work requires one held condition")
        allowed = {"forward", "reverse", "equilibrium"}
        if self.reaction_orientation.family != "reaction-orientation" or self.reaction_orientation.label not in allowed:
            raise InadmissibleExactValue("reaction direction must be a held forward, reverse or equilibrium label")
        if not isinstance(self.transferred_carriers, PositiveCount):
            raise InadmissibleExactValue("transferred carrier count must be exact and positive")
        if self.reaction_orientation.label == "equilibrium":
            if self.potential_separation != EMPTY_ONE:
                raise InadmissibleExactValue("equilibrium must close potential separation to EmptyOne")
        elif not isinstance(self.potential_separation, PositiveRatio):
            raise InadmissibleExactValue("directed reaction work requires positive exact potential separation")


@dataclass(frozen=True)
class ElectrochemicalWorkResult:
    orientation: HeldLabel
    work_magnitude: PositiveRatio | EmptyOne
    chemical_path: HeldLabel
    electrical_path: HeldLabel
    transferred_carriers: PositiveCount
    condition: HeldLabel


def electrochemical_work(account: ElectrochemicalWorkAccount) -> ElectrochemicalWorkResult:
    if account.potential_separation == EMPTY_ONE:
        magnitude: PositiveRatio | EmptyOne = EMPTY_ONE
    else:
        magnitude = _ratio(account.potential_separation.fraction * account.transferred_carriers.value)
    return ElectrochemicalWorkResult(
        account.reaction_orientation,
        magnitude,
        account.chemical_path,
        account.electrical_path,
        account.transferred_carriers,
        account.condition,
    )


def reverse_work_account(account: ElectrochemicalWorkAccount) -> ElectrochemicalWorkAccount:
    reverse = {"forward": "reverse", "reverse": "forward", "equilibrium": "equilibrium"}[account.reaction_orientation.label]
    return ElectrochemicalWorkAccount(
        account.cell_identity,
        HeldLabel("chemical-reaction-path", account.chemical_path.label + "-reverse"),
        HeldLabel("electrical-transfer-path", account.electrical_path.label + "-reverse"),
        account.condition,
        HeldLabel("reaction-orientation", reverse),
        account.transferred_carriers,
        account.potential_separation,
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-PLASMA-COLLECTIVE-001", "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-REDOX-COUPLING-001", "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("custody", "anonymous-energy-number", "An anonymous energy loses its reaction and cell.", "complete-cell-chemical-electrical-custody", "Cell, chemical path and electrical path remain held."),
    dimension("carrier", "uncounted-charge", "Uncounted charge cannot establish chemical work.", "positive-counted-transfer-carriers", "Every transferred distinction is counted positively."),
    dimension("potential", "signed-voltage-premise", "A signed voltage imports negative proof magnitude.", "positive-potential-separation-with-held-direction", "Magnitude is positive and direction is a held label."),
    dimension("composition", "free-energy-postulate", "A named free-energy formula does not derive work custody.", "exact-carrier-potential-product", "Work is forced as carrier count composed with potential separation."),
    dimension("direction", "unoriented-work", "Unoriented work cannot determine the reaction path.", "held-work-reaction-correspondence", "Forward and reverse directions are retained structurally."),
    dimension("equilibrium", "numerical-zero-work", "Numerical zero is not a native proof magnitude.", "structural-EmptyOne-equilibrium", "Coincidence closes the work distinction to EmptyOne."),
    dimension("record", "selected-cell-result", "A selected result can hide conditions and uncertainty.", "complete-cell-work-equilibrium-vector", "Every registered potential, constant, work and uncertainty row remains downstream."),
    dimension("reverse", "irreversible-sign-change", "A sign change cannot reconstruct both transfer paths.", "exact-path-reversal-preserves-positive-work", "Reversal swaps held direction and preserves the exact magnitude."),
)

EXACT_RESULT = "complete-cell-chemical-electrical-custody__positive-counted-transfer-carriers__positive-potential-separation-with-held-direction__exact-carrier-potential-product__held-work-reaction-correspondence__structural-EmptyOne-equilibrium__complete-cell-work-equilibrium-vector__exact-path-reversal-preserves-positive-work"


def _account(direction: str, potential: PositiveRatio | EmptyOne) -> ElectrochemicalWorkAccount:
    return ElectrochemicalWorkAccount(
        HeldLabel("electrochemical-cell", "test-cell"), HeldLabel("chemical-reaction-path", "chemical"),
        HeldLabel("electrical-transfer-path", "electrical"), HeldLabel("electrochemical-condition", "held-condition"),
        HeldLabel("reaction-orientation", direction), PositiveCount(2), potential,
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    forward = _account("forward", PositiveRatio.from_pair(3, 2))
    result = electrochemical_work(forward)
    reverse = reverse_work_account(forward)
    equilibrium = electrochemical_work(_account("equilibrium", EMPTY_ONE))
    invalid = False
    try:
        _account("forward", EMPTY_ONE)
    except InadmissibleExactValue:
        invalid = True
    return (
        ("exact-product", "Two carriers at three-halves separation yield three exact work parts.", result.work_magnitude.fraction == 3),
        ("positive-only", "Directed work magnitude remains exact and positive.", isinstance(result.work_magnitude, PositiveRatio)),
        ("chemical-custody", "Chemical path remains held.", result.chemical_path == forward.chemical_path),
        ("electrical-custody", "Electrical path remains held.", result.electrical_path == forward.electrical_path),
        ("direction", "Forward reaction orientation remains held.", result.orientation.label == "forward"),
        ("equilibrium", "Equilibrium closes to EmptyOne.", equilibrium.work_magnitude == EMPTY_ONE),
        ("reverse", "Reversal changes held direction and preserves magnitude.", reverse.reaction_orientation.label == "reverse" and electrochemical_work(reverse).work_magnitude == result.work_magnitude),
        ("invalid-directed-empty", "Directed work without positive separation halts.", invalid),
    )


OPERATIONAL_WITNESSES = _witnesses()

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ElectrochemicalWorkAccount", "ElectrochemicalWorkResult", "OPERATIONAL_WITNESSES", "electrochemical_work", "reverse_work_account")
