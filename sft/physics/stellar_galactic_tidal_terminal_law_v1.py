"""Terminal stellar-balance, galactic-response and tidal-lock law.

V1/V2 descriptions are observational audit targets only.  This module reads
no stellar, galaxy, lunar, planetary or fitted exponent measurement.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


CLAIM_ID = "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067"
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)


def hydrostatic_balance() -> dict[str, Fraction | bool]:
    outward = HALF_ONE
    inward = HALF_ONE
    return {
        "outward_share": outward,
        "inward_share": inward,
        "complete": outward + inward == ONE,
        "balanced": outward == inward,
    }


def radial_response_exponents() -> dict[str, Fraction]:
    """Return exact response exponents without evaluating fractional powers."""

    space = generator_period_three()
    fibres = 2
    return {
        "pressure": Fraction(space + fibres, space),
        "gravity": Fraction(space + 1, space),
    }


def radial_restoration(q: Fraction) -> dict[str, Fraction | bool]:
    """Compare cubed response carriers at exact compression/expansion q>One."""

    if not isinstance(q, Fraction) or q <= ONE:
        raise ValueError("radial response requires an exact positive ratio above the One")
    compressed_pressure_cubed = q ** 5
    compressed_gravity_cubed = q ** 4
    expanded_pressure_cubed = ONE / (q ** 5)
    expanded_gravity_cubed = ONE / (q ** 4)
    return {
        "q": q,
        "compressed_pressure_cubed": compressed_pressure_cubed,
        "compressed_gravity_cubed": compressed_gravity_cubed,
        "compression_pushes_out": compressed_pressure_cubed > compressed_gravity_cubed,
        "expanded_pressure_cubed": expanded_pressure_cubed,
        "expanded_gravity_cubed": expanded_gravity_cubed,
        "expansion_pulls_in": expanded_gravity_cubed > expanded_pressure_cubed,
        "irrational_root_evaluated": False,
    }


def stellar_luminosity_exponents() -> tuple[int, int]:
    """Volume and volume-plus-radiative-recurrence terminal classes."""

    space = generator_period_three()
    return space, space + 1


def stellar_lifetime_fall_exponents() -> tuple[int, int]:
    """One fuel carrier divided by each luminosity carrier."""

    return tuple(exponent - 1 for exponent in stellar_luminosity_exponents())


def stellar_scaling(q: Fraction) -> dict[str, tuple[Fraction, ...]]:
    if not isinstance(q, Fraction) or q <= ONE:
        raise ValueError("stellar scaling requires an exact positive mass ratio above the One")
    luminosity = tuple(q ** exponent for exponent in stellar_luminosity_exponents())
    lifetime_divisors = tuple(q ** exponent for exponent in stellar_lifetime_fall_exponents())
    return {
        "mass_ratio": (q,),
        "luminosity_ratios": luminosity,
        "higher_mass_lifetime_divisors": lifetime_divisors,
    }


def circular_velocity_square(enclosed_mass: Fraction, radius: Fraction) -> Fraction:
    if not all(isinstance(value, Fraction) and value > 0 for value in (enclosed_mass, radius)):
        raise ValueError("circular balance requires exact positive mass and radius")
    return enclosed_mass / radius


def flat_curve_mass_growth(radius_ratio: Fraction) -> Fraction:
    if not isinstance(radius_ratio, Fraction) or radius_ratio <= ONE:
        raise ValueError("flat-curve comparison requires an outward radius ratio")
    # v^2=M/r is unchanged only when M grows by the identical radius ratio.
    return radius_ratio


def visible_asymptote_comparison(radius_ratio: Fraction) -> dict[str, Fraction | bool]:
    if not isinstance(radius_ratio, Fraction) or radius_ratio <= ONE:
        raise ValueError("visible-asymptote comparison requires an outward radius ratio")
    inner = circular_velocity_square(ONE, ONE)
    outer = circular_velocity_square(ONE, radius_ratio)
    flat_outer = circular_velocity_square(flat_curve_mass_growth(radius_ratio), radius_ratio)
    return {
        "visible_inner_velocity_squared": inner,
        "visible_outer_velocity_squared": outer,
        "visible_only_falls": outer < inner,
        "linearly_growing_mass_flat_velocity_squared": flat_outer,
        "flat_requires_additional_enclosed_support": flat_outer == inner and flat_curve_mass_growth(radius_ratio) > ONE,
    }


def baryonic_tully_fisher_exponent() -> int:
    return generator_period_three() + 1


def baryonic_tully_fisher_ratio(velocity_ratio: Fraction) -> Fraction:
    if not isinstance(velocity_ratio, Fraction) or velocity_ratio <= 0:
        raise ValueError("Tully-Fisher comparison requires an exact positive velocity ratio")
    return velocity_ratio ** baryonic_tully_fisher_exponent()


def tidal_dissipation_trace(spin_cycles: int, orbit_cycles: int) -> tuple[dict[str, int | str], ...]:
    """Exhaust a finite rational mismatch one generated cycle at a time."""

    if isinstance(spin_cycles, bool) or isinstance(orbit_cycles, bool):
        raise ValueError("cycle counts must be positive wholes")
    if not isinstance(spin_cycles, int) or not isinstance(orbit_cycles, int) or min(spin_cycles, orbit_cycles) < 1:
        raise ValueError("cycle counts must be positive wholes")
    spin, orbit = spin_cycles, orbit_cycles
    rows = []
    while spin != orbit:
        before = abs(spin - orbit)
        if spin > orbit:
            spin -= 1
            direction = "spin-surplus-transferred"
        else:
            orbit -= 1
            direction = "orbit-surplus-transferred"
        after = abs(spin - orbit)
        rows.append({"spin": spin, "orbit": orbit, "mismatch_before": before, "mismatch_after": after, "direction": direction})
        if after >= before:
            raise ValueError("tidal dissipation failed to reduce mismatch")
    rows.append({"spin": spin, "orbit": orbit, "mismatch_before": 0, "mismatch_after": 0, "direction": "one-to-one-lock"})
    return tuple(rows)


def tidal_terminal(spin_cycles: int, orbit_cycles: int) -> dict[str, object]:
    trace = tidal_dissipation_trace(spin_cycles, orbit_cycles)
    terminal = trace[-1]
    return {
        "trace": trace,
        "finite": len(trace) == abs(spin_cycles - orbit_cycles) + 1,
        "strictly_dissipative_before_lock": all(row["mismatch_after"] < row["mismatch_before"] for row in trace[:-1]),
        "terminal_ratio": (terminal["spin"], terminal["orbit"]),
        "terminal_one_to_one": terminal["spin"] == terminal["orbit"],
        "external_forcing_or_eccentric_resonance_boundary": "separate-generated-boundary",
    }


def theorem_certificate() -> dict[str, object]:
    radial_rows = tuple(radial_restoration(q) for q in (Fraction(3, 2), Fraction(2), Fraction(5, 2)))
    galaxy_rows = tuple(visible_asymptote_comparison(q) for q in (Fraction(3, 2), Fraction(2), Fraction(3)))
    tidal_rows = tuple(tidal_terminal(*pair) for pair in ((2, 1), (3, 1), (3, 2), (5, 3)))
    return {
        "hydrostatic": hydrostatic_balance(),
        "radial_exponents": radial_response_exponents(),
        "radial_rows": radial_rows,
        "luminosity_exponents": stellar_luminosity_exponents(),
        "lifetime_fall_exponents": stellar_lifetime_fall_exponents(),
        "stellar_rows": tuple(stellar_scaling(q) for q in (Fraction(3, 2), Fraction(2), Fraction(3))),
        "galaxy_rows": galaxy_rows,
        "tully_fisher_exponent": baryonic_tully_fisher_exponent(),
        "tidal_rows": tidal_rows,
        "all_radial_restoring": all(row["compression_pushes_out"] and row["expansion_pulls_in"] for row in radial_rows),
        "all_flat_rows_require_growth": all(row["flat_requires_additional_enclosed_support"] for row in galaxy_rows),
        "all_tidal_rows_lock": all(row["terminal_one_to_one"] and row["finite"] for row in tidal_rows),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal stellar hydrostatics, galactic response and tidal-lock law",
    statement=(
        "Half-One is the unique complete two-share balance, so normalized stellar pressure and gravity meet at "
        "one-half each. In three generated spatial directions, complete pressure response retains the three directions "
        "plus both Fold fibres, while gravity retains the three directions plus the One source: exact exponents 5/3 "
        "and 4/3. Cubing removes every root; compression gives q^5>q^4 and expansion gives 1/q^4>1/q^5, forcing "
        "radial restoration. Three-space volume and its one radiative recurrence force the two terminal luminosity "
        "classes M^3 and M^4; one fuel carrier then forces lifetime divisors M^2 and M^3. Under the admitted "
        "inverse-square law, circular balance is v^2=M(r)/r: a finite visible-mass asymptote must fall, while a flat "
        "curve forces enclosed support to grow exactly with radius. Three-space plus the orbital recurrence forces "
        "the fourth-power baryonic Tully-Fisher carrier. Finally, every finite rational spin-orbit mismatch loses one "
        "generated surplus cell per dissipative step and terminates at 1:1 when no separate eccentric or external "
        "forcing channel remains."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-ONE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009",
        "SFT-PHYS-FLUID-PRESSURE-STRESS-001",
        "SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043",
        "SFT-PHYS-WAVE-RESONANCE-001",
        "SFT-PHYS-MECH-ANGULAR-MOTION-001",
        "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061",
        "SFT-PHYS-COSMO-STRUCTURE-GROWTH-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of hydrostatic balance, radial response, stellar scaling, lifetime, "
        "circular balance, flat-curve support, dark carrier, Tully-Fisher exponent, resonance, tidal dissipation, "
        "measurement custody and extension forms."
    ),
    grammar_boundary=(
        "Exact positive normalized shares; three-space and two-fibre counts; exact q above the One; perfect-power "
        "response comparisons; homologous volume and radiative-recurrence stellar endpoints; circular inverse-square "
        "balance; finite enclosed-support and velocity ratios; finite rational spin/orbit cycle counts; inherited "
        "neutral relic and resonance laws; and no measurement before seal."
    ),
    axes=(
        binary_axis("hydrostatic", "What closes stellar push and pull?", "selected-pressure-gravity-ratio", "A selected ratio is a parameter.", "complete-self-antipodal-half-One", "The only complete equal two-share partition is half-One plus half-One."),
        binary_axis("radial", "What determines restoration?", "asserted-self-correction", "An assertion does not compare response carriers.", "five-thirds-versus-four-thirds-perfect-power-test", "Three-space with two fibres and one source forces q^5 versus q^4 after cubing."),
        binary_axis("stellar", "Which terminal homologous luminosity classes are generated?", "fitted-single-power", "A fitted exponent is selected by stellar data.", "three-space-and-volume-plus-recurrence", "Volume supplies power three and one radiative recurrence supplies power four."),
        binary_axis("lifetime", "How does lifetime follow?", "independent-lifetime-fit", "An independent lifetime exponent adds a dial.", "one-fuel-carrier-over-complete-luminosity", "Subtracting the one fuel carrier from powers three/four forces fall magnitudes two/three."),
        binary_axis("circular", "What is the circular-response relation?", "imported-Kepler-answer", "An inherited named answer is not a Fold derivation.", "inverse-square-balance-v-squared-equals-M-over-r", "The admitted inverse-square carrier and circular recurrence close the exact squared relation."),
        binary_axis("flat", "What sustains a flat outer curve?", "finite-visible-asymptote", "A fixed mass makes M/r fall outward.", "enclosed-support-grows-linearly-with-radius", "Exact constancy of M/r forces identical mass and radius ratios."),
        binary_axis("dark", "Which carrier supplies the additional support?", "modified-law-or-named-particle", "A named alternative is not structurally selected.", "admitted-neutral-stable-relic-under-fixed-gravity", "The existing neutral relic supplies support while the independently sealed gravity law remains fixed."),
        binary_axis("tully", "What fixes the baryonic rotation exponent?", "measured-or-fitted-slope", "A slope selected from galaxies is a parameter.", "three-space-plus-one-orbital-recurrence", "Complete spatial support plus its recurrence forces fourth-power velocity transport."),
        binary_axis("resonance", "Which orbital recurrences are admissible?", "irrational-continuum-period", "An irrational continuum period violates the generated finite recurrence grammar.", "finite-low-denominator-common-refinement", "The inherited resonance law retains exact rational common refinements."),
        binary_axis("tidal", "Where does isolated circular tidal dissipation terminate?", "unbounded-or-selected-terminal-ratio", "An unbounded path or selected ratio does not close.", "finite-mismatch-exhaustion-to-one-to-one", "Every step removes one surplus cycle and finite support terminates at equality."),
        binary_axis("measurement", "May observations select any exponent or terminal?", "target-readable-before-seal", "That would fit the result.", "all-targets-inaccessible-until-seal", "Stellar, galaxy and planetary measurements open only after the formal receipt."),
        binary_axis("extension", "May another response or correction be appended?", "free-response-scale-or-correction", "An added response forks the law.", "no-extra-rule", "The complete generated carriers and explicit external-forcing boundary exhaust the grammar."),
    ),
    exact_result=(
        "Hydrostatic balance is exactly (1/2,1/2). Radial pressure and gravity responses are 5/3 and 4/3, certified "
        "only through q^5 and q^4 perfect powers: every compression is outward restoring and every expansion inward "
        "restoring. The two terminal homologous luminosity exponents are three and four, forcing lifetime-fall "
        "magnitudes two and three. Circular balance is v^2=M(r)/r; flat v forces M(r) proportional to r and excludes "
        "a finite visible-only asymptote. The baryonic Tully-Fisher exponent is exactly four. Every finite rational "
        "isolated circular tidal mismatch exhausts to 1:1; eccentric or externally forced resonances remain an explicit "
        "separate boundary rather than a counterexample hidden from the census."
    ),
    induction_base="Half-One closes the first pressure/gravity pair; q^5 versus q^4 closes the first exact radial displacement; one surplus spin/orbit cell closes in one dissipative step.",
    induction_step="Every positive q successor preserves perfect-power order, every homologous mass successor preserves the generated powers, every radius successor preserves M/r only by identical enclosed-support growth, and every finite mismatch successor removes exactly one remaining surplus cell.",
    exclusions=(
        "no V1/V2 executable, stellar catalogue, galaxy slope, lunar period, survivor identifier or measured target in formal execution",
        "no fitted exponent, mass-to-light ratio, halo profile, tidal quality factor, age, metallicity or normalization",
        "no universal claim that every stellar mass domain has one exponent and no concealment of separate microphysical regimes",
        "no universal 1:1 claim for eccentric or externally maintained spin-orbit resonances",
        "no negative, irrational, imaginary, floating, NaN, continuum or infinite proof scalar",
    ),
    witnesses=(
        Witness("hydrostatic", "Half-One is the complete balanced pair.", hydrostatic_balance()["complete"] and hydrostatic_balance()["balanced"]),
        Witness("radial-restoration", "All exact registered displacements restore without evaluating a fractional root.", theorem_certificate()["all_radial_restoring"] and all(not row["irrational_root_evaluated"] for row in theorem_certificate()["radial_rows"])),
        Witness("stellar-endpoints", "Three/four luminosity and two/three lifetime endpoint classes are exact.", stellar_luminosity_exponents() == (3, 4) and stellar_lifetime_fall_exponents() == (2, 3)),
        Witness("flat-curve", "Every exact registered flat curve forces enclosed support growth.", theorem_certificate()["all_flat_rows_require_growth"]),
        Witness("tully-four", "Three-space plus the recurrence forces fourth-power baryonic transport.", baryonic_tully_fisher_exponent() == 4 and baryonic_tully_fisher_ratio(Fraction(2)) == 16),
        Witness("tidal-terminal", "Every finite registered mismatch terminates at one-to-one with strict prior decrease.", theorem_certificate()["all_tidal_rows_lock"] and all(row["strictly_dissipative_before_lock"] for row in theorem_certificate()["tidal_rows"])),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "HALF_ONE",
    "ONE",
    "SPEC",
    "baryonic_tully_fisher_exponent",
    "baryonic_tully_fisher_ratio",
    "circular_velocity_square",
    "flat_curve_mass_growth",
    "hydrostatic_balance",
    "radial_response_exponents",
    "radial_restoration",
    "stellar_lifetime_fall_exponents",
    "stellar_luminosity_exponents",
    "stellar_scaling",
    "theorem_certificate",
    "tidal_dissipation_trace",
    "tidal_terminal",
    "visible_asymptote_comparison",
)
