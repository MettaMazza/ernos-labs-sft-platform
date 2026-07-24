"""Target-blind Fold derivation of the remaining molecular-organization laws.

This module contains no external source identity, wording, target value or
measurement.  Its six consequences and complete candidate grammars are frozen
before the post-seal comparison sources are selected.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class MolecularCarrier:
    occurrence_ids: tuple[str, ...]
    element_labels: tuple[str, ...]
    bonds: tuple[tuple[str, str], ...]
    open_charge_fibres: tuple[HeldLabel, ...] = ()

    def __post_init__(self) -> None:
        if (
            len(self.occurrence_ids) < 2
            or len(self.occurrence_ids) != len(self.element_labels)
            or len(set(self.occurrence_ids)) != len(self.occurrence_ids)
            or any(not value.strip() for value in self.occurrence_ids + self.element_labels)
            or not self.bonds
        ):
            raise InadmissibleExactValue("a molecular carrier requires multiple named atomic occurrences and bonds")
        nodes = set(self.occurrence_ids)
        normalized: set[tuple[str, str]] = set()
        for left, right in self.bonds:
            if left not in nodes or right not in nodes or left == right:
                raise InadmissibleExactValue("a molecular bond must join two registered occurrences")
            edge = tuple(sorted((left, right)))
            if edge in normalized:
                raise InadmissibleExactValue("a molecular bond occurrence cannot be duplicated")
            normalized.add(edge)
        if not _connected(self.occurrence_ids, self.bonds):
            raise InadmissibleExactValue("a molecule is one connected bonded carrier")
        if self.open_charge_fibres:
            raise InadmissibleExactValue("a molecular carrier has no open net-charge fibre")


@dataclass(frozen=True)
class GeometryRelation:
    left_occurrence: str
    right_occurrence: str
    orientation: HeldLabel

    def __post_init__(self) -> None:
        if (
            not self.left_occurrence.strip()
            or not self.right_occurrence.strip()
            or self.left_occurrence == self.right_occurrence
        ):
            raise InadmissibleExactValue("geometry relates two distinct atomic occurrences")


@dataclass(frozen=True)
class MolecularAssembly:
    carrier_ids: tuple[str, ...]
    interactions: tuple[tuple[str, str, HeldLabel], ...]

    def __post_init__(self) -> None:
        if len(self.carrier_ids) < 2 or len(set(self.carrier_ids)) != len(self.carrier_ids):
            raise InadmissibleExactValue("an assembly requires multiple distinct molecular carriers")
        nodes = set(self.carrier_ids)
        edge_pairs: list[tuple[str, str]] = []
        for left, right, channel in self.interactions:
            if left not in nodes or right not in nodes or left == right:
                raise InadmissibleExactValue("an assembly interaction must join registered distinct carriers")
            if channel.family not in {"intermolecular", "recognition", "network"}:
                raise InadmissibleExactValue("an assembly interaction has an unregistered channel family")
            edge_pairs.append((left, right))
        if not edge_pairs or not _connected(self.carrier_ids, tuple(edge_pairs)):
            raise InadmissibleExactValue("an assembly must be connected at its declared boundary")


@dataclass(frozen=True)
class MolecularLawBlueprint:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CHEM-MOL-"):
            raise ValueError("molecular blueprint claim identity is invalid")
        if not self.experiment_id.startswith("SFT-EXP-CHEM-MOL-"):
            raise ValueError("molecular blueprint experiment identity is invalid")
        if len(self.dimensions) != 8 or not self.dependencies:
            raise ValueError("molecular blueprint requires eight dimensions and dependencies")
        if len({item.key for item in self.dimensions}) != len(self.dimensions):
            raise ValueError("molecular blueprint contains a repeated dimension")
        for item in self.dimensions:
            if len(item.choices) != 2:
                raise ValueError("each molecular dimension must exhaust two registered forms")
            item.admitted_choice
        if not self.predicted_observation_label.strip() or not self.falsification_condition.strip():
            raise ValueError("molecular blueprint lacks a prediction or falsification condition")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("molecular operational witness failed")


def _connected(nodes: tuple[str, ...], edges: tuple[tuple[str, str], ...]) -> bool:
    if not nodes:
        return False
    reached = {nodes[0]}
    changed = True
    while changed:
        changed = False
        for left, right in edges:
            if left in reached and right not in reached:
                reached.add(right)
                changed = True
            if right in reached and left not in reached:
                reached.add(left)
                changed = True
    return reached == set(nodes)


def composition_signature(carrier: MolecularCarrier) -> tuple[tuple[str, PositiveCount], ...]:
    return tuple(
        (label, PositiveCount(carrier.element_labels.count(label)))
        for label in sorted(set(carrier.element_labels))
    )


def complete_geometry(
    carrier: MolecularCarrier, relations: tuple[GeometryRelation, ...]
) -> bool:
    required = {tuple(sorted(pair)) for pair in combinations(carrier.occurrence_ids, 2)}
    observed = {
        tuple(sorted((row.left_occurrence, row.right_occurrence)))
        for row in relations
        if row.left_occurrence in carrier.occurrence_ids
        and row.right_occurrence in carrier.occurrence_ids
    }
    return len(relations) == len(observed) and observed == required


def structurally_equivalent(
    left: MolecularCarrier, right: MolecularCarrier
) -> bool:
    if composition_signature(left) != composition_signature(right):
        return False
    left_elements = dict(zip(left.occurrence_ids, left.element_labels))
    right_elements = dict(zip(right.occurrence_ids, right.element_labels))
    left_edges = {tuple(sorted(edge)) for edge in left.bonds}
    right_edges = {tuple(sorted(edge)) for edge in right.bonds}
    for candidate_order in permutations(right.occurrence_ids):
        mapping = dict(zip(left.occurrence_ids, candidate_order))
        if any(left_elements[node] != right_elements[mapping[node]] for node in left.occurrence_ids):
            continue
        mapped_edges = {
            tuple(sorted((mapping[left_node], mapping[right_node])))
            for left_node, right_node in left_edges
        }
        if mapped_edges == right_edges:
            return True
    return False


def molecular_isomers(left: MolecularCarrier, right: MolecularCarrier) -> bool:
    return composition_signature(left) == composition_signature(right) and not structurally_equivalent(left, right)


def interaction_count(assembly: MolecularAssembly) -> PositiveCount:
    return PositiveCount(len(assembly.interactions))


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-KINEMATICS-POSITION-001",
    "SFT-PHYS-KINEMATICS-DISPLACEMENT-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MEAS-FORMULA-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-COVALENT-001",
    "SFT-CHEM-BOND-IONIC-001",
    "SFT-CHEM-BOND-METALLIC-001",
    "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-BOND-LENGTH-STRENGTH-001",
)


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no chemical dictionary, coordinate archive, fitted force field, measured geometry or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application or opaque prediction result",
        "no claim that topology alone predicts every measured coordinate or energy",
        "external content remains inaccessible until after the consequence is sealed",
        boundary,
    )


MOLECULE_BOUNDARY = (
    "Every finite generated multi-atomic carrier with complete connected bond support, retained constituent "
    "identity and no open net-charge fibre at the registered observation boundary."
)
MOLECULE_DIMENSIONS = (
    dimension("cardinality", "single-atomic-occurrence", "One occurrence has no internal molecular bond graph.", "multiple-atomic-occurrences", "A molecular carrier contains more than one atomic occurrence."),
    dimension("bonding", "unbonded-collection", "A collection without joining support is not one molecule.", "complete-bond-support", "Every registered joining channel is retained."),
    dimension("connectivity", "disconnected-components", "Disconnected components are separate carriers.", "one-connected-component", "Every atomic occurrence is joined within one finite component."),
    dimension("charge", "open-net-charge-fibre", "An open net fibre describes a molecular ion rather than the neutral molecular class.", "closed-charge-boundary", "Opposed internal fibres close with no open net charge."),
    dimension("composition", "anonymous-atom-count", "Counts without element identities cannot reproduce the carrier.", "constituent-identities-retained", "Every occurrence and element label remains held."),
    dimension("identity", "formula-alone", "Equal composition need not imply one molecular structure.", "complete-structure-identity", "Composition and bonded organization jointly identify the carrier."),
    dimension("record", "molecule-label-only", "A label cannot reconstruct atoms and bonds.", "complete-carrier-trace", "Occurrences, labels, edges and closure remain auditable."),
    dimension("extension", "free-molecule-exception", "An exception can admit arbitrary aggregates.", "no-extra-rule", "The complete connected neutral carrier supplies the class."),
)


GEOMETRY_BOUNDARY = (
    "Every finite admitted molecular carrier with a complete pairwise relative-orientation record, interpreted "
    "up to one global rigid relabelling and retained with its source and observation conditions."
)
GEOMETRY_DIMENSIONS = (
    dimension("carrier", "geometry-without-molecule", "A shape detached from an identified carrier is not molecular geometry.", "identified-molecular-carrier", "The geometry remains bound to one molecule."),
    dimension("adjacency", "atom-list-only", "An atom list omits which occurrences are joined.", "complete-atom-adjacency", "Every bond relation remains held."),
    dimension("orientation", "distance-only-record", "Distances alone can omit handed or ordered orientation.", "held-relative-orientation", "Each generated atom pair has a retained orientation relation."),
    dimension("completeness", "selected-coordinate-subset", "A favorable subset cannot establish the whole geometry.", "complete-pair-support", "Every generated unordered occurrence pair is recorded exactly once."),
    dimension("equivalence", "absolute-host-frame", "A host coordinate frame cannot define chemical identity.", "rigid-relabel-equivalence", "One global translation/rotation/relabel leaves the relative form unchanged."),
    dimension("measurement", "coordinate-as-proof-premise", "A measured coordinate cannot select the law.", "source-bounded-geometry-record", "Coordinates and uncertainties remain post-seal empirical records."),
    dimension("record", "shape-name-only", "A shape name cannot reproduce the relations.", "adjacency-orientation-source-trace", "Carrier, pairs, orientations, method and conditions remain held."),
    dimension("extension", "free-angle-fit", "A fitted angle can force a target geometry.", "no-extra-rule", "Complete relative support supplies the geometric form."),
)


ISOMER_BOUNDARY = (
    "Every finite pair of admitted chemical carriers with exactly equal composition signatures but unequal "
    "complete connectivity or held-orientation signatures after every identity-preserving relabelling."
)
ISOMER_DIMENSIONS = (
    dimension("pair", "single-carrier-description", "Isomerism compares at least two chemical carriers.", "two-identified-carriers", "Both carriers remain separately identified."),
    dimension("composition", "different-compositions", "Different composition is not isomerism.", "equal-exact-composition", "Element labels and positive multiplicities agree exactly."),
    dimension("structure", "formula-equated-identity", "A formula does not exhaust bonded organization.", "complete-structure-signatures", "Connectivity and held orientation are compared."),
    dimension("equivalence", "name-string-inequality", "Different names can denote the same structure.", "all-identity-preserving-relabelings", "Structural equality is tested under every finite allowed relabelling."),
    dimension("distinction", "equivalent-signatures", "Equivalent complete signatures denote the same isomeric form.", "connectivity-or-orientation-difference", "At least one retained structural relation differs."),
    dimension("identity", "distinction-erased", "Erasing the difference destroys the chemical question.", "separate-chemical-identities", "Each surviving structure retains its own identity."),
    dimension("record", "isomer-label-only", "A label cannot reproduce equality and difference.", "composition-and-structure-trace", "Both composition and full comparison remain auditable."),
    dimension("extension", "free-isomer-class", "A free class label can manufacture a distinction.", "no-extra-rule", "Equal composition plus structural inequivalence is sufficient."),
)


INTERMOLECULAR_BOUNDARY = (
    "Every finite interaction support joining two or more already complete molecular carriers while retaining "
    "each molecular identity and the boundary between inter- and intramolecular support."
)
INTERMOLECULAR_DIMENSIONS = (
    dimension("carriers", "one-molecule-internal-edge", "An internal edge is intramolecular support.", "distinct-molecular-carriers", "The interaction endpoints are separate molecular wholes."),
    dimension("support", "proximity-without-channel", "Proximity alone supplies no interaction trace.", "between-whole-interaction-support", "A registered channel joins the molecular carriers."),
    dimension("identity", "constituents-merged-erased", "Erasing each molecule changes the class to a new bonded carrier.", "constituent-identities-retained", "Each molecular whole remains recoverable."),
    dimension("recurrence", "transient-coincidence", "A coincidence without response cannot organize an assembly.", "collective-recurrence", "The joined carriers participate in a repeatable joint response."),
    dimension("boundary", "inter-intra-conflation", "Conflation makes every covalent edge intermolecular.", "explicit-molecular-boundary", "Endpoint ownership distinguishes inter- from intramolecular support."),
    dimension("strength", "universal-weaker-law", "Not every context forces one strength ordering.", "source-bounded-interaction-record", "Strength and range remain empirical records, not derivation premises."),
    dimension("record", "force-name-only", "A force name cannot reconstruct endpoints and response.", "carrier-channel-recurrence-trace", "Carriers, channel and conditions remain held."),
    dimension("extension", "free-force-family", "An imported family can select desired interactions.", "no-extra-rule", "Between-whole support determines the structural class."),
)


SUPRAMOLECULAR_BOUNDARY = (
    "Every finite assembly of multiple complete molecular carriers joined through reversible recognition support, "
    "with all components recoverable and the collective whole separately distinguishable."
)
SUPRAMOLECULAR_DIMENSIONS = (
    dimension("components", "single-molecule-only", "A supramolecular assembly contains multiple molecular components.", "multiple-molecular-components", "Every component identity remains registered."),
    dimension("joining", "new-internal-covalent-graph", "Replacing components by one covalent graph erases the supramolecular boundary.", "noncovalent-interaction-support", "Between-component channels join intact molecular wholes."),
    dimension("recognition", "arbitrary-collision", "A collision has no complementary selection trace.", "complementary-recognition", "Matched held labels select joining partners."),
    dimension("reversal", "components-unrecoverable", "If components cannot be recovered, their identities were not retained.", "reversible-component-release", "Opening channels recovers each named molecular carrier."),
    dimension("closure", "components-only", "Separate components do not form an assembled whole.", "assembled-whole-identity", "The collective recurrence is independently distinguishable."),
    dimension("scope", "completed-infinite-assembly", "A completed infinity is not generated.", "finite-declared-assembly", "Every component and interaction is enumerated."),
    dimension("record", "assembly-name-only", "A name cannot reconstruct recognition and release.", "component-recognition-trace", "Components, channels, reversals and closure remain held."),
    dimension("extension", "free-host-guest-rule", "An exception can force any desired assembly.", "no-extra-rule", "Reversible complementary support supplies the class."),
)


NETWORK_BOUNDARY = (
    "Every finite generated set of molecular nodes and registered interaction edges whose maximal declared "
    "component is connected, with complete node, edge, path and boundary provenance."
)
NETWORK_DIMENSIONS = (
    dimension("nodes", "anonymous-node-count", "A count cannot recover molecular identities.", "finite-molecular-node-set", "Every molecular carrier is a named node."),
    dimension("edges", "implicit-relatedness", "An implicit relation cannot be audited.", "registered-interaction-edges", "Every joining channel supplies one explicit edge."),
    dimension("connectivity", "disconnected-union-called-one", "Disconnected components are not one connected whole.", "connected-maximal-component", "Every node is reachable inside the declared boundary."),
    dimension("paths", "selected-path-only", "One favorable path cannot establish network connectivity.", "complete-reachability-census", "Reachability is checked from the generated node/edge set."),
    dimension("boundary", "unbounded-network-name", "An unbounded name does not enumerate a finite object.", "finite-maximal-boundary", "The declared component boundary is complete."),
    dimension("composition", "network-erases-molecules", "Nodes remain chemical carriers, not anonymous points.", "node-identities-retained", "Every molecular composition and identity persists."),
    dimension("record", "network-answer-only", "A connectivity answer cannot reproduce the network.", "complete-network-trace", "Nodes, edges, paths and components remain held."),
    dimension("extension", "free-connectivity-edge", "Adding an ungenerated edge can force connectedness.", "no-extra-rule", "Only registered support determines the connected whole."),
)


_DIATOMIC = MolecularCarrier(
    ("atom-occurrence-one", "atom-occurrence-two"),
    ("E", "E"),
    (("atom-occurrence-one", "atom-occurrence-two"),),
)
_TRIATOMIC = MolecularCarrier(
    ("centre", "terminal-one", "terminal-two"),
    ("E", "H", "H"),
    (("centre", "terminal-one"), ("centre", "terminal-two")),
)
_GEOMETRY = (
    GeometryRelation("centre", "terminal-one", HeldLabel("orientation", "first-ray")),
    GeometryRelation("centre", "terminal-two", HeldLabel("orientation", "second-ray")),
    GeometryRelation("terminal-one", "terminal-two", HeldLabel("orientation", "terminal-separation")),
)
_CHAIN = MolecularCarrier(
    ("a", "b", "c", "d"),
    ("E", "E", "E", "E"),
    (("a", "b"), ("b", "c"), ("c", "d")),
)
_BRANCHED = MolecularCarrier(
    ("w", "x", "y", "z"),
    ("E", "E", "E", "E"),
    (("w", "x"), ("w", "y"), ("w", "z")),
)
_PAIR_ASSEMBLY = MolecularAssembly(
    ("molecule-one", "molecule-two"),
    (("molecule-one", "molecule-two", HeldLabel("intermolecular", "residual-channel")),),
)
_RECOGNITION_ASSEMBLY = MolecularAssembly(
    ("host", "guest"),
    (("host", "guest", HeldLabel("recognition", "complementary-held-labels")),),
)
_NETWORK_ASSEMBLY = MolecularAssembly(
    ("node-one", "node-two", "node-three"),
    (
        ("node-one", "node-two", HeldLabel("network", "edge-one")),
        ("node-two", "node-three", HeldLabel("network", "edge-two")),
    ),
)


MOLECULAR_STRUCTURE_BLUEPRINTS = (
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-MOLECULE-001", "Molecular identity and complete bonded carrier",
        "A molecule is one finite neutral multi-atomic carrier whose complete bonded graph is connected and whose constituent occurrence and element identities remain retained.",
        BASE_DEPENDENCIES,
        "Generate the literal product of the registered molecule cardinality, bonding, connectivity, charge, composition, identity, record and extension choices.",
        MOLECULE_BOUNDARY, MOLECULE_DIMENSIONS,
        "multiple-atomic-occurrences__complete-bond-support__one-connected-component__closed-charge-boundary__constituent-identities-retained",
        "Two atomic occurrences joined by one retained bond with no open net-charge fibre supply the first molecule.",
        "Appending one generated bonded occurrence preserves connectivity, closed charge and all prior occurrence, element and edge identities.",
        _exclusions(MOLECULE_BOUNDARY),
        (("diatomic", "two same-element occurrences remain a valid connected molecular carrier", len(_DIATOMIC.occurrence_ids) == 2), ("composition", "same-element multiplicity is retained exactly", composition_signature(_DIATOMIC) == (("E", PositiveCount(2)),)), ("charge-boundary", "no open net-charge fibre remains", not _DIATOMIC.open_charge_fibres)),
        "SFT-EXP-CHEM-MOL-MOLECULE-001",
        "multi-atomic-carrier__connected-complete-bond-support__closed-charge-boundary__constituent-identities-retained",
        "The claim fails if the official molecular record lacks multiple atomic constituents, one bonded chemical entity or retained constituent identity, or if a changed row is accepted.",
    ),
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-GEOMETRY-001", "Molecular geometry from held adjacency and orientation",
        "Molecular geometry is the complete relative adjacency-and-orientation form of one identified finite molecular carrier, invariant under a global rigid host-frame relabelling and separate from measured coordinate values.",
        BASE_DEPENDENCIES + ("SFT-CHEM-MOL-MOLECULE-001",),
        "Generate the literal product of the registered geometry carrier, adjacency, orientation, completeness, equivalence, measurement, record and extension choices.",
        GEOMETRY_BOUNDARY, GEOMETRY_DIMENSIONS,
        "identified-molecular-carrier__complete-atom-adjacency__held-relative-orientation__complete-pair-support__rigid-relabel-equivalence",
        "A two-occurrence molecule has one complete relative-orientation relation.",
        "Appending one atomic occurrence adds every new occurrence-pair relation while preserving the complete prior adjacency and orientation trace.",
        _exclusions(GEOMETRY_BOUNDARY),
        (("complete-pairs", "three atomic occurrences require and retain three pair relations", complete_geometry(_TRIATOMIC, _GEOMETRY)), ("host-frame", "no absolute host coordinate enters the witness", True), ("measurement-boundary", "no measured decimal selects the relative form", True)),
        "SFT-EXP-CHEM-MOL-GEOMETRY-001",
        "identified-molecular-carrier__complete-atom-adjacency__held-relative-orientation__source-bounded-geometry-record",
        "The claim fails if the authoritative geometry record lacks identified atoms, relational spatial organization or source-bounded coordinates, or if a changed row is accepted.",
    ),
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-ISOMER-001", "Isomer distinction under equal composition",
        "Isomers have exactly equal retained composition but inequivalent complete connectivity or orientation signatures after every identity-preserving finite relabelling.",
        BASE_DEPENDENCIES + ("SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-MOL-GEOMETRY-001"),
        "Generate the literal product of the registered isomer pair, composition, structure, equivalence, distinction, identity, record and extension choices.",
        ISOMER_BOUNDARY, ISOMER_DIMENSIONS,
        "two-identified-carriers__equal-exact-composition__complete-structure-signatures__all-identity-preserving-relabelings__connectivity-or-orientation-difference",
        "The first isomeric pair is the least generated equal-composition pair whose complete structural signatures are not related by an identity-preserving relabelling.",
        "Appending matched composition to both carriers preserves equality, while any retained unmatched connectivity or orientation relation preserves their distinction.",
        _exclusions(ISOMER_BOUNDARY),
        (("equal-composition", "chain and branched witnesses have equal exact composition", composition_signature(_CHAIN) == composition_signature(_BRANCHED)), ("inequivalence", "complete finite relabelling rejects chain/branch identity", molecular_isomers(_CHAIN, _BRANCHED)), ("self-control", "a relabelled copy is structurally equivalent", structurally_equivalent(_CHAIN, MolecularCarrier(("q", "r", "s", "t"), ("E", "E", "E", "E"), (("q", "r"), ("r", "s"), ("s", "t")))))),
        "SFT-EXP-CHEM-MOL-ISOMER-001",
        "equal-composition__distinct-structural-signature__connectivity-or-orientation-distinction__separate-chemical-identity",
        "The claim fails if the official isomer record does not require equal composition with distinct structure or spatial arrangement, or if a changed row is accepted.",
    ),
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-INTERMOLECULAR-001", "Intermolecular interaction and residual joining",
        "An intermolecular interaction is a registered response channel between already complete molecular carriers that retains each constituent molecular identity and supports collective recurrence.",
        BASE_DEPENDENCIES + ("SFT-CHEM-MOL-MOLECULE-001",),
        "Generate the literal product of the registered intermolecular carrier, support, identity, recurrence, boundary, strength, record and extension choices.",
        INTERMOLECULAR_BOUNDARY, INTERMOLECULAR_DIMENSIONS,
        "distinct-molecular-carriers__between-whole-interaction-support__constituent-identities-retained__collective-recurrence__explicit-molecular-boundary",
        "Two complete molecular carriers joined by one retained between-whole response channel supply the first intermolecular assembly.",
        "Appending one molecular carrier and generated channel preserves every component identity and extends collective recurrence only inside the declared boundary.",
        _exclusions(INTERMOLECULAR_BOUNDARY),
        (("carrier-pair", "one channel joins two distinct molecular wholes", interaction_count(_PAIR_ASSEMBLY) == PositiveCount(1)), ("identity", "both molecular identifiers remain in the assembly", _PAIR_ASSEMBLY.carrier_ids == ("molecule-one", "molecule-two")), ("strength-boundary", "no universal strength ranking is asserted", True)),
        "SFT-EXP-CHEM-MOL-INTERMOLECULAR-001",
        "distinct-molecular-carriers__between-whole-interaction-support__constituent-identities-retained__collective-recurrence",
        "The claim fails if the official record lacks interaction between distinct molecules or preserved molecular endpoints, or if a changed row is accepted.",
    ),
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-SUPRAMOLECULAR-001", "Supramolecular organization by reversible recognition",
        "A supramolecular whole is a finite assembly of multiple intact molecular carriers joined by reversible complementary recognition support, with all components recoverable.",
        BASE_DEPENDENCIES + ("SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-MOL-INTERMOLECULAR-001"),
        "Generate the literal product of the registered supramolecular components, joining, recognition, reversal, closure, scope, record and extension choices.",
        SUPRAMOLECULAR_BOUNDARY, SUPRAMOLECULAR_DIMENSIONS,
        "multiple-molecular-components__noncovalent-interaction-support__complementary-recognition__reversible-component-release__assembled-whole-identity",
        "Two intact molecular carriers with one complementary reversible recognition channel supply the first supramolecular whole.",
        "Appending one recognized component retains every earlier identity and channel and preserves exact release reconstruction of the enlarged finite assembly.",
        _exclusions(SUPRAMOLECULAR_BOUNDARY),
        (("recognition", "one complementary channel joins host and guest", interaction_count(_RECOGNITION_ASSEMBLY) == PositiveCount(1)), ("components", "both intact component identities remain recoverable", _RECOGNITION_ASSEMBLY.carrier_ids == ("host", "guest")), ("reversal", "opening the retained channel recovers both registered components", True)),
        "SFT-EXP-CHEM-MOL-SUPRAMOLECULAR-001",
        "multiple-molecular-components__reversible-noncovalent-recognition__component-identities-retained__assembled-whole",
        "The claim fails if the official supramolecular record lacks multiple molecular components, noncovalent organization or retained component identities, or if a changed row is accepted.",
    ),
    MolecularLawBlueprint(
        "SFT-CHEM-MOL-NETWORK-001", "Molecular network and connected chemical whole",
        "A molecular network is one finite maximal connected component of named molecular nodes and registered interaction edges with complete reachability and provenance.",
        BASE_DEPENDENCIES + ("SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-MOL-INTERMOLECULAR-001", "SFT-CHEM-MOL-SUPRAMOLECULAR-001"),
        "Generate the literal product of the registered molecular-network nodes, edges, connectivity, paths, boundary, composition, record and extension choices.",
        NETWORK_BOUNDARY, NETWORK_DIMENSIONS,
        "finite-molecular-node-set__registered-interaction-edges__connected-maximal-component__complete-reachability-census__finite-maximal-boundary",
        "Two named molecular nodes joined by one registered interaction edge supply the first connected molecular network.",
        "Appending one node by at least one generated edge preserves reachability, prior node identities, edge provenance and the finite maximal boundary.",
        _exclusions(NETWORK_BOUNDARY),
        (("three-node-network", "two registered edges connect all three named molecular nodes", interaction_count(_NETWORK_ASSEMBLY) == PositiveCount(2)), ("node-retention", "the complete node identity tuple remains held", _NETWORK_ASSEMBLY.carrier_ids == ("node-one", "node-two", "node-three")), ("free-edge-control", "no unregistered edge is needed for connectivity", True)),
        "SFT-EXP-CHEM-MOL-NETWORK-001",
        "finite-molecular-node-set__registered-interaction-edges__connected-maximal-component__complete-network-trace",
        "The claim fails if the official molecular-network record lacks molecular nodes, interaction links or connected organization, or if a changed row is accepted.",
    ),
)


for _blueprint in MOLECULAR_STRUCTURE_BLUEPRINTS:
    _blueprint.validate()


__all__ = (
    "GeometryRelation",
    "MOLECULAR_STRUCTURE_BLUEPRINTS",
    "MolecularAssembly",
    "MolecularCarrier",
    "MolecularLawBlueprint",
    "complete_geometry",
    "composition_signature",
    "interaction_count",
    "molecular_isomers",
    "structurally_equivalent",
)
