"""Dependency-ordered catalog of all 113 classical-computation obligations."""

from __future__ import annotations

from sft.computation.generated_law import LawSpec, Witness, binary_dimension
from sft.computation.operations import group_witnesses
from sft.computation.spec_data import GROUP_CODES, GROUP_TITLES, GROUP_TOPICS, Topic


FOUNDATION_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
)


DIMENSION_TEMPLATES = {
    "formal_computation": (
        ("carrier", "sampled-carrier", "complete-generated-carrier"),
        ("identity", "presentation-identity", "canonical-held-identity"),
        ("relation", "assumed-operation", "source-bound-exact-relation"),
        ("trace", "result-only", "complete-retained-trace"),
        ("boundary", "implicit-terminal-boundary", "explicit-initial-terminal-boundary"),
        ("composition", "opaque-assembly", "interface-preserving-composition"),
        ("generality", "fixed-examples", "structural-successor"),
        ("addition", "imported-machine-model", "no-extra-computational-premise"),
    ),
    "computability": (
        ("domain", "sampled-descriptions", "complete-generated-description-domain"),
        ("execution", "verdict-without-run", "exact-recognition-execution-trace"),
        ("result", "implicit-nontermination", "accept-reject-continue-classes"),
        ("self_reference", "self-reference-excluded", "generated-self-description-support"),
        ("totality", "assumed-total-decider", "explicit-totality-or-partiality-boundary"),
        ("translation", "answer-changing-map", "answer-preserving-reduction"),
        ("generality", "fixed-depth-table", "description-successor-certificate"),
        ("addition", "hidden-oracle", "no-undeclared-computational-power"),
    ),
    "complexity": (
        ("input", "presentation-length", "canonical-encoding-support"),
        ("resource", "unrecorded-cost", "complete-resource-ledger"),
        ("model", "model-unspecified", "registered-computation-model"),
        ("comparison", "unmatched-instances", "common-family-comparison"),
        ("composition", "cost-erasing-composition", "overhead-retaining-composition"),
        ("witness", "claimed-bound", "constructive-or-adversarial-bound-witness"),
        ("generality", "benchmark-only", "family-successor-certificate"),
        ("addition", "imported-scale-or-rate", "no-extra-resource-parameter"),
    ),
    "algorithms": (
        ("domain", "sampled-inputs", "complete-generated-input-domain"),
        ("precondition", "implicit-precondition", "exact-registered-precondition"),
        ("transition", "answer-producing-heuristic", "exact-step-relation"),
        ("invariant", "unchecked-intermediate-state", "retained-invariant-ledger"),
        ("output", "result-without-certificate", "reconstructible-output-certificate"),
        ("resource", "unreported-resources", "complete-time-space-trace"),
        ("generality", "example-program", "input-successor-certificate"),
        ("addition", "imported-algorithm", "no-extra-answer-model"),
    ),
    "semantics": (
        ("syntax", "partial-or-ambiguous-syntax", "complete-generated-syntax"),
        ("binding", "presentation-name", "canonical-held-binding"),
        ("relation", "informal-meaning", "exact-semantic-relation"),
        ("evaluation", "result-only", "complete-evaluation-trace"),
        ("equivalence", "visual-equivalence", "observation-bound-equivalence"),
        ("proof", "test-only", "machine-checkable-proof-object"),
        ("generality", "sample-programs", "syntax-successor-certificate"),
        ("addition", "imported-language-semantics", "no-extra-semantic-premise"),
    ),
    "distributed_computation": (
        ("processes", "anonymous-or-partial-processes", "complete-held-process-identities"),
        ("events", "unrecorded-events", "complete-local-event-ledgers"),
        ("causality", "assumed-global-order", "exact-partial-causal-order"),
        ("communication", "implicit-shared-state", "source-bound-message-records"),
        ("faults", "unspecified-faults", "declared-fault-support"),
        ("knowledge", "omniscient-process", "observation-relative-local-knowledge"),
        ("generality", "one-schedule", "schedule-successor-certificate"),
        ("addition", "hidden-coordinator-or-clock", "no-extra-global-oracle"),
    ),
    "cryptography_security": (
        ("support", "sampled-messages-or-keys", "complete-generated-challenge-support"),
        ("adversary", "undefined-adversary", "exact-adversary-process-grammar"),
        ("interaction", "outcome-only", "complete-interaction-trace"),
        ("observation", "implicit-leakage", "exact-adversary-observation"),
        ("security", "informal-security", "retained-closed-distinction-property"),
        ("resources", "unbounded-claim", "declared-information-or-resource-bound"),
        ("generality", "challenge-examples", "support-successor-certificate"),
        ("addition", "imported-hardness-assumption", "no-extra-security-premise"),
    ),
    "learning_intelligence": (
        ("support", "sampled-hypotheses", "complete-generated-hypothesis-support"),
        ("representation", "opaque-representation", "traceable-canonical-representation"),
        ("inference", "pretrained-answer", "exact-evidence-to-hypothesis-relation"),
        ("evaluation", "development-score", "sealed-independent-evaluation"),
        ("uncertainty", "single-winner-erasure", "retained-alternative-ledger"),
        ("resources", "unreported-search", "complete-learning-resource-trace"),
        ("generality", "training-examples-only", "structural-or-empirical-target-boundary"),
        ("addition", "fitted-weight-or-prior", "no-extra-learning-parameter"),
    ),
    "scientific_computation": (
        ("model", "unstated-model", "registered-exact-model-relation"),
        ("inputs", "sampled-or-fitted-inputs", "complete-declared-input-support"),
        ("operation", "opaque-calculation", "exact-executable-operation-trace"),
        ("error", "unsigned-error-scalar", "orientation-labelled-error-ledger"),
        ("closure", "visual-convergence", "base-successor-closure-certificate"),
        ("validation", "fit-only", "sealed-falsifiable-comparison-boundary"),
        ("generality", "single-resolution", "generated-refinement-successor"),
        ("addition", "imported-equation-or-parameter", "no-extra-scientific-prior"),
    ),
}


