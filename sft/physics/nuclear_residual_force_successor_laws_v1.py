"""Terminal residual nuclear-interaction and mediator-range successor.

The formal law contains no particle name, measured mass, cross section, length,
source locator or fitted force coefficient. Opposed interaction directions are
held labels; leading neutral closure is the empty form, never numerical zero.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis, fold_part, generator_period_three


NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID = "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005"


def primary_boundary_support() -> Fraction:
    return Fraction(1, binary_count())


def residual_boundary_support() -> Fraction:
    """The first retained exchange after both leading neutral acts close."""

    primary = primary_boundary_support()
    residual = primary * primary
    if fold_part(residual) != primary or fold_part(fold_part(residual)) != Fraction(1, 1):
        raise ValueError("second-order residual did not return through the Fold tower")
    return residual


def neutral_composite_exchange() -> dict[str, tuple[()] | Fraction | int]:
    colour_cells = generator_period_three()
    leading_external = ()
    residual = residual_boundary_support()
    return {
        "closed_colour_cells": colour_cells,
        "leading_external_label": leading_external,
        "first_retained_boundary_exchange": residual,
    }


def mediator_range(mass_carrier: Fraction) -> Fraction:
    if not isinstance(mass_carrier, Fraction) or mass_carrier <= 0:
        raise ValueError("mediator mass carrier must be exact and positive")
    return Fraction(1, 1) / mass_carrier


def mediator_reach_class(mass_carrier: Fraction | tuple[()]) -> str:
    if mass_carrier == ():
        return "unbounded-no-mass-label"
    mediator_range(mass_carrier)
    return "finite-positive-reciprocal-scale"


def inverse_mass_order(light_mass: Fraction, heavy_mass: Fraction) -> bool:
    if not isinstance(light_mass, Fraction) or not isinstance(heavy_mass, Fraction):
        raise ValueError("mass carriers must be exact fractions")
    if light_mass <= 0 or heavy_mass <= light_mass:
        raise ValueError("range ordering requires positive ordered masses")
    return mediator_range(light_mass) > mediator_range(heavy_mass)


def finite_boundary_capacity() -> int:
    """Count the complete held boundary labels of one colour-closed composite."""

    capacity = generator_period_three()
    if capacity < 1:
        raise ValueError("finite boundary support was not generated")
    return capacity


def axes() -> tuple:
    return (
        binary_axis("predecessor", "How are admitted colour closure and confinement used?", "rewrite-nucleon-predecessors", "A successor cannot alter admitted receipts.", "compose-immutable-neutral-composite-predecessors", "The complete colour singlet, confinement and interaction classes remain immutable dependencies."),
        binary_axis("neutral", "What leaves a closed colour boundary at leading order?", "export-raw-colour-label", "A raw colour label would violate the admitted singlet boundary.", "leading-colour-act-closes-to-empty-form", "Every internal colour is completed inside the singlet, leaving no separately observable leading label outside."),
        binary_axis("residual", "What is the first nonempty inter-boundary exchange?", "reuse-primary-half-One", "A first-order carrier ignores both neutral closures.", "paired-half-One-boundary-act", "One retained boundary act from each neutral composite forces the second-order product one-quarter."),
        binary_axis("strength", "Is the quarter-One a universal measured force coefficient?", "identify-quarter-with-all-cross-sections", "Measured channels need not share one dimensional strength.", "structural-order-not-universal-dimensional-strength", "Quarter-One fixes the first retained Fold order; physical channel strength remains an external comparison object."),
        binary_axis("mass", "How is absent versus present mediator mass represented?", "numerical-zero-mass", "Numerical zero is outside the proof domain.", "empty-mass-label-or-positive-mass-carrier", "The massless class uses an absent held label; the massive class carries one exact positive part."),
        binary_axis("range", "What range law follows from a positive mass carrier?", "chosen-decay-length", "A selected length is a parameter.", "exact-reciprocal-mass-scale", "One complete action divided over the positive mass carrier forces range scale One/m."),
        binary_axis("ordering", "Which mediator reaches farther?", "import-particle-range-ranking", "A named particle table cannot prove the order.", "lighter-positive-mass-has-greater-reciprocal", "Exact order reversal under reciprocation forces every lighter mediator to have the longer scale."),
        binary_axis("saturation", "Why is the residual interaction local and saturating?", "all-to-all-independent-links", "Unlimited independent links ignore finite boundary support and finite range.", "finite-boundary-cells-with-finite-range", "A colour-closed composite has finitely many held boundary cells and a massive exchange has a finite reciprocal scale, bounding independent local links."),
        binary_axis("target", "May external masses or scattering data enter execution?", "external-target-readable", "Target access cannot seal a prediction.", "target-inaccessible-until-seal", "No particle name, mass, length, cross section, uncertainty or source is accessible to the executable law."),
        binary_axis("extension", "May an exponential, cutoff or fitted coupling be appended?", "free-decay-profile-or-coupling", "An ungenerated profile or coefficient is a parameter.", "no-extra-rule", "Neutral closure, paired residual order, reciprocal mass and finite boundary support exhaust the declared grammar."),
    )


NUCLEAR_RESIDUAL_FORCE_SPEC = StructuralPhysicsSpec(
    claim_id=NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID,
    title="Terminal residual nuclear interaction and inverse-mediator range",
    statement=(
        "A complete colour-three composite closes every leading colour label inside its boundary, so the external "
        "leading act is the empty form.  The first nonempty exchange must retain one boundary act from each of two "
        "neutral composites; the forced half-One therefore enters twice and fixes the second-order structural support "
        "at one-quarter.  This is an exact Fold order, not a universal dimensional cross section.  A present mediator "
        "mass is a positive carrier and forces the finite reciprocal range One/m; an absent mass label has no finite "
        "subtraction endpoint.  Thus lighter massive mediators reach farther, while finite boundary cells and finite "
        "range force locality and saturation without an imported exponential or hard numerical-zero cutoff."
    ),
    dependencies=(
        "SFT-FOUNDATION-HALF-ONE-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        "SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",
        "SFT-PHYS-FIELD-INTERACTION-CLASSES-001",
        "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005",
        "SFT-PHYS-HADRON-REGGE-TERMINAL-005",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis predecessor, neutral closure, residual order, strength scope, mass class, reciprocal range, ordering, saturation, custody and extension product.",
    grammar_boundary="Every exchange between two complete colour-three neutral composite boundaries, the forced half-One primary carrier, absent or exact positive mediator-mass labels, and every positive mass ordering under reciprocal range.",
    axes=axes(),
    exact_result="Leading colour exchange outside a singlet is the empty form; the first retained two-boundary order is (1/2)^2=1/4 and returns 1/4 to 1/2 to One in two Folds; every positive mediator has finite normalized range 1/m and m1<m2 forces 1/m1>1/m2.",
    induction_base="Two neutral boundaries each retain one half-One boundary act, whose paired support is exactly one-quarter; one positive mediator mass has one exact reciprocal scale.",
    induction_step="Appending another closed composite repeats the same paired residual order rather than reopening raw colour; increasing any positive mass strictly decreases its reciprocal range while preserving finite boundary capacity.",
    exclusions=(
        "no V1/V2 executable, certificate, answer value, Yukawa potential or consensus interaction model as a premise",
        "no particle name, measured mass, cross section, length, uncertainty or source access in execution",
        "no numerical-zero state, negative, irrational, imaginary or floating proof value",
        "no identification of structural one-quarter with a universal dimensional nuclear-force strength",
        "no fitted coupling, exponential decay profile, hard cutoff or selected mediator scale",
        "no target access before derivation and prediction seals",
    ),
    witnesses=(
        Witness("neutral-leading-closure", "A complete colour composite retains no separately observable leading external colour label.", neutral_composite_exchange()["leading_external_label"] == ()),
        Witness("quarter-residual", "Two forced half-One boundary acts give exact quarter-One support and two-Fold return.", residual_boundary_support() == Fraction(1, 4) and fold_part(fold_part(residual_boundary_support())) == Fraction(1, 1)),
        Witness("range-order", "Every tested positive heavier carrier has the shorter exact reciprocal scale.", all(inverse_mass_order(Fraction(rank, 17), Fraction(rank + 1, 17)) for rank in range(1, 128))),
        Witness("finite-saturation", "One closed composite has the finite complete generator-three boundary capacity.", finite_boundary_capacity() == 3),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


NUCLEAR_RESIDUAL_FORCE_SPEC.validate()


__all__ = (
    "NUCLEAR_RESIDUAL_FORCE_SPEC",
    "NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID",
    "finite_boundary_capacity",
    "inverse_mass_order",
    "mediator_range",
    "mediator_reach_class",
    "neutral_composite_exchange",
    "primary_boundary_support",
    "residual_boundary_support",
)
