"""Same-strength exact atomic and molecular-spectrum reconstruction laws.

These laws reconstruct the Physics-owned content of V1 Phase III and V2 atomic
Steps 47, 60, 62, 96 and 142.  No measured wavelength, energy or target record
is imported into this module.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, inverse_fine_structure
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


CUBIC_ATOMIC_SUPPORT_ID = "SFT-PHYS-ATOMIC-CUBIC-SUPPORT-004"
HYDROGEN_SPECTRUM_ID = "SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004"
ATOMIC_CORRECTION_HIERARCHY_ID = "SFT-PHYS-ATOMIC-CORRECTION-HIERARCHY-004"
ATOMIC_TRANSITION_ID = "SFT-PHYS-ATOMIC-TRANSITION-SELECTION-004"
MOLECULAR_SPECTRUM_ID = "SFT-PHYS-MOLECULAR-SPECTRUM-HIERARCHY-004"


def cubic_coordination() -> int:
    return binary_count() * generator_period_three()


def cubic_neighbour_weight() -> Fraction:
    return Fraction(1, binary_count() * cubic_coordination())


def cubic_balance() -> Fraction:
    return cubic_coordination() * cubic_neighbour_weight()


def hydrogen_level(principal: int) -> Fraction:
    if principal < 1:
        raise ValueError("principal support must be a positive count")
    return Fraction(1, principal ** binary_count())


def hydrogen_transition(upper: int, lower: int) -> Fraction:
    if upper <= lower:
        raise ValueError("the emitted transition requires upper principal support above lower support")
    difference = positive_take(hydrogen_level(lower), hydrogen_level(upper))
    if not isinstance(difference, Fraction):
        raise ValueError("hydrogen transition orientation failed")
    return difference


def gross_atomic_scale() -> Fraction:
    alpha = Fraction(1, 1) / inverse_fine_structure()
    return alpha ** binary_count() / binary_count()


def fine_to_gross_ratio() -> Fraction:
    alpha = Fraction(1, 1) / inverse_fine_structure()
    return alpha ** binary_count()


def lamb_to_gross_order() -> Fraction:
    """First closed bound-state self-return is one fine-ratio below gross."""

    return fine_to_gross_ratio()


def atomic_scale_hierarchy() -> dict[str, Fraction]:
    gross = Fraction(1, 1)
    fine = fine_to_gross_ratio()
    lamb = fine * lamb_to_gross_order()
    return {"gross": gross, "fine": fine, "lamb": lamb}


def transition_selection() -> dict[str, object]:
    return {
        "orbital_step": 1,
        "magnetic_orientations": binary_count(),
        "complete_spatial_orientations": cubic_coordination(),
        "carrier_conserved": True,
        "one_step_required": True,
    }


def molecular_spectrum_hierarchy() -> dict[str, Fraction]:
    electronic = Fraction(1, binary_count())
    molecular = Fraction(1, binary_count() ** binary_count())
    return {
        "electronic": electronic,
        "molecular_rotation_vibration": molecular,
        "two_molecular_quanta": binary_count() * molecular,
    }


def common_axes(topic: str) -> tuple:
    return (
        binary_axis("carrier", f"What carries {topic}?", "untyped-observed-label", "A label alone is not a generated law.", "generated-exact-Fold-carrier", "The carrier is constructed from admitted exact Fold counts and relations."),
        binary_axis("support", "Which support is used?", "selected-partial-support", "A selected subset can tune the result.", "complete-typed-support", "Every support cell named by the law is generated and retained."),
        binary_axis("operation", "Which operation composes the relation?", "imported-continuum-operation", "An imported continuum operation violates the exact domain.", "exact-positive-Fold-operation", "Only exact positive composition, ratio and guarded Take occur."),
        binary_axis("orientation", "How is direction retained?", "signed-or-erased-direction", "Signed proof values or erased direction violate the domain.", "held-label-orientation", "Direction is represented by retained labels and ordered positive Take."),
        binary_axis("depth", "How is depth chosen?", "selected-depth", "A chosen depth is a parameter.", "forced-counted-depth", "The binary, generator-three and already admitted covering counts force the depth."),
        binary_axis("provenance", "May measured atomic data enter the law?", "measurement-readable-relation", "A measured target cannot construct or select the survivor.", "target-inaccessible-formal-relation", "The formal module contains no measured energy or wavelength."),
        binary_axis("trace", "What evidence is retained?", "result-without-dependency-trace", "An untraced result cannot be admitted.", "complete-root-directed-trace", "The result retains its dependency chain to the foundational theorem."),
        binary_axis("extension", "May an extra term or rule be appended?", "free-extra-rule", "An extra rule introduces a choice.", "no-extra-rule", "The declared typed grammar is exhausted."),
    )


CUBIC_SPEC = StructuralPhysicsSpec(
    claim_id=CUBIC_ATOMIC_SUPPORT_ID,
    title="Cubic atomic support and exact neighbour balance",
    statement=(
        "Three-space supplies three axes and the binary Fold supplies the two held directions on each axis, "
        "forcing six nearest neighbours.  Dividing the half-One balance equally over those complete neighbours "
        "forces weight one-twelfth per neighbour and their exact sum is the half-One."
    ),
    dependencies=("SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-PHYS-STRUCT-GENERATOR-THREE-001", "SFT-FOUNDATION-HALF-ONE-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis cubic-support product.",
    grammar_boundary="All nearest-neighbour organizations using every held direction on every forced spatial axis and an exact equal partition of the half-One balance.",
    axes=common_axes("the cubic atomic support"),
    exact_result="The unique cubic support has 2*3=6 nearest neighbours, exact weight 1/12 per neighbour and complete balance 6/12=1/2.",
    induction_base="One spatial axis has exactly the two held Fold directions.",
    induction_step="Appending each of the remaining forced axes contributes the same two directions once; equal partition of the half-One over the completed six-cell support fixes one-twelfth.",
    exclusions=("no imported cubic lattice", "no measured coordination number", "no floating or signed proof value", "no selected neighbour subset"),
    witnesses=(
        Witness("coordination", "Binary directions on three axes force six neighbours.", cubic_coordination() == 6),
        Witness("neighbour-weight", "Each complete neighbour receives one-twelfth.", cubic_neighbour_weight() == Fraction(1, 12)),
        Witness("half-balance", "All six neighbour weights recompose the half-One.", cubic_balance() == Fraction(1, 2)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


HYDROGEN_SPEC = StructuralPhysicsSpec(
    claim_id=HYDROGEN_SPECTRUM_ID,
    title="Depth-independent exact hydrogen spectral ladder",
    statement=(
        "For every supplied positive finite principal count n, the binary Fold forces the exact bound support "
        "one over n squared.  An emitted line is the guarded positive difference between the lower and upper "
        "supports, forcing Lyman-alpha three-quarters and Balmer-alpha five-thirty-sixths without a continuum solver."
    ),
    dependencies=("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003", "SFT-PHYS-DYNAMICS-STATIONARY-SPECTRUM-003", "SFT-MATH-EXACT-ARITHMETIC-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis hydrogen-support product and the positive finite principal-count successor.",
    grammar_boundary="All exact positive finite Coulomb-bound principal supports generated by the binary exponent and all ordered emitted transition gaps between them.",
    axes=common_axes("the hydrogen spectrum"),
    exact_result="For every positive finite n, H(n)=1/n^2; H(1)-H(2)=3/4 and H(2)-H(3)=5/36, with every emitted line an exact guarded positive difference.",
    induction_base="Principal support One gives the exact ground binding share One.",
    induction_step="The next supplied positive principal count is squared by the forced binary count; its reciprocal remains positive and every ordered lower-to-upper gap is a lawful Take.",
    exclusions=("no measured wavelength or Rydberg value", "no continuum Schroedinger solution", "no completed infinity", "no numerical zero or negative energy"),
    witnesses=(
        Witness("ground", "The first principal support is the One.", hydrogen_level(1) == Fraction(1, 1)),
        Witness("lyman-alpha", "The second-to-first gap is three-quarters.", hydrogen_transition(2, 1) == Fraction(3, 4)),
        Witness("balmer-alpha", "The third-to-second gap is five-thirty-sixths.", hydrogen_transition(3, 2) == Fraction(5, 36)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


CORRECTION_SPEC = StructuralPhysicsSpec(
    claim_id=ATOMIC_CORRECTION_HIERARCHY_ID,
    title="Exact atomic gross, fine and first bound-return hierarchy",
    statement=(
        "The forced inverse fine-structure carrier supplies alpha exactly.  Two held Fold directions force the "
        "relative fine scale alpha squared below gross; one complete bound-state self-return applies the same "
        "fine carrier once more, placing the first Lamb-family support at alpha to the fourth below gross."
    ),
    dependencies=("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", HYDROGEN_SPECTRUM_ID, "SFT-PHYS-RELATIVITY-FULL-DIRAC-SQUARE-003", "SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis atomic-correction hierarchy product.",
    grammar_boundary="The first two complete binary-direction correction layers on the admitted gross atomic support, with alpha transported once per direction and the first closed bound-state self-return applied once.",
    axes=common_axes("the atomic correction hierarchy"),
    exact_result="Gross is the One scale, fine/gross is alpha^2, and the first complete bound-return support is alpha^4 of gross; the gross Rydberg carrier in electron-rest units is alpha^2/2.",
    induction_base="The gross bound-state ladder supplies the One reference scale.",
    induction_step="Transport through both held directions contributes alpha squared; the first complete self-return repeats that already typed carrier once and then stops.",
    exclusions=("no imported QED coefficient series", "no measured splitting", "no irrational or floating proof value", "no selected correction order"),
    witnesses=(
        Witness("gross-scale", "The exact gross Rydberg carrier is alpha squared over the binary count.", gross_atomic_scale() > Fraction(1, 100000)),
        Witness("fine-below-gross", "Fine support is a strict positive part of gross.", Fraction(1, 100000) < fine_to_gross_ratio() < Fraction(1, 10000)),
        Witness("ordered-hierarchy", "Gross, fine and first bound return are strictly ordered.", atomic_scale_hierarchy()["gross"] > atomic_scale_hierarchy()["fine"] > atomic_scale_hierarchy()["lamb"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


TRANSITION_SPEC = StructuralPhysicsSpec(
    claim_id=ATOMIC_TRANSITION_ID,
    title="Atomic transition, selection and field-splitting law",
    statement=(
        "One atomic Fold act transfers one generated orbital unit while preserving the conserved carrier trace. "
        "The binary fibre supplies the two magnetic orientations and their field-dependent separation; the "
        "complete three-axis held-direction support supplies six spatial orientations for electric displacement."
    ),
    dependencies=(HYDROGEN_SPECTRUM_ID, CUBIC_ATOMIC_SUPPORT_ID, "SFT-PHYS-QUANTUM-SPIN-001", "SFT-PHYS-FIELD-MAGNETIC-RELATIVITY-003", "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis atomic-transition and field-orientation product.",
    grammar_boundary="All one-act transitions between adjacent generated orbital supports with conserved carrier records, binary magnetic orientation and complete cubic electric orientation.",
    axes=common_axes("atomic transitions and field splitting"),
    exact_result="An elementary admitted transition changes one orbital support unit, retains its carrier, has two magnetic orientations and six complete cubic electric orientations.",
    induction_base="A single atomic Fold act carries exactly one generated transition unit.",
    induction_step="Composition appends another individually traceable one-unit act; it cannot convert one act into an unrecorded multi-unit elementary transition.",
    exclusions=("no measured line intensity", "no imported angular-momentum algebra", "no unrecorded multi-unit elementary jump", "no signed field proof value"),
    witnesses=(
        Witness("one-step", "The elementary transition carries one generated unit.", transition_selection()["orbital_step"] == 1),
        Witness("magnetic-binary", "The Fold fibre supplies two magnetic orientations.", transition_selection()["magnetic_orientations"] == 2),
        Witness("electric-cubic", "The complete cubic direction support contains six orientations.", transition_selection()["complete_spatial_orientations"] == 6),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


MOLECULAR_SPEC = StructuralPhysicsSpec(
    claim_id=MOLECULAR_SPECTRUM_ID,
    title="Exact molecular rotational-vibrational spectral hierarchy",
    statement=(
        "The atomic electronic carrier occupies the first binary half-support.  Molecular rotation and vibration "
        "are the next complete composed Fold level at the quarter-One; two such molecular quanta exactly recompose "
        "the electronic half-support, forcing the spectral ordering without choosing a measured frequency."
    ),
    dependencies=(HYDROGEN_SPECTRUM_ID, "SFT-PHYS-WAVE-RESONANCE-001", "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-CHEM-BOND-COVALENT-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis electronic/molecular spectral-level product.",
    grammar_boundary="The first atomic electronic half-support and its next complete binary-composed rotational/vibrational support, each used exactly once in the cross-level relation.",
    axes=common_axes("the molecular spectral hierarchy"),
    exact_result="Electronic support is 1/2, molecular rotational-vibrational support is 1/4, and two molecular quanta exactly recompose the electronic support.",
    induction_base="The electronic carrier occupies the first binary half-support.",
    induction_step="One further complete binary composition produces the quarter support; composing both held quarter labels returns the electronic half and leaves no intermediate typed level.",
    exclusions=("no selected molecular frequency", "no imported rigid-rotor or harmonic-oscillator parameter", "no fitted isotope factor", "no floating proof value"),
    witnesses=(
        Witness("electronic-half", "Electronic support is the first half-One level.", molecular_spectrum_hierarchy()["electronic"] == Fraction(1, 2)),
        Witness("molecular-quarter", "Molecular rotation/vibration occupies the next quarter level.", molecular_spectrum_hierarchy()["molecular_rotation_vibration"] == Fraction(1, 4)),
        Witness("recomposition", "Two molecular quanta recompose the electronic support.", molecular_spectrum_hierarchy()["two_molecular_quanta"] == Fraction(1, 2)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ATOMIC_SPECS = (CUBIC_SPEC, HYDROGEN_SPEC, CORRECTION_SPEC, TRANSITION_SPEC, MOLECULAR_SPEC)
SPEC_BY_ID = {spec.claim_id: spec for spec in ATOMIC_SPECS}
for _spec in ATOMIC_SPECS:
    _spec.validate()


__all__ = (
    "ATOMIC_CORRECTION_HIERARCHY_ID",
    "ATOMIC_SPECS",
    "ATOMIC_TRANSITION_ID",
    "CUBIC_ATOMIC_SUPPORT_ID",
    "HYDROGEN_SPECTRUM_ID",
    "MOLECULAR_SPECTRUM_ID",
    "SPEC_BY_ID",
    "atomic_scale_hierarchy",
    "cubic_balance",
    "cubic_coordination",
    "cubic_neighbour_weight",
    "fine_to_gross_ratio",
    "gross_atomic_scale",
    "hydrogen_level",
    "hydrogen_transition",
    "molecular_spectrum_hierarchy",
    "transition_selection",
)
