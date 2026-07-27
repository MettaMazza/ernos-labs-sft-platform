"""Fold-native complete composition-retaining rearrangement law for ORG-011.

The law is generated before any newly registered rearrangement product vector
is opened.  It treats rearrangement as an exact held-support incidence change,
not as a named reaction, species rule, energy ranking, or measured selector.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations

from sft.chemistry.addition_reaction_law_v1 import (
    AdditionBond,
    AdditionState,
    atom,
    connected_components,
    support,
)
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _bond_map(state: AdditionState) -> dict[HeldLabel, frozenset[HeldLabel]]:
    return {bond.held_support: bond.endpoints for bond in state.bonds}


def _unlabelled_adjacencies(state: AdditionState, ordering: tuple[HeldLabel, ...]) -> frozenset[frozenset[int]]:
    index = {occurrence: ordinal for ordinal, occurrence in enumerate(ordering)}
    return frozenset(frozenset((index[bond.left], index[bond.right])) for bond in state.bonds)


def unlabelled_graph_isomorphic(source: AdditionState, terminal: AdditionState) -> bool:
    """Exhaust the finite vertex bijections; no coordinate tolerance is used."""

    if len(source.atoms) != len(terminal.atoms) or len(source.bonds) != len(terminal.bonds):
        return False
    source_edges = _unlabelled_adjacencies(source, source.atoms)
    terminal_edges = _unlabelled_adjacencies(terminal, terminal.atoms)
    size = len(source.atoms)
    for image in permutations(range(size)):
        mapped = frozenset(frozenset(image[index] for index in edge) for edge in source_edges)
        if mapped == terminal_edges:
            return True
    return False


@dataclass(frozen=True)
class ExactCompleteRearrangement:
    reaction_identity: HeldLabel
    source: AdditionState
    terminal: AdditionState
    moved_supports: tuple[HeldLabel, ...]
    moved_support_count: PositiveCount
    broken_incidences: tuple[frozenset[HeldLabel], ...]
    formed_incidences: tuple[frozenset[HeldLabel], ...]
    candidate_target_incidences: tuple[tuple[HeldLabel, tuple[frozenset[HeldLabel], ...]], ...]
    path_classes: tuple[HeldLabel, ...]
    constitutionally_degenerate: bool


def forced_complete_rearrangement_transform(
    reaction_identity: HeldLabel,
    source: AdditionState,
    terminal: AdditionState,
) -> ExactCompleteRearrangement:
    if reaction_identity.family != "registered-reaction":
        raise InadmissibleExactValue("rearrangement requires one registered reaction identity")
    if source.atoms != terminal.atoms:
        raise InadmissibleExactValue("rearrangement must retain every atom occurrence in exact source order")
    if source.support_occurrences != terminal.support_occurrences:
        raise InadmissibleExactValue("rearrangement must retain every held support occurrence")
    if len(connected_components(source)) != 1 or len(connected_components(terminal)) != 1:
        raise InadmissibleExactValue("complete molecular rearrangement endpoints require one connected carrier")
    if source.free_supports or terminal.free_supports:
        raise InadmissibleExactValue("endpoint rearrangement records require every support incidence to be closed")

    source_map = _bond_map(source)
    terminal_map = _bond_map(terminal)
    moved = tuple(
        sorted(
            (held for held in source.support_occurrences if source_map[held] != terminal_map[held]),
            key=lambda held: held.label,
        )
    )
    if not moved:
        raise InadmissibleExactValue("rearrangement requires at least one exact adjacency change")
    all_incidences = tuple(frozenset(pair) for pair in combinations(source.atoms, 2))
    targets = tuple(
        (
            held,
            tuple(incidence for incidence in all_incidences if incidence != source_map[held]),
        )
        for held in moved
    )
    if any(terminal_map[held] not in alternatives for held, alternatives in targets):
        raise InadmissibleExactValue("terminal incidence lies outside the complete generated alternative family")
    return ExactCompleteRearrangement(
        reaction_identity=reaction_identity,
        source=source,
        terminal=terminal,
        moved_supports=moved,
        moved_support_count=PositiveCount(len(moved)),
        broken_incidences=tuple(source_map[held] for held in moved),
        formed_incidences=tuple(terminal_map[held] for held in moved),
        candidate_target_incidences=targets,
        path_classes=(
            HeldLabel("rearrangement-path", "direct-held-support-relocation"),
            HeldLabel("rearrangement-path", "opened-support-then-exact-reclosure"),
        ),
        constitutionally_degenerate=unlabelled_graph_isomorphic(source, terminal),
    )


def exact_reverse_reconstruction(result: ExactCompleteRearrangement) -> bool:
    reverse = forced_complete_rearrangement_transform(
        result.reaction_identity,
        result.terminal,
        result.source,
    )
    return (
        reverse.moved_supports == result.moved_supports
        and reverse.broken_incidences == result.formed_incidences
        and reverse.formed_incidences == result.broken_incidences
        and reverse.moved_support_count == result.moved_support_count
    )


def extend_unchanged_rearrangement(
    result: ExactCompleteRearrangement,
    anchor: HeldLabel,
    fresh_atom: HeldLabel,
    fresh_support: HeldLabel,
) -> bool:
    if anchor not in result.source.atoms or fresh_atom in result.source.atoms:
        raise InadmissibleExactValue("rearrangement successor requires a retained anchor and fresh occurrence")
    extension = AdditionBond(anchor, fresh_atom, fresh_support)
    source = AdditionState(
        HeldLabel("addition-state", result.source.identity.label + "-successor"),
        result.source.atoms + (fresh_atom,),
        result.source.bonds + (extension,),
        result.source.free_supports,
    )
    terminal = AdditionState(
        HeldLabel("addition-state", result.terminal.identity.label + "-successor"),
        result.terminal.atoms + (fresh_atom,),
        result.terminal.bonds + (extension,),
        result.terminal.free_supports,
    )
    extended = forced_complete_rearrangement_transform(result.reaction_identity, source, terminal)
    return (
        extended.moved_supports == result.moved_supports
        and extended.broken_incidences == result.broken_incidences
        and extended.formed_incidences == result.formed_incidences
        and source.bonds[:-1] == result.source.bonds
        and terminal.bonds[:-1] == result.terminal.bonds
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
    "SFT-CHEM-MOL-ISOMER-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-group-or-product-fragment-only", "A fragment cannot prove that the same complete carrier rearranged.", "complete-source-and-terminal-carrier", "The complete connected source and terminal molecular carriers remain explicit."),
    dimension("atoms", "atom-created-erased-or-collapsed-to-formula", "A changed atom inventory is a different composition, not a rearrangement.", "every-atom-occurrence-retained-in-source-order", "Every exact atom occurrence remains once in the same carrier."),
    dimension("supports", "support-created-erased-or-renamed", "A replaced bond label cannot be traced through the rearrangement.", "every-held-support-occurrence-retained-once", "Every held support identity remains once while its incidence may move."),
    dimension("adjacency", "unchanged-graph-or-unregistered-edit", "No change is not a rearrangement and an arbitrary edit is not forced.", "positive-finite-held-support-incidence-change", "At least one held support changes from one exact incidence to another generated incidence."),
    dimension("path", "named-mechanism-or-single-imported-order", "A conventional mechanism name cannot select the native path.", "complete-direct-or-opened-reclosure-path-family", "The held support moves directly or opens and exactly recloses with its identity retained."),
    dimension("alternatives", "species-selected-target-or-degenerate-path-erased", "A named product omits other lawful target incidences and constitutionally degenerate traces.", "all-nonoriginal-incidences-and-degenerate-traces-generated", "Every nonoriginal pair is generated and an isomorphic endpoint retains its exact transition trace."),
    dimension("observation", "product-scope-readable-before-seal", "An opened rearrangement scope could choose the survivor.", "value-free-rearrangement-product-vector-seal", "The law, target identities and predicted relation seal before new product vectors open."),
    dimension("extension", "reaction-specific-exception-or-recomputed-prefix", "A named exception is not depth-independent.", "fresh-unchanged-carrier-successor-no-extra-rule", "A fresh unchanged occurrence preserves every prior support move and decision."),
)


def _state(label: str, atoms: tuple[HeldLabel, ...], bonds: tuple[AdditionBond, ...]) -> AdditionState:
    return AdditionState(HeldLabel("addition-state", label), atoms, bonds, ())


def _single_move() -> ExactCompleteRearrangement:
    a, b, c, d = map(atom, ("rearr-a", "rearr-b", "rearr-c", "rearr-d"))
    ab, moving, cd = map(support, ("rearr-ab", "rearr-moving", "rearr-cd"))
    atoms = (a, b, c, d)
    source = _state("rearr-source", atoms, (AdditionBond(a, b, ab), AdditionBond(b, c, moving), AdditionBond(c, d, cd)))
    terminal = _state("rearr-terminal", atoms, (AdditionBond(a, b, ab), AdditionBond(a, c, moving), AdditionBond(c, d, cd)))
    return forced_complete_rearrangement_transform(HeldLabel("registered-reaction", "rearr-single"), source, terminal)


def _three_moves() -> ExactCompleteRearrangement:
    a, b, c, d, e = map(atom, ("multi-a", "multi-b", "multi-c", "multi-d", "multi-e"))
    base, first, second, third = map(support, ("multi-base", "multi-first", "multi-second", "multi-third"))
    atoms = (a, b, c, d, e)
    source = _state("multi-source", atoms, (AdditionBond(a, b, base), AdditionBond(b, c, first), AdditionBond(c, d, second), AdditionBond(d, e, third)))
    terminal = _state("multi-terminal", atoms, (AdditionBond(a, b, base), AdditionBond(a, c, first), AdditionBond(b, d, second), AdditionBond(c, e, third)))
    return forced_complete_rearrangement_transform(HeldLabel("registered-reaction", "rearr-multi"), source, terminal)


def _degenerate() -> ExactCompleteRearrangement:
    a, b, c = map(atom, ("deg-a", "deg-b", "deg-c"))
    first, second, third = map(support, ("deg-first", "deg-second", "deg-third"))
    atoms = (a, b, c)
    source = _state("deg-source", atoms, (AdditionBond(a, b, first), AdditionBond(b, c, second), AdditionBond(a, c, third)))
    terminal = _state("deg-terminal", atoms, (AdditionBond(a, c, first), AdditionBond(a, b, second), AdditionBond(b, c, third)))
    return forced_complete_rearrangement_transform(HeldLabel("registered-reaction", "rearr-degenerate"), source, terminal)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    single = _single_move()
    multi = _three_moves()
    degenerate = _degenerate()
    unchanged_rejected = False
    composition_rejected = False
    try:
        forced_complete_rearrangement_transform(single.reaction_identity, single.source, single.source)
    except InadmissibleExactValue:
        unchanged_rejected = True
    try:
        shortened = _state("shortened", single.source.atoms[:-1], single.source.bonds[:-1])
        forced_complete_rearrangement_transform(single.reaction_identity, single.source, shortened)
    except InadmissibleExactValue:
        composition_rejected = True
    alternatives = single.candidate_target_incidences[0][1]
    successor = extend_unchanged_rearrangement(
        single,
        single.source.atoms[0],
        atom("rearr-successor-atom"),
        support("rearr-successor-support"),
    )
    return (
        ("carrier", "Both endpoints remain complete connected carriers.", len(connected_components(single.source)) == len(connected_components(single.terminal)) == 1),
        ("composition", "Every atom and held support occurrence remains exact.", single.source.atoms == single.terminal.atoms and single.source.support_occurrences == single.terminal.support_occurrences),
        ("adjacency", "One held support changes its exact incidence.", single.moved_support_count == PositiveCount(1) and single.broken_incidences != single.formed_incidences),
        ("positive-finite-family", "Three held supports may rearrange without a new rule.", multi.moved_support_count == PositiveCount(3)),
        ("complete-targets", "Every nonoriginal pair is generated for the moved support.", len(alternatives) == 5 and single.formed_incidences[0] in alternatives),
        ("path-family", "Direct relocation and opened exact reclosure are both retained.", tuple(path.label for path in single.path_classes) == ("direct-held-support-relocation", "opened-support-then-exact-reclosure")),
        ("degenerate", "An isomorphic endpoint retains a nonempty exact support-move trace.", degenerate.constitutionally_degenerate and degenerate.moved_support_count == PositiveCount(3)),
        ("reverse", "The complete rearrangement reconstructs exactly in reverse.", exact_reverse_reconstruction(multi)),
        ("unchanged-control", "An unchanged adjacency organization halts.", unchanged_rejected),
        ("composition-control", "A missing atom occurrence halts.", composition_rejected),
        ("successor", "A fresh unchanged occurrence preserves the complete transform.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-source-and-terminal-carrier__every-atom-occurrence-retained-in-source-order__"
    "every-held-support-occurrence-retained-once__positive-finite-held-support-incidence-change__"
    "complete-direct-or-opened-reclosure-path-family__all-nonoriginal-incidences-and-degenerate-traces-generated__"
    "value-free-rearrangement-product-vector-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactCompleteRearrangement",
    "OPERATIONAL_WITNESSES",
    "exact_reverse_reconstruction",
    "extend_unchanged_rearrangement",
    "forced_complete_rearrangement_transform",
    "unlabelled_graph_isomorphic",
)
