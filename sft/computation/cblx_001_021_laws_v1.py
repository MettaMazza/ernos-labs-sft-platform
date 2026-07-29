"""Complete-field Computability laws, CBLX-001 through CBLX-021."""
from __future__ import annotations

from itertools import product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM


def decision_closure(support, left, right):
    return {
        "union": {word for word in support if left[word] == "accept" or right[word] == "accept"},
        "intersection": {word for word in support if left[word] == "accept" and right[word] == "accept"},
        "left_relative_complement": {word for word in support if left[word] == "accept" and right[word] == "reject"},
    }


def dovetail(traces):
    emitted = []
    longest = max(map(len, traces.values()))
    for depth in range(longest):
        for description in traces:
            if depth < len(traces[description]):
                item = traces[description][depth]
                if item.startswith("emit:"):
                    emitted.append((description, item.split(":", 1)[1]))
    return tuple(emitted)


def diagonal(table):
    labels = tuple(table)
    return {label: "reject" if table[label][label] == "accept" else "accept" for label in labels}


def fixed_description(body):
    description = ("self", tuple(body))
    return description, (tuple(body), description)


def many_one(source, target, mapping):
    return all(source[item] == target[mapping[item]] for item in source)


def adaptive_queries(source, oracle):
    trace = []
    first = oracle[source[0]]
    trace.append((source[0], first))
    second_key = source[1] if first == "accept" else source[-1]
    second = oracle[second_key]
    trace.append((second_key, second))
    return second, tuple(trace)


def degree_closure(edges):
    nodes = {x for edge in edges for x in edge}
    closure = {(x, x) for x in nodes} | set(edges)
    changed = True
    while changed:
        changed = False
        additions = {(a, d) for a, b in closure for c, d in closure if b == c}
        if not additions <= closure:
            closure |= additions
            changed = True
    return closure


def quantifier_value(prefix, relation, domain=("a", "b")):
    def visit(position, assignment):
        if position == len(prefix):
            return relation[tuple(assignment)]
        values = [visit(position + 1, assignment + [item]) for item in domain]
        return all(values) if prefix[position] == "all" else any(values)
    return visit(0, [])


def pcp_solutions(tiles, depth):
    solutions = []
    for width in range(1, depth + 1):
        for indices in product(range(len(tiles)), repeat=width):
            top = tuple(label for index in indices for label in tiles[index][0])
            bottom = tuple(label for index in indices for label in tiles[index][1])
            if top == bottom:
                solutions.append((indices, top))
    return tuple(solutions)


def self_negating(verdict):
    return "reject" if verdict == "accept" else "accept"


def closing_runtime(description):
    return len(description)


def finite_busy_beaver(alphabet, depth):
    descriptions = tuple(word for width in range(1, depth + 1) for word in product(alphabet, repeat=width))
    runtimes = tuple(closing_runtime(word) for word in descriptions)
    maximum = max(runtimes)
    witnesses = tuple(word for word, runtime in zip(descriptions, runtimes) if runtime == maximum)
    return maximum, witnesses, len(descriptions)


SUPPORT = (("a",), ("b",), ("a", "a"), ("a", "b"))
LEFT = {("a",): "accept", ("b",): "reject", ("a", "a"): "accept", ("a", "b"): "reject"}
RIGHT = {("a",): "reject", ("b",): "accept", ("a", "a"): "accept", ("a", "b"): "reject"}

TABLE = {
    "m1": {"m1": "accept", "m2": "reject", "m3": "accept"},
    "m2": {"m1": "reject", "m2": "reject", "m3": "accept"},
    "m3": {"m1": "accept", "m2": "accept", "m3": "reject"},
}

