"""Exact zero-parameter dimensional carrier for the light-hadron Regge ladder."""

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count
from sft.physics.relativistic_field_laws_v1 import two_hand_dirac_square
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059"


def motion_share() -> Fraction:
    share = two_hand_dirac_square()["momentum"]
    if share != Fraction(3, 5):
        raise ValueError("admitted three-motion share changed")
    return share


def tube_successor_share() -> Fraction:
    share = binary_count() * motion_share()
    if share != Fraction(6, 5):
        raise ValueError("paired tube successor did not close as six-fifths")
    return share


def squared_resonance_carrier(spin_rank: int) -> Fraction:
    if isinstance(spin_rank, bool) or not isinstance(spin_rank, int) or spin_rank < 1:
        raise ValueError("spin rank must be a positive whole")
    return motion_share() + Fraction(spin_rank - 1, 1) * tube_successor_share()


def theorem_certificate(depth: int = 64) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("certificate depth must be a positive whole above the One")
    carriers = tuple(squared_resonance_carrier(rank) for rank in range(1, depth + 1))
    return {
        "motion_share": motion_share(),
        "tube_hands": binary_count(),
        "successor_share": tube_successor_share(),
        "carriers": carriers,
        "first_five": carriers[:5],
        "all_positive": all(value > 0 for value in carriers),
        "constant_successor": all(carriers[index + 1] - carriers[index] == Fraction(6, 5) for index in range(len(carriers) - 1)),
        "closed_form": all(value == Fraction(6 * rank - 3, 5) for rank, value in enumerate(carriers, start=1)),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal dimensional light-hadron Regge carrier",
    statement=(
        "The admitted two-hand relativistic closure forces the exact positive three-motion share 3/5. A confined "
        "rotating tube has the two forced Fold hands, so one spin successor retains one motion share on each hand and "
        "adds 2(3/5)=6/5 squared-support units. The first positive spin rank carries the unsucceeded 3/5 motion share. "
        "Therefore every positive rank is forced depth-independently as Q(J)=3/5+(J-1)6/5=(6J-3)/5. No slope, "
        "intercept, resonance mass, width or residual is fitted or available to the formal execution."
    ),
    dependencies=(
        "SFT-PHYS-HADRON-REGGE-TERMINAL-005",
        "SFT-PHYS-RELATIVITY-TWO-HAND-DIRAC-SQUARE-003",
        "SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of predecessor custody, motion share, tube hands, base rank, successor act, closed form, unit boundary, target custody and extension forms.",
    grammar_boundary="The admitted exact 3/5 motion share, exactly two Fold tube hands, every positive spin successor, exact positive fractions, a post-seal common unit label and no measurement in survivor selection.",
    axes=(
        binary_axis("predecessor", "How are earlier laws used?", "rewrite-or-ignore-admitted-laws", "A successor may not replace an admitted dependency.", "immutable-receipt-custody", "The relativistic and confinement receipts remain immutable inputs."),
        binary_axis("motion", "What is the first rotating carrier?", "selected-or-fitted-intercept", "A selected intercept reads the spectrum.", "admitted-three-fifths-motion-share", "Three spatial motion positions over the forced 3-4-5 closure give exact 3/5."),
        binary_axis("hands", "How many tube contributions enter one successor?", "chosen-trajectory-multiplicity", "A chosen multiplicity changes the slope.", "both-forced-Fold-hands", "The confined tube retains both Fold hands exactly once."),
        binary_axis("successor", "What does one spin successor add?", "fitted-common-slope", "A measured slope is not a derivation.", "two-times-three-fifths", "One 3/5 motion share on each of two hands forces 6/5."),
        binary_axis("base", "Where does the positive ladder begin?", "numerical-zero-or-free-offset", "Neither numerical nothingness nor an offset is generated.", "first-positive-rank-three-fifths", "The first positive spin rank retains the unsucceeded motion share."),
        binary_axis("closure", "How does the rule extend?", "finite-five-row-pattern", "Five inspected rows do not establish a general law.", "depth-independent-induction", "Every successor repeats the same paired tube act, forcing (6J-3)/5 for every positive J."),
        binary_axis("units", "Can a conventional unit alter the law?", "unit-name-selects-coefficients", "A unit label cannot choose a ratio.", "postseal-common-positive-unit", "A common positive squared comparison unit is held only after the exact rational law seals."),
        binary_axis("target", "May measured resonances select the survivor?", "target-readable-before-seal", "That would fit the known spectrum.", "target-inaccessible-until-formal-seal", "No particle name, mass, width, uncertainty or source exists in this module."),
        binary_axis("extension", "May a residual correction be appended?", "free-spin-correction", "An ungenerated correction is a parameter.", "no-extra-rule", "Motion, both hands, base and successor exhaust the declared grammar."),
    ),
    exact_result="Every positive spin rank has the exact squared resonance-support carrier Q(J)=(6J-3)/5. The base is 3/5; every successor step is 6/5; the first five carriers are 3/5, 9/5, 3, 21/5 and 27/5.",
    induction_base="At J=1 the rotating carrier is the admitted three-motion share 3/5.",
    induction_step="If Q(J)=(6J-3)/5, the next two-hand tube act adds 6/5, giving Q(J+1)=(6J+3)/5=(6(J+1)-3)/5.",
    exclusions=(
        "no fitted or measured Regge slope, intercept, mass, width, residual or selected trajectory row",
        "no imported string-tension parameter or continuum string equation",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof scalar",
        "no pre-seal physical-unit calibration or target access",
    ),
    witnesses=(
        Witness("motion", "The admitted rotating motion share is exactly 3/5.", motion_share() == Fraction(3, 5)),
        Witness("successor", "Two Fold hands force exact successor share 6/5.", tube_successor_share() == Fraction(6, 5)),
        Witness("first-five", "The first five carriers are generated without measurement.", theorem_certificate()["first_five"] == (Fraction(3, 5), Fraction(9, 5), Fraction(3, 1), Fraction(21, 5), Fraction(27, 5))),
        Witness("induction", "The exact closed form and constant step hold at every registered witness depth.", theorem_certificate()["constant_successor"] and theorem_certificate()["closed_form"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)

SPEC.validate()

__all__ = ("CLAIM_ID", "SPEC", "motion_share", "squared_resonance_carrier", "theorem_certificate", "tube_successor_share")
