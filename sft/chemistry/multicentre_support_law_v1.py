"""Fold-native multicentre and delocalized molecular support for ELEC-008."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import FoldWord
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


RIBBON = HeldLabel("delocalized-topology", "ribbon-path")
SURFACE = HeldLabel("delocalized-topology", "surface-cycle")
VOLUME = HeldLabel("delocalized-topology", "volume-polyhedron")


@dataclass(frozen=True)
class SupportEdge:
    left: HeldLabel
    right: HeldLabel

    def __post_init__(self) -> None:
        if self.left.family != "molecular-centre" or self.right.family != "molecular-centre":
            raise InadmissibleExactValue("multicentre support edges require retained molecular centres")
        if self.left == self.right:
            raise InadmissibleExactValue("a support edge cannot erase its endpoint distinction")

    @property
    def unordered_key(self) -> frozenset[HeldLabel]:
        return frozenset((self.left, self.right))


@dataclass(frozen=True)
class DelocalizedMolecularSupport:
    molecular_carrier: HeldLabel
    topology: HeldLabel
    centres: tuple[HeldLabel, ...]
    edges: tuple[SupportEdge, ...]
    electron_support: FoldWord

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("delocalized support requires one retained molecular carrier")
        if self.topology not in (RIBBON, SURFACE, VOLUME):
            raise InadmissibleExactValue("delocalized support requires one generated topology")
        if len(self.centres) < 3 or len(set(self.centres)) != len(self.centres):
            raise InadmissibleExactValue("multicentre support requires at least three distinct retained centres")
        if any(centre.family != "molecular-centre" for centre in self.centres):
            raise InadmissibleExactValue("every multicentre vertex must retain its molecular-centre identity")
        if len({edge.unordered_key for edge in self.edges}) != len(self.edges):
            raise InadmissibleExactValue("multicentre support contains a duplicate undirected edge")
        if any(edge.left not in self.centres or edge.right not in self.centres for edge in self.edges):
            raise InadmissibleExactValue("multicentre support edge escapes its registered centres")
        if self.electron_support.cells != self.centres:
            raise InadmissibleExactValue("one delocalized electron support must retain every centre exactly once")
        if not _connected(self.centres, self.edges):
            raise InadmissibleExactValue("delocalized molecular support must be connected")
        degrees = _degrees(self.centres, self.edges)
        if self.topology == RIBBON and not (
            len(self.edges) + 1 == len(self.centres)
            and tuple(sorted(degrees.values())).count(1) == 2
            and all(value in (1, 2) for value in degrees.values())
        ):
            raise InadmissibleExactValue("ribbon support must be one connected generated path")
        if self.topology == SURFACE and not (
            len(self.edges) == len(self.centres) and all(value == 2 for value in degrees.values())
        ):
            raise InadmissibleExactValue("surface support must be one connected generated cycle")
        if self.topology == VOLUME and not (
            len(self.centres) >= 4
            and len(self.edges) > len(self.centres)
            and any(value >= 3 for value in degrees.values())
        ):
            raise InadmissibleExactValue("volume support must contain a connected polyhedral branch")

    @property
    def positive_centre_count(self) -> PositiveCount:
        return PositiveCount(len(self.centres))

    @property
    def positive_edge_count(self) -> PositiveCount:
        return PositiveCount(len(self.edges))

    @property
    def irreducible_to_one_localized_pair(self) -> bool:
        return len(self.centres) >= 3 and all(cell in self.centres for cell in self.electron_support.cells)


def _degrees(centres: tuple[HeldLabel, ...], edges: tuple[SupportEdge, ...]) -> dict[HeldLabel, int]:
    return {centre: sum(centre in edge.unordered_key for edge in edges) for centre in centres}


def _connected(centres: tuple[HeldLabel, ...], edges: tuple[SupportEdge, ...]) -> bool:
    reached = {centres[0]}
    changed = True
    while changed:
        before = len(reached)
        for edge in edges:
            if edge.left in reached or edge.right in reached:
                reached.update((edge.left, edge.right))
        changed = len(reached) > before
    return len(reached) == len(centres)


def _centres(labels: tuple[str, ...]) -> tuple[HeldLabel, ...]:
    return tuple(HeldLabel("molecular-centre", label) for label in labels)


def _support(molecule: str, topology: HeldLabel, labels: tuple[str, ...], pairs: tuple[tuple[int, int], ...]) -> DelocalizedMolecularSupport:
    centres = _centres(labels)
    edges = tuple(SupportEdge(centres[left], centres[right]) for left, right in pairs)
    return DelocalizedMolecularSupport(HeldLabel("molecular-carrier", molecule), topology, centres, edges, FoldWord(centres))


def ribbon_support(molecule: str, labels: tuple[str, ...]) -> DelocalizedMolecularSupport:
    if len(labels) < 3:
        raise InadmissibleExactValue("ribbon support requires at least three centre labels")
    return _support(molecule, RIBBON, labels, tuple((position, position + 1) for position in range(len(labels) - 1)))


def surface_cycle_support(molecule: str, labels: tuple[str, ...]) -> DelocalizedMolecularSupport:
    if len(labels) < 3:
        raise InadmissibleExactValue("surface support requires at least three centre labels")
    pairs = tuple((position, position + 1) for position in range(len(labels) - 1)) + ((len(labels) - 1, 0),)
    return _support(molecule, SURFACE, labels, pairs)


def tetrahedral_volume_support(molecule: str, labels: tuple[str, str, str, str]) -> DelocalizedMolecularSupport:
    return _support(molecule, VOLUME, labels, ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)))


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006",
    "SFT-CHEM-JOINT-CORRELATION-DISSOCIATION-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "isolated-bond-list", "A list erases the single molecular carrier joining the support.", "complete-molecular-carrier", "One carrier retains the complete connected support."),
    dimension("centres", "two-centre-only-premise", "A two-centre restriction excludes generated supports before enumeration.", "three-or-more-generated-centres", "Every positive finite support of at least three retained centres remains admissible for testing."),
    dimension("support", "localized-edge-identities", "Separate edge identities cannot preserve one electron-support identity spanning the graph.", "one-complete-extended-support", "One held electron support retains every centre of the connected graph."),
    dimension("connection", "disconnected-centre-union", "A disconnected union is not one molecular support.", "connected-generated-graph", "Every retained centre is reachable through generated support edges."),
    dimension("topology", "imported-or-single-topology", "Selecting one familiar shape omits lawful connected alternatives.", "ribbon-surface-volume-census", "Path, cycle and polyhedral branch arise from exact graph incidence."),
    dimension("reduction", "pairwise-model-declared-complete", "Independent localized pairs erase the one support identity extending beyond either endpoint.", "multicentre-irreducible-support", "At least three centres occur in one indivisible support word."),
    dimension("record", "selected-example-only", "One favourable example cannot test the registered topology and geometry surface.", "complete-authority-and-geometry-vector", "All IUPAC topology and NIST experimental geometry rows remain bound to provenance."),
    dimension("extension", "species-specific-extra-rule", "A species exception or empirical bonding model adds an unforced premise.", "connected-successor-with-no-extra-rule", "Adding a connected centre preserves the same support law without a new parameter."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    bridge = ribbon_support("diborane", ("B-left", "H-bridge", "B-right"))
    ring = surface_cycle_support("benzene", tuple(f"C-{position}" for position in range(1, 7)))
    volume = tetrahedral_volume_support("tetrahedrane", ("C-one", "C-two", "C-three", "C-four"))
    localized_rejected = disconnected_rejected = False
    try:
        ribbon_support("invalid", ("left", "right"))
    except InadmissibleExactValue:
        localized_rejected = True
    try:
        centres = _centres(("one", "two", "three"))
        DelocalizedMolecularSupport(HeldLabel("molecular-carrier", "invalid"), RIBBON, centres, (SupportEdge(centres[0], centres[1]),), FoldWord(centres))
    except InadmissibleExactValue:
        disconnected_rejected = True
    return (
        ("three-centre-bridge", "One connected support spans B-left, bridging H and B-right.", bridge.positive_centre_count == PositiveCount(3) and bridge.irreducible_to_one_localized_pair),
        ("six-centre-cycle", "One surface support spans all six cyclic carbon centres.", ring.positive_centre_count == PositiveCount(6) and ring.positive_edge_count == PositiveCount(6)),
        ("four-centre-volume", "One volume support spans the complete tetrahedral graph.", volume.positive_centre_count == PositiveCount(4) and volume.positive_edge_count == PositiveCount(6)),
        ("two-centre-control", "A pair cannot be relabelled as multicentre support.", localized_rejected),
        ("disconnected-control", "An omitted connection cannot be relabelled as one delocalized support.", disconnected_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "complete-molecular-carrier__three-or-more-generated-centres__one-complete-extended-support__connected-generated-graph__ribbon-surface-volume-census__multicentre-irreducible-support__complete-authority-and-geometry-vector__connected-successor-with-no-extra-rule"


__all__ = ("DEPENDENCIES", "DIMENSIONS", "DelocalizedMolecularSupport", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "RIBBON", "SURFACE", "SupportEdge", "VOLUME", "ribbon_support", "surface_cycle_support", "tetrahedral_volume_support")