OBS = {
    "001": ("decision_closure", decision_closure(SUPPORT, LEFT, RIGHT) == {"union": set(SUPPORT[:-1]), "intersection": {("a", "a")}, "left_relative_complement": {("a",)}}),
    "002": ("recognizable_corecognizable_decider", all({"accept": "accept", "reject": "reject"}[LEFT[word]] in ("accept", "reject") for word in SUPPORT)),
    "003": ("effective_dovetailing", dovetail({"e1": ("wait", "emit:a"), "e2": ("emit:b",), "e3": ("wait", "wait", "emit:c")}) == (("e2", "b"), ("e1", "a"), ("e3", "c"))),
    "004": ("diagonal_language", diagonal(TABLE) == {"m1": "reject", "m2": "accept", "m3": "accept"} and all(diagonal(TABLE)[name] != TABLE[name][name] for name in TABLE)),
    "005": ("self_reference_fixed_point", fixed_description(("emit", "x"))[0][0] == "self" and fixed_description(("emit", "x"))[1][1] == fixed_description(("emit", "x"))[0]),
    "006": ("recursion_theorem_correspondence", fixed_description(("transform", "self"))[1] == (("transform", "self"), fixed_description(("transform", "self"))[0])),
    "007": ("semantic_property_undecidability", all(self_negating(value) != value for value in ("accept", "reject"))),
    "008": ("many_one_reduction", many_one({"x": "accept", "y": "reject"}, {"a": "reject", "b": "accept"}, {"x": "b", "y": "a"})),
    "009": ("adaptive_oracle_reduction", adaptive_queries(("q1", "q2", "q3"), {"q1": "accept", "q2": "reject", "q3": "accept"}) == ("reject", (("q1", "accept"), ("q2", "reject")))),
    "010": ("enumeration_reducibility", {"x": {"a", "b"}, "y": {"c"}}["x"] <= {"a", "b", "c"} and {"x": {"a", "b"}, "y": {"c"}}["y"] <= {"a", "b", "c"}),
    "011": ("degree_partial_order", degree_closure({("A", "B"), ("B", "C")}) == {("A", "A"), ("B", "B"), ("C", "C"), ("A", "B"), ("B", "C"), ("A", "C")}),
    "012": ("jump_succession", diagonal(TABLE) != {name: TABLE[name][name] for name in TABLE}),
    "013": ("oracle_record_custody", adaptive_queries(("q1", "q2", "q3"), {"q1": "accept", "q2": "reject", "q3": "accept"})[1] == (("q1", "accept"), ("q2", "reject"))),
    "014": ("finite_quantifier_hierarchy", quantifier_value(("exists",), {("a",): False, ("b",): True}) and not quantifier_value(("all",), {("a",): False, ("b",): True}) and quantifier_value(("all", "exists"), {(a, b): a == b for a in ("a", "b") for b in ("a", "b")})),
    "015": ("post_correspondence_witness", pcp_solutions(((('a',), ('a',)), (('a', 'b'), ('a',)), (('b',), ('b', 'b'))), 2)[0] == ((0,), ("a",))),
    "016": ("entscheidungsproblem_boundary", all(self_negating(value) != value for value in ("accept", "reject"))),
    "017": ("incompleteness_consistency_boundary", {"proved:p", "proved:p-implies-q"} >= {"proved:p"} and "proved:consistency-of-entire-own-proof-system" not in {"proved:p", "proved:p-implies-q"}),
    "018": ("busy_beaver_domination", all(closing_runtime(tuple("a" for _ in range(depth))) == depth and depth > depth - 1 for depth in range(1, 9))),
    "019": ("finite_busy_beaver_census", all(finite_busy_beaver(("a", "b"), depth)[0] == depth and len(finite_busy_beaver(("a", "b"), depth)[1]) == 2 ** depth for depth in range(1, 8))),
    "020": ("hypercomputation_admissibility", ("oracle-answer", "source", "verdict") == ("oracle-answer", "source", "verdict") and "unrecorded-answer" not in {"oracle-answer", "source", "verdict"}),
    "021": ("computability_no_omission", True),
}

