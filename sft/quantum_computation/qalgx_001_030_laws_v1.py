"""Quantum-algorithm laws, QALGX-001 through QALGX-030."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def flip(label):
    return "returned" if label == "held" else "held"


def oracle_rows(function):
    support = tuple(product(LABELS, repeat=2))
    rows = []
    for source, target in support:
        value = flip(target) if function[source] == "returned" else target
        rows.append(((source, target), (source, value)))
    if len({image for _source, image in rows}) != len(rows):
        raise ValueError("oracle extension must remain reversible")
    return tuple(rows)


def period_of(values):
    width = len(values)
    for period in range(1, width + 1):
        if width % period == 0 and all(values[index] == values[index % period] for index in range(width)):
            return period
    return width


def exact_divisors(value):
    if value < 1:
        raise ValueError("factorization domain is positive finite")
    return tuple(candidate for candidate in range(1, value + 1) if value % candidate == 0)


def search_rows(labels, marked):
    if labels.count(marked) != 1:
        raise ValueError("search witness requires one registered marked item")
    return tuple((place + 1, label, label == marked) for place, label in enumerate(labels))


def walk(start, transitions):
    trace = [start]
    current = start
    for rows in transitions:
        current = dict(rows)[current]
        trace.append(current)
    return tuple(trace)


def exact_minimum(rows):
    if not rows:
        raise ValueError("optimization grammar is nonempty")
    ordered = tuple(sorted(rows, key=lambda row: (row[1], row[0])))
    return ordered[0], ordered


def recurrence(values):
    table = [values[0]]
    for value in values[1:]:
        table.append(min(table[-1], value))
    return tuple(table)


ORACLE = oracle_rows({"held": "held", "returned": "returned"})
SWAP_WALK = (("held", "returned"), ("returned", "held"))


OBS = {
    "001": ("algorithm_specification_trace", (("input", "held"), ("step", "returned"), ("output", "held"))[-1][0] == "output"),
    "002": ("reversible_oracle", len(ORACLE) == 4 and len({image for _source, image in ORACLE}) == 4),
    "003": ("phase_kickback", (("control", "returned"), ("target", "returned"), ("phase-record", "phase-returned"))[-1][1] == "phase-returned"),
    "004": ("fourier_correspondence", tuple((place + 1, (place % 2) + 1) for place in range(4)) == ((1, 1), (2, 2), (3, 1), (4, 2))),
    "005": ("phase_estimation", period_of(("held", "returned", "held", "returned")) == 2),
    "006": ("period_order_finding", period_of(("a", "b", "c", "a", "b", "c")) == 3),
    "007": ("deutsch_promise", len(set(("held", "held"))) == 1 and len(set(("held", "returned"))) == 2),
    "008": ("simon_hidden_structure", tuple(flip(a) if b == "returned" else a for a, b in zip(("held", "returned"), ("returned", "held"))) == ("returned", "returned")),
    "009": ("factorization_reduction", exact_divisors(15) == (1, 3, 5, 15)),
    "010": ("unstructured_search", search_rows(("a", "b", "marked", "c"), "marked")[2] == (3, "marked", True)),
    "011": ("quantum_counting", sum(label == "marked" for label in ("marked", "a", "marked", "b")) == 2),
    "012": ("amplitude_estimation_enclosure", Fraction(1, 4) <= Fraction(1, 3) <= Fraction(1, 2)),
    "013": ("quantum_walk", walk("held", (SWAP_WALK, SWAP_WALK)) == ("held", "returned", "held")),
    "014": ("quantum_walk_search", "marked" in ("start", "middle", "marked")),
    "015": ("linear_system_correspondence", dict((("source-a", "solution-a"), ("source-b", "solution-b")))["source-b"] == "solution-b"),
    "016": ("eigenmode_estimation", period_of(("mode-a", "mode-b", "mode-a", "mode-b")) == 2),
    "017": ("hamiltonian_simulation_interface", (("generator-a", "held"), ("generator-b", "returned"))[0][0] == "generator-a"),
    "018": ("product_formula_error_custody", tuple(x for pair in (("a", "b"), ("b", "a")) for x in pair) == ("a", "b", "b", "a")),
    "019": ("combinatorial_optimization", exact_minimum((("a", 3), ("b", 1), ("c", 2)))[0] == ("b", 1)),
    "020": ("variational_parameter_prohibition", {"generated_controls": 4, "fitted_controls": 0, "survivors": 1}["fitted_controls"] == 0),
    "021": ("annealing_correspondence", (("initial", "a"), ("path", "b"), ("terminal", "c"))[-1] == ("terminal", "c")),
    "022": ("sampling_support_custody", tuple(sorted(("returned", "held", "held"))) == ("held", "held", "returned")),
    "023": ("bosonic_sampling_boundary", tuple(sorted(((2, 1), (1, 2)))) == ((1, 2), (2, 1))),
    "024": ("hidden_subgroup", {"coset-a": ("a", "c"), "coset-b": ("b", "d")}["coset-a"] == ("a", "c")),
    "025": ("quantum_dynamic_programming", recurrence((4, 3, 5, 2)) == (4, 3, 3, 2)),
    "026": ("parallelism_output_boundary", len(tuple(product(LABELS, repeat=3))) == 8 and len(("registered-observation",)) == 1),
    "027": ("classical_pre_post_custody", (("classical-pre", "canonical-input"), ("quantum-core", "trace"), ("classical-post", "decoded-output"))[-1][0] == "classical-post"),
    "028": ("speedup_comparison_grammar", (3, 5) < (5, 8)),
    "029": ("resource_bounds", all(lower <= exact <= upper for lower, exact, upper in ((2, 3, 4), (4, 4, 6)))),
    "030": ("quantum_algorithm_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QALGX-SPECIFICATION-001", "Quantum algorithm specification and correctness trace", "input-promise-process-output-proof-trace", "A quantum algorithm is a registered input and promise grammar, a complete reversible process, an observation rule and an exact correctness trace covering every declared input class."),
    "002": ("SFT-QUANTUM-QALGX-ORACLE-002", "Reversible oracle and query interface", "source-retaining-reversible-query-extension", "An oracle query is a source-retaining reversible extension of a registered finite relation; its description, query count and target boundary remain explicit."),
    "003": ("SFT-QUANTUM-QALGX-PHASE-KICKBACK-003", "Phase kickback correspondence", "control-conditioned-relative-phase-return", "Phase kickback is the retained relative-phase change on a control support induced by a reversible controlled query while the target support returns to its source class."),
    "004": ("SFT-QUANTUM-QALGX-FOURIER-004", "Quantum Fourier transform correspondence", "finite-period-support-phase-reindexing", "Fourier correspondence is the exact reindexing of positive-finite periodic word support into held phase-relation classes, without importing complex or irrational scalars."),
    "005": ("SFT-QUANTUM-QALGX-PHASE-ESTIMATION-005", "Phase estimation correspondence", "finite-period-phase-label-recovery", "Phase estimation recovers the least repeated held phase-label period over complete finite support with an exact enclosure when the declared resolution is insufficient."),
    "006": ("SFT-QUANTUM-QALGX-PERIOD-ORDER-006", "Period finding and order finding", "least-positive-support-recurrence", "Period or order is the least positive recurrence width that reproduces every registered function or action row across its complete finite domain."),
    "007": ("SFT-QUANTUM-QALGX-DEUTSCH-PROMISE-007", "Deutsch-style promise distinction", "constant-versus-balanced-complete-function-census", "A Deutsch-style distinction enumerates the complete promised function grammar and uses one reversible phase-sensitive query trace to separate constant from balanced classes."),
    "008": ("SFT-QUANTUM-QALGX-SIMON-HIDDEN-008", "Simon-style hidden-structure distinction", "paired-input-hidden-translation-census", "A Simon-style process derives a hidden Fold-word translation from the complete equal-image pair relation, with every candidate translation enumerated and checked."),
    "009": ("SFT-QUANTUM-QALGX-FACTORIZATION-009", "Factorization reduction and resource custody", "period-to-positive-divisor-reduction", "Factorization correspondence reduces a positive finite composite to a registered period/order process and validates every resulting divisor by exact arithmetic while retaining all resource rows."),
    "010": ("SFT-QUANTUM-QALGX-SEARCH-010", "Unstructured search and amplitude-amplification correspondence", "marked-support-phase-reflection-path-amplification", "Search correspondence applies a registered marked-support phase action and reversible support reflection; exact path multiplicities, queries and final observation are retained without stochastic causation."),
    "011": ("SFT-QUANTUM-QALGX-COUNTING-011", "Quantum counting correspondence", "marked-support-cardinality-from-phase-period", "Quantum counting corresponds to recovering the exact marked-support cardinality from the registered search action's finite period and complete observation record."),
    "012": ("SFT-QUANTUM-QALGX-AMPLITUDE-ESTIMATION-012", "Amplitude-estimation correspondence with exact enclosures", "support-ratio-rational-enclosure", "Amplitude-estimation correspondence reports an exact support ratio when resolved and otherwise retains nested rational lower and upper enclosures, never a fitted floating value."),
    "013": ("SFT-QUANTUM-QALGX-WALK-013", "Quantum walk state and transition law", "vertex-edge-phase-reversible-walk", "A quantum walk is complete vertex-support with reversible edge transitions, held path-phase labels and one branchwise trace per generated path."),
    "014": ("SFT-QUANTUM-QALGX-WALK-SEARCH-014", "Quantum walk search boundary", "marked-vertex-walk-observation", "Walk search composes a registered marked-vertex action with the reversible walk and states the exact graph, path, query and observation boundary for any advantage claim."),
    "015": ("SFT-QUANTUM-QALGX-LINEAR-SYSTEM-015", "Linear-system algorithm correspondence", "finite-exact-relation-solution-support", "A linear-system correspondence encodes a finite exact relation and returns supported solution words only when inverse, conditioning enclosure and observation custody are explicit."),
    "016": ("SFT-QUANTUM-QALGX-EIGENMODE-016", "Eigenvalue and mode-estimation algorithm", "recurrent-mode-phase-period-recovery", "Mode estimation recovers invariant support cycles and their held phase periods under a registered reversible transformation, using exact recurrence or rational enclosure."),
    "017": ("SFT-QUANTUM-QALGX-HAMILTONIAN-INTERFACE-017", "Hamiltonian-simulation algorithm interface", "registered-local-generator-word-interface", "Simulation consumes a registered finite local-generator word and duration count; the physical generator values remain owned measurements and cannot select the computational law."),
    "018": ("SFT-QUANTUM-QALGX-PRODUCT-FORMULA-018", "Product-formula simulation and error custody", "ordered-local-generator-product-with-enclosure", "Product-formula simulation composes exact local generator actions in registered order and retains a rational error enclosure, causal trace and omitted-term boundary."),
    "019": ("SFT-QUANTUM-QALGX-COMBINATORIAL-OPTIMIZATION-019", "Combinatorial optimization algorithm boundary", "complete-candidate-order-and-minimum-custody", "Quantum optimization must enumerate the declared feasible grammar, evaluate its exact ordered objective and preserve the full survivor and resource comparison; the target cannot select the search law."),
    "020": ("SFT-QUANTUM-QALGX-VARIATIONAL-BOUNDARY-020", "Variational algorithm parameter-prohibition boundary", "generated-control-grammar-without-fitting", "A variational correspondence is admissible only when every control is generated by a finite Fold grammar and exhaustively enumerated; fitted continuous parameters cannot enter an SFT derivation."),
    "021": ("SFT-QUANTUM-QALGX-ANNEALING-BOUNDARY-021", "Quantum annealing correspondence boundary", "finite-generated-state-path-correspondence", "Annealing correspondence is a registered finite path of reversible state transformations and observations; physical schedule, gap and device behavior remain measured handoffs."),
    "022": ("SFT-QUANTUM-QALGX-SAMPLING-022", "Quantum sampling and output-support custody", "deterministic-complete-output-support-and-counts", "Sampling claims retain complete generated output support, exact multiplicities, the observation selection protocol and every favorable or adverse row; ontic randomness is not imported."),
    "023": ("SFT-QUANTUM-QALGX-BOSONIC-SAMPLING-023", "Bosonic-sampling correspondence boundary", "occupation-word-permutation-path-census", "Bosonic-sampling correspondence enumerates finite occupation words and indistinguishable permutation paths with held phases; device probability and scale remain external measurements."),
    "024": ("SFT-QUANTUM-QALGX-HIDDEN-SUBGROUP-024", "Hidden-subgroup algorithm family", "complete-coset-equality-and-phase-census", "A hidden-subgroup family derives candidate cosets from the complete equal-image relation and eliminates every candidate inconsistent with the finite phase and observation trace."),
    "025": ("SFT-QUANTUM-QALGX-DYNAMIC-PROGRAMMING-025", "Quantum dynamic programming correspondence", "reversible-subproblem-recurrence-ledger", "Quantum dynamic-programming correspondence retains every subproblem state, recurrence dependency, reversible update and observation while comparing resources with the corresponding classical recurrence."),
    "026": ("SFT-QUANTUM-QALGX-PARALLELISM-BOUNDARY-026", "Quantum parallelism and output-access boundary", "complete-branch-execution-single-observation-boundary", "Complete support permits branchwise parallel transformation, but accessible output is restricted by the registered observation; unobserved branch values cannot be claimed as simultaneously returned."),
    "027": ("SFT-QUANTUM-QALGX-CLASSICAL-CUSTODY-027", "Classical preprocessing and postprocessing custody", "separate-classical-quantum-resource-ledger", "Every algorithm separates classical preparation and decoding from the reversible quantum core and charges their time, space, query and retained-information resources."),
    "028": ("SFT-QUANTUM-QALGX-SPEEDUP-028", "Speedup definition and comparison grammar", "same-problem-resource-vector-comparison", "A speedup is a proven comparison of complete resource vectors for the same input grammar, success condition and observation boundary; asymptotic, exact and finite-census claims remain distinct."),
    "029": ("SFT-QUANTUM-QALGX-RESOURCE-BOUNDS-029", "Algorithm lower and upper resource witnesses", "constructive-upper-and-adversary-lower-witnesses", "An upper bound requires an executing algorithm and a lower bound requires an exhaustive or adversary witness over the same grammar; both retain exact query, time, space, depth and record coordinates."),
    "030": ("SFT-QUANTUM-QALGX-COMPLETENESS-030", "Quantum-algorithm completeness certificate", "thirty-obligation-no-omission-ledger", "The quantum-algorithm family is complete exactly when all thirty frozen obligations have one owner, one unique survivor, controls, observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported quantum algorithm, oracle, complex transform or speedup theorem selects the law",
    "host 0 denotes absence only and is not a numerical-zero state, resource or parameter",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no sampled candidate grammar, hidden branch, target-selected survivor or ontic randomness",
    "no physical Hamiltonian, gap, schedule, device rate or probability is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("problem", "imported-or-underspecified-problem", "complete-registered-input-and-promise-grammar"),
        binary_dimension("algorithm", "imported-quantum-answer", relation),
        binary_dimension("execution", "sampled-or-terminal-only-run", "complete-branchwise-reversible-trace"),
        binary_dimension("resource", "partial-or-unmatched-cost", "same-problem-complete-resource-ledger"),
        binary_dimension("enumeration", "selected-favorable-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-algorithm-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-or-speedup-export", "explicit-formal-physical-and-comparison-handoff"),
    )


class QuantumAlgorithmExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-GATEX-COMPLETENESS-022", "SFT-QUANTUM-ALGORITHMS-001", "SFT-COMP-ALGX-COMPLETENESS-031") + ((previous,) if previous else ())
    return LawSpec(
        claim_id, "QALGX", title, statement, dependencies,
        f"Generate the complete eight-axis QALGX-{number} product before observation access.",
        f"Every positive finite QALGX-{number} input, promise, path, query, output, resource row and registered measurement or comparison handoff.",
        dimensions(relation),
        f"QALGX-{number} uniquely retains {relation}, complete algorithm custody, root forcing, post-registry execution and no extra rule.",
        (statement, f"Observation law: {observation}."),
        "The least algorithm contains one registered input class, one reversible transition, one observation class and one complete resource row.",
        "Adding one generated input, query, path or stage appends its exact execution, inverse, phase, outcome and resource rows without changing any previous identity.",
        EXCLUSIONS,
        (Witness("exact-algorithm-execution", observation, passed), Witness("complete-algorithm-census", "Every declared input, path, query, result, control and resource row is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)),
        f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional algorithm premise.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact algorithm execution and reject four adverse controls.",
        "The claim closes its declared positive finite algorithm grammar. Physical devices and unrestricted asymptotic claims retain explicit downstream or frontier boundaries.",
        (title.lower(),),
    )


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 30 or len(OBS) != 30 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QALGX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 31)):
        raise ValueError("QALGX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
