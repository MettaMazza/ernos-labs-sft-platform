"""Fold-native complete adjacency and support transform for Chemistry ORG-009.

The law is generated without a named substrate, product, reagent, mechanism,
rate, energy, solvent, yield or external reaction row.  External addition
records are admitted only at the post-seal correspondence boundary.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def atom(label: str) -> HeldLabel:
    return HeldLabel("addition-atom-occurrence", label)


def support(label: str) -> HeldLabel:
    return HeldLabel("addition-held-support", label)


@dataclass(frozen=True)
class AdditionBond:
    left: HeldLabel
    right: HeldLabel
    held_support: HeldLabel

    def __post_init__(self) -> None:
        if (
            self.left.family != "addition-atom-occurrence"
            or self.right.family != "addition-atom-occurrence"
            or self.left == self.right
        ):
            raise InadmissibleExactValue("an addition bond requires two distinct retained atoms")
        if self.held_support.family != "addition-held-support":
            raise InadmissibleExactValue("an addition bond requires one exact held support")

    @property
    def endpoints(self) -> frozenset[HeldLabel]:
        return frozenset((self.left, self.right))


@dataclass(frozen=True)
class FreeAdditionSupport:
    owner: HeldLabel
    held_support: HeldLabel

    def __post_init__(self) -> None:
        if self.owner.family != "addition-atom-occurrence":
            raise InadmissibleExactValue("a free addition support requires a retained atom owner")
        if self.held_support.family != "addition-held-support":
            raise InadmissibleExactValue("a free addition support requires one exact held support")


@dataclass(frozen=True)
class AdditionState:
    identity: HeldLabel
    atoms: tuple[HeldLabel, ...]
    bonds: tuple[AdditionBond, ...]
    free_supports: tuple[FreeAdditionSupport, ...]

    def __post_init__(self) -> None:
        if self.identity.family != "addition-state":
            raise InadmissibleExactValue("an addition state requires one exact state identity")
        if len(self.atoms) < 2 or len(self.atoms) != len(set(self.atoms)):
            raise InadmissibleExactValue("an addition state requires distinct retained atoms")
        allowed = set(self.atoms)
        if any(row.family != "addition-atom-occurrence" for row in self.atoms):
            raise InadmissibleExactValue("an addition state contains an invalid atom occurrence")
        if any(set(row.endpoints) - allowed for row in self.bonds):
            raise InadmissibleExactValue("an addition bond leaves the declared atom carrier")
        if any(row.owner not in allowed for row in self.free_supports):
            raise InadmissibleExactValue("a free support leaves the declared atom carrier")
        support_ids = tuple(row.held_support for row in self.bonds) + tuple(
            row.held_support for row in self.free_supports
        )
        if len(support_ids) != len(set(support_ids)):
            raise InadmissibleExactValue("each held support must occur exactly once in a state")
        bond_keys = tuple((row.endpoints, row.held_support) for row in self.bonds)
        if len(bond_keys) != len(set(bond_keys)):
            raise InadmissibleExactValue("one exact bond support cannot be duplicated")

    @property
    def support_occurrences(self) -> frozenset[HeldLabel]:
        return frozenset(
            tuple(row.held_support for row in self.bonds)
            + tuple(row.held_support for row in self.free_supports)
        )


def connected_components(state: AdditionState) -> tuple[frozenset[HeldLabel], ...]:
    remaining = set(state.atoms)
    adjacency = {row: set() for row in state.atoms}
    for bond in state.bonds:
        adjacency[bond.left].add(bond.right)
        adjacency[bond.right].add(bond.left)
    components = []
    while remaining:
        seed = min(remaining, key=lambda row: row.label)
        frontier = [seed]
        component = set()
        while frontier:
            current = frontier.pop()
            if current in component:
                continue
            component.add(current)
            frontier.extend(adjacency[current] - component)
        remaining.difference_update(component)
        components.append(frozenset(component))
    return tuple(sorted(components, key=lambda row: tuple(sorted(item.label for item in row))))


def _bond_by_support(state: AdditionState) -> dict[HeldLabel, AdditionBond]:
    return {row.held_support: row for row in state.bonds}


@dataclass(frozen=True)
class ExactAddition:
    reaction_identity: HeldLabel
    source: AdditionState
    terminal: AdditionState
    source_component_count: PositiveCount
    new_bond_count: PositiveCount
    reduced_multiplicity_support: HeldLabel
    relocated_supports: tuple[HeldLabel, ...]


def forced_addition_transform(
    reaction_identity: HeldLabel,
    source: AdditionState,
    terminal: AdditionState,
) -> ExactAddition:
    if reaction_identity.family != "registered-reaction":
        raise InadmissibleExactValue("addition requires one registered reaction identity")
    if source.atoms != terminal.atoms:
        raise InadmissibleExactValue("every reactant atom occurrence must remain in the product")
    if source.support_occurrences != terminal.support_occurrences:
        raise InadmissibleExactValue("every held support occurrence must remain in the product")
    source_components = connected_components(source)
    terminal_components = connected_components(terminal)
    if len(source_components) < 2 or len(terminal_components) != 1:
        raise InadmissibleExactValue("addition must merge two or more source carriers into one product")
    source_by_support = _bond_by_support(source)
    terminal_by_support = _bond_by_support(terminal)
    source_free = {row.held_support for row in source.free_supports}
    terminal_free = {row.held_support for row in terminal.free_supports}
    changed = tuple(
        held for held in source.support_occurrences
        if source_by_support.get(held) != terminal_by_support.get(held)
        or (held in source_free) != (held in terminal_free)
    )
    added_bonds = tuple(
        bond for held, bond in terminal_by_support.items()
        if source_by_support.get(held) != bond
    )
    if len(added_bonds) != 2 or terminal_free:
        raise InadmissibleExactValue("the complete addition transform must form exactly two product bonds")
    component_of = {
        occurrence: index
        for index, component in enumerate(source_components)
        for occurrence in component
    }
    if any(component_of[row.left] == component_of[row.right] for row in added_bonds):
        raise InadmissibleExactValue("each formed bond must join previously distinct source carriers")
    removed_bonds = tuple(
        bond for held, bond in source_by_support.items()
        if terminal_by_support.get(held) != bond
    )
    reduced = tuple(
        bond.held_support for bond in removed_bonds
        if any(
            other.held_support != bond.held_support and other.endpoints == bond.endpoints
            for other in source.bonds
            if terminal_by_support.get(other.held_support) == other
        )
    )
    if len(reduced) != 1:
        raise InadmissibleExactValue("exactly one source bond layer must reduce while its base incidence remains")
    unchanged = tuple(
        held for held, bond in source_by_support.items()
        if terminal_by_support.get(held) == bond
    )
    if not unchanged:
        raise InadmissibleExactValue("the product must retain the unchanged source adjacency")
    return ExactAddition(
        reaction_identity,
        source,
        terminal,
        PositiveCount(len(source_components)),
        PositiveCount(len(added_bonds)),
        reduced[0],
        tuple(sorted(changed, key=lambda row: row.label)),
    )


def extend_unchanged_product_carrier(
    result: ExactAddition,
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
    extended = forced_addition_transform(result.reaction_identity, source, terminal)
    return (
        extended.source_component_count == result.source_component_count
        and extended.new_bond_count == result.new_bond_count
        and extended.reduced_multiplicity_support == result.reduced_multiplicity_support
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
    dimension("carrier", "selected-product-label-or-reactant-fragment-omitted", "A named product or omitted reactant cannot reconstruct the complete source.", "complete-multicarrier-source-and-single-product", "Every source carrier and the single product state remain in one source-ordered reaction record."),
    dimension("atoms", "atom-created-erased-or-collapsed-to-formula", "A formula or incomplete occurrence list loses exact stoichiometric identity.", "every-reactant-atom-occurrence-retained", "Every exact atom occurrence in every source component occurs once in the product."),
    dimension("supports", "support-created-erased-or-collapsed-to-bond-order-number", "A scalar order or partial support cannot reconstruct the transform.", "every-held-support-occurrence-retained", "Every exact bond or available support occurrence is conserved and relocated at most once."),
    dimension("adjacency", "endpoint-only-product-or-unregistered-edge-edit", "An endpoint or arbitrary graph edit does not prove addition.", "exact-two-new-cross-component-bonds", "Exactly two product incidences join source components and no unregistered edit is admitted."),
    dimension("multiplicity", "unchanged-or-imported-multiplicity-rule", "Without an exact retained base incidence the reduction is not structurally identified.", "one-reducible-layer-removed-base-incidence-retained", "Exactly one parallel source layer is relocated while its base incidence remains unchanged."),
    dimension("composition", "disconnected-terminal-or-reactant-carrier-lost", "A fragmentary terminal does not contain all reacting components.", "all-source-components-merge-into-one-product", "The two-or-more complete source components become exactly one connected product carrier."),
    dimension("observation", "product-equation-or-database-row-readable-before-seal", "An external product could select the survivor.", "value-free-addition-product-vector-seal", "The law, source identities and complete selection rule seal before any newly registered product outcome opens."),
    dimension("extension", "reaction-specific-exception-or-recomputed-prefix", "A species exception is not depth-independent.", "fresh-unchanged-carrier-successor-no-extra-rule", "Appending one fresh unchanged product-carrier occurrence preserves the complete prior transform."),
)


def _example() -> ExactAddition:
    left, right, entering_left, entering_right = map(
        atom, ("substrate-left", "substrate-right", "entering-left", "entering-right")
    )
    base = support("substrate-base")
    reducible = support("substrate-reducible-layer")
    addend = support("entering-carrier")
    atoms = (left, right, entering_left, entering_right)
    source = AdditionState(
        HeldLabel("addition-state", "complete-source"),
        atoms,
        (
            AdditionBond(left, right, base),
            AdditionBond(left, right, reducible),
            AdditionBond(entering_left, entering_right, addend),
        ),
        (),
    )
    terminal = AdditionState(
        HeldLabel("addition-state", "single-product"),
        atoms,
        (
            AdditionBond(left, right, base),
            AdditionBond(left, entering_left, reducible),
            AdditionBond(right, entering_right, addend),
        ),
        (),
    )
    return forced_addition_transform(
        HeldLabel("registered-reaction", "complete-addition-transform"), source, terminal
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    result = _example()
    source_components = connected_components(result.source)
    terminal_components = connected_components(result.terminal)
    bad_atom_rejected = False
    try:
        AdditionState(
            HeldLabel("addition-state", "missing-atom"),
            result.terminal.atoms[:-1], result.terminal.bonds, (),
        )
    except InadmissibleExactValue:
        bad_atom_rejected = True
    bad_multiplicity_rejected = False
    try:
        forced_addition_transform(
            result.reaction_identity,
            AdditionState(
                HeldLabel("addition-state", "no-reducible-layer"),
                result.source.atoms,
                (result.source.bonds[0], result.source.bonds[2]),
                (FreeAdditionSupport(result.source.atoms[0], result.source.bonds[1].held_support),),
            ),
            result.terminal,
        )
    except InadmissibleExactValue:
        bad_multiplicity_rejected = True
    successor = extend_unchanged_product_carrier(
        result, result.source.atoms[0], atom("unchanged-successor"), support("unchanged-successor")
    )
    return (
        ("complete-carriers", "Two complete source carriers become one complete product.", len(source_components) == 2 and len(terminal_components) == 1),
        ("atom-conservation", "Every reactant atom occurrence survives exactly once.", result.source.atoms == result.terminal.atoms),
        ("support-conservation", "Every exact held support survives exactly once.", result.source.support_occurrences == result.terminal.support_occurrences),
        ("two-new-bonds", "Exactly two cross-component product bonds are formed.", result.new_bond_count == PositiveCount(2)),
        ("multiplicity-reduction", "One reducible layer moves while the base incidence remains.", result.reduced_multiplicity_support == support("substrate-reducible-layer")),
        ("missing-atom-control", "An omitted atom occurrence halts.", bad_atom_rejected),
        ("unchanged-multiplicity-control", "A transform without the exact reducible layer halts.", bad_multiplicity_rejected),
        ("successor", "One fresh unchanged occurrence preserves the prior transform without another rule.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-multicarrier-source-and-single-product__every-reactant-atom-occurrence-retained__"
    "every-held-support-occurrence-retained__exact-two-new-cross-component-bonds__"
    "one-reducible-layer-removed-base-incidence-retained__all-source-components-merge-into-one-product__"
    "value-free-addition-product-vector-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)


__all__ = (
    "AdditionBond", "AdditionState", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactAddition", "FreeAdditionSupport", "OPERATIONAL_WITNESSES", "atom",
    "connected_components", "extend_unchanged_product_carrier", "forced_addition_transform", "support",
)
