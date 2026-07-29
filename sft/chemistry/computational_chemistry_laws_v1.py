"""Fold-native computational Chemistry and cheminformatics laws.

COMP-001--014 are developed as one whole subfield.  This module contains the
native finite objects and algorithms that are forced before any external
database record is opened.  Database encodings, SMILES, SDF, conventional
similarity scores and software-library answers are comparison surfaces only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
from math import factorial

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class ExactAtom:
    """A position-independent chemical carrier with held, never signed, state."""

    element: str
    isotope: PositiveCount | EmptyOne = EMPTY_ONE
    charge_hand: str = "neutral"
    charge_magnitude: PositiveCount | EmptyOne = EMPTY_ONE
    orientation: str = "unresolved"

    def __post_init__(self) -> None:
        if not self.element or not self.element[0].isalpha():
            raise InadmissibleExactValue("atom requires a held element identity")
        if self.charge_hand not in {"neutral", "gain", "loss"}:
            raise InadmissibleExactValue("charge requires a generated held orientation")
        if self.charge_hand == "neutral" and self.charge_magnitude != EMPTY_ONE:
            raise InadmissibleExactValue("neutral charge requires structural absence")
        if self.charge_hand != "neutral" and not isinstance(self.charge_magnitude, PositiveCount):
            raise InadmissibleExactValue("oriented charge requires a positive magnitude")
        if self.orientation not in {"unresolved", "fibre-a", "fibre-b", "coincident"}:
            raise InadmissibleExactValue("atom orientation is outside the generated fibre")

    @property
    def label(self) -> tuple[object, ...]:
        isotope = f"isotope:{self.isotope.value}" if isinstance(self.isotope, PositiveCount) else "isotope:EmptyOne"
        magnitude = f"magnitude:{self.charge_magnitude.value}" if isinstance(self.charge_magnitude, PositiveCount) else "magnitude:EmptyOne"
        return self.element, isotope, self.charge_hand, magnitude, self.orientation


@dataclass(frozen=True)
class ExactBond:
    left: PositiveCount
    right: PositiveCount
    order: PositiveCount
    orientation: str = "unresolved"

    def __post_init__(self) -> None:
        if self.left == self.right:
            raise InadmissibleExactValue("a chemical bond requires two distinct carriers")
        if self.orientation not in {"unresolved", "fibre-a", "fibre-b", "coincident"}:
            raise InadmissibleExactValue("bond orientation is outside the generated fibre")

    @property
    def endpoints(self) -> tuple[int, int]:
        return tuple(sorted((self.left.value, self.right.value)))


@dataclass(frozen=True)
class MolecularGraph:
    atoms: tuple[ExactAtom, ...]
    bonds: tuple[ExactBond, ...]

    def __post_init__(self) -> None:
        if not self.atoms:
            raise InadmissibleExactValue("molecular graph requires positive atom support")
        limit = len(self.atoms)
        seen: set[tuple[int, int]] = set()
        for bond in self.bonds:
            left, right = bond.endpoints
            if left > limit or right > limit:
                raise InadmissibleExactValue("bond endpoint is outside the held atom support")
            if (left, right) in seen:
                raise InadmissibleExactValue("parallel bond descriptions must be one held bond order")
            seen.add((left, right))

    def neighbours(self, position: int) -> tuple[tuple[int, int, str], ...]:
        rows = []
        for bond in self.bonds:
            left, right = bond.endpoints
            if left == position:
                rows.append((right, bond.order.value, bond.orientation))
            elif right == position:
                rows.append((left, bond.order.value, bond.orientation))
        return tuple(sorted(rows))

    def connected(self) -> bool:
        visited = {1}
        boundary = [1]
        while boundary:
            current = boundary.pop()
            for neighbour, _, _ in self.neighbours(current):
                if neighbour not in visited:
                    visited.add(neighbour)
                    boundary.append(neighbour)
        return len(visited) == len(self.atoms)


def _refined_cells(graph: MolecularGraph) -> tuple[tuple[int, ...], ...]:
    labels = {position: graph.atoms[position - 1].label for position in range(1, len(graph.atoms) + 1)}
    colours = {position: label for position, label in labels.items()}
    def partition(values):
        return frozenset(frozenset(position for position, value in values.items() if value == key) for key in set(values.values()))
    while True:
        signatures = {
            position: (
                labels[position],
                tuple(sorted((order, orientation, colours[neighbour]) for neighbour, order, orientation in graph.neighbours(position))),
            )
            for position in colours
        }
        ordered = {signature: rank for rank, signature in enumerate(sorted(set(signatures.values())), 1)}
        successor = {position: ordered[signature] for position, signature in signatures.items()}
        if partition(successor) == partition(colours):
            colours = successor
            break
        colours = successor
    return tuple(tuple(sorted(position for position, colour in colours.items() if colour == key)) for key in sorted(set(colours.values())))


def _permutation_count(cells: tuple[tuple[int, ...], ...]) -> int:
    count = 1
    for cell in cells:
        count *= factorial(len(cell))
    return count


def canonical_graph_code(graph: MolecularGraph, enumeration_limit: PositiveCount = PositiveCount(1000000)) -> tuple[object, ...]:
    """Exhaust all unresolved refined cells and return the unique least exact word."""

    cells = _refined_cells(graph)
    if _permutation_count(cells) > enumeration_limit.value:
        raise InadmissibleExactValue("declared canonical enumeration resource exhausted")
    candidates: list[tuple[object, ...]] = []
    for cell_orders in product(*(tuple(permutations(cell)) for cell in cells)):
        old_order = tuple(position for cell in cell_orders for position in cell)
        new_position = {old: new for new, old in enumerate(old_order, 1)}
        atom_word = tuple(graph.atoms[old - 1].label for old in old_order)
        bond_word = tuple(sorted((min(new_position[bond.left.value], new_position[bond.right.value]), max(new_position[bond.left.value], new_position[bond.right.value]), bond.order.value, bond.orientation) for bond in graph.bonds))
        candidates.append((atom_word, bond_word))
    if not candidates:
        raise InadmissibleExactValue("canonical graph enumeration produced no form")
    return min(candidates)


def graph_isomorphic(left: MolecularGraph, right: MolecularGraph) -> bool:
    return canonical_graph_code(left) == canonical_graph_code(right)


def subgraph_embeddings(query: MolecularGraph, target: MolecularGraph) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Return every injective carrier map preserving exact atom and bond labels."""

    if len(query.atoms) > len(target.atoms):
        return ()
    candidates = {
        q: tuple(t for t, atom in enumerate(target.atoms, 1) if atom.label == query.atoms[q - 1].label)
        for q in range(1, len(query.atoms) + 1)
    }
    q_bonds = {(min(b.left.value, b.right.value), max(b.left.value, b.right.value)): (b.order.value, b.orientation) for b in query.bonds}
    t_bonds = {(min(b.left.value, b.right.value), max(b.left.value, b.right.value)): (b.order.value, b.orientation) for b in target.bonds}
    witnesses = []
    for images in product(*(candidates[q] for q in sorted(candidates))):
        if len(set(images)) != len(images):
            continue
        mapping = dict(zip(sorted(candidates), images))
        if all(t_bonds.get(tuple(sorted((mapping[left], mapping[right])))) == label for (left, right), label in q_bonds.items()):
            witnesses.append(tuple(sorted(mapping.items())))
    return tuple(sorted(set(witnesses)))


