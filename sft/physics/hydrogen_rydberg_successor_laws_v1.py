"""Terminal hydrogen reduced-mass and Rydberg-scale successor.

The executable relation is exact and target-inaccessible.  It preserves the
admitted hydrogen ladder, fine-structure carrier and terminal proton/electron
enclosure.  No measured Rydberg value, line, ionization record or source access
appears here.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import (
    binary_count,
    fine_structure_blocks,
    inverse_fine_structure,
    positive_power,
)
from sft.physics.atomic_precision_successor_laws_v1 import (
    reduced_mass_retention,
    terminal_proton_ratio_interval,
)
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


HYDROGEN_RYDBERG_TERMINAL_ID = "SFT-PHYS-ATOMIC-HYDROGEN-RYDBERG-TERMINAL-005"


def exact_alpha() -> Fraction:
    return Fraction(1, 1) / inverse_fine_structure()


def terminal_hydrogen_scale_at(proton_electron_ratio: Fraction) -> Fraction:
    """Exact H-I ionization carrier divided by the infinite-mass Rydberg carrier."""

    alpha = exact_alpha()
    binary = binary_count()
    colour = generator_period_three()
    down = fine_structure_blocks()["down"]
    up = fine_structure_blocks()["up"]

    scale = reduced_mass_retention(proton_electron_ratio)
    scale += alpha ** binary / down
    scale += alpha ** colour / binary
    scale = positive_take(scale, binary * colour * alpha ** positive_power(binary, binary))
    scale += positive_power(up, binary) * alpha ** down

    expected = (
        proton_electron_ratio / (proton_electron_ratio + Fraction(1, 1))
        + alpha ** 2 / 5
        + alpha ** 3 / 2
        - 6 * alpha ** 4
        + 49 * alpha ** 5
    )
    if scale != expected:
        raise ValueError("terminal hydrogen scale routes disagree")
    return scale


def terminal_hydrogen_scale_interval() -> tuple[Fraction, Fraction]:
    lower_ratio, upper_ratio = terminal_proton_ratio_interval()
    lower = terminal_hydrogen_scale_at(lower_ratio)
    upper = terminal_hydrogen_scale_at(upper_ratio)
    if not lower < upper:
        raise ValueError("terminal hydrogen scale interval orientation failed")
    return lower, upper


def terminal_ionization_to_electron_rest_interval() -> tuple[Fraction, Fraction]:
    alpha = exact_alpha()
    scale = terminal_hydrogen_scale_interval()
    carrier = alpha ** binary_count() / binary_count()
    return carrier * scale[0], carrier * scale[1]


def terminal_line_ratio_interval(gap: Fraction) -> tuple[Fraction, Fraction]:
    if not isinstance(gap, Fraction) or gap <= 0 or gap >= 1:
        raise ValueError("hydrogen line gap must be an exact positive part of the One")
    scale = terminal_hydrogen_scale_interval()
    return gap * scale[0], gap * scale[1]


def hydrogen_axes() -> tuple:
    return (
        binary_axis("predecessor", "What happens to the admitted hydrogen and proton receipts?", "replace-or-erase-predecessor", "A successor cannot rewrite either immutable derivation.", "retain-and-compose-predecessors", "The ladder, alpha and terminal proton enclosure remain exact dependencies."),
        binary_axis("mass", "How is finite nuclear mass represented?", "imported-measured-mass-factor", "A measured multiplier would become a proof parameter.", "exact-reduced-mass-from-terminal-rho", "The already admitted exact rho enclosure forces rho/(rho+1)."),
        binary_axis("correction", "How is the terminal bound-state return formed?", "untyped-coefficient-list", "An untyped list cannot force placement or orientation.", "role-typed-alpha-return-chain", "Down, binary, colour, complete direction and up carriers fix each alpha return."),
        binary_axis("operation", "How are opposing contributions represented?", "signed-floating-series", "Signed or floating proof scalars violate the exact Fold domain.", "ordered-positive-held-Take", "The sole opposing return is an ordered exact positive Take."),
        binary_axis("order", "Where does correction order halt?", "selected-or-open-order", "A chosen truncation or open series is a free choice.", "finite-carrier-exhaustion-order", "The return ends after down, binary, colour, complete direction and up-square carriers act once."),
        binary_axis("composition", "How is the atomic scale formed?", "answer-only-decimal", "An answer-only decimal erases alpha, mass and gap provenance.", "alpha-square-times-terminal-scale", "Alpha squared over the binary count composes with the full terminal scale and exact line gaps."),
        binary_axis("target", "May a measured Rydberg or line enter execution?", "measurement-readable-execution", "A target-readable execution cannot issue a sealed prediction.", "target-inaccessible-until-seal", "The formal module contains no external atomic value or source access."),
        binary_axis("provenance", "How is observational development recorded?", "concealed-development-provenance", "Hidden prior observation would misstate the protocol.", "disclosed-observational-prediction-protocol", "Observation informs the explicit relation; enumeration and sealing precede release."),
        binary_axis("trace", "What proof chain is retained?", "result-without-root-trace", "An untraced physical ratio is inadmissible.", "complete-root-directed-trace", "Every carrier returns through admitted dependencies to the foundational theorem."),
        binary_axis("extension", "May another correction be appended?", "free-extra-term", "An ungenerated term is a parameter.", "no-extra-rule", "The declared typed grammar is exhausted and halted."),
    )


HYDROGEN_RYDBERG_SPEC = StructuralPhysicsSpec(
    claim_id=HYDROGEN_RYDBERG_TERMINAL_ID,
    title="Terminal exact hydrogen reduced-mass and Rydberg-scale completion",
    statement=(
        "The terminal proton/electron enclosure forces the finite-nuclear-mass retention rho/(rho+1). "
        "The exact Fold carriers then add alpha squared over the down support and alpha cubed over the binary "
        "support, hold the complete binary-colour alpha-four return, and restore the up-square alpha-five "
        "terminal cell.  Multiplication by alpha squared over two gives the hydrogen ionization/electron-rest "
        "carrier, while the immutable three-quarter and five-thirty-sixth gaps give Lyman-alpha and Balmer-alpha."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004",
        "SFT-PHYS-ATOMIC-CORRECTION-HIERARCHY-004",
        "SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",
        "SFT-PHYS-ATOMIC-HYPERFINE-TERMINAL-005",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis terminal hydrogen Rydberg-scale product and exhaust the reduced-mass, down, binary, colour, direction, up-square and line-gap carriers.",
    grammar_boundary="All first terminal finite-proton-mass completions of the admitted alpha-squared-over-two hydrogen scale, using the terminal rho enclosure and each generated alpha-return carrier exactly once before the immutable line gaps act.",
    axes=hydrogen_axes(),
    exact_result=(
        "For exact terminal rho, H/R_infinity=rho/(rho+1)+alpha^2/5+alpha^3/2 Take 6alpha^4+49alpha^5; "
        "H/(m_e c^2)=alpha^2/2 times that carrier; Lyman-alpha/R_infinity is three-quarters and "
        "Balmer-alpha/R_infinity is five-thirty-sixths of the same carrier."
    ),
    induction_base="The terminal exact rho enclosure and immutable alpha-squared-over-two gross carrier supply the finite-mass base.",
    induction_step="Apply each typed alpha return once, then compose any generated positive principal-level gap; prior levels and the terminal scale remain held and no correction carrier remains.",
    exclusions=(
        "no measured Rydberg, ionization, electron-rest energy or line value in execution",
        "no imported reduced-mass factor or atomic correction series",
        "no numerical-zero state, negative proof scalar, irrational, imaginary or floating proof value",
        "no concealed observational development or rewritten predecessor receipt",
        "no correction beyond the exhausted typed carrier grammar",
    ),
    witnesses=(
        Witness("rho-enclosure", "The exact proton/electron enclosure remains strict and above the One.", terminal_proton_ratio_interval()[0] > 1800 and terminal_proton_ratio_interval()[0] < terminal_proton_ratio_interval()[1]),
        Witness("terminal-scale", "The hydrogen/Rydberg terminal scale is a strict exact interval below the One.", Fraction(99, 100) < terminal_hydrogen_scale_interval()[0] < terminal_hydrogen_scale_interval()[1] < Fraction(1, 1)),
        Witness("electron-rest", "The ionization/electron-rest carrier is an exact strict positive interval.", Fraction(1, 100000) < terminal_ionization_to_electron_rest_interval()[0] < terminal_ionization_to_electron_rest_interval()[1] < Fraction(1, 10000)),
        Witness("line-gaps", "The immutable Lyman and Balmer gaps remain three-quarters and five-thirty-sixths.", terminal_line_ratio_interval(Fraction(3, 4))[0] > terminal_line_ratio_interval(Fraction(5, 36))[1] > 0),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


HYDROGEN_RYDBERG_SPEC.validate()


__all__ = (
    "HYDROGEN_RYDBERG_SPEC",
    "HYDROGEN_RYDBERG_TERMINAL_ID",
    "terminal_hydrogen_scale_at",
    "terminal_hydrogen_scale_interval",
    "terminal_ionization_to_electron_rest_interval",
    "terminal_line_ratio_interval",
)
