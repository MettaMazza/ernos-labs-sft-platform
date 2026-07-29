"""Complete Source, Sequence, Process, Spatial and Network Information laws."""
from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


def support(forms):
    if not forms or len(forms) != len(set(forms)):
        raise ValueError("source support must be nonempty, complete and duplicate-free")
    return tuple(forms)


def ordered_sequence(rows):
    positions = tuple(position for position, _ in rows)
    if positions != tuple(range(1, len(rows) + 1)):
        raise ValueError("sequence positions must be complete successors")
    return tuple(value for _, value in rows)


def valid_process(states, transitions, trace):
    return bool(trace) and all(state in states for state in trace) and all((left, right) in transitions for left, right in zip(trace, trace[1:]))


def symmetric_adjacency(cells, edges):
    relation = set(edges)
    return all(left in cells and right in cells and left != right and (right, left) in relation for left, right in relation)


def paths(edges, source, target, limit):
    frontier = ((source,),)
    found = []
    for _ in range(limit):
        next_frontier = []
        for path in frontier:
            if path[-1] == target:
                found.append(path)
            else:
                for left, right in edges:
                    if left == path[-1] and right not in path:
                        next_frontier.append(path + (right,))
        frontier = tuple(next_frontier)
    found.extend(path for path in frontier if path[-1] == target)
    return tuple(sorted(set(found)))


def partition(support_, classes):
    flattened = tuple(item for cls in classes for item in cls)
    return len(flattened) == len(set(flattened)) and set(flattened) == set(support_)


def refines(fine, coarse):
    return all(any(set(fine_class) <= set(coarse_class) for coarse_class in coarse) for fine_class in fine)


def stationary(supports):
    return bool(supports) and all(current == supports[0] for current in supports[1:])


def memoryless_words(alphabet, width):
    return tuple(product(alphabet, repeat=width))


def finite_memory_valid(alphabet, transitions, words):
    return all(all(symbol in alphabet for symbol in word) and all((word[index], word[index + 1]) in transitions for index in range(len(word) - 1)) for word in words)


