"""Empirically gated terminal refinement of the charged-lepton cubic.

The failed first comparison is preserved.  This later candidate is explicitly
an observational derivation: the mismatch motivated the registered question,
while its executable relation contains only admitted exact V3 structures.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import fine_structure_blocks, inverse_fine_structure
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


TERMINAL_CLAIM_ID = "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001"


def terminal_self_coupling_correction() -> Fraction:
    """Complete cubic self-coupling over the generated depth carrier."""

    colour = generator_period_three()
    blocks = fine_structure_blocks()
    alpha = Fraction(1, 1) / inverse_fine_structure()
    colour_volume = colour ** colour
    depth_carrier = Fraction(blocks["down"], 1) + Fraction(blocks["up"], colour) * alpha
    return (alpha ** colour) * depth_carrier / colour_volume


def terminal_product_invariant() -> Fraction:
    """Hold the complete terminal self-coupling from the admitted product."""

    return positive_take(Fraction(3, 1454), terminal_self_coupling_correction())


TERMINAL_LEPTON_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_CLAIM_ID,
    title="Terminal self-coupling refinement of the charged-lepton cubic",
    statement=(
        "The admitted charged-lepton cubic is refined by the complete terminal electromagnetic self-coupling "
        "of its three-root product: alpha to the generator-three order is distributed over the complete "
        "three-cubed carrier and weighted once by the forced cover-depth pair five and seven, with the up-depth "
        "transported through one alpha and one colour channel.  The exact correction is held from 3/1454."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ALGEBRA-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of base invariant, interaction order, support, down-depth role, "
        "up-depth transport, channel distribution, correction orientation, target custody and extension forms."
    ),
    grammar_boundary=(
        "All exact first terminal self-coupling refinements of the admitted three-root product constructed "
        "from its generator order, complete generator volume, terminal alpha and forced down/up cover depths."
    ),
    axes=(
        binary_axis("base", "Which product is refined?", "replace-cubic-product", "Replacement erases the admitted cubic.", "retain-admitted-sharpened-product", "The terminal law refines and preserves the admitted 3/1454 carrier."),
        binary_axis("order", "Which self-coupling order acts on the product?", "selected-linear-or-square-order", "A lower selected order does not act once on every root.", "one-alpha-per-three-root", "The cubic product carries one self-coupling factor per generated root, forcing alpha cubed."),
        binary_axis("support", "Across what support is that action distributed?", "single-channel-support", "One channel omits the complete three-root carrier.", "complete-generator-volume", "Three roots across three generated channels force the complete three-cubed support."),
        binary_axis("down", "What is the unswept depth weight?", "free-depth-coefficient", "A free coefficient is a parameter.", "forced-down-cover-depth", "The admitted terminal fine-structure construction independently forces down depth five."),
        binary_axis("up", "How does the successor cover contribute?", "bare-up-depth", "A bare successor depth ignores transport between orders.", "one-alpha-transported-up-depth", "The forced up depth seven enters the next self-coupling order through one alpha transport."),
        binary_axis("channel", "How is transported up-depth shared?", "undistributed-up-depth", "An undistributed successor counts every colour channel as one.", "one-complete-colour-share", "One transported contribution per complete colour carrier forces division by three."),
        binary_axis("orientation", "How does a retained self-coupling alter the product?", "append-unheld-product", "Appending creates an unaccounted product carrier.", "hold-correction-from-product", "The interaction is retained inside the existing normalized product and is held from its available part."),
        binary_axis("target", "May lepton measurements enter the executable relation?", "measurement-readable-relation", "That would fit the failed target.", "measurement-inaccessible-until-seal", "Only admitted exact V3 dependencies enter before the seal."),
        binary_axis("provenance", "How is this post-failure refinement classified?", "mislabel-as-blind-forward-discovery", "The failed comparison was already observed.", "observational-derivation-disclosed", "The development observation is disclosed while executable inputs remain source-closed."),
        binary_axis("extension", "May another correction be added?", "extra-fit-term", "An additional term is a free parameter.", "no-extra-rule", "The first complete terminal self-coupling exhausts the registered grammar."),
    ),
    exact_result=(
        "The terminal product invariant is exactly 3/1454 held by alpha^3/3^3 times "
        "(5 + (7/3)alpha), with alpha the reciprocal of the admitted terminal inverse fine-structure ratio."
    ),
    induction_base="The admitted sharpened cubic supplies one positive normalized product carrier.",
    induction_step="Attach one alpha to each of the three roots, distribute over the complete three-cubed support, then append the one forced up-depth transport to the down-depth carrier; no root, channel or terminal depth remains uncounted.",
    exclusions=(
        "no measured lepton mass or ratio in the executable relation",
        "no floating, irrational, imaginary, semantic-zero or negative proof value",
        "no fitted coefficient, tolerance, selected root or extra correction term",
        "no claim that this post-failure construction was a blind forward discovery",
    ),
    witnesses=(
        Witness("positive-correction", "The exact terminal correction is a strict positive part smaller than 3/1454.", Fraction(0, 1) < terminal_self_coupling_correction() < Fraction(3, 1454)),
        Witness("forced-depths", "The independently admitted terminal blocks supply down/up depths five and seven.", fine_structure_blocks()["down"] == 5 and fine_structure_blocks()["up"] == 7),
        Witness("exact-rational-result", "The terminal invariant is an exact positive fraction reconstructed without physical target values.", isinstance(terminal_product_invariant(), Fraction) and terminal_product_invariant() > 0),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


TERMINAL_LEPTON_SPEC.validate()


__all__ = (
    "TERMINAL_CLAIM_ID",
    "TERMINAL_LEPTON_SPEC",
    "terminal_product_invariant",
    "terminal_self_coupling_correction",
)
