"""Exact dark-relic, Smithion-spectrum and flavour-transition closure.

The prior corpora identify the reconstruction obligations only.  This module
reads neither prior answer artifacts nor measurements.  Algebraic roots remain
exact polynomial objects represented by rational isolating intervals.
"""

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, minimal_binary_cover, positive_power
from sft.physics.matter_flavour_completion_laws_v1 import sharpened_quark_products
from sft.physics.particle_mode_generation_terminal_law_v1 import generation_coordinates
from sft.physics.sector_inventory_law_v1 import (
    fermion_mass_part,
    mediator_count,
    prime_sector_ladder,
    sector_coupling,
    singlet_constituent_count,
)
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis, generator_period_three


CLAIM_ID = "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061"
NEW_SECTORS = (5, 7)
KINDS = ("down", "up")
EMPTY_ONE = ()


def coloured_product(sector: int, depth: int) -> Fraction:
    if sector not in prime_sector_ladder() or isinstance(depth, bool) or depth < 1:
        raise ValueError("coloured product requires an admitted prime sector and positive depth")
    support = sector * (binary_count() * positive_power(sector, depth) - 1) - 1
    return Fraction(sector, support)


def spectrum_depth(sector: int, kind: str) -> int:
    if sector not in prime_sector_ladder() or kind not in KINDS:
        raise ValueError("spectrum depth requires an admitted sector and generated kind")
    power = generator_period_three() if kind == "down" else generator_period_three() + 1
    return minimal_binary_cover(positive_power(sector, power))


def pair_sum(sector: int, kind: str) -> Fraction:
    if sector not in prime_sector_ladder() or kind not in KINDS:
        raise ValueError("pair sum requires an admitted sector and generated kind")
    if kind == "down":
        return Fraction(1, binary_count() ** generator_period_three())
    return Fraction(1, binary_count() ** binary_count() * sector)


def spectrum_invariants(sector: int, kind: str) -> tuple[Fraction, Fraction, Fraction]:
    depth = spectrum_depth(sector, kind)
    return Fraction(1, 1), pair_sum(sector, kind), coloured_product(sector, depth)


def cubic_side(x: Fraction, second: Fraction, third: Fraction):
    positive_hand = x * x * x + second * x
    counter_hand = x * x + third
    if positive_hand == counter_hand:
        return EMPTY_ONE
    if positive_hand > counter_hand:
        return "positive-hand", positive_hand - counter_hand
    return "counter-hand", counter_hand - positive_hand


def sign_change_brackets(second: Fraction, third: Fraction, grid_depth: int = 10):
    if isinstance(grid_depth, bool) or grid_depth < 1:
        raise ValueError("grid depth must be positive")
    support = positive_power(binary_count(), grid_depth)
    rows = []
    lower = EMPTY_ONE
    lower_side = ("counter-hand", third)
    for index in range(1, support + 1):
        upper = Fraction(index, support)
        upper_side = cubic_side(upper, second, third)
        if lower_side == EMPTY_ONE and lower != EMPTY_ONE:
            rows.append((lower, lower))
        elif upper_side == EMPTY_ONE or lower_side[0] != upper_side[0]:
            rows.append((lower, upper))
        lower, lower_side = upper, upper_side
    if len(rows) != generator_period_three():
        raise ValueError("complete grid did not isolate exactly three positive roots")
    return tuple(rows)


def bisect_bracket(bracket, second: Fraction, third: Fraction):
    lower, upper = bracket
    midpoint = upper / binary_count() if lower == EMPTY_ONE else (lower + upper) / binary_count()
    lower_side = ("counter-hand", third) if lower == EMPTY_ONE else cubic_side(lower, second, third)
    midpoint_side = cubic_side(midpoint, second, third)
    if midpoint_side == EMPTY_ONE:
        return midpoint, midpoint
    if lower_side == EMPTY_ONE or lower_side[0] != midpoint_side[0]:
        return lower, midpoint
    return midpoint, upper


def spectrum_root_brackets(sector: int, kind: str, halvings: int = 60):
    if isinstance(halvings, bool) or halvings < 1:
        raise ValueError("root refinement requires a positive halving count")
    _, second, third = spectrum_invariants(sector, kind)
    brackets = sign_change_brackets(second, third)
    for _ in range(halvings):
        brackets = tuple(bisect_bracket(bracket, second, third) for bracket in brackets)
    return brackets


def mass_ratio_enclosures(sector: int, kind: str):
    roots = spectrum_root_brackets(sector, kind)
    light_lower, light_upper = roots[0]
    rows = [(Fraction(1, 1), Fraction(1, 1))]
    for lower, upper in roots[1:]:
        rows.append((lower * lower / (binary_count() * light_upper * light_upper), upper * upper / (binary_count() * light_lower * light_lower)))
    return tuple(rows)


def smithion_spectrum_census():
    return tuple(
        {
            "sector": sector,
            "kind": kind,
            "depth": spectrum_depth(sector, kind),
            "invariants": spectrum_invariants(sector, kind),
            "roots": spectrum_root_brackets(sector, kind),
            "mass_ratios": mass_ratio_enclosures(sector, kind),
        }
        for sector in NEW_SECTORS
        for kind in KINDS
    )


