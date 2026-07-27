"""Fold-native exact molecular magnetic-response law for Chemistry PROP-012.

No measured molecular moment, susceptibility, fitted g-factor, continuum field
equation, species coefficient or target source is available here.  Opposing
magnetic directions are held labels.  Balanced support closes structurally to
EmptyOne; an unbalanced support has one held orientation and one positive
magnitude.  Moment and susceptibility are exact positive response ratios.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def exact_orientation_excess(
    side_a: PositiveCount,
    side_b: PositiveCount,
    orientation_a: HeldLabel,
    orientation_b: HeldLabel,
) -> tuple[HeldLabel, PositiveCount | EmptyOne]:
    """Close equal opposed support or retain the positive unmatched side."""

    if not isinstance(side_a, PositiveCount) or not isinstance(side_b, PositiveCount):
        raise InadmissibleExactValue("magnetic support requires two positive counts")
    if (
        not isinstance(orientation_a, HeldLabel)
        or not isinstance(orientation_b, HeldLabel)
        or orientation_a.family != "magnetic-orientation"
        or orientation_b.family != "magnetic-orientation"
        or orientation_a == orientation_b
    ):
        raise InadmissibleExactValue("two distinct held magnetic orientations are required")
    if side_a.value == side_b.value:
        return HeldLabel("magnetic-response-orientation", "balanced-closed"), EMPTY_ONE
    if side_a.value > side_b.value:
        return HeldLabel("magnetic-response-orientation", orientation_a.label), PositiveCount(side_a.value - side_b.value)
    return HeldLabel("magnetic-response-orientation", orientation_b.label), PositiveCount(side_b.value - side_a.value)


def exact_moment_ratio(
    retained_response_displacements: PositiveCount,
    angular_recurrences: PositiveCount,
) -> PositiveRatio:
    """Return exact positive magnetic response per angular recurrence."""

    if not isinstance(retained_response_displacements, PositiveCount) or not isinstance(angular_recurrences, PositiveCount):
        raise InadmissibleExactValue("molecular moment requires two positive counts")
    return PositiveRatio.from_pair(retained_response_displacements.value, angular_recurrences.value)


def exact_susceptibility_ratio(
    induced_response: PositiveRatio,
    field_acts: PositiveCount,
) -> PositiveRatio:
    """Return exact positive induced response per positive applied-field act."""

    if not isinstance(induced_response, PositiveRatio) or not isinstance(field_acts, PositiveCount):
        raise InadmissibleExactValue("susceptibility requires positive response and field acts")
    return PositiveRatio.from_pair(
        induced_response.numerator.value,
        induced_response.denominator.value * field_acts.value,
    )


def repeated_response_preserves_susceptibility(
    induced_response: PositiveRatio,
    field_acts: PositiveCount,
    repetition: PositiveCount,
) -> bool:
    """Equal repetition of response and field acts preserves susceptibility."""

    if not isinstance(repetition, PositiveCount):
        raise InadmissibleExactValue("response repetition requires a positive count")
    original = exact_susceptibility_ratio(induced_response, field_acts)
    repeated_response = PositiveRatio.from_pair(
        induced_response.numerator.value * repetition.value,
        induced_response.denominator.value,
    )
    repeated_field = PositiveCount(field_acts.value * repetition.value)
    return exact_susceptibility_ratio(repeated_response, repeated_field).fraction == original.fraction


@dataclass(frozen=True)
class MolecularMagneticResponseCarrier:
    molecule: HeldLabel
    molecular_state: HeldLabel
    angular_support: HeldLabel
    spin_support: HeldLabel
    orbital_support: HeldLabel
    field_orientation: HeldLabel
    response_orientation: HeldLabel
    response_unit: HeldLabel
    observation_condition: HeldLabel

    def __post_init__(self) -> None:
        required = (
            (self.molecule, "molecular-identity"),
            (self.molecular_state, "molecular-state"),
            (self.angular_support, "angular-support"),
            (self.spin_support, "spin-support"),
            (self.orbital_support, "orbital-support"),
            (self.field_orientation, "magnetic-field-orientation"),
            (self.response_orientation, "magnetic-response-orientation"),
            (self.response_unit, "held-magnetic-response-unit"),
            (self.observation_condition, "measurement-condition"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("molecular magnetic carrier lost a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-FIELD-MAGNETIC-RELATIVITY-003",
    "SFT-PHYS-ELECTRON-DIRAC-G-FACTOR-002",
    "SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006",
    "SFT-CHEM-JOINT-CORRELATION-DISSOCIATION-007",
    "SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013",
    "SFT-CHEM-ROTATIONAL-CONSTANT-010",
    "SFT-CHEM-INTERMOLECULAR-BINDING-011",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "answer-only-magnetic-number", "A bare number erases molecule, state and angular support.", "complete-molecular-state-and-angular-carrier", "Molecule, state, spin, orbital and rotational support remain held."),
    dimension("orientation", "signed-direction-as-proof-number", "A signed proof scalar imports negative numbers and loses the generating side.", "opposed-held-orientation-labels", "Direction is retained as one of two distinct fibre labels."),
    dimension("closure", "assume-every-carrier-has-net-moment", "Paired complementary support can close and must not be assigned a numerical zero.", "pairwise-closure-to-EmptyOne-or-positive-excess", "Balanced support is structural EmptyOne; unmatched support is positive and oriented."),
    dimension("moment", "fitted-or-species-g-coefficient", "A fitted g-factor lets the measured molecule select the law.", "positive-response-per-angular-recurrence", "Molecular moment is an exact positive response-count ratio."),
    dimension("susceptibility", "continuum-derivative-field-law", "A continuum derivative imports an ungenerated field model.", "positive-induced-response-per-field-act", "Susceptibility is an exact positive ratio over counted field acts."),
    dimension("prediction", "moment-or-susceptibility-readable-before-seal", "Readable targets could select the relation or molecule subset.", "value-free-complete-magnetic-identity-seal", "Every source page, row, axis and response identity seals before values open."),
    dimension("record", "favorable-or-accessible-molecule-subset", "Selecting positive, convenient or currently accessible pages conceals blanks and source failures.", "complete-g-factor-susceptibility-and-unavailable-custody", "All accessible values, blanks, signed orientations, the complete diatomic PDF and unavailable links remain explicit."),
    dimension("extension", "species-correction-or-new-field-coefficient", "A species residual creates a free parameter for every molecule.", "one-ratio-law-with-depth-independent-repetition", "Equal positive repetition preserves response ratios without a new rule."),
)


EXACT_RESULT = (
    "complete-molecular-state-and-angular-carrier__opposed-held-orientation-labels__"
    "pairwise-closure-to-EmptyOne-or-positive-excess__positive-response-per-angular-recurrence__"
    "positive-induced-response-per-field-act__value-free-complete-magnetic-identity-seal__"
    "complete-g-factor-susceptibility-and-unavailable-custody__one-ratio-law-with-depth-independent-repetition"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    side_a = HeldLabel("magnetic-orientation", "fibre-a")
    side_b = HeldLabel("magnetic-orientation", "fibre-b")
    closed_orientation, closed = exact_orientation_excess(PositiveCount(3), PositiveCount(3), side_a, side_b)
    retained_orientation, retained = exact_orientation_excess(PositiveCount(5), PositiveCount(2), side_a, side_b)
    moment = exact_moment_ratio(PositiveCount(3), PositiveCount(2))
    susceptibility = exact_susceptibility_ratio(moment, PositiveCount(5))
    return (
        ("balanced-closure", "Equal opposing support closes structurally.", closed_orientation.label == "balanced-closed" and isinstance(closed, EmptyOne)),
        ("positive-unmatched-support", "Five against two retains three on fibre-a.", retained_orientation.label == "fibre-a" and isinstance(retained, PositiveCount) and retained.value == 3),
        ("exact-moment-ratio", "Three responses over two angular recurrences yield 3/2.", moment.fraction == Fraction(3, 2)),
        ("exact-susceptibility-ratio", "Moment 3/2 over five field acts yields 3/10.", susceptibility.fraction == Fraction(3, 10)),
        ("depth-independent-repetition", "Equal repetition preserves the exact susceptibility ratio.", repeated_response_preserves_susceptibility(moment, PositiveCount(5), PositiveCount(7))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "MolecularMagneticResponseCarrier", "exact_moment_ratio", "exact_orientation_excess",
    "exact_susceptibility_ratio", "repeated_response_preserves_susceptibility",
)
