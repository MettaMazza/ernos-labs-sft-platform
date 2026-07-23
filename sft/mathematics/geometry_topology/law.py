"""Force computational finite geometry and topology without a continuum premise."""

from __future__ import annotations

from collections import deque

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-GEOMETRY-TOPOLOGY-001"
EMPTY_ONE = ("empty-One",)


def incidence_is_well_formed(cells: tuple[str, ...], boundary: tuple[tuple[str, str], ...]) -> bool:
    return bool(cells) and len(set(cells)) == len(cells) and len(set(boundary)) == len(boundary) and all(
        face in cells and cell in cells and face != cell for face, cell in boundary
    )


def cell_dimension(cells: tuple[str, ...], boundary: tuple[tuple[str, str], ...], cell: str) -> int:
    if not incidence_is_well_formed(cells, boundary) or cell not in cells:
        raise ValueError("dimension requires a registered finite incidence complex")
    visiting: set[str] = set()

    def depth(held: str) -> int:
        if held in visiting:
            raise ValueError("boundary descent cannot contain a return cycle")
        faces = tuple(face for face, target in boundary if target == held)
        if not faces:
            return 1
        visiting.add(held)
        result = 1 + max(depth(face) for face in faces)
        visiting.remove(held)
        return result

    return depth(cell)


def adjacent(boundary: tuple[tuple[str, str], ...], left: str, right: str) -> bool:
    left_faces = {face for face, cell in boundary if cell == left}
    right_faces = {face for face, cell in boundary if cell == right}
    return left != right and bool(left_faces.intersection(right_faces))


def path_distance(nodes: tuple[str, ...], edges: tuple[tuple[str, str], ...], origin: str, target: str):
    if origin not in nodes or target not in nodes:
        raise ValueError("distance endpoints must belong to the generated carrier")
    if origin == target:
        return EMPTY_ONE
    queue = deque(((origin, (origin,)),))
    visited: set[str] = set()
    while queue:
        node, path = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for left, right in edges:
            neighbor = right if left == node else left if right == node else None
            if neighbor is None or neighbor in visited:
                continue
            extended = path + (neighbor,)
            if neighbor == target:
                return extended
            queue.append((neighbor, extended))
    return None


def is_finite_topology(points: tuple[str, ...], opens: tuple[tuple[str, ...], ...]) -> bool:
    if not points or len(set(points)) != len(points):
        return False
    canonical = {
        tuple(point for point in points if point in held) or EMPTY_ONE
        for held in opens
    }
    if len(canonical) != len(opens) or EMPTY_ONE not in canonical or points not in canonical:
        return False
    for left in canonical:
        for right in canonical:
            union = tuple(point for point in points if point in left or point in right) or EMPTY_ONE
            intersection = tuple(point for point in points if point in left and point in right) or EMPTY_ONE
            if union not in canonical or intersection not in canonical:
                return False
    return True


def is_continuous(
    source_points: tuple[str, ...],
    source_opens: tuple[tuple[str, ...], ...],
    target_opens: tuple[tuple[str, ...], ...],
    mapping: tuple[tuple[str, str], ...],
) -> bool:
    images = dict(mapping)
    if set(images) != set(source_points):
        return False
    for target_open in target_opens:
        inverse = tuple(point for point in source_points if images[point] in target_open) or EMPTY_ONE
        if inverse not in source_opens:
            return False
    return True


