"""Fold-native exact molecular electron-affinity law for Chemistry PROP-008."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ElectronAffinityDifference:
    state_order_orientation: HeldLabel
    magnitude: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if (
            not isinstance(self.state_order_orientation, HeldLabel)
            or self.state_order_orientation.family != "electron-affinity-state-order"
            or not isinstance(self.magnitude, (PositiveRatio, EmptyOne))
        ):
            raise InadmissibleExactValue("electron affinity requires held state order and an exact Fold magnitude")


def exact_electron_affinity_difference(
    neutral_plus_electron_height: PositiveRatio,
    resulting_anion_height: PositiveRatio,
) -> ElectronAffinityDifference:
    """Replace a conventional signed EA scalar by held order plus positive Take."""

    if not isinstance(neutral_plus_electron_height, PositiveRatio) or not isinstance(resulting_anion_height, PositiveRatio):
        raise InadmissibleExactValue("electron-affinity state heights must be exact positive ratios")
    neutral, anion = neutral_plus_electron_height.fraction, resulting_anion_height.fraction
    if neutral == anion:
        return ElectronAffinityDifference(
            HeldLabel("electron-affinity-state-order", "coincident-no-affinity-distinction"),
            EMPTY_ONE,
        )
    if neutral > anion:
        difference = neutral - anion
        orientation = "anion-below-neutral-bound-attachment"
    else:
        difference = anion - neutral
        orientation = "anion-above-neutral-unbound-autodetachment"
    return ElectronAffinityDifference(
        HeldLabel("electron-affinity-state-order", orientation),
        PositiveRatio.from_pair(difference.numerator, difference.denominator),
    )


@dataclass(frozen=True)
class MolecularElectronAffinityCarrier:
    species: HeldLabel
    initial_molecular_state: HeldLabel
    resulting_anion_state: HeldLabel
    gained_carrier: HeldLabel
    gain_orientation: HeldLabel
    gain_path: HeldLabel
    condition: HeldLabel

    def __post_init__(self) -> None:
        required = (
            (self.species, "molecular-species"),
            (self.initial_molecular_state, "initial-molecular-state"),
            (self.resulting_anion_state, "resulting-anion-state"),
            (self.gained_carrier, "gained-carrier"),
            (self.gain_orientation, "held-gain-orientation"),
            (self.gain_path, "electron-gain-path"),
            (self.condition, "measurement-condition"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("molecular electron-affinity carrier erased a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-CHEM-ELEM-ION-001",
    "SFT-CHEM-REDOX-COUPLING-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    "SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "electron-affinity-answer-with-erased-states",
        "An answer-only scalar erases the neutral molecule and resulting anion.",
        "complete-neutral-electron-anion-carrier",
        "Neutral carrier, gained electron and resulting anion state all remain held.",
    ),
    dimension(
        "gain", "signed-electron-addition",
        "A signed addition imports a negative proof magnitude.",
        "held-electron-gain-orientation",
        "Electron gain is a held transfer orientation with a positive carrier count.",
    ),
    dimension(
        "magnitude", "conventional-signed-affinity-scalar",
        "One signed number conflates state order with energy magnitude.",
        "held-order-plus-positive-state-Take",
        "State order is held and the energy distinction is the exact positive higher Take lower.",
    ),
    dimension(
        "boundary", "bound-anion-only-domain",
        "Discarding unbound anions selects favorable conventional signs.",
        "bound-unbound-and-EmptyOne-boundary",
        "Bound, unbound and coincident states share one orientation-and-magnitude law.",
    ),
    dimension(
        "prediction", "affinity-value-or-orientation-readable-before-seal",
        "A readable sign or magnitude could select the representation or carrier subset.",
        "value-and-orientation-free-carrier-seal",
        "Complete identities and the exact representation seal before state order or magnitude opens.",
    ),
    dimension(
        "record", "selected-positive-or-favorable-molecular-row",
        "A selected subset can conceal unbound carriers and source diversity.",
        "complete-NIST-molecular-experimental-vector",
        "Every molecular CCCBDB page with an explicit experimental value remains in catalog order.",
    ),
    dimension(
        "uncertainty", "central-value-with-erased-uncertainty",
        "Dropping uncertainty weakens the empirical record.",
        "complete-source-uncertainty-custody",
        "Every explicit uncertainty and every disclosed rounding enclosure remains attached.",
    ),
    dimension(
        "extension", "species-fit-or-sign-correction",
        "A species coefficient or sign correction is a fitted parameter.",
        "one-affinity-law-no-extra-rule",
        "One held-order and positive-Take law exhausts bound and unbound records.",
    ),
)


EXACT_RESULT = (
    "complete-neutral-electron-anion-carrier__held-electron-gain-orientation__"
    "held-order-plus-positive-state-Take__bound-unbound-and-EmptyOne-boundary__"
    "value-and-orientation-free-carrier-seal__complete-NIST-molecular-experimental-vector__"
    "complete-source-uncertainty-custody__one-affinity-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    higher, lower = PositiveRatio.from_pair(8, 1), PositiveRatio.from_pair(3, 1)
    bound = exact_electron_affinity_difference(higher, lower)
    unbound = exact_electron_affinity_difference(lower, higher)
    coincident = exact_electron_affinity_difference(lower, lower)
    return (
        ("bound-orientation", "Neutral above anion forces bound attachment orientation and positive Take five.", bound.state_order_orientation.label == "anion-below-neutral-bound-attachment" and isinstance(bound.magnitude, PositiveRatio) and bound.magnitude.fraction == Fraction(5, 1)),
        ("unbound-orientation", "Anion above neutral forces unbound autodetachment orientation and positive Take five.", unbound.state_order_orientation.label == "anion-above-neutral-unbound-autodetachment" and isinstance(unbound.magnitude, PositiveRatio) and unbound.magnitude.fraction == Fraction(5, 1)),
        ("coincident-boundary", "Coincident state heights produce structural EmptyOne rather than numerical zero.", coincident.state_order_orientation.label == "coincident-no-affinity-distinction" and isinstance(coincident.magnitude, EmptyOne)),
        ("one-law", "Bound and unbound state orders use the same ordered positive distinction operation.", isinstance(bound.magnitude, PositiveRatio) and bound.magnitude == unbound.magnitude),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ElectronAffinityDifference",
    "MolecularElectronAffinityCarrier", "OPERATIONAL_WITNESSES", "exact_electron_affinity_difference",
)