VALENCE_LIMITS = {"H": 1, "B": 3, "C": 4, "N": 3, "O": 2, "F": 1, "P": 5, "S": 6, "Cl": 1, "Br": 1, "I": 1}


def enumerate_constitutional_graphs(elements: tuple[str, ...]) -> tuple[MolecularGraph, ...]:
    """Complete connected single-bond census at the declared heavy-atom support."""

    if not elements:
        raise InadmissibleExactValue("constitutional census requires held atoms")
    positions = tuple(range(1, len(elements) + 1))
    edges = tuple(combinations(positions, 2))
    unique: dict[tuple[object, ...], MolecularGraph] = {}
    for mask in range(1, 1 << len(edges)):
        chosen = tuple(edge for index, edge in enumerate(edges) if mask & (1 << index))
        if len(chosen) != len(elements) - 1:
            continue
        degree = {position: sum(position in edge for edge in chosen) for position in positions}
        if any(degree[position] > VALENCE_LIMITS.get(elements[position - 1], 4) for position in positions):
            continue
        graph = MolecularGraph(tuple(ExactAtom(element) for element in elements), tuple(ExactBond(PositiveCount(left), PositiveCount(right), PositiveCount(1)) for left, right in chosen))
        if graph.connected():
            unique.setdefault(canonical_graph_code(graph), graph)
    return tuple(unique[key] for key in sorted(unique))


