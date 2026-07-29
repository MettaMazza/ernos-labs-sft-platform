"""Fold-native quantitative Polymer Chemistry laws for POLY-001--013.

The thirteen obligations are one frozen subfield batch.  The native objects in
this module are finite generated carriers.  Decimal inscriptions, published
polymer equations, fitted distributions, continuum chains and database answers
are comparison surfaces only and cannot select any law below.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


def _positive_fraction(value: Fraction | PositiveCount) -> Fraction:
    result = Fraction(value.value, 1) if isinstance(value, PositiveCount) else Fraction(value)
    if result <= 0:
        raise InadmissibleExactValue("polymer quantities require positive exact support")
    return result


@dataclass(frozen=True)
class PolymerPopulation:
    """Complete finite population by molecular size and positive multiplicity."""

    rows: tuple[tuple[Fraction, PositiveCount], ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise InadmissibleExactValue("polymer population requires at least one retained chain class")
        masses = tuple(_positive_fraction(mass) for mass, _ in self.rows)
        if len(set(masses)) != len(masses):
            raise InadmissibleExactValue("equal molecular sizes must be one retained multiplicity row")

    @property
    def chain_count(self) -> PositiveCount:
        return PositiveCount(sum(multiplicity.value for _, multiplicity in self.rows))

    def number_average(self) -> Fraction:
        numerator = sum(_positive_fraction(mass) * multiplicity.value for mass, multiplicity in self.rows)
        return numerator / self.chain_count.value

    def mass_average(self) -> Fraction:
        numerator = sum(_positive_fraction(mass) ** 2 * multiplicity.value for mass, multiplicity in self.rows)
        denominator = sum(_positive_fraction(mass) * multiplicity.value for mass, multiplicity in self.rows)
        return numerator / denominator

    def dispersity(self) -> Fraction:
        return self.mass_average() / self.number_average()


def degree_of_polymerization(chain_mass: Fraction, repeat_mass: Fraction, end_mass: Fraction | EmptyOne = EMPTY_ONE) -> Fraction:
    """Return the exact retained repeat count from complete mass custody."""

    total = _positive_fraction(chain_mass)
    repeat = _positive_fraction(repeat_mass)
    terminal = Fraction(0, 1) if end_mass == EMPTY_ONE else _positive_fraction(end_mass)
    if total <= terminal:
        raise InadmissibleExactValue("terminal support cannot exhaust the chain carrier")
    result = (total - terminal) / repeat
    if result <= 0:
        raise InadmissibleExactValue("degree of polymerization must retain positive extent")
    return result


@dataclass(frozen=True)
class PolymerTransition:
    source: str
    destination: str
    operation: str
    carrier_delta: tuple[tuple[str, str, PositiveCount], ...] = ()

    def __post_init__(self) -> None:
        if not self.source or not self.destination or not self.operation:
            raise InadmissibleExactValue("polymer transition requires held source, destination and operation")
        if any(hand not in {"retained", "joined", "released", "transferred"} for _, hand, _ in self.carrier_delta):
            raise InadmissibleExactValue("polymer carrier change requires a held orientation")


@dataclass(frozen=True)
class PolymerNetwork:
    states: tuple[str, ...]
    transitions: tuple[PolymerTransition, ...]

    def __post_init__(self) -> None:
        if not self.states or len(set(self.states)) != len(self.states):
            raise InadmissibleExactValue("polymer network requires distinct held states")
        if any(row.source not in self.states or row.destination not in self.states for row in self.transitions):
            raise InadmissibleExactValue("polymer transition leaves the declared state support")

    def paths(self, source: str, terminal: str) -> tuple[tuple[str, ...], ...]:
        if source not in self.states or terminal not in self.states:
            raise InadmissibleExactValue("path endpoints are outside the polymer network")
        complete: list[tuple[str, ...]] = []
        boundary = [(source, (), (source,))]
        while boundary:
            state, trace, visited = boundary.pop()
            if state == terminal:
                complete.append(trace)
                continue
            for row in self.transitions:
                if row.source == state and row.destination not in visited:
                    boundary.append((row.destination, trace + (row.operation,), visited + (row.destination,)))
        return tuple(sorted(complete))

    def operation_support(self) -> tuple[str, ...]:
        return tuple(sorted({row.operation for row in self.transitions}))


def step_growth_chain_count(initial_molecules: PositiveCount, intermolecular_bonds: PositiveCount | EmptyOne) -> PositiveCount:
    """Every intermolecular bond merges exactly two components into one."""

    bonds = 0 if intermolecular_bonds == EMPTY_ONE else intermolecular_bonds.value
    remaining = initial_molecules.value - bonds
    if remaining <= 0:
        raise InadmissibleExactValue("finite step-growth support cannot consume every component")
    return PositiveCount(remaining)


def labelled_composition(word: tuple[HeldLabel, ...]) -> tuple[tuple[str, Fraction], ...]:
    if not word:
        raise InadmissibleExactValue("copolymer sequence requires positive monomer support")
    if any(label.family != "polymer-monomer" for label in word):
        raise InadmissibleExactValue("copolymer word contains an unregistered label family")
    counts: dict[str, int] = {}
    for label in word:
        counts[label.label] = counts.get(label.label, 0) + 1
    return tuple((key, Fraction(value, len(word))) for key, value in sorted(counts.items()))


@dataclass(frozen=True)
class PolymerGraph:
    vertices: tuple[HeldLabel, ...]
    edges: tuple[tuple[PositiveCount, PositiveCount], ...]

    def __post_init__(self) -> None:
        if not self.vertices:
            raise InadmissibleExactValue("polymer graph requires positive carrier support")
        normalized: set[tuple[int, int]] = set()
        for left, right in self.edges:
            if left == right or left.value > len(self.vertices) or right.value > len(self.vertices):
                raise InadmissibleExactValue("polymer edge is outside its finite carrier support")
            edge = tuple(sorted((left.value, right.value)))
            if edge in normalized:
                raise InadmissibleExactValue("polymer edge identity is duplicated")
            normalized.add(edge)

    def degrees(self) -> tuple[int, ...]:
        return tuple(sum(position in (left.value, right.value) for left, right in self.edges) for position in range(1, len(self.vertices) + 1))

    def components(self) -> tuple[tuple[int, ...], ...]:
        unseen = set(range(1, len(self.vertices) + 1)); result = []
        while unseen:
            seed = min(unseen); found = {seed}; frontier = [seed]
            while frontier:
                current = frontier.pop()
                for left, right in self.edges:
                    pair = (left.value, right.value)
                    if current in pair:
                        neighbour = pair[1] if pair[0] == current else pair[0]
                        if neighbour not in found:
                            found.add(neighbour); frontier.append(neighbour)
            unseen -= found; result.append(tuple(sorted(found)))
        return tuple(sorted(result))

    def architecture(self) -> HeldLabel:
        degrees = self.degrees()
        if len(self.components()) > 1:
            return HeldLabel("polymer-architecture", "disconnected-population")
        branch_nodes = sum(value > 2 for value in degrees)
        ends = sum(value == 1 for value in degrees)
        if branch_nodes == 0 and ends <= 2:
            label = "linear"
        elif branch_nodes == 1 and ends > 2:
            label = "star-or-single-branch-centre"
        elif branch_nodes > 0 and len(self.edges) < len(self.vertices):
            label = "branched-acyclic"
        else:
            label = "crosslinked-network"
        return HeldLabel("polymer-architecture", label)

    def finite_gel_certificate(self, inlet: tuple[PositiveCount, ...], outlet: tuple[PositiveCount, ...]) -> tuple[HeldLabel, tuple[int, ...] | EmptyOne]:
        left = {item.value for item in inlet}; right = {item.value for item in outlet}
        if not left or not right or left & right:
            raise InadmissibleExactValue("finite gel test requires disjoint positive boundaries")
        for component in self.components():
            support = set(component)
            if support & left and support & right:
                return HeldLabel("polymer-gelation", "finite-boundaries-connected"), component
        return HeldLabel("polymer-gelation", "finite-boundaries-not-connected"), EMPTY_ONE


def squared_radius_of_gyration(points: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    """Exact finite chain-size relation; no square root or continuum walk."""

    if not points or not points[0] or any(len(point) != len(points[0]) for point in points):
        raise InadmissibleExactValue("chain conformation requires a finite common coordinate rank")
    rank = len(points[0]); count = len(points)
    centres = tuple(sum(Fraction(point[index]) for point in points) / count for index in range(rank))
    result = sum(sum((Fraction(point[index]) - centres[index]) ** 2 for index in range(rank)) for point in points) / count
    if result <= 0:
        raise InadmissibleExactValue("chain size requires distinguishable generated positions")
    return result


def phase_transition_trace(rows: tuple[tuple[PositiveCount, HeldLabel], ...]) -> tuple[tuple[int, str, str], ...]:
    if not rows or tuple(item[0].value for item in rows) != tuple(sorted(item[0].value for item in rows)):
        raise InadmissibleExactValue("polymer phase record requires ordered positive states")
    transitions = []
    for previous, current in zip(rows, rows[1:]):
        if previous[1] != current[1]:
            transitions.append((current[0].value, previous[1].label, current[1].label))
    return tuple(transitions)


def degradation_balance(initial_units: PositiveCount, fragments: tuple[PositiveCount, ...], released_units: PositiveCount | EmptyOne = EMPTY_ONE) -> bool:
    if not fragments:
        raise InadmissibleExactValue("degradation requires retained product support")
    released = 0 if released_units == EMPTY_ONE else released_units.value
    return sum(item.value for item in fragments) + released == initial_units.value


def chemistry_materials_handoff(chemical_record: tuple[object, ...], bulk_record: tuple[object, ...]) -> tuple[HeldLabel, str, str]:
    if not chemical_record or not bulk_record:
        raise InadmissibleExactValue("polymer handoff requires complete paired records")
    return HeldLabel("polymer-handoff", "complete-paired-records"), "chemistry", "materials"


COMMON_DEPS = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-POLYMER-CHAIN-001",
    "SFT-CHEM-POLYMER-DISTRIBUTION-001",
)


def _law(number: str, claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], decisions: tuple[tuple[str, str, str], ...]):
    if len(decisions) != 8:
        raise ValueError(f"POLY-{number} requires exactly eight exhaustive decisions")
    dimensions = tuple(dimension(key, rejected, f"{rejected} closes a distinction required by {key}.", survivor, f"{survivor} retains the complete {key} distinction.") for key, rejected, survivor in decisions)
    return {
        "claim_id": claim_id,
        "title": title,
        "statement": statement,
        "dependencies": tuple(dict.fromkeys(COMMON_DEPS + dependencies)),
        "dimensions": dimensions,
        "operational_witnesses": tuple((key, survivor, True) for key, _, survivor in decisions),
        "result": "__".join(survivor for _, _, survivor in decisions),
    }


LAW_ROWS = {
    "001": _law("001", "SFT-CHEM-DEGREE-OF-POLYMERIZATION-001", "Fold degree-of-polymerization law", "A complete finite chain forces its degree of polymerization as the exact positive repeat-unit count, equivalently the exact repeat-supported chain mass after separately retained end-group support is removed.", (), (
        ("carrier", "sample-average-without-chain", "one-complete-finite-chain-carrier"), ("repeat", "anonymous-backbone-mass", "held-repeat-unit-identity"), ("extent", "continuum-chain-length", "positive-exact-repeat-count"), ("mass", "total-mass-with-ends-conflated", "repeat-supported-mass-separated-from-ends"), ("ratio", "rounded-decimal-quotient", "exact-positive-rational-relation"), ("ends", "terminal-groups-erased", "terminal-support-retained"), ("population", "single-value-replaces-population", "per-chain-result-before-population-summary"), ("certificate", "degree-only-output", "chain-repeat-end-and-ratio-trace"))),
    "002": _law("002", "SFT-CHEM-NUMBER-AVERAGE-MOLECULAR-SIZE-002", "Fold number-average molecular-size law", "For a complete finite polymer population, the number-average molecular size is the exact sum of every chain size repeated by its positive multiplicity divided by the complete positive chain count.", ("SFT-CHEM-DEGREE-OF-POLYMERIZATION-001",), (
        ("population", "selected-representative-chains", "complete-resolved-chain-population"), ("sizes", "binned-or-rounded-sizes", "exact-positive-chain-sizes"), ("multiplicity", "duplicate-carriers-collapsed", "positive-multiplicity-per-size"), ("numerator", "unweighted-size-total", "multiplicity-weighted-size-total"), ("denominator", "mass-total-denominator", "complete-chain-count-denominator"), ("arithmetic", "floating-average", "exact-positive-rational-average"), ("scope", "unbounded-population-claim", "sample-and-method-boundary-retained"), ("certificate", "mean-only-output", "all-rows-sums-ratio-and-boundary-trace"))),
    "003": _law("003", "SFT-CHEM-MASS-WEIGHTED-MOLECULAR-SIZE-003", "Fold mass-weighted molecular-size law", "For a complete finite polymer population, the mass-weighted molecular size is the exact second size moment divided by the exact first size moment, with every multiplicity retained.", ("SFT-CHEM-NUMBER-AVERAGE-MOLECULAR-SIZE-002",), (
        ("population", "selected-heavy-chains", "complete-resolved-chain-population"), ("sizes", "nominal-class-labels", "exact-positive-chain-sizes"), ("multiplicity", "frequency-erased", "positive-multiplicity-per-size"), ("weight", "free-statistical-weight", "one-held-mass-copy-per-carrier-mass"), ("numerator", "first-moment-only", "complete-second-size-moment"), ("denominator", "chain-count-denominator", "complete-first-size-moment"), ("arithmetic", "floating-moment-ratio", "exact-positive-rational-moment-ratio"), ("certificate", "weighted-mean-only-output", "all-rows-moments-ratio-and-boundary-trace"))),
    "004": _law("004", "SFT-CHEM-POLYMER-DISPERSITY-004", "Fold polymer dispersity law", "Polymer dispersity is the exact positive ratio of the separately forced mass-weighted and number-average molecular sizes for the same complete source-bound population.", ("SFT-CHEM-MASS-WEIGHTED-MOLECULAR-SIZE-003",), (
        ("population", "different-populations-for-moments", "one-shared-complete-population"), ("number", "number-average-untraced", "forced-number-average-with-trace"), ("mass", "mass-average-untraced", "forced-mass-average-with-trace"), ("ratio", "subtracted-spread", "mass-average-over-number-average"), ("arithmetic", "floating-fit-statistic", "exact-positive-rational-result"), ("distribution", "named-distribution-assumption", "no-distribution-shape-assumed"), ("adverse", "unresolved-rows-discarded", "all-source-bound-rows-retained"), ("certificate", "scalar-only-output", "population-both-moments-ratio-and-boundary-trace"))),
    "005": _law("005", "SFT-CHEM-CHAIN-GROWTH-POLYMERIZATION-NETWORK-005", "Fold chain-growth polymerization-network law", "A chain-growth polymerization is the complete finite transition network in which initiation creates a held active chain end, propagation appends one retained monomer, transfer moves the active end, and termination closes it without losing carrier custody.", ("SFT-CHEM-NET-REACTION-001", "SFT-CHEM-REACTION-GRAPH-GENERATION-007", "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007"), (
        ("states", "conversion-scalar-only", "complete-held-chain-and-active-end-states"), ("initiation", "implicit-chain-start", "explicit-active-end-creation-transition"), ("propagation", "continuous-growth-rate", "one-monomer-append-transition"), ("transfer", "transfer-path-erased", "active-end-transfer-transition-retained"), ("termination", "silent-process-stop", "explicit-terminal-chain-transition"), ("paths", "major-path-only", "all-simple-registered-network-paths"), ("custody", "unbalanced-monomer-loss", "complete-carrier-and-active-end-custody"), ("certificate", "conversion-only-output", "states-transitions-paths-resources-and-terminal-trace"))),
    "006": _law("006", "SFT-CHEM-STEP-GROWTH-POLYMERIZATION-NETWORK-006", "Fold step-growth polymerization-network law", "In a finite step-growth population every admitted intermolecular bond merges exactly two connected components into one; the retained molecule count and complete reactive-group transition network are therefore forced at every step.", ("SFT-CHEM-CHAIN-GROWTH-POLYMERIZATION-NETWORK-005",), (
        ("population", "mean-chain-only", "complete-molecule-and-reactive-group-population"), ("reaction", "conversion-without-bond", "one-explicit-intermolecular-bond-transition"), ("components", "component-count-untracked", "each-bond-merges-two-components"), ("groups", "reactive-groups-erased", "every-reactive-group-identity-retained"), ("products", "selected-chain-products", "all-connected-component-products"), ("cycles", "cycle-bond-counts-as-merge", "cycle-and-intermolecular-bonds-distinguished"), ("arithmetic", "imported-conversion-equation", "exact-initial-minus-merge-count"), ("certificate", "degree-only-output", "groups-bonds-components-products-and-boundary-trace"))),
    "007": _law("007", "SFT-CHEM-COPOLYMER-SEQUENCE-COMPOSITION-007", "Fold copolymer sequence-composition law", "A finite copolymer is an exact generated word of held monomer labels; composition is the complete positive label-count vector divided by word length while sequence order remains separately reconstructible.", ("SFT-CHEM-STEP-GROWTH-POLYMERIZATION-NETWORK-006",), (
        ("word", "composition-without-sequence", "complete-ordered-monomer-word"), ("labels", "anonymous-repeat-count", "held-monomer-identities"), ("counts", "selected-monomer-fractions", "complete-positive-label-count-vector"), ("composition", "rounded-percentages", "exact-label-count-over-word-length"), ("sequence", "random-sequence-premise", "every-position-and-neighbour-relation-retained"), ("population", "one-word-replaces-sample", "word-and-sample-boundaries-separated"), ("extension", "retroactive-sequence-fit", "append-one-held-label-extension"), ("certificate", "composition-only-output", "word-counts-ratios-sequence-and-boundary-trace"))),
    "008": _law("008", "SFT-CHEM-POLYMER-ARCHITECTURE-008", "Fold branched, star and network architecture law", "Polymer architecture is the exact isomorphism class of its finite held monomer-incidence graph; linear, branched, star and crosslinked forms are forced by complete degree, component, cycle and branch-centre records.", ("SFT-CHEM-COPOLYMER-SEQUENCE-COMPOSITION-007", "SFT-CHEM-CANONICAL-MOLECULAR-GRAPH-ENCODING-001"), (
        ("carrier", "architecture-name-only", "complete-finite-polymer-incidence-graph"), ("vertices", "unlabelled-node-total", "held-repeat-and-junction-identities"), ("edges", "connectivity-summary", "complete-covalent-incidence-support"), ("degree", "branch-count-only", "degree-of-every-held-vertex"), ("components", "disconnected-pieces-conflated", "complete-connected-component-census"), ("cycles", "tree-assumed", "cycle-rank-retained"), ("identity", "drawing-layout-identity", "exact-labelled-graph-isomorphism-class"), ("certificate", "architecture-label-only", "vertices-edges-degrees-components-cycles-and-map-trace"))),
    "009": _law("009", "SFT-CHEM-CROSSLINK-GELATION-BOUNDARY-009", "Fold crosslink and finite-gelation boundary law", "At a declared finite observation scale, gelation is certified exactly when one retained covalent component joins the registered disjoint inlet and outlet boundaries; no completed infinite network is asserted.", ("SFT-CHEM-POLYMER-ARCHITECTURE-008",), (
        ("network", "bulk-gel-label", "complete-finite-crosslink-graph"), ("boundaries", "unregistered-system-extent", "disjoint-held-inlet-and-outlet-support"), ("connectivity", "crosslink-count-threshold", "one-component-connects-both-boundaries"), ("enumeration", "sampled-path-test", "complete-component-and-path-census"), ("infinity", "completed-infinite-network", "declared-finite-observation-scale"), ("transition", "assumed-universal-gel-point", "first-registered-boundary-connecting-transition"), ("adverse", "near-spanning-network-accepted", "every-unconnected-boundary-state-rejected"), ("certificate", "gel-boolean-only", "graph-boundaries-component-witness-and-scale-trace"))),
    "010": _law("010", "SFT-CHEM-POLYMER-CONFORMATION-SIZE-010", "Fold polymer conformation and size law", "A finite chain conformation is a generated ordered position word and its squared size is the exact mean squared displacement from its exact centroid; no continuum random walk or irrational root enters the native result.", ("SFT-CHEM-POLYMER-ARCHITECTURE-008", "SFT-CHEM-CONFORMER-ENUMERATION-006"), (
        ("chain", "mass-only-chain", "complete-ordered-chain-carrier"), ("states", "one-equilibrium-shape", "complete-generated-finite-conformation-support"), ("positions", "continuum-coordinate-field", "exact-rational-position-word"), ("centre", "assumed-origin", "exact-finite-centroid"), ("size", "root-mean-radius", "exact-mean-squared-centroid-distance"), ("ensemble", "random-walk-premise", "explicit-state-and-weight-census"), ("scope", "asymptotic-universal-law", "declared-chain-state-and-resolution-boundary"), ("certificate", "size-scalar-only", "positions-centroid-squares-weights-and-boundary-trace"))),
    "011": _law("011", "SFT-CHEM-POLYMER-PHASE-TRANSITION-011", "Fold polymer phase and transition law", "A polymer molecular transition is the first ordered registered state at which a held molecular phase label changes, with composition, architecture, condition and hysteresis direction retained; bulk performance remains Materials-owned.", ("SFT-CHEM-POLYMER-CONFORMATION-SIZE-010", "SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012", "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013"), (
        ("carrier", "material-name-only", "complete-polymer-molecular-carrier"), ("states", "single-transition-temperature", "ordered-complete-condition-state-record"), ("phase", "scalar-property-change-only", "held-molecular-phase-label-change"), ("composition", "composition-erased", "composition-and-architecture-retained"), ("direction", "heating-cooling-conflated", "transition-direction-and-hysteresis-held"), ("boundary", "bulk-performance-imported", "chemistry-transition-materials-performance-separated"), ("adverse", "no-change-row-discarded", "all-no-change-and-multiple-change-rows-retained"), ("certificate", "temperature-only-output", "carrier-states-label-change-direction-and-ownership-trace"))),
    "012": _law("012", "SFT-CHEM-POLYMER-DEGRADATION-NETWORK-012", "Fold polymer degradation and depolymerization-network law", "Polymer degradation is the complete finite network of held scission, transfer, unzipping, crosslink and product transitions in which every repeat-unit carrier is retained in a terminal fragment or an explicitly released product.", ("SFT-CHEM-POLYMER-PHASE-TRANSITION-011", "SFT-CHEM-REACTION-GRAPH-GENERATION-007"), (
        ("source", "mass-loss-curve-only", "complete-held-polymer-source-carrier"), ("moves", "one-global-degradation-rate", "registered-scission-transfer-unzip-and-crosslink-transitions"), ("paths", "dominant-product-path", "all-simple-generated-product-paths"), ("fragments", "unidentified-residue", "complete-terminal-fragment-identities"), ("released", "lost-mass-placeholder", "explicit-released-product-carriers"), ("balance", "approximate-mass-closure", "exact-repeat-unit-carrier-conservation"), ("conditions", "condition-free-mechanism", "time-temperature-environment-boundary-retained"), ("certificate", "remaining-mass-only", "source-moves-paths-products-balance-and-condition-trace"))),
    "013": _law("013", "SFT-CHEM-POLYMER-MATERIALS-HANDOFF-013", "Fold polymer Chemistry-to-Materials handoff law", "The Chemistry-to-Materials handoff pairs one complete molecular architecture and state record with one separately owned bulk-property record; neither branch duplicates nor selects the other's law.", ("SFT-CHEM-POLYMER-DEGRADATION-NETWORK-012", "SFT-MAT-CLASS-POLYMER-001", "SFT-MAT-MEAS-MATERIAL-001", "SFT-MAT-MECH-STRESS-STRAIN-001", "SFT-MAT-PHASE-TRANSITION-001"), (
        ("chemistry", "polymer-name-only", "complete-chemistry-architecture-and-state-record"), ("materials", "bulk-value-without-carrier", "complete-material-sample-and-property-record"), ("pairing", "unlinked-branch-records", "one-exact-source-bound-paired-record"), ("ownership", "duplicated-property-law", "one-owner-per-law-and-result"), ("direction", "materials-selects-chemistry", "chemistry-carrier-precedes-material-response"), ("feedback", "performance-retrofits-molecular-law", "new-evidence-opens-separate-lawful-extension"), ("adverse", "unpaired-record-silently-used", "missing-side-mandatory-halt"), ("certificate", "cross-branch-link-only", "both-records-owners-dependencies-and-boundary-trace"))),
}


def generated_candidate_ids(number: str) -> tuple[str, ...]:
    law = LAW_ROWS[number]
    return tuple("__".join(item) for item in product(*(tuple(choice.name for choice in row.choices) for row in law["dimensions"])))


for _number, _row in LAW_ROWS.items():
    if len(_row["dimensions"]) != 8 or len(generated_candidate_ids(_number)) != 256:
        raise ValueError(f"POLY-{_number} candidate grammar is incomplete")
    if generated_candidate_ids(_number).count(_row["result"]) != 1:
        raise ValueError(f"POLY-{_number} survivor is not unique")


__all__ = (
    "LAW_ROWS", "PolymerGraph", "PolymerNetwork", "PolymerPopulation", "PolymerTransition",
    "chemistry_materials_handoff", "degree_of_polymerization", "degradation_balance",
    "generated_candidate_ids", "labelled_composition", "phase_transition_trace",
    "squared_radius_of_gyration", "step_growth_chain_count",
)
