"""Exact prime-sector interaction table and common standing-mode law."""

from __future__ import annotations

from fractions import Fraction
from math import gcd

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025"
ONE = Fraction(1, 1)
HALF = Fraction(1, 2)
PRIME_SECTORS = (2, 3, 5, 7)


def standing_modes(sector: int) -> tuple[Fraction, ...]:
    if isinstance(sector, bool) or sector < 2:
        raise ValueError("standing modes require a generated sector count")
    return tuple(Fraction(index, sector - 1) for index in range(1, sector - 1))


def common_half_one_sectors() -> tuple[int, ...]:
    return tuple(sector for sector in PRIME_SECTORS if HALF in standing_modes(sector))


def base_sector_table(sector: int) -> dict[str, object]:
    if sector not in PRIME_SECTORS:
        raise ValueError("the terminal interaction table uses the complete forced prime-sector ladder")
    return {
        "sector": sector,
        "coupling": Fraction(sector - 1, sector),
        "mixing_share": Fraction(1, sector - 1),
        "mass_shortfall": Fraction(1, sector),
        "mediator_count": sector * sector - 1,
        "standing_modes": standing_modes(sector),
        "half_One_standing": HALF in standing_modes(sector),
    }


def running_share(sector: int, support: int) -> Fraction:
    if sector not in PRIME_SECTORS or isinstance(support, bool) or support < 1:
        raise ValueError("running share requires a forced sector and positive support")
    source = sector + support
    return Fraction(source - 1, source)


def running_shortfall(sector: int, support: int) -> Fraction:
    return ONE - running_share(sector, support)


def running_gap(lower: int, upper: int, support: int) -> Fraction:
    if not (lower in PRIME_SECTORS and upper in PRIME_SECTORS and lower < upper):
        raise ValueError("running gap requires ordered forced sectors")
    return running_share(upper, support) - running_share(lower, support)


def fold_part(value: Fraction) -> Fraction:
    doubled = value + value
    return doubled if doubled <= ONE else doubled - ONE


def period(value: Fraction) -> int:
    current = value
    count = 0
    while True:
        current = fold_part(current)
        count += 1
        if current == value:
            return count


def period_dictionary() -> dict[str, int]:
    gravity = period(ONE)
    electromagnetic = period(Fraction(1, 3))
    strong = period(Fraction(1, 7))
    joint = gravity * electromagnetic * strong // gcd(gravity, gcd(electromagnetic, strong))
    return {
        "gravity": gravity,
        "electromagnetic": electromagnetic,
        "strong": strong,
        "joint": joint,
    }


def all_depth_order_and_noncoincidence(depth: int) -> bool:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("common-support order requires positive depth")
    support = 2 ** (depth - 1)
    shares = tuple(running_share(sector, support) for sector in PRIME_SECTORS)
    return all(shares[index] < shares[index + 1] for index in range(len(shares) - 1)) and len(set(shares)) == len(shares) and all(running_gap(lower, upper, support) > 0 for lower, upper in zip(PRIME_SECTORS, PRIME_SECTORS[1:]))