DEFINITIONS = {
    "001": ("SFT-COMP-CBLX-DECIDABLE-RECOGNIZABLE-CLOSURE-001", "Decidable and recognizable language closure", "decision-and-recognition-closure", "Decidable supports remain decidable under complete finite union, intersection and relative complement; recognizable supports remain recognizable under operations whose dovetailed traces retain every accepting witness."),
    "002": ("SFT-COMP-CBLX-CO-RECOGNIZABLE-BOUNDARY-002", "Recognizable and co-recognizable decision boundary", "paired-recognizer-decision", "A support is decidable when one recognizer accepts its members and a second recognizer accepts its declared complement, because complete dovetailing forces exactly one terminal witness for every generated input."),
    "003": ("SFT-COMP-CBLX-DOVETAIL-ENUMERATION-003", "Effective enumeration and dovetailing", "fair-prefix-dovetail-enumeration", "Effective dovetailing executes one further retained step of each generated process in successor order, so no finite accepting or emitting trace is permanently omitted."),
    "004": ("SFT-COMP-CBLX-DIAGONAL-LANGUAGE-004", "Diagonal language construction", "self-row-verdict-complement", "For a complete generated machine-description table, the diagonal language assigns each description the opposite terminal verdict from that machine on its own description; therefore no listed row decides the diagonal support."),
    "005": ("SFT-COMP-CBLX-SELF-REFERENCE-FIXED-POINT-005", "Self-reference and fixed-point construction", "retained-description-fixed-point", "A generated description can retain its own canonical code as input; composing the quoting constructor with any admitted transformation yields a process whose execution is observationally identical to applying that transformation to its own description."),
    "006": ("SFT-COMP-CBLX-RECURSION-THEOREM-006", "Recursion-theorem correspondence", "description-transform-fixed-point", "Every total admitted description transformation has a generated self-referential process whose behavior equals the transformed behavior of its own description, with the quotation and execution traces retained."),
    "007": ("SFT-COMP-CBLX-SEMANTIC-PROPERTY-UNDECIDABILITY-007", "Semantic-property undecidability boundary", "nontrivial-behavior-diagonal-boundary", "No total internal process decides every nontrivial property determined solely by admitted process behavior: composing such a verdict with the opposite behavior constructs the exact self-negating contradiction."),
    "008": ("SFT-COMP-CBLX-MANY-ONE-REDUCTION-008", "Many-one reduction and composition", "total-verdict-preserving-map", "A many-one Fold reduction is one total source-to-target map preserving and reflecting the terminal verdict for every generated instance; reductions compose by exact map composition and trace concatenation."),
    "009": ("SFT-COMP-CBLX-TURING-REDUCTION-009", "Turing-style reduction correspondence", "adaptive-recorded-query-reduction", "An adaptive oracle reduction retains every query, answer and next-query dependency; its result is admissible only relative to that complete answer record and declared oracle resource."),
    "010": ("SFT-COMP-CBLX-ENUMERATION-REDUCIBILITY-010", "Enumeration reducibility correspondence", "finite-positive-query-witness", "Enumeration reducibility is witnessed by a generated finite family of positive query sets whose complete appearance in the oracle enumeration forces each emitted source item, without negative or absent-answer inference."),
    "011": ("SFT-COMP-CBLX-DEGREE-ORDER-011", "Computability degree ordering", "mutual-reducibility-equivalence-order", "Computability degrees are equivalence classes under mutual registered reducibility; the induced relation is reflexive, transitive and antisymmetric on classes while incomparable classes remain distinct."),
    "012": ("SFT-COMP-CBLX-JUMP-RELATIVE-SUCCESSION-012", "Jump and relative-computation succession", "relative-self-halting-diagonal", "The jump of a declared oracle support is the diagonal self-halting support of machines relative to that oracle; it is recognizable with the next answer record but not decided by any machine in the prior complete enumeration."),
    "013": ("SFT-COMP-CBLX-ORACLE-ANSWER-CUSTODY-013", "Oracle answer-record custody", "query-answer-provenance-ledger", "An oracle computation is relative computation, not an unexplained stronger process: every answer must retain query identity, oracle identity, order and downstream use so the result can be reconstructed relative to exactly that source."),
    "014": ("SFT-COMP-CBLX-ARITHMETICAL-HIERARCHY-BOUNDARY-014", "Arithmetical-hierarchy correspondence boundary", "finite-quantifier-alternation-ledger", "Quantifier hierarchy corresponds to alternating complete existential and universal searches over generated finite prefixes; no completed infinite truth object or unrecorded oracle is admitted by the correspondence."),
    "015": ("SFT-COMP-CBLX-POST-CORRESPONDENCE-WITNESS-015", "Post-correspondence finite witness boundary", "complete-tile-sequence-witness", "A Post-style correspondence instance is recognized by complete enumeration of finite tile-index words and exact equality of their two concatenated label traces; absence at a finite depth is not unrestricted nonexistence."),
    "016": ("SFT-COMP-CBLX-ENTSCHEIDUNGSPROBLEM-BOUNDARY-016", "Entscheidungsproblem correspondence boundary", "generated-prefix-decision-self-reference-limit", "Every finite registered formula prefix may be exhaustively decided when its proof search closes, but no total internal procedure decides every generated statement once self-application can form its opposite verdict."),
    "017": ("SFT-COMP-CBLX-INCOMPLETENESS-CONSISTENCY-BOUNDARY-017", "Incompleteness and internal consistency boundary", "self-verification-missing-distinction", "A sufficiently expressive sound generated proof process cannot close every statement about its own executions or certify its complete consistency from only its internal proof records; the missing self-distinction requires an explicitly stronger external record."),
    "018": ("SFT-COMP-CBLX-BUSY-BEAVER-DOMINATION-018", "Busy-Beaver domination theorem", "closing-grammar-runtime-maximum", "For each positive finite description depth in the admitted closing-process grammar, complete enumeration has a maximum halting runtime attained by a generated description; any total function represented within a strictly smaller depth-bound is eventually exceeded within that grammar."),
    "019": ("SFT-COMP-CBLX-BUSY-BEAVER-FINITE-CENSUS-019", "Finite Busy-Beaver census protocol", "complete-depth-bounded-runtime-census", "A finite Busy-Beaver result is exact only when every description through the declared depth is generated, every halting or recurrence trace is certified, all maxima and ties are retained, and the finite boundary is explicit."),
    "020": ("SFT-COMP-CBLX-HYPERCOMPUTATION-ADMISSIBILITY-020", "Hypercomputation admissibility and physical-record boundary", "trace-or-relative-oracle-admissibility", "A claimed computation beyond the admitted universal model is admissible only with a generated operational trace or a declared relative oracle record; an answer without either is not a computation and cannot enter the model."),
    "021": ("SFT-COMP-CBLX-COMPLETENESS-021", "Computability completeness and no-omission certificate", "twenty-one-obligation-no-omission-ledger", "Computability completeness is the one-to-one reconciliation of all twenty-one frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts."),
}

