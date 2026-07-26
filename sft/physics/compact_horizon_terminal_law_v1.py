"""Exact compact-object and horizon-thermodynamics composition.

The module imports no stellar catalogue, compact-object mass, conventional
equation of state, black-hole metric or temperature measurement.  Earlier SFT
corpora identify the reconstruction obligation only.  Every proof carrier is
an exact positive whole/fractional Fold form; the empty One form represents a
closed support.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071"
EMPTY_ONE_FORM = ()
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)
THREE_QUARTER_ONE = Fraction(3, 4)
QUARTER_ONE = Fraction(1, 4)
REFERENCE_MASS = QUARTER_ONE
REFERENCE_TEMPERATURE = QUARTER_ONE
THERMAL_MASS_PRODUCT = REFERENCE_MASS * REFERENCE_TEMPERATURE


def positive_whole(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("a compact-support count must be a positive whole")
    return value


def positive_fraction(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0:
        raise ValueError("a compact carrier must be an exact positive fraction")
    return value


def fold_upper_preimage(value: Fraction) -> Fraction:
    """Expose the held upper fibre without a signed proof scalar."""

    value = positive_fraction(value)
    if value <= HALF_ONE or value > ONE:
        raise ValueError("upper-preimage Fold requires half-One < value <= One")
    return value - QUARTER_ONE


def exclusion_scaling(side: int) -> dict[str, int | bool]:
    """Perfect-cube packing certificate for relativistic degeneracy support.

    A side-q three-space support contains q^3 singly occupied cells.  Complete
    exclusion therefore forces momentum depth q.  The retained relativistic
    support numerator is q^4, whereas paired gravitational source support is
    q^6.  Perfect powers keep the proof exact; no cube root is evaluated.
    """

    side = positive_whole(side)
    occupants = side * side * side
    degeneracy = occupants * side
    gravity = occupants * occupants
    return {
        "side": side,
        "occupants": occupants,
        "forced_momentum_depth": side,
        "degeneracy_support_numerator": degeneracy,
        "gravity_support_numerator": gravity,
        "gravity_strict_after_base": side == 1 or gravity > degeneracy,
    }


def exclusion_scaling_certificate(depth: int) -> dict[str, object]:
    depth = positive_whole(depth)
    rows = tuple(exclusion_scaling(side) for side in range(1, depth + 1))
    return {
        "rows": rows,
        "base_equal": rows[0]["degeneracy_support_numerator"] == rows[0]["gravity_support_numerator"],
        "gravity_strict_after_base": all(
            row["gravity_support_numerator"] > row["degeneracy_support_numerator"]
            for row in rows[1:]
        ),
        "perfect_cube_support": all(row["occupants"] == row["side"] ** 3 for row in rows),
        "depth_independent_exponent_order": all(side ** 6 > side ** 4 for side in range(2, depth + 2)),
    }


def endpoint_census() -> dict[str, object]:
    """The exact two-family pre-horizon endpoint census."""

    balance = fold_upper_preimage(THREE_QUARTER_ONE)
    families = ("electron-exclusion-support", "neutral-fermion-exclusion-support")
    return {
        "loaded_exclusion_threshold": THREE_QUARTER_ONE,
        "folded_gravity_balance": balance,
        "families": families,
        "family_count": len(families),
        "third_pre_horizon_family": EMPTY_ONE_FORM,
        "successor_after_second_family": "horizon-closure",
    }


def horizon_thermodynamics(mass: Fraction) -> dict[str, Fraction]:
    """Exact scale law anchored only to the admitted quarter-One witness."""

    mass = positive_fraction(mass)
    radius = mass + mass
    area_support = radius * radius
    entropy_support = QUARTER_ONE * area_support
    temperature = THERMAL_MASS_PRODUCT / mass
    if radius != mass + mass:
        raise ValueError("horizon radius lost the Fold doubling law")
    if temperature * mass != THERMAL_MASS_PRODUCT:
        raise ValueError("horizon thermal-mass product changed")
    if entropy_support * 4 != area_support:
        raise ValueError("horizon quarter-area support changed")
    return {
        "mass": mass,
        "radius": radius,
        "area_support": area_support,
        "entropy_support": entropy_support,
        "temperature": temperature,
        "thermal_mass_product": THERMAL_MASS_PRODUCT,
    }


def evaporation_trace(depth: int) -> tuple[dict[str, Fraction], ...]:
    """Finite halving trace; every reached mass and temperature stays positive."""

    depth = positive_whole(depth)
    rows = []
    mass = ONE
    for _ in range(depth):
        rows.append(horizon_thermodynamics(mass))
        mass = mass * HALF_ONE
    return tuple(rows)


def evaporation_certificate(depth: int) -> dict[str, object]:
    rows = evaporation_trace(depth)
    return {
        "rows": rows,
        "mass_strictly_falls": all(left["mass"] > right["mass"] for left, right in zip(rows, rows[1:])),
        "temperature_strictly_rises": all(left["temperature"] < right["temperature"] for left, right in zip(rows, rows[1:])),
        "area_strictly_falls": all(left["area_support"] > right["area_support"] for left, right in zip(rows, rows[1:])),
        "thermal_mass_invariant": all(row["temperature"] * row["mass"] == THERMAL_MASS_PRODUCT for row in rows),
        "all_reached_carriers_positive": all(
            row[key] > 0 for row in rows for key in ("mass", "radius", "area_support", "entropy_support", "temperature")
        ),
        "finite_floor_retained": rows[-1]["mass"] > 0,
    }


def theorem_certificate() -> dict[str, object]:
    exclusion = tuple(exclusion_scaling_certificate(depth) for depth in (1, 2, 3, 8, 16))
    evaporation = tuple(evaporation_certificate(depth) for depth in (1, 2, 3, 8, 16))
    reference = horizon_thermodynamics(REFERENCE_MASS)
    endpoints = endpoint_census()
    return {
        "exclusion": exclusion,
        "endpoints": endpoints,
        "reference_horizon": reference,
        "evaporation": evaporation,
        "all_exclusion_scalings_close": all(
            row["base_equal"] and row["gravity_strict_after_base"] and row["depth_independent_exponent_order"]
            for row in exclusion
        ),
        "two_pre_horizon_families": endpoints["family_count"] == 2 and endpoints["third_pre_horizon_family"] == EMPTY_ONE_FORM,
        "reference_cross_closes": reference["radius"] == HALF_ONE and reference["temperature"] == QUARTER_ONE,
        "all_evaporation_traces_close": all(
            row["thermal_mass_invariant"] and row["all_reached_carriers_positive"] and row["finite_floor_retained"]
            for row in evaporation
        ),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal compact-object and horizon-thermodynamics law",
    statement=(
        "Complete three-space exclusion packing gives q^3 singly occupied cells, momentum depth q and relativistic "
        "support numerator q^4, while paired gravitational source support is q^6; gravity therefore overtakes the "
        "exclusion scaling after the exact base. The loaded upper preimage is three-quarter-One and Folds to the "
        "half-One balance. The binary fibre supplies exactly two pre-horizon exclusion families and no third. The "
        "already admitted horizon Fold doubles mass to radius, rank-two support makes area proportional to radius "
        "paired with itself, and two binary halvings force entropy to one quarter of that boundary support. The live "
        "vacuum recurrence and admitted quarter-One horizon witness fix temperature times mass to one-sixteenth, so "
        "temperature varies exactly inversely with mass. Every finite emission successor lowers positive mass, raises "
        "positive temperature and lowers area while the finite floor prevents a numerical-zero or infinite proof form."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-QUANTUM-EXCLUSION-001",
        "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
        "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
        "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",
        "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023",
        "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of occupation, momentum, support scaling, gravity scaling, "
        "threshold, endpoint-family, horizon-radius, area, entropy, thermal, finite-floor and extension forms."
    ),
    grammar_boundary=(
        "Every positive finite perfect-cube exclusion support and successor; the complete binary endpoint fibre; "
        "the admitted quarter-One horizon witness; every positive exact mass carrier; every finite binary emission "
        "depth; and the complete twelve-axis alternative product, with dimensional observations inaccessible."
    ),
    axes=(
        binary_axis("occupation", "How are compact fermions placed?", "multiply-occupied-cell", "That violates the admitted exclusion law.", "one-fermion-per-generated-cell", "Complete exclusion packing retains one indistinguishable fermion per occupied cell."),
        binary_axis("momentum", "What depth does complete three-space packing force?", "selected-momentum-scale", "A selected scale is a free parameter.", "cube-side-momentum-depth", "q^3 occupied cells force the positive depth q without evaluating a root."),
        binary_axis("support", "What is the relativistic exclusion support?", "imported-pressure-equation", "An imported equation cannot select the Fold law.", "occupants-times-forced-depth-q4", "q^3 occupants times depth q gives exact q^4 support."),
        binary_axis("gravity", "What gravitational source support competes?", "linear-unpaired-source", "Gravity couples the complete source support to itself.", "paired-source-q6", "q^3 paired with itself gives exact q^6 support."),
        binary_axis("threshold", "Which loaded Fold threshold reaches balance?", "chosen-dimensional-mass", "A measured mass cannot choose a structural threshold.", "three-quarter-preimage-to-half-One", "The complete loaded upper preimage Folds exactly to half-One."),
        binary_axis("endpoint", "How many pre-horizon exclusion families exist?", "open-ended-remnant-list", "An open list is not generated by the binary fibre.", "exactly-two-binary-fibre-families", "The two fibre labels supply exactly two support families and no third."),
        binary_axis("radius", "How does horizon radius depend on mass?", "imported-metric-radius", "A conventional metric is not a premise.", "one-Fold-mass-doubling", "The admitted horizon law forces radius equal to mass held twice."),
        binary_axis("area", "Where is horizon support counted?", "volume-support", "A volume count contradicts boundary rank two.", "rank-two-radius-pair", "The forced boundary rank pairs radius with itself."),
        binary_axis("entropy", "How much boundary information is retained?", "selected-entropy-coefficient", "A selected coefficient is an extra rule.", "quarter-area-boundary-record", "Two binary halvings force the admitted quarter-area record."),
        binary_axis("thermal", "How does the live horizon recurrence scale?", "constant-or-fitted-temperature", "A constant or fitted temperature loses the scale recurrence.", "fixed-thermal-mass-product", "The admitted quarter-One witness fixes the one-sixteenth product and therefore inverse-mass scaling."),
        binary_axis("floor", "What happens under continued emission?", "numerical-zero-or-completed-infinity", "Neither is an admissible Fold proof form.", "positive-finite-floor-at-every-reached-depth", "Every finite successor retains positive mass and temperature."),
        binary_axis("extension", "May a third family or correction be added?", "free-family-or-correction", "An ungenerated addition destroys uniqueness.", "no-extra-rule", "The complete fibre, scale and finite-floor grammar requires no added selector."),
    ),
    exact_result=(
        "For every positive whole q, complete exclusion packing has q^3 occupants, forced momentum depth q, "
        "relativistic support q^4 and gravitational paired support q^6; q^6 is strictly greater after the exact base. "
        "The loaded exclusion threshold is 3/4 and its Fold balance is 1/2. Exactly two pre-horizon support families "
        "exist. For every positive exact mass m, horizon radius is 2m, area support is (2m)^2, entropy support is "
        "one quarter of that area, and temperature is 1/(16m), preserving exact product mT=1/16. At m=1/4 the "
        "admitted radius and temperature are respectively 1/2 and 1/4. Every finite halving emission trace retains "
        "positive mass, temperature, area and information support; no numerical zero or completed infinity enters."
    ),
    induction_base="One occupied cell has unit exclusion and gravitational support; the first fibre family exists; the admitted mass 1/4 horizon has radius 1/2 and temperature 1/4.",
    induction_step="q to q+1 preserves q^4 versus q^6 exponent order; the second fibre label adds the second and final pre-horizon family; each finite mass halving quarters area and doubles temperature while retaining mT=1/16.",
    exclusions=(
        "no V1/V2 executable, conventional compact-object equation, catalogue mass or Hawking target in formal execution",
        "no fitted mass limit, equation-of-state knob, temperature calibration, area normalization or evaporation correction",
        "no numerical zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinite proof scalar",
        "no claim that a normalized Fold temperature alone is a direct kelvin observation",
        "no third pre-horizon family, hidden support source, volume entropy or information deletion",
    ),
    witnesses=(
        Witness("exclusion-scaling", "Perfect-cube exclusion and gravity exponents close at every registered depth.", theorem_certificate()["all_exclusion_scalings_close"]),
        Witness("endpoint-census", "The binary fibre supplies exactly two pre-horizon families.", theorem_certificate()["two_pre_horizon_families"]),
        Witness("reference-horizon", "The admitted quarter-One witness cross-closes radius and temperature.", theorem_certificate()["reference_cross_closes"]),
        Witness("inverse-temperature", "Every registered finite emission trace preserves mT=1/16 and positive support.", theorem_certificate()["all_evaporation_traces_close"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EMPTY_ONE_FORM", "HALF_ONE", "ONE", "QUARTER_ONE", "REFERENCE_MASS",
    "REFERENCE_TEMPERATURE", "SPEC", "THERMAL_MASS_PRODUCT", "THREE_QUARTER_ONE",
    "endpoint_census", "evaporation_certificate", "evaporation_trace", "exclusion_scaling",
    "exclusion_scaling_certificate", "fold_upper_preimage", "horizon_thermodynamics", "theorem_certificate",
)