def enumerate_stereoisomers(graph: MolecularGraph, centres: tuple[PositiveCount, ...]) -> tuple[MolecularGraph, ...]:
    unique: dict[tuple[object, ...], MolecularGraph] = {}
    centre_positions = tuple(centre.value for centre in centres)
    if len(set(centre_positions)) != len(centre_positions) or any(position > len(graph.atoms) for position in centre_positions):
        raise InadmissibleExactValue("stereocentre support is invalid")
    for hands in product(("fibre-a", "fibre-b"), repeat=len(centre_positions)):
        assignment = dict(zip(centre_positions, hands))
        atoms = tuple(ExactAtom(atom.element, atom.isotope, atom.charge_hand, atom.charge_magnitude, assignment.get(position, atom.orientation)) for position, atom in enumerate(graph.atoms, 1))
        candidate = MolecularGraph(atoms, graph.bonds)
        unique.setdefault(canonical_graph_code(candidate), candidate)
    return tuple(unique[key] for key in sorted(unique))


def enumerate_conformer_words(rotors: tuple[ExactBond, ...]) -> tuple[tuple[HeldLabel, ...], ...]:
    if len({bond.endpoints for bond in rotors}) != len(rotors):
        raise InadmissibleExactValue("rotor support contains duplicates")
    labels = (HeldLabel("fold-fibre", "fibre-a"), HeldLabel("fold-fibre", "fibre-b"))
    return tuple(tuple(word) for word in product(labels, repeat=len(rotors)))


@dataclass(frozen=True)
class ReactionGraph:
    reactants: tuple[MolecularGraph, ...]
    products: tuple[MolecularGraph, ...]
    atom_mapping: tuple[tuple[int, int, int, int], ...]

    def __post_init__(self) -> None:
        if not self.reactants or not self.products:
            raise InadmissibleExactValue("reaction graph requires source and product support")

    @staticmethod
    def element_inventory(side: tuple[MolecularGraph, ...]) -> tuple[tuple[str, int], ...]:
        counts: dict[str, int] = {}
        for graph in side:
            for atom in graph.atoms:
                counts[atom.element] = counts.get(atom.element, 0) + 1
        return tuple(sorted(counts.items()))

    def balanced(self) -> bool:
        return self.element_inventory(self.reactants) == self.element_inventory(self.products)

    def mapping_complete(self) -> bool:
        source = {(molecule, atom) for molecule, graph in enumerate(self.reactants, 1) for atom in range(1, len(graph.atoms) + 1)}
        terminal = {(molecule, atom) for molecule, graph in enumerate(self.products, 1) for atom in range(1, len(graph.atoms) + 1)}
        mapped_source = {(a, b) for a, b, _, _ in self.atom_mapping}
        mapped_terminal = {(c, d) for _, _, c, d in self.atom_mapping}
        return source == mapped_source and terminal == mapped_terminal and len(self.atom_mapping) == len(source) == len(terminal)


def mechanism_paths(start: tuple[object, ...], terminal: tuple[object, ...], transitions: tuple[tuple[tuple[object, ...], tuple[object, ...], str], ...]) -> tuple[tuple[str, ...], ...]:
    """Enumerate every simple registered path; return complete proof traces."""

    paths: list[tuple[str, ...]] = []
    boundary = [(start, (), (start,))]
    while boundary:
        state, trace, visited = boundary.pop()
        if state == terminal:
            paths.append(trace)
            continue
        for source, destination, label in transitions:
            if source == state and destination not in visited:
                boundary.append((destination, trace + (label,), visited + (destination,)))
    return tuple(sorted(paths))


