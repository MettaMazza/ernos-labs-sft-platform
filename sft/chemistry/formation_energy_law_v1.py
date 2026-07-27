"""Fold-native exact molecular formation-energy relation for Chemistry PROP-013.

The executable law has no measured formation energy, imported thermodynamic
reference value, fitted atomic contribution, species coefficient or target
source.  A formation record retains the product state and the complete named
reference-state composition.  Their exact order is a held orientation and
their separation is a positive magnitude; equality is structural EmptyOne.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def exact_reference_state_composition(
    constituent_reference_states: tuple[PositiveRatio, ...],
) -> PositiveRatio:
    """Compose a nonempty finite reference state without a zero initializer."""

    if not isinstance(constituent_reference_states, tuple) or not constituent_reference_states:
        raise InadmissibleExactValue("formation reference requires at least one exact constituent state")
    if any(not isinstance(state, PositiveRatio) for state in constituent_reference_states):
        raise InadmissibleExactValue("every formation reference constituent must be exact and positive")
    total = constituent_reference_states[0].fraction
    for state in constituent_reference_states[1:]:
        total += state.fraction
    return PositiveRatio.from_pair(total.numerator, total.denominator)


def exact_formation_state_relation(
    product_state: PositiveRatio,
    reference_state: PositiveRatio,
) -> tuple[HeldLabel, PositiveRatio | EmptyOne]:
    """Return held state order and exact positive separation."""

    if not isinstance(product_state, PositiveRatio) or not isinstance(reference_state, PositiveRatio):
        raise InadmissibleExactValue("formation relation requires two exact positive states")
    if product_state.fraction == reference_state.fraction:
        return HeldLabel("formation-state-orientation", "product-reference-equal"), EMPTY_ONE
    if product_state.fraction > reference_state.fraction:
        delta = product_state.fraction - reference_state.fraction
        orientation = "product-above-reference"
    else:
        delta = reference_state.fraction - product_state.fraction
        orientation = "product-below-reference"
    return HeldLabel("formation-state-orientation", orientation), PositiveRatio.from_pair(delta.numerator, delta.denominator)


def shared_state_extension_preserves_formation_relation(
    product_state: PositiveRatio,
    reference_state: PositiveRatio,
    shared_state: PositiveRatio,
) -> bool:
    """Adding the same exact state to both endpoints preserves the relation."""

    if not isinstance(shared_state, PositiveRatio):
        raise InadmissibleExactValue("shared formation extension must be exact and positive")
    orientation, magnitude = exact_formation_state_relation(product_state, reference_state)
    product = product_state.fraction + shared_state.fraction
    reference = reference_state.fraction + shared_state.fraction
    extended_orientation, extended_magnitude = exact_formation_state_relation(
        PositiveRatio.from_pair(product.numerator, product.denominator),
        PositiveRatio.from_pair(reference.numerator, reference.denominator),
    )
    return extended_orientation == orientation and extended_magnitude == magnitude


def repeated_formation_relation(
    product_state: PositiveRatio,
    reference_state: PositiveRatio,
    repetition: PositiveCount,
) -> tuple[HeldLabel, PositiveRatio | EmptyOne]:
    """Equal positive repetition scales the separation and retains its order."""

    if not isinstance(repetition, PositiveCount):
        raise InadmissibleExactValue("formation repetition requires a positive count")
    product = product_state.fraction * repetition.value
    reference = reference_state.fraction * repetition.value
    return exact_formation_state_relation(
        PositiveRatio.from_pair(product.numerator, product.denominator),
        PositiveRatio.from_pair(reference.numerator, reference.denominator),
    )


@dataclass(frozen=True)
class MolecularFormationEnergyCarrier:
    product_identity: HeldLabel
    product_state: HeldLabel
    constituent_identities: tuple[HeldLabel, ...]
    constituent_reference_states: tuple[HeldLabel, ...]
    reference_state_convention: HeldLabel
    temperature_reference: HeldLabel
    phase_identity: HeldLabel
    energy_unit: HeldLabel

    def __post_init__(self) -> None:
        if not self.constituent_identities or len(self.constituent_identities) != len(self.constituent_reference_states):
            raise InadmissibleExactValue("formation carrier requires one reference state per constituent")
        if any(not isinstance(value, HeldLabel) or value.family != "chemical-constituent" for value in self.constituent_identities):
            raise InadmissibleExactValue("formation carrier lost a constituent identity")
        if any(not isinstance(value, HeldLabel) or value.family != "constituent-reference-state" for value in self.constituent_reference_states):
            raise InadmissibleExactValue("formation carrier lost a constituent reference state")
        required = (
            (self.product_identity, "molecular-product"),
            (self.product_state, "molecular-product-state"),
            (self.reference_state_convention, "thermochemical-reference-state-convention"),
            (self.temperature_reference, "temperature-reference"),
            (self.phase_identity, "phase-identity"),
            (self.energy_unit, "held-energy-unit"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("formation carrier lost a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MEAS-FORMULA-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-BOND-DISSOCIATION-ENERGY-002",
    "SFT-CHEM-INTERMOLECULAR-BINDING-011",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "answer-only-formation-number", "A bare number erases product, phase, reference and condition.", "complete-product-reference-state-carrier", "Product and every reference-state constituent remain held."),
    dimension("reference", "imported-or-fitted-atomic-reference", "An imported or fitted reference lets external values select the relation.", "exact-named-constituent-reference-composition", "The complete named reference state composes exactly from positive retained states."),
    dimension("orientation", "signed-formation-proof-number", "A signed proof number imports negatives and loses state order.", "held-product-reference-state-order", "Above, below and equality are held structural relations."),
    dimension("magnitude", "species-coefficient-or-target-value", "A species coefficient or target value is a fitted parameter.", "exact-positive-state-separation", "Unequal states force their exact positive separation."),
    dimension("absence", "numerical-zero-for-equality-or-blank", "Numerical zero is not an SFT value and a source blank is not a measured equality.", "equality-or-unmeasured-as-distinct-structural-EmptyOne", "Equal state support and absent measurement are separately recorded structural absences."),
    dimension("prediction", "formation-values-readable-before-seal", "Readable values could select the law, reference or species subset.", "value-free-complete-formation-identity-seal", "All product and reference identities seal before any value or orientation opens."),
    dimension("record", "favorable-species-temperature-or-sign-subset", "Selecting only convenient values conceals blanks and opposite orientations.", "complete-values-blanks-orientations-and-reference-custody", "The complete official source surface and reference-state page remain in custody."),
    dimension("extension", "new-coefficient-per-added-constituent", "A new coefficient per constituent destroys zero-parameter closure.", "one-relation-with-depth-independent-shared-state-extension", "A shared state extension preserves the exact relation without a new rule."),
)


EXACT_RESULT = (
    "complete-product-reference-state-carrier__exact-named-constituent-reference-composition__"
    "held-product-reference-state-order__exact-positive-state-separation__"
    "equality-or-unmeasured-as-distinct-structural-EmptyOne__value-free-complete-formation-identity-seal__"
    "complete-values-blanks-orientations-and-reference-custody__one-relation-with-depth-independent-shared-state-extension"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    reference = exact_reference_state_composition((PositiveRatio.from_pair(5, 2), PositiveRatio.from_pair(7, 3)))
    below_orientation, below = exact_formation_state_relation(PositiveRatio.from_pair(4, 1), reference)
    above_orientation, above = exact_formation_state_relation(PositiveRatio.from_pair(6, 1), reference)
    equal_orientation, equal = exact_formation_state_relation(reference, reference)
    repeated_orientation, repeated = repeated_formation_relation(PositiveRatio.from_pair(4, 1), reference, PositiveCount(3))
    return (
        ("exact-reference-composition", "The two reference constituents compose to 29/6.", reference.fraction == Fraction(29, 6)),
        ("held-below-orientation", "Product 4 is below reference 29/6 by 5/6.", below_orientation.label == "product-below-reference" and isinstance(below, PositiveRatio) and below.fraction == Fraction(5, 6)),
        ("held-above-orientation", "Product 6 is above reference 29/6 by 7/6.", above_orientation.label == "product-above-reference" and isinstance(above, PositiveRatio) and above.fraction == Fraction(7, 6)),
        ("structural-equality", "Equal endpoints close to structural EmptyOne.", equal_orientation.label == "product-reference-equal" and isinstance(equal, EmptyOne)),
        ("shared-state-invariance", "A shared exact state preserves order and separation.", shared_state_extension_preserves_formation_relation(PositiveRatio.from_pair(4, 1), reference, PositiveRatio.from_pair(11, 5))),
        ("positive-repetition", "Three repetitions retain the below orientation and scale 5/6 to 5/2.", repeated_orientation == below_orientation and isinstance(repeated, PositiveRatio) and repeated.fraction == Fraction(5, 2)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "MolecularFormationEnergyCarrier", "exact_formation_state_relation",
    "exact_reference_state_composition", "repeated_formation_relation",
    "shared_state_extension_preserves_formation_relation",
)
