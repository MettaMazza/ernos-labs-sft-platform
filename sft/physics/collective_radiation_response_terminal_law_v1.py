"""Exact finite radiation, acoustic, laser, plasma and Alfvén response law."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041"
SPACE_RANK = 3
BINARY = 2


def require_positive(value: Fraction, name: str) -> Fraction:
    result = Fraction(value)
    if result <= 0:
        raise ValueError(f"{name} must be an exact positive Fold carrier")
    return result


def finite_boson_occupations(mode_costs: tuple[int, ...], total_quanta: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate every finite occupation word at fixed exact total energy.

    The host integer 0 denotes an empty mode record; it is not admitted as a
    physical magnitude.  Every occupied contribution is a positive whole.
    """

    if not mode_costs or any(isinstance(cost, bool) or cost < 1 for cost in mode_costs):
        raise ValueError("mode costs must be positive generated wholes")
    if isinstance(total_quanta, bool) or total_quanta < 1:
        raise ValueError("total quanta must be a positive generated whole")
    limits = tuple(total_quanta // cost for cost in mode_costs)
    return tuple(
        word
        for word in product(*(range(limit + 1) for limit in limits))
        if sum(cost * count for cost, count in zip(mode_costs, word)) == total_quanta
    )


def exact_mode_occupation(mode_costs: tuple[int, ...], total_quanta: int) -> tuple[Fraction, ...]:
    words = finite_boson_occupations(mode_costs, total_quanta)
    if not words:
        raise ValueError("generated support has no complete occupation word")
    count = len(words)
    return tuple(Fraction(sum(word[index] for word in words), count) for index in range(len(mode_costs)))


def ultraviolet_closed(mode_costs: tuple[int, ...], total_quanta: int) -> bool:
    occupations = exact_mode_occupation(mode_costs, total_quanta)
    return all(occupation == 0 for cost, occupation in zip(mode_costs, occupations) if cost > total_quanta)


def occupation_scale_covariant(mode_costs: tuple[int, ...], total_quanta: int, scale: int) -> bool:
    if isinstance(scale, bool) or scale < 1:
        raise ValueError("scale must be a positive generated whole")
    return finite_boson_occupations(mode_costs, total_quanta) == finite_boson_occupations(
        tuple(scale * cost for cost in mode_costs), scale * total_quanta
    )


def radiation_power_ratio(temperature_ratio: Fraction) -> Fraction:
    ratio = require_positive(temperature_ratio, "temperature ratio")
    return ratio ** (SPACE_RANK + 1)


def acoustic_ladder(fundamental: Fraction, mode_count: int) -> tuple[Fraction, ...]:
    base = require_positive(fundamental, "fundamental")
    if isinstance(mode_count, bool) or mode_count < 1:
        raise ValueError("mode count must be a positive generated whole")
    return tuple(mode * base for mode in range(1, mode_count + 1))


def laser_ledger(excited: int, lower: int, gain: Fraction, loss: Fraction, coherence_ticks: int) -> dict[str, object]:
    if any(isinstance(value, bool) or value < 1 for value in (excited, lower, coherence_ticks)):
        raise ValueError("laser counts must be positive generated wholes")
    exact_gain = require_positive(gain, "gain")
    exact_loss = require_positive(loss, "loss")
    inversion = Fraction(excited, excited + lower)
    return {
        "inversion": inversion,
        "population_inverted": inversion > Fraction(1, 2),
        "at_threshold": exact_gain == exact_loss,
        "above_threshold": exact_gain > exact_loss and inversion > Fraction(1, 2),
        "linewidth": Fraction(1, coherence_ticks),
        "linewidth_time_product": Fraction(1, coherence_ticks) * coherence_ticks,
    }


def plasma_squared_carriers(
    charge_count: Fraction, charge: Fraction, mass: Fraction, permittivity: Fraction, temperature: Fraction
) -> dict[str, Fraction]:
    n = require_positive(charge_count, "charge count")
    q = require_positive(charge, "charge")
    m = require_positive(mass, "mass")
    e = require_positive(permittivity, "permittivity")
    t = require_positive(temperature, "temperature")
    stiffness = n * q * q
    return {
        "plasma_frequency_squared": stiffness / (m * e),
        "debye_length_squared": e * t / stiffness,
    }


def alfven_squared_carrier(field: Fraction, permeability: Fraction, density: Fraction) -> Fraction:
    b = require_positive(field, "field")
    mu = require_positive(permeability, "permeability")
    rho = require_positive(density, "density")
    return b * b / (mu * rho)


def theorem_certificate() -> dict[str, object]:
    costs = (1, 2, 3, 5, 8)
    quanta = 7
    plasma = plasma_squared_carriers(Fraction(3), Fraction(2), Fraction(5), Fraction(7), Fraction(11))
    laser = laser_ledger(3, 2, Fraction(4, 3), Fraction(5, 4), 7)
    return {
        "occupation_count": len(finite_boson_occupations(costs, quanta)),
        "energy_exact": all(sum(c * n for c, n in zip(costs, word)) == quanta for word in finite_boson_occupations(costs, quanta)),
        "uv_closed": ultraviolet_closed(costs, quanta),
        "scale_covariant": all(occupation_scale_covariant(costs, quanta, scale) for scale in range(1, 7)),
        "fourth_power": radiation_power_ratio(Fraction(2)) == 16 and radiation_power_ratio(Fraction(3, 2)) == Fraction(81, 16),
        "acoustic": acoustic_ladder(Fraction(1, 6), 4) == (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)),
        "laser": laser["population_inverted"] and laser["above_threshold"] and laser["linewidth_time_product"] == 1,
        "plasma": plasma["plasma_frequency_squared"] == Fraction(12, 35) and plasma["debye_length_squared"] == Fraction(77, 12),
        "alfven": alfven_squared_carrier(Fraction(3), Fraction(5), Fraction(7)) == Fraction(9, 35),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal finite radiation, acoustic, laser, plasma and Alfvén response law",
    statement=(
        "Finite bosonic cavity support is the complete exact occupation-word census at held total quanta; modes costing "
        "more than the support carry only an empty record, so the ultraviolet tail closes without a continuum exponential. "
        "Common exact scaling of energy and mode costs preserves every occupation word, forcing peak-frequency covariance "
        "with temperature. Three spatial mode-count powers plus one energy power force radiated power ratio g^4. Fixed "
        "boundaries force acoustic frequencies n times the fundamental. Stimulated emission duplicates the held photon "
        "mode; inversion is strictly above half-One, lasing threshold is exact gain/loss equality, and linewidth times "
        "coherence ticks is One. Charge stiffness forces plasma-frequency-squared=nq^2/(m epsilon) and Debye-length-squared="
        "epsilon T/(nq^2). Magnetic tension over inertia forces Alfvén-speed-squared=B^2/(mu rho). Squared carriers retain "
        "exact Fold arithmetic without importing irrational roots."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001", "SFT-FOUNDATION-FOLD-001", "SFT-FOUNDATION-PART-001",
        "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001", "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001",
        "SFT-PHYS-THERMO-TEMPERATURE-001", "SFT-PHYS-MATTER-FERMION-BOSON-001",
        "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001", "SFT-PHYS-FIELD-RADIATION-001",
        "SFT-PHYS-WAVE-RESONANCE-001", "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005",
        "SFT-PHYS-PLASMA-COLLECTIVE-001", "SFT-PHYS-PLASMA-OSCILLATION-001",
        "SFT-PHYS-FLUID-DENSITY-001", "SFT-PHYS-FIELD-MAGNETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of finite occupation, radiative dimension, acoustic boundary, stimulated mode, "
        "gain threshold, linewidth, plasma balance and magnetofluid response forms."
    ),
    grammar_boundary=(
        "Every finite positive-whole mode-cost list and positive total-quanta support; every common positive-whole scale; "
        "every exact positive temperature ratio; every positive acoustic mode count; every positive laser population, "
        "gain, loss and coherence count; and every exact positive charge, mass, permittivity, temperature, field, "
        "permeability and density carrier. Empty occupation is a structural empty record, not a physical zero magnitude."
    ),
    axes=(
        binary_axis("occupation", "What fixes cavity occupation?", "continuum-exponential-premise", "An imported exponential violates finite exact generation.", "complete-finite-boson-word-census", "Every exact word at held total quanta is generated once."),
        binary_axis("radiation", "What fixes total radiative scaling?", "fitted-Stefan-exponent", "A fitted exponent is target-selected.", "three-mode-powers-plus-one-energy-power", "Stable three-space plus energy forces fourth power."),
        binary_axis("acoustic", "What frequencies fit fixed boundaries?", "selected-frequency-list", "A named spectrum cannot select the law.", "positive-whole-harmonic-ladder", "Closure admits exactly positive-whole multiples of the fundamental."),
        binary_axis("stimulated", "What does stimulated emission preserve?", "unrelated-spontaneous-output", "An unrelated output does not amplify a held mode.", "duplicated-identical-held-mode", "Bosonic mode preservation appends one identical photon record."),
        binary_axis("threshold", "What fixes lasing threshold?", "free-gain-setting", "A free setting adds a parameter.", "gain-loss-equality-with-strict-half-One-inversion", "Balance is equality and inversion is strictly above the binary midpoint."),
        binary_axis("linewidth", "What fixes linewidth?", "zero-width-monochromatic-idealization", "A numerical-zero width erases the finite record.", "positive-reciprocal-coherence-carrier", "One over positive coherence ticks closes the exact product to One."),
        binary_axis("plasma", "What fixes plasma response and screening?", "named-empirical-fit", "A named fit cannot select the carrier.", "charge-stiffness-over-inertia-and-thermal-balance", "The same exact charge stiffness supplies oscillation and screening balances."),
        binary_axis("magnetofluid", "What fixes the Alfvén carrier?", "selected-wave-speed", "A measured speed is not a derivation.", "magnetic-tension-over-fluid-inertia", "Field-square tension divided by permeability-density is the unique squared carrier."),
    ),
    exact_result=(
        "Every finite cavity occupation is an exact rational mean over the complete microcanonical word census; all modes "
        "above total support are empty and common scale changes preserve the complete word set. Wien covariance is exact "
        "at the relation level. In stable three-space P(gT)/P(T)=g^4, so doubling gives 16. Acoustic modes are f_n=n f_1. "
        "Laser inversion is greater than 1/2, threshold is gain=loss, above-threshold requires gain>loss, and linewidth "
        "times coherence ticks is One. Plasma omega_p^2=nq^2/(m epsilon), lambda_D^2=epsilon T/(nq^2), and Alfvén "
        "v_A^2=B^2/(mu rho), all as exact positive rational carriers."
    ),
    induction_base=(
        "The first positive mode and first quantum have one complete occupation word; one acoustic half-wave gives the fundamental; one coherence tick gives linewidth One."
    ),
    induction_step=(
        "Appending a finite mode or quantum regenerates the complete energy-preserving word set; appending a spatial mode-count direction appends one temperature power; each boundary mode appends one fundamental; every positive carrier successor preserves the three squared balance identities."
    ),
    exclusions=(
        "no Planck exponential, Bose-Einstein continuum distribution, fitted Wien constant or Stefan coefficient as premise",
        "no measured spectrum, laser setting, plasma frequency, screening length or Alfvén speed available to selection",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof magnitude",
        "no square-root proof value; squared frequency, length and speed carriers are the exact native forms",
        "no free gain, loss, linewidth, plasma, acoustic or magnetofluid coefficient",
    ),
    witnesses=(
        Witness("occupation", "The complete finite word census preserves energy, closes its ultraviolet support and is exactly scale covariant.", theorem_certificate()["energy_exact"] and theorem_certificate()["uv_closed"] and theorem_certificate()["scale_covariant"]),
        Witness("radiation-acoustic", "Three-space radiation is fourth-power and fixed boundaries give whole harmonics.", theorem_certificate()["fourth_power"] and theorem_certificate()["acoustic"]),
        Witness("laser", "Strict inversion, gain-over-loss and positive reciprocal linewidth close together.", theorem_certificate()["laser"]),
        Witness("plasma", "Oscillation and screening share the exact charge stiffness.", theorem_certificate()["plasma"]),
        Witness("alfven", "Magnetic tension over inertia gives an exact positive squared carrier.", theorem_certificate()["alfven"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "SPEC", "acoustic_ladder", "alfven_squared_carrier", "exact_mode_occupation",
    "finite_boson_occupations", "laser_ledger", "occupation_scale_covariant", "plasma_squared_carriers",
    "radiation_power_ratio", "theorem_certificate", "ultraviolet_closed",
)
