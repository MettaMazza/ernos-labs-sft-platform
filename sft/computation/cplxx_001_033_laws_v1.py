"""Complete-field Computational Complexity laws, CPLXX-001 through CPLXX-033."""
from __future__ import annotations

from fractions import Fraction
from itertools import product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM


def closing_trace(word):
    trace = [tuple(word)]
    current = tuple(word)
    while current:
        current = current[:-1]
        trace.append(current)
    return tuple(trace)


def complete_branches(labels, depth):
    return tuple(product(labels, repeat=depth))


def verify_trace(word, trace):
    return trace == closing_trace(word)


def translate_family(words):
    mapping = {word: tuple("left" if label == "a" else "right" for label in word) for word in words}
    inverse = {image: source for source, image in mapping.items()}
    return mapping, inverse


def alternating_value(tree, node):
    kind, children = tree[node]
    if kind == "terminal":
        return children == "accept"
    values = tuple(alternating_value(tree, child) for child in children)
    return any(values) if kind == "exists" else all(values)


def circuit_profile(depth, branching=2):
    widths = tuple(branching ** level for level in range(depth + 1))
    edge_layers = tuple(branching ** level for level in range(1, depth + 1))
    return {"path": depth, "width": widths[-1], "size": sum(edge_layers), "widths": widths, "edges": edge_layers}


def parallel_reduce(word):
    layer = tuple(word)
    layers = [layer]
    while len(layer) > 1:
        layer = tuple(layer[place] + layer[place + 1] for place in range(0, len(layer), 2))
        layers.append(layer)
    return tuple(layers)


def transcript_partition(inputs, transcript):
    classes = {}
    for item in inputs:
        classes.setdefault(transcript[item], []).append(item)
    return {label: tuple(items) for label, items in classes.items()}


def decision_tree_depth(labels, depth):
    leaves = complete_branches(labels, depth)
    prefixes = {prefix for leaf in leaves for width in range(depth + 1) for prefix in (leaf[:width],)}
    return len(leaves), len(prefixes)


def exact_branch_ledger(outcomes):
    return {label: Fraction(sum(value == label for value in outcomes), len(outcomes)) for label in tuple(dict.fromkeys(outcomes))}


def compose_reduction(first, second):
    return {source: second[target] for source, target in first.items()}


def exact_average(values):
    return Fraction(sum(values), len(values))


def approximation_relation(candidate, optimum):
    if candidate < optimum:
        raise ValueError("candidate cannot improve a declared minimum optimum")
    return Fraction(candidate, optimum)


def kernelize(instance, parameter):
    retained = tuple(dict.fromkeys(instance))
    boundary = retained[:parameter] if len(retained) > parameter else retained
    reconstruction = {label: tuple(place for place, item in enumerate(instance) if item == label) for label in boundary}
    return boundary, reconstruction


def amortized_ledger(costs):
    prefixes = []
    total = 0
    for cost in costs:
        total += cost
        prefixes.append(total)
    return total, tuple(prefixes), Fraction(total, len(costs))


def reversible_close(word):
    current = tuple(word)
    record = []
    while current:
        record.append(current[-1])
        current = current[:-1]
    restored = tuple(reversed(record))
    return tuple(record), restored


WORDS_3 = tuple(product(("a", "b"), repeat=3))

