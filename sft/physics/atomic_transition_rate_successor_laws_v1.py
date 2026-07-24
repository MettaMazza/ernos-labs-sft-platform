"""Terminal atomic transition-rate, lifetime and multipole successor.

The executable relations are exact and target-inaccessible.  No wavelength,
transition probability, lifetime, source record or external constant occurs in
this module.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_spectra_completion_laws_v1 import transition_selection
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


ATOMIC_TRANSITION_RATE_TERMINAL_ID = "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005"


def electric_multipole_exponent(multipole_rank: int) -> int:
    if isinstance(multipole_rank, bool) or not isinstance(multipole_rank, int) or multipole_rank < 1:
        raise ValueError("multipole rank must be a positive whole count")
    return 2 * multipole_rank + 1


def normalized_electric_rate(
    gap: Fraction,
    strength: Fraction,
    statistical_weight: int,
    multipole_rank: int = 1,
) -> Fraction:
    if not isinstance(gap, Fraction) or gap <= 0 or gap >= Fraction(1, 1):
        raise ValueError("gap must be an exact positive strict part of the One")
    if not isinstance(strength, Fraction) or strength <= 0:
        raise ValueError("line strength must be an exact positive carrier")
    if isinstance(statistical_weight, bool) or not isinstance(statistical_weight, int) or statistical_weight < 1:
        raise ValueError("statistical weight must be a positive whole count")
    return gap ** electric_multipole_exponent(multipole_rank) * strength / statistical_weight


def exact_lifetime(rates: tuple[Fraction, ...]) -> Fraction:
    if not rates or any(not isinstance(rate, Fraction) or rate <= 0 for rate in rates):
        raise ValueError("lifetime requires complete positive exact decay rates")
    return Fraction(1, 1) / sum(rates)


def successor_multipole_ratio(gap: Fraction) -> Fraction:
    """Equal-strength/equal-weight E(L+1)-to-EL suppression."""

    if not isinstance(gap, Fraction) or gap <= 0 or gap >= Fraction(1, 1):
        raise ValueError("gap must be an exact positive strict part of the One")
    return gap * gap


def transition_rate_axes() -> tuple:
    return (
        binary_axis("predecessor", "How is the admitted one-act selection law used?", "replace-selection-law", "A successor cannot rewrite the immutable one-unit receipt.", "retain-one-unit-elementary-act", "The elementary E1 orbital step remains exactly one."),
        binary_axis("gap", "What supplies transition throw?", "selected-decimal-frequency", "A selected frequency would be a target-bearing parameter.", "exact-positive-level-gap", "The already generated ordered level difference supplies the gap."),
        binary_axis("space", "How many gap carriers make the elementary radiative volume?", "free-rate-exponent", "A chosen exponent is a parameter.", "complete-generator-three-volume", "One gap carrier traverses each of the three forced spatial directions, forcing the cube."),
        binary_axis("strength", "How is transition overlap retained?", "erase-or-fit-strength", "Erasure or fitting cannot distinguish lines.", "held-exact-line-strength", "The exact positive squared transition carrier remains explicit."),
        binary_axis("weight", "How is upper-state multiplicity handled?", "unweighted-or-fitted-factor", "A hidden multiplicity changes rates freely.", "divide-by-complete-positive-weight", "The complete generated upper-state class count normalizes the rate."),
        binary_axis("lifetime", "How does retention time follow from decay channels?", "independent-lifetime-parameter", "A separately chosen lifetime is not forced.", "reciprocal-complete-rate-sum", "One retained population exhausted by all positive channels forces the reciprocal of their sum."),
        binary_axis("multipole", "How does electric multipole rank extend?", "chosen-power-list", "A list has no successor theorem.", "append-held-boundary-pair", "Each rank successor appends the two held boundary directions, so exponent 2L+1 advances by two."),
        binary_axis("forbidden", "Does the word forbidden alone force every rate ordering?", "universal-slower-label", "M1 shares the cubic exponent and distinct strengths can reverse an unqualified ordering.", "typed-channel-conditional-suppression", "For equal positive strength and weight, each electric-rank successor is suppressed by exact gap squared; other channels retain their own strength carrier."),
        binary_axis("target", "May NIST formulas or lifetimes enter execution?", "external-target-readable", "Target-readable execution cannot seal a prediction.", "target-inaccessible-until-seal", "The formal module contains no external formula, value or source access."),
        binary_axis("extension", "May another coefficient or exception be appended?", "free-coefficient-or-exception", "An ungenerated coefficient is a parameter.", "no-extra-rule", "Gap, spatial volume, strength, weight, rate sum and multipole succession exhaust the grammar."),
    )


ATOMIC_TRANSITION_RATE_SPEC = StructuralPhysicsSpec(
    claim_id=ATOMIC_TRANSITION_RATE_TERMINAL_ID,
    title="Terminal exact atomic transition-rate, lifetime and multipole completion",
    statement=(
        "The admitted one-unit elementary transition retains an exact positive level gap.  Transport through "
        "all three forced spatial directions makes the E1 rate proportional to gap cubed times held line "
        "strength divided by complete upper-state weight.  Complete positive decay channels force lifetime to "
        "be the reciprocal of their rate sum.  Electric multipole rank L has exponent 2L+1, so each successor "
        "is conditionally suppressed by exact gap squared at equal strength and weight.  Magnetic and other "
        "typed channels retain distinct strengths; the label forbidden alone is not promoted to a false universal ordering."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-TRANSITION-SELECTION-004",
        "SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-QUANTUM-SPIN-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis transition-act, gap, spatial-volume, strength, weight, lifetime, multipole, typed-channel, custody and extension product.",
    grammar_boundary="All exact positive normalized electric-multipole rates generated from an admitted level gap, held strength, positive upper-state weight and every finite positive multipole rank, plus complete finite positive decay-channel sums.",
    axes=transition_rate_axes(),
    exact_result=(
        "Normalized E1 rate is gap^3*S/g; lifetime is 1/(sum_i A_i); normalized electric rank-L rate is "
        "gap^(2L+1)*S/g and the equal-strength/equal-weight successor ratio is gap^2. The elementary orbital "
        "step remains One, while non-electric typed channels require their own held strengths."
    ),
    induction_base="Electric rank One consists of one emitted gap carrier plus the complete held spatial boundary pair, giving exponent three.",
    induction_step="Appending one electric multipole rank appends exactly the two held boundary directions, changing 2L+1 to 2(L+1)+1 and multiplying the normalized equal-strength/equal-weight rate by gap squared.",
    exclusions=(
        "no measured wavelength, rate, line strength, lifetime or source access in execution",
        "no imported continuum radiation equation or floating proof value",
        "no numerical-zero state, negative rate, irrational or imaginary proof scalar",
        "no universal claim that every forbidden-channel rate is slower independent of strength",
        "no fitted exponent, coefficient, lifetime or multipole exception",
    ),
    witnesses=(
        Witness("elementary-step-retained", "The immutable elementary transition remains one orbital unit.", transition_selection()["orbital_step"] == 1),
        Witness("electric-exponents", "The first four electric multipole exponents are 3,5,7,9.", tuple(electric_multipole_exponent(rank) for rank in range(1, 5)) == (3, 5, 7, 9)),
        Witness("rate-and-lifetime", "Complete exact rates force the exact reciprocal lifetime.", exact_lifetime((Fraction(1, 8), Fraction(1, 24))) == Fraction(6, 1)),
        Witness("conditional-suppression", "Every tested electric-rank successor is strictly suppressed for every exact strict-part gap.", all(0 < successor_multipole_ratio(Fraction(k, 17)) < Fraction(1, 1) for k in range(1, 17))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ATOMIC_TRANSITION_RATE_SPEC.validate()


__all__ = (
    "ATOMIC_TRANSITION_RATE_SPEC",
    "ATOMIC_TRANSITION_RATE_TERMINAL_ID",
    "electric_multipole_exponent",
    "exact_lifetime",
    "normalized_electric_rate",
    "successor_multipole_ratio",
)
