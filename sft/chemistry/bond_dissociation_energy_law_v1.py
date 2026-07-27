"""Exact Fold state-path law for Chemistry PROP-002.

The executable law contains no molecular threshold, atomic frequency,
dissociation energy, uncertainty, source path, conventional potential or fitted
coefficient.  It states only the exact path-composition rule: when a retained
molecular threshold ends in M(1s)+M(2s), the X-state dissociation separation to
M(1s)+M(1s) is the threshold after the held atomic 1s--2s segment is Taken.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine.exact import InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension
from sft.physics.prior_value_laws import positive_take


def ground_dissociation_from_transition(
    excited_threshold: Fraction,
    atomic_excitation: Fraction,
) -> Fraction:
    """Compose the exact retained path using ordered positive Take."""

    if (
        not isinstance(excited_threshold, Fraction)
        or excited_threshold.numerator < 1
        or excited_threshold.denominator < 1
    ):
        raise InadmissibleExactValue("molecular threshold must be an exact positive fraction")
    if (
        not isinstance(atomic_excitation, Fraction)
        or atomic_excitation.numerator < 1
        or atomic_excitation.denominator < 1
    ):
        raise InadmissibleExactValue("atomic excitation must be an exact positive fraction")
    if excited_threshold <= atomic_excitation:
        raise InadmissibleExactValue("the retained threshold cannot Take a non-smaller segment")
    result = positive_take(excited_threshold, atomic_excitation)
    if not isinstance(result, Fraction) or result.numerator < 1 or result.denominator < 1:
        raise InadmissibleExactValue("dissociation path did not close as an exact positive fraction")
    return result


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-ATOMIC-HYDROGEN-RYDBERG-TERMINAL-005",
    "SFT-CHEM-JOINT-CORRELATION-DISSOCIATION-007",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-EQUILIBRIUM-BOND-LENGTH-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "identity",
        "generic-molecule-with-erased-isotope",
        "A generic molecule cannot own an isotopologue-specific quantitative path.",
        "named-isotopologue-and-X-state",
        "H2 and D2 identities and their X-state origins remain held throughout.",
    ),
    dimension(
        "channel",
        "dissociation-products-erased",
        "Erasing the atomic product states destroys the path whose segment is Taken.",
        "both-product-channels-held",
        "M(1s)+M(2s) and M(1s)+M(1s) are retained as distinct endpoints.",
    ),
    dimension(
        "path",
        "answer-only-energy-lookup",
        "An answer-only energy does not derive the relation between the two state paths.",
        "shared-prefix-path-composition",
        "The two paths share M(1s); their sole remaining distinction is the atomic 1s--2s segment.",
    ),
    dimension(
        "operation",
        "signed-or-floating-subtraction",
        "A signed scalar or floating subtraction is outside the Fold exact domain.",
        "ordered-positive-held-Take",
        "The longer exact path Takes the strictly smaller held atomic segment.",
    ),
    dimension(
        "input",
        "measured-value-used-as-prediction-input",
        "A measured threshold or atomic interval inside prediction would make observation select the number.",
        "all-measurements-opened-post-seal",
        "The structural Take relation seals before any threshold, atomic or ground-dissociation value opens.",
    ),
    dimension(
        "measurement",
        "dissociation-target-readable-before-seal",
        "A readable target can select or alter the predicted interval.",
        "target-inaccessible-until-prediction-seal",
        "The four target intervals are released only after the two-row prediction is sealed.",
    ),
    dimension(
        "record",
        "selected-historical-or-current-row",
        "Selecting one resolution or era can conceal an unfavorable comparison.",
        "complete-historical-and-current-vector",
        "Both isotopologues and both registered measurement generations are retained.",
    ),
    dimension(
        "extension",
        "species-coefficient-or-correction",
        "A species coefficient or residual correction would be a free parameter.",
        "typed-two-row-exhaustion-no-extra-rule",
        "The registered H2/D2 vector closes with the same path law and no added term.",
    ),
)


EXACT_RESULT = (
    "named-isotopologue-and-X-state__"
    "both-product-channels-held__"
    "shared-prefix-path-composition__"
    "ordered-positive-held-Take__"
    "all-measurements-opened-post-seal__"
    "target-inaccessible-until-prediction-seal__"
    "complete-historical-and-current-vector__"
    "typed-two-row-exhaustion-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    threshold = Fraction(9, 8)
    atomic = Fraction(3, 4)
    result = ground_dissociation_from_transition(threshold, atomic)
    reversed_rejected = False
    try:
        ground_dissociation_from_transition(atomic, threshold)
    except InadmissibleExactValue:
        reversed_rejected = True
    return (
        (
            "exact-path-composition",
            "A longer exact path Takes its held terminal segment and remains exact and positive.",
            result == Fraction(3, 8),
        ),
        (
            "orientation-retained",
            "Reversing the ordered Take halts rather than creating a negative value.",
            reversed_rejected,
        ),
        (
            "one-law-both-isotopologues",
            "The operation depends on retained path roles, not on a species coefficient.",
            ground_dissociation_from_transition(Fraction(17, 16), Fraction(3, 4))
            == Fraction(5, 16),
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "OPERATIONAL_WITNESSES",
    "ground_dissociation_from_transition",
)