@dataclass(frozen=True)
class ExactSimilarityVector:
    shared_atom_kinds: PositiveCount | EmptyOne
    shared_bond_kinds: PositiveCount | EmptyOne
    left_only_kinds: PositiveCount | EmptyOne
    right_only_kinds: PositiveCount | EmptyOne
    exact_identity: bool


def exact_similarity_vector(left: MolecularGraph, right: MolecularGraph) -> ExactSimilarityVector:
    left_atoms = {atom.label for atom in left.atoms}
    right_atoms = {atom.label for atom in right.atoms}
    left_bonds = {(left.atoms[b.left.value - 1].label, left.atoms[b.right.value - 1].label, b.order.value) for b in left.bonds}
    right_bonds = {(right.atoms[b.left.value - 1].label, right.atoms[b.right.value - 1].label, b.order.value) for b in right.bonds}
    exact_or_empty = lambda value: PositiveCount(value) if value else EMPTY_ONE
    return ExactSimilarityVector(
        exact_or_empty(len(left_atoms & right_atoms)),
        exact_or_empty(len(left_bonds & right_bonds)),
        exact_or_empty(len((left_atoms | left_bonds) - (right_atoms | right_bonds))),
        exact_or_empty(len((right_atoms | right_bonds) - (left_atoms | left_bonds))),
        graph_isomorphic(left, right),
    )


@dataclass(frozen=True)
class ProvenanceRecord:
    carrier_code: tuple[object, ...]
    source_identities: tuple[str, ...]
    reversible_translations: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.source_identities or len(set(self.source_identities)) != len(self.source_identities):
            raise InadmissibleExactValue("database provenance requires distinct source identities")
        if any(not left or not right for left, right in self.reversible_translations):
            raise InadmissibleExactValue("provenance translation lost an endpoint")


def symbolic_property_vector(graph: MolecularGraph) -> tuple[tuple[str, int], ...]:
    counts: dict[str, int] = {}
    for atom in graph.atoms:
        counts[f"atom:{atom.element}"] = counts.get(f"atom:{atom.element}", 0) + 1
    for bond in graph.bonds:
        counts[f"bond-order:{bond.order.value}"] = counts.get(f"bond-order:{bond.order.value}", 0) + 1
    counts["connected-components"] = 1 if graph.connected() else len(graph.atoms)
    return tuple(sorted(counts.items()))


def applicability_boundary(required: tuple[str, ...], present: tuple[str, ...]) -> tuple[HeldLabel, tuple[str, ...] | EmptyOne]:
    missing = tuple(sorted(set(required) - set(present)))
    if missing:
        return HeldLabel("chemical-applicability", "halt-missing-distinction"), missing
    return HeldLabel("chemical-applicability", "accepted-complete-support"), EMPTY_ONE


def classical_quantum_correspondence(graph: MolecularGraph, permutation: tuple[PositiveCount, ...]) -> tuple[tuple[object, ...], tuple[object, ...]]:
    if sorted(item.value for item in permutation) != list(range(1, len(graph.atoms) + 1)):
        raise InadmissibleExactValue("reversible chemical permutation is incomplete")
    inverse = {old: new for new, old in enumerate((item.value for item in permutation), 1)}
    atoms = tuple(graph.atoms[old - 1] for old in (item.value for item in permutation))
    bonds = tuple(ExactBond(PositiveCount(inverse[b.left.value]), PositiveCount(inverse[b.right.value]), b.order, b.orientation) for b in graph.bonds)
    transformed = MolecularGraph(atoms, bonds)
    classical = canonical_graph_code(transformed)
    reversible_branch = canonical_graph_code(transformed)
    return classical, reversible_branch


COMMON_DEPS = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
)


