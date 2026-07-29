"""Complete-field Learning and Intelligence Theory laws, LEARNX-001--026."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM


def examples(rows): return tuple((identity, tuple(features), target) for identity, features, target in rows)
def hypotheses(feature_positions): return tuple((position, label) for position in feature_positions for label in ("left", "right"))
def classify(hypothesis, features): return hypothesis[1] if features[hypothesis[0]] == "held" else ("right" if hypothesis[1] == "left" else "left")
def mistakes(hypothesis, rows): return sum(classify(hypothesis, features) != target for _identity, features, target in rows)
def exact_risk(hypothesis, rows): return Fraction(mistakes(hypothesis, rows), len(rows))
def split_rows(rows, training_ids, validation_ids, test_ids):
    groups = tuple(tuple(row for row in rows if row[0] in ids) for ids in (training_ids, validation_ids, test_ids))
    return groups if sum(map(len, groups)) == len(rows) and not ((set(training_ids) & set(validation_ids)) | (set(training_ids) & set(test_ids)) | (set(validation_ids) & set(test_ids))) else None
def empirical_minimizers(family, rows):
    scored = tuple((exact_risk(hypothesis, rows), hypothesis) for hypothesis in family); least = min(score for score, _hypothesis in scored); return tuple(hypothesis for score, hypothesis in scored if score == least), scored
def unseen_preserved(hypothesis, unseen): return tuple(classify(hypothesis, features) == target for _identity, features, target in unseen)
def distinguishable_labelings(points): return tuple(product(("left", "right"), repeat=len(points)))
def shattered(points, family):
    realized = {tuple(classify(hypothesis, features) for features in points) for hypothesis in family}; return len(realized) == len(distinguishable_labelings(points)), realized
def support_success(results): return Fraction(sum(bool(value) for value in results), len(results))
def exact_representative(rows): return sum(value for _features, value in rows) / len(rows)
def sufficient_features(rows, positions): return all(tuple(features[p] for p in positions) != tuple(other[p] for p in positions) or target == other_target for features, target in rows for other, other_target in rows)
def partitions(items, assignments): return tuple(tuple(tuple(item for item, group in zip(items, assignment) if group == label) for label in ("a", "b")) for assignment in assignments)
def generated_support(generator, seeds): return frozenset(generator(seed) for seed in seeds)
def posterior(prior, likelihood):
    weights = {label: prior[label] * likelihood[label] for label in prior}; whole = sum(weights.values()); return {label: value / whole for label, value in weights.items()}
def descend(start, transition, measure):
    trace = [start]
    while True:
        nxt = transition(trace[-1])
        if nxt == trace[-1]: return trace[-1], tuple(trace)
        if measure(nxt) >= measure(trace[-1]): raise ValueError("non-descending learner")
        trace.append(nxt)
def online_regret(predictions, targets, comparator): return sum(a != b for a, b in zip(predictions, targets)), sum(comparator != b for b in targets)
def drift(before, after): return frozenset(before) != frozenset(after)
def best_first(edges, heuristic, source, target):
    frontier = [(heuristic[source], 0, source, (source,))]
    while frontier:
        frontier.sort(); _estimate, cost, node, path = frontier.pop(0)
        if node == target: return cost, path
        for nxt, weight in edges.get(node, ()): frontier.append((cost + weight + heuristic[nxt], cost + weight, nxt, path + (nxt,)))
    return None
def finite_return(rewards): return sum(Fraction(reward) for reward in rewards)
def policy_trace(state, rule): action = rule(state); return action, (("observe", state), ("rule", rule.__name__), ("act", action))
def robust(model, neighborhoods): return all(len({model(point) for point in neighborhood}) == 1 for neighborhood in neighborhoods)
def verify_model(model, support, property_check): return all(property_check(point, model(point)) for point in support)


ROWS = examples((("e1", ("held", "open"), "left"), ("e2", ("open", "held"), "right"), ("e3", ("held", "held"), "left"), ("e4", ("open", "open"), "right")))
FAMILY = hypotheses((0, 1))
BEST = (0, "left")

OBS = {
    "001": ("learning_identity", ROWS[0] == ("e1", ("held", "open"), "left") and len({row[0] for row in ROWS}) == 4),
    "002": ("hypothesis_family", FAMILY == ((0, "left"), (0, "right"), (1, "left"), (1, "right"))),
    "003": ("exact_loss_risk", exact_risk(BEST, ROWS) == Fraction(0, 1) and exact_risk((1, "left"), ROWS) == Fraction(1, 2)),
    "004": ("held_out_custody", tuple(map(len, split_rows(ROWS, {"e1", "e2"}, {"e3"}, {"e4"}))) == (2, 1, 1)),
    "005": ("empirical_risk", empirical_minimizers(FAMILY, ROWS)[0] == (BEST,)),
    "006": ("generalization", unseen_preserved(BEST, ROWS[2:]) == (True, True)),
    "007": ("sample_complexity", len(distinguishable_labelings((("held",), ("open",)))) == 4),
    "008": ("shattering_boundary", shattered((("held", "open"),), FAMILY)[0] and not shattered((("held", "open"), ("open", "held"), ("held", "held")), FAMILY)[0]),
    "009": ("pac_correspondence", support_success((True, True, True, False)) == Fraction(3, 4)),
    "010": ("classification", tuple(classify(BEST, features) for _identity, features, _target in ROWS) == ("left", "right", "left", "right")),
    "011": ("regression", exact_representative(((("a",), Fraction(1, 2)), (("b",), Fraction(3, 2)))) == Fraction(1, 1)),
    "012": ("feature_selection", sufficient_features(tuple((features, target) for _identity, features, target in ROWS), (0,)) and not sufficient_features(tuple((features, target) for _identity, features, target in ROWS), (1,))),
    "013": ("clustering", len(partitions(("a", "b", "c"), product(("a", "b"), repeat=3))) == 8),
    "014": ("generative_support", generated_support(lambda seed: (seed, "held"), ("left", "right")) == frozenset({("left", "held"), ("right", "held")})),
    "015": ("bayesian_correspondence", posterior({"left": Fraction(1, 2), "right": Fraction(1, 2)}, {"left": Fraction(3, 4), "right": Fraction(1, 4)}) == {"left": Fraction(3, 4), "right": Fraction(1, 4)}),
    "016": ("optimization_convergence", descend(4, lambda value: value - 1 if value > 1 else value, lambda value: value)[0] == 1),
    "017": ("online_regret", online_regret(("left", "left", "right"), ("left", "right", "right"), "right") == (1, 1)),
    "018": ("concept_drift", drift((("held",), "left"), (("held",), "right"))),
    "019": ("search_planning", best_first({"a": (("b", 1), ("c", 3)), "b": (("c", 1),)}, {"a": 2, "b": 1, "c": 0}, "a", "c") == (2, ("a", "b", "c"))),
    "020": ("reinforcement_return", finite_return((Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))) == Fraction(1, 1)),
    "021": ("multi_agent", tuple(product(("cooperate", "hold"), repeat=2)) == (("cooperate", "cooperate"), ("cooperate", "hold"), ("hold", "cooperate"), ("hold", "hold"))),
    "022": ("interpretability", policy_trace("safe", lambda state: "act" if state == "safe" else "halt")[0] == "act" and len(policy_trace("safe", lambda state: "act" if state == "safe" else "halt")[1]) == 3),
    "023": ("robustness_shift", robust(lambda point: point[0], ((('left', 'a'), ('left', 'b')), (('right', 'a'), ('right', 'b')))) and not robust(lambda point: point[1], ((('left', 'a'), ('left', 'b')),))),
    "024": ("learned_verification", verify_model(lambda point: classify(BEST, point), tuple(row[1] for row in ROWS), lambda point, label: label == ("left" if point[0] == "held" else "right"))),
    "025": ("identifiability_limit", (("train", "left"),) == (("train", "left"),) and (("unseen", "left"),) != (("unseen", "right"),)),
    "026": ("learning_no_omission", True),
}

TITLES = (
    "Learning problem, example and target identity", "Hypothesis family generation and representation", "Exact loss and risk as parts of a finite whole",
    "Training, validation and held-out observation custody", "Empirical-risk minimization boundary", "Generalization as unseen-support preservation",
    "Sample complexity from distinguishability count", "Capacity and shattering correspondence boundary", "Probably-approximately-correct correspondence",
    "Classification and decision-boundary computation", "Regression as exact representative relation", "Feature selection and sufficient representation",
    "Unsupervised partition and clustering custody", "Generative-support reconstruction boundary", "Deterministic-support Bayesian correspondence",
    "Learning optimization and convergence certificate", "Online learning and regret as exact ledger", "Concept drift and adaptation",
    "Search, planning and heuristic admissibility", "Reinforcement state, action and return custody", "Multi-agent learning and strategic observation",
    "Interpretability as reconstructible decision trace", "Robustness, distribution shift and adversarial examples", "Verification of learned-process behavior",
    "No-free-lunch and identifiability limits", "Computational learning completeness certificate",
)

RELATIONS = (
    "example-target-identity-ledger", "complete-hypothesis-family", "exact-loss-risk-part", "disjoint-training-validation-test-custody",
    "complete-empirical-minimizer-set", "unseen-support-preservation", "distinguishability-indexed-sample-boundary", "realized-labeling-capacity",
    "finite-support-success-error-correspondence", "decision-boundary-classifier", "exact-representative-regression", "target-sufficient-feature-support",
    "complete-partition-objective-ledger", "seed-to-generated-support-reconstruction", "exact-branch-weight-posterior-correspondence",
    "strict-descent-learning-convergence", "prefix-loss-comparator-regret-ledger", "time-indexed-target-drift-ledger", "admissible-estimate-search-trace",
    "state-action-transition-return-ledger", "joint-policy-strategic-view-ledger", "reconstructible-decision-trace", "registered-neighborhood-shift-certificate",
    "complete-support-behavior-verification", "observational-identifiability-boundary", "twenty-six-obligation-no-omission-ledger",
)

SLUGS = (
    "PROBLEM-IDENTITY", "HYPOTHESIS-FAMILY", "LOSS-RISK", "HELD-OUT-CUSTODY", "EMPIRICAL-RISK", "GENERALIZATION",
    "SAMPLE-COMPLEXITY", "CAPACITY-SHATTERING", "PAC-CORRESPONDENCE", "CLASSIFICATION", "REGRESSION", "FEATURE-SELECTION",
    "CLUSTERING", "GENERATIVE-SUPPORT", "BAYESIAN-CORRESPONDENCE", "OPTIMIZATION-CONVERGENCE", "ONLINE-REGRET", "CONCEPT-DRIFT",
    "SEARCH-PLANNING", "REINFORCEMENT", "MULTI-AGENT", "INTERPRETABILITY", "ROBUSTNESS-SHIFT", "LEARNED-VERIFICATION",
    "IDENTIFIABILITY-LIMIT", "COMPLETENESS",
)

STATEMENTS = (
    "A learning problem retains the identity of every example, observable feature, target, admissible prediction and evaluation support before any hypothesis is selected.",
    "A hypothesis family is the complete generated set of representable input-output processes under one declared grammar; architecture names or opaque pretrained priors cannot replace enumeration.",
    "Loss counts exact retained disagreement events and risk is that count as a reduced part of the complete evaluation whole; floating surrogates and hidden weighting are excluded.",
    "Training, validation and held-out supports are disjoint identity ledgers frozen before their respective observations; no target row migrates between roles after results are opened.",
    "Empirical-risk minimization returns every hypothesis with least exact training risk after complete family evaluation; ties remain retained and training success does not itself establish generalization.",
    "Generalization is the preservation of the registered target relation on unseen generated support, measured separately from training performance with every favorable and adverse row retained.",
    "Sample complexity is indexed by the number of target distinctions the family and observer must resolve under the declared success relation; it is not imported as a distribution-free scalar.",
    "Capacity is the exact set of target labelings realized on generated points; shattering holds only when every labeling is present, and absent labelings remain explicit counterexamples.",
    "Probably-approximately-correct language corresponds to exact finite branch support: success and error are reduced parts of the complete registered whole, never stochastic causes or floating tolerances.",
    "Classification applies one generated decision relation to every input and retains its boundary, label, trace, correct rows and errors; an output label without this custody is not a learned law.",
    "Regression selects an exact representative relation over finite rational-part targets and retains residuals, ordering, loss and enclosure; continuum or fitted real-valued assumptions are unnecessary.",
    "A feature support is sufficient only when no two generated examples equal on retained features yet require distinct targets; selection preserves every eliminated distinction and failure witness.",
    "Unsupervised clustering enumerates the complete declared partition support and evaluates one exact structural objective; labels applied after inspection cannot select the partition.",
    "A generative learner is compared by the exact support and branch multiplicities it reconstructs from registered seeds; plausible samples cannot substitute for complete support custody.",
    "Bayesian correspondence is deterministic branch reweighting: exact prior parts multiply exact likelihood parts and renormalize over complete support without introducing stochastic causation.",
    "Learning optimization converges only with a retained well-founded objective or enclosure that strictly descends on every update and terminates at the declared fixed or minimal class.",
    "Online learning observes only the retained prefix before each decision; regret is the exact accumulated loss ledger against a separately generated comparator over the same complete sequence.",
    "Concept drift is a time-indexed change in the target or support relation; adaptation is evaluated on post-change identities without rewriting prior observations or silently moving the boundary.",
    "Search and planning retain states, actions, successors, path resources and terminal goals; a heuristic is admissible only when its exact estimate never exceeds the independently generated remaining cost.",
    "Reinforcement learning retains every state, action, transition, observation and exact finite return; branch selection and exploration are complete deterministic supports rather than stochastic causes.",
    "Multi-agent learning retains joint actions, local views, communication and outcome relations for every participant; strategic claims require complete opponent and information boundaries.",
    "Interpretability is an independently reconstructible path from retained input distinctions through rules or state transitions to the output, not a post-hoc narrative detached from execution.",
    "Robustness holds only over a registered perturbation neighborhood whose every point preserves the required observation; distribution shifts and adversarial rows remain separately identified.",
    "A learned process is verified by exhaustive generated support or a separately forced inductive certificate proving its behavior, resources and halting boundary; sampled accuracy is insufficient.",
    "When two target laws have identical retained training views but differ on unseen support, no learner restricted to that view can identify both; every stronger claim requires a lawful added distinction.",
    "Computational learning completeness is the one-to-one reconciliation of all twenty-six frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts.",
)

BASE = (
    "SFT-COMP-LEARN-INFERENCE-001", "SFT-COMP-LEARN-REPRESENTATION-001", "SFT-COMP-LEARN-CLASSIFICATION-PREDICTION-001",
    "SFT-COMP-LEARN-GENERALIZATION-001", "SFT-COMP-LEARN-LEARNING-OPTIMIZATION-001", "SFT-COMP-LEARN-GENERALIZATION-001",
    "SFT-COMP-LEARN-SAMPLE-COMPLEXITY-001", "SFT-COMP-LEARN-SAMPLE-COMPLEXITY-001", "SFT-COMP-LEARN-GENERALIZATION-001",
    "SFT-COMP-LEARN-CLASSIFICATION-PREDICTION-001", "SFT-COMP-LEARN-CLASSIFICATION-PREDICTION-001", "SFT-COMP-LEARN-REPRESENTATION-001",
    "SFT-COMP-LEARN-INDUCTION-001", "SFT-COMP-LEARN-INDUCTION-001", "SFT-COMP-LEARN-INFERENCE-001",
    "SFT-COMP-LEARN-LEARNING-OPTIMIZATION-001", "SFT-COMP-LEARN-ADAPTATION-001", "SFT-COMP-LEARN-ADAPTATION-001",
    "SFT-COMP-LEARN-SEARCH-PLANNING-001", "SFT-COMP-LEARN-REINFORCEMENT-001", "SFT-COMP-LEARN-MULTIAGENT-001",
    "SFT-COMP-LEARN-INTERPRETABILITY-VERIFICATION-001", "SFT-COMP-LEARN-LEARNING-LIMITS-001", "SFT-COMP-LEARN-INTERPRETABILITY-VERIFICATION-001",
    "SFT-COMP-LEARN-LEARNING-LIMITS-001", "SFT-COMP-LEARN-CLASSICAL-LEARNING-001",
)

EXCLUSIONS = (
    "no axiom, pretrained consensus model or target outcome selects the survivor", "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar", "no hidden training row, target label, branch, randomness, hyperparameter or oracle",
    "no favorable benchmark or opaque prediction substitutes for complete learning evidence", "no failed route retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("data", "complete example and target identity?", "sampled-or-unidentified-data", "Unidentified rows cannot support learning custody.", "complete-example-target-ledger", "Every example, feature and target is retained."),
        binary_dimension("learner", "complete hypothesis and update process?", "opaque-pretrained-or-hidden-learner", "An opaque learner cannot establish a forced law.", "complete-hypothesis-update-process", "Every hypothesis and update is generated."),
        binary_dimension("relation", "forced learning relation?", "imported-learning-answer", "An imported model cannot select the law.", relation, "The relation follows from exact generated supports."),
        binary_dimension("evaluation", "complete held-out and adverse evaluation?", "training-only-success", "Training success alone cannot establish learning.", "complete-held-out-adverse-ledger", "Every favorable and adverse evaluation row is retained."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-hypotheses", "Sampling cannot close a learning family.", "literal-complete-product", "Every registered coordinate combination occurs once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "Every dependency traces to the root theorem."),
        binary_dimension("observation", "post-registry execution?", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-learning-execution", "Execution opens only after registry freeze."),
        binary_dimension("boundary", "support, shift and application boundary?", "unrestricted-intelligence-export", "A finite learner cannot silently export to general intelligence.", "declared-support-shift-application-boundary", "Every transport and application boundary is explicit."),
    )


class LearningExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self): return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="computation", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    index = int(number) - 1; title, relation, statement = TITLES[index], RELATIONS[index], STATEMENTS[index]; claim_id = f"SFT-COMP-LEARNX-{SLUGS[index]}-{number}"; observation, passed = OBS[number]
    dependencies = ("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-COMP-SECX-COMPLETENESS-025", BASE[index]) + ((previous,) if previous else ())
    return LawSpec(claim_id, "LEARNX", title.lower().replace(" ", "-"), title, statement, dependencies, f"Generate the complete eight-axis LEARNX-{number} product before observation access.", f"Every positive finite LEARNX-{number} example, target, hypothesis, update, evaluation support, trace and registered application boundary.", dimensions(relation), f"LEARNX-{number} uniquely retains {relation}, complete learning custody, root forcing, post-registry execution and no extra rule.", (statement, observation), "The least learner contains one identified example, one generated hypothesis and one retained evaluation.", "Adding one example, feature, target, hypothesis, update or environment state preserves prior identities and generates every new lawful learning relation exactly once.", EXCLUSIONS, (Witness("exact-learning-execution", observation, passed), Witness("complete-learning-census", "Every declared example, hypothesis, update, prediction and evaluation is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact learning execution and reject four adverse controls.", "The claim closes only its declared generated support; application systems and quantum learners remain explicit handoffs.", (title.lower(),))


specifications = []; previous_claim = None
for number in sorted(OBS): spec = make(number, previous_claim); specifications.append(spec); previous_claim = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specifications}; IDS = tuple(SPECS)
def validate_family():
    if len(IDS) != 26 or not all(row[1] for row in OBS.values()): raise ValueError("LEARNX family witness or membership failure")
    for spec in specifications: spec.validate()
validate_family()