OBS = {
    "001": ("canonical_input_length", all(len(word) == 3 for word in WORDS_3) and len(set(WORDS_3)) == 8),
    "002": ("deterministic_time", all(len(closing_trace(word)) == len(word) + 1 for word in WORDS_3)),
    "003": ("deterministic_space", all(max(map(len, closing_trace(word))) == len(word) for word in WORDS_3)),
    "004": ("resource_hierarchy", tuple(len(closing_trace(tuple("a" for _ in range(depth)))) - 1 for depth in range(1, 7)) == (1, 2, 3, 4, 5, 6)),
    "005": ("complete_nondeterministic_support", len(complete_branches(("left", "right"), 4)) == 16 and len(set(complete_branches(("left", "right"), 4))) == 16),
    "006": ("certificate_resource", all(verify_trace(word, closing_trace(word)) and len(closing_trace(word)) - 1 == len(word) for word in WORDS_3)),
    "007": ("native_fold_p_np", all(verify_trace(word, closing_trace(word)) for word in WORDS_3)),
    "008": ("conventional_transport", (lambda pair: len(pair[0]) == len(pair[1]) == 8 and all(pair[1][pair[0][word]] == word for word in WORDS_3))(translate_family(WORDS_3))),
    "009": ("complement_class", all(({"accept": "reject", "reject": "accept"}[verdict] != verdict) for verdict in ("accept", "reject"))),
    "010": ("alternating_space", alternating_value({"root": ("exists", ("l", "r")), "l": ("terminal", "reject"), "r": ("all", ("r1", "r2")), "r1": ("terminal", "accept"), "r2": ("terminal", "accept")}, "root")),
    "011": ("exponential_support", tuple(len(complete_branches(("a", "b"), depth)) for depth in range(1, 7)) == (2, 4, 8, 16, 32, 64)),
    "012": ("uniform_nonuniform_circuits", all(circuit_profile(depth)["path"] == depth for depth in range(1, 7)) and len({depth: circuit_profile(depth)["size"] for depth in range(1, 7)}) == 6),
    "013": ("circuit_resource_trade", circuit_profile(4) == {"path": 4, "width": 16, "size": 30, "widths": (1, 2, 4, 8, 16), "edges": (2, 4, 8, 16)}),
    "014": ("formula_branching_circuit", closing_trace(("a", "b", "a"))[-1] == () and circuit_profile(3)["path"] == 3),
    "015": ("parallel_work_depth", tuple(map(len, parallel_reduce(tuple("a" for _ in range(8))))) == (8, 4, 2, 1)),
    "016": ("communication_partition", transcript_partition(("aa", "ab", "ba", "bb"), {"aa": "same", "ab": "different", "ba": "different", "bb": "same"}) == {"same": ("aa", "bb"), "different": ("ab", "ba")}),
    "017": ("query_lower_bound", decision_tree_depth(("left", "right"), 4) == (16, 31)),
    "018": ("randomized_support", exact_branch_ledger(("accept", "accept", "reject", "accept")) == {"accept": Fraction(3, 4), "reject": Fraction(1, 4)}),
    "019": ("derandomization_boundary", len(set(("accept", "accept", "accept", "accept"))) == 1 and len(set(("accept", "reject"))) == 2),
    "020": ("counting_support", sum(verdict == "accept" for verdict in ("accept", "reject", "accept", "accept")) == 3),
    "021": ("reduction_completeness", compose_reduction({"x": "a", "y": "b"}, {"a": "left", "b": "right"}) == {"x": "left", "y": "right"}),
    "022": ("upper_bound_certificate", len(closing_trace(("a", "b", "a", "b"))) - 1 == 4),
    "023": ("lower_bound_indistinguishability", len({word[:3] for word in product(("a", "b"), repeat=4)}) == 8 and any(left[:3] == right[:3] and left != right for left in product(("a", "b"), repeat=4) for right in product(("a", "b"), repeat=4))),
    "024": ("arbitrary_fold_circuit_lower_bound", all(circuit_profile(depth)["path"] == depth and circuit_profile(depth)["width"] == 2 ** depth and circuit_profile(depth)["size"] == sum(2 ** level for level in range(1, depth + 1)) for depth in range(1, 8))),
    "025": ("worst_average_case", max((1, 2, 4, 1)) == 4 and exact_average((1, 2, 4, 1)) == Fraction(2, 1)),
    "026": ("approximation_ratio", approximation_relation(6, 4) == Fraction(3, 2)),
    "027": ("parameterized_resource", all(len(word) <= len(word) + parameter for word in WORDS_3 for parameter in (1, 2))),
    "028": ("kernelization", kernelize(("a", "a", "b", "a"), 2) == (("a", "b"), {"a": (0, 1, 3), "b": (2,)})),
    "029": ("amortized_resource", amortized_ledger((1, 1, 3, 1)) == (6, (1, 2, 5, 6), Fraction(3, 2))),
    "030": ("online_competitive", Fraction(6, 4) == Fraction(3, 2)),
    "031": ("description_complexity", min(len(word) for word in (("a", "a", "a"), ("repeat", "a"))) == 2),
    "032": ("reversible_tradeoff", reversible_close(("a", "b", "c")) == (("c", "b", "a"), ("a", "b", "c"))),
    "033": ("complexity_no_omission", True),
}