def prior_flat_slope_bundle_is_consistent() -> bool:
    """V2 243 simultaneously states slope=m-1 and slope(2)=0."""

    formula_at_two = 2 - 1
    asserted_at_two = 0
    return formula_at_two == asserted_at_two


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Prime-sector standing-mode, interaction and period unification",
    statement=(
        "The complete prime-sector ladder two, three, five and seven is governed by "
        "one exact table.  Sector m has holding coupling (m-1)/m, positive mass "
        "shortfall 1/m, mixing share 1/(m-1), m-squared take One mediators and "
        "interior standing modes j/(m-1).  Half-One is the unique self-antipodal "
        "standing mode common to every odd prime sector and is absent from the "
        "fundamental two-sector interior.  On common positive support R, every "
        "sector has holding share (m+R-1)/(m+R); exact positive pair gaps preserve "
        "strict sector order and forbid finite triple coincidence while shrinking "
        "under every support successor.  The Fold period dictionary is gravity one, "
        "electromagnetism two, strong three and joint recurrence six.  The prior "
        "bundle claiming both slope m-1 and an abelian slope of zero is internally "
        "inconsistent and is rejected; the admitted terminal running laws replace it."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-STRONG-RUNNING-DIRECTION-002",
        "SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003",
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003",
        "SFT-PHYS-VALIDATION-VACUUM-POLARIZATION-003",
        "SFT-MATH-ORBIT-NUMBER-THEORY-002",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of sector domain, standing-mode carrier, "
        "coupling table, mass relation, common support, sector order, coincidence "
        "boundary, period dictionary, empirical succession and extension forms."
    ),
    grammar_boundary=(
        "Every forced prime sector through seven, every interior standing mode, "
        "every positive binary common-support successor, every ordered sector pair, "
        "the exact Fold periods of One, one-third and one-seventh, and the already "
        "sealed complete force/running comparison records."
    ),
    axes=(
        binary_axis("sector", "Which interaction sectors enter?", "selected-familiar-sectors", "Selection omits generated prime sectors or the exclusion boundary.", "complete-prime-ladder-through-seven", "The forced cover ceiling retains exactly two, three, five and seven."),
        binary_axis("standing", "What unifies odd sectors?", "named-unification-point", "A name does not prove membership or uniqueness.", "unique-self-antipodal-half-One-mode", "Complete interior-mode enumeration places half-One in every odd sector and nowhere else as a self-antipode."),
        binary_axis("table", "How are sector relations generated?", "independent-fitted-couplings", "Independent values violate the one-generator law.", "single-m-indexed-exact-table", "Coupling, mixing, mass shortfall and mediator count are all exact functions of m."),
        binary_axis("mass", "What is the rest carrier?", "inserted-mass-parameter", "An inserted mass is not forced by the holding relation.", "positive-shortfall-from-unison", "The mass carrier is exactly the positive share required to reassemble the One."),
        binary_axis("support", "How do sectors run together?", "independent-scale-axes", "Independent axes cannot define exact separation or convergence.", "common-positive-binary-support", "Every sector receives the same generated support R and keeps its identity m."),
        binary_axis("order", "What orders sector shares?", "target-named-physical-order", "A physical label cannot choose an inequality.", "exact-positive-m-difference-gap", "For lower m and upper n the gap is (n-m)/((m+R)(n+R)), always positive."),
        binary_axis("coincidence", "Can finite sectors exactly coincide?", "asserted-unification-crossing", "A crossing contradicts the positive pair-gap identity.", "finite-triple-coincidence-forbidden", "Every finite pair gap is positive although all gaps shrink by successor."),
        binary_axis("period", "How are gravity, EM and strong recurrences related?", "selected-force-periods", "Selected labels provide no Fold traces.", "complete-one-two-three-period-dictionary", "Exact first-return traces give periods one, two and three and joint recurrence six."),
        binary_axis("comparison", "Which physical running record is retained?", "flat-EM-and-inconsistent-slope-bundle", "It conflicts internally and with admitted electromagnetic running.", "terminal-carrier-specific-running-and-anchors", "The sealed strong/EM directions and complete force-sector anchors replace the adverse bundle."),
        binary_axis("extension", "May another unification rule enter?", "free-group-or-crossing-scale", "An added group or fitted crossing scale is a free premise.", "no-extra-rule", "Standing modes, sector table, support and period traces exhaust the grammar."),
    ),
    exact_result=(
        "The forced sectors (2,3,5,7) share one exact m-indexed interaction table; "
        "half-One uniquely unifies the odd-sector standing modes; all finite common-"
        "support sector gaps are positive and shrink without finite coincidence; "
        "the gravity/EM/strong Fold periods are 1/2/3 with joint recurrence 6; and "
        "the inconsistent flat-EM slope bundle is rejected in favour of the sealed "
        "terminal carrier-specific running laws."
    ),
    induction_base=(
        "At support One, complete prime-sector enumeration yields four exact table "
        "rows, strictly ordered holding shares and positive pair gaps."
    ),
    induction_step=(
        "Replacing support R by twice R preserves each sector identity, keeps every "
        "pair gap positive and reduces its denominator-controlled magnitude; "
        "standing modes and Fold periods are unchanged."
    ),
    exclusions=(
        "no imported gauge-unification group, beta function, coupling crossing or mass model",
        "no V1/V2 executable, answer table, measured target or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no physical-sector ordering substituted for the exact common-support m ordering",
        "no retention of the internally inconsistent slope=m-1 and slope(2)=0 bundle",
        "no target access before the inherited force-sector and running seals",
    ),
    witnesses=(
        Witness("complete-table", "The sector table yields couplings, mass shortfalls and mediator counts for all four forced primes.", tuple((base_sector_table(sector)["coupling"], base_sector_table(sector)["mass_shortfall"], base_sector_table(sector)["mediator_count"]) for sector in PRIME_SECTORS) == ((Fraction(1, 2), Fraction(1, 2), 3), (Fraction(2, 3), Fraction(1, 3), 8), (Fraction(4, 5), Fraction(1, 5), 24), (Fraction(6, 7), Fraction(1, 7), 48))),
        Witness("shared-half-One", "Half-One is present in every odd forced sector and absent from the two-sector interior.", common_half_one_sectors() == (3, 5, 7) and standing_modes(2) == ()),
        Witness("all-depth-order", "Every tested common-support depth retains strict order and no coincidence.", all(all_depth_order_and_noncoincidence(depth) for depth in range(1, 17))),
        Witness("period-dictionary", "Exact Fold traces yield gravity one, EM two, strong three and joint six.", period_dictionary() == {"gravity": 1, "electromagnetic": 2, "strong": 3, "joint": 6}),
        Witness("adverse-slope-bundle", "The prior simultaneous slope=m-1 and slope(2)=0 statements fail their own exact substitution.", not prior_flat_slope_bundle_is_consistent()),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "PRIME_SECTORS",
    "SPEC",
    "all_depth_order_and_noncoincidence",
    "base_sector_table",
    "common_half_one_sectors",
    "period_dictionary",
    "prior_flat_slope_bundle_is_consistent",
    "running_gap",
    "running_share",
    "running_shortfall",
    "standing_modes",
)
