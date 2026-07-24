"""Terminal atomic Zeeman and Stark field-splitting successor.

All executable relations use positive exact counts, fractions and held side
labels.  The central unshifted class is represented by the empty form rather
than a numerical zero.  No measured field coefficient or source is present.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


ATOMIC_FIELD_SPLITTING_TERMINAL_ID = "SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005"


def magnetic_sublevel_count(doubled_angular_count: int) -> int:
    """Positive translation of conventional 2J+1 multiplicity."""

    if isinstance(doubled_angular_count, bool) or not isinstance(doubled_angular_count, int) or doubled_angular_count < 1:
        raise ValueError("doubled angular support must be a positive whole count")
    return doubled_angular_count + 1


def zeeman_shift_magnitude(g_factor: Fraction, orientation_distance: int, field: Fraction) -> Fraction:
    if not isinstance(g_factor, Fraction) or g_factor <= 0:
        raise ValueError("g carrier must be exact and positive")
    if isinstance(orientation_distance, bool) or not isinstance(orientation_distance, int) or orientation_distance < 1:
        raise ValueError("orientation distance must be a positive count")
    if not isinstance(field, Fraction) or field <= 0:
        raise ValueError("field magnitude must be exact and positive")
    return g_factor * orientation_distance * field


def linear_stark_magnitude(dipole: Fraction, field: Fraction) -> Fraction:
    if not isinstance(dipole, Fraction) or dipole <= 0 or not isinstance(field, Fraction) or field <= 0:
        raise ValueError("linear Stark carriers must be exact and positive")
    return dipole * field


def quadratic_stark_magnitude(polarizability: Fraction, field: Fraction) -> Fraction:
    if not isinstance(polarizability, Fraction) or polarizability <= 0 or not isinstance(field, Fraction) or field <= 0:
        raise ValueError("quadratic Stark carriers must be exact and positive")
    return polarizability * field * field / 2


def field_axes() -> tuple:
    return (
        binary_axis("predecessor", "How are existing magnetic/electric orientation laws used?", "replace-field-predecessors", "A successor cannot rewrite admitted receipts.", "compose-immutable-field-predecessors", "Magnetic handedness and electric displacement remain exact dependencies."),
        binary_axis("multiplicity", "How is a J-level orientation support counted?", "selected-line-count", "A chosen multiplet width imports the answer.", "complete-held-orientation-successor", "All doubled angular positions plus the retained successor class give exactly 2J+1."),
        binary_axis("direction", "How are opposing shifts represented?", "signed-energy-scalar", "Negative proof scalars violate the domain.", "held-side-label-and-positive-distance", "Side is a label; displacement from the empty central class is a positive count."),
        binary_axis("magnetic", "How does weak magnetic response compose?", "chosen-field-polynomial", "A chosen response polynomial is a parameter.", "one-field-act-per-held-orientation", "One field act on one held orientation forces a linear magnitude g*m*B."),
        binary_axis("spacing", "What separates adjacent Zeeman classes?", "unequal-free-spacing", "Free spacings destroy the generated orientation order.", "one-common-positive-field-step", "Adjacent positive orientation distances differ by one act, so their magnitude spacing is the common g*B carrier."),
        binary_axis("electric-degenerate", "What survives in a degenerate electric support?", "erase-first-displacement", "Erasure loses the held cross-state channel.", "held-first-order-dipole-channel", "Degenerate partners retain the first displacement act, forcing a linear Stark magnitude."),
        binary_axis("electric-nondegenerate", "What survives without that partner?", "free-first-order-shift", "A first-order scalar without a retained partner is ungenerated.", "paired-first-act-closes-then-square", "The opposed first acts close to the empty form; the first retained magnitude uses two field acts and is quadratic."),
        binary_axis("order", "Can linear and quadratic Stark laws be conflated?", "universal-single-order", "One order erases the degeneracy discriminator.", "degeneracy-typed-response-order", "The retained support class uniquely selects first or second positive order."),
        binary_axis("target", "May external splitting data enter execution?", "external-target-readable", "Target-readable execution cannot seal a prediction.", "target-inaccessible-until-seal", "No external coefficient, splitting or source is accessible to the formal module."),
        binary_axis("extension", "May another field coefficient or response rule be added?", "free-coefficient-or-rule", "An ungenerated response is a parameter.", "no-extra-rule", "Orientation, side, field act and degeneracy exhaust the declared grammar."),
    )


ATOMIC_FIELD_SPLITTING_SPEC = StructuralPhysicsSpec(
    claim_id=ATOMIC_FIELD_SPLITTING_TERMINAL_ID,
    title="Terminal exact atomic Zeeman and Stark field-splitting completion",
    statement=(
        "Complete held angular support forces 2J+1 magnetic sublevels.  Opposing directions remain labels and "
        "every displacement magnitude is positive; one weak-field act therefore forces linear Zeeman shifts "
        "g*m*B with equal adjacent spacing g*B.  In electric response a retained degenerate partner preserves "
        "the first dipole act and forces a linear Stark shift.  Without that partner the opposed first acts close "
        "to the empty form and the first retained response uses two field acts, forcing a quadratic shift."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-TRANSITION-SELECTION-004",
        "SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005",
        "SFT-PHYS-FIELD-MAGNETIC-RELATIVITY-003",
        "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
        "SFT-PHYS-QUANTUM-SPIN-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis field-predecessor, multiplicity, held-direction, magnetic response, spacing, degenerate/nondegenerate electric response, order, custody and extension product.",
    grammar_boundary="Every finite positive angular support, exact positive field magnitude, held side/orientation label and the two complete electric support classes distinguished by whether a degenerate partner is retained.",
    axes=field_axes(),
    exact_result="A J level has 2J+1 magnetic classes; Zeeman magnitude is g*m*B with adjacent spacing g*B; retained degeneracy gives dipole*E while nondegenerate closure gives polarizability*E^2/2.",
    induction_base="The first noncentral held orientation has one positive distance and one field act, so its magnetic response is linear; one retained degenerate electric pair likewise holds its first displacement.",
    induction_step="Appending one doubled-angular position adds exactly one sublevel and preserves common field spacing; removing the degenerate partner closes the paired first acts and promotes the first retained electric response from one to two field acts.",
    exclusions=(
        "no measured Zeeman coefficient, Stark coefficient, splitting or source access in execution",
        "no numerical-zero central state or negative signed proof scalar",
        "no irrational, imaginary or floating proof value",
        "no universal Stark order that erases the degeneracy discriminator",
        "no fitted g factor, dipole, polarizability or response coefficient",
    ),
    witnesses=(
        Witness("multiplicity", "Positive doubled-angular counts generate conventional 2J+1 multiplicities.", tuple(magnetic_sublevel_count(value) for value in range(1, 7)) == (2, 3, 4, 5, 6, 7)),
        Witness("linear-zeeman", "Doubling the field doubles every exact Zeeman magnitude.", zeeman_shift_magnitude(Fraction(3, 2), 2, Fraction(2, 5)) == 2 * zeeman_shift_magnitude(Fraction(3, 2), 2, Fraction(1, 5))),
        Witness("linear-degenerate-Stark", "Doubling the field doubles the degenerate response.", linear_stark_magnitude(Fraction(4, 7), Fraction(2, 5)) == 2 * linear_stark_magnitude(Fraction(4, 7), Fraction(1, 5))),
        Witness("quadratic-nondegenerate-Stark", "Doubling the field quadruples the nondegenerate response.", quadratic_stark_magnitude(Fraction(4, 7), Fraction(2, 5)) == 4 * quadratic_stark_magnitude(Fraction(4, 7), Fraction(1, 5))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ATOMIC_FIELD_SPLITTING_SPEC.validate()


__all__ = (
    "ATOMIC_FIELD_SPLITTING_SPEC",
    "ATOMIC_FIELD_SPLITTING_TERMINAL_ID",
    "linear_stark_magnitude",
    "magnetic_sublevel_count",
    "quadratic_stark_magnitude",
    "zeeman_shift_magnitude",
)
