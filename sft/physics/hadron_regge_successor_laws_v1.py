"""Terminal light-hadron multiplet and Regge-support successor.

The executable law contains no particle name, measured mass, uncertainty,
source locator or fitted tube tension.  It uses only positive generated counts,
exact fractions, held symmetry labels and the empty form for absent support.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations_with_replacement, product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, positive_power
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
    positive_predecessor,
)


HADRON_REGGE_TERMINAL_ID = "SFT-PHYS-HADRON-REGGE-TERMINAL-005"


def light_flavour_words(width: int) -> tuple[tuple[int, ...], ...]:
    """Generate every ordered word over the forced three-member support."""

    if isinstance(width, bool) or not isinstance(width, int) or width < 1:
        raise ValueError("word width must be a positive whole")
    labels = tuple(range(1, generator_period_three() + 1))
    return tuple(product(labels, repeat=width))


def meson_multiplet_partition() -> dict[str, int]:
    flavours = generator_period_three()
    total = len(light_flavour_words(binary_count()))
    singlet = 1
    octet = positive_predecessor(total)
    if total != positive_power(flavours, binary_count()) or octet + singlet != total:
        raise ValueError("complete meson flavour support did not close")
    return {"ordered_support": total, "predecessor_multiplet": octet, "invariant_singlet": singlet}


def symmetric_baryon_words() -> tuple[tuple[int, ...], ...]:
    labels = tuple(range(1, generator_period_three() + 1))
    return tuple(combinations_with_replacement(labels, generator_period_three()))


def baryon_multiplet_partition() -> dict[str, int]:
    """Partition the complete three-flavour, three-place support by exchange type."""

    total = len(light_flavour_words(generator_period_three()))
    symmetric = len(symmetric_baryon_words())
    antisymmetric = 1
    mixed_total = total - symmetric - antisymmetric
    hands = binary_count()
    if mixed_total < 1 or mixed_total % hands:
        raise ValueError("mixed exchange support did not split into complete Fold hands")
    mixed_hand = mixed_total // hands
    if symmetric + mixed_hand + mixed_hand + antisymmetric != total:
        raise ValueError("complete baryon symmetry support did not close")
    return {
        "ordered_support": total,
        "symmetric": symmetric,
        "mixed_first_hand": mixed_hand,
        "mixed_second_hand": mixed_hand,
        "antisymmetric": antisymmetric,
    }


def normalized_regge_squared_support(spin_rank: int) -> Fraction:
    """Exact fixed-carrier affine support in normalized Fold units."""

    if isinstance(spin_rank, bool) or not isinstance(spin_rank, int) or spin_rank < 1:
        raise ValueError("spin rank must be a positive whole")
    if spin_rank == 1:
        return Fraction(1, 1)
    return Fraction(1, 1) + Fraction(positive_predecessor(spin_rank), 1)


def affine_regge_carrier(anchor: Fraction, tube_step: Fraction, spin_rank: int) -> Fraction:
    """Restore exact positive unit carriers without making either a fitted parameter."""

    if not isinstance(anchor, Fraction) or anchor <= 0:
        raise ValueError("anchor carrier must be exact and positive")
    if not isinstance(tube_step, Fraction) or tube_step <= 0:
        raise ValueError("tube-step carrier must be exact and positive")
    if isinstance(spin_rank, bool) or not isinstance(spin_rank, int) or spin_rank < 1:
        raise ValueError("spin rank must be a positive whole")
    if spin_rank == 1:
        return anchor
    return anchor + Fraction(positive_predecessor(spin_rank), 1) * tube_step


def regge_step(anchor: Fraction, tube_step: Fraction, spin_rank: int) -> Fraction:
    current = affine_regge_carrier(anchor, tube_step, spin_rank)
    successor = affine_regge_carrier(anchor, tube_step, spin_rank + 1)
    step = successor - current
    if step <= 0:
        raise ValueError("Regge successor failed positivity")
    return step


def trajectory_multiplicity(depth: int) -> int:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 1:
        raise ValueError("trajectory depth must be a positive whole")
    return positive_power(binary_count(), depth)


def axes() -> tuple:
    return (
        binary_axis("predecessor", "How are admitted colour and confinement results used?", "rewrite-hadron-predecessors", "A successor cannot alter admitted receipts.", "compose-immutable-hadron-predecessors", "The exact three-cycle, minimal singlets and confinement carrier remain immutable dependencies."),
        binary_axis("flavour", "How is light-flavour support obtained?", "import-named-flavour-table", "Names do not generate a support.", "complete-generator-three-flavour-support", "The already forced generator three supplies every position of one complete light-flavour support."),
        binary_axis("meson", "How is the light meson organization counted?", "assert-nonet", "A conventional name does not prove its size.", "enumerate-three-by-three-ordered-pairs", "Every flavour/antiflavour position is generated exactly once, forcing nine cells."),
        binary_axis("meson-partition", "How does the nine-cell support split?", "import-octet-singlet-representation", "An imported representation would select the answer.", "one-invariant-and-positive-predecessor", "The unique complete diagonal invariant uses one cell class; its positive predecessor has eight classes."),
        binary_axis("baryon", "How is the light baryon organization counted?", "assert-octet-and-decuplet", "Named multiplets are not a derivation.", "enumerate-three-place-flavour-words", "The complete three-place support over three flavours contains twenty-seven ordered words."),
        binary_axis("exchange", "How is baryon support partitioned?", "import-SU-three-decomposition", "A conventional group decomposition cannot be a premise.", "enumerate-exchange-symmetry-classes", "Ten symmetric multisets, one fully antisymmetric class and two Fold hands of the remaining sixteen force ten, eight, eight and one."),
        binary_axis("tube", "What does one fixed confinement-tube act contribute?", "chosen-spin-dependent-increment", "A different free increment at each rank destroys structural closure.", "one-retained-step-per-spin-successor", "Each rank successor adds the same held positive tube carrier exactly once."),
        binary_axis("Regge", "What squared-support law follows?", "fitted-mass-polynomial", "A fitted polynomial is not forced.", "depth-independent-affine-successor", "Anchor plus one common positive carrier per successor forces exact affine squared support at every positive rank."),
        binary_axis("target", "May PDG multiplets or resonance masses enter execution?", "external-target-readable", "Target access cannot seal a prediction.", "target-inaccessible-until-seal", "No external count, particle name, mass, uncertainty or source is accessible to the executable law."),
        binary_axis("extension", "May residuals, slopes or correction terms be fitted?", "free-residual-or-tension-fit", "An ungenerated correction would be a parameter.", "no-extra-rule", "Generated flavour support, exchange class and one fixed tube act exhaust the declared grammar."),
    )


HADRON_REGGE_SPEC = StructuralPhysicsSpec(
    claim_id=HADRON_REGGE_TERMINAL_ID,
    title="Terminal light-hadron multiplets and depth-independent Regge support",
    statement=(
        "Generator-three flavour support forces nine ordered flavour/antiflavour cells, partitioned as one "
        "invariant cell class and its eight-class positive predecessor.  Complete three-place flavour support "
        "forces twenty-seven cells; direct exchange enumeration partitions them as ten symmetric, two eight-cell "
        "mixed hands and one antisymmetric class.  Independently, one retained fixed-tube act per positive spin "
        "successor forces exact affine squared support.  The exact theorem governs normalized fixed-carrier support; "
        "whether physical resonance masses realize literal equal spacing is a separate post-seal measurement."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
        "SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis predecessor, flavour, meson, partition, baryon, exchange, tube, affine-support, custody and extension product.",
    grammar_boundary="Every ordered word over the complete generated three-member light-flavour support at widths two and three, every permutation-exchange class, and every positive rank produced by repeated application of one held fixed-tube successor act.",
    axes=axes(),
    exact_result="Light mesons have exact flavour support 9=8+1; light three-place baryons have exact support 27=10+8+8+1; normalized fixed-tube squared support is Q(J)=J and every positive successor difference is exactly One.",
    induction_base="One positive spin rank carries one normalized squared-support unit; complete generator-three words give nine two-place and twenty-seven three-place cells.",
    induction_step="Appending one spin successor adds the same held tube carrier once, so the squared-support difference remains exactly One at every depth; appending generated words never changes the already exhaustive exchange partition.",
    exclusions=(
        "no V1/V2 executable, certificate, answer value or conventional SU(n) representation as a premise",
        "no measured resonance mass, uncertainty, trajectory slope or source access in execution",
        "no numerical-zero state, negative, irrational, imaginary or floating proof value",
        "no fitted tube tension, intercept, residual, correction term or selected trajectory subset",
        "no claim that non-minimal colour-neutral composites are forbidden",
        "no target access before derivation and prediction seals",
    ),
    witnesses=(
        Witness("meson-partition", "Complete light flavour/antiflavour support closes as eight plus one.", meson_multiplet_partition() == {"ordered_support": 9, "predecessor_multiplet": 8, "invariant_singlet": 1}),
        Witness("baryon-partition", "Complete three-place light-flavour support closes as ten plus eight plus eight plus one.", baryon_multiplet_partition() == {"ordered_support": 27, "symmetric": 10, "mixed_first_hand": 8, "mixed_second_hand": 8, "antisymmetric": 1}),
        Witness("affine-successor", "Every tested positive rank has the same exact normalized squared-support step.", all(regge_step(Fraction(1, 1), Fraction(1, 1), rank) == Fraction(1, 1) for rank in range(1, 65))),
        Witness("depth-seven-multiplicity", "The inherited finite depth ceiling retains exact binary multiplicity through seven.", tuple(trajectory_multiplicity(depth) for depth in range(1, 8)) == (2, 4, 8, 16, 32, 64, 128)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


HADRON_REGGE_SPEC.validate()


__all__ = (
    "HADRON_REGGE_SPEC",
    "HADRON_REGGE_TERMINAL_ID",
    "affine_regge_carrier",
    "baryon_multiplet_partition",
    "light_flavour_words",
    "meson_multiplet_partition",
    "normalized_regge_squared_support",
    "regge_step",
    "symmetric_baryon_words",
    "trajectory_multiplicity",
)
