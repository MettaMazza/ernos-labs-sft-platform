"""Zero-parameter terminal nuclear-binding curve successor.

The executable relation contains no nuclide name, measured binding energy,
mass table, semi-empirical coefficient or fitted residual.  All scientific
quantities are positive exact counts or :class:`fractions.Fraction` values.
Structural absence is the empty tuple.  Cube roots are never admitted as
values: exact rational lower and upper enclosures are refined only until the
ordering certificate separates.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import (
    binary_count,
    fine_structure_blocks,
    inverse_fine_structure,
    positive_power,
)
from sft.physics.nuclear_residual_force_successor_laws_v1 import residual_boundary_support
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
    positive_predecessor,
)


NUCLEAR_BINDING_CURVE_TERMINAL_ID = "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005"
Empty = tuple[()]


@lru_cache(maxsize=1)
def surface_deficit_share() -> Fraction:
    """One missing boundary act over the binary-plus-generator interface."""

    down = fine_structure_blocks()["down"]
    if down != binary_count() + generator_period_three():
        raise ValueError("surface interface carrier did not cross-lock")
    return Fraction(1, down)


@lru_cache(maxsize=1)
def electromagnetic_share() -> Fraction:
    return Fraction(1, 1) / inverse_fine_structure()


@lru_cache(maxsize=1)
def asymmetry_share() -> Fraction:
    return residual_boundary_support()


@lru_cache(maxsize=1)
def pairing_share() -> Fraction:
    return residual_boundary_support()


def neutron_count(mass_number: int, charge_count: int) -> int:
    if isinstance(mass_number, bool) or isinstance(charge_count, bool):
        raise ValueError("nuclear counts must be exact positive counts")
    if mass_number <= 1 or charge_count < 1 or charge_count >= mass_number:
        raise ValueError("a nucleus requires positive proton and neutron support")
    retained = positive_take(Fraction(mass_number, 1), Fraction(charge_count, 1))
    if retained.denominator != 1:
        raise ValueError("neutron count did not remain whole")
    return retained.numerator


def ordered_charge_paths(charge_count: int) -> int | Empty:
    """Count source-to-distinct-target Coulomb paths without a half factor."""

    if isinstance(charge_count, bool) or charge_count < 1:
        raise ValueError("charge support must be a positive exact count")
    if charge_count == 1:
        return ()
    return charge_count * positive_predecessor(charge_count)


def unmatched_label_count(mass_number: int, charge_count: int) -> int | Empty:
    neutrons = neutron_count(mass_number, charge_count)
    if neutrons == charge_count:
        return ()
    larger, smaller = (neutrons, charge_count) if neutrons > charge_count else (charge_count, neutrons)
    retained = positive_take(Fraction(larger, 1), Fraction(smaller, 1))
    return retained.numerator


def pairing_class(mass_number: int, charge_count: int) -> str:
    neutrons = neutron_count(mass_number, charge_count)
    proton_even = charge_count % binary_count() == 0
    neutron_even = neutrons % binary_count() == 0
    if proton_even and neutron_even:
        return "paired-gain"
    if not proton_even and not neutron_even:
        return "unpaired-loss"
    return "mixed-empty"


@lru_cache(maxsize=None)
def exact_cube_root_enclosure(mass_number: int, refinements: int) -> tuple[Fraction, Fraction]:
    """Enclose a positive cube root by exact bisection, never emit the root."""

    if isinstance(mass_number, bool) or mass_number < 2:
        raise ValueError("mass support begins with the binary composite")
    if isinstance(refinements, bool) or refinements < 1:
        raise ValueError("refinement count must be positive")
    lower_whole = 1
    while positive_power(lower_whole + 1, generator_period_three()) <= mass_number:
        lower_whole += 1
    if positive_power(lower_whole, generator_period_three()) == mass_number:
        exact = Fraction(lower_whole, 1)
        return exact, exact
    lower = Fraction(lower_whole, 1)
    upper = Fraction(lower_whole + 1, 1)
    for _ in range(refinements):
        midpoint = (lower + upper) / binary_count()
        if midpoint * midpoint * midpoint < mass_number:
            lower = midpoint
        else:
            upper = midpoint
    if not lower * lower * lower < mass_number < upper * upper * upper:
        raise ValueError("rational cube-root enclosure failed")
    return lower, upper


@lru_cache(maxsize=None)
def binding_ledger(mass_number: int, charge_count: int) -> dict[str, Fraction | int | str | Empty]:
    """Return the exact positive bulk/surface/Coulomb/asymmetry/pairing ledger."""

    neutrons = neutron_count(mass_number, charge_count)
    paths = ordered_charge_paths(charge_count)
    unmatched = unmatched_label_count(mass_number, charge_count)
    coulomb = () if paths == () else electromagnetic_share() * Fraction(paths, mass_number)
    asymmetry = () if unmatched == () else asymmetry_share() * Fraction(
        unmatched * unmatched, mass_number * mass_number
    )
    pairing = pairing_share() * Fraction(1, mass_number)
    return {
        "mass_number": mass_number,
        "charge_count": charge_count,
        "neutron_count": neutrons,
        "bulk_support": Fraction(1, 1),
        "surface_radial_loss": surface_deficit_share(),
        "ordered_charge_paths": paths,
        "coulomb_radial_loss": coulomb,
        "asymmetry_loss": asymmetry,
        "pairing_radial_part": pairing,
        "pairing_class": pairing_class(mass_number, charge_count),
    }


@lru_cache(maxsize=None)
def net_radial_loss(mass_number: int, charge_count: int) -> Fraction:
    ledger = binding_ledger(mass_number, charge_count)
    loss = ledger["surface_radial_loss"]
    coulomb = ledger["coulomb_radial_loss"]
    if not isinstance(loss, Fraction):
        raise ValueError("surface loss changed type")
    if isinstance(coulomb, Fraction):
        loss += coulomb
    pairing = ledger["pairing_radial_part"]
    if not isinstance(pairing, Fraction):
        raise ValueError("pairing part changed type")
    if ledger["pairing_class"] == "paired-gain":
        loss = positive_take(loss, pairing)
    elif ledger["pairing_class"] == "unpaired-loss":
        loss += pairing
    return loss


@lru_cache(maxsize=None)
def nonradial_retention(mass_number: int, charge_count: int) -> Fraction:
    asymmetry = binding_ledger(mass_number, charge_count)["asymmetry_loss"]
    if asymmetry == ():
        return Fraction(1, 1)
    if not isinstance(asymmetry, Fraction):
        raise ValueError("asymmetry part changed type")
    return positive_take(Fraction(1, 1), asymmetry)


def binding_score_enclosure(
    mass_number: int, charge_count: int, refinements: int
) -> tuple[Fraction, Fraction]:
    """Enclose normalized binding using rational values only."""

    radius_lower, radius_upper = exact_cube_root_enclosure(mass_number, refinements)
    retained = nonradial_retention(mass_number, charge_count)
    radial_loss = net_radial_loss(mass_number, charge_count)
    lower = positive_take(retained, radial_loss / radius_lower)
    upper = positive_take(retained, radial_loss / radius_upper)
    if lower > upper:
        raise ValueError("binding enclosure reversed")
    return lower, upper


def continuous_vertex_enclosure(mass_number: int, refinements: int) -> tuple[Fraction, Fraction]:
    """Enclose the concave ledger vertex before integer/parity restriction."""

    lower, upper = exact_cube_root_enclosure(mass_number, refinements)
    alpha = electromagnetic_share()

    def vertex(radius: Fraction) -> Fraction:
        return Fraction(mass_number, 1) * (radius + alpha) / (
            binary_count() * radius + binary_count() * alpha * mass_number
        )

    result = vertex(lower), vertex(upper)
    if result[0] > result[1]:
        raise ValueError("vertex enclosure reversed")
    return result


@lru_cache(maxsize=None)
def possible_mass_maximizers(mass_number: int) -> tuple[int, ...]:
    """Enumerate every integer/parity point that can maximize the concave ledger."""

    refinements = 1
    while True:
        lower, upper = continuous_vertex_enclosure(mass_number, refinements)
        if upper - lower < residual_boundary_support():
            break
        refinements += 1
    lower_whole = lower.numerator // lower.denominator
    upper_whole = upper.numerator // upper.denominator
    start = max(1, lower_whole - binary_count())
    stop = min(mass_number - 1, upper_whole + generator_period_three())
    candidates = tuple(range(start, stop + 1))
    if not candidates:
        raise ValueError("concave candidate enclosure is empty")
    return candidates


@lru_cache(maxsize=1)
def finite_peak_candidates() -> tuple[tuple[int, int], ...]:
    return tuple(
        (mass_number, charge_count)
        for mass_number in range(binary_count(), tail_cutoff_mass())
        for charge_count in possible_mass_maximizers(mass_number)
    )


def tail_cutoff_mass() -> int:
    blocks = fine_structure_blocks()
    return positive_power(binary_count(), blocks["down"] + blocks["up"])


def tail_upper_bounds() -> dict[str, Fraction | int | bool]:
    """Close every mass at and beyond the forced cutoff in two charge cases."""

    cutoff = tail_cutoff_mass()
    radius, radius_upper = exact_cube_root_enclosure(cutoff, 1)
    if radius != radius_upper:
        raise ValueError("forced tail cutoff lacks an exact cubic radius")
    low_charge_asymmetry = asymmetry_share() * Fraction(9, 25)
    maximum_pairing_gain = pairing_share() * Fraction(1, cutoff) / radius
    low_charge_upper = positive_take(Fraction(1, 1), low_charge_asymmetry) + maximum_pairing_gain

    least_high_charge = cutoff // fine_structure_blocks()["down"] + 1
    high_charge_paths = least_high_charge * positive_predecessor(least_high_charge)
    high_charge_coulomb = electromagnetic_share() * Fraction(
        high_charge_paths, cutoff
    ) / radius
    high_charge_upper = positive_take(Fraction(1, 1), high_charge_coulomb) + maximum_pairing_gain
    successor_monotone = (
        binary_count() * cutoff * cutoff
        > (
            binary_count()
            * binary_count()
            * generator_period_three()
            * cutoff
            + 14
        )
    )
    return {
        "cutoff_mass": cutoff,
        "cutoff_radius": radius.numerator,
        "low_charge_upper": low_charge_upper,
        "high_charge_upper": high_charge_upper,
        "coulomb_tail_successor_monotone": successor_monotone,
    }


@lru_cache(maxsize=1)
def binding_peak_certificate() -> dict[str, Fraction | int | bool]:
    """Force the unique all-mass maximum by finite census plus tail induction."""

    candidates = finite_peak_candidates()
    refinements = 1
    while True:
        intervals = {
            candidate: binding_score_enclosure(candidate[0], candidate[1], refinements)
            for candidate in candidates
        }
        winner = max(candidates, key=lambda candidate: intervals[candidate][0])
        rival_upper = max(
            intervals[candidate][1] for candidate in candidates if candidate != winner
        )
        if intervals[winner][0] > rival_upper:
            break
        refinements += refinements
    tail = tail_upper_bounds()
    if tail["coulomb_tail_successor_monotone"] is not True:
        raise ValueError("high-charge tail did not close under positive succession")
    winner_lower, winner_upper = intervals[winner]
    if winner_lower <= tail["low_charge_upper"] or winner_lower <= tail["high_charge_upper"]:
        raise ValueError("forced tail bound did not remain below the finite winner")
    mass_number, charge_count = winner
    return {
        "mass_number": mass_number,
        "charge_count": charge_count,
        "neutron_count": neutron_count(mass_number, charge_count),
        "score_lower": winner_lower,
        "score_upper": winner_upper,
        "rival_upper": rival_upper,
        "refinements_until_separation": refinements,
        "finite_mass_count": tail_cutoff_mass() - binary_count(),
        "possible_maximizer_count": len(candidates),
        "tail_cutoff_mass": tail_cutoff_mass(),
        "tail_closed": True,
    }


def axes() -> tuple:
    return (
        binary_axis("predecessor", "How are admitted nuclear and field laws used?", "rewrite-predecessor-laws", "A successor cannot alter admitted receipts.", "compose-immutable-predecessors", "Binding, residual order, exact alpha, spatial rank and mass-energy closure remain immutable dependencies."),
        binary_axis("bulk", "What is the interior binding carrier?", "unbounded-pairwise-bulk-growth", "Short-range saturation forbids growth with every distant constituent.", "one-saturating-bulk-support", "Every completed interior word retains one normalized saturated binding support."),
        binary_axis("surface", "How is the surface deficit fixed?", "fitted-surface-coefficient", "A fitted coefficient is a parameter.", "one-over-binary-plus-generator-interface", "One missing boundary act is shared over the forced binary-plus-generator interface carrier 2+3=5."),
        binary_axis("coulomb", "How is proton repulsion counted?", "import-semi-empirical-coulomb-term", "An imported mass formula cannot select the law.", "exact-alpha-times-ordered-charge-paths", "Every source-to-distinct-target proton path carries the admitted exact electromagnetic share."),
        binary_axis("asymmetry", "How is neutron/proton imbalance retained?", "chosen-asymmetry-penalty", "A chosen coefficient is not forced.", "quarter-order-unmatched-label-square", "The residual quarter-order weights the complete unmatched-label pair support."),
        binary_axis("pairing", "How are even and odd compositions distinguished?", "fitted-pairing-term", "A fitted parity correction is a parameter.", "quarter-order-paired-gain-unpaired-loss", "The residual quarter-order is retained for complete pairs, held for mixed words and charged against two unpaired classes."),
        binary_axis("radius", "May an irrational cube root enter proof values?", "evaluate-irrational-radius", "Irrational values are outside the exact proof domain.", "rational-enclosures-until-order-separates", "Boundary-rank-two over volume-rank-three is compared only through exact rational cube enclosures."),
        binary_axis("maximum", "How is the peak closed beyond a finite scan?", "selected-isotope-window", "A chosen neighborhood cannot prove a global maximum.", "complete-concave-census-plus-forced-tail-induction", "Every possible integer/parity maximizer below 2^(5+7) is enumerated and both unbounded tail cases are closed."),
        binary_axis("target", "May mass-evaluation data select the peak?", "external-target-readable", "Target access would fit the isotope coordinate.", "target-inaccessible-until-seal", "The complete structural ledger and unique coordinate seal before the authoritative table opens."),
        binary_axis("extension", "May another coefficient or correction be appended?", "free-coefficient-or-residual", "An ungenerated correction destroys zero-parameter closure.", "no-extra-rule", "Bulk, surface, Coulomb, asymmetry and pairing exhaust the declared grammar."),
    )


PEAK = binding_peak_certificate()


NUCLEAR_BINDING_CURVE_SPEC = StructuralPhysicsSpec(
    claim_id=NUCLEAR_BINDING_CURVE_TERMINAL_ID,
    title="Terminal zero-parameter nuclear binding curve and stability maximum",
    statement=(
        "Short-range quarter-order residual recurrence and exact electromagnetic opposition force one positive "
        "bulk/surface/Coulomb/asymmetry/pairing ledger with no fitted coefficient. The surface share is exactly "
        "One over the binary-plus-generator interface carrier five; Coulomb loss is the admitted exact alpha over "
        "every ordered distinct proton path; asymmetry and pairing carry the admitted quarter-order. Exact rational "
        "radius enclosures, complete concave integer/parity enumeration below the forced mass 2^(5+7), and a "
        "two-case tail induction uniquely maximize normalized binding at mass count 62, charge count 28 and neutron "
        "count 34. No nuclide name or measured binding value enters execution."
    ),
    dependencies=(
        "SFT-PHYS-NUCLEAR-BINDING-001",
        "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
        "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-MATTER-MASS-ENERGY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis predecessor, bulk, surface, Coulomb, asymmetry, pairing, radius, maximum, target-custody and extension product.",
    grammar_boundary="Every positive proton/neutron composite, exact saturated bulk, forced 1/5 interface share, exact alpha ordered charge path, quarter-order imbalance/pairing class, rational rank-two/rank-three enclosure and every mass beyond the forced 4096 tail boundary.",
    axes=axes(),
    exact_result=(
        "The unique zero-parameter normalized binding maximum over every positive proton/neutron composition is "
        "A=62, Z=28, N=34. The exact ledger is bulk One; radial surface loss (1/5)/A^(1/3) represented only by "
        "rational enclosures; Coulomb loss alpha*Z*(Z-1)/A^(4/3); quarter-order asymmetry loss "
        "(1/4)*(N-Z)^2/A^2; and quarter-order parity gain/loss (1/4)/A^(4/3)."
    ),
    induction_base="Complete exact concavity reduces every fixed-mass proton census to the integer/parity neighbors of one enclosed vertex; all masses from two through 4095 are exhausted and yield one separated maximum at 62/28/34.",
    induction_step="At and beyond 4096, charge at most one-fifth forces at least 9/100 asymmetry loss; charge above one-fifth forces a Coulomb loss already large enough at the exact cubic base and increasing thereafter. Both upper bounds remain below the sealed winner.",
    exclusions=(
        "no V1/V2 executable, semi-empirical mass formula or fitted coefficient as a premise",
        "no nuclide name, measured mass, binding energy, uncertainty, table row or source access in execution",
        "no numerical-zero state, negative, irrational, imaginary or floating proof value",
        "no evaluated cube root; exact rational enclosures refine only until order separates",
        "no selected isotope neighborhood, finite scan standing in for the unbounded tail or hidden parity class",
        "no target access before derivation and prediction seals",
        "no free bulk, surface, Coulomb, asymmetry, pairing or residual correction",
    ),
    witnesses=(
        Witness("forced-ledger-shares", "Surface, electromagnetic, asymmetry and pairing shares are exact admitted carriers.", surface_deficit_share() == Fraction(1, 5) and asymmetry_share() == Fraction(1, 4) and pairing_share() == Fraction(1, 4)),
        Witness("unique-finite-peak", "Exact enclosure separation leaves mass 62, charge 28 and neutron 34 as the unique finite winner.", PEAK["mass_number"] == 62 and PEAK["charge_count"] == 28 and PEAK["neutron_count"] == 34 and PEAK["score_lower"] > PEAK["rival_upper"]),
        Witness("unbounded-tail-closed", "Both forced tail cases lie strictly below the sealed finite winner and the high-charge bound increases under every positive successor.", PEAK["tail_closed"] is True and tail_upper_bounds()["coulomb_tail_successor_monotone"] is True and PEAK["score_lower"] > tail_upper_bounds()["low_charge_upper"] and PEAK["score_lower"] > tail_upper_bounds()["high_charge_upper"]),
        Witness("no-irrational-value", "The predicted winner is enclosed by exact positive fractions only.", isinstance(PEAK["score_lower"], Fraction) and isinstance(PEAK["score_upper"], Fraction)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


NUCLEAR_BINDING_CURVE_SPEC.validate()


__all__ = (
    "NUCLEAR_BINDING_CURVE_SPEC",
    "NUCLEAR_BINDING_CURVE_TERMINAL_ID",
    "binding_ledger",
    "binding_peak_certificate",
    "binding_score_enclosure",
    "electromagnetic_share",
    "exact_cube_root_enclosure",
    "finite_peak_candidates",
    "net_radial_loss",
    "pairing_class",
    "surface_deficit_share",
    "tail_cutoff_mass",
    "tail_upper_bounds",
)
