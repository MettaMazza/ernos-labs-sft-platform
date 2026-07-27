"""Fold-native inverse addition law for Chemistry ORG-010.

An elimination is forced here as the exact reversible boundary of the already
admitted complete addition transform.  The inverse is not a named conventional
mechanism: it retains the entire source and product carrier, every atom and
every held support occurrence, and reverses only the registered incidences.
External products do not enter the law or survivor selection.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.addition_reaction_law_v1 import AdditionBond, AdditionState, atom, support
from sft.chemistry.addition_reaction_law_v3 import (
    ComponentAdditionSiteClass,
    ExactCompleteAddition,
    forced_complete_addition_transform,
)
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ExactCompleteElimination:
    reaction_identity: HeldLabel
    source: AdditionState
    products: AdditionState
    product_component_count: PositiveCount
    removed_adjacencies: tuple[frozenset[HeldLabel], ...]
    removed_bond_count: PositiveCount
    restored_multiplicity_supports: tuple[HeldLabel, ...]
    restored_layer_count: PositiveCount
    product_site_classes: tuple[ComponentAdditionSiteClass, ...]
    relocated_supports: tuple[HeldLabel, ...]


def forced_complete_elimination_transform(
    reaction_identity: HeldLabel,
    source: AdditionState,
    products: AdditionState,
) -> ExactCompleteElimination:
    """Force one elimination by exact reconstruction of its addition inverse."""

    inverse = forced_complete_addition_transform(reaction_identity, products, source)
    if inverse.source.atoms != source.atoms or inverse.source.support_occurrences != source.support_occurrences:
        raise InadmissibleExactValue("elimination must retain every atom and held support occurrence")
    return ExactCompleteElimination(
        reaction_identity=reaction_identity,
        source=source,
        products=products,
        product_component_count=inverse.source_component_count,
        removed_adjacencies=inverse.new_adjacencies,
        removed_bond_count=inverse.new_bond_count,
        restored_multiplicity_supports=inverse.reduced_multiplicity_supports,
        restored_layer_count=inverse.reduced_layer_count,
        product_site_classes=inverse.component_site_classes,
        relocated_supports=inverse.relocated_supports,
    )


def extend_unchanged_complete_elimination(
    result: ExactCompleteElimination,
    anchor: HeldLabel,
    fresh_atom: HeldLabel,
    fresh_support: HeldLabel,
) -> bool:
    if anchor not in result.products.atoms or fresh_atom in result.products.atoms:
        raise InadmissibleExactValue("elimination successor requires a retained anchor and fresh occurrence")
    extension = AdditionBond(anchor, fresh_atom, fresh_support)
    products = AdditionState(
        HeldLabel("addition-state", result.products.identity.label + "-successor"),
        result.products.atoms + (fresh_atom,),
        result.products.bonds + (extension,),
        result.products.free_supports,
    )
    source = AdditionState(
        HeldLabel("addition-state", result.source.identity.label + "-successor"),
        result.source.atoms + (fresh_atom,),
        result.source.bonds + (extension,),
        result.source.free_supports,
    )
    extended = forced_complete_elimination_transform(result.reaction_identity, source, products)
    return (
        extended.product_component_count == result.product_component_count
        and extended.removed_adjacencies == result.removed_adjacencies
        and extended.restored_multiplicity_supports == result.restored_multiplicity_supports
        and extended.product_site_classes == result.product_site_classes
        and extended.relocated_supports == result.relocated_supports
        and products.bonds[:-1] == result.products.bonds
        and source.bonds[:-1] == result.source.bonds
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-QUANTUM-REVERSIBLE-MODEL-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-COVALENT-001",
    "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-alkene-or-leaving-fragment-omitted", "A selected product cannot reconstruct the complete reaction carrier.", "complete-single-source-and-multicarrier-products", "The complete source and every product carrier remain in one record."),
    dimension("atoms", "atom-erased-created-or-collapsed-to-formula", "An omitted leaving atom violates exact occurrence conservation.", "every-source-atom-occurrence-retained", "Every source atom occurs once across the complete products."),
    dimension("supports", "support-erased-created-or-collapsed-to-order-number", "A scalar bond order cannot retain the held support identity.", "every-held-support-occurrence-retained", "Every held bond or free support remains exactly once across the products."),
    dimension("adjacency", "named-leaving-group-or-arbitrary-cleavage-count", "A named group or free cleavage count imports a selector.", "exact-two-source-adjacencies-removed-across-product-components", "The exact inverse of addition removes the two cross-product adjacencies that had joined the carriers."),
    dimension("multiplicity", "fixed-one-layer-or-product-selected-order", "One chosen multiplicity omits the positive finite inverse family.", "positive-finite-multiplicity-family-restored-with-base-retained", "Every relocated layer returns to its retained product incidence while the base incidence remains."),
    dimension("sites", "beta-only-or-species-selected-site", "A beta-only convention omits same-site and positive finite non-adjacent forms.", "complete-productwise-same-adjacent-and-nonadjacent-site-family", "Every product carrier retains its exact same, adjacent or positive finite non-adjacent separation."),
    dimension("observation", "product-scheme-or-yield-readable-before-seal", "An opened product scope could choose the survivor.", "value-free-elimination-product-vector-seal", "The inverse law, identities and predicted vector seal before registered products open."),
    dimension("extension", "reaction-specific-exception-or-recomputed-prefix", "A named exception is not depth-independent.", "fresh-unchanged-carrier-successor-no-extra-rule", "A fresh unchanged occurrence preserves the complete inverse transform."),
)


def _state(label: str, atoms: tuple[HeldLabel, ...], bonds: tuple[AdditionBond, ...]) -> AdditionState:
    return AdditionState(HeldLabel("addition-state", label), atoms, bonds, ())


def _addition_witness(site: str, layers: int = 1) -> ExactCompleteAddition:
    left, middle, right, entering_left, entering_right = map(
        atom,
        (f"elim-{site}-left", f"elim-{site}-middle", f"elim-{site}-right", f"elim-{site}-enter-left", f"elim-{site}-enter-right"),
    )
    atoms = (left, middle, right, entering_left, entering_right)
    base_left = support(f"elim-{site}-base-left")
    base_right = support(f"elim-{site}-base-right")
    reduced = tuple(support(f"elim-{site}-layer-{ordinal}") for ordinal in range(1, layers + 1))
    entering = support(f"elim-{site}-entering")
    source_bonds = (
        AdditionBond(left, middle, base_left),
        AdditionBond(middle, right, base_right),
        *(AdditionBond(left, middle, held) for held in reduced),
        AdditionBond(entering_left, entering_right, entering),
    )
    if site == "same":
        first = second = left
    elif site == "adjacent":
        first, second = left, middle
    elif site == "nonadjacent":
        first, second = left, right
    else:
        raise InadmissibleExactValue("unknown generated elimination site")
    terminal_bonds = (
        AdditionBond(left, middle, base_left),
        AdditionBond(middle, right, base_right),
        AdditionBond(first, entering_left, reduced[0]),
        AdditionBond(second, entering_right, entering),
    )
    if layers > 1:
        terminal_bonds += tuple(AdditionBond(right, entering_right, held) for held in reduced[1:])
    return forced_complete_addition_transform(
        HeldLabel("registered-reaction", f"elim-{site}-inverse"),
        _state(f"elim-{site}-products", atoms, source_bonds),
        _state(f"elim-{site}-source", atoms, terminal_bonds),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    same_addition = _addition_witness("same")
    adjacent_addition = _addition_witness("adjacent")
    nonadjacent_addition = _addition_witness("nonadjacent")
    same = forced_complete_elimination_transform(same_addition.reaction_identity, same_addition.terminal, same_addition.source)
    adjacent = forced_complete_elimination_transform(adjacent_addition.reaction_identity, adjacent_addition.terminal, adjacent_addition.source)
    nonadjacent = forced_complete_elimination_transform(nonadjacent_addition.reaction_identity, nonadjacent_addition.terminal, nonadjacent_addition.source)
    invalid_rejected = False
    try:
        forced_complete_elimination_transform(adjacent.reaction_identity, adjacent.source, adjacent.source)
    except InadmissibleExactValue:
        invalid_rejected = True
    classes = {row.label.label for result in (same, adjacent, nonadjacent) for row in result.product_site_classes}
    successor = extend_unchanged_complete_elimination(
        nonadjacent,
        nonadjacent.products.atoms[1],
        atom("elim-successor-atom"),
        support("elim-successor-support"),
    )
    return (
        ("inverse-addition", "Every elimination is reconstructed by its complete addition inverse.", all(result.removed_bond_count == PositiveCount(2) for result in (same, adjacent, nonadjacent))),
        ("atom-conservation", "Every source atom occurrence remains across the products.", same.source.atoms == same.products.atoms),
        ("support-conservation", "Every held support occurrence remains across the products.", adjacent.source.support_occurrences == adjacent.products.support_occurrences),
        ("two-removed-adjacencies", "Exactly two source adjacencies separate the product carriers.", len(nonadjacent.removed_adjacencies) == 2),
        ("positive-multiplicity-restoration", "A positive multiplicity layer returns to its retained incidence.", adjacent.restored_layer_count == PositiveCount(1)),
        ("complete-site-family", "Same, adjacent and non-adjacent product-site classes are generated.", classes == {"same-site", "adjacent-sites", "non-adjacent-sites"}),
        ("invalid-inverse-control", "A state without a complete multicarrier inverse halts.", invalid_rejected),
        ("successor", "A fresh unchanged occurrence preserves the complete transform.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-single-source-and-multicarrier-products__every-source-atom-occurrence-retained__"
    "every-held-support-occurrence-retained__exact-two-source-adjacencies-removed-across-product-components__"
    "positive-finite-multiplicity-family-restored-with-base-retained__complete-productwise-same-adjacent-and-nonadjacent-site-family__"
    "value-free-elimination-product-vector-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactCompleteElimination",
    "OPERATIONAL_WITNESSES",
    "extend_unchanged_complete_elimination",
    "forced_complete_elimination_transform",
)
