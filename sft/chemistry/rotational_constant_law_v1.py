"""Fold-native exact molecular rotational-constant law for Chemistry PROP-010.

No measured rotational constant, rigid-rotor equation, moment of inertia,
continuum angle, fitted geometry, floating value or source record is available
to this module.  A constant begins as a positive finite recurrence count on a
held generated molecular axis divided by a positive observation interval.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.atomic_constants import binary_count
from sft.physics.generated_empirical_law import LawDimension, dimension


def exact_axis_rotational_constant(
    recurrence_count: PositiveCount,
    observation_interval_count: PositiveCount,
) -> PositiveRatio:
    """Return the exact held-axis recurrence ratio after both counts exist."""

    if not isinstance(recurrence_count, PositiveCount) or not isinstance(observation_interval_count, PositiveCount):
        raise InadmissibleExactValue("a rotational constant requires positive recurrence and interval counts")
    return PositiveRatio(recurrence_count, observation_interval_count)


def repeated_equal_interval_constant(
    recurrence_count: PositiveCount,
    observation_interval_count: PositiveCount,
    repetition: PositiveCount,
) -> PositiveRatio:
    """Equal repetition scales both finite counts and preserves the constant."""

    if not isinstance(repetition, PositiveCount):
        raise InadmissibleExactValue("axis-recurrence repetition requires a positive count")
    return exact_axis_rotational_constant(
        PositiveCount(recurrence_count.value * repetition.value),
        PositiveCount(observation_interval_count.value * repetition.value),
    )


def rotational_level_multiple(rotational_ordinal: PositiveCount) -> PositiveCount:
    """Force the positive J(J+1) multiplier; the unexcited form is EmptyOne."""

    if not isinstance(rotational_ordinal, PositiveCount):
        raise InadmissibleExactValue("a rotational level requires a positive ordinal")
    ordinal = rotational_ordinal.value
    return PositiveCount(ordinal * (ordinal + 1))


def adjacent_rotational_gap_multiple(upper_ordinal: PositiveCount) -> PositiveCount:
    """Force the exact adjacent 2J multiplier for a positive upper ordinal."""

    if not isinstance(upper_ordinal, PositiveCount):
        raise InadmissibleExactValue("a rotational gap requires a positive upper ordinal")
    return PositiveCount(binary_count() * upper_ordinal.value)


def rotational_level_ratio(
    constant: PositiveRatio,
    rotational_ordinal: PositiveCount,
) -> PositiveRatio:
    """Compose a held-axis constant with its forced positive ladder multiple."""

    if not isinstance(constant, PositiveRatio):
        raise InadmissibleExactValue("rotational level composition requires an exact positive constant")
    multiple = rotational_level_multiple(rotational_ordinal)
    return PositiveRatio(
        PositiveCount(constant.numerator.value * multiple.value),
        constant.denominator,
    )


def unexcited_rotational_form() -> EmptyOne:
    """Return structural absence, never numerical zero."""

    return EMPTY_ONE


@dataclass(frozen=True)
class RotationalAxisCarrier:
    species: HeldLabel
    molecular_state: HeldLabel
    geometry: HeldLabel
    geometry_coordinate_count: PositiveCount
    axis: HeldLabel
    axis_equivalence_class: HeldLabel
    recurrence_count: PositiveCount
    observation_interval_count: PositiveCount
    interval_unit: HeldLabel

    def __post_init__(self) -> None:
        if (
            not isinstance(self.species, HeldLabel)
            or self.species.family != "molecular-species"
            or not isinstance(self.molecular_state, HeldLabel)
            or self.molecular_state.family != "molecular-state"
            or not isinstance(self.geometry, HeldLabel)
            or self.geometry.family != "generated-molecular-geometry"
            or not isinstance(self.geometry_coordinate_count, PositiveCount)
            or not isinstance(self.axis, HeldLabel)
            or self.axis.family != "rotational-axis"
            or self.axis.label not in {"principal-axis-A", "principal-axis-B", "principal-axis-C"}
            or not isinstance(self.axis_equivalence_class, HeldLabel)
            or self.axis_equivalence_class.family != "rotational-axis-equivalence"
            or not isinstance(self.recurrence_count, PositiveCount)
            or not isinstance(self.observation_interval_count, PositiveCount)
            or not isinstance(self.interval_unit, HeldLabel)
            or self.interval_unit.family != "observation-interval-unit"
        ):
            raise InadmissibleExactValue("rotational carrier erased or altered a required finite field")

    @property
    def exact_constant(self) -> PositiveRatio:
        return exact_axis_rotational_constant(self.recurrence_count, self.observation_interval_count)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-WAVE-PERIOD-FREQUENCY-001",
    "SFT-PHYS-MOLECULAR-SPECTRUM-HIERARCHY-004",
    "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-ROVIBRONIC-COMPOSITION-001",
    "SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013",
    "SFT-CHEM-EQUILIBRIUM-BOND-LENGTH-001",
    "SFT-CHEM-MOLECULAR-BOND-ANGLE-003",
    "SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
    "SFT-CHEM-VIBRATIONAL-FREQUENCY-009",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "answer-only-rotational-number",
        "An answer-only number erases molecular state, geometry and axis identity.",
        "complete-finite-state-geometry-axis-carrier",
        "Species, state, finite generated geometry, coordinate support and axis identity remain held without a continuum rigid body.",
    ),
    dimension(
        "axis", "merged-or-relabelled-axis",
        "Merging principal axes destroys distinct and symmetry-equivalent recurrence records.",
        "held-principal-axis-and-equivalence-class",
        "A, B and C remain held labels with their generated equivalence class.",
    ),
    dimension(
        "magnitude", "imported-rotational-constant-or-inertia-equation",
        "A named constant or moment-of-inertia equation does not derive the Fold quantity.",
        "exact-axis-recurrence-over-interval-ratio",
        "The constant is the exact positive held-axis recurrence count over a positive interval count.",
    ),
    dimension(
        "ladder", "continuum-or-free-angular-spectrum",
        "A continuum spectrum or selected angular coefficient is not generated.",
        "positive-JJplusOne-level-and-2J-gap",
        "Positive ordinals force J(J+1) levels and exact adjacent 2J gaps; the unexcited form is EmptyOne.",
    ),
    dimension(
        "translation", "reciprocal-centimeter-selects-law",
        "A conventional unit cannot select the axis-recurrence relation.",
        "post-recurrence-held-unit-translation",
        "The exact ratio exists before a reciprocal-centimeter label is attached.",
    ),
    dimension(
        "prediction", "rotational-target-readable-before-seal",
        "A readable A, B or C value could select the relation or row set.",
        "value-free-complete-axis-identity-seal",
        "Every returned molecular-row and axis identity seals without any rotational value.",
    ),
    dimension(
        "record", "favorable-molecule-or-present-axis-subset",
        "Dropping unavailable species, blank axes or asymmetric rows hides the source boundary.",
        "complete-NIST-list-choice-result-and-axis-custody",
        "The complete list query, returned choices, returned rows and every present or absent A/B/C cell remain explicit.",
    ),
    dimension(
        "extension", "fitted-inertia-geometry-or-species-correction",
        "A fitted inertia, geometry coefficient or species residual is a free parameter.",
        "one-axis-recurrence-law-no-extra-rule",
        "One exact recurrence law and one forced ladder cover every returned axis without a correction term.",
    ),
)


EXACT_RESULT = (
    "complete-finite-state-geometry-axis-carrier__"
    "held-principal-axis-and-equivalence-class__exact-axis-recurrence-over-interval-ratio__"
    "positive-JJplusOne-level-and-2J-gap__post-recurrence-held-unit-translation__"
    "value-free-complete-axis-identity-seal__complete-NIST-list-choice-result-and-axis-custody__"
    "one-axis-recurrence-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    constant = exact_axis_rotational_constant(PositiveCount(12), PositiveCount(3))
    repeated = repeated_equal_interval_constant(PositiveCount(12), PositiveCount(3), PositiveCount(5))
    levels = tuple(rotational_level_multiple(PositiveCount(j)).value for j in range(1, 5))
    gaps = tuple(adjacent_rotational_gap_multiple(PositiveCount(j)).value for j in range(1, 5))
    level = rotational_level_ratio(constant, PositiveCount(3))
    return (
        ("axis-recurrence-ratio", "Twelve held-axis recurrences over three intervals force exact constant four.", constant.fraction == Fraction(4, 1)),
        ("equal-interval-successor", "Five equal repetitions preserve the exact axis recurrence ratio.", repeated.fraction == constant.fraction),
        ("forced-positive-ladder", "The first four positive levels are 2, 6, 12 and 20 with gaps 2, 4, 6 and 8.", levels == (2, 6, 12, 20) and gaps == (2, 4, 6, 8)),
        ("constant-level-composition", "J=3 composes constant four with multiplier twelve to give exact level forty-eight.", level.fraction == Fraction(48, 1)),
        ("empty-ground", "The unexcited rotational form is structural EmptyOne rather than numerical zero.", isinstance(unexcited_rotational_form(), EmptyOne)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "RotationalAxisCarrier", "adjacent_rotational_gap_multiple", "exact_axis_rotational_constant",
    "repeated_equal_interval_constant", "rotational_level_multiple", "rotational_level_ratio",
    "unexcited_rotational_form",
)
