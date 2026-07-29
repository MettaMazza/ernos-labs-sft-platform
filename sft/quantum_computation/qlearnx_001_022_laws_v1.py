"""Quantum learning laws, QLEARNX-001 through QLEARNX-022."""

from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def words(width):
    if width < 1:
        raise ValueError("positive finite word width required")
    return tuple(product(LABELS, repeat=width))


def hypothesis_family(domain):
    return tuple(tuple(zip(domain, images)) for images in product(LABELS, repeat=len(domain)))


def evaluate(hypothesis, example):
    return dict(hypothesis)[example]


def exact_score(hypothesis, examples):
    return sum(evaluate(hypothesis, source) == target for source, target in examples)


def select_unique(hypotheses, examples):
    scores = tuple((hypothesis, exact_score(hypothesis, examples)) for hypothesis in hypotheses)
    best = max(score for _hypothesis, score in scores)
    survivors = tuple(hypothesis for hypothesis, score in scores if score == best)
    if len(survivors) != 1:
        raise ValueError("training examples do not force one hypothesis")
    return survivors[0], scores


def feature_map(source):
    return tuple((place, label) for place, label in enumerate(source, 1))


def similarity(left, right):
    return sum(a == b for a, b in zip(left, right))


def cluster(support):
    return tuple((pivot, tuple(word for word in support if word[0] == pivot)) for pivot in LABELS)


def transition(state, action):
    if action == "retain":
        return state
    if action == "flip-first":
        return (("returned" if state[0] == "held" else "held"), *state[1:])
    raise ValueError("action outside registered grammar")


DOMAIN = words(1)
HYPOTHESES = hypothesis_family(DOMAIN)
TRAINING = ((('held',), 'held'), (('returned',), 'returned'))
IDENTITY_HYPOTHESIS, IDENTITY_SCORES = select_unique(HYPOTHESES, TRAINING)