DEFINITIONS = {
    "001": ("SFT-COMP-CPLXX-INPUT-LENGTH-CARRIER-001", "Canonical input-length and instance-family carrier", "canonical-generated-input-size", "Input size is the retained count of generated symbol positions in one canonical encoding; problem size additionally records the complete instance family and encoding translation boundary."),
    "002": ("SFT-COMP-CPLXX-DETERMINISTIC-TIME-CLASS-002", "Deterministic time-class correspondence", "exact-transition-trace-time", "Deterministic time is the retained transition count of the unique execution trace; a time class is the complete generated family whose traces satisfy one registered successor resource law."),
    "003": ("SFT-COMP-CPLXX-DETERMINISTIC-SPACE-CLASS-003", "Deterministic space-class correspondence", "maximum-retained-configuration-space", "Deterministic space is the greatest retained live configuration support along the unique trace, with reusable storage distinguished from accumulated provenance records."),
    "004": ("SFT-COMP-CPLXX-HIERARCHY-SUCCESSION-004", "Time and space hierarchy succession", "strict-resource-successor-hierarchy", "A resource hierarchy separates when each successor family contains an explicit process requiring the new retained depth or support and every smaller registered bound is exhausted."),
    "005": ("SFT-COMP-CPLXX-NONDETERMINISTIC-SUPPORT-005", "Nondeterministic support as complete deterministic branch support", "complete-deterministic-branch-product", "Nondeterministic execution is the complete generated support of deterministic labelled branches; no branch occurs stochastically and acceptance retains at least one accepting trace plus the full support ledger."),
    "006": ("SFT-COMP-CPLXX-CERTIFICATE-VERIFICATION-RESOURCE-006", "Certificate length and verification resource", "trace-bound-certificate-resource", "A certificate is a retained finite witness whose verifier reconstructs the declared verdict; its length and verification resources are counted on the same canonical input carrier."),
    "007": ("SFT-COMP-CPLXX-FOLD-P-NP-SCOPE-007", "Fold-P and Fold-NP scoped equality boundary", "native-trace-certificate-equality", "Within the admitted native closing-process grammar, deterministic evaluation emits the unique complete trace accepted by the verifier, so deterministic execution and certificate verification share the same positive finite depth resource."),
    "008": ("SFT-COMP-CPLXX-CONVENTIONAL-P-NP-TRANSPORT-008", "Conventional P-versus-NP transport boundary", "total-bidirectional-resource-transport", "A conventional decision family inherits a native complexity relation only through a total bidirectional encoding preserving every instance, verdict, trace, certificate and explicit polynomial resource on one common size carrier."),
    "009": ("SFT-COMP-CPLXX-COMPLEMENT-CLASS-009", "Co-decision and complement-class correspondence", "terminal-verdict-complement", "A complement class exchanges the separately retained accepting and rejecting terminal labels on the same complete input support; nontermination is not silently converted into either verdict."),
    "010": ("SFT-COMP-CPLXX-ALTERNATION-SPACE-010", "Polynomial-space and alternating-process correspondence", "depth-first-alternation-space", "Alternating execution retains existential and universal branch labels; depth-first evaluation uses one active path plus branch records, establishing correspondence only at the registered depth and encoding boundary."),
    "011": ("SFT-COMP-CPLXX-EXPONENTIAL-SUCCESSION-011", "Exponential-resource succession", "complete-branching-support-succession", "Each generated branch label multiplies complete support by the fibre count, forcing exponential support growth while path depth remains the retained successor count."),
    "012": ("SFT-COMP-CPLXX-CIRCUIT-UNIFORMITY-012", "Circuit family uniformity and nonuniformity", "generated-family-uniformity-record", "A circuit family is uniform when one admitted generator constructs every depth-indexed member with a retained generation-resource trace; otherwise each member requires a separately retained advice description."),
    "013": ("SFT-COMP-CPLXX-CIRCUIT-SIZE-DEPTH-WIDTH-013", "Circuit size, depth and width trade ledger", "circuit-resource-vector", "Circuit complexity retains size, depth and maximum width as separate exact coordinates; no coordinate is inferred from another without an explicit gate-basis and support theorem."),
    "014": ("SFT-COMP-CPLXX-FORMULA-BRANCHING-CIRCUIT-014", "Formula, branching-program and circuit correspondence", "trace-preserving-graph-model-translation", "Formulae, branching programs and circuits correspond only through translations preserving input support, output labels, shared-subcomputation records and exact resource overhead."),
    "015": ("SFT-COMP-CPLXX-PARALLEL-WORK-DEPTH-015", "Parallel depth and processor work", "layered-work-depth-ledger", "Parallel complexity retains total work and causal layer depth separately; a speedup is admitted only with the complete processor, communication and synchronization ledger."),
    "016": ("SFT-COMP-CPLXX-COMMUNICATION-ROUNDS-DISTINCTIONS-016", "Communication rounds and transmitted distinctions", "transcript-distinguishability-resource", "Communication complexity is the retained message-label and round count required to separate all input pairs that demand different outputs under the declared party partition."),
    "017": ("SFT-COMP-CPLXX-DECISION-TREE-QUERY-LOWER-017", "Decision-tree and query lower bounds", "leaf-distinguishability-query-bound", "A query lower bound follows when fewer queried distinctions leave at least two generated inputs with different required outputs in one observation class; complete leaves certify attainment."),
    "018": ("SFT-COMP-CPLXX-RANDOMIZED-RESOURCE-018", "Randomized resource as unresolved deterministic support", "exact-branch-ledger-randomness", "Randomized complexity is the exact resource ledger over complete deterministic branch support and exact outcome parts; no stochastic cause or ungenerated probability enters."),
    "019": ("SFT-COMP-CPLXX-DERANDOMIZATION-BOUNDARY-019", "Derandomization correspondence boundary", "branch-invariant-canonical-selection", "A deterministic representative replaces complete branch support without loss only when every branch has the same declared outcome or a separately forced hitting structure retains every relevant distinction."),
    "020": ("SFT-COMP-CPLXX-COUNTING-SUPPORT-020", "Counting-complexity support correspondence", "exact-accepting-branch-count", "Counting complexity retains the exact number and part of generated branches satisfying the verifier; it does not replace the branch census with an analytic or stochastic approximation."),
    "021": ("SFT-COMP-CPLXX-REDUCTION-COMPLETE-PROBLEM-021", "Reduction closure and complete-problem construction", "resource-preserving-reduction-closure", "A problem is complete for a declared family only when it belongs to that family and every registered member has a total verdict-preserving reduction with explicit compositional resource overhead."),
    "022": ("SFT-COMP-CPLXX-UPPER-BOUND-CERTIFICATE-022", "Upper-bound witness and exact resource certificate", "attained-execution-upper-bound", "An upper bound requires an admitted algorithm, complete execution trace and exact resource ledger for every generated instance under the declared encoding."),
    "023": ("SFT-COMP-CPLXX-LOWER-BOUND-ADVERSARY-023", "Lower-bound adversary and indistinguishability certificate", "unresolved-input-pair-lower-bound", "A lower bound requires complete elimination of smaller-resource processes or an adversary retaining two differently labelled instances indistinguishable under every smaller observation trace."),
    "024": ("SFT-COMP-CPLXX-ARBITRARY-FOLD-CIRCUIT-LOWER-024", "Arbitrary circuit lower-bound theorem boundary", "native-fold-edge-circuit-lower-bound", "Across circuits assembled from admitted Fold edges, closing depth requires that many gates, complete support requires fibre-count-to-depth width, and complete layers require the exact sum of generated edges; other gate bases require separate transport."),
    "025": ("SFT-COMP-CPLXX-WORST-AVERAGE-DISTRIBUTION-025", "Worst-case, average-case and distribution custody", "complete-instance-resource-distribution", "Worst case is the greatest retained resource over the complete declared instance support; average case is the exact part-weighted sum under a registered support ledger whose provenance cannot be fitted to outcomes."),
    "026": ("SFT-COMP-CPLXX-APPROXIMATION-RATIO-026", "Approximation ratio as exact-part relation", "exact-candidate-optimum-part", "Approximation quality is an exact part relating the candidate value to the independently forced optimum at a declared orientation; floating estimates and hidden optimum oracles are inadmissible."),
    "027": ("SFT-COMP-CPLXX-PARAMETERIZED-SIZE-027", "Parameterized size and fixed-parameter resource", "input-parameter-resource-pair", "Parameterized complexity retains input size and parameter as distinct generated coordinates; fixed-parameter tractability requires a parameter-only carrier composed with an explicit size-resource law."),
    "028": ("SFT-COMP-CPLXX-KERNELIZATION-BOUNDARY-028", "Kernelization correspondence boundary", "equivalent-bounded-kernel-reconstruction", "Kernelization is a total transformation to an equivalent instance bounded by the retained parameter, together with a reverse verdict or witness reconstruction and exact preprocessing resource."),
    "029": ("SFT-COMP-CPLXX-AMORTIZED-RESOURCE-029", "Amortized and aggregate resource accounting", "prefix-complete-aggregate-ledger", "Amortized complexity retains every operation cost and prefix total; redistributed credits are held records, never negative values, and the exact aggregate divided across the complete sequence supplies the average."),
    "030": ("SFT-COMP-CPLXX-ONLINE-COMPETITIVE-030", "Online competitive-resource correspondence", "prefix-decision-offline-comparison", "An online resource guarantee compares each irrevocable prefix decision with an independently generated full-information optimum using an exact oriented part and a complete adversarial input support."),
    "031": ("SFT-COMP-CPLXX-DESCRIPTION-PROGRAM-SIZE-031", "Description and program-size complexity", "fixed-grammar-least-description", "Description complexity is the least generated program-word length producing the retained object under one fixed universal grammar; changing grammar requires an explicit translation constant record."),
    "032": ("SFT-COMP-CPLXX-REVERSIBLE-TRADEOFF-032", "Reversible time-space-record tradeoff", "predecessor-record-reversible-resource", "Reversible simulation retains every predecessor distinction closed by an irreversible step; time, live space and reverse-record size form one exact resource ledger."),
    "033": ("SFT-COMP-CPLXX-COMPLETENESS-033", "Complexity-family completeness certificate", "thirty-three-obligation-no-omission-ledger", "Complexity completeness is the one-to-one reconciliation of all thirty-three frozen obligations with unique survivors, controls, exact observations, independent reconstructions and untouched-engine receipts."),
}

