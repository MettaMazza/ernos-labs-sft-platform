"""Force finite graphs, paths, connectivity, trees, cuts and network balance."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-GRAPH-NETWORK-001"
Edge = tuple[str, str]


@dataclass(frozen=True)
class GeneratedGraph:
    nodes: tuple[str, ...]
    edges: tuple[Edge, ...]

    def __post_init__(self) -> None:
        if not self.nodes or len(set(self.nodes)) != len(self.nodes):
            raise ValueError("graph nodes must be a nonempty canonical collection")
        if len(set(self.edges)) != len(self.edges):
            raise ValueError("graph relation cannot repeat an edge")
        if any(origin not in self.nodes or target not in self.nodes for origin, target in self.edges):
            raise ValueError("every edge endpoint must belong to the node carrier")


def path_is_valid(graph: GeneratedGraph, path: tuple[str, ...]) -> bool:
    return bool(path) and all(node in graph.nodes for node in path) and all(
        (left, right) in graph.edges for left, right in zip(path, path[1:])
    )


def reachable(graph: GeneratedGraph, origin: str, target: str) -> bool:
    if origin == target:
        return origin in graph.nodes
    frontier = (origin,)
    visited: tuple[str, ...] = ()
    while frontier:
        held, frontier = frontier[0], frontier[1:]
        if held == target:
            return True
        if held in visited:
            continue
        visited += (held,)
        frontier += tuple(
            next_node for left, next_node in graph.edges if left == held and next_node not in visited
        )
    return False


def directed_cycle_exists(graph: GeneratedGraph) -> bool:
    def visit(node: str, held_path: tuple[str, ...]) -> bool:
        for left, right in graph.edges:
            if left != node:
                continue
            if right in held_path:
                return True
            if visit(right, held_path + (right,)):
                return True
        return False
    return any(visit(node, (node,)) for node in graph.nodes)


def crossing_cut(graph: GeneratedGraph, held_nodes: tuple[str, ...]) -> tuple[Edge, ...]:
    if not held_nodes or any(node not in graph.nodes for node in held_nodes):
        raise ValueError("a cut requires a nonempty held node selection")
    return tuple(
        edge for edge in graph.edges if (edge[0] in held_nodes) != (edge[1] in held_nodes)
    )


def internal_balance(incoming: tuple[tuple[str, ...], ...], outgoing: tuple[tuple[str, ...], ...]) -> bool:
    return bool(incoming) and len(incoming) == len(outgoing) and len(set(incoming)) == len(incoming) and len(set(outgoing)) == len(outgoing)


_chain = GeneratedGraph(("a", "b", "c"), (("a", "b"), ("b", "c")))
_cycle = GeneratedGraph(("a", "b", "c"), (("a", "b"), ("b", "c"), ("c", "a")))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite graph and network structure",
    statement=(
        "Every admitted finite graph is a complete canonical node collection plus a held selection of generated "
        "ordered node-pair relations; paths retain every adjacent transition, reachability is a complete finite "
        "path witness, cycles retain return, trees are connected cycle-free forms, cuts are exact crossing-edge "
        "selections, and internal network conservation is complete ingress/egress pairing."
    ),
    dependencies=(
        "SFT-FOUNDATION-FORM-GRAMMAR-001",
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    generation_rule=(
        "Generate the complete product of node coverage, edge provenance, orientation, path trace, connectivity, "
        "cycle return, cut support, internal balance and extra-network-rule status."
    ),
    grammar_boundary=(
        "All finite graphs and networks generated from canonical finite form carriers, held pair-cell relations, "
        "complete path traces, return relations and exact positive flow-token pairings."
    ),
    dimensions=(
        binary_dimension("nodes", "What fixes the vertex carrier?", "partial-or-aliased-nodes", "Missing or aliased nodes change the graph carrier.", "complete-canonical-nodes", "Every generated node form occurs once with canonical identity."),
        binary_dimension("edges", "What fixes edge membership?", "free-endpoint-list", "A free list can contain ungenerated endpoints or duplicate relations.", "held-pair-cell-relation", "Edges are a held duplicate-free selection of complete node pair support."),
        binary_dimension("orientation", "How is edge direction represented?", "signed-edge-weight", "A signed weight imports negative magnitude and does not identify endpoints.", "held-endpoint-order", "The ordered endpoint labels retain orientation; complementary order represents reversal."),
        binary_dimension("path", "What witnesses a path?", "endpoint-only", "Endpoints alone omit the intervening adjacency requirements.", "complete-adjacent-trace", "Every node and edge transition in the path is retained in order."),
        binary_dimension("connectivity", "What witnesses reachability?", "assumed-connected", "An assertion without a path omits the connecting structure.", "generated-path-witness", "Reachability requires a complete generated adjacent path."),
        binary_dimension("cycle", "What distinguishes a cycle?", "repeated-label-only", "A repeated label without a transition trace does not prove return.", "explicit-return-path", "A cycle is a nontrivial complete path whose terminal relation returns to a held prior node."),
        binary_dimension("cut", "How is a network cut derived?", "borrowed-scalar-threshold", "A scalar threshold imports an external coordinate.", "held-crossing-selection", "A held node selection forces exactly the edges with one held and one complementary endpoint."),
        binary_dimension("balance", "What expresses internal conservation?", "unaccounted-net-value", "A net signed value hides unmatched tokens.", "ingress-egress-pairing", "Every incoming positive token has one outgoing mate and conversely."),
        binary_dimension("addition", "Are graph laws added beyond generated relations?", "extra-network-rule", "An extra weight, metric or random law is not supplied by the graph dependencies.", "no-extra-network-rule", "All graph properties are witnessed by carriers, relations, paths, returns, selections and pairings."),
    ),
    exact_result=(
        "The graph/network kernel is complete canonical nodes with held ordered pair-cell edges, complete adjacent "
        "paths, witnessed reachability and return, held crossing cuts, ingress/egress pairing and no extra rule."
    ),
    laws=(
        "path concatenation is lawful exactly when the interface node agrees",
        "reachability is reflexive by the retained identity path and transitive by path composition",
        "a tree is a connected generated graph with no nontrivial return path",
        "a cut contains every and only relation crossing a held/complementary node partition",
        "network balance preserves token identity rather than cancelling signed magnitudes",
    ),
    induction_base="One canonical node supplies the identity path and contains no nontrivial edge cycle.",
    induction_step=(
        "Appending one fresh node generates exactly its ordered pair cells with prior nodes; any held edge selection "
        "extends paths locally, and connectivity, cycle, cut and balance witnesses update only through those new cells."
    ),
    boundary_exclusions=(
        "no ungenerated vertex or edge",
        "no negative edge or flow quantity",
        "no stochastic graph law",
        "no infinite graph as a completed object",
    ),
    witnesses=(
        Witness("valid-path", "The chain retains both required adjacent edges.", path_is_valid(_chain, ("a", "b", "c"))),
        Witness("missing-edge-control", "An endpoint sequence with a missing adjacency is not a path.", not path_is_valid(_chain, ("a", "c"))),
        Witness("reachability", "Generated path search reaches c from a and does not reach a from c in the directed chain.", reachable(_chain, "a", "c") and not reachable(_chain, "c", "a")),
        Witness("cycle-return", "The explicit c-to-a return distinguishes the cycle from the chain.", directed_cycle_exists(_cycle) and not directed_cycle_exists(_chain)),
        Witness("cut-selection", "Holding the first chain node selects exactly its crossing edge.", crossing_cut(_chain, ("a",)) == (("a", "b"),)),
        Witness("paired-balance", "Equal unique ingress and egress token traces witness internal balance.", internal_balance((("i1",), ("i2",)), (("o1",), ("o2",)))),
    ),
    why=(
        "Graphs are the minimal mathematics of explicit relations and paths. Their laws must follow from generated "
        "carriers and pair support rather than imported matrices, weights or probabilistic ensembles."
    ),
    derivation=(
        "Discrete mathematics supplies canonical carriers and relations; combinatorics supplies complete path-family "
        "generation. Exhausting nine structural choices leaves the relation/path/return/pairing graph kernel."
    ),
    check=(
        "Execute all 512 graph kernels, validate path and missing-edge controls, reachability, cycle return, cut "
        "selection and paired network balance, then independently regenerate the census."
    ),
    limitations=(
        "This law closes exact generated finite graph structure. Weighted geometry, random graphs, infinite graph "
        "limits and algorithmic graph complexity require later derived laws."
    ),
    correspondence_terms=("directed graph", "path", "reachability", "cycle", "tree", "cut", "network flow"),
)
