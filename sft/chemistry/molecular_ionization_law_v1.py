"""Fold-native exact molecular-ionization law for Chemistry PROP-007."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


def ordered_ionization_take(
    ionized_separated_height: PositiveRatio,
    neutral_bound_height: PositiveRatio,
) -> PositiveRatio:
    """Take the lower bound-state height from the higher separated state."""

    if not isinstance(ionized_separated_height, PositiveRatio) or not isinstance(neutral_bound_height, PositiveRatio):
        raise InadmissibleExactValue("ionization heights must be exact positive ratios")
    if ionized_separated_height.fraction <= neutral_bound_height.fraction:
        raise InadmissibleExactValue("ionization requires a strictly higher separated terminal state")
    difference = ionized_separated_height.fraction - neutral_bound_height.fraction
    return PositiveRatio.from_pair(difference.numerator, difference.denominator)


def least_adiabatic_take(
    neutral_bound_height: PositiveRatio,
    generated_ionic_terminal_heights: tuple[PositiveRatio, ...],
) -> PositiveRatio:
    """Choose the least positive terminal Take over the complete generated support."""

    if not isinstance(generated_ionic_terminal_heights, tuple) or not generated_ionic_terminal_heights:
        raise InadmissibleExactValue("adiabatic support requires a nonempty finite generated terminal set")
    takes = tuple(
        ordered_ionization_take(terminal, neutral_bound_height)
        for terminal in generated_ionic_terminal_heights
    )
    return min(takes, key=lambda value: value.fraction)


def vertical_not_below_adiabatic(
    neutral_bound_height: PositiveRatio,
    generated_ionic_terminal_heights: tuple[PositiveRatio, ...],
    held_geometry_terminal: PositiveRatio,
) -> bool:
    """A held-geometry terminal belongs to the complete set and cannot beat its least member."""

    if held_geometry_terminal not in generated_ionic_terminal_heights:
        raise InadmissibleExactValue("vertical terminal must belong to the generated ionic support")
    adiabatic = least_adiabatic_take(neutral_bound_height, generated_ionic_terminal_heights)
    vertical = ordered_ionization_take(held_geometry_terminal, neutral_bound_height)
    return vertical.fraction >= adiabatic.fraction


@dataclass(frozen=True)
class MolecularIonizationCarrier:
    species: HeldLabel
    initial_molecular_state: HeldLabel
    initial_conformation: HeldLabel
    resulting_ionic_state: HeldLabel
    removed_carrier: HeldLabel
    removal_orientation: HeldLabel
    ionization_path: HeldLabel
    condition: HeldLabel

    def __post_init__(self) -> None:
        required = (
            (self.species, "molecular-species"),
            (self.initial_molecular_state, "initial-molecular-state"),
            (self.initial_conformation, "initial-molecular-conformation"),
            (self.resulting_ionic_state, "resulting-ionic-state"),
            (self.removed_carrier, "removed-carrier"),
            (self.removal_orientation, "held-removal-orientation"),
            (self.ionization_path, "ionization-path"),
            (self.condition, "measurement-condition"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("molecular ionization carrier erased a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-CHEM-ELEM-ION-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    "SFT-CHEM-MOLECULAR-POLARIZABILITY-006",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "ionization-answer-with-erased-states",
        "An answer-only energy erases the neutral carrier and resulting ionic state.",
        "complete-neutral-to-ionic-carrier",
        "Species, initial state, conformation, removed carrier and resulting ion remain held.",
    ),
    dimension(
        "transformation", "signed-electron-subtraction",
        "A signed electron subtraction imports a negative proof magnitude.",
        "held-removal-and-positive-terminal-separation",
        "Removal is an orientation label and the terminal separated state lies positively above the bound state.",
    ),
    dimension(
        "magnitude", "imported-orbital-energy-equality",
        "An imported orbital theorem does not force the complete many-carrier state difference.",
        "ordered-positive-final-from-initial-Take",
        "Ionization energy is the exact positive Take from bound initial height to separated terminal height.",
    ),
    dimension(
        "path", "adiabatic-vertical-state-conflation",
        "Erasing geometry custody conflates two different terminal-state classes.",
        "least-adiabatic-and-held-geometry-vertical-paths",
        "Adiabatic is the least generated terminal Take; vertical retains the initial geometry.",
    ),
    dimension(
        "order", "unconstrained-vertical-reordering",
        "A held-geometry member cannot be declared below the least complete-support member.",
        "vertical-not-below-adiabatic",
        "Set inclusion forces every vertical Take to be at least the adiabatic least Take.",
    ),
    dimension(
        "prediction", "ionization-value-readable-before-seal",
        "Readable energy values could select the law or carrier boundary.",
        "value-free-carrier-and-operation-seal",
        "Complete carrier identities and exact operations seal before any energy inscription opens.",
    ),
    dimension(
        "record", "selected-isotopologue-or-favorable-row",
        "A selected subset can conceal isotope, spin or polarity dependence.",
        "complete-nine-diatomic-NIST-vector",
        "All nine preregistered neutral diatomic carriers remain in source order.",
    ),
    dimension(
        "extension", "species-fit-or-residual-correction",
        "A species coefficient or residual correction is a fitted parameter.",
        "one-ionization-law-no-extra-rule",
        "One ordered Take and typed path law exhausts the registered vector.",
    ),
)


EXACT_RESULT = (
    "complete-neutral-to-ionic-carrier__held-removal-and-positive-terminal-separation__"
    "ordered-positive-final-from-initial-Take__least-adiabatic-and-held-geometry-vertical-paths__"
    "vertical-not-below-adiabatic__value-free-carrier-and-operation-seal__"
    "complete-nine-diatomic-NIST-vector__one-ionization-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    initial = PositiveRatio.from_pair(3, 1)
    terminals = (
        PositiveRatio.from_pair(8, 1),
        PositiveRatio.from_pair(6, 1),
        PositiveRatio.from_pair(7, 1),
    )
    invalid_rejected = False
    missing_vertical_rejected = False
    try:
        ordered_ionization_take(initial, terminals[0])
    except InadmissibleExactValue:
        invalid_rejected = True
    try:
        vertical_not_below_adiabatic(initial, terminals, PositiveRatio.from_pair(9, 1))
    except InadmissibleExactValue:
        missing_vertical_rejected = True
    return (
        ("ordered-positive-Take", "Eight above three forces an exact energy requirement of five.", ordered_ionization_take(terminals[0], initial).fraction == Fraction(5, 1)),
        ("least-adiabatic-terminal", "The least complete-support terminal six forces adiabatic Take three.", least_adiabatic_take(initial, terminals).fraction == Fraction(3, 1)),
        ("vertical-order", "Every held-geometry member is not below the least adiabatic member.", vertical_not_below_adiabatic(initial, terminals, terminals[2])),
        ("reversed-order-rejected", "A terminal below the declared initial height is rejected.", invalid_rejected),
        ("missing-vertical-rejected", "A vertical state outside complete generated support is rejected.", missing_vertical_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "MolecularIonizationCarrier",
    "OPERATIONAL_WITNESSES", "least_adiabatic_take", "ordered_ionization_take",
    "vertical_not_below_adiabatic",
)
