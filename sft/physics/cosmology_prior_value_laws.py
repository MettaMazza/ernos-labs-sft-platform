"""Clean-room reconstruction of prior cosmological value obligations."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, fine_structure_blocks, positive_power
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    first_return_trace,
    generator_period_three,
    positive_predecessor,
)


DARK_BARYON_CLAIM_ID = "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001"


def dark_baryon_structure() -> dict[str, object]:
    colour = generator_period_three()
    volume = positive_power(colour, colour)
    depth = fine_structure_blocks()["down"]
    tower = positive_power(binary_count(), depth)
    orbit_floor = positive_predecessor(tower)
    leading = Fraction(volume, depth)
    refined = Fraction(volume, 1) / (Fraction(depth, 1) + Fraction(1, orbit_floor))
    return {
        "volume": volume,
        "depth": depth,
        "tower": tower,
        "baryon_share": Fraction(depth, tower),
        "dark_share": Fraction(volume, tower),
        "leading_ratio": leading,
        "orbit_floor": orbit_floor,
        "orbit_trace": first_return_trace(Fraction(1, orbit_floor)),
        "refined_ratio": refined,
    }


DARK_BARYON_SPEC = StructuralPhysicsSpec(
    claim_id=DARK_BARYON_CLAIM_ID,
    title="Generation-cover dark-to-baryon fraction",
    statement=(
        "Generator three over the forced three-space supplies volume 27. Its least complete binary cover "
        "has depth five and support 32, forcing leading baryon/dark shares 5/32 and 27/32 and ratio 27/5. "
        "The unique period-five orbit floor 31 deepens the same depth once, forcing 279/52."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of generation carrier, spatial volume, cover, partition, leading "
        "ratio, recurrence floor, deepening, measurement boundary, provenance and extension forms."
    ),
    grammar_boundary=(
        "All exact first-recursive dark/baryon partitions generated from the admitted generator-three "
        "spatial volume, its least binary cover and the first-return orbit native to that cover depth."
    ),
    axes=(
        binary_axis("carrier", "What carries the matter distinction?", "named-dark-and-baryon-scalars", "Names do not construct a common conserved support.", "one-complete-matter-cover", "One cover retains both complementary matter sectors."),
        binary_axis("volume", "What fixes the unconfined sector volume?", "selected-cosmological-volume", "A selected volume reads the target.", "generator-over-forced-space", "Generator three over three forced spatial directions yields exactly 3^3."),
        binary_axis("cover", "What fixes the confined anchor?", "free-cover-depth", "A free depth is a fitted parameter.", "least-complete-binary-cover", "The least binary support covering 27 is depth five, cross-locked by two plus three."),
        binary_axis("partition", "How are leading shares formed?", "independent-normalizations", "Separate denominators need not conserve one matter whole.", "depth-and-volume-over-cover", "Depth five and volume 27 partition the complete support 32 exactly once."),
        binary_axis("leading", "Which leading ratio follows?", "measured-ratio-insertion", "A measured ratio is not a derivation.", "volume-over-depth", "Common support cancellation forces 27/5."),
        binary_axis("orbit", "What supplies the next depth resolution?", "tower-or-up-depth-floor", "The tower is pre-periodic and the up-depth belongs to another carrier.", "own-depth-first-return-floor", "The positive predecessor 31 is the unique denominator with first-return period five."),
        binary_axis("deepening", "How is the recurrence retained?", "selected-sign-or-bare-depth", "A chosen orientation or bare repeat adds no forced recurrence record.", "one-positive-orbit-part-appended", "One positive 1/31 recurrence part is appended to its own depth, forcing 279/52."),
        binary_axis("target", "May cosmological densities select a form?", "density-readable-construction", "That would fit the ratio.", "densities-inaccessible-until-seal", "Both exact ratios and all candidates seal first."),
        binary_axis("provenance", "How is the prior result handled?", "old-answer-runtime-input", "Earlier answer artifacts cannot select the V3 law.", "prior-question-machine-independent-reconstruction", "The prior statement defines the obligation but no old answer enters execution."),
        binary_axis("extension", "May another cosmological term enter?", "extra-density-or-fit-term", "An added term is a free parameter.", "no-extra-rule", "Volume, cover and native orbit exhaust the first-recursive grammar."),
    ),
    exact_result=(
        "The leading dark-to-baryon ratio is 27/5 with shares 27/32 and 5/32; the unique native "
        "period-five deepening is exactly 279/52."
    ),
    induction_base="Volume 27 and least cover depth five partition complete binary support 32.",
    induction_step="The first-return orbit of the cover's positive predecessor appends exactly one retained 1/31 part to depth five; every other registered floor or orientation fails the carrier role.",
    exclusions=(
        "no V1/V2 answer artifact or cosmological density in the executable derivation",
        "no numerical zero, negative, irrational, imaginary or floating proof value",
        "no fitted density, tolerance, selected floor or additional cosmological parameter",
        "no assertion that an external cosmological model is an SFT premise",
    ),
    witnesses=(
        Witness("complete-partition", "The forced depth and volume shares sum exactly to the One.", dark_baryon_structure()["baryon_share"] + dark_baryon_structure()["dark_share"] == Fraction(1, 1)),
        Witness("native-orbit", "The unit part over 31 has exact first-return period five.", len(dark_baryon_structure()["orbit_trace"]) == 5),
        Witness("exact-ratios", "Both leading and first-recursive ratios reconstruct exactly.", dark_baryon_structure()["leading_ratio"] == Fraction(27, 5) and dark_baryon_structure()["refined_ratio"] == Fraction(279, 52)),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


DARK_BARYON_SPEC.validate()


__all__ = ("DARK_BARYON_CLAIM_ID", "DARK_BARYON_SPEC", "dark_baryon_structure")