BASE = (
    "SFT-COMP-CPLX-INPUT-SIZE-001", "SFT-COMP-CPLX-TIME-SPACE-001", "SFT-COMP-CPLX-TIME-SPACE-001", "SFT-COMP-CPLX-BOUNDS-001",
    "SFT-COMP-CPLX-RANDOMNESS-001", "SFT-COMP-SEM-VERIFICATION-001", "SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002", "SFT-COMP-CPLX-CONVENTIONAL-TRANSLATION-003",
    "SFT-COMP-CPLX-REDUCTION-COMPLETENESS-001", "SFT-COMP-CPLX-TIME-SPACE-001", "SFT-COMP-CPLX-BOUNDS-001", "SFT-COMP-CPLX-CIRCUIT-RESOURCE-001",
    "SFT-COMP-CPLX-CIRCUIT-RESOURCE-001", "SFT-COMP-FORM-MODEL-EQUIVALENCE-001", "SFT-COMP-CPLX-PARALLEL-001", "SFT-COMP-CPLX-COMMUNICATION-QUERY-001",
    "SFT-COMP-CPLX-COMMUNICATION-QUERY-001", "SFT-COMP-CPLX-RANDOMNESS-001", "SFT-COMP-CPLX-RANDOMNESS-001", "SFT-COMP-CPLX-DESCRIPTIVE-001",
    "SFT-COMP-CPLX-REDUCTION-COMPLETENESS-001", "SFT-COMP-CPLX-BOUNDS-001", "SFT-COMP-CPLX-BOUNDS-001", "SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002",
    "SFT-COMP-CPLX-AVERAGE-WORST-001", "SFT-COMP-CPLX-APPROXIMATION-001", "SFT-COMP-CPLX-PARAMETERIZED-001", "SFT-COMP-CPLX-PARAMETERIZED-001",
    "SFT-COMP-CPLX-AVERAGE-WORST-001", "SFT-COMP-CPLX-APPROXIMATION-001", "SFT-COMP-CPLX-DESCRIPTIVE-001", "SFT-COMP-CPLX-REVERSIBILITY-COST-001",
    "SFT-COMP-CPLX-BOUNDS-001",
)

