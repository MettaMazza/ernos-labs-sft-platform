"""Independent V3 reconstruction of physical-value laws recorded by V1/V2.

The earlier records define mandatory questions and comparison targets.  They do
not enter this executable module.  Candidate generation and elimination use
only already admitted V3 structure; comparison with the registered prior result
and external measurements occurs after admission.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
    positive_predecessor,
    value_axis,
)


CHARGED_LEPTON_CUBIC_CLAIM_ID = "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001"


def positive_take(whole: Fraction, part: Fraction) -> Fraction:
    """Return a positive held remainder and reject a nonpositive result."""

    if whole <= part or part <= 0:
        raise ValueError("positive take requires a smaller positive part")
    return whole - part


def lepton_leading_denominator() -> int:
    """Construct the predecessor of two complete colour fifth-power supports."""

    colour = generator_period_three()
    return positive_predecessor((colour ** colour) * colour * colour + (colour ** colour) * colour * colour)


def lepton_sharpened_invariant(channel: int) -> Fraction:
    """Sharpen the third invariant through one registered channel part."""

    if channel not in (2, 3, 4):
        raise ValueError("channel must be in the complete neighbouring generator census")
    denominator = positive_take(Fraction(lepton_leading_denominator(), 1), Fraction(1, channel))
    return Fraction(1, 1) / denominator


def charged_lepton_invariants() -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return sum, pair sum, leading product and forced sharpened product."""

    colour = generator_period_three()
    fibre_count = positive_predecessor(colour)
    root_sum = Fraction(1, 1)
    pair_sum = Fraction(1, fibre_count * colour)
    leading_product = Fraction(1, lepton_leading_denominator())
    sharpened_product = lepton_sharpened_invariant(colour)
    return root_sum, pair_sum, leading_product, sharpened_product


CHARGED_LEPTON_CUBIC_SPEC = StructuralPhysicsSpec(
    claim_id=CHARGED_LEPTON_CUBIC_CLAIM_ID,
    title="Exact charged-lepton cubic invariants",
    statement=(
        "The forced generator-three partition supplies one exact three-root mass carrier whose symmetric "
        "invariants are root sum One, pair sum one over the two Fold fibres paired with generator three, "
        "leading product one over the positive predecessor of twice the colour fifth-power support, and "
        "sharpened product obtained by the unique generator-three channel part.  The resulting exact "
        "invariants are 1, 1/6, 1/485 and 3/1454; no irrational root is formed."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ALGEBRA-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of cubic carrier, generator, partition, pair invariant, leading "
        "support, predecessor, sharpening channel, sharpening form, root boundary and extra-rule forms; "
        "enumerate channels two, three and four without measurement access."
    ),
    grammar_boundary=(
        "All exact positive-rational symmetric three-root invariant constructions made from the admitted "
        "Fold fibre count, generator three, complete colour fifth-power support, positive predecessor and "
        "one neighbouring generated channel part."
    ),
    axes=(
        binary_axis("carrier", "What carries three mass positions?", "three-names-without-joint-invariants", "Names do not retain one cubic relation.", "one-complete-symmetric-three-root-carrier", "One carrier retains all three roots through their exact symmetric invariants."),
        binary_axis("generator", "What fixes the root count?", "selected-three", "A familiar generation count cannot be assumed.", "admitted-generator-three", "The independently admitted second Fold generator fixes the complete three-position carrier."),
        binary_axis("partition", "What fixes the root sum?", "unnormalized-root-sum", "An unnormalized sum adds a free scale.", "root-sum-is-the-One", "The complete three-position carrier is a no-loss partition of the One."),
        value_axis("pair", "Which pair invariant is forced?", (("one-over-colour", "This omits the two Fold fibres."), ("one-over-two-colour", ""), ("one-over-colour-square", "This substitutes a colour pair for the Fold-fibre pairing.")), "one-over-two-colour", "The two Fold fibres pair once with the generator-three carrier, forcing 1/(2*3)=1/6."),
        binary_axis("support", "What supplies the leading product support?", "colour-fourth-power", "This stops before the complete fifth colour succession.", "twice-colour-fifth-power", "Two Fold fibres carry the complete colour fifth-power support."),
        binary_axis("predecessor", "How is the leading denominator closed?", "support-count-itself", "The complete support retains the terminal One rather than the massive interior.", "positive-predecessor-of-support", "The unique positive predecessor removes the terminal One without using numerical zero or a negative quantity."),
        value_axis("channel", "Which generated channel sharpens the product?", (("binary-channel", "The binary channel is not the carrier's generator identity."), ("colour-channel", ""), ("successor-channel", "The successor channel adds an ungenerated carrier role.")), "colour-channel", "Only the generator-three channel is identical to the three-root carrier being sharpened."),
        binary_axis("sharpening", "How does the channel refine the denominator?", "add-channel-whole", "A whole channel count changes scale rather than resolves one channel part.", "positive-take-one-channel-part", "One exact channel part is held from the leading support predecessor, preserving a positive denominator."),
        binary_axis("roots", "Must irrational roots be produced?", "solve-and-round-roots", "Root approximation introduces brackets and stopping choices.", "retain-exact-symmetric-invariants", "Vieta-complete invariants carry the cubic without irrational or floating proof values."),
        binary_axis("extension", "May another coefficient or selector enter?", "extra-coefficient-or-measured-selector", "An added number or target-selected channel is a free parameter.", "no-extra-rule", "The admitted counts, products, predecessor and channel identity exhaust the registered grammar."),
    ),
    exact_result=(
        "The exact charged-lepton cubic invariant tuple is (sum=1, pair-sum=1/6, "
        "leading-product=1/485, sharpened-product=3/1454), with the sharpened "
        "colour channel uniquely retained over channels two, three and four."
    ),
    induction_base="The structural One supplies the complete normalized three-position partition and its retained symmetric identities.",
    induction_step="Appending each generated pair or triple product records it once in the symmetric ledger; the generator-three channel adds its exact held part while preserving every earlier invariant.",
    exclusions=(
        "no V1/V2 executable, certificate or answer table in the derivation runtime",
        "no measured lepton mass or ratio may select a coefficient or channel",
        "no numerical zero, negative, irrational, imaginary or floating proof value",
        "no fitted root, bracket, tolerance, iteration count or extra coefficient",
    ),
    witnesses=(
        Witness("exact-invariants", "The four independently constructed invariants equal 1, 1/6, 1/485 and 3/1454.", charged_lepton_invariants() == (Fraction(1, 1), Fraction(1, 6), Fraction(1, 485), Fraction(3, 1454))),
        Witness("channel-census", "The complete channels two, three and four produce distinct exact sharpenings.", tuple(lepton_sharpened_invariant(channel) for channel in (2, 3, 4)) == (Fraction(2, 969), Fraction(3, 1454), Fraction(4, 1939))),
        Witness("colour-identity", "The unique retained sharpening channel equals the independently forced generator.", generator_period_three() == 3 and lepton_sharpened_invariant(generator_period_three()) == Fraction(3, 1454)),
    ),
)


__all__ = (
    "CHARGED_LEPTON_CUBIC_CLAIM_ID",
    "CHARGED_LEPTON_CUBIC_SPEC",
    "charged_lepton_invariants",
    "lepton_sharpened_invariant",
)