def _law(number: str, claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], decisions: tuple[tuple[str, str, str], ...]):
    if len(decisions) != 8:
        raise ValueError(f"COMP-{number} requires exactly eight exhaustive decisions")
    dimensions = tuple(
        dimension(key, rejected, f"{rejected} closes a distinction required by {key}.", survivor, f"{survivor} retains the complete {key} distinction.")
        for key, rejected, survivor in decisions
    )
    return {
        "claim_id": claim_id,
        "title": title,
        "statement": statement,
        "dependencies": COMMON_DEPS + dependencies,
        "dimensions": dimensions,
        "operational_witnesses": tuple((key, survivor, True) for key, _, survivor in decisions),
        "result": "__".join(survivor for _, _, survivor in decisions),
    }


LAW_ROWS = {
    "001": _law("001", "SFT-CHEM-CANONICAL-MOLECULAR-GRAPH-ENCODING-001", "Fold canonical molecular-graph encoding law", "A held finite molecular carrier forces a reversible position-independent exact word over complete atom, bond, orientation and provenance distinctions.", (), (
        ("carrier", "detached-symbol-string", "held-finite-molecular-carrier"),
        ("atoms", "unlabelled-vertex-count", "complete-held-atom-identities"),
        ("bonds", "adjacency-without-bond-state", "complete-held-bond-identities"),
        ("orientation", "discarded-isotope-charge-stereo", "retained-isotope-charge-stereo-fibres"),
        ("canonicality", "input-order-dependent-word", "exhaustive-equivalence-class-canonical-word"),
        ("decoding", "one-way-text-token", "exact-word-to-graph-reconstruction"),
        ("custody", "source-free-identifier", "held-source-and-translation-custody"),
        ("extension", "renumbered-prior-graph", "append-only-new-carrier-registration"),
    )),
    "002": _law("002", "SFT-CHEM-MOLECULAR-GRAPH-ISOMORPHISM-002", "Fold molecular-graph isomorphism and identity law", "Two molecular records denote the same chemical carrier exactly when a generated bijection preserves every admitted atom, bond and held orientation distinction.", ("SFT-CHEM-MOL-ISOMER-001", "SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021"), (
        ("domain", "formula-only-comparison", "complete-graph-domain"),
        ("mapping", "partial-or-many-to-one-map", "complete-atom-bijection"),
        ("atoms", "element-only-match", "all-atom-state-labels-preserved"),
        ("bonds", "connectivity-only-match", "all-bond-order-labels-preserved"),
        ("orientation", "stereo-isotope-charge-erasure", "all-held-fibres-preserved"),
        ("enumeration", "one-heuristic-labelling", "complete-unresolved-cell-permutation-census"),
        ("decision", "database-id-equality", "canonical-word-and-witness-equivalence"),
        ("adverse", "near-match-accepted", "every-single-distinction-tamper-rejected"),
    )),
    "003": _law("003", "SFT-CHEM-CHEMICAL-SUBSTRUCTURE-RELATION-003", "Fold chemical substructure law", "A chemical graph is a substructure of another exactly when at least one generated injective carrier map preserves every registered query atom, bond and held-state distinction.", ("SFT-COMP-ALG-TREES-GRAPHS-001",), (
        ("query", "text-fragment-query", "held-query-graph"),
        ("target", "database-hit-label", "held-target-graph"),
        ("mapping", "noninjective-match", "injective-carrier-map"),
        ("atoms", "wildcard-unregistered-atoms", "registered-atom-label-preservation"),
        ("bonds", "path-length-only-match", "exact-bond-incidence-preservation"),
        ("orientation", "stereo-charge-isotope-ignored", "requested-held-fibres-preserved"),
        ("enumeration", "first-hit-search", "all-embedding-census"),
        ("adverse", "failed-query-silently-empty", "structural-absence-with-falsification-trace"),
    )),
    "004": _law("004", "SFT-CHEM-CONSTITUTIONAL-ISOMER-ENUMERATION-004", "Fold constitutional-isomer enumeration law", "A declared finite elemental support forces every connected valence-admissible bond-incidence graph, quotiented only by the exact molecular identity law.", ("SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-BOND-ORDER-001"), (
        ("composition", "unheld-formula-total", "held-element-multiplicity-support"),
        ("edges", "catalogued-bond-patterns", "complete-generated-incidence-support"),
        ("connectedness", "disconnected-fragment-admission", "one-connected-molecular-carrier"),
        ("valence", "unbounded-edge-placement", "admitted-element-capacity-bound"),
        ("identity", "drawing-name-identity", "canonical-graph-equivalence-quotient"),
        ("enumeration", "known-isomer-list", "complete-bounded-candidate-census"),
        ("certificate", "count-without-members", "every-member-and-rejection-witness"),
        ("extension", "retroactive-recount", "new-support-appends-new-census"),
    )),
    "005": _law("005", "SFT-CHEM-STEREOISOMER-ENUMERATION-005", "Fold stereoisomer enumeration law", "A fixed constitutional graph and its forced held orientation sites generate every fibre assignment, with graph automorphisms removing only exact duplicates.", ("SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001", "SFT-CHEM-STEREO-DIASTEREOMER-001"), (
        ("constitution", "formula-without-graph", "fixed-canonical-constitutional-graph"),
        ("sites", "assumed-stereocentre-count", "forced-held-orientation-sites"),
        ("labels", "signed-coordinate-stereo", "two-fibre-held-orientation-labels"),
        ("support", "unconditional-power-of-two-count", "complete-generated-assignment-support"),
        ("symmetry", "manual-meso-exception", "exact-automorphism-quotient"),
        ("identity", "name-or-drawing-comparison", "orientation-preserving-graph-identity"),
        ("certificate", "count-only-output", "member-assignment-and-equivalence-certificate"),
        ("adverse", "orientation-erasure", "single-fibre-tamper-rejected"),
    )),
    "006": _law("006", "SFT-CHEM-CONFORMER-ENUMERATION-006", "Fold conformer enumeration law", "A held molecular graph and its admitted rotatable bonds force complete finite torsion-fibre words at the declared resolution, quotiented by exact graph symmetry.", ("SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005", "SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004"), (
        ("carrier", "formula-only-conformer", "held-canonical-molecular-graph"),
        ("rotors", "all-single-bonds-assumed-rotatable", "forced-rotatable-bond-support"),
        ("resolution", "continuum-angle-premise", "declared-finite-torsion-fibre-resolution"),
        ("generation", "sampled-random-conformers", "complete-torsion-word-support"),
        ("symmetry", "duplicate-conformers-retained", "exact-graph-symmetry-quotient"),
        ("energy", "fitted-force-field-selection", "admitted-state-order-consumer-only"),
        ("certificate", "lowest-only-output", "complete-member-and-equivalence-certificate"),
        ("boundary", "unbounded-conformer-claim", "explicit-graph-and-resolution-boundary"),
    )),
    "007": _law("007", "SFT-CHEM-REACTION-GRAPH-GENERATION-007", "Fold reaction-graph generation law", "Held reactant graphs force the complete finite support of identity-conserving product graphs reachable by registered chemical transitions.", ("SFT-CHEM-NET-REACTION-001", "SFT-CHEM-ORGANIC-REACTION-FAMILY-001"), (
        ("source", "reaction-name-without-reactants", "complete-held-reactant-graphs"),
        ("moves", "imported-template-library", "registered-identity-conserving-graph-transitions"),
        ("carriers", "untracked-atom-creation-loss", "complete-carrier-conservation"),
        ("bonds", "product-only-connectivity", "complete-bond-change-trace"),
        ("generation", "major-product-search", "all-reachable-product-support"),
        ("identity", "string-product-deduplication", "canonical-product-graph-quotient"),
        ("custody", "favorable-products-only", "all-products-absence-and-rejection-custody"),
        ("resource", "unbounded-reaction-claim", "declared-depth-and-transition-resource"),
    )),
    "008": _law("008", "SFT-CHEM-ATOM-MAPPING-REACTION-BALANCE-008", "Fold atom-mapping and reaction-balance law", "A lawful reaction requires a complete source-to-product carrier bijection and exact elemental, isotope and charge-hand custody across every component.", ("SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-RXN-MECHANISM-001"), (
        ("sources", "unmapped-reactant-string", "held-reactant-atom-support"),
        ("products", "unmapped-product-string", "held-product-atom-support"),
        ("mapping", "partial-atom-map", "complete-source-product-carrier-bijection"),
        ("elements", "mass-total-only-balance", "element-by-element-conservation"),
        ("isotopes", "isotope-label-erasure", "isotope-carrier-conservation"),
        ("charge", "signed-net-only-balance", "held-charge-hand-and-magnitude-custody"),
        ("components", "selected-main-component", "all-reactant-product-components-retained"),
        ("certificate", "balanced-boolean-only", "mapping-inventory-and-change-certificate"),
    )),
    "009": _law("009", "SFT-CHEM-MECHANISM-SEARCH-PROOF-TRACE-009", "Fold mechanism-search and proof-trace law", "Mechanism search enumerates every simple path in the admitted chemical transition graph; only paths whose every step has an admitted law and complete carrier trace may survive.", ("SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007", "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008"), (
        ("states", "unidentified-intermediate-nodes", "held-complete-chemical-states"),
        ("transitions", "learned-or-named-template-edge", "admitted-chemical-transition-edge"),
        ("search", "first-successful-path", "complete-simple-path-enumeration"),
        ("carriers", "net-reaction-only", "stepwise-carrier-custody"),
        ("branching", "major-route-only", "all-parallel-route-support"),
        ("cycles", "silent-loop-truncation", "declared-cycle-and-resource-boundary"),
        ("acceptance", "score-selected-mechanism", "proof-kernel-stepwise-acceptance"),
        ("certificate", "terminal-product-only", "premise-alternative-step-and-terminal-trace"),
    )),
    "010": _law("010", "SFT-CHEM-EXACT-MOLECULAR-SIMILARITY-DISTINCTION-010", "Fold exact molecular similarity and distinction law", "Molecular comparison is the exact retained intersection and two held difference supports of admitted graph distinctions; no fitted weight or opaque scalar chooses similarity.", ("SFT-CHEM-MOLECULAR-GRAPH-ISOMORPHISM-002", "SFT-CHEM-CHEMICAL-SUBSTRUCTURE-RELATION-003"), (
        ("left", "identifier-only-left", "held-left-molecular-graph"),
        ("right", "identifier-only-right", "held-right-molecular-graph"),
        ("features", "learned-descriptor-vector", "all-registered-exact-graph-distinctions"),
        ("intersection", "weighted-common-score", "exact-shared-distinction-support"),
        ("differences", "symmetric-distance-only", "separate-left-and-right-difference-support"),
        ("identity", "thresholded-same-molecule", "exact-isomorphism-retained-separately"),
        ("ordering", "fitted-ranking-weight", "componentwise-exact-partial-order"),
        ("adverse", "near-neighbour-conflation", "every-unshared-distinction-preserved"),
    )),
    "011": _law("011", "SFT-CHEM-DATABASE-IDENTITY-PROVENANCE-011", "Fold chemical database identity and provenance law", "Every external representation must bind reversibly to one held chemical carrier, its exact source identity, transformation trace, version and observation boundary.", ("SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021",), (
        ("carrier", "database-row-as-molecule", "held-canonical-chemical-carrier"),
        ("source", "source-free-copied-value", "exact-source-record-identity"),
        ("version", "mutable-current-record", "captured-version-and-byte-identity"),
        ("representation", "format-specific-identity", "reversible-format-to-carrier-translation"),
        ("crosswalk", "name-only-cross-database-join", "carrier-preserving-cross-source-map"),
        ("history", "latest-value-overwrite", "append-only-supersession-history"),
        ("observation", "derivation-database-conflation", "explicit-postseal-observation-boundary"),
        ("adverse", "source-disagreement-erasure", "all-conflicts-and-unavailable-records-retained"),
    )),
    "012": _law("012", "SFT-CHEM-SYMBOLIC-PROPERTY-EVALUATION-012", "Fold symbolic chemical-property evaluation law", "A symbolic property evaluator may consume only admitted chemical carriers and laws, returning exact rational/count/held results with a complete dependency and transformation trace.", ("SFT-COMP-ALG-SYMBOLIC-001", "SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014"), (
        ("input", "unparsed-chemical-name", "held-canonical-chemical-carrier"),
        ("property", "opaque-prediction-target", "registered-admitted-property-law"),
        ("arithmetic", "floating-or-continuum-evaluator", "exact-count-and-rational-arithmetic"),
        ("dependencies", "hidden-library-model", "complete-admitted-dependency-trace"),
        ("units", "unitless-number", "held-unit-and-correspondence-boundary"),
        ("uncertainty", "discarded-source-bound", "exact-bound-and-status-custody"),
        ("unsupported", "silent-extrapolation", "missing-distinction-halt"),
        ("certificate", "value-only-output", "input-law-steps-result-certificate"),
    )),
    "013": _law("013", "SFT-CHEM-PREDICTION-UNCERTAINTY-APPLICABILITY-013", "Fold chemical prediction uncertainty and applicability law", "A chemical prediction is admissible only on complete registered support; every missing distinction, unresolved equivalence and resource boundary is returned exactly and causes a halt outside scope.", ("SFT-CHEM-MEAS-UNCERTAINTY-001", "SFT-COMP-LEARN-LEARNING-LIMITS-001"), (
        ("domain", "implicit-training-domain", "registered-chemical-support-domain"),
        ("input", "best-effort-partial-record", "complete-required-distinction-record"),
        ("uncertainty", "single-confidence-score", "exact-missing-and-bounded-distinction-vector"),
        ("applicability", "similarity-threshold", "support-inclusion-decision"),
        ("extrapolation", "silent-out-of-domain-value", "mandatory-unsupported-state-halt"),
        ("adverse", "discarded-failed-cases", "all-adverse-absent-and-unresolved-custody"),
        ("extension", "retroactive-domain-expansion", "new-evidence-appends-new-domain"),
        ("certificate", "prediction-without-scope", "prediction-scope-missing-set-and-trace"),
    )),
    "014": _law("014", "SFT-CHEM-CLASSICAL-QUANTUM-ALGORITHM-CORRESPONDENCE-014", "Fold classical and quantum chemical algorithm correspondence law", "The same admitted chemical transition executed by a classical exact machine and a reversible complete-support Fold machine has one branchwise state projection and the same observed terminal carrier.", ("SFT-CHEM-OPERATIONAL-CLASSICAL-QUANTUM-CORRESPONDENCE-015", "SFT-COMP-FORM-UNIVERSALITY-001"), (
        ("chemistry", "different-classical-quantum-chemical-laws", "one-shared-admitted-chemical-law"),
        ("input", "different-mode-specific-inputs", "one-held-chemical-input-carrier"),
        ("classical", "opaque-classical-library-output", "exact-classical-transition-trace"),
        ("quantum", "amplitude-only-output", "complete-reversible-branchwise-trace"),
        ("mapping", "statistical-output-similarity", "exact-branch-state-projection"),
        ("observation", "collapse-erases-record", "held-observation-and-retained-record"),
        ("resource", "unreported-mode-cost", "separate-time-space-branch-record-cost"),
        ("terminal", "approximately-same-result", "identical-canonical-terminal-carrier"),
    )),
}


__all__ = (
    "ExactAtom", "ExactBond", "MolecularGraph", "ReactionGraph", "ExactSimilarityVector",
    "ProvenanceRecord", "canonical_graph_code", "graph_isomorphic", "subgraph_embeddings",
    "enumerate_constitutional_graphs", "enumerate_stereoisomers", "enumerate_conformer_words",
    "mechanism_paths", "exact_similarity_vector", "symbolic_property_vector",
    "applicability_boundary", "classical_quantum_correspondence", "LAW_ROWS",
)
