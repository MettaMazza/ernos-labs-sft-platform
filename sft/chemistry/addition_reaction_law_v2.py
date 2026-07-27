"""Complete Fold-native addition adjacency law for Chemistry ORG-009.

This replaces the unsubmitted V1 candidate.  V2 generates every positive
finite multiplicity reduction and every same-site, adjacent-site and
non-adjacent-site attachment form required by the frozen complete IUPAC
boundary.  No external product, species, yield, mechanism, rate or energy
enters generation or survivor selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque

from sft.chemistry.addition_reaction_law_v1 import (
    AdditionBond,
    AdditionState,
    FreeAdditionSupport,
    atom,
    connected_components,
    support,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _bond_by_support(state: AdditionState) -> dict[HeldLabel, AdditionBond]:
    return {row.held_support: row for row in state.bonds}


def _shortest_positive_distance(
    state: AdditionState,
    left: HeldLabel,
    right: HeldLabel,
) -> PositiveCount:
    if left == right:
        raise InadmissibleExactValue("same-site addition has structural EmptyOne separation")
    adjacency = {row: set() for row in state.atoms}
    for bond in state.bonds:
        adjacency[bond.left].add(bond.right)
        adjacency[bond.right].add(bond.left)
    queue = deque(((left, 0),))
    visited = set()
    while queue:
        current, distance = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        if current == right:
            return PositiveCount(distance)
        queue.extend((next_atom, distance + 1) for next_atom in adjacency[current] - visited)
    raise InadmissibleExactValue("addition sites must lie in one retained source carrier")


@dataclass(frozen=True)
class AdditionSiteClass:
    label: HeldLabel
    separation: EmptyOne | PositiveCount

    def __post_init__(self) -> None:
        if self.label.family != "addition-site-class" or self.label.label not in {
            "same-site", "adjacent-sites", "non-adjacent-sites"
        }:
            raise InadmissibleExactValue("addition site class is outside the complete generated family")
        if self.label.label == "same-site" and self.separation is not EMPTY_ONE:
            raise InadmissibleExactValue("same-site separation must be structural EmptyOne")
        if self.label.label == "adjacent-sites" and self.separation != PositiveCount(1):
            raise InadmissibleExactValue("adjacent-site separation must be one retained incidence")
        if self.label.label == "non-adjacent-sites" and (
            not isinstance(self.separation, PositiveCount) or self.separation.value < 2
        ):
            raise InadmissibleExactValue("non-adjacent sites require a positive path beyond one incidence")


@dataclass(frozen=True)
class ExactCompleteAddition:
    reaction_identity: HeldLabel
    source: AdditionState
    terminal: AdditionState
    source_component_count: PositiveCount
    new_bond_count: PositiveCount
    reduced_multiplicity_supports: tuple[HeldLabel, ...]
    reduced_layer_count: PositiveCount
    site_class: AdditionSiteClass
    relocated_supports: tuple[HeldLabel, ...]


def forced_complete_addition_transform(
    reaction_identity: HeldLabel,
    source: AdditionState,
    terminal: AdditionState,
) -> ExactCompleteAddition:
    if reaction_identity.family != "registered-reaction":
        raise InadmissibleExactValue("addition requires one registered reaction identity")
    if source.atoms != terminal.atoms:
        raise InadmissibleExactValue("every reactant atom occurrence must remain once in the product")
    if source.support_occurrences != terminal.support_occurrences:
        raise InadmissibleExactValue("every held support occurrence must remain once in the product")

    source_components = connected_components(source)
    terminal_components = connected_components(terminal)
    if len(source_components) < 2 or len(terminal_components) != 1:
        raise InadmissibleExactValue("two or more complete source carriers must become one product")
    source_component_of = {
        occurrence: index
        for index, component in enumerate(source_components)
        for occurrence in component
    }
    source_bonds = _bond_by_support(source)
    terminal_bonds = _bond_by_support(terminal)
    source_free = {row.held_support for row in source.free_supports}
    terminal_free = {row.held_support for row in terminal.free_supports}
    changed = tuple(
        held for held in source.support_occurrences
        if source_bonds.get(held) != terminal_bonds.get(held)
        or (held in source_free) != (held in terminal_free)
    )
    added_bonds = tuple(
        bond for held, bond in terminal_bonds.items()
        if source_bonds.get(held) != bond
    )
    if len(added_bonds) != 2:
        raise InadmissibleExactValue("the complete addition transform forms exactly two bonds")
    if any(source_component_of[row.left] == source_component_of[row.right] for row in added_bonds):
        raise InadmissibleExactValue("each formed bond must join previously distinct source carriers")

    removed_bonds = tuple(
        bond for held, bond in source_bonds.items()
        if terminal_bonds.get(held) != bond
    )
    unchanged_bonds = tuple(
        bond for held, bond in source_bonds.items()
        if terminal_bonds.get(held) == bond
    )
    reduced = tuple(
        bond.held_support
        for bond in removed_bonds
        if any(other.endpoints == bond.endpoints for other in unchanged_bonds)
    )
    if not reduced:
        raise InadmissibleExactValue("at least one exact source multiplicity layer must reduce")
    reduced_endpoints = {
        source_bonds[held].endpoints for held in reduced
    }
    reduced_components = {
        source_component_of[next(iter(endpoints))] for endpoints in reduced_endpoints
    }
    if len(reduced_components) != 1:
        raise InadmissibleExactValue("all reduced layers must belong to one retained substrate carrier")
    substrate_component = next(iter(reduced_components))
    substrate_sites = []
    for bond in added_bonds:
        candidates = tuple(
            endpoint for endpoint in (bond.left, bond.right)
            if source_component_of[endpoint] == substrate_component
        )
        if len(candidates) != 1:
            raise InadmissibleExactValue("each new bond must meet the retained substrate exactly once")
        substrate_sites.append(candidates[0])
    left_site, right_site = substrate_sites
    if left_site == right_site:
        site_class = AdditionSiteClass(HeldLabel("addition-site-class", "same-site"), EMPTY_ONE)
    else:
        separation = _shortest_positive_distance(source, left_site, right_site)
        site_class = AdditionSiteClass(
            HeldLabel(
                "addition-site-class",
                "adjacent-sites" if separation == PositiveCount(1) else "non-adjacent-sites",
            ),
            separation,
        )
    return ExactCompleteAddition(
        reaction_identity,
        source,
        terminal,
        PositiveCount(len(source_components)),
        PositiveCount(len(added_bonds)),
        tuple(sorted(reduced, key=lambda row: row.label)),
        PositiveCount(len(reduced)),
        site_class,
        tuple(sorted(changed, key=lambda row: row.label)),
    )


def extend_unchanged_complete_carrier(
    result: ExactCompleteAddition,
    anchor: HeldLabel,
    new_atom: HeldLabel,
    new_support: HeldLabel,
) -> bool:
    if anchor not in result.source.atoms or new_atom in result.source.atoms:
        raise InadmissibleExactValue("addition successor requires one retained anchor and one fresh atom")
    extension = AdditionBond(anchor, new_atom, new_support)
    source = AdditionState(
        HeldLabel("addition-state", result.source.identity.label + "-successor"),
        result.source.atoms + (new_atom,), result.source.bonds + (extension,), result.source.free_supports,
    )
    terminal = AdditionState(
        HeldLabel("addition-state", result.terminal.identity.label + "-successor"),
        result.terminal.atoms + (new_atom,), result.terminal.bonds + (extension,), result.terminal.free_supports,
    )
    extended = forced_complete_addition_transform(result.reaction_identity, source, terminal)
    return (
        extended.source_component_count == result.source_component_count
        and extended.new_bond_count == result.new_bond_count
        and extended.reduced_multiplicity_supports == result.reduced_multiplicity_supports
        and extended.site_class == result.site_class
        and extended.relocated_supports == result.relocated_supports
        and source.bonds[:-1] == result.source.bonds
        and terminal.bonds[:-1] == result.terminal.bonds
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-ORDER-001", "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001", "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007",
    "SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-product-label-or-reactant-fragment-omitted", "A named product or omitted reactant cannot reconstruct the complete source.", "complete-multicarrier-source-and-single-product", "Every source carrier and the single product remain in one source-ordered record."),
    dimension("atoms", "atom-created-erased-or-collapsed-to-formula", "A formula or incomplete occurrence list loses exact identity.", "every-reactant-atom-occurrence-retained", "Every exact source atom occurs once in the product."),
    dimension("supports", "support-created-erased-or-collapsed-to-order-number", "A scalar order or partial support cannot reconstruct the transform.", "every-held-support-occurrence-retained", "Every exact bond or free support remains exactly once."),
    dimension("adjacency", "endpoint-only-product-or-unregistered-edge-edit", "An endpoint or arbitrary edit does not prove addition.", "exact-two-new-cross-component-bonds", "Exactly two product bonds join previously distinct source carriers."),
    dimension("multiplicity", "exactly-one-layer-or-imported-named-rule", "A fixed one-layer restriction omits generated positive finite reductions.", "positive-finite-reduced-layer-family-with-base-retained", "Every positive finite number of reduced layers is generated while at least one base incidence remains."),
    dimension("sites", "adjacent-only-or-species-selected-site", "One preferred site distance omits lawful addition forms.", "complete-same-adjacent-and-nonadjacent-site-family", "Same-site, adjacent-site and every positive finite non-adjacent site separation are retained."),
    dimension("observation", "product-equation-or-database-row-readable-before-seal", "An external product could select the survivor.", "value-free-addition-product-vector-seal", "Law, identities and selector seal before every newly registered product opens."),
    dimension("extension", "reaction-specific-exception-or-recomputed-prefix", "A species exception is not depth-independent.", "fresh-unchanged-carrier-successor-no-extra-rule", "A fresh unchanged occurrence preserves the complete prior transform."),
)


def _state(
    label: str,
    atoms: tuple[HeldLabel, ...],
    bonds: tuple[AdditionBond, ...],
    free: tuple[FreeAdditionSupport, ...] = (),
) -> AdditionState:
    return AdditionState(HeldLabel("addition-state", label), atoms, bonds, free)


def _example(site: str, reduced_layers: int = 1) -> ExactCompleteAddition:
    left, middle, right, entering_left, entering_right = map(
        atom, (f"{site}-left", f"{site}-middle", f"{site}-right", f"{site}-entering-left", f"{site}-entering-right")
    )
    atoms = (left, middle, right, entering_left, entering_right)
    base_left = support(f"{site}-base-left")
    base_right = support(f"{site}-base-right")
    layers = tuple(support(f"{site}-layer-{index}") for index in range(1, reduced_layers + 1))
    addend = support(f"{site}-addend")
    source_bonds = (
        AdditionBond(left, middle, base_left),
        AdditionBond(middle, right, base_right),
        *(AdditionBond(left, middle, held) for held in layers),
        AdditionBond(entering_left, entering_right, addend),
    )
    if site == "same":
        attachment_left = attachment_right = left
    elif site == "adjacent":
        attachment_left, attachment_right = left, middle
    elif site == "nonadjacent":
        attachment_left, attachment_right = left, right
    else:
        raise InadmissibleExactValue("unknown generated site witness")
    used = (layers[0], addend)
    unused = layers[1:]
    terminal_bonds = (
        AdditionBond(left, middle, base_left),
        AdditionBond(middle, right, base_right),
        AdditionBond(attachment_left, entering_left, used[0]),
        AdditionBond(attachment_right, entering_right, used[1]),
    )
    terminal_free = tuple(FreeAdditionSupport(right, held) for held in unused)
    return forced_complete_addition_transform(
        HeldLabel("registered-reaction", f"{site}-complete-addition"),
        _state(f"{site}-source", atoms, source_bonds),
        _state(f"{site}-terminal", atoms, terminal_bonds, terminal_free),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    same = _example("same")
    adjacent = _example("adjacent")
    nonadjacent = _example("nonadjacent")
    multiple = _example("adjacent", 3)
    no_reduction_rejected = False
    try:
        source = adjacent.source
        terminal = AdditionState(
            HeldLabel("addition-state", "no-reduction"),
            source.atoms,
            source.bonds,
            (),
        )
        forced_complete_addition_transform(adjacent.reaction_identity, source, terminal)
    except InadmissibleExactValue:
        no_reduction_rejected = True
    successor = extend_unchanged_complete_carrier(
        nonadjacent, nonadjacent.source.atoms[1], atom("complete-successor"), support("complete-successor")
    )
    return (
        ("same-site", "Same-site addition is retained with structural EmptyOne separation.", same.site_class.label.label == "same-site" and same.site_class.separation is EMPTY_ONE),
        ("adjacent-site", "Adjacent-site addition is retained at one exact incidence.", adjacent.site_class.label.label == "adjacent-sites" and adjacent.site_class.separation == PositiveCount(1)),
        ("nonadjacent-site", "Non-adjacent addition is retained at its exact positive path.", nonadjacent.site_class.label.label == "non-adjacent-sites" and nonadjacent.site_class.separation == PositiveCount(2)),
        ("positive-finite-layers", "More than one reduced layer is generated without a new rule.", multiple.reduced_layer_count == PositiveCount(3)),
        ("atom-conservation", "Every source atom occurrence survives exactly once.", same.source.atoms == same.terminal.atoms),
        ("support-conservation", "Every held support occurrence survives exactly once.", multiple.source.support_occurrences == multiple.terminal.support_occurrences),
        ("two-new-bonds", "Every generated site class forms exactly two cross-carrier bonds.", all(row.new_bond_count == PositiveCount(2) for row in (same, adjacent, nonadjacent, multiple))),
        ("no-reduction-control", "A transform without a reduced multiplicity layer halts.", no_reduction_rejected),
        ("successor", "A fresh unchanged occurrence preserves the complete prior transform.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-multicarrier-source-and-single-product__every-reactant-atom-occurrence-retained__"
    "every-held-support-occurrence-retained__exact-two-new-cross-component-bonds__"
    "positive-finite-reduced-layer-family-with-base-retained__complete-same-adjacent-and-nonadjacent-site-family__"
    "value-free-addition-product-vector-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)


__all__ = (
    "AdditionSiteClass", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactCompleteAddition",
    "OPERATIONAL_WITNESSES", "extend_unchanged_complete_carrier", "forced_complete_addition_transform",
)
