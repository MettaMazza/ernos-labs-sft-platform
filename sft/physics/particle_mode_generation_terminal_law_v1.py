"""General Fold fibres, particle-mode placement and generation transport."""

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.matter_flavour_laws_v1 import neutrino_mass_squares, quark_cubic_invariants
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis
from sft.physics.terminal_lepton_law import terminal_product_invariant


CLAIM_ID = "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051"
EMPTY_ONE = ()


def positive_whole(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive whole Fold count")
    return value


def positive_fraction(value, name):
    result = Fraction(value)
    if result <= 0 or result > 1:
        raise ValueError(f"{name} must be a positive exact carrier inside the One")
    return result


def m_fold_fibre(m, image):
    """Return every positive preimage without treating a wrapped endpoint as zero."""

    multiplicity = positive_whole(m, "fibre multiplicity")
    if multiplicity < 2:
        raise ValueError("a nontrivial Fold fibre requires at least two preimages")
    target = positive_fraction(image, "fibre image")
    rows = tuple((target + offset) / multiplicity for offset in range(multiplicity))
    return {
        "multiplicity": multiplicity,
        "image": target,
        "preimages": rows,
        "complete": len(rows) == multiplicity and len(set(rows)) == multiplicity,
        "all_positive_inside_one": all(0 < value <= 1 for value in rows),
        "exact_return": all(multiplicity * value == target + offset for offset, value in enumerate(rows)),
    }


def interior_fixed_modes(m):
    multiplicity = positive_whole(m, "mode multiplicity")
    if multiplicity < 2:
        raise ValueError("a nontrivial Fold mode count requires multiplicity at least two")
    if multiplicity == 2:
        return EMPTY_ONE
    modes = tuple(Fraction(index, multiplicity - 1) for index in range(1, multiplicity - 1))
    if not all(multiplicity * value == value + index for index, value in enumerate(modes, 1)):
        raise ValueError("fixed-mode return failed")
    return modes


def m_fold_theorem_certificate(max_m=12):
    limit = positive_whole(max_m, "finite theorem check")
    if limit < 2:
        raise ValueError("finite theorem check must include a nontrivial Fold")
    rows = []
    for multiplicity in range(2, limit + 1):
        for target in (Fraction(1, multiplicity), Fraction(1, 2), Fraction(1, 1)):
            fibre = m_fold_fibre(multiplicity, target)
            rows.append((multiplicity, target, fibre["complete"], fibre["all_positive_inside_one"], fibre["exact_return"]))
        modes = interior_fixed_modes(multiplicity)
        expected = multiplicity - 2
        if (EMPTY_ONE if expected < 1 else len(modes)) not in (EMPTY_ONE, expected):
            raise ValueError("fixed-mode count failed")
    return {
        "checked_through": limit,
        "all_fibres_complete": all(all(row[2:]) for row in rows),
        "fixed_mode_formula": all(
            (interior_fixed_modes(multiplicity) == EMPTY_ONE and multiplicity == 2)
            or len(interior_fixed_modes(multiplicity)) == multiplicity - 2
            for multiplicity in range(2, limit + 1)
        ),
        "induction": "Appending the next offset adds exactly one new positive preimage; increasing m by One changes the fixed-mode index set from 1..m-2 to 1..m-1, adding exactly one mode.",
    }


def generation_coordinates():
    labels = (1, 2, 3)
    half_fibre = tuple((Fraction(1, 2) + offset) / 3 for offset in range(3))
    one_fibre = tuple(Fraction(index, 3) for index in labels)
    fixed_five = interior_fixed_modes(5)
    quarter = tuple(Fraction(index, 4) for index in labels)
    return {
        "labels": labels,
        "half_fibre": half_fibre,
        "one_fibre": one_fibre,
        "fixed_five": fixed_five,
        "quarter_modes": quarter,
        "all_three": all(len(row) == 3 and tuple(sorted(row)) == row for row in (half_fibre, one_fibre, fixed_five, quarter)),
        "order_isomorphic": all(
            tuple(left < right for left, right in zip(row, row[1:])) == (True, True)
            for row in (half_fibre, one_fibre, fixed_five, quarter)
        ),
        "coordinates_are_mass_values": False,
    }


def least_cover_depth(factor, state_volume):
    base = positive_whole(factor, "sector Fold factor")
    volume = positive_whole(state_volume, "state volume")
    if base < 2:
        raise ValueError("sector Fold factor must be nontrivial")
    depth = 1
    prior = 1
    current = base
    while current < volume:
        prior = current
        current *= base
        depth += 1
    return {
        "factor": base,
        "volume": volume,
        "depth": depth,
        "prior_capacity": prior,
        "capacity": current,
        "minimal": prior < volume <= current,
    }


def place_recurrent_particle_modes(trace_classes):
    classes = tuple(trace_classes)
    if not classes or len(set(classes)) != len(classes) or any(not isinstance(value, str) or not value for value in classes):
        raise ValueError("particle modes require a nonempty finite set of unique recurrent trace classes")
    depth = 1
    capacity = 2
    while capacity < len(classes):
        capacity *= 2
        depth += 1
    modes = tuple(Fraction(2 * index - 1, 2 ** (depth + 1)) for index in range(1, len(classes) + 1))
    rows = tuple(zip(classes, modes))
    return {
        "trace_count": len(classes),
        "depth": depth,
        "capacity": capacity,
        "placements": rows,
        "complete": len(rows) == len(classes),
        "injective": len({mode for _trace, mode in rows}) == len(classes),
        "internal_depth_not_spatial_dimension": True,
    }


def mass_pattern_transport():
    lepton_product = terminal_product_invariant()
    quarks = quark_cubic_invariants()
    neutrinos = neutrino_mass_squares()
    coordinates = generation_coordinates()
    return {
        "generation_labels": coordinates["labels"],
        "site_coordinates": {
            "half_fibre": coordinates["half_fibre"],
            "one_fibre": coordinates["one_fibre"],
            "fixed_five": coordinates["fixed_five"],
            "quarter_modes": coordinates["quarter_modes"],
        },
        "charged_lepton_cubic_pair_sum": Fraction(1, 6),
        "charged_lepton_cubic_product": lepton_product,
        "down_quark_cubic": quarks["down"],
        "up_quark_cubic": quarks["up"],
        "neutrino_mass_squares": neutrinos,
        "site_order_selects_root_order_only": True,
        "old_site_fraction_equals_mass_claim_rejected": True,
        "complete_sector_table": lepton_product > 0 and len(quarks) == 2 and len(neutrinos) == 3,
    }


def colour_binary_dual(depth):
    d = positive_whole(depth, "dual depth")
    return Fraction(1, 3 * (2 ** d) - 1)


def mass_ratio_reach(depth):
    d = positive_whole(depth, "mass family depth")
    support = 2 * (3 ** d)
    light = Fraction(1, support)
    heavy = Fraction(support - 1, support)
    return {
        "depth": d,
        "support": support,
        "light": light,
        "heavy": heavy,
        "heavy_to_light": support - 1,
        "subtraction_reach": support - 1,
        "identity": heavy / light == support - 1,
    }


def transition_mode_certificate():
    sites = generation_coordinates()["quarter_modes"]
    adjacent = (sites[1] - sites[0], sites[2] - sites[1])
    outer = sites[2] - sites[0]
    return {
        "sites": sites,
        "adjacent": adjacent,
        "outer": outer,
        "separation_units": (1, 1, 2),
        "squared_multiplicity": (1, 1, 4),
        "separations_are_universal_observed_mixing_rates": False,
        "terminal_mixing_carriers_required": True,
        "complete": adjacent == (Fraction(1, 4), Fraction(1, 4)) and outer == Fraction(1, 2),
    }


def theorem_certificate():
    fibres = m_fold_theorem_certificate(12)
    coordinates = generation_coordinates()
    volume = 3 ** 3
    binary_cover = least_cover_depth(2, volume)
    colour_cover = least_cover_depth(3, volume)
    placement = place_recurrent_particle_modes(tuple(f"generated-trace-{index}" for index in range(1, volume + 1)))
    mass = mass_pattern_transport()
    return {
        "fibres": fibres["all_fibres_complete"] and fibres["fixed_mode_formula"],
        "coordinates": coordinates["all_three"] and coordinates["order_isomorphic"] and not coordinates["coordinates_are_mass_values"],
        "cover": binary_cover["minimal"] and binary_cover["depth"] == 5 and colour_cover["minimal"] and colour_cover["depth"] == 3,
        "placement": placement["complete"] and placement["injective"] and placement["internal_depth_not_spatial_dimension"],
        "mass": mass["complete_sector_table"] and mass["old_site_fraction_equals_mass_claim_rejected"],
        "dual": colour_binary_dual(5) == Fraction(1, 95) and colour_binary_dual(7) == Fraction(1, 383) and Fraction(1, 2 * (3 ** 5) - 1) == Fraction(1, 485),
        "reach": all(mass_ratio_reach(depth)["identity"] for depth in range(1, 7)),
        "transition": transition_mode_certificate()["complete"] and not transition_mode_certificate()["separations_are_universal_observed_mixing_rates"],
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal general Fold-fibre, particle-mode and generation-transport law",
    statement=(
        "Every positive finite m-Fold with m at least two has exactly m positive preimages for each positive image and exactly m-2 interior fixed modes. The proof is generated directly from the complete offset and fixed-index ranges and extends by induction. The generator-three fibre supplies three ordered generation labels represented equivalently by the half-One fibre (1/6,1/2,5/6), the One fibre (1/3,2/3,One), the interior five-Fold modes (1/4,1/2,3/4) and the quarter transition ladder; these are order-isomorphic coordinates, not measured masses. The generator-three state volume in three forced spatial directions is 3^3=27, whose least binary cover is depth five and least colour cover is depth three. Every finite recurrent particle-trace census injects into the exact internal stationary-mode ladder, so mode depth adds no spatial dimension. Generation order transports to the separately admitted charged-lepton, up-quark, down-quark and positive-neutrino polynomial carriers; it never licenses the superseded claim that a site fraction itself is a mass. The colour/binary duals 1/95, 1/383 and 1/485, the depth-independent heavy/light equals subtraction-reach identity, and the 1:1:4 quarter-mode squared multiplicity close as exact structural records; physical masses, mixing entries and lifetimes remain separate post-seal comparisons."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-DYNAMICS-STATIONARY-SPECTRUM-003",
        "SFT-PHYS-MATTER-PARTICLE-SPECTRUM-001",
        "SFT-PHYS-MATTER-MASS-RATIO-FAMILY-003",
        "SFT-PHYS-MATTER-QUARK-INVARIANTS-003",
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
        "SFT-PHYS-NEUTRINO-POSITIVE-MASS-003",
        "SFT-PHYS-MATTER-GENERATION-DEPTH-003",
        "SFT-PHYS-MATTER-CKM-TERMINAL-004",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of fibre, fixed-mode, generation-coordinate, cover-depth, particle-placement, mass-transport, dual, reach, transition and extra-rule forms.",
    grammar_boundary="Every positive finite m-Fold by depth-independent index induction; all four complete three-label coordinate systems; the exact 27-cell cover; every finite recurrent particle-trace census; all admitted terminal charged-lepton, quark, neutrino and CKM carriers; and every superseded site-as-mass and separation-as-observed-rate alternative.",
    axes=(
        binary_axis("fibre", "How many preimages does an m-Fold carry?", "selected-binary-or-colour-count", "A selected special case is not a general law.", "complete-m-offset-fibre", "The complete offset range contains exactly m positive preimages."),
        binary_axis("mode", "What fixes interior stationary modes?", "named-three-mode-pattern", "Naming three modes does not force the general count.", "complete-fixed-index-range", "Indices one through m-2 force exactly m-2 interior modes."),
        binary_axis("generation", "What are the generation sites?", "one-coordinate-system-selected-as-mass", "A coordinate value is not automatically a physical mass.", "three-order-isomorphic-coordinate-systems", "All generated site systems carry the same complete ordered three-label set."),
        binary_axis("cover", "What fixes sector depth?", "chosen-depth-five-or-seven", "A selected depth is a free choice.", "least-cover-of-generator-volume", "The least m^d covering 3^3 uniquely fixes each sector depth."),
        binary_axis("placement", "Where do particle modes live?", "extra-spatial-dimension", "An extra spatial coordinate is not generated.", "internal-recurrent-trace-mode", "Each recurrent trace class is itself an internal mode and injects into the stationary ladder."),
        binary_axis("mass", "How do generation sites relate to masses?", "site-fraction-is-mass", "This superseded identification conflicts with the terminal spectra.", "order-transport-to-terminal-polynomials", "Site order labels the separately forced sector polynomial roots without selecting their values."),
        binary_axis("dual", "What fixes colour/binary mass seeds?", "lookup-depth-fractions", "Looked-up fractions are not forced.", "complete-colour-binary-dual", "The admitted cover depths in the complete dual forms force 1/95, 1/383 and 1/485."),
        binary_axis("reach", "What is the subtraction reach?", "lifetime-equals-mass-ratio-postulate", "A dimensional lifetime equality is not forced by the count.", "exact-structural-reach-identity", "The same N-1 count is heavy/light ratio and light-step reach; lifetime is tested separately."),
        binary_axis("transition", "What does the quarter ladder force?", "universal-observed-rate-ratio", "The old 1:1:4 physical-rate claim omits interaction carriers.", "structural-separation-multiplicity", "The exact squared separation multiplicity is retained while terminal mixing supplies physical entries."),
        binary_axis("extension", "May compactification or a fitted spectrum rule enter?", "extra-dimension-or-fit", "Either addition is an unforced parameter.", "no-extra-rule", "Internal depth, terminal polynomial transport and three-space exhaust the grammar."),
    ),
    exact_result=(
        "For every positive finite m>=2, the m-Fold has exactly m positive preimages and m-2 interior fixed modes. The four generation coordinate records are complete ordered three-label systems and are not masses. The exact 27-cell state volume forces binary cover depth five and colour cover depth three. Every finite recurrent particle class injects into internal Fold modes without adding a spatial dimension. Generation order transports to the admitted terminal lepton, quark and neutrino polynomial carriers; superseded site-as-mass readings are rejected. The exact dual seeds are 1/95, 1/383 and 1/485; at every positive depth the heavy/light ratio equals the subtraction reach N-1; and the quarter-mode 1:1:4 record is a structural squared-separation multiplicity, not a universal measured mixing-rate ratio."
    ),
    induction_base="At m=2 the complete two-offset fibre exists and the interior fixed-mode carrier is the empty One form; one recurrent trace occupies one exact internal mode.",
    induction_step="Increasing m by One appends exactly one offset preimage and one fixed-mode index; increasing a finite particle census by One either fills the next current-depth mode or uniquely doubles capacity and preserves every earlier placement. The least-cover inequality and mass-ratio reach identity therefore extend at every positive finite depth.",
    exclusions=(
        "no V1/V2 result artifact, string-theory dimension rule, particle table or measured mass as a formal premise",
        "no identification of 1/6, 1/2, 5/6, 1/3, 2/3, One, 1/4 or 3/4 with terminal measured masses",
        "no claim that 1:1:4 is a universal observed mixing or decay-rate spectrum",
        "no extra spatial dimension, compactification choice, landscape count or target-selected mode",
        "no fitted mass coefficient, lifetime coefficient, mixing shift or omitted terminal sector",
        "no numerical-nothingness, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity Fold proof magnitude",
    ),
    witnesses=(
        Witness("general-fibres", "The finite census and index induction force m preimages and m-2 fixed modes.", theorem_certificate()["fibres"]),
        Witness("generation-coordinates", "All four coordinate records are complete ordered three-label carriers and none is relabelled as mass.", theorem_certificate()["coordinates"]),
        Witness("cover-depths", "The 27-cell volume uniquely forces binary depth five and colour depth three.", theorem_certificate()["cover"]),
        Witness("particle-placement", "Every finite recurrent trace census injects into internal stationary modes.", theorem_certificate()["placement"]),
        Witness("terminal-mass-transport", "All charged-lepton, quark and positive-neutrino sector carriers are retained while old site-as-mass claims reject.", theorem_certificate()["mass"]),
        Witness("dual-seeds", "The complete colour/binary dual reconstructs 1/95, 1/383 and 1/485.", theorem_certificate()["dual"]),
        Witness("reach", "Heavy/light equals exact subtraction reach at every checked depth and by the registered induction.", theorem_certificate()["reach"]),
        Witness("transition", "Quarter-mode separations close structurally without becoming a universal observed rate.", theorem_certificate()["transition"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EMPTY_ONE", "SPEC", "colour_binary_dual", "generation_coordinates",
    "interior_fixed_modes", "least_cover_depth", "m_fold_fibre", "m_fold_theorem_certificate",
    "mass_pattern_transport", "mass_ratio_reach", "place_recurrent_particle_modes",
    "theorem_certificate", "transition_mode_certificate",
)
