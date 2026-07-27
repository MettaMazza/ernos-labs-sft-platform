"""Fold-native finite conformer generation and equivalence law for ORG-005."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


Position = PositiveCount
Bond = tuple[Position, Position]


def _ordered_bond(left: Position, right: Position) -> Bond:
    if left == right:
        raise InadmissibleExactValue("a molecular bond requires two distinct positive positions")
    return (left, right) if left.value < right.value else (right, left)


@dataclass(frozen=True)
class FiniteMolecularGraph:
    atom_types: tuple[HeldLabel, ...]
    bonds: tuple[Bond, ...]

    def __post_init__(self) -> None:
        if not self.atom_types or any(atom.family != "atom-type" for atom in self.atom_types):
            raise InadmissibleExactValue("a conformer carrier requires positive finite atom support")
        positions = tuple(PositiveCount(index) for index in range(1, len(self.atom_types) + 1))
        allowed = set(positions)
        normalized = tuple(_ordered_bond(*bond) for bond in self.bonds)
        if not normalized or len(set(normalized)) != len(normalized) or any(set(bond) - allowed for bond in normalized):
            raise InadmissibleExactValue("molecular bonds must be complete distinct positive-position pairs")
        reached = {positions[0]}
        while True:
            expanded = reached | {
                endpoint
                for left, right in normalized
                if left in reached or right in reached
                for endpoint in (left, right)
            }
            if expanded == reached:
                break
            reached = expanded
        if reached != allowed:
            raise InadmissibleExactValue("conformer generation requires one connected molecular graph")
        object.__setattr__(self, "bonds", tuple(sorted(normalized, key=lambda bond: (bond[0].value, bond[1].value))))

    @property
    def positions(self) -> tuple[Position, ...]:
        return tuple(PositiveCount(index) for index in range(1, len(self.atom_types) + 1))


@dataclass(frozen=True)
class HeldRotor:
    ordered_sites: tuple[Position, Position, Position, Position]

    def validate_on(self, graph: FiniteMolecularGraph) -> None:
        if len(set(self.ordered_sites)) != 4 or any(site not in graph.positions for site in self.ordered_sites):
            raise InadmissibleExactValue("a rotor requires four distinct retained molecular positions")
        required = tuple(
            _ordered_bond(self.ordered_sites[index], self.ordered_sites[index + 1])
            for index in range(3)
        )
        if any(bond not in graph.bonds for bond in required):
            raise InadmissibleExactValue("a rotor requires the complete ordered three-bond path")

    @property
    def reversed_sites(self) -> tuple[Position, Position, Position, Position]:
        return tuple(reversed(self.ordered_sites))


@dataclass(frozen=True)
class HeldTorsionAlphabet:
    states: tuple[HeldLabel, ...]
    reversal: tuple[tuple[HeldLabel, HeldLabel], ...]

    def __post_init__(self) -> None:
        if not self.states or len(set(self.states)) != len(self.states) or any(state.family != "torsion-state" for state in self.states):
            raise InadmissibleExactValue("each rotor requires a complete positive finite held-state alphabet")
        mapping = dict(self.reversal)
        if set(mapping) != set(self.states) or any(value not in self.states for value in mapping.values()):
            raise InadmissibleExactValue("torsion reversal must cover every held state exactly once")
        if any(mapping[mapping[state]] != state for state in self.states):
            raise InadmissibleExactValue("torsion reversal must be an exact involution")

    def reverse(self, state: HeldLabel) -> HeldLabel:
        try:
            return dict(self.reversal)[state]
        except KeyError as exc:
            raise InadmissibleExactValue("torsion state is outside the registered alphabet") from exc


@dataclass(frozen=True)
class GraphAutomorphism:
    image: tuple[Position, ...]

    def __post_init__(self) -> None:
        expected = tuple(PositiveCount(index) for index in range(1, len(self.image) + 1))
        if tuple(sorted(self.image, key=lambda row: row.value)) != expected:
            raise InadmissibleExactValue("graph action must be a complete positive-position bijection")

    def apply(self, position: Position) -> Position:
        return self.image[position.value - 1]


@dataclass(frozen=True)
class ExactConformerAssignment:
    states: tuple[HeldLabel, ...]


@dataclass(frozen=True)
class ExactConformerCensus:
    graph: FiniteMolecularGraph
    rotors: tuple[HeldRotor, ...]
    alphabets: tuple[HeldTorsionAlphabet, ...]
    automorphisms: tuple[GraphAutomorphism, ...]
    generated_assignments: tuple[ExactConformerAssignment, ...]
    equivalence_classes: tuple[tuple[ExactConformerAssignment, ...], ...]

    def __post_init__(self) -> None:
        if not self.rotors or len(self.rotors) != len(self.alphabets):
            raise InadmissibleExactValue("conformer census requires every rotor and its exact held alphabet")
        if not self.generated_assignments or not self.equivalence_classes:
            raise InadmissibleExactValue("conformer census cannot omit generated assignments or classes")
        flattened = tuple(row for group in self.equivalence_classes for row in group)
        if len(flattened) != len(set(flattened)) or set(flattened) != set(self.generated_assignments):
            raise InadmissibleExactValue("each generated assignment must occur in exactly one equivalence class")


def finite_graph_automorphisms(graph: FiniteMolecularGraph) -> tuple[GraphAutomorphism, ...]:
    positions = graph.positions
    bond_set = set(graph.bonds)
    actions = []
    for image in permutations(positions):
        action = GraphAutomorphism(image)
        if any(graph.atom_types[position.value - 1] != graph.atom_types[action.apply(position).value - 1] for position in positions):
            continue
        mapped_bonds = {_ordered_bond(action.apply(left), action.apply(right)) for left, right in graph.bonds}
        if mapped_bonds == bond_set:
            actions.append(action)
    if not actions:
        raise InadmissibleExactValue("complete graph-automorphism enumeration returned structural EmptyOne")
    return tuple(actions)


def generate_conformer_assignments(alphabets: tuple[HeldTorsionAlphabet, ...]) -> tuple[ExactConformerAssignment, ...]:
    if not alphabets:
        raise InadmissibleExactValue("conformer generation requires at least one retained rotor")
    return tuple(ExactConformerAssignment(tuple(states)) for states in product(*(alphabet.states for alphabet in alphabets)))


def _apply_action(
    assignment: ExactConformerAssignment,
    action: GraphAutomorphism,
    rotors: tuple[HeldRotor, ...],
    alphabets: tuple[HeldTorsionAlphabet, ...],
) -> ExactConformerAssignment:
    if len(assignment.states) != len(rotors):
        raise InadmissibleExactValue("conformer assignment omits a rotor state")
    transformed: dict[int, HeldLabel] = {}
    for source_index, (rotor, state, alphabet) in enumerate(zip(rotors, assignment.states, alphabets)):
        mapped = tuple(action.apply(site) for site in rotor.ordered_sites)
        matches = [
            (target_index, False)
            for target_index, target in enumerate(rotors)
            if mapped == target.ordered_sites
        ] + [
            (target_index, True)
            for target_index, target in enumerate(rotors)
            if mapped == target.reversed_sites
        ]
        if len(matches) != 1:
            raise InadmissibleExactValue("graph action does not induce one complete rotor action")
        target_index, reversed_orientation = matches[0]
        if target_index in transformed or alphabets[target_index].states != alphabet.states:
            raise InadmissibleExactValue("graph action changes or duplicates a registered rotor alphabet")
        transformed[target_index] = alphabet.reverse(state) if reversed_orientation else state
    if len(transformed) != len(rotors):
        raise InadmissibleExactValue("graph action omits a target rotor")
    return ExactConformerAssignment(tuple(transformed[index] for index in range(len(rotors))))


def conformer_census(
    graph: FiniteMolecularGraph,
    rotors: tuple[HeldRotor, ...],
    alphabets: tuple[HeldTorsionAlphabet, ...],
) -> ExactConformerCensus:
    for rotor in rotors:
        rotor.validate_on(graph)
    actions = finite_graph_automorphisms(graph)
    assignments = generate_conformer_assignments(alphabets)
    assignment_order = {assignment: index for index, assignment in enumerate(assignments)}
    remaining = set(assignments)
    classes = []
    while remaining:
        anchor = min(remaining, key=assignment_order.__getitem__)
        orbit = {_apply_action(anchor, action, rotors, alphabets) for action in actions}
        if not orbit.issubset(set(assignments)):
            raise InadmissibleExactValue("symmetry orbit leaves the complete generated assignment space")
        classes.append(tuple(sorted(orbit, key=assignment_order.__getitem__)))
        remaining.difference_update(orbit)
    return ExactConformerCensus(graph, rotors, alphabets, actions, assignments, tuple(classes))


ANTI = HeldLabel("torsion-state", "anti")
GAUCHE_FORWARD = HeldLabel("torsion-state", "gauche-forward")
GAUCHE_REVERSE = HeldLabel("torsion-state", "gauche-reverse")


def butane_four_site_census() -> ExactConformerCensus:
    carbon = HeldLabel("atom-type", "carbon")
    graph = FiniteMolecularGraph(
        (carbon, carbon, carbon, carbon),
        tuple((PositiveCount(index), PositiveCount(index + 1)) for index in range(1, 4)),
    )
    rotor = HeldRotor(tuple(PositiveCount(index) for index in range(1, 5)))
    alphabet = HeldTorsionAlphabet(
        (ANTI, GAUCHE_FORWARD, GAUCHE_REVERSE),
        ((ANTI, ANTI), (GAUCHE_FORWARD, GAUCHE_REVERSE), (GAUCHE_REVERSE, GAUCHE_FORWARD)),
    )
    return conformer_census(graph, (rotor,), (alphabet,))


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-FOLD-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-MOL-ISOMER-001",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "name-or-coordinate-list", "A name or selected coordinates omit molecular identity and adjacency.", "complete-finite-molecular-graph", "Every atom occurrence, type and bond remains in one connected finite graph."),
    dimension("rotor", "selected-single-angle", "One selected angle omits other rotors and held states.", "complete-ordered-rotor-census", "Every rotatable four-site path and its full held state alphabet is retained."),
    dimension("generation", "energy-picked-conformer", "Measured energy cannot choose which assignments are generated.", "complete-cartesian-state-generation", "The exact finite product generates every rotor-state assignment once."),
    dimension("symmetry", "named-symmetry-assumption", "A named symmetry can omit or add an equivalence action.", "exhaustive-graph-automorphism-action", "Every atom-type and bond-preserving position bijection is generated and acts on all rotors."),
    dimension("equivalence", "coordinate-tolerance-clustering", "A tolerance or continuum metric introduces a fitted boundary.", "exact-automorphism-orbit-equivalence", "Assignments are equivalent exactly when one generated graph action connects them."),
    dimension("quotient", "selected-representative-list", "A selected list can duplicate or omit lawful conformers.", "complete-disjoint-orbit-quotient", "Every generated assignment occurs in exactly one nonempty equivalence class."),
    dimension("observation", "source-readable-generator", "External conformer names or energies could select the quotient.", "value-free-operational-census-seal", "The generation and quotient close before complete terminology and experimental surfaces are compared."),
    dimension("extension", "species-exception-or-extra-rule", "A species exception cannot establish a general finite algorithm.", "finite-product-successor-no-extra-rule", "Appending a rotor takes the exact product and reruns the same complete automorphism quotient."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    census = butane_four_site_census()
    classes = tuple(tuple(state.states[0] for state in group) for group in census.equivalence_classes)
    incomplete_reversal_rejected = missing_path_rejected = False
    try:
        HeldTorsionAlphabet((ANTI, GAUCHE_FORWARD), ((ANTI, ANTI),))
    except InadmissibleExactValue:
        incomplete_reversal_rejected = True
    try:
        graph = FiniteMolecularGraph(
            tuple(HeldLabel("atom-type", "carbon") for _ in range(4)),
            ((PositiveCount(1), PositiveCount(2)), (PositiveCount(3), PositiveCount(4))),
        )
        HeldRotor(tuple(PositiveCount(index) for index in range(1, 5))).validate_on(graph)
    except InadmissibleExactValue:
        missing_path_rejected = True
    return (
        ("complete-raw-generation", "Three held torsion assignments are generated exactly once.", len(census.generated_assignments) == 3 and len(set(census.generated_assignments)) == 3),
        ("complete-automorphism-census", "The four-site path has identity and reversal and no selected action.", len(census.automorphisms) == 2),
        ("exact-orbit-quotient", "Anti is self-equivalent and the two opposed gauche orientations form one class.", len(classes) == 2 and any(group == (ANTI,) for group in classes) and any(set(group) == {GAUCHE_FORWARD, GAUCHE_REVERSE} for group in classes)),
        ("partition-certificate", "Every assignment occurs in exactly one nonempty conformer class.", sum(len(group) for group in census.equivalence_classes) == 3),
        ("incomplete-reversal-control", "A torsion alphabet without complete involution halts.", incomplete_reversal_rejected),
        ("missing-path-control", "A rotor without its complete bonded path halts.", missing_path_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-finite-molecular-graph__complete-ordered-rotor-census__complete-cartesian-state-generation__"
    "exhaustive-graph-automorphism-action__exact-automorphism-orbit-equivalence__"
    "complete-disjoint-orbit-quotient__value-free-operational-census-seal__"
    "finite-product-successor-no-extra-rule"
)


__all__ = (
    "ANTI", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactConformerAssignment",
    "ExactConformerCensus", "FiniteMolecularGraph", "GAUCHE_FORWARD", "GAUCHE_REVERSE",
    "GraphAutomorphism", "HeldRotor", "HeldTorsionAlphabet", "OPERATIONAL_WITNESSES",
    "butane_four_site_census", "conformer_census", "finite_graph_automorphisms",
    "generate_conformer_assignments",
)