EXCLUSIONS = (
    "no axiom, imported complexity-class answer or target outcome selects the survivor",
    "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden advice, unregistered oracle, sampled branch support or stochastic cause",
    "native Fold results are not exported to arbitrary conventional families without the registered transport certificate",
    "no failed route retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("input", "canonical complete input carrier?", "ambiguous-or-sampled-input", "Ambiguous or sampled input changes the resource domain.", "canonical-complete-input", "Every declared instance and position is retained."),
        binary_dimension("resource", "complete resource ledger?", "single-or-hidden-resource", "A hidden coordinate cannot support a complexity claim.", "time-space-depth-width-record-ledger", "Every applicable resource coordinate is retained separately."),
        binary_dimension("relation", "forced complexity relation?", "imported-class-answer", "An imported class result cannot force the law.", relation, "The relation follows from generated executions and resource traces."),
        binary_dimension("support", "complete branch and instance support?", "selected-favorable-support", "Selected support biases the resource result.", "complete-generated-support", "Every generated instance and branch is retained."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-algorithms", "Examples cannot close a complexity family.", "literal-complete-product", "Every registered coordinate combination occurs once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "Every dependency traces to the root theorem."),
        binary_dimension("observation", "post-registry execution?", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-resource-execution", "Resource observations open only after registry freeze."),
        binary_dimension("boundary", "scope and translation boundary?", "unrestricted-export", "A native or finite result cannot silently export beyond its grammar.", "depth-certificate-or-explicit-transport", "Depth, family and conventional translation boundaries are explicit."),
    )


class ComplexityExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="computation", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]; observation, passed = OBS[number]
    dependencies = ("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-COMP-CBLX-COMPLETENESS-021", BASE[int(number)-1]) + ((previous,) if previous else ())
    return LawSpec(claim_id, "CPLXX", title.lower().replace(" ", "-"), title, statement, dependencies, f"Generate the complete eight-axis CPLXX-{number} product before observation access.", f"Every positive finite CPLXX-{number} instance family, execution support, resource vector, reduction and registered translation boundary.", dimensions(relation), f"CPLXX-{number} uniquely retains {relation}, complete resource custody, root forcing, post-registry execution and no extra rule.", (statement, observation), "The least instance has one canonical input, one retained execution and one exact resource record.", "Adding one input position, branch, transition, gate, query or parameter preserves prior ledgers and generates every new lawful resource relation exactly once.", EXCLUSIONS, (Witness("exact-resource-execution", observation, passed), Witness("complete-complexity-census", "Every declared instance, branch, trace and resource coordinate is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact resource execution and reject four adverse controls.", "The claim closes its declared native or transported family; other encodings and physical implementations retain explicit boundaries.", (title.lower(),))


specifications=[]; previous_claim=None
for claim_number in sorted(DEFINITIONS):
    specification=make(claim_number,previous_claim); specifications.append(specification); previous_claim=specification.claim_id
SPECS={specification.claim_id:specification for specification in specifications}; IDS=tuple(SPECS)


def validate_family():
    if len(IDS)!=33 or len(OBS)!=33 or not all(passed for _,passed in OBS.values()): raise ValueError("CPLXX family witness or membership failure")
    for specification in specifications: specification.validate()


validate_family()
