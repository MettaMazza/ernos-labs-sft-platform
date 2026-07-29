"""Fold-native cyclic-support and stereochemical-alternative law for ORG-012.

WHY
    A pericyclic transformation is not admitted from a reaction name or an
    imported orbital rule.  The native question is whether one complete set of
    atom and held-support occurrences can change incidence through one closed
    transition cycle while every orientation alternative remains explicit.

DERIVATION
    The generator retains the complete source and terminal carriers, forms the
    finite cycle from an ordered tuple of exact atom occurrences, exhausts the
    two forced Fold fibre labels on both participating faces, and quotients only
    by simultaneous global complementation.  Four assignments therefore force
    two relative-orientation classes; neither class is selected by measurement.

CHECK
    Exact conservation, cycle closure, complete assignments, reversal,
    rejected incomplete cycles and a fresh unchanged successor are executable
    below.  Conventional endo/exo or orbital-symmetry terminology is used only
    later at the empirical correspondence boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.chemistry.addition_reaction_law_v1 import AdditionBond, AdditionState, atom, support
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def _bond_map(state: AdditionState) -> dict[HeldLabel, frozenset[HeldLabel]]:
    return {row.held_support: row.endpoints for row in state.bonds}


def _cycle_edges(atoms: tuple[HeldLabel, ...]) -> tuple[frozenset[HeldLabel], ...]:
    return tuple(
        frozenset((atoms[index], atoms[(index + 1) % len(atoms)]))
        for index in range(len(atoms))
    )


@dataclass(frozen=True)
class FaceAssignment:
    first_face: HeldLabel
    second_face: HeldLabel
    relative_class: HeldLabel


@dataclass(frozen=True)
class ExactPericyclicTransition:
    reaction_identity: HeldLabel
    source: AdditionState
    terminal: AdditionState
    transition_cycle_atoms: tuple[HeldLabel, ...]
    transition_cycle_edges: tuple[frozenset[HeldLabel], ...]
    participating_supports: tuple[HeldLabel, ...]
    participating_support_count: PositiveCount
    face_assignments: tuple[FaceAssignment, ...]
    relative_orientation_classes: tuple[HeldLabel, ...]
    complement_pairs: tuple[tuple[FaceAssignment, FaceAssignment], ...]


def _complete_face_assignments() -> tuple[FaceAssignment, ...]:
    labels = (
        HeldLabel("fold-fibre", "first"),
        HeldLabel("fold-fibre", "second"),
    )
    rows = []
    for first, second in product(labels, repeat=2):
        relation = "retained" if first == second else "opposed"
        rows.append(FaceAssignment(first, second, HeldLabel("relative-orientation", relation)))
    return tuple(rows)


def forced_pericyclic_transition(
    reaction_identity: HeldLabel,
    source: AdditionState,
    terminal: AdditionState,
    transition_cycle_atoms: tuple[HeldLabel, ...],
) -> ExactPericyclicTransition:
    if reaction_identity.family != "registered-reaction":
        raise InadmissibleExactValue("pericyclic transition requires one registered reaction identity")
    if source.atoms != terminal.atoms:
        raise InadmissibleExactValue("every atom occurrence must remain in exact source order")
    if source.support_occurrences != terminal.support_occurrences:
        raise InadmissibleExactValue("every held support occurrence must remain exactly once")
    if len(transition_cycle_atoms) < 4:
        raise InadmissibleExactValue("the least closed transition cycle requires four atom occurrences")
    if len(set(transition_cycle_atoms)) != len(transition_cycle_atoms):
        raise InadmissibleExactValue("a transition-cycle occurrence cannot be repeated")
    if any(row not in source.atoms for row in transition_cycle_atoms):
        raise InadmissibleExactValue("the transition cycle must use retained source occurrences")

    source_map = _bond_map(source)
    terminal_map = _bond_map(terminal)
    cycle_edges = _cycle_edges(transition_cycle_atoms)
    cycle_edge_set = frozenset(cycle_edges)
    endpoint_union = frozenset((*source_map.values(), *terminal_map.values()))
    if any(edge not in endpoint_union for edge in cycle_edges):
        raise InadmissibleExactValue("every transition-cycle edge must occur in a complete endpoint trace")

    moved = tuple(
        sorted(
            (held for held in source.support_occurrences if source_map[held] != terminal_map[held]),
            key=lambda held: held.label,
        )
    )
    if not moved:
        raise InadmissibleExactValue("a pericyclic transition requires a positive moved-support family")
    if any(source_map[held] not in cycle_edge_set or terminal_map[held] not in cycle_edge_set for held in moved):
        raise InadmissibleExactValue("every moved support must remain inside the closed transition cycle")

    assignments = _complete_face_assignments()
    relative = tuple(dict.fromkeys(row.relative_class for row in assignments))
    complements = (
        (assignments[0], assignments[3]),
        (assignments[1], assignments[2]),
    )
    if len(assignments) != 4 or len(relative) != 2:
        raise InadmissibleExactValue("the two Fold fibres must exhaust four assignments and two relative classes")
    return ExactPericyclicTransition(
        reaction_identity,
        source,
        terminal,
        transition_cycle_atoms,
        cycle_edges,
        moved,
        PositiveCount(len(moved)),
        assignments,
        relative,
        complements,
    )


def exact_reverse(result: ExactPericyclicTransition) -> bool:
    reverse = forced_pericyclic_transition(
        result.reaction_identity,
        result.terminal,
        result.source,
        tuple(reversed(result.transition_cycle_atoms)),
    )
    return (
        reverse.participating_supports == result.participating_supports
        and reverse.face_assignments == result.face_assignments
        and reverse.relative_orientation_classes == result.relative_orientation_classes
        and frozenset(reverse.transition_cycle_edges) == frozenset(result.transition_cycle_edges)
    )


def extend_unchanged_transition(
    result: ExactPericyclicTransition,
    anchor: HeldLabel,
    fresh_atom: HeldLabel,
    fresh_support: HeldLabel,
) -> bool:
    if anchor not in result.source.atoms or fresh_atom in result.source.atoms:
        raise InadmissibleExactValue("successor requires one retained anchor and one fresh occurrence")
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
    extended = forced_pericyclic_transition(
        result.reaction_identity, source, terminal, result.transition_cycle_atoms
    )
    return (
        extended.participating_supports == result.participating_supports
        and extended.face_assignments == result.face_assignments
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
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-QUANTUM-STATE-COMPOSITION-001",
    "SFT-QUANTUM-PHASE-INTERFERENCE-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
    "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-product-fragment-or-missing-reactant", "A partial carrier cannot establish a closed transformation.", "complete-source-and-terminal-carriers", "Every atom and support occurrence remains explicit at both endpoints."),
    dimension("cycle", "open-path-or-named-reaction-assumed", "An open or named path does not force cyclic support.", "complete-generated-transition-cycle", "Every cycle edge occurs in the exact source/terminal incidence union."),
    dimension("supports", "support-created-erased-or-renamed", "Unretained support destroys the exact transition trace.", "every-held-support-retained-once", "Every moved and unchanged support retains its identity."),
    dimension("transition", "sequential-story-or-target-selected-edit", "A story or observed product cannot select the native operation.", "positive-finite-cycle-confined-incidence-change", "Every moved support changes incidence inside one closed cycle."),
    dimension("phase", "imported-orbital-sign-or-complex-scalar", "An imported sign or complex value is outside native arithmetic.", "complete-two-fibre-face-assignment-product", "The two Fold fibres generate all four joint face assignments."),
    dimension("stereochemistry", "single-preferred-product-or-erased-alternative", "One preferred product omits lawful alternatives.", "two-relative-classes-under-global-complement", "Four assignments form retained and opposed relative classes without target selection."),
    dimension("observation", "external-stereochemistry-open-before-seal", "An opened target could select the law.", "value-free-cycle-and-stereochemistry-seal", "The exact law and complete target identities seal before payload outcomes."),
    dimension("extension", "species-exception-or-recomputed-prefix", "A reaction-specific exception is not a general law.", "fresh-unchanged-successor-no-extra-rule", "A fresh unchanged occurrence preserves the entire prior transition."),
)


def _example() -> ExactPericyclicTransition:
    a, b, c, d, e, f = map(atom, ("peri-a", "peri-b", "peri-c", "peri-d", "peri-e", "peri-f"))
    base_ab, base_bc, base_cd, base_ef = map(support, ("peri-base-ab", "peri-base-bc", "peri-base-cd", "peri-base-ef"))
    layer_ab, layer_cd, layer_ef = map(support, ("peri-layer-ab", "peri-layer-cd", "peri-layer-ef"))
    source = AdditionState(HeldLabel("addition-state", "peri-source"), (a, b, c, d, e, f), (
        AdditionBond(a, b, base_ab), AdditionBond(a, b, layer_ab), AdditionBond(b, c, base_bc),
        AdditionBond(c, d, base_cd), AdditionBond(c, d, layer_cd),
        AdditionBond(e, f, base_ef), AdditionBond(e, f, layer_ef),
    ), ())
    terminal = AdditionState(HeldLabel("addition-state", "peri-terminal"), source.atoms, (
        AdditionBond(a, b, base_ab), AdditionBond(b, c, base_bc), AdditionBond(b, c, layer_ab),
        AdditionBond(c, d, base_cd), AdditionBond(e, f, base_ef),
        AdditionBond(a, e, layer_cd), AdditionBond(d, f, layer_ef),
    ), ())
    return forced_pericyclic_transition(
        HeldLabel("registered-reaction", "generated-six-occurrence-cycle"),
        source,
        terminal,
        (a, b, c, d, f, e),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    result = _example()
    incomplete_rejected = False
    try:
        forced_pericyclic_transition(
            result.reaction_identity, result.source, result.terminal, result.transition_cycle_atoms[:-1]
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    successor = extend_unchanged_transition(
        result, result.source.atoms[1], atom("peri-successor"), support("peri-successor")
    )
    return (
        ("atom-conservation", "Every atom occurrence remains in source order.", result.source.atoms == result.terminal.atoms),
        ("support-conservation", "Every held support remains exactly once.", result.source.support_occurrences == result.terminal.support_occurrences),
        ("closed-cycle", "All six generated transition edges occur in the endpoint union.", len(result.transition_cycle_edges) == 6),
        ("positive-moved-family", "Three exact support occurrences move inside the cycle.", result.participating_support_count == PositiveCount(3)),
        ("complete-face-product", "Two forced fibres generate four face assignments.", len(result.face_assignments) == 4),
        ("relative-classes", "Global complement leaves two relative classes.", len(result.relative_orientation_classes) == 2),
        ("complement-pairs", "All four assignments occur in two complete complement pairs.", len(result.complement_pairs) == 2),
        ("reverse", "The exact reversed cycle reconstructs the source.", exact_reverse(result)),
        ("incomplete-cycle-control", "Removing a required cycle occurrence halts.", incomplete_rejected),
        ("successor", "A fresh unchanged occurrence preserves the complete prior transition.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-source-and-terminal-carriers__complete-generated-transition-cycle__"
    "every-held-support-retained-once__positive-finite-cycle-confined-incidence-change__"
    "complete-two-fibre-face-assignment-product__two-relative-classes-under-global-complement__"
    "value-free-cycle-and-stereochemistry-seal__fresh-unchanged-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactPericyclicTransition",
    "FaceAssignment", "OPERATIONAL_WITNESSES", "exact_reverse",
    "extend_unchanged_transition", "forced_pericyclic_transition",
)
