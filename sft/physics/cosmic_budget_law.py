"""Refined V3 reconstruction of the complete present cosmic budget."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, fine_structure_blocks, positive_power
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


COSMIC_BUDGET_CLAIM_ID = "SFT-PHYS-COSMO-COMPLETE-BUDGET-001"


def cosmic_budget_structure() -> dict[str, Fraction | int]:
    binary = binary_count()
    generator = generator_period_three()
    depth = fine_structure_blocks()["down"]
    support = positive_power(binary, depth)
    pinned = binary * depth
    free = support - pinned
    matter = Fraction(pinned, support)
    vacuum = Fraction(free, support)
    baryon_within_matter = Fraction(depth, support)
    dark_within_matter = Fraction(generator ** generator, support)
    baryon = matter * baryon_within_matter
    cold_dark = matter * dark_within_matter
    return {
        "depth": depth,
        "support": support,
        "pinned": pinned,
        "free": free,
        "matter": matter,
        "vacuum": vacuum,
        "baryon_within_matter": baryon_within_matter,
        "dark_within_matter": dark_within_matter,
        "baryon": baryon,
        "cold_dark": cold_dark,
    }


COSMIC_BUDGET_SPEC = StructuralPhysicsSpec(
    claim_id=COSMIC_BUDGET_CLAIM_ID,
    title="Depth-five Fold cosmic energy budget",
    statement=(
        "The least binary support covering the generator-three spatial volume has depth five and 32 states. "
        "The complete Fold boundary pair pins two states at each depth, forcing ten pinned matter states and "
        "twenty-two free vacuum states: matter 5/16 and vacuum 11/16. The independently reconstructed "
        "five-to-twenty-seven matter partition then forces baryon 25/512 and cold dark 135/512."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
        "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of support, boundary incidence, pinning, free complement, global "
        "partition, internal matter partition, composition, closure, target custody, provenance and extension forms."
    ),
    grammar_boundary=(
        "All exact present-budget partitions formed from the least depth-five binary cover, one complete "
        "boundary pair per depth and the independently admitted five-to-twenty-seven matter partition."
    ),
    axes=(
        binary_axis("support", "What carries the budget?", "selected-density-denominator", "A selected denominator fits observations.", "least-generator-volume-binary-cover", "The least complete binary cover of generator volume 27 fixes depth five and support 32."),
        binary_axis("boundary", "What is retained at each cover depth?", "free-pinned-count", "A free count is a parameter.", "complete-two-state-boundary-pair", "Boundary rank two supplies exactly one retained pair per depth."),
        binary_axis("pinning", "Which states form the matter carrier?", "named-matter-share", "A name does not construct a share.", "all-depth-boundary-pairs", "Two pinned states at each of five depths force ten matter states."),
        binary_axis("free", "Which states form the vacuum carrier?", "selected-vacuum-share", "A selected share reads the target.", "complete-unpinned-complement", "The remaining twenty-two states are the complete free complement within support 32."),
        binary_axis("global", "Which exact global shares follow?", "leading-one-third-two-thirds-only", "The earlier leading partition ignores the admitted depth-five boundary discriminator.", "five-sixteenths-and-eleven-sixteenths", "Ten and twenty-two over 32 reduce exactly to 5/16 and 11/16."),
        binary_axis("internal", "How is matter partitioned?", "new-baryon-dark-parameter", "A new ratio is free.", "admitted-five-to-twenty-seven-partition", "The upstream law fixes baryon/dark shares 5/32 and 27/32 within matter."),
        binary_axis("composition", "How are absolute component shares formed?", "independent-component-normalizations", "Independent denominators need not close.", "global-matter-times-internal-shares", "Multiplying the global matter share by both complete internal shares forces 25/512 and 135/512."),
        binary_axis("closure", "Does the full budget exhaust the One?", "separate-rounded-total", "Rounded values cannot prove closure.", "exact-four-part-One-closure", "Vacuum plus baryon plus cold dark is exactly the One, with baryon plus cold dark exactly matter."),
        binary_axis("target", "May Planck values select the budget?", "planck-budget-readable-before-seal", "That would fit four targets.", "all-planck-rows-inaccessible-until-seal", "Every exact component and alternative seals before any external row opens."),
        binary_axis("provenance", "How is the later V2 refinement handled?", "erase-leading-law-or-mislabel-discovery", "The leading law and later observed refinement must both remain visible.", "disclosed-successor-observational-reconstruction", "The earlier leading law is preserved while the later structural discriminator is independently rebuilt."),
        binary_axis("extension", "May another density parameter enter?", "extra-budget-rule", "An added rule is a free parameter.", "no-extra-rule", "Cover, boundary and admitted internal partition exhaust the registered present-budget grammar."),
    ),
    exact_result=(
        "The refined present budget is vacuum 11/16, total matter 5/16, baryon 25/512 and cold dark "
        "135/512; baryon plus cold dark equals matter and vacuum plus matter equals the One."
    ),
    induction_base="The depth-five support contains 32 states and one complete boundary pair is pinned at the first depth.",
    induction_step="Each positive depth successor appends exactly one boundary pair; after all five forced depths, ten states are pinned and the exhaustive complement contains twenty-two, while internal matter composition preserves both global closures.",
    exclusions=(
        "no Planck value or V1/V2 answer artifact in executable forcing",
        "no numerical zero, negative, irrational, imaginary or floating proof value",
        "no fitted density, selected tolerance, free pinned count or extra component rule",
        "no erasure of the earlier 1/3 and 2/3 leading approximation",
        "no claim that the external base-Lambda-CDM parameter analysis is an SFT premise",
    ),
    witnesses=(
        Witness("forced-support", "Depth five has 32 complete states, ten pinned and twenty-two free.", cosmic_budget_structure()["support"] == 32 and cosmic_budget_structure()["pinned"] == 10 and cosmic_budget_structure()["free"] == 22),
        Witness("global-closure", "Matter and vacuum close exactly to the One.", cosmic_budget_structure()["matter"] + cosmic_budget_structure()["vacuum"] == Fraction(1, 1)),
        Witness("matter-closure", "Baryon and cold-dark shares close exactly to total matter.", cosmic_budget_structure()["baryon"] + cosmic_budget_structure()["cold_dark"] == cosmic_budget_structure()["matter"]),
        Witness("exact-components", "All four refined component values are exact.", cosmic_budget_structure()["vacuum"] == Fraction(11, 16) and cosmic_budget_structure()["matter"] == Fraction(5, 16) and cosmic_budget_structure()["baryon"] == Fraction(25, 512) and cosmic_budget_structure()["cold_dark"] == Fraction(135, 512)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


COSMIC_BUDGET_SPEC.validate()


__all__ = ("COSMIC_BUDGET_CLAIM_ID", "COSMIC_BUDGET_SPEC", "cosmic_budget_structure")