_cells = ("p", "q", "r", "pq", "qr", "triangle")
_boundary = (("p", "pq"), ("q", "pq"), ("q", "qr"), ("r", "qr"), ("pq", "triangle"), ("qr", "triangle"))
_points = ("a", "b")
_discrete_opens = (EMPTY_ONE, ("a",), ("b",), _points)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite geometry and topology for computation",
    statement=(
        "Computational geometry is forced as canonical finite cells plus an acyclic held boundary-incidence "
        "relation; dimension is retained boundary depth, adjacency is shared incidence, and distance is a shortest "
        "generated path with self-distance represented by empty One rather than numerical zero. Computational "
        "topology is a complete generated open-family closed under generated joins and pairwise intersections; "
        "continuity is exact inverse-image preservation."
    ),
    dependencies=(
        "SFT-FOUNDATION-PART-001",
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule=(
        "Generate the complete product of cell carrier, incidence, dimension, adjacency, path distance, open-family "
        "closure, connectedness, continuity, deformation and extra-geometric status."
    ),
    grammar_boundary=(
        "All finite incidence complexes, path geometries and finite open families generated from canonical forms, "
        "held boundary relations, exact path traces, selections, joins and intersections."
    ),
    dimensions=(
        binary_dimension("cells", "What fixes geometric objects?", "coordinate-samples", "Samples from a borrowed coordinate field omit structural provenance.", "canonical-generated-cells", "Every cell is an exact canonical generated form."),
        binary_dimension("incidence", "What fixes boundary?", "assumed-containment", "Assumed containment has no exact face-to-cell witness.", "held-acyclic-boundary", "Every face relation is retained and boundary descent forbids return."),
        binary_dimension("dimension", "What fixes dimension?", "borrowed-coordinate-count", "A coordinate count imports an ambient space.", "boundary-chain-depth", "Dimension is the longest retained face-descent trace."),
        binary_dimension("adjacency", "What fixes adjacency?", "metric-threshold", "A threshold imports a free scale.", "shared-incidence-witness", "Cells are adjacent exactly when they share a generated face."),
        binary_dimension("distance", "What fixes computational distance?", "floating-metric", "A floating metric imports precision and possibly irrational values.", "shortest-generated-path", "Distance is the complete least-length path trace; identity is empty One."),
        binary_dimension("opens", "What fixes a finite topology?", "named-neighborhoods", "Named neighborhoods need not satisfy closure.", "generated-open-family-closure", "Empty One, whole, generated joins and pairwise intersections remain in the family."),
        binary_dimension("connectedness", "What fixes connectedness?", "visual-continuity", "A presentation cannot establish structural connection.", "no-disjoint-open-separation", "No two nonempty disjoint admitted opens jointly exhaust the carrier."),
        binary_dimension("continuity", "What fixes continuity?", "epsilon-scale", "An imported scale is neither forced nor needed in the finite grammar.", "inverse-open-preservation", "Every target open has an admitted source inverse image."),
        binary_dimension("deformation", "What fixes deformation equivalence?", "untracked-shape-change", "An untracked change can erase incidence.", "reversible-incidence-trace", "Each elementary change retains a lawful reverse and preserves registered incidence invariants."),
        binary_dimension("addition", "Is an ambient continuum added?", "continuum-or-extra-metric", "A continuum or metric field is outside the generated computational need.", "no-ambient-continuum", "The law uses only finite generated cells, paths and open families."),
    ),
    exact_result=(
        "The geometry/topology kernel is finite canonical cells with held acyclic incidence, boundary-depth "
        "dimension, shared-face adjacency, exact shortest paths, closed finite open families, inverse-image "
        "continuity and reversible incidence-preserving deformation."
    ),
    laws=(
        "cell dimension is determined by complete acyclic boundary descent",
        "path distance retains a shortest generated transition trace and uses empty One at identity",
        "finite topological closure is exhaustively decidable from the registered open family",
        "continuity is exact inverse-image preservation of every admitted target open",
        "geometric equivalence requires a reversible invariant-preserving transformation trace",
    ),
    induction_base="One point is a canonical cell; its open family consists of empty One and the whole point carrier.",
    induction_step=(
        "Adding one fresh cell generates its possible boundary incidences, shared-face adjacencies and path edges; "
        "adding one fresh point generates exactly the open selections needed for closure checks. Every new boundary, "
        "path, intersection, join and inverse image is then exhaustively tested."
    ),
    boundary_exclusions=(
        "no ungenerated continuum",
        "no irrational or floating proof coordinate",
        "no free metric threshold",
        "no completed infinite topological family",
    ),
    witnesses=(
        Witness("incidence", "Every witness face and cell belongs to the finite carrier.", incidence_is_well_formed(_cells, _boundary)),
        Witness("dimension-depth", "The witness triangle has one more boundary layer than its edge.", cell_dimension(_cells, _boundary, "triangle") == 3 and cell_dimension(_cells, _boundary, "pq") == 2),
        Witness("adjacency", "The two witness edges are adjacent exactly through their shared q face.", adjacent(_boundary, "pq", "qr")),
        Witness("path-distance", "Shortest path retains a-to-b-to-c and identity returns empty One.", path_distance(("a", "b", "c"), (("a", "b"), ("b", "c")), "a", "c") == ("a", "b", "c") and path_distance(("a", "b"), (("a", "b"),), "a", "a") == EMPTY_ONE),
        Witness("finite-topology", "The complete two-point selection family is closed.", is_finite_topology(_points, _discrete_opens)),
        Witness("continuity", "The identity map preserves every witness open by inverse image.", is_continuous(_points, _discrete_opens, _discrete_opens, (("a", "a"), ("b", "b")))),
    ),
    why=(
        "Algorithms need incidence, locality, paths, neighborhoods and continuity, but do not require importing a "
        "real-coordinate continuum. The finite structural form is the exact computationally required kernel."
    ),
    derivation=(
        "Graphs supply paths and incidence; orders supply joins and intersections; exact parts supply held/whole "
        "selection. The ten-dimensional census forces the finite incidence-and-open-family kernel."
    ),
    check=(
        "Execute all 1,024 kernels, test incidence and boundary depth, shortest-path identity, finite topology "
        "closure and inverse-image continuity, then regenerate the full candidate product independently."
    ),
    limitations=(
        "This closes geometry and topology where finite computation requires them. Smooth, differential, measure "
        "and continuum correspondences are not premises and require separate generated approximation laws if used."
    ),
    correspondence_terms=("incidence complex", "dimension", "adjacency", "metric", "topology", "continuity", "homotopy"),
)
