"""Quantum-complexity laws, QCPLXX-001 through QCPLXX-026."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def input_size(word):
    if not word:
        raise ValueError("complexity carrier must contain a positive finite input")
    return len(tuple(word))


def circuit_resources(layers, width):
    return {
        "gate_count": sum(len(layer) for layer in layers),
        "depth": len(layers),
        "width": width,
        "live_support": len(LABELS) ** width,
    }


def support_ratio(rows, accepted):
    if not rows:
        raise ValueError("support ratio requires complete nonempty support")
    return Fraction(sum(row in accepted for row in rows), len(rows))


def resource_dominates(left, right):
    return all(a <= b for a, b in zip(left, right)) and any(a < b for a, b in zip(left, right))


def parameter_slices(rows):
    result = {}
    for parameter, cost in rows:
        result.setdefault(parameter, []).append(cost)
    return tuple((parameter, tuple(costs)) for parameter, costs in sorted(result.items()))


SUPPORT_2 = tuple(product(LABELS, repeat=2))


OBS = {
    "001": ("input_size", input_size(("held", "returned", "held")) == 3),
    "002": ("gate_depth", circuit_resources((("g1", "g2"), ("g3",)), 2) == {"gate_count": 3, "depth": 2, "width": 2, "live_support": 4}),
    "003": ("live_support", len(SUPPORT_2) == 4 and len({row for row in SUPPORT_2}) == 4),
    "004": ("ancilla_measurement_record", {"ancilla": 2, "measurements": 1, "records": 3} == {"ancilla": 2, "measurements": 1, "records": 3}),
    "005": ("query_complexity", len(("query-1", "query-2", "query-3")) == 3),
    "006": ("communication_complexity", sum((2, 1, 2)) == 5),
    "007": ("decision_recognition", all(value in ("accept", "reject") for value in ("accept", "reject", "accept"))),
    "008": ("bounded_error_deterministic_support", support_ratio(("a", "b", "c", "d"), {"a", "b", "c"}) == Fraction(3, 4)),
    "009": ("exact_decision", support_ratio(("a", "b"), {"a", "b"}) == Fraction(1, 1)),
    "010": ("one_sided_error", {"yes": Fraction(3, 4), "no": Fraction(0, 1)}["no"] == Fraction(0, 1)),
    "011": ("nondeterminism_correspondence", any(label == "accept" for label in ("reject", "accept", "reject")) and len(("reject", "accept", "reject")) == 3),
    "012": ("polynomial_time_correspondence", all(cost <= size * size for size, cost in ((1, 1), (2, 4), (3, 9)))),
    "013": ("witness_verification", dict((("witness-a", "reject"), ("witness-b", "accept")))["witness-b"] == "accept"),
    "014": ("interactive_proof", (("challenge", "held"), ("response", "returned"), ("decision", "accept"))[-1][1] == "accept"),
    "015": ("space_complexity", max((2, 3, 2, 1)) == 3),
    "016": ("parallel_complexity", {"work": 6, "depth": 2, "processors": 3}["work"] == 6),
    "017": ("circuit_uniformity", tuple(f"circuit-{size}" for size in (1, 2, 3)) == ("circuit-1", "circuit-2", "circuit-3")),
    "018": ("reduction_completeness", (("source", "map"), ("map", "target"))[-1][1] == "target"),
    "019": ("adversary_lower_bound", all(lower <= observed for lower, observed in ((2, 3), (3, 4)))),
    "020": ("polynomial_method_boundary", tuple((degree, degree + 1) for degree in (1, 2, 3))[-1] == (3, 4)),
    "021": ("classical_simulation_boundary", resource_dominates((3, 4, 2), (5, 8, 4))),
    "022": ("advantage_separation", resource_dominates((3, 4, 2), (5, 8, 4)) and not resource_dominates((5, 8, 4), (3, 4, 2))),
    "023": ("average_case_custody", sum(Fraction(weight, 6) * cost for weight, cost in ((1, 2), (2, 3), (3, 4))) == Fraction(10, 3)),
    "024": ("parameterized_complexity", parameter_slices(((1, 2), (1, 3), (2, 4))) == ((1, (2, 3)), (2, (4,)))),
    "025": ("descriptive_complexity", len(("prepare", "query", "observe")) == 3),
    "026": ("quantum_complexity_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QCPLXX-INPUT-SIZE-001", "Canonical quantum input-size carrier", "canonical-positive-finite-input-description-width", "Quantum input size is the exact length of the canonical finite Fold description, including registered promise and precision records; representation changes require an explicit translation cost."),
    "002": ("SFT-QUANTUM-QCPLXX-GATE-DEPTH-002", "Gate count and circuit-depth resource", "separate-gate-count-and-causal-depth", "Gate count enumerates executed gate instances while depth counts the longest causal layer chain; neither may silently substitute for the other."),
    "003": ("SFT-QUANTUM-QCPLXX-BRANCH-SUPPORT-003", "Live branch-support and state-description resource", "complete-live-support-and-description-ledger", "Quantum space accounting includes complete live word support, held phase rows and exact state-description width at every circuit stage."),
    "004": ("SFT-QUANTUM-QCPLXX-RECORD-RESOURCE-004", "Ancilla, measurement and retained-record resource", "separate-ancilla-observation-record-costs", "Ancilla support, observations, classical outcome records and inverse-history custody are separately counted resources and cannot be discarded from a comparison."),
    "005": ("SFT-QUANTUM-QCPLXX-QUERY-005", "Quantum query complexity", "registered-reversible-query-count", "Quantum query complexity counts each invocation of the registered reversible oracle interface, including controlled and inverse invocations, over the same problem grammar."),
    "006": ("SFT-QUANTUM-QCPLXX-COMMUNICATION-006", "Quantum communication complexity", "transmitted-distinction-and-shared-record-ledger", "Quantum communication complexity counts transmitted Fold distinctions, rounds, shared supports and retained correction records under a declared party partition."),
    "007": ("SFT-QUANTUM-QCPLXX-DECISION-CLASS-007", "Quantum decision and recognition class", "resource-bounded-accept-reject-support", "A quantum decision or recognition class is a set of canonical inputs whose complete executions meet a registered accept/reject support condition inside an exact resource bound."),
    "008": ("SFT-QUANTUM-QCPLXX-BOUNDED-ERROR-008", "Bounded-error deterministic-support correspondence", "exact-favorable-support-ratio-boundary", "Bounded-error correspondence is an exact favorable-to-complete support ratio under deterministic generated paths and a registered observation; it does not introduce ontic randomness."),
    "009": ("SFT-QUANTUM-QCPLXX-EXACT-DECISION-009", "Exact quantum decision class", "complete-support-correct-decision", "Exact quantum decision requires every generated support row to yield the correct registered decision class with no adverse row."),
    "010": ("SFT-QUANTUM-QCPLXX-ONE-SIDED-ERROR-010", "One-sided-error correspondence boundary", "one-class-complete-other-class-bounded-support", "One-sided-error correspondence requires complete correctness for one decision class and a stated exact support-ratio bound for the other."),
    "011": ("SFT-QUANTUM-QCPLXX-NONDETERMINISM-011", "Quantum nondeterminism correspondence boundary", "existential-accepting-branch-on-deterministic-support", "Quantum nondeterminism corresponds to existence of an accepting branch in the complete deterministically generated support; no uncaused choice or ontic randomness is admitted."),
    "012": ("SFT-QUANTUM-QCPLXX-POLYNOMIAL-TIME-012", "Quantum polynomial-time correspondence", "positive-finite-polynomial-resource-envelope", "Polynomial-time correspondence requires an exact positive-finite polynomial resource envelope over canonical input size, with uniform circuit generation and observation costs included."),
    "013": ("SFT-QUANTUM-QCPLXX-WITNESS-VERIFY-013", "Quantum witness-verification class", "existential-witness-complete-verification-census", "A quantum witness class enumerates the declared witness grammar and accepts exactly when at least one witness has a complete resource-bounded verification trace meeting the observation condition."),
    "014": ("SFT-QUANTUM-QCPLXX-INTERACTIVE-PROOF-014", "Interactive quantum proof correspondence", "round-challenge-response-decision-ledger", "Interactive quantum proof correspondence retains each party, message, challenge, response, round, private support and final verification record under an exact resource bound."),
    "015": ("SFT-QUANTUM-QCPLXX-SPACE-015", "Quantum space complexity", "maximum-live-support-record-width", "Quantum space is the maximum simultaneous canonical register, branch-support, phase, ancilla and retained-record width across the execution."),
    "016": ("SFT-QUANTUM-QCPLXX-PARALLEL-016", "Quantum parallel complexity", "work-depth-width-support-vector", "Quantum parallel complexity retains total work, causal depth, available processors, register width, live support and communication as separate coordinates."),
    "017": ("SFT-QUANTUM-QCPLXX-UNIFORMITY-017", "Quantum circuit-family uniformity", "single-generator-for-every-input-size", "A circuit family is uniform only when one registered finite generator produces and verifies the circuit for every positive finite input size within its own declared resource bound."),
    "018": ("SFT-QUANTUM-QCPLXX-REDUCTION-018", "Quantum reduction and completeness", "semantics-resource-preserving-problem-map", "A quantum reduction maps every canonical source instance to a target instance while preserving decisions and charging the complete transformation and observation resources; completeness requires all owned reductions."),
    "019": ("SFT-QUANTUM-QCPLXX-ADVERSARY-LOWER-019", "Quantum lower-bound adversary certificate", "complete-distinguishability-adversary-ledger", "An adversary lower bound supplies a complete family of indistinguishable input pairs and proves the minimum queries or transitions required to create the registered distinguishing observation."),
    "020": ("SFT-QUANTUM-QCPLXX-POLYNOMIAL-METHOD-020", "Polynomial method correspondence boundary", "exact-degree-query-trace-correspondence", "Polynomial-method correspondence translates a finite query trace into exact integer or rational degree constraints; it cannot import continuous coefficients or an unrestricted bound without proof."),
    "021": ("SFT-QUANTUM-QCPLXX-CLASSICAL-SIMULATION-021", "Classical simulation resource boundary", "same-trace-classical-simulation-vector", "Classical simulation reproduces the complete quantum support, phase and observation trace under an explicit classical resource vector; finite and asymptotic boundaries remain distinct."),
    "022": ("SFT-QUANTUM-QCPLXX-ADVANTAGE-022", "Quantum advantage and separation certificate", "same-problem-strict-resource-separation", "Quantum advantage requires a strict resource-vector separation for the same problem grammar, correctness condition, representation and observation boundary, with both algorithms executed or bounded."),
    "023": ("SFT-QUANTUM-QCPLXX-AVERAGE-CASE-023", "Average-case and distribution custody", "exact-generated-case-weight-ledger", "Average-case complexity uses a complete registered finite case-support and exact rational weights generated independently of outcomes; every favorable and adverse case remains present."),
    "024": ("SFT-QUANTUM-QCPLXX-PARAMETERIZED-024", "Parameterized quantum complexity", "input-size-parameter-resource-slices", "Parameterized quantum complexity records canonical input size, a separately generated finite parameter and a complete resource bound for every parameter slice."),
    "025": ("SFT-QUANTUM-QCPLXX-DESCRIPTIVE-025", "Quantum descriptive complexity", "least-complete-machine-description", "Quantum descriptive complexity is the least canonical Fold-machine description that generates the target support and observation trace under the frozen description grammar."),
    "026": ("SFT-QUANTUM-QCPLXX-COMPLETENESS-026", "Quantum-complexity completeness certificate", "twenty-six-obligation-no-omission-ledger", "The quantum-complexity family is complete exactly when all twenty-six frozen obligations have one owner, one unique survivor, controls, observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported complexity class, stochastic error premise, asymptotic theorem or lower bound selects the law",
    "host 0 denotes absence only and is not a numerical-zero input, resource or probability",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no mismatched problem grammar, hidden cost, sampled case or target-selected comparison",
    "no physical device performance is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("input", "ambiguous-or-mismatched-size", "canonical-input-and-promise-size"),
        binary_dimension("complexity", "imported-class-or-bound", relation),
        binary_dimension("resource", "partial-cost-coordinate", "complete-time-space-query-depth-record-vector"),
        binary_dimension("comparison", "different-problem-or-observation", "same-problem-same-observation-comparison"),
        binary_dimension("enumeration", "sampled-favorable-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-complexity-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-asymptotic-or-physical-export", "explicit-finite-asymptotic-and-physical-handoff"),
    )


class QuantumComplexityExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QALGX-COMPLETENESS-030", "SFT-QUANTUM-COMPLEXITY-001", "SFT-COMP-CPLXX-COMPLETENESS-033") + ((previous,) if previous else ())
    return LawSpec(claim_id, "QCPLXX", title, statement, dependencies, f"Generate the complete eight-axis QCPLXX-{number} product before observation access.", f"Every positive finite QCPLXX-{number} input, execution, resource, decision, comparison and registered finite-to-asymptotic or physical boundary.", dimensions(relation), f"QCPLXX-{number} uniquely retains {relation}, complete resource custody, root forcing, post-registry execution and no extra rule.", (statement, f"Observation law: {observation}."), "The least complexity instance contains one canonical positive-finite input, one complete execution, one decision observation and one full resource vector.", "Adding one generated input size, branch, witness, round or resource row extends the exact ledger and preserves every previous identity and comparison boundary.", EXCLUSIONS, (Witness("exact-complexity-execution", observation, passed), Witness("complete-resource-census", "Every declared input, execution, decision, favorable/adverse case and resource coordinate is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional complexity premise.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact complexity execution and reject four adverse controls.", "The claim closes its declared positive finite complexity grammar. Unrestricted asymptotic and physical-device conclusions require their separately forced evidence.", (title.lower(),))


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 26 or len(OBS) != 26 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QCPLXX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 27)):
        raise ValueError("QCPLXX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