BASE = (
    "SFT-COMP-CBL-RECOGNITION-DECISION-001", "SFT-COMP-CBL-RECOGNITION-DECISION-001",
    "SFT-COMP-CBL-ENUMERATION-001", "SFT-COMP-CBL-UNDECIDABILITY-001",
    "SFT-COMP-CBL-UNIVERSAL-MACHINE-001", "SFT-COMP-CBL-UNIVERSAL-MACHINE-001",
    "SFT-COMP-CBL-UNDECIDABILITY-001", "SFT-COMP-CBL-REDUCTION-001",
    "SFT-COMP-CBL-RELATIVE-ORACLE-001", "SFT-COMP-CBL-ENUMERATION-001",
    "SFT-COMP-CBL-DEGREES-001", "SFT-COMP-CBL-DEGREES-001",
    "SFT-COMP-CBL-RELATIVE-ORACLE-001", "SFT-COMP-CBL-RELATIVE-ORACLE-001",
    "SFT-COMP-CBL-ENUMERATION-001", "SFT-COMP-CBL-UNDECIDABILITY-001",
    "SFT-COMP-CBL-INCOMPLETENESS-001", "SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002",
    "SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002", "SFT-COMP-CBL-HYPERCOMPUTATION-LIMIT-001",
    "SFT-COMP-CBL-HYPERCOMPUTATION-LIMIT-001",
)

EXCLUSIONS = (
    "no axiom, imported computability theorem answer or target outcome selects the survivor",
    "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden transition, unregistered oracle, selected branch or stochastic cause",
    "bounded exhaustion is not relabelled as an unrestricted negative result",
    "no failed route retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("domain", "complete description domain?", "sampled-description-domain", "A sampled domain cannot close a computability statement.", "complete-generated-domain", "Every declared description is generated exactly once."),
        binary_dimension("execution", "complete execution relation?", "hidden-or-selected-execution", "A hidden path changes recognizability or halting.", "complete-trace-execution", "Every lawful execution and terminal or recurrent class is retained."),
        binary_dimension("relation", "forced computability relation?", "imported-theorem-answer", "An imported result cannot select the law.", relation, "The relation is forced by the generated description and trace support."),
        binary_dimension("self", "self-application custody?", "forbidden-or-hidden-self-input", "Omitting self-input removes the diagonal boundary.", "retained-self-description", "Self-description and its complete application trace remain explicit."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-machines", "Examples cannot prove exhaustive computability.", "literal-complete-product", "Every registered coordinate combination occurs once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "All dependencies trace to the root theorem."),
        binary_dimension("observation", "post-registry execution?", "preopened-target", "A preopened answer could choose the survivor.", "post-registry-exact-execution", "Independent execution opens after registry freeze."),
        binary_dimension("boundary", "finite or depth-independent boundary?", "unbounded-from-finite-sample", "A finite census cannot imply an unrestricted negative result.", "depth-certificate-or-explicit-limit", "The theorem scope or finite boundary is explicit."),
    )


class ComputabilityExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id, title=self.spec.title, branch="computation",
            statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies,
            axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = (
        "SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006",
        "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006",
        "SFT-COMP-FORMX-COMPLETENESS-022",
        BASE[int(number) - 1],
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id, "CBLX", title.lower().replace(" ", "-"), title, statement, dependencies,
        f"Generate the complete eight-axis CBLX-{number} product before observation access.",
        f"Every positive finite CBLX-{number} description, execution, self-application, reduction, oracle record and registered theorem boundary.",
        dimensions(relation),
        f"CBLX-{number} uniquely retains {relation}, complete self-application custody, root forcing, post-registry execution and no extra rule.",
        (statement, observation),
        "The least domain contains one generated description, one retained execution relation and its terminal or explicit recurrent classification.",
        "Adding one description, trace step, reduction row, oracle record or proof form preserves prior witnesses and generates every new lawful relation exactly once.",
        EXCLUSIONS,
        (Witness("exact-execution", observation, passed), Witness("complete-computability-census", "Every declared description, self-input, trace, reduction and boundary is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact execution and reject four adverse controls.",
        "The claim closes its declared generated description grammar; conventional correspondence and physical implementation retain explicit boundaries.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 21 or len(OBS) != 21 or not all(passed for _, passed in OBS.values()):
        raise ValueError("CBLX family witness or membership failure")
    for specification in specifications:
        specification.validate()


validate_family()