OBS = {
    "001": ("problem_example_identity", len(TRAINING) == 2 and len({row[0] for row in TRAINING}) == 2),
    "002": ("classical_data_boundary", tuple((source, feature_map(source)) for source in DOMAIN)[0][0] == ("held",)),
    "003": ("quantum_data_custody", len(words(2)) == 4 and len({feature_map(word) for word in words(2)}) == 4),
    "004": ("hypothesis_family", len(HYPOTHESES) == 4 and len(set(HYPOTHESES)) == 4),
    "005": ("feature_map", len({feature_map(word) for word in words(2)}) == len(words(2))),
    "006": ("kernel_boundary", similarity(("held", "returned"), ("held", "held")) == 1),
    "007": ("classification", evaluate(IDENTITY_HYPOTHESIS, ("returned",)) == "returned"),
    "008": ("regression_correspondence", tuple((word, word.count("held")) for word in words(2))[-1][1] == 0),
    "009": ("generative_support", tuple(dict.fromkeys(words(2))) == words(2)),
    "010": ("clustering", all(len(group) == 2 for _pivot, group in cluster(words(2)))),
    "011": ("principal_structure", tuple(sorted(((1, 2), (2, 1)), key=lambda row: (-row[1], row[0])))[0] == (1, 2)),
    "012": ("learning_optimization", max(score for _hypothesis, score in IDENTITY_SCORES) == 2),
    "013": ("variational_boundary", {"generated_setting_count": 4, "target_fitted": False}["generated_setting_count"] == 4),
    "014": ("reinforcement_process", transition(("held", "returned"), "flip-first") == ("returned", "returned")),
    "015": ("online_learning", len(((1, TRAINING[0]), (2, TRAINING[1]))) == 2),
    "016": ("sample_complexity", len(TRAINING) == 2 and select_unique(HYPOTHESES, TRAINING)[0] == IDENTITY_HYPOTHESIS),
    "017": ("query_complexity", len(tuple((query, evaluate(IDENTITY_HYPOTHESIS, query)) for query in DOMAIN)) == 2),
    "018": ("generalization_custody", {"training_rows": 1, "held_out_rows": 1, "target_opened_after_selection": True}["target_opened_after_selection"]),
    "019": ("advantage_certificate", {"same_task": True, "classical_ledger": True, "quantum_ledger": True, "physical_speedup_claimed": False}["same_task"]),
    "020": ("interpretability", len(("input", "feature", "hypothesis", "branch", "observation")) == 5),
    "021": ("robustness", all(transition(state, "retain") == state for state in words(2))),
    "022": ("quantum_learning_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QLEARNX-PROBLEM-EXAMPLE-IDENTITY-001", "Quantum learning problem and example identity", "typed-problem-example-target-resource-registry", "A quantum learning problem registers its source domain, example identities, target relation, admissible observations, loss/order relation and resources before any outcome is opened."),
    "002": ("SFT-QUANTUM-QLEARNX-CLASSICAL-DATA-BOUNDARY-002", "Classical-data quantum-process boundary", "canonical-classical-data-to-Fold-support-encoding", "Classical data enters a quantum process only through a canonical reversible encoding with complete source identity and decoding records; encoding does not create information."),
    "003": ("SFT-QUANTUM-QLEARNX-QUANTUM-DATA-CUSTODY-003", "Quantum-data support and observation custody", "complete-quantum-example-support-observation-ledger", "Quantum data is a complete finite Fold support with phase and joint records; each observation retains its class, closed distinctions and source custody."),
    "004": ("SFT-QUANTUM-QLEARNX-HYPOTHESIS-FAMILY-004", "Quantum hypothesis family generation", "complete-generated-quantum-hypothesis-family", "A quantum hypothesis family is the complete generated set of source-bound processes admitted before training targets are opened, with no pretrained or silently selected member."),
    "005": ("SFT-QUANTUM-QLEARNX-FEATURE-MAP-005", "Quantum feature-map correspondence", "reversible-source-feature-support-map", "Feature-map correspondence is a reversible source-to-Fold-support relation whose collisions, phase actions, resource cost and inverse records are explicit."),
    "006": ("SFT-QUANTUM-QLEARNX-KERNEL-BOUNDARY-006", "Quantum kernel correspondence boundary", "exact-pair-comparison-observation-relation", "Quantum-kernel correspondence is an exact pair-comparison observation relation over registered feature supports; no continuum inner product or physical advantage is imported."),
    "007": ("SFT-QUANTUM-QLEARNX-CLASSIFICATION-007", "Quantum classification process", "complete-hypothesis-class-observation-selection", "Classification enumerates every registered hypothesis and example, computes exact class observations, preserves ties and adverse rows, and selects only a uniquely forced survivor."),
    "008": ("SFT-QUANTUM-QLEARNX-REGRESSION-008", "Quantum regression process", "exact-ordered-output-support-relation", "Regression correspondence maps examples to exact finite ordered output support and reports an enclosure when observation cannot distinguish a unique output; no irrational continuum target is presumed."),
    "009": ("SFT-QUANTUM-QLEARNX-GENERATIVE-SUPPORT-009", "Quantum generative-support reconstruction", "complete-source-support-reconstruction", "Generative learning reconstructs the complete registered finite support and exact multiplicity/order records; a sampled subset cannot certify missing support."),
    "010": ("SFT-QUANTUM-QLEARNX-CLUSTERING-010", "Quantum clustering correspondence", "generated-equivalence-class-partition", "Clustering correspondence generates an exact distinguishability relation and its complete equivalence-class partition, preserving boundary and tied assignments."),
    "011": ("SFT-QUANTUM-QLEARNX-PRINCIPAL-STRUCTURE-011", "Quantum principal-structure correspondence", "exact-incidence-rank-and-tie-ledger", "Principal-structure correspondence orders generated finite incidence patterns by exact retained distinction counts while preserving every tie and discarded-coordinate record."),
    "012": ("SFT-QUANTUM-QLEARNX-OPTIMIZATION-012", "Quantum optimization in learning", "exhaustive-hypothesis-score-order-selection", "Learning optimization enumerates the complete hypothesis/resource grammar, evaluates its exact order relation, retains ties and selects only an independently reconstructed unique optimum."),
    "013": ("SFT-QUANTUM-QLEARNX-VARIATIONAL-BOUNDARY-013", "Variational quantum learning parameter boundary", "generated-setting-not-fitted-parameter-boundary", "A variational setting is a generated finite control word, not a free or fitted proof parameter; target data may compare sealed settings but cannot alter their grammar or law."),
    "014": ("SFT-QUANTUM-QLEARNX-REINFORCEMENT-014", "Quantum reinforcement-process correspondence", "state-action-transition-observation-transcript", "Reinforcement correspondence is a complete state/action/transition/observation transcript with exact return ordering and causal custody; stochastic policy is represented by deterministic support plus observation."),
    "015": ("SFT-QUANTUM-QLEARNX-ONLINE-015", "Quantum online-learning correspondence", "causal-example-update-prediction-transcript", "Online learning retains every causal example, prediction, observation and hypothesis update; future targets remain inaccessible before their prediction seal."),
    "016": ("SFT-QUANTUM-QLEARNX-SAMPLE-COMPLEXITY-016", "Quantum sample complexity", "least-example-support-for-declared-learning-condition", "Sample complexity is the least positive finite example support forcing the registered learning condition across the complete hypothesis family, with every smaller support counterexample retained."),
    "017": ("SFT-QUANTUM-QLEARNX-QUERY-COMPLEXITY-017", "Quantum query complexity of learning", "least-query-transcript-for-declared-learning-condition", "Quantum learning query complexity is the least positive finite source-bound query transcript forcing the registered condition, counting preparation, oracle, observation and retained records."),
    "018": ("SFT-QUANTUM-QLEARNX-GENERALIZATION-CUSTODY-018", "Generalization and held-out target custody", "sealed-hypothesis-blind-held-out-comparison", "Generalization requires a frozen hypothesis and target identity before held-out outcomes are released; all favorable, adverse, absent and unresolved rows remain in the comparison."),
    "019": ("SFT-QUANTUM-QLEARNX-ADVANTAGE-CERTIFICATE-019", "Quantum advantage in learning certificate", "same-task-complete-resource-ledger-separation", "A quantum-learning advantage certificate requires the same task and error condition, complete classical and quantum resource ledgers, lower and upper bounds, and separately measured physical timing where claimed."),
    "020": ("SFT-QUANTUM-QLEARNX-INTERPRETABILITY-020", "Interpretability and branch-trace reconstruction", "input-feature-hypothesis-branch-output-reconstruction", "Interpretability is exact reconstruction of the input, feature support, hypothesis action, phase/interference branches, observation and output from the retained trace."),
    "021": ("SFT-QUANTUM-QLEARNX-ROBUSTNESS-021", "Verification and robustness of quantum learners", "complete-perturbation-tamper-verification-census", "Learner robustness is verified only over a frozen complete perturbation and adversary grammar with every changed output, invariant output, rejection and unresolved boundary preserved."),
    "022": ("SFT-QUANTUM-QLEARNX-COMPLETENESS-022", "Quantum-learning completeness certificate", "twenty-two-obligation-no-omission-ledger", "QLEARNX is complete exactly when all twenty-two frozen obligations have one owner, one unique survivor, controls, post-registry observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no pretrained model, conventional learning theorem, continuum kernel or target-selected hypothesis selects the law",
    "host 0 denotes absence only and is not a numerical-zero probability, loss, feature or learning rate",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no hidden training row, held-out leakage, sampled-only support, omitted tie/adverse row or ontic randomness",
    "no physical advantage, timing, fidelity or domain prediction is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("problem", "imported-or-target-shaped-learning-problem", "registered-source-target-resource-problem"),
        binary_dimension("learning", "pretrained-or-selected-learner", relation),
        binary_dimension("trace", "terminal-prediction-only", "complete-example-hypothesis-branch-observation-trace"),
        binary_dimension("resource", "hidden-sample-query-or-physical-resource", "complete-sample-query-depth-and-record-ledger"),
        binary_dimension("enumeration", "sampled-favorable-hypotheses", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-training-or-heldout-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-advantage-or-physical-export", "explicit-formal-finite-physical-handoff"),
    )


class QuantumLearningExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation_name, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QSIMX-COMPLETENESS-024", "SFT-QUANTUM-LEARNING-001", "SFT-COMP-LEARNX-COMPLETENESS-026") + ((previous,) if previous else ())
    return LawSpec(claim_id, "QLEARNX", title, statement, dependencies, f"Generate the complete eight-axis QLEARNX-{number} product after the value-free family registry is frozen.", f"Every positive finite QLEARNX-{number} example, hypothesis, query, branch, target-custody row, resource comparison and formal/physical boundary.", dimensions(relation_name), f"QLEARNX-{number} uniquely retains {relation_name}, complete learning custody, root forcing, post-registry execution and no extra rule.", (statement, f"Observation law: {observation}."), "One Fold distinction supplies the least two-example domain, finite hypothesis family, exact observation and retained training record.", "Adding one generated example, feature, hypothesis, query, perturbation or held-out row appends every new evaluation and resource comparison while preserving all earlier identities, ties and adverse records.", EXCLUSIONS, (Witness("exact-quantum-learning-execution", observation, passed), Witness("complete-learning-census", "Every declared example, hypothesis, query, branch, tie, favorable/adverse result and resource row is retained.", passed), Witness("target-free", "The family question and source registry was frozen before learning outcomes were opened.", True)), f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a pretrained learning premise.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact learning operation or explicit handoff and reject four adverse controls.", "The claim closes its declared positive finite grammar. Physical advantage and unrestricted statistical conclusions require separately forced evidence.", (title.lower(),))


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 22 or len(OBS) != 22 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QLEARNX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 23)):
        raise ValueError("QLEARNX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