def claim_id(group: str, topic: Topic) -> str:
    return f"SFT-COMP-{GROUP_CODES[group]}-{topic.slug}-001"


def dimensions_for(group: str):
    return tuple(
        binary_dimension(
            key,
            f"Which {key} coordinate preserves the complete {GROUP_TITLES[group]} obligation?",
            rejected,
            f"{rejected} removes a required exact {key} condition.",
            admitted,
            f"{admitted} retains the complete registered {key} condition.",
        )
        for key, rejected, admitted in DIMENSION_TEMPLATES[group]
    )


def build_specs() -> tuple[LawSpec, ...]:
    specs: list[LawSpec] = []
    previous: str | None = None
    for group, topics in GROUP_TOPICS.items():
        for topic in topics:
            current = claim_id(group, topic)
            dependencies = FOUNDATION_DEPENDENCIES if previous is None else (previous, *FOUNDATION_DEPENDENCIES)
            witness_rows = group_witnesses(group, current)
            result = (
                f"The forced {topic.subject} kernel retains {topic.components}; every operation is source-bound, "
                "trace-complete, boundary-explicit, composition-preserving, successor-general and contains no imported answer-producing premise."
            )
            specs.append(
                LawSpec(
                    claim_id=current,
                    group=group,
                    slug=topic.slug,
                    title=topic.title,
                    statement=result,
                    dependencies=dependencies,
                    generation_rule=f"Generate the literal product of the eight registered {GROUP_TITLES[group]} structural axes for {topic.subject}.",
                    grammar_boundary=f"All generated finite {topic.subject} structures whose carriers, relations, traces and interfaces are composed from admitted Foundation, Mathematics and Information Science forms. {topic.limitations}",
                    dimensions=dimensions_for(group),
                    exact_result=result,
                    laws=(
                        f"Carrier law: {topic.components}.",
                        "Trace law: every accepted result reconstructs from the exact initial form and retained transition or relation rows.",
                        "Boundary law: unregistered forms, powers, parameters, models and omitted rows halt the computation claim.",
                        "Composition law: serial or parallel assembly preserves interfaces, component identities and lost/retained distinction ledgers.",
                    ),
                    induction_base=f"The structural One supplies one canonical {topic.subject} form with its identity trace and no unrecorded predecessor.",
                    induction_step=f"Appending one generated {topic.subject} form adds its exact carrier row, relations, trace positions and new pair/interface distinctions while preserving every earlier record.",
                    boundary_exclusions=(
                        "no conventional machine, algorithm, language, security definition or learning model may select the law",
                        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
                        "no completed infinity or ungenerated continuum",
                        "no free, fitted or learned parameter",
                        "no application result or pretrained model",
                        topic.limitations,
                    ),
                    witnesses=tuple(Witness(*row) for row in witness_rows),
                    why=f"{topic.title} is required to derive {topic.subject} without importing its conventional answer-producing model.",
                    derivation=f"Admitted finite forms, exact relations, distinction ledgers and composition supply the carriers. Exhausting the eight group-specific axes forces the only structure retaining: {topic.components}.",
                    check=f"Execute all 256 product members, decide every member, verify the sole survivor, replay the group operational witnesses, run four adverse controls and independently regenerate the literal product.",
                    limitations=topic.limitations,
                    correspondence_terms=topic.correspondence,
                )
            )
            previous = current
    return tuple(specs)


SPECS = build_specs()
SPEC_BY_ID = {spec.claim_id: spec for spec in SPECS}


def validate_catalog() -> None:
    if len(SPECS) != 113:
        raise ValueError("the classical-computation catalog must contain exactly 113 obligations")
    if len(SPEC_BY_ID) != len(SPECS):
        raise ValueError("the classical-computation catalog contains duplicate claim identities")
    available = set(FOUNDATION_DEPENDENCIES)
    for spec in SPECS:
        spec.validate()
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()

