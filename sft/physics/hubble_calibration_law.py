"""Same-strength V3 reconstruction of the prior Hubble calibration law.

The V1/V2 result is a registered observation and therefore motivates this
question.  It is not an executable premise.  All proof quantities below are
exact positive counts or parts generated from admitted V3 structures.
"""

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


HUBBLE_CALIBRATION_CLAIM_ID = "SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001"


def hubble_calibration_structure() -> dict[str, object]:
    """Return the complete leading and first-recursive exact construction."""

    binary = binary_count()
    generator = generator_period_three()
    matter_share = Fraction(1, generator)
    vacuum_share = Fraction(binary, generator)
    covering_tower = positive_power(binary, generator)
    leading_correction = vacuum_share / covering_tower
    leading_ratio = Fraction(1, 1) + leading_correction

    deep_depth = fine_structure_blocks()["up"]
    orbit_floor = positive_predecessor(positive_power(binary, deep_depth))
    orbit_trace = first_return_trace(Fraction(1, orbit_floor))
    refined_correction = (vacuum_share + Fraction(1, orbit_floor)) / covering_tower
    refined_ratio = Fraction(1, 1) + refined_correction
    return {
        "matter_share": matter_share,
        "vacuum_share": vacuum_share,
        "covering_tower": covering_tower,
        "leading_correction": leading_correction,
        "leading_ratio": leading_ratio,
        "deep_depth": deep_depth,
        "orbit_floor": orbit_floor,
        "orbit_trace": orbit_trace,
        "refined_correction": refined_correction,
        "refined_ratio": refined_ratio,
    }


HUBBLE_CALIBRATION_SPEC = StructuralPhysicsSpec(
    claim_id=HUBBLE_CALIBRATION_CLAIM_ID,
    title="Fold calibration ratio between early and late expansion routes",
    statement=(
        "One retained formed class and the complete two-fibre open complement partition the generator-three "
        "cosmic carrier into exact matter and vacuum shares 1/3 and 2/3. Distributing the open share over the "
        "depth-three Fold support eight forces correction 1/12 and late/early calibration ratio 13/12. The "
        "independently forced depth-seven first-return floor 127 supplies the unique registered first-recursive "
        "deepening, giving exact ratio 3305/3048."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of cosmic carrier, occupancy distinction, partition, calibration "
        "support, leading correction, deep cover, recurrence floor, recursive correction, target custody, "
        "provenance and extension forms."
    ),
    grammar_boundary=(
        "All exact leading and one-native-recurrence calibration ratios formed from the complete One, the "
        "Fold fibres, generator three, depth-three support and the independently forced depth-seven orbit."
    ),
    axes=(
        binary_axis("carrier", "What carries the cosmic partition?", "independent-density-scalars", "Independent scalars do not close one conserved whole.", "one-complete-cosmic-carrier", "Every retained sector is a part of one complete carrier."),
        binary_axis("occupancy", "Which structural distinction separates the parts?", "named-matter-and-vacuum", "Names do not force multiplicity or orientation.", "one-formed-class-and-two-fibre-open-complement", "The One supplies one retained formed class while the complete Fold supplies its two distinguishable open fibres."),
        binary_axis("partition", "Which exact shares follow?", "selected-or-reversed-shares", "Selection or reversal loses the formed/open orientation.", "one-third-formed-two-thirds-open", "The oriented generator-three carrier contains the One formed class and both open Fold fibres exactly once."),
        binary_axis("support", "Across what support is the open calibration distributed?", "free-calibration-scale", "A free scale is a fitted parameter.", "complete-depth-three-Fold-support", "The generator-three depth has exactly two-cubed complete word support."),
        binary_axis("leading", "What leading correction is admitted?", "measured-ratio-correction", "A measured correction would select the answer.", "open-share-over-complete-support", "Two-thirds divided over eight forces one-twelfth and therefore thirteen-twelfths."),
        binary_axis("depth", "Which deeper recurrence may refine it?", "selected-cosmological-depth", "A selected depth is a parameter.", "independently-forced-up-cover-depth", "The admitted cover construction fixes the deeper positive depth at seven before cosmological comparison."),
        binary_axis("orbit", "Which recurrence record belongs to that depth?", "arbitrary-denominator", "An arbitrary denominator fits a correction.", "depth-seven-first-return-floor", "The positive predecessor of complete depth-seven support is 127 and its unit part first-returns in seven Folds."),
        binary_axis("deepening", "How is one recurrence retained?", "selected-sign-or-extra-term", "A sign choice or external term is not forced.", "one-positive-orbit-part-inside-open-share", "Exactly one positive 1/127 recurrence part deepens the open share before the same support distribution."),
        binary_axis("target", "May Hubble measurements select a form?", "hubble-values-readable-before-seal", "That is fitting.", "both-routes-inaccessible-until-seal", "Both exact ratios and all alternatives seal before external rows open."),
        binary_axis("provenance", "How is the known V1/V2 result classified?", "mislabel-as-unobserved-discovery", "The prior result was already observed.", "observational-reconstruction-with-independent-runtime", "The prior record defines the obligation while no prior answer or measurement enters execution."),
        binary_axis("extension", "May another calibration parameter enter?", "extra-calibration-rule", "An added rule is a free parameter.", "no-extra-rule", "The registered leading and one-native-recurrence grammar is exhausted."),
    ),
    exact_result=(
        "The exact matter/vacuum shares are 1/3 and 2/3; the leading correction and late/early ratio are "
        "1/12 and 13/12; the unique registered depth-seven recurrence refinement is 3305/3048."
    ),
    induction_base=(
        "One formed class plus both Fold-fibre open classes exhaust the generator-three carrier, and complete "
        "depth-three support distributes its open share over eight words."
    ),
    induction_step=(
        "The independently fixed depth-seven unit part returns only after seven Folds; retaining exactly its "
        "first positive recurrence part inside the open share yields the sole first-recursive registered form."
    ),
    exclusions=(
        "no V1/V2 answer artifact or Hubble measurement in executable forcing",
        "no numerical zero, negative, irrational, imaginary or floating proof value",
        "no fitted density, selected tolerance, calibration scale, depth, sign or extra term",
        "no claim that either external measurement route is itself an SFT premise",
        "no claim that the observational reconstruction was an unobserved blind discovery",
    ),
    witnesses=(
        Witness("complete-partition", "The exact formed and open shares close to the One.", hubble_calibration_structure()["matter_share"] + hubble_calibration_structure()["vacuum_share"] == Fraction(1, 1)),
        Witness("leading-ratio", "The complete leading construction is exactly thirteen-twelfths.", hubble_calibration_structure()["leading_correction"] == Fraction(1, 12) and hubble_calibration_structure()["leading_ratio"] == Fraction(13, 12)),
        Witness("depth-seven-orbit", "The unit part over 127 has exact first-return period seven.", len(hubble_calibration_structure()["orbit_trace"]) == 7),
        Witness("refined-ratio", "The one-recurrence deepening is exactly 3305/3048.", hubble_calibration_structure()["refined_ratio"] == Fraction(3305, 3048)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


HUBBLE_CALIBRATION_SPEC.validate()


__all__ = (
    "HUBBLE_CALIBRATION_CLAIM_ID",
    "HUBBLE_CALIBRATION_SPEC",
    "hubble_calibration_structure",
)