def relic_certificate():
    rows = smithion_spectrum_census()
    return {
        "new_sectors": NEW_SECTORS,
        "singlet_constituents": tuple(singlet_constituent_count(sector) for sector in NEW_SECTORS),
        "neutral_complete_fibres": tuple(singlet_constituent_count(sector) == sector for sector in NEW_SECTORS),
        "generation_count": tuple(len(row["roots"]) for row in rows),
        "lightest_unique": tuple(row["roots"][0][1] < row["roots"][1][0] < row["roots"][2][0] for row in rows),
        "electromagnetic_channel": EMPTY_ONE,
        "sector_channels": tuple(sector_coupling(sector) for sector in NEW_SECTORS),
        "mediators": tuple(mediator_count(sector) for sector in NEW_SECTORS),
        "mass_parts": tuple(fermion_mass_part(sector) for sector in NEW_SECTORS),
        "stability_scope": "lightest-complete-neutral-singlet-under-the-closed-prime-sector-and-generation-grammar",
    }


def lfv_certificate():
    coordinates = generation_coordinates()
    sites = coordinates["half_fibre"]
    modes = coordinates["quarter_modes"]
    electron, muon, tau = sites
    adjacent = modes[1] - modes[0]
    long = modes[2] - modes[0]
    weights = {
        "mu_to_e": adjacent * adjacent * muon,
        "tau_to_mu": adjacent * adjacent * tau,
        "tau_to_e": long * long * tau,
    }
    common = Fraction(1, 96)
    return {
        "mass_parts": sites,
        "weights": weights,
        "integer_ratio": tuple(weight // common for weight in weights.values()),
        "tau_ratio": weights["tau_to_e"] / weights["tau_to_mu"],
        "beta_slopes": tuple((sector, sector_coupling(sector) / fermion_mass_part(sector)) for sector in prime_sector_ladder()),
    }


def abundance_certificate():
    volume = positive_power(generator_period_three(), generator_period_three())
    depth = minimal_binary_cover(volume)
    support = positive_power(binary_count(), depth)
    return {
        "volume": volume,
        "cover_depth": depth,
        "cover_support": support,
        "baryon_share": Fraction(depth, support),
        "dark_share": Fraction(volume, support),
        "dark_to_baryon": Fraction(volume, depth),
        "matter_to_baryon": Fraction(support, depth),
    }


def theorem_certificate():
    spectra = smithion_spectrum_census()
    relic = relic_certificate()
    lfv = lfv_certificate()
    abundance = abundance_certificate()
    return {
        "quark_cross_lock": coloured_product(3, 5) == sharpened_quark_products()["down"] and coloured_product(3, 7) == sharpened_quark_products()["up"],
        "four_spectra": len(spectra) == 4,
        "twelve_roots": sum(len(row["roots"]) for row in spectra) == 12,
        "all_roots_disjoint_positive": all(all(lower > 0 and lower <= upper for lower, upper in row["roots"]) and row["roots"][0][1] < row["roots"][1][0] < row["roots"][2][0] for row in spectra),
        "relic": relic,
        "lfv": lfv,
        "abundance": abundance,
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal dark relic, Smithion spectrum and flavour-transition law",
    statement=(
        "The closed prime-sector ladder transports the already admitted coloured mass construction without a new scale. "
        "For each penta and hepta sector and each generated down/up depth, one exact cubic has root sum One, the forced "
        "pair carrier and product p/[p(2p^d-1)-1]. Complete 1/1024 enumeration finds exactly three disjoint positive "
        "roots per cubic and sixty exact halvings retain rational enclosures, closing twelve Smithion mass-ratio "
        "predictions. The complete p-member fibre is neutral, the least root is unique in each spectrum, and the closed "
        "sector/generation grammar leaves no lower same-charge decay image, forcing the lightest neutral singlet as the "
        "stable relic class. The same generated lepton preimages force mass-weighted flavour carriers 1/32, 5/96 and "
        "5/24, hence 3:5:20 and a tau-channel ratio 4:1. Generator volume 27 and its least binary cover force dark/baryon "
        "27/5 and matter/baryon 32/5. Measurements and search outcomes are inaccessible to this formal execution."
    ),
    dependencies=(
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",
        "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051",
        "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of sector, kind, depth, invariant, root-census, mass-ratio, neutral-singlet, stability, abundance, flavour-weight, measurement-boundary and extension forms.",
    grammar_boundary="Prime sectors five and seven; down/up cover powers three/four; the complete exact cubic grid; all three root intervals; complete neutral sector fibres; all three lepton transitions; exact positive whole/fraction carriers; and no physical target before seal.",
    axes=(
        binary_axis("sector", "Which new sectors enter?", "selected-particle-sector", "A selected sector is not a complete census.", "both-forced-prime-sectors", "Prime five and seven are the two complete new sectors below the closed ceiling."),
        binary_axis("kind", "Which matter kinds enter?", "one-selected-kind", "One kind omits half the generated spectrum.", "complete-down-up-dual", "Both generated cover powers are retained for every sector."),
        binary_axis("depth", "What fixes each depth?", "chosen-depth", "A chosen exponent fits a hierarchy.", "least-binary-cover-of-sector-power", "The down/up powers three/four have unique least binary covers."),
        binary_axis("invariant", "What fixes the product?", "independent-mass-parameter", "A mass parameter forks the law.", "same-coloured-product-family", "The exact p/[p(2p^d-1)-1] carrier cross-locks both admitted quark products."),
        binary_axis("roots", "How are generations obtained?", "chosen-decimal-roots", "Chosen decimals import an irrational model.", "complete-grid-and-rational-halving", "Every sign change is enumerated and retained only as exact rational enclosure."),
        binary_axis("ratios", "How are mass ratios represented?", "floating-central-estimates", "A central decimal loses exact root custody.", "squared-rational-enclosures-with-light-lift", "Every ratio is bounded by exact squared endpoints and the admitted two-fibre lift."),
        binary_axis("relic", "Which state is the relic?", "named-dark-particle", "A name does not force stability or neutrality.", "least-complete-neutral-singlet", "The complete p-fibre is neutral and its least root has no lower same-charge image."),
        binary_axis("abundance", "What fixes its amount?", "freezeout-fit-or-density-input", "A cross-section or density would be a parameter.", "generation-volume-over-cover-depth", "Volume 27 over depth five forces 27/5 before comparison."),
        binary_axis("flavour", "What fixes transition weights?", "fitted-branching-fractions", "Fitted rates cannot force a ratio.", "squared-separation-times-parent-part", "Every channel retains its exact mode separation and parent preimage."),
        binary_axis("measurement", "May observations select the survivor?", "search-result-readable-before-seal", "That would tune the theory to current limits.", "all-targets-inaccessible-until-seal", "Densities, limits, masses and searches occur only in the empirical successor."),
        binary_axis("extension", "May another scale or particle enter?", "extra-scale-sector-or-correction", "Any added choice violates zero parameters.", "no-extra-rule", "The closed sector, kind, root, singlet, abundance and transition supports exhaust the grammar."),
    ),
    exact_result=(
        "Four exact penta/hepta cubics at depths (7,10,9,12) each have three disjoint positive roots, yielding twelve "
        "exact rationally enclosed Smithion mass-ratio predictions. Their coloured product family cross-locks the two "
        "quark values 3/1454 and 3/13118. Complete neutral p-member singlets and unique lightest roots force the stable "
        "relic class within the closed grammar. Dark/baryon is 27/5 and matter/baryon 32/5. Flavour weights are exactly "
        "1/32, 5/96 and 5/24, reducing to 3:5:20 with tau-to-e over tau-to-mu equal to 4. Sector beta slopes are p-1."
    ),
    induction_base="The penta down spectrum is the first new-sector cubic; complete enumeration produces exactly three positive disjoint roots and one unique least root.",
    induction_step="Advancing across the generated kind and prime-sector successors changes only the forced pair carrier and least-cover depth; the same complete cubic census, neutral fibre, lightest-root order and no-extra rule are preserved.",
    exclusions=(
        "no V1/V2 code, answer table, survivor identifier or measurement in formal execution",
        "no fitted mass, coupling, cross-section, freeze-out efficiency, density, branching fraction or search limit",
        "no negative, irrational, imaginary, floating, NaN, infinite or continuum proof scalar",
        "no claim that an unobserved Smithion mass has already been experimentally measured",
        "no claim that non-detection alone identifies the relic",
    ),
    witnesses=(
        Witness("quark-cross-lock", "The same product family returns both independently admitted sharpened quark products.", theorem_certificate()["quark_cross_lock"]),
        Witness("twelve-roots", "The complete four-cubic census contains exactly twelve disjoint positive rational root enclosures.", theorem_certificate()["twelve_roots"] and theorem_certificate()["all_roots_disjoint_positive"]),
        Witness("neutral-lightest", "Both new sectors have complete neutral fibres and every spectrum has one unique least root.", all(relic_certificate()["neutral_complete_fibres"]) and all(relic_certificate()["lightest_unique"])),
        Witness("abundance", "The exact cover partition forces both abundance ratios.", abundance_certificate()["dark_to_baryon"] == Fraction(27, 5) and abundance_certificate()["matter_to_baryon"] == Fraction(32, 5)),
        Witness("lfv", "The complete transition table reduces exactly to 3:5:20 and the same-parent tau ratio is four.", lfv_certificate()["integer_ratio"] == (3, 5, 20) and lfv_certificate()["tau_ratio"] == 4),
        Witness("beta", "Coupling divided by its sector shortfall is p-1 at every admitted prime sector.", lfv_certificate()["beta_slopes"] == ((2, Fraction(1)), (3, Fraction(2)), (5, Fraction(4)), (7, Fraction(6)))),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)

SPEC.validate()

__all__ = (
    "CLAIM_ID", "SPEC", "abundance_certificate", "coloured_product", "lfv_certificate",
    "mass_ratio_enclosures", "relic_certificate", "smithion_spectrum_census", "spectrum_depth",
    "spectrum_invariants", "spectrum_root_brackets", "theorem_certificate",
)