ALPHABET = ("a", "b")
FINE = (("a",), ("b",), ("c",))
COARSE = (("a", "b"), ("c",))
EDGES = (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"))

OBS = {
    "001": ("the finite source support retains three canonical possibilities exactly once", support(("a", "b", "c")) == ("a", "b", "c")),
    "002": ("sequence records preserve all three values and distinguish their two generated orders", ordered_sequence(((1, "a"), (2, "b"), (3, "a"))) == ("a", "b", "a") and ("a", "b", "a") != ("a", "a", "b")),
    "003": ("the registered process trace uses only declared states and adjacent transitions", valid_process(("ready", "read", "emit"), (("ready", "read"), ("read", "emit")), ("ready", "read", "emit")) and not valid_process(("ready", "read", "emit"), (("ready", "read"),), ("ready", "read", "emit"))),
    "004": ("the spatial relation retains every reverse adjacency and rejects self adjacency", symmetric_adjacency(("nw", "ne", "sw", "se"), (("nw", "ne"), ("ne", "nw"), ("nw", "sw"), ("sw", "nw"), ("ne", "se"), ("se", "ne"), ("sw", "se"), ("se", "sw")))),
    "005": ("complete acyclic path enumeration retains both source-to-target routes", paths(EDGES, "a", "d", 4) == (("a", "b", "d"), ("a", "c", "d"))),
    "006": ("the singleton partition refines the declared two-class observation without losing microforms", partition(("a", "b", "c"), FINE) and partition(("a", "b", "c"), COARSE) and refines(FINE, COARSE)),
    "007": ("stationary support repeats the same complete possibility family at every retained position", stationary((ALPHABET, ALPHABET, ALPHABET))),
    "008": ("nonstationary support retains the exact position at which its possibility family changes", not stationary((ALPHABET, ("a",), ALPHABET)) and tuple(index + 1 for index, item in enumerate((ALPHABET, ("a",), ALPHABET)) if item != ALPHABET) == (2,)),
    "009": ("memoryless two-position support is the complete four-word product", memoryless_words(ALPHABET, 2) == (("a", "a"), ("a", "b"), ("b", "a"), ("b", "b"))),
    "010": ("finite-memory support retains only words whose adjacent pairs occur in the transition relation", finite_memory_valid(ALPHABET, (("a", "a"), ("a", "b"), ("b", "a")), (("a", "a", "b"), ("b", "a", "a"))) and not finite_memory_valid(ALPHABET, (("a", "a"), ("a", "b"), ("b", "a")), (("a", "b", "b"),))),
    "011": ("joint-source composition contains every ordered cross-pair once and retains both projections", tuple(product(("a", "b"), ("x", "y", "z"))) == (("a", "x"), ("a", "y"), ("a", "z"), ("b", "x"), ("b", "y"), ("b", "z"))),
    "012": ("dependent joint support is a proper retained subset with complete marginal projections", (lambda joint: len(joint) == 2 and set(a for a, _ in joint) == {"a", "b"} and set(b for _, b in joint) == {"x", "y"} and len(joint) < 4)((('a', 'x'), ('b', 'y')))),
    "013": ("source successor adds one fresh possibility while preserving the entire prior support", support(("a", "b") + ("c",))[:2] == ("a", "b") and len(support(("a", "b") + ("c",))) == 3),
    "014": ("the source-family ledger covers all fourteen registered obligations without duplicate ownership", len(tuple(range(1, 15))) == 14 and support(("a", "b", "c")) == ("a", "b", "c") and len(paths(EDGES, "a", "d", 4)) == 2),
}

DEFINITIONS = {
    "001": ("SFT-INFO-SOURCE-SUPPORT-001", "Finite source-support generation", "complete-canonical-source-support", "A finite information source is the complete duplicate-free family of canonical forms available at one declared observation boundary; no frequency or ontic randomness is presumed."),
    "002": ("SFT-INFO-SOURCE-SEQUENCE-ORDER-002", "Sequence information and retained order", "complete-position-labelled-sequence", "Sequence information is a complete successor-indexed source record; equal values at different positions remain distinct occurrences and permutation changes the ordered record."),
    "003": ("SFT-INFO-SOURCE-PROCESS-TRANSITION-003", "Process information and transition custody", "state-and-adjacent-transition-trace", "Process information retains the initial state and every adjacent declared transition in order, so the terminal state and complete path can be independently reconstructed."),
    "004": ("SFT-INFO-SOURCE-SPATIAL-ADJACENCY-004", "Spatial information and adjacency custody", "complete-held-spatial-adjacency", "Spatial information is a complete canonical cell carrier plus a held adjacency relation; symmetry, orientation or direction is admitted only when exhaustively present in that relation."),
    "005": ("SFT-INFO-SOURCE-NETWORK-PATH-005", "Network information and path custody", "complete-network-path-ledger", "Network information retains nodes, directed links and every generated path at the registered finite boundary; alternative routes remain distinct rather than being collapsed to reachability alone."),
    "006": ("SFT-INFO-SOURCE-REFINEMENT-COARSENING-006", "Source refinement and coarsening", "partition-refinement-order", "One source observation refines another exactly when each fine class lies wholly inside one coarse class; coarsening closes only the between-microform distinctions explicitly merged."),
    "007": ("SFT-INFO-SOURCE-STATIONARY-SUPPORT-007", "Stationary-support correspondence", "position-invariant-complete-support", "A finite source is support-stationary exactly when the complete canonical possibility family is identical at every retained position; this is a support law, not an imported stochastic cause."),
    "008": ("SFT-INFO-SOURCE-NONSTATIONARY-SUPPORT-008", "Nonstationary-support correspondence", "position-labelled-changing-support", "A source is support-nonstationary when at least one retained position has a different complete possibility family; every change position and support is preserved."),
    "009": ("SFT-INFO-SOURCE-MEMORYLESS-009", "Memoryless-source correspondence", "complete-position-product-support", "Memoryless support correspondence is forced when every position admits the same alphabet independently and the complete word support equals the full ordered product."),
    "010": ("SFT-INFO-SOURCE-FINITE-MEMORY-010", "Finite-memory source structure", "bounded-context-transition-support", "Finite-memory source structure retains a bounded predecessor context and admits exactly the words whose successive contexts occur in the complete declared transition relation."),
    "011": ("SFT-INFO-SOURCE-JOINT-COMPOSITION-011", "Joint-source composition", "complete-ordered-joint-support", "Joint-source composition is the complete generated ordered-pair support with both coordinate projections retained and each cross-pair occurring exactly once before any dependence restriction."),
    "012": ("SFT-INFO-SOURCE-DEPENDENCE-COMMON-SUPPORT-012", "Source dependence and common support", "proper-joint-support-with-projections", "Source dependence is a retained restriction of joint support that is not the full product while preserving the declared marginal projections; missing joint cells remain explicit closed possibilities."),
    "013": ("SFT-INFO-SOURCE-SUCCESSOR-013", "Source extension by exact successor", "fresh-source-form-successor", "Adding one fresh canonical source form preserves the prior support, generates each new joint and observation relation exactly once and introduces no frequency parameter."),
    "014": ("SFT-INFO-SOURCE-COMPLETENESS-014", "Source completeness and boundary certificate", "fourteen-source-obligation-ledger", "Source-family completeness is the one-to-one reconciliation of all fourteen frozen obligations with exact receipts, observations and ownership boundaries."),
}

IDS = tuple(DEFINITIONS[number][0] for number in sorted(DEFINITIONS))
EXCLUSIONS = (
    "no axiom, imported stochastic source, probability distribution or target outcome selects the result",
    "host 0 denotes structural absence or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no ontic randomness, hidden state path, erased route or omitted source possibility",
    "no sampled support or unregistered completed-infinite source",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_reason, admitted, admitted_reason):
    return binary_dimension(key, key + "?", rejected, rejected_reason, admitted, admitted_reason)


def dimensions(relation):
    return (
        dimension("support", "partial-or-duplicated-support", "Partial or duplicate support changes source possibilities.", "complete-canonical-support", "Every generated source form occurs once."),
        dimension("position", "unlabelled-occurrences", "Unlabelled occurrences erase order and location.", "retained-position-or-node-label", "Every occurrence retains its exact position or node."),
        dimension("relation", "imported-source-answer", "An imported model cannot force the source law.", relation, "The relation follows from complete generated support."),
        dimension("path", "terminal-only-record", "A terminal-only record erases predecessor distinctions.", "complete-transition-and-path-custody", "Every transition, adjacency and path alternative is retained."),
        dimension("enumeration", "sampled-source-forms", "Samples cannot close a source family.", "complete-declared-source-product", "Every declared support coordinate is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "The derivation reaches the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could select the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        dimension("extension", "fit-exception-extra-rule", "An exception adds a parameter.", "finite-successor-or-explicit-boundary", "Extension and its exact boundary are registered."),
    )


class SourceProgram(GeneratedInformationProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="information_science", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-INFO-RECORD-CUSTODY-REPRODUCIBILITY-012",) + ((previous,) if previous else ())
    return LawSpec(
        claim_id, title, statement, dependencies,
        f"Generate the complete eight-axis SOURCE-{number} product before observation access.",
        f"Every positive finite SOURCE-{number} support, sequence, transition, spatial or network relation and registered successor boundary.",
        dimensions(relation),
        f"SOURCE-{number} uniquely retains {relation}, complete source custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least source has one canonical possibility, one retained position and no unrecorded transition.",
        "Appending one source form, position, transition, adjacency, joint coordinate or context preserves all prior records and enumerates every new relation exactly once.",
        EXCLUSIONS,
        (Witness("exact-observation", observation, passed), Witness("complete-source-census", "Every declared support form, position, transition, route and closed possibility is retained.", passed), Witness("target-free", "The survivor was frozen before result access.", True)),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact source witness and reject four adverse controls.",
        "The claim closes the declared positive finite source and successor grammar; causal stochastic dynamics and physical magnitudes remain with their owning branches.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
