"""Complete Fold-native addition adjacency law for Chemistry ORG-009.

V3 preserves the unopened V1/V2 development history and distinguishes two
new adjacencies from the complete set of held-support relocations.  This is
required for cycloaddition: two cross-carrier adjacencies form while further
held layers may move among already adjacent atom pairs.  Product outcomes do
not enter the law, its candidate grammar or survivor selection.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

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


def _endpoint_supports(state: AdditionState) -> dict[frozenset[HeldLabel], tuple[HeldLabel, ...]]:
    rows: dict[frozenset[HeldLabel], list[HeldLabel]] = defaultdict(list)
    for bond in state.bonds:
        rows[bond.endpoints].append(bond.held_support)
    return {key: tuple(sorted(value, key=lambda row: row.label)) for key, value in rows.items()}


def _shortest_distance(state: AdditionState, left: HeldLabel, right: HeldLabel) -> EmptyOne | PositiveCount:
    if left == right:
        return EMPTY_ONE
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
    raise InadmissibleExactValue("addition sites must belong to one retained source carrier")


@dataclass(frozen=True)
class ComponentAdditionSiteClass:
    source_component_ordinal: PositiveCount
    label: HeldLabel
    separation: EmptyOne | PositiveCount

    def __post_init__(self) -> None:
        if self.label.family != "addition-site-class" or self.label.label not in {
            "same-site", "adjacent-sites", "non-adjacent-sites"
        }:
            raise InadmissibleExactValue("addition site class lies outside the complete generated family")
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
    new_adjacencies: tuple[frozenset[HeldLabel], ...]
    new_bond_count: PositiveCount
    reduced_multiplicity_supports: tuple[HeldLabel, ...]
    reduced_layer_count: PositiveCount
    component_site_classes: tuple[ComponentAdditionSiteClass, ...]
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

    source_components = tuple(
        sorted(
            connected_components(source),
            key=lambda component: min(source.atoms.index(row) for row in component),
        )
    )
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
    source_endpoints = _endpoint_supports(source)
    terminal_endpoints = _endpoint_supports(terminal)
    source_free = {row.held_support for row in source.free_supports}
    terminal_free = {row.held_support for row in terminal.free_supports}
    changed = tuple(
        held
        for held in source.support_occurrences
        if source_bonds.get(held) != terminal_bonds.get(held)
        or (held in source_free) != (held in terminal_free)
    )

    new_adjacencies = tuple(
        sorted(
            (endpoints for endpoints in terminal_endpoints if endpoints not in source_endpoints),
            key=lambda endpoints: tuple(sorted(row.label for row in endpoints)),
        )
    )
    if len(new_adjacencies) != 2:
        raise InadmissibleExactValue("the complete addition transform forms exactly two new adjacencies")
    for endpoints in new_adjacencies:
        left, right = tuple(endpoints)
        if source_component_of[left] == source_component_of[right]:
            raise InadmissibleExactValue("each new adjacency must join previously distinct source carriers")
        if not terminal_endpoints[endpoints]:
            raise InadmissibleExactValue("each new adjacency must carry a held support")

    unchanged_supports = {
        held for held, bond in source_bonds.items() if terminal_bonds.get(held) == bond
    }
    reduced = tuple(
        held
        for held, bond in source_bonds.items()
        if terminal_bonds.get(held) != bond
        and any(base in unchanged_supports for base in source_endpoints[bond.endpoints])
    )
    if not reduced:
        raise InadmissibleExactValue("at least one exact source multiplicity layer must reduce")

    attachment_occurrences: dict[int, list[HeldLabel]] = defaultdict(list)
    for endpoints in new_adjacencies:
        for occurrence in endpoints:
            attachment_occurrences[source_component_of[occurrence]].append(occurrence)
    site_classes = []
    for component_index, occurrences in sorted(attachment_occurrences.items()):
        if len(occurrences) != 2:
            continue
        separation = _shortest_distance(source, occurrences[0], occurrences[1])
        if separation is EMPTY_ONE:
            label = "same-site"
        elif separation == PositiveCount(1):
            label = "adjacent-sites"
        else:
            label = "non-adjacent-sites"
        site_classes.append(
            ComponentAdditionSiteClass(
                PositiveCount(component_index + 1),
                HeldLabel("addition-site-class", label),
                separation,
            )
        )
    if not site_classes:
        raise InadmissibleExactValue("the complete transform must retain at least one exact attachment separation")

    return ExactCompleteAddition(
        reaction_identity,
        source,
        terminal,
        PositiveCount(len(source_components)),
        new_adjacencies,
        PositiveCount(len(new_adjacencies)),
        tuple(sorted(reduced, key=lambda row: row.label)),
        PositiveCount(len(reduced)),
        tuple(site_classes),
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
        and extended.new_adjacencies == result.new_adjacencies
        and extended.reduced_multiplicity_supports == result.reduced_multiplicity_supports
        and extended.component_site_classes == result.component_site_classes
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
    dimension("adjacency", "changed-support-count-confused-with-new-adjacency-count", "Relocated multiplicity support is not an additional new atom adjacency.", "exact-two-new-cross-component-adjacencies", "Exactly two previously absent endpoint pairs join source carriers."),
    dimension("multiplicity", "exactly-one-layer-or-one-component-only", "A fixed layer or component restriction omits complete additions.", "positive-finite-reduced-layer-family-with-base-retained", "A positive finite number of multiplicity layers may relocate from any retained source carrier while every reduced endpoint keeps a base incidence."),
    dimension("sites", "adjacent-only-or-species-selected-site", "One preferred site distance omits lawful addition forms.", "complete-componentwise-same-adjacent-and-nonadjacent-site-family", "Every component receiving both new incidences retains its exact same, adjacent or positive finite non-adjacent separation."),
    dimension("observation", "product-equation-or-database-row-readable-before-seal", "An external product could select the survivor.", "value-free-addition-product-vector-seal", "Law, source identities and prediction seal before registered products open."),
    dimension("extension", "reaction-specific-exception-or-recomputed-prefix", "A species exception is not depth-independent.", "fresh-unchanged-carrier-successor-no-extra-rule", "A fresh unchanged occurrence preserves the complete prior transform."),
)


def _state(label: str, atoms: tuple[HeldLabel, ...], bonds: tuple[AdditionBond, ...], free: tuple[FreeAdditionSupport, ...] = ()) -> AdditionState:
    return AdditionState(HeldLabel("addition-state", label), atoms, bonds, free)


def _simple_example(site: str, reduced_layers: int = 1) -> ExactCompleteAddition:
    left, middle, right, entering_left, entering_right = map(
        atom, (f"{site}-left", f"{site}-middle", f"{site}-right", f"{site}-entering-left", f"{site}-entering-right")
    )
    atoms = (left, middle, right, entering_left, entering_right)
    base_left, base_right = support(f"{site}-base-left"), support(f"{site}-base-right")
    layers = tuple(support(f"{site}-layer-{index}") for index in range(1, reduced_layers + 1))
    addend = support(f"{site}-addend")
    source_bonds = (
        AdditionBond(left, middle, base_left), AdditionBond(middle, right, base_right),
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
    terminal_bonds = (
        AdditionBond(left, middle, base_left), AdditionBond(middle, right, base_right),
        AdditionBond(attachment_left, entering_left, layers[0]),
        AdditionBond(attachment_right, entering_right, addend),
    )
    terminal_free = tuple(FreeAdditionSupport(right, held) for held in layers[1:])
    return forced_complete_addition_transform(
        HeldLabel("registered-reaction", f"{site}-complete-addition"),
        _state(f"{site}-source", atoms, source_bonds),
        _state(f"{site}-terminal", atoms, terminal_bonds, terminal_free),
    )


def _cycloaddition_example() -> ExactCompleteAddition:
    a, b, c, d, e, f = map(atom, ("cyclo-a", "cyclo-b", "cyclo-c", "cyclo-d", "cyclo-e", "cyclo-f"))
    base_ab, base_bc, base_cd, base_ef = map(support, ("cyclo-base-ab", "cyclo-base-bc", "cyclo-base-cd", "cyclo-base-ef"))
    layer_ab, layer_cd, layer_ef = map(support, ("cyclo-layer-ab", "cyclo-layer-cd", "cyclo-layer-ef"))
    source = _state("cyclo-source", (a, b, c, d, e, f), (
        AdditionBond(a, b, base_ab), AdditionBond(a, b, layer_ab),
        AdditionBond(b, c, base_bc),
        AdditionBond(c, d, base_cd), AdditionBond(c, d, layer_cd),
        AdditionBond(e, f, base_ef), AdditionBond(e, f, layer_ef),
    ))
    terminal = _state("cyclo-terminal", source.atoms, (
        AdditionBond(a, b, base_ab), AdditionBond(b, c, base_bc), AdditionBond(b, c, layer_ab),
        AdditionBond(c, d, base_cd), AdditionBond(e, f, base_ef),
        AdditionBond(a, e, layer_cd), AdditionBond(d, f, layer_ef),
    ))
    return forced_complete_addition_transform(HeldLabel("registered-reaction", "complete-cycloaddition"), source, terminal)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    same = _simple_example("same")
    adjacent = _simple_example("adjacent")
    nonadjacent = _simple_example("nonadjacent")
    multiple = _simple_example("adjacent", 3)
    cyclo = _cycloaddition_example()
    no_reduction_rejected = False
    try:
        forced_complete_addition_transform(adjacent.reaction_identity, adjacent.source, adjacent.source)
    except InadmissibleExactValue:
        no_reduction_rejected = True
    successor = extend_unchanged_complete_carrier(
        nonadjacent, nonadjacent.source.atoms[1], atom("complete-successor"), support("complete-successor")
    )
    classes = {row.label.label for result in (same, adjacent, nonadjacent) for row in result.component_site_classes}
    return (
        ("complete-site-family", "Same, adjacent and non-adjacent attachment separations are all generated.", classes == {"same-site", "adjacent-sites", "non-adjacent-sites"}),
        ("positive-finite-layers", "More than one reduced layer is generated without a new rule.", multiple.reduced_layer_count == PositiveCount(3)),
        ("atom-conservation", "Every source atom occurrence survives exactly once.", same.source.atoms == same.terminal.atoms),
        ("support-conservation", "Every held support occurrence survives exactly once.", multiple.source.support_occurrences == multiple.terminal.support_occurrences),
        ("two-new-adjacencies", "Every generated transform forms exactly two new cross-carrier adjacencies.", all(row.new_bond_count == PositiveCount(2) for row in (same, adjacent, nonadjacent, multiple, cyclo))),
        ("cycloaddition-relocation", "Cycloaddition forms two new adjacencies while three multiplicity layers relocate.", cyclo.new_bond_count == PositiveCount(2) and cyclo.reduced_layer_count == PositiveCount(3) and len(cyclo.relocated_supports) == 3),
        ("componentwise-sites", "Cycloaddition retains both component attachment separations.", len(cyclo.component_site_classes) == 2),
        ("no-reduction-control", "A transform without a reduced multiplicity layer halts.", no_reduction_rejected),
        ("successor", "A fresh unchanged occurrence preserves the complete prior transform.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-multicarrier-source-and-single-product__every-reactant-atom-occurrence-retained__"
    "every-held-support-occurrence-retained__exact-two-new-cross-component-adjacencies__"
    "positive-finite-reduced-layer-family-with-base-retained__complete-componentwise-same-adjacent-and-nonadjacent-site-family__"
    "value-free-addition-product-vector-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)


__all__ = (
    "ComponentAdditionSiteClass", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactCompleteAddition",
    "OPERATIONAL_WITNESSES", "extend_unchanged_complete_carrier", "forced_complete_addition_transform",
)
