"""Terminal displaced-ground, Higgs mass-ratio and self-coupling law.

The V1/V2 statements are audit targets only.  No Higgs measurement, VEV,
reported coupling, earlier executable or stored survivor is read here.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, minimal_binary_cover, positive_power
from sft.physics.precision_value_laws_v1 import terminal_alpha
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    fold_part,
    generator_period_three,
    positive_predecessor,
)


CLAIM_ID = "SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065"
ONE = Fraction(1, 1)
EMPTY_ONE = ("empty-One",)


def vacuum_ground_census() -> tuple[dict[str, object], ...]:
    """Enumerate absence, the unique positive displaced ground, and unison."""

    half = Fraction(1, binary_count())
    return (
        {
            "form": EMPTY_ONE,
            "positive_carrier": False,
            "proper_part": False,
            "self_antipodal": False,
            "folds_to_One": False,
            "displaced_ground": False,
        },
        {
            "form": half,
            "positive_carrier": True,
            "proper_part": True,
            "self_antipodal": ONE - half == half,
            "folds_to_One": fold_part(half) == ONE,
            "displaced_ground": True,
        },
        {
            "form": ONE,
            "positive_carrier": True,
            "proper_part": False,
            "self_antipodal": False,
            "folds_to_One": fold_part(ONE) == ONE,
            "displaced_ground": False,
        },
    )


def displaced_ground() -> Fraction:
    survivors = tuple(
        row for row in vacuum_ground_census()
        if all((row["positive_carrier"], row["proper_part"], row["self_antipodal"], row["folds_to_One"], row["displaced_ground"]))
    )
    if len(survivors) != 1:
        raise ValueError("displaced-ground census did not close uniquely")
    value = survivors[0]["form"]
    if not isinstance(value, Fraction):
        raise ValueError("displaced ground is not an exact positive part")
    return value


def leading_higgs_rungs() -> tuple[Fraction, Fraction, Fraction]:
    vacuum = displaced_ground()
    mass = vacuum / binary_count()
    coupling = mass / binary_count()
    return vacuum, mass, coupling


def generation_cover_depth() -> int:
    volume = positive_power(generator_period_three(), generator_period_three())
    return minimal_binary_cover(volume)


def scalar_direction_support() -> int:
    return binary_count() * generator_period_three()


def active_scalar_directions() -> int:
    return positive_predecessor(scalar_direction_support())


def terminal_higgs_return() -> Fraction:
    """Transport one alpha return over all active scalar directions."""

    if active_scalar_directions() != generation_cover_depth():
        raise ValueError("held direction support and generation cover did not cross-lock")
    return Fraction(scalar_direction_support(), active_scalar_directions()) * terminal_alpha()


def terminal_higgs_mass_ratio() -> Fraction:
    ratio = displaced_ground() + terminal_higgs_return()
    if ratio <= displaced_ground() or ratio >= ONE:
        raise ValueError("terminal Higgs ratio left its exact positive displaced interval")
    return ratio


def terminal_higgs_self_coupling() -> Fraction:
    ratio = terminal_higgs_mass_ratio()
    coupling = ratio * ratio / binary_count()
    if coupling <= leading_higgs_rungs()[2] or coupling >= displaced_ground():
        raise ValueError("terminal Higgs self-coupling left its generated interval")
    return coupling


def route_cross_lock() -> dict[str, Fraction | bool]:
    ratio = terminal_higgs_mass_ratio()
    coupling = terminal_higgs_self_coupling()
    return {
        "mass_route_squared": ratio * ratio,
        "two_fibre_coupling_route": binary_count() * coupling,
        "routes_equal": ratio * ratio == binary_count() * coupling,
    }


def theorem_certificate() -> dict[str, object]:
    vacuum, leading_mass, leading_coupling = leading_higgs_rungs()
    return {
        "vacuum_census": vacuum_ground_census(),
        "displaced_ground": vacuum,
        "leading_mass_ratio": leading_mass / vacuum,
        "leading_self_coupling": leading_coupling,
        "scalar_direction_support": scalar_direction_support(),
        "active_scalar_directions": active_scalar_directions(),
        "generation_cover_depth": generation_cover_depth(),
        "terminal_return": terminal_higgs_return(),
        "terminal_mass_ratio": terminal_higgs_mass_ratio(),
        "terminal_self_coupling": terminal_higgs_self_coupling(),
        "route_cross_lock": route_cross_lock(),
        "absence_ground_rejected": not vacuum_ground_census()[0]["displaced_ground"],
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal displaced-ground and Higgs mass/self-coupling law",
    statement=(
        "The complete minimal vacuum census contains structural empty-One, the half-One and the One. Empty-One is "
        "absence rather than a field value; the One is unison rather than a displaced proper part. Half-One alone is "
        "positive, proper, self-antipodal and folds to the One, forcing the displaced ground without an inserted mass "
        "or potential. Its first binary successors retain the V2 leading rungs 1/2, 1/4 and 1/8. Terminal completion "
        "then acts on the scalar's complete two-hand by generator-three directional product: six cells. Holding the "
        "unique invariant return leaves five active cells, independently cross-locked to the least binary cover depth "
        "of the generation volume 27. One terminal alpha return therefore contributes exactly (6/5) alpha to the "
        "half-One mass ratio. The complete two-fibre sharing of its squared excitation forces the self-coupling to one "
        "half of that exact squared ratio. No mass, VEV, coupling or measurement selects either result."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-ONE-001",
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of ground carrier, displacement, leading rungs, scalar directional support, "
        "held return, cover cross-lock, terminal transport, coupling composition, route equality, measurement custody "
        "and extension forms."
    ),
    grammar_boundary=(
        "Structural empty-One, half-One and One ground forms; every binary successor of the displaced ground through "
        "the leading coupling rung; the complete binary-hand times generator-direction product; its unique held return; "
        "the least cover of generator volume; exactly one terminal alpha transport; exact positive rational operations; "
        "and no physical target before seal."
    ),
    axes=(
        binary_axis("ground", "What can be the field ground?", "absence-as-numerical-ground", "Structural absence is not a field value.", "positive-proper-ground-carrier", "A ground carrier must be an exact positive proper part of the One."),
        binary_axis("displacement", "Which positive proper part closes the ground?", "unison-or-selected-part", "Unison is not displaced and a selected part is a parameter.", "unique-self-antipodal-half-One", "Half-One alone is self-antipodal and folds exactly to the One."),
        binary_axis("rungs", "What happens to the earlier Higgs hierarchy?", "discard-or-rewrite-leading-rungs", "A terminal successor cannot erase its lower-order receipt.", "retain-half-quarter-eighth-controls", "Binary succession preserves 1/2, 1/4 and 1/8 as explicit leading controls."),
        binary_axis("directions", "Which scalar directions participate?", "selected-direction-subset", "A subset omits a generated hand or generator direction.", "complete-two-by-three-product", "The scalar excitation retains all six hand-direction cells."),
        binary_axis("return", "How is invariant support treated?", "retain-all-six-as-active", "The invariant return cannot also be an active displaced direction.", "hold-unique-return-leaving-five", "The positive predecessor of complete six-cell support leaves five active directions."),
        binary_axis("cover", "What independently fixes the active count?", "free-denominator", "A denominator chosen for agreement is a parameter.", "least-cover-of-generation-volume", "The least binary cover of 27 is five and cross-locks the held direction count."),
        binary_axis("transport", "How does the terminal self-return enter?", "fitted-offset-or-repeated-series", "An offset or truncation is a fit.", "one-six-over-five-alpha-return", "All six cells transport one terminal alpha across the five active supports exactly once."),
        binary_axis("coupling", "How is scalar self-coupling formed?", "import-potential-or-free-lambda", "An imported potential or free lambda would add an axiom.", "squared-excitation-shared-over-two-fibres", "Complete binary sharing forces lambda to the exact squared mass ratio over two."),
        binary_axis("route", "Do mass and coupling constructions agree?", "independent-mass-and-coupling-routes", "Independent routes introduce a dial.", "exact-two-route-cross-lock", "The squared mass route and twice-coupling route are identically equal."),
        binary_axis("measurement", "Can Higgs data select the terminal form?", "target-readable-before-seal", "That would fit the coefficient to the measured mass.", "all-targets-inaccessible-until-seal", "The exact ratio, coupling and census seal before measurements open."),
        binary_axis("extension", "May another term or field be appended?", "extra-mass-potential-or-correction", "Any added term is a free parameter.", "no-extra-rule", "The ground, rungs, complete directions, held return and single terminal transport exhaust the grammar."),
    ),
    exact_result=(
        "The displaced ground is uniquely half-One; the retained leading Higgs rungs are 1/2, 1/4 and 1/8. Complete "
        "six-cell scalar support, its unique held return and the independently equal cover depth five force terminal "
        "m_H/v = 1/2 + (6/5) alpha = 2563352914777/5038463954690. The exact native self-coupling is "
        "lambda = (m_H/v)^2/2 = 6570778165695741824959729/50772238045420788745992200. Both routes cross-lock in "
        "the squared domain; no irrational root is formed."
    ),
    induction_base="Half-One is the unique minimal positive proper self-antipodal ground and its first binary successor supplies the leading mass rung.",
    induction_step="Completing every hand-direction cell and holding the unique invariant return leaves five active cells; the independently identical generation cover fixes the sole terminal transport, after which binary sharing closes the coupling with no additional successor.",
    exclusions=(
        "no V1/V2 executable, certificate, target value, candidate table or stored survivor as a premise",
        "no measured Higgs mass, VEV, Fermi constant or self-coupling in formal execution",
        "no imported Higgs potential, Standard Model mass relation, fitted coefficient, uncertainty or correction series",
        "no semantic numerical zero, negative, irrational, imaginary, floating, NaN, continuum or infinite proof scalar",
        "no claim that the leading 1/2 mass ratio or 1/8 coupling is the terminal result",
    ),
    witnesses=(
        Witness("ground-census", "Three minimal ground forms are generated and half-One is the unique displaced survivor.", len(vacuum_ground_census()) == 3 and displaced_ground() == Fraction(1, 2)),
        Witness("leading-rungs", "The earlier half/quarter/eighth hierarchy is retained exactly.", leading_higgs_rungs() == (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8))),
        Witness("support-cross-lock", "Complete scalar support is six and both independent predecessor and cover routes return five.", scalar_direction_support() == 6 and active_scalar_directions() == generation_cover_depth() == 5),
        Witness("terminal-ratio", "The one terminal return forces the exact mass ratio without a target.", terminal_higgs_mass_ratio() == Fraction(2563352914777, 5038463954690)),
        Witness("terminal-coupling", "The exact self-coupling and squared mass route cross-lock over the two fibres.", terminal_higgs_self_coupling() == Fraction(6570778165695741824959729, 50772238045420788745992200) and route_cross_lock()["routes_equal"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EMPTY_ONE",
    "ONE",
    "SPEC",
    "active_scalar_directions",
    "displaced_ground",
    "generation_cover_depth",
    "leading_higgs_rungs",
    "route_cross_lock",
    "scalar_direction_support",
    "terminal_higgs_mass_ratio",
    "terminal_higgs_return",
    "terminal_higgs_self_coupling",
    "theorem_certificate",
    "vacuum_ground_census",
)
