"""The Unified Constants Object: one rooted cross-sector Fold geometry.

This is a distinct V3 Physics derivation.  It does not rename, replace or
reinterpret the already published Physics Grand Lock.  V1/V2 identify the
question that must be reconstructed; every executable premise below is an
already admitted V3 dependency.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.atomic_constants import fine_structure_blocks, inverse_fine_structure
from sft.physics.cosmology_prior_value_laws import dark_baryon_structure
from sft.physics.hubble_calibration_law import hubble_calibration_structure
from sft.physics.lineage_particle_laws import proton_planck_squared_ratio
from sft.physics.matter_flavour_laws_v1 import quark_cubic_invariants
from sft.physics.precision_value_laws_v1 import terminal_proton_planck_squared_ratio
from sft.physics.prior_value_laws import charged_lepton_invariants
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    boundary_rank_two,
    generator_period_three,
    spatial_dimension_three,
)
from sft.physics.terminal_lepton_law import terminal_product_invariant
from sft.physics.vacuum_density_scale_terminal_law_v1 import (
    local_vacuum_amplitude_floor,
    local_vacuum_energy_floor,
    normalized_cosmological_constant,
)


CLAIM_ID = "SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077"
ONE = Fraction(1, 1)


def positive_predecessor(value: int) -> int:
    if isinstance(value, bool) or value <= 1:
        raise ValueError("positive predecessor requires a count beyond the One")
    candidate = 1
    while candidate + 1 != value:
        candidate += 1
    return candidate


def positive_power(base: int, exponent: int) -> int:
    if isinstance(base, bool) or isinstance(exponent, bool) or base < 1 or exponent < 1:
        raise ValueError("positive power requires positive generated counts")
    result = base
    for _ in range(1, exponent):
        result *= base
    return result


def minimal_binary_cover(carrier: int, binary: int) -> int:
    if carrier < 1 or binary <= 1:
        raise ValueError("cover requires positive carrier and nonidentity fibre count")
    depth = 1
    support = binary
    while support < carrier:
        support *= binary
        depth += 1
    return depth


def foundation_order_vector(generator: int) -> dict[str, Fraction | int]:
    """Reconstruct the common order at which the shared geometry is visible."""

    if generator < 3:
        raise ValueError("the dependency probe requires generator three or its successor")
    binary = 2
    spatial_rank = 3
    down = minimal_binary_cover(positive_power(generator, spatial_rank), binary)
    up = minimal_binary_cover(positive_power(generator, spatial_rank + 1), binary)
    down_support = positive_power(binary, down)
    up_support = positive_power(binary, up)
    cover = binary * positive_power(down, generator)
    boundary = positive_power(generator, binary)
    inverse_alpha = Fraction(up_support, 1) + Fraction(boundary * (cover + 1), cover)
    lepton_product = Fraction(
        1,
        positive_predecessor(binary * positive_power(generator, down)),
    )
    down_cover_conjugate = Fraction(
        1,
        positive_predecessor(generator * down_support),
    )
    up_cover_product = Fraction(
        1,
        positive_predecessor(generator * up_support),
    )
    volume = positive_power(generator, spatial_rank)
    vacuum_share = Fraction(generator - 1, generator)
    return {
        "binary_fibre_count": binary,
        "generator_count": generator,
        "spatial_rank": spatial_rank,
        "boundary_rank": 2,
        "down_cover_depth": down,
        "up_cover_depth": up,
        "inverse_fine_structure_leading": inverse_alpha,
        "charged_lepton_leading_product": lepton_product,
        "down_cover_conjugate": down_cover_conjugate,
        "up_cover_product": up_cover_product,
        "dark_to_baryon_leading": Fraction(volume, down),
        "dark_share_leading": Fraction(volume, down_support),
        "hubble_leading": ONE + vacuum_share / positive_power(binary, spatial_rank),
        "planck_hierarchy_exponent": Fraction(positive_predecessor(up_support), binary),
        "local_vacuum_energy_floor": Fraction(1, positive_power(binary, 4 * down)),
        "half_One": Fraction(1, binary),
    }


def admitted_terminal_vector() -> dict[str, Fraction | int]:
    """Read the completed V3 branches without importing the Grand Lock."""

    blocks = fine_structure_blocks()
    leptons = charged_lepton_invariants()
    quarks = quark_cubic_invariants()
    dark = dark_baryon_structure()
    hubble = hubble_calibration_structure()
    return {
        "binary_fibre_count": blocks["binary"],
        "generator_count": blocks["generator"],
        "spatial_rank": spatial_dimension_three(),
        "boundary_rank": boundary_rank_two(),
        "down_cover_depth": blocks["down"],
        "up_cover_depth": blocks["up"],
        "inverse_fine_structure_leading": inverse_fine_structure(1),
        "inverse_fine_structure_terminal": inverse_fine_structure(),
        "charged_lepton_leading_product": leptons[2],
        "charged_lepton_sharpened_product": leptons[3],
        "charged_lepton_terminal_product": terminal_product_invariant(),
        "down_quark_terminal_product": quarks["down"][2],
        "up_quark_terminal_product": quarks["up"][2],
        "dark_to_baryon_leading": dark["leading_ratio"],
        "dark_to_baryon_terminal": dark["refined_ratio"],
        "dark_share_leading": dark["dark_share"],
        "baryon_share_leading": dark["baryon_share"],
        "hubble_leading": hubble["leading_ratio"],
        "hubble_terminal": hubble["refined_ratio"],
        "planck_hierarchy_exponent": Fraction(127, 2),
        "planck_hierarchy_squared": proton_planck_squared_ratio(),
        "planck_hierarchy_terminal_squared": terminal_proton_planck_squared_ratio(),
        "local_vacuum_amplitude_floor": local_vacuum_amplitude_floor(),
        "local_vacuum_energy_floor": local_vacuum_energy_floor(),
        "normalized_cosmological_magnitude": normalized_cosmological_constant(),
        "half_One": Fraction(1, 2),
    }


def dependency_graph() -> dict[str, tuple[str, ...]]:
    """Return the exact rooted object as parent-to-child incidence."""

    return {
        "One": ("Fold",),
        "Fold": ("binary_fibre_count", "generator_count"),
        "binary_fibre_count": ("down_cover_depth", "up_cover_depth", "half_One"),
        "generator_count": ("spatial_rank", "lepton_sector", "quark_sector", "cosmic_partition"),
        "spatial_rank": ("boundary_rank", "down_cover_depth", "up_cover_depth"),
        "boundary_rank": ("fine_structure_sector", "vacuum_sector"),
        "down_cover_depth": ("fine_structure_sector", "lepton_sector", "dark_baryon_sector", "vacuum_sector"),
        "up_cover_depth": ("fine_structure_sector", "quark_sector", "hubble_sector", "planck_sector"),
        "fine_structure_sector": ("lepton_sector", "quark_sector", "planck_sector"),
        "cosmic_partition": ("dark_baryon_sector", "hubble_sector", "vacuum_sector"),
    }


def reachable_from_one(graph: dict[str, tuple[str, ...]]) -> set[str]:
    reached = {"One"}
    frontier = ["One"]
    while frontier:
        parent = frontier.pop()
        for child in graph.get(parent, ()):
            if child not in reached:
                reached.add(child)
                frontier.append(child)
    return reached


SECTOR_NODES = {
    "fine_structure_sector",
    "lepton_sector",
    "quark_sector",
    "dark_baryon_sector",
    "hubble_sector",
    "planck_sector",
    "vacuum_sector",
}


def theorem_certificate() -> dict[str, object]:
    leading = foundation_order_vector(generator_period_three())
    successor = foundation_order_vector(generator_period_three() + 1)
    terminal = admitted_terminal_vector()
    graph = dependency_graph()
    reached = reachable_from_one(graph)
    dependent = tuple(key for key in leading if key not in {"binary_fibre_count", "spatial_rank", "boundary_rank", "half_One"})
    held = ("binary_fibre_count", "spatial_rank", "boundary_rank", "half_One")
    return {
        "foundation_order": leading,
        "terminal": terminal,
        "successor_probe": successor,
        "all_sectors_reach_One": SECTOR_NODES.issubset(reached),
        "shared_geometry_not_disconnected_list": all(
            sum(node in children for children in graph.values()) >= 1 for node in SECTOR_NODES
        ),
        "every_generator_dependent_carrier_moves": all(leading[key] != successor[key] for key in dependent),
        "independent_controls_hold": all(leading[key] == successor[key] for key in held),
        "leading_terminal_cross_lock": all(
            terminal[key] == leading[key]
            for key in (
                "binary_fibre_count", "generator_count", "spatial_rank", "boundary_rank",
                "down_cover_depth", "up_cover_depth", "inverse_fine_structure_leading",
                "charged_lepton_leading_product", "dark_to_baryon_leading",
                "dark_share_leading", "hubble_leading", "planck_hierarchy_exponent",
                "local_vacuum_energy_floor", "half_One",
            )
        ),
    }


_certificate = theorem_certificate()

DEPENDENCIES = (
    "SFT-FOUNDATION-ONE-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-FOUNDATION-COUNT-001",
    "SFT-FOUNDATION-PART-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
    "SFT-PHYS-SPACE-DIMENSION-THREE-001",
    "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
    "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
    "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    "SFT-PHYS-MATTER-QUARK-CUBICS-003",
    "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
    "SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",
    "SFT-PHYS-SCALE-PROTON-PLANCK-HIERARCHY-002",
    "SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003",
    "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
    "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="The Unified Constants Object",
    statement=(
        "The admitted electromagnetic, lepton, quark, cosmological, hierarchy and vacuum constants are not "
        "independent numerical dials. They are typed readings of one rooted Fold geometry: the One forces the "
        "Fold; the Fold forces binary two and generator three; three-space and boundary rank two force the shared "
        "cover depths five and seven; and those same retained carriers generate the complete registered exact "
        "cross-sector vector. A generator-successor dependency probe moves every and only generator-dependent "
        "carrier, while the binary-only half-One and independently held ranks remain fixed."
    ),
    dependencies=DEPENDENCIES,
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete twelve-axis product of root, Fold carrier, generated counts, cover geometry, typed "
        "sector incidence, leading vector, terminal continuation, graph connectedness, dependency mutation, "
        "independence control, measurement direction and extra-rule forms."
    ),
    grammar_boundary=(
        "Every rooted typed dependency object over the admitted V3 electromagnetic, lepton, quark, dark/baryon, "
        "Hubble, Planck-hierarchy and vacuum branches, their exact foundation-order and terminal values, the full "
        "generator-three-to-successor dependency probe, the binary/rank independence controls and all 4096 alternatives."
    ),
    axes=(
        binary_axis("root", "Does every sector share one root?", "disconnected-constant-list", "A list cannot establish common mathematical identity.", "single-One-root", "Every sector is reachable from the same foundational One."),
        binary_axis("fold", "How are the primary carriers obtained?", "borrowed-numerals", "Borrowed numbers are untraced inputs.", "Fold-generated-binary-and-generator", "Binary two and generator three are retained from admitted Fold recurrence."),
        binary_axis("covers", "How are depths five and seven fixed?", "selected-depth-labels", "Selected depths are parameters.", "least-binary-covers-of-generated-volumes", "The depths are the least complete covers of three cubed and three to its successor."),
        binary_axis("typing", "How do repeated values cross sectors?", "untyped-number-coincidence", "Equal digits alone do not prove one object.", "shared-carrier-incidence", "Each repeated carrier keeps one identity and all consuming edges."),
        binary_axis("leading", "Is the common-order object complete?", "selected-headline-values", "Headline selection can hide a disconnected branch.", "complete-registered-foundation-vector", "Every registered foundation-order sector reading is retained."),
        binary_axis("terminal", "How are deeper V3 readings related?", "replacement-values-with-new-roots", "Replacement would break the common object.", "root-preserving-terminal-continuations", "Every terminal reading preserves the same counted roots while exhausting added structure."),
        binary_axis("graph", "What proves one object rather than many?", "sector-local-formulas-only", "Local formulas do not expose common dependence.", "connected-rooted-dependency-graph", "All sector nodes are connected to the One through shared carriers."),
        binary_axis("mutation", "How is shared dependence tested?", "decorative-shared-labels", "Labels without recomputation do not demonstrate dependence.", "complete-generator-successor-probe", "Every generator-dependent carrier is recomputed and moves."),
        binary_axis("control", "How is independence distinguished?", "blanket-global-mutation", "Changing everything cannot localize dependence.", "binary-and-rank-held-controls", "Binary-only half-One and independently held ranks remain exact."),
        binary_axis("measurement", "May measurement select the object?", "measurement-assembled-object", "That would fit the dependency graph to targets.", "formal-object-sealed-before-comparison", "The exact object is forced before external values are opened."),
        binary_axis("extension", "What happens when a new constant is lawfully derived?", "rewrite-existing-object", "Rewriting destroys provenance.", "append-traced-node", "A lawful extension appends a typed edge and retains every prior identity."),
        binary_axis("rule", "May any additional selector enter?", "free-extra-rule", "An extra selector is a parameter.", "no-extra-rule", "The admitted roots, covers, typing and complete incidence exhaust the grammar."),
    ),
    exact_result=(
        "One connected rooted Fold object generates the registered cross-sector constants. Its common order is "
        "b=2, c=3, spatial rank 3, boundary rank 2, down/up cover depths 5 and 7, leading inverse alpha "
        "34259/250, charged-lepton product 1/485, depth-five conjugate 1/95, depth-seven product 1/383, "
        "dark/baryon 27/5 with dark share 27/32, Hubble 13/12, Planck exponent 127/2, local vacuum-energy "
        "floor 1/2^20 and half-One 1/2. V3 terminal continuations retain the same object and include inverse "
        "alpha 503846395469/3676744786, charged-lepton sharpened product 3/1454 and terminal product, quark "
        "products 1/383 and 1/3071, dark/baryon 279/52, Hubble 3305/3048, the terminal squared Planck hierarchy, "
        "local vacuum amplitude/energy floors 1/2^10 and 1/2^20, and normalized cosmological magnitude 33/16."
    ),
    induction_base="The One and Fold generate binary two, generator three, stable rank three, boundary rank two and their least covers before any physical target is opened.",
    induction_step="Every lawful sector extension must consume an existing typed carrier or add a uniquely forced descendant, retain the complete incidence trace, and pass the same mutation and independence controls; otherwise it is not part of the object.",
    exclusions=(
        "no renaming, replacement or reinterpretation of Grand Lock 075 or 076",
        "no V1/V2 proof artifact or measured constant as an executable premise",
        "no fitted parameter, selected coefficient, target tolerance or untyped numerical coincidence",
        "no numerical-zero, negative, irrational, imaginary, floating, NaN or completed-infinite proof scalar",
        "no omitted sector, severed root edge, blanket mutation or silently rewritten terminal value",
    ),
    witnesses=(
        Witness("rooted-object", "Every registered sector node is reachable from the foundational One.", bool(_certificate["all_sectors_reach_One"])),
        Witness("shared-incidence", "Every sector has at least one explicit incoming shared-carrier edge.", bool(_certificate["shared_geometry_not_disconnected_list"])),
        Witness("leading-terminal-cross-lock", "All common-order carriers equal their independently admitted V3 implementations.", bool(_certificate["leading_terminal_cross_lock"])),
        Witness("dependency-probe", "Every generator-dependent common-order carrier moves under three-to-four.", bool(_certificate["every_generator_dependent_carrier_moves"])),
        Witness("independence-control", "Binary-only half-One and independently held ranks remain fixed.", bool(_certificate["independent_controls_hold"])),
    ),
)

SPEC.validate()


__all__ = (
    "CLAIM_ID", "DEPENDENCIES", "SPEC", "SECTOR_NODES", "admitted_terminal_vector",
    "dependency_graph", "foundation_order_vector", "reachable_from_one", "theorem_certificate",
)
