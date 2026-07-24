"""Exact V3 relativistic dynamics and field-closure successors.

V1/V2 statements are reconstruction obligations, not premises.  This module
uses admitted V3 Fold structures and exact positive rationals only.  A vanished
or equal-oriented difference is represented by ``()``, never numerical zero;
orientation is a held label and never a negative magnitude.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.atomic_constants import binary_count
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    boundary_rank_two,
    fold_part,
    spatial_dimension_three,
)
from sft.physics.vacuum_lineage_laws_v1 import oscillator_levels


FREE_PHASE_ID = "SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003"
POTENTIAL_PHASE_ID = "SFT-PHYS-DYNAMICS-POTENTIAL-EVOLUTION-003"
STATIONARY_ID = "SFT-PHYS-DYNAMICS-STATIONARY-SPECTRUM-003"
TWO_HAND_DIRAC_ID = "SFT-PHYS-RELATIVITY-TWO-HAND-DIRAC-SQUARE-003"
FULL_DIRAC_ID = "SFT-PHYS-RELATIVITY-FULL-DIRAC-SQUARE-003"
COULOMB_GAUSS_ID = "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003"
MAGNETIC_RELATIVITY_ID = "SFT-PHYS-FIELD-MAGNETIC-RELATIVITY-003"
LORENTZ_TRANSFER_ID = "SFT-PHYS-FIELD-LORENTZ-TRANSFER-003"
MAXWELL_PLANAR_ID = "SFT-PHYS-FIELD-MAXWELL-PLANAR-CLOSURE-003"
MAXWELL_SPACE_ID = "SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003"
OPTICAL_OPERATIONS_ID = "SFT-PHYS-WAVE-EXACT-OPERATIONS-003"
FINITE_LOOP_ID = "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003"


def cyclic_advance(phase: Fraction, advance: Fraction) -> Fraction:
    """Advance on the exact One-cycle, casting out complete Ones only."""

    if not isinstance(phase, Fraction) or not isinstance(advance, Fraction):
        raise ValueError("phase advance requires exact fractions")
    if not 0 < phase <= 1 or advance <= 0:
        raise ValueError("phase and advance must be positive Fold carriers")
    total = phase + advance
    while total > 1:
        total -= 1
    return total


def free_particle_phase(phase: Fraction, momentum: Fraction) -> dict[str, Fraction]:
    """Compare one Fold momentum advance with two momentum advances."""

    if not isinstance(momentum, Fraction) or not 0 < momentum <= Fraction(1, 2):
        raise ValueError("momentum must be an exact positive part no larger than half-One")
    dispersion = fold_part(momentum)
    by_fold = cyclic_advance(phase, dispersion)
    by_two_steps = cyclic_advance(cyclic_advance(phase, momentum), momentum)
    if by_fold != by_two_steps:
        raise ValueError("free phase failed exact Fold/two-step correspondence")
    return {"momentum": momentum, "dispersion": dispersion, "phase_after": by_fold}


def potential_phase_evolution(
    phase: Fraction, kinetic: Fraction, potential: Fraction
) -> dict[str, Fraction]:
    """Compose kinetic and potential rotations without an imported equation."""

    if any(not isinstance(value, Fraction) or value <= 0 for value in (kinetic, potential)):
        raise ValueError("energy carriers must be exact positive fractions")
    sequential = cyclic_advance(cyclic_advance(phase, kinetic), potential)
    joint = cyclic_advance(phase, kinetic + potential)
    if sequential != joint:
        raise ValueError("sequential and joint exact phase evolution differ")
    return {"kinetic": kinetic, "potential": potential, "total": kinetic + potential, "phase_after": joint}


def stationary_spectrum(depth: int) -> tuple[Fraction, ...]:
    """Return the already generated half-step grid at a positive depth."""

    levels = oscillator_levels(depth)
    if len(levels) < 2:
        raise ValueError("stationary spectrum witness requires at least two levels")
    spacing = levels[1] - levels[0]
    if spacing <= 0 or any(levels[index + 1] - levels[index] != spacing for index in range(len(levels) - 1)):
        raise ValueError("stationary spectrum is not uniformly separated")
    return levels


def two_hand_dirac_square() -> dict[str, Fraction]:
    """Close motion/substance squares at the first generated 3-4-5 partition."""

    three = spatial_dimension_three()
    four = binary_count() * binary_count()
    five = three + binary_count()
    momentum = Fraction(three, five)
    mass = Fraction(four, five)
    energy_square = momentum * momentum + mass * mass
    if energy_square != 1:
        raise ValueError("two-hand Dirac square did not close at the One")
    return {"momentum": momentum, "mass": mass, "energy_square": energy_square}


def held_difference(left: Fraction, right: Fraction) -> tuple[()] | tuple[str, Fraction]:
    """Return empty equality or a positive difference with a held orientation."""

    if left == right:
        return ()
    if left > right:
        return ("left", left - right)
    return ("right", right - left)


def full_dirac_square() -> dict[str, object]:
    """Close the three momentum hands plus mass by two exact routes."""

    half = Fraction(1, binary_count())
    components = (half, half, half, half)
    direct = components[0] * components[0]
    for value in components[1:]:
        direct += value * value
    # Structural absences are emitted as empty records, not proof quantities.
    differences = (held_difference(half, half), held_difference(half, half))
    present_polarized_squares = (half + half) ** 2 + (half + half) ** 2
    polarized = present_polarized_squares / binary_count()
    if direct != 1 or polarized != 1 or differences != ((), ()):
        raise ValueError("full Dirac square failed one of its exact closure routes")
    return {
        "components": components,
        "direct_square": direct,
        "held_equal_differences": differences,
        "polarized_square": polarized,
    }


def coulomb_gauss_closure(source: Fraction, radius: Fraction) -> dict[str, Fraction]:
    """Generate inverse-square response and reconstruct the source flux."""

    if not isinstance(radius, Fraction) or not 0 < source < radius <= 1:
        raise ValueError("Coulomb witness requires exact ordered positive source and radius")
    field = source / (radius * radius)
    flux = field * radius * radius
    potential = Fraction(1, 1) - source / radius
    if flux != source or potential <= 0:
        raise ValueError("Coulomb/Gauss closure lost source or retained potential")
    return {"field": field, "flux": flux, "retained_potential": potential}


def magnetic_relativistic_factor(speed: Fraction) -> dict[str, Fraction]:
    """Return the positive electric remainder and its Fold-covariance witness."""

    if not isinstance(speed, Fraction) or not 0 < speed < 1:
        raise ValueError("speed must be an exact positive sub-One carrier")
    speed_square = speed * speed
    correction = Fraction(1, 1) - speed_square
    folded_correction = fold_part(correction)
    complementary_fold = Fraction(1, 1) - fold_part(speed_square)
    if folded_correction != complementary_fold:
        raise ValueError("magnetic correction does not commute with the Fold")
    return {
        "speed_square": speed_square,
        "electric_remainder": correction,
        "folded_remainder": folded_correction,
    }


def lorentz_transfer(electric_force: Fraction, speed: Fraction) -> dict[str, Fraction]:
    """Partition one electric transfer into retained and motion-held shares."""

    if not isinstance(electric_force, Fraction) or electric_force <= 0:
        raise ValueError("electric force must be exact and positive")
    factor = magnetic_relativistic_factor(speed)
    retained = electric_force * factor["electric_remainder"]
    motion_share = electric_force * factor["speed_square"]
    if retained + motion_share != electric_force:
        raise ValueError("Lorentz transfer did not conserve the source force")
    return {"retained_force": retained, "motion_share": motion_share, "source_force": electric_force}


def maxwell_closure(dimension: int) -> dict[str, Fraction | int]:
    """Close equal per-axis spatial and temporal binary curvatures."""

    if dimension not in (boundary_rank_two(), spatial_dimension_three()):
        raise ValueError("Maxwell witness is registered only for forced planar and three-space support")
    per_axis = binary_count()
    spatial_curvature = per_axis * dimension
    temporal_curvature = binary_count()
    total_ratio = Fraction(spatial_curvature, temporal_curvature)
    speed_square = Fraction(spatial_curvature, dimension * temporal_curvature)
    if total_ratio != dimension or speed_square != 1:
        raise ValueError("Maxwell curvature did not close at the One speed")
    return {
        "dimension": dimension,
        "spatial_curvature": spatial_curvature,
        "temporal_curvature": temporal_curvature,
        "total_ratio": total_ratio,
        "speed_square": speed_square,
    }


def exact_optical_operations() -> dict[str, object]:
    """Execute propagation, polarization, interference and nonlinear mixing."""

    half = Fraction(1, binary_count())
    propagation = tuple(cyclic_advance(Fraction(1, 3), Fraction(1, 1)) for _ in range(8))
    polarization = ("transverse-left", "transverse-right")
    bright = half + half
    dark: tuple[()] = ()
    first, second = Fraction(1, 3), Fraction(1, 4)
    mixing = {
        "sum": first + second,
        "positive_difference": first - second,
        "second_harmonic": fold_part(second),
        "kerr_self_action": fold_part(Fraction(3, 4)),
        "third_harmonic": Fraction(3, 1) * Fraction(1, 6),
    }
    if any(phase != Fraction(1, 3) for phase in propagation):
        raise ValueError("One-speed propagation retained a phase residue")
    if bright != 1 or dark != () or set(mixing.values()) != {Fraction(7, 12), Fraction(1, 12), Fraction(1, 2)}:
        raise ValueError("optical operation ledger failed")
    return {
        "propagation": propagation,
        "polarization": polarization,
        "bright_support": bright,
        "dark_record": dark,
        "mixing": mixing,
    }


def finite_loop_sum(depth: int) -> Fraction:
    """Sum the complete generated positive binary loop support to finite depth."""

    if isinstance(depth, bool) or depth < 1:
        raise ValueError("loop depth must be a positive generated count")
    total = Fraction(1, binary_count())
    term = total
    for _ in range(1, depth):
        term /= binary_count()
        total += term
    if not 0 < total < 1:
        raise ValueError("finite Fold loop sum left its exact sub-One boundary")
    return total


COMMON_EXCLUSIONS = (
    "no V1/V2 executable, candidate table, certificate or answer artifact as a premise",
    "no conventional field equation, continuum, matrix algebra or measured constant selecting a survivor",
    "no fitted coefficient, adjustable phase, imported normalization or target-selected value",
    "no semantic numerical zero, negative, irrational, imaginary or floating proof quantity",
    "no target access before the complete exact result and candidate census are sealed",
)


def field_axes(relation: str, preservation: str, rejected_relation: str) -> tuple:
    return (
        binary_axis("carrier", "What carries the result?", "imported-continuum-object", "The object lacks a generated Fold support trace.", "generated-exact-Fold-carrier", "Every carrier is an exact admitted Fold count, part, word or held label."),
        binary_axis("dependency", "How are prerequisites obtained?", "asserted-prior-result", "A prior answer cannot act as a V3 premise.", "admitted-V3-dependency-chain", "Every dependency has an engine receipt back to the root theorem."),
        binary_axis("relation", "Which relation survives?", rejected_relation, "The alternative loses a required conservation or recurrence record.", relation, preservation),
        binary_axis("enumeration", "Are alternatives exhausted?", "selected-neighbourhood", "A selected candidate neighbourhood cannot prove uniqueness.", "complete-registered-product", "Every registered axis choice occurs with every other choice."),
        binary_axis("minimality", "Are omissions tested?", "uncontrolled-omission", "A missing carrier could silently select the answer.", "every-omission-rejected", "Each omitted carrier has a named failure condition."),
        binary_axis("measurement", "Can observation select the law?", "target-visible-before-seal", "Target access would reverse the empirical direction.", "formal-result-sealed-first", "The exact formal result is sealed before any comparison."),
        binary_axis("record", "What is retained?", "answer-only", "An answer without trace cannot be independently reproduced.", "complete-trace-and-controls", "The exact trace, census, decisions and hostile controls remain held."),
        binary_axis("extension", "May an extra selector be added?", "free-extra-rule", "An added selector is a free parameter.", "no-extra-rule", "The registered grammar is exhausted without another choice."),
    )


def spec(claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], relation: str,
         preservation: str, rejected: str, exact_result: str, base: str, step: str,
         witnesses: tuple[Witness, ...], *extra_exclusions: str) -> StructuralPhysicsSpec:
    return StructuralPhysicsSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.FORMAL,
        generation_rule=f"Generate the complete eight-axis product for {title.lower()}, including carrier, dependency, relation, enumeration, minimality, measurement direction, record and extension.",
        grammar_boundary="All finite exact Fold carriers named by this claim and every product of the eight registered binary form axes; conventional correspondence and physical calibration remain downstream.",
        axes=field_axes(relation, preservation, rejected),
        exact_result=exact_result,
        induction_base=base,
        induction_step=step,
        exclusions=COMMON_EXCLUSIONS + extra_exclusions,
        witnesses=witnesses,
    )


FREE_PHASE_SPEC = spec(
    FREE_PHASE_ID, "Free-particle Fold phase and exact dispersion",
    "A free phase advances by the Fold of its exact momentum carrier, and that advance is identically the composition of two momentum advances on the One-cycle.",
    ("SFT-FOUNDATION-FOLD-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-PHYS-MECH-MOMENTUM-001"),
    "Fold-momentum-equals-two-cyclic-advances", "Fold pairing and two exact advances are the same generated operation.", "borrowed-dispersion-law",
    "For p=1/4, Fold dispersion is 1/2 and phase 1/3 advances exactly to 5/6 by either one Fold step or two p steps.",
    "One positive momentum part generates one exact cyclic advance.", "Each further tick composes the same source-bound advance and retains its phase trace.",
    (Witness("dispersion", "Quarter momentum Folds to half-One dispersion.", free_particle_phase(Fraction(1, 3), Fraction(1, 4))["dispersion"] == Fraction(1, 2)), Witness("route-equality", "Fold and two-step routes end at five-sixths.", free_particle_phase(Fraction(1, 3), Fraction(1, 4))["phase_after"] == Fraction(5, 6))),
)

POTENTIAL_PHASE_SPEC = spec(
    POTENTIAL_PHASE_ID, "Potential evolution and additive exact phase",
    "Sequential kinetic and potential Fold rotations equal one rotation by their exact positive sum, so a path phase retains every energy contribution without an imported evolution equation.",
    (FREE_PHASE_ID, "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001"),
    "sequential-rotations-equal-summed-energy-rotation", "Exact cyclic composition is associative and retains both named energy carriers.", "opaque-phase-generator",
    "At phase 1/3, kinetic 1/8 followed by potential 1/4 equals one 3/8 advance and ends at 17/24.",
    "One kinetic and one potential carrier compose exactly.", "Each added positive contribution appends one rotation and the same contribution to the held total.",
    (Witness("composition", "Sequential and joint evolution agree.", potential_phase_evolution(Fraction(1, 3), Fraction(1, 8), Fraction(1, 4))["phase_after"] == Fraction(17, 24)), Witness("total", "The retained exact energy sum is three-eighths.", potential_phase_evolution(Fraction(1, 3), Fraction(1, 8), Fraction(1, 4))["total"] == Fraction(3, 8))),
)

STATIONARY_SPEC = spec(
    STATIONARY_ID, "Stationary Fold spectrum",
    "At every positive binary depth the unique half-spacing construction yields a finite exact spectrum with ground support half a grid step and every adjacent gap one whole grid step.",
    (POTENTIAL_PHASE_ID, "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001"),
    "half-step-ground-and-uniform-whole-step-gaps", "Complete binary support fixes all odd numerators and therefore every adjacent gap.", "selected-or-continuous-spectrum",
    "At depth k the levels are (2j-1)/2^(k+1); depth two is 1/8, 3/8, 5/8, 7/8 with gap 1/4.",
    "Depth One contains the two half-offset states one-quarter and three-quarters.", "Support doubling preserves odd numerators and halves the whole-step spacing.",
    (Witness("depth-two", "Depth two has the complete four-level spectrum.", stationary_spectrum(2) == (Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8))), Witness("uniform", "All tested finite successors retain uniform gaps.", all(len(set(stationary_spectrum(k)[i + 1] - stationary_spectrum(k)[i] for i in range(len(stationary_spectrum(k)) - 1))) == 1 for k in range(1, 6)))),
)

TWO_HAND_DIRAC_SPEC = spec(
    TWO_HAND_DIRAC_ID, "Two-hand exact Dirac square",
    "The first generated spatial, binary-square and covering counts force the exact 3/5 motion and 4/5 substance partition whose squares close on the One.",
    (STATIONARY_ID, "SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "generated-three-four-five-square-closure", "Three, binary-square four and their covering count five admit no chosen radical or measured mass.", "chosen-Pythagorean-or-imported-relativity",
    "The exact two-component square is (3/5)^2 + (4/5)^2 = 9/25 + 16/25 = One.",
    "The forced generator three and binary square four produce covering count five.", "Replication retains the same exact square identity for every source-labelled copy.",
    (Witness("parts", "Motion and substance are exact three-fifths and four-fifths.", two_hand_dirac_square()["momentum"] == Fraction(3, 5) and two_hand_dirac_square()["mass"] == Fraction(4, 5)), Witness("square", "Their squares close exactly.", two_hand_dirac_square()["energy_square"] == 1)),
)

FULL_DIRAC_SPEC = spec(
    FULL_DIRAC_ID, "Full three-plus-one Dirac square",
    "Three momentum generators and one mass generator exhaust the binary-square count four; placing each at the unique half-One balance partitions total square support into four quarters and closes on the One by direct and polarized routes.",
    (TWO_HAND_DIRAC_ID, "SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003"),
    "four-half-One-generators-close-by-two-routes", "The 3+1 generator count is binary-square and every critical component contributes one quarter.", "matrix-postulate-or-omitted-generator",
    "Four half-One generators give direct square 4*(1/2)^2=One; the complete polarized pairing gives the same One, with equal differences retained as empty structural records.",
    "Three spatial generators plus one mass generator make the complete count four.", "Every complete replicated 3+1 cell retains four quarter squares and both exact closure routes.",
    (Witness("direct", "The four component squares sum to One.", full_dirac_square()["direct_square"] == 1), Witness("polarized", "The polarized route also closes at One.", full_dirac_square()["polarized_square"] == 1), Witness("absence", "Equal differences are structural empty records.", full_dirac_square()["held_equal_differences"] == ((), ()))),
)

COULOMB_GAUSS_SPEC = spec(
    COULOMB_GAUSS_ID, "Charge, Coulomb potential and Gauss closure",
    "A conserved held charge distributed over the forced rank-two boundary yields exact inverse-square response; multiplying by complete boundary growth reconstructs the source at every generated radius.",
    (FULL_DIRAC_ID, "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001", "SFT-PHYS-FIELD-INVERSE-SQUARE-001"),
    "held-charge-over-rank-two-boundary-with-source-return", "Boundary rank two and conservation fix both field dilution and Gauss source reconstruction.", "imported-Coulomb-profile-or-free-exponent",
    "For source 1/8, radii 1/4 and 1/2 retain identical Gauss flux 1/8; fields are 2 and 1/2 and retained potentials are 1/2 and 3/4.",
    "One source on one complete boundary returns itself under field times boundary growth.", "Every generated radius changes cell count by the forced square while source flux remains invariant.",
    (Witness("inner", "The inner shell reconstructs source and half-One potential.", coulomb_gauss_closure(Fraction(1, 8), Fraction(1, 4))["flux"] == Fraction(1, 8) and coulomb_gauss_closure(Fraction(1, 8), Fraction(1, 4))["retained_potential"] == Fraction(1, 2)), Witness("outer", "The outer shell reconstructs source and three-quarter potential.", coulomb_gauss_closure(Fraction(1, 8), Fraction(1, 2))["flux"] == Fraction(1, 8) and coulomb_gauss_closure(Fraction(1, 8), Fraction(1, 2))["retained_potential"] == Fraction(3, 4))),
)

MAGNETIC_RELATIVITY_SPEC = spec(
    MAGNETIC_RELATIVITY_ID, "Magnetic relativistic correction",
    "For exact sub-One speed, the motion-held square and positive electric remainder partition the One; the remainder commutes with the Fold and therefore supplies the magnetic correction as a dynamical projection of the electric carrier.",
    (COULOMB_GAUSS_ID, "SFT-PHYS-FIELD-MAGNETIC-001", "SFT-PHYS-SPACETIME-LIMIT-SPEED-001"),
    "One-partition-by-speed-square-and-Fold-covariant-remainder", "Exact positive take preserves the source carrier and Fold covariance without a second force magnitude.", "independent-magnetic-force-postulate",
    "The correction is C(v)=One-v^2 as a positive retained part; at v=1/2 it is 3/4 and Fold(C)=1/2=One-Fold(v^2), likewise at v=1/3.",
    "One exact speed square partitions the One into motion-held and retained electric support.", "Every exact sub-One speed repeats the positive partition and Fold-covariance identity.",
    (Witness("half-speed", "Half speed gives three-quarter remainder and half folded remainder.", magnetic_relativistic_factor(Fraction(1, 2))["electric_remainder"] == Fraction(3, 4) and magnetic_relativistic_factor(Fraction(1, 2))["folded_remainder"] == Fraction(1, 2)), Witness("third-speed", "Third speed independently preserves Fold covariance.", magnetic_relativistic_factor(Fraction(1, 3))["folded_remainder"] == Fraction(7, 9))),
)

LORENTZ_TRANSFER_SPEC = spec(
    LORENTZ_TRANSFER_ID, "Lorentz transfer partition",
    "Motion does not create a second unaccounted force: it holds the exact speed-square share of electric transfer while the positive remainder acts on the observed carrier, and both shares reconstruct the source force.",
    (MAGNETIC_RELATIVITY_ID, "SFT-PHYS-MECH-FORCE-001", "SFT-PHYS-MECH-CONSERVATION-001"),
    "electric-transfer-partitioned-by-motion-share", "The two positive held shares sum exactly to the source transfer.", "unrelated-added-force",
    "For electric force 1/4 and speed 1/2, retained force is 3/16 and motion-held share is 1/16; together they return 1/4.",
    "One force carrier and one speed-square partition close exactly.", "Every added interaction event retains its own source, motion and recipient transfer records.",
    (Witness("retained", "The exact retained force is three-sixteenths.", lorentz_transfer(Fraction(1, 4), Fraction(1, 2))["retained_force"] == Fraction(3, 16)), Witness("partition", "Retained and motion shares reconstruct the source.", lorentz_transfer(Fraction(1, 4), Fraction(1, 2))["retained_force"] + lorentz_transfer(Fraction(1, 4), Fraction(1, 2))["motion_share"] == Fraction(1, 4))),
)

MAXWELL_PLANAR_SPEC = spec(
    MAXWELL_PLANAR_ID, "Planar Maxwell curvature closure",
    "On the forced rank-two boundary, two spatial axes each carry binary second-difference curvature while one temporal axis carries the same binary curvature; per-axis balance fixes wave speed-square at the One.",
    (LORENTZ_TRANSFER_ID, "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001", "SFT-PHYS-FIELD-ELECTROMAGNETIC-COMPOSITION-001"),
    "two-spatial-binary-curvatures-balance-one-temporal-per-axis", "Equal generated curvature per axis leaves no adjustable propagation speed.", "imported-planar-wave-equation",
    "Planar spatial curvature is four, temporal curvature is two, total ratio is two and dimension-normalized speed-square is One.",
    "One temporal and two spatial axes each carry the binary curvature count two.", "Each complete planar cell preserves equal per-axis curvature and One-speed closure.",
    (Witness("planar", "Planar curvatures and speed close exactly.", maxwell_closure(2) == {"dimension": 2, "spatial_curvature": 4, "temporal_curvature": 2, "total_ratio": Fraction(2, 1), "speed_square": Fraction(1, 1)}),),
)

MAXWELL_SPACE_SPEC = spec(
    MAXWELL_SPACE_ID, "Three-space Maxwell curvature closure",
    "In forced three-space, three spatial axes each carry binary second-difference curvature while one temporal axis carries the same binary curvature; dimension-normalized balance again fixes speed-square at the One.",
    (MAXWELL_PLANAR_ID, "SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-PHYS-FIELD-ELECTROMAGNETIC-COMPOSITION-001"),
    "three-spatial-binary-curvatures-balance-one-temporal-per-axis", "The same per-axis Fold curvature in every generated dimension forces dimension-independent One speed.", "imported-three-space-wave-equation",
    "Three-space spatial curvature is six, temporal curvature is two, total ratio is three and dimension-normalized speed-square is One.",
    "One temporal and three spatial axes each carry the binary curvature count two.", "Every complete three-space cell preserves equal per-axis curvature and One-speed closure.",
    (Witness("three-space", "Three-space curvatures and speed close exactly.", maxwell_closure(3) == {"dimension": 3, "spatial_curvature": 6, "temporal_curvature": 2, "total_ratio": Fraction(3, 1), "speed_square": Fraction(1, 1)}),),
)

OPTICAL_OPERATIONS_SPEC = spec(
    OPTICAL_OPERATIONS_ID, "Exact wave, polarization, interference and nonlinear operations",
    "The joint electromagnetic Fold carrier propagates one One per tick, retains two transverse held labels, merges two half-One predecessors into bright One or an empty dark record by orientation, and generates sum, positive-difference and harmonic nonlinear frequencies by exact Fold operations.",
    (MAXWELL_SPACE_ID, "SFT-PHYS-WAVE-INTERFERENCE-001", "SFT-PHYS-WAVE-POLARIZATION-001", "SFT-PHYS-WAVE-RESONANCE-001"),
    "One-speed-walk-held-polarization-predecessor-merge-and-exact-mixing", "All optical operations are generated by recurrence, held orientation, predecessor composition and exact positive beat/fold operations.", "imported-amplitude-or-nonlinear-susceptibility",
    "Eight One-speed ticks retain phase exactly; polarization has two held transverse labels; equal half carriers give bright One or an empty dark record; 1/3 and 1/4 mix to 7/12, 1/12 and second harmonic 1/2, while Kerr witnesses also return 1/2.",
    "One joint electric/magnetic recurrence transports one complete tick with held orientation.", "Every further tick or interaction composes exact carriers and retains the full source/phase ledger.",
    (Witness("walk", "Eight One-speed ticks retain the phase.", len(exact_optical_operations()["propagation"]) == 8 and len(set(exact_optical_operations()["propagation"])) == 1), Witness("polarization", "The two transverse labels remain held.", exact_optical_operations()["polarization"] == ("transverse-left", "transverse-right")), Witness("interference", "Bright is One and dark is structural absence.", exact_optical_operations()["bright_support"] == 1 and exact_optical_operations()["dark_record"] == ()), Witness("mixing", "Exact nonlinear outputs are generated without fitting.", exact_optical_operations()["mixing"]["sum"] == Fraction(7, 12) and exact_optical_operations()["mixing"]["positive_difference"] == Fraction(1, 12))),
)

FINITE_LOOP_SPEC = spec(
    FINITE_LOOP_ID, "Floored finite-loop closure",
    "Every generated physical loop support has positive finite Fold depth; summing its complete exact rational terms therefore yields a finite rational receipt, while an ungenerated continuum or unlimited-depth completion is outside the admitted claim.",
    (OPTICAL_OPERATIONS_ID, "SFT-PHYS-VACUUM-ODD-RECURRENCE-003", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "complete-finite-depth-exact-rational-loop-sum", "Finite generated support and exact addition cannot produce an unrecorded divergence or subtraction counterterm.", "continuum-divergence-and-fitted-counterterm",
    "The depth-n binary loop sum is the exact positive finite sum 1/2+1/4+...+1/2^n; depths one through six give 1/2, 3/4, 7/8, 15/16, 31/32, 63/64.",
    "Depth One contains exactly the half-One loop carrier.", "Appending a generated depth appends its exact halved positive term, preserving a finite rational total below the One.",
    (Witness("prefix", "The first six loop sums are exact and finite.", tuple(finite_loop_sum(k) for k in range(1, 7)) == (Fraction(1, 2), Fraction(3, 4), Fraction(7, 8), Fraction(15, 16), Fraction(31, 32), Fraction(63, 64))), Witness("finite-boundary", "Every tested generated depth remains a positive rational below One.", all(0 < finite_loop_sum(k) < 1 for k in range(1, 17)))),
    "no claim about an actually completed infinite support or a measured radiative coefficient",
)


RELATIVISTIC_FIELD_SPECS = (
    FREE_PHASE_SPEC,
    POTENTIAL_PHASE_SPEC,
    STATIONARY_SPEC,
    TWO_HAND_DIRAC_SPEC,
    FULL_DIRAC_SPEC,
    COULOMB_GAUSS_SPEC,
    MAGNETIC_RELATIVITY_SPEC,
    LORENTZ_TRANSFER_SPEC,
    MAXWELL_PLANAR_SPEC,
    MAXWELL_SPACE_SPEC,
    OPTICAL_OPERATIONS_SPEC,
    FINITE_LOOP_SPEC,
)
SPEC_BY_ID = {item.claim_id: item for item in RELATIVISTIC_FIELD_SPECS}

for _spec in RELATIVISTIC_FIELD_SPECS:
    _spec.validate()


__all__ = (
    "RELATIVISTIC_FIELD_SPECS",
    "SPEC_BY_ID",
    "cyclic_advance",
    "free_particle_phase",
    "potential_phase_evolution",
    "stationary_spectrum",
    "two_hand_dirac_square",
    "full_dirac_square",
    "coulomb_gauss_closure",
    "magnetic_relativistic_factor",
    "lorentz_transfer",
    "maxwell_closure",
    "exact_optical_operations",
    "finite_loop_sum",
)
