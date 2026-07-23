"""Force noise and error as exact source-to-received transformation relations."""

from __future__ import annotations

from dataclasses import dataclass

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-NOISE-ERROR-001"
Word = tuple[str, ...]


@dataclass(frozen=True)
class ErrorRelation:
    sources: tuple[Word, ...]
    received: tuple[Word, ...]
    relation: tuple[tuple[Word, Word, str], ...]

    def __post_init__(self) -> None:
        if not self.sources or not self.received or len(set(self.sources)) != len(self.sources) or len(set(self.received)) != len(self.received):
            raise ValueError("error relation requires complete canonical carriers")
        if len(set(self.relation)) != len(self.relation):
            raise ValueError("error transformation cells cannot repeat")
        if any(source not in self.sources or image not in self.received or not action for source, image, action in self.relation):
            raise ValueError("every error cell retains source, received form and action identity")
        if any(not any(source == item for source, _, _ in self.relation) for item in self.sources):
            raise ValueError("every source requires at least one registered received image")


def error_images(relation: ErrorRelation, source: Word) -> tuple[Word, ...]:
    if source not in relation.sources:
        raise ValueError("source is outside the registered error relation")
    return tuple(dict.fromkeys(image for held, image, _ in relation.relation if held == source))


def predecessors(relation: ErrorRelation, received: Word) -> tuple[Word, ...]:
    if received not in relation.received:
        raise ValueError("received form is outside registered support")
    return tuple(dict.fromkeys(source for source, image, _ in relation.relation if image == received))


def error_trace(source: Word, received: Word):
    if len(source) != len(received):
        raise ValueError("word comparison requires the same generated position carrier")
    changed = tuple(
        (f"position-{position + 1}", left, right)
        for position, (left, right) in enumerate(zip(source, received))
        if left != right
    )
    return changed if changed else ("empty-One",)


def detectable(valid_codewords: tuple[Word, ...], source: Word, received: Word) -> bool:
    trace = error_trace(source, received)
    if trace == ("empty-One",):
        return True
    return received not in valid_codewords


def uniquely_correctable(relation: ErrorRelation, received: Word) -> bool:
    return len(predecessors(relation, received)) == 1


def correction_record(relation: ErrorRelation, received: Word):
    held = predecessors(relation, received)
    return ("unique-source", held[0]) if len(held) == 1 else ("closed-source-class", held)


_a = ("a", "a", "a")
_b = ("b", "b", "b")
_received = (_a, _b, ("b", "a", "a"), ("a", "b", "b"), ("a", "a", "b"))
_relation = ErrorRelation(
    (_a, _b),
    _received,
    (
        (_a, _a, "identity"),
        (_b, _b, "identity"),
        (_a, ("b", "a", "a"), "first-label-change"),
        (_b, ("a", "b", "b"), "first-label-change"),
        (_a, ("a", "a", "b"), "third-label-change"),
    ),
)
_ambiguous = ErrorRelation(
    (_a, _b),
    (("b", "a", "b"),),
    ((_a, ("b", "a", "b"), "two-position-action"), (_b, ("b", "a", "b"), "one-position-action")),
)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact noise, error, detection and correction boundaries",
    statement=(
        "Noise is a registered source-to-received transformation relation over complete canonical word carriers; "
        "error is the exact changed-position trace between a held source and received form. Detection is forced when "
        "a nonidentity image lies outside valid code support. Correction is forced only when the received form has one "
        "registered source predecessor; multiple predecessors remain an explicit closed source class. No random cause, "
        "error probability, distance threshold or unrecorded predecessor inference is admitted."
    ),
    dependencies=(
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-INFO-CHANNEL-CAPACITY-001",
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    ),
    generation_rule=(
        "Generate the complete product of source support, received support, transformation provenance, error trace, "
        "detection, predecessor classes, correction, deterministic status, generality and extra-noise status."
    ),
    grammar_boundary=(
        "All finite error systems generated from canonical source and received words, held transformation actions, "
        "exact changed-position traces, valid code support and complete predecessor classes."
    ),
    dimensions=(
        binary_dimension("source", "What fixes clean inputs?", "partial-source-support", "An omitted source hides a possible predecessor.", "complete-canonical-sources", "Every registered clean word occurs once."),
        binary_dimension("received", "What fixes possible received forms?", "sampled-received-forms", "Sampling cannot establish the transformation boundary complete.", "complete-registered-images", "Every generated image under registered actions is retained."),
        binary_dimension("action", "What fixes noise transport?", "opaque-perturbation", "An opaque change hides which source produced which image.", "held-action-relation", "Each cell retains source, image and action identity."),
        binary_dimension("error", "What fixes an error?", "scalar-error-size", "A scalar count erases changed positions and labels.", "complete-changed-position-trace", "Every differing position retains old and new labels; identity is empty One."),
        binary_dimension("detection", "What forces error detection?", "probability-threshold", "A threshold imports a distribution and free parameter.", "invalid-codeword-witness", "A changed received form outside valid code support is detected structurally."),
        binary_dimension("predecessors", "What uncertainty remains after receipt?", "chosen-likely-source", "Choosing one predecessor imports a prior.", "complete-source-class", "Every registered source mapping to the received form is retained."),
        binary_dimension("correction", "When is correction exact?", "nearest-form-assumption", "Nearest requires an unforced metric and can tie.", "singleton-predecessor", "Correction occurs exactly when one registered source remains."),
        binary_dimension("cause", "Does noise require randomness?", "stochastic-noise-source", "A random cause is neither generated nor needed.", "deterministic-transformation-family", "Noise names the complete registered action relation over deterministic forms."),
        binary_dimension("generality", "What closes arbitrary finite error families?", "sampled-masks", "Examples do not establish a fresh action image.", "action-successor", "A fresh registered action adds its exact source/image cells and updates predecessor classes."),
        binary_dimension("addition", "Is another error model added?", "extra-error-rate-or-metric", "A rate, distribution or metric is not supplied by exact transformations.", "no-extra-error-model", "Detection and correction use only code support and predecessor identity."),
    ),
    exact_result=(
        "The noise/error kernel is complete source and received support, held action provenance, exact position traces, "
        "invalid-code detection, complete predecessor classes, singleton correction and no stochastic or metric rule."
    ),
    laws=(
        "identity transport has structural empty-One error trace",
        "nonidentity error retains every changed position and both labels",
        "detection requires a received form outside the valid codebook",
        "exact correction is equivalent to a singleton registered predecessor class",
        "ambiguous received forms preserve all source predecessors rather than choosing a likely one",
    ),
    induction_base="One source under its identity action yields itself, empty-One error and a singleton predecessor class.",
    induction_step=(
        "Adding one registered action adds one exact image cell for each source on which it acts. Error traces compare "
        "those forms positionwise, and each affected received predecessor class extends by precisely the new source cell."
    ),
    boundary_exclusions=(
        "no stochastic noise cause",
        "no floating error rate or threshold",
        "no assumed metric or nearest-neighbor rule",
        "no unrecorded source inference",
    ),
    witnesses=(
        Witness("identity-error", "Identity transport returns structural empty-One error.", error_trace(_a, _a) == ("empty-One",)),
        Witness("position-trace", "The first-label change retains its exact position and labels.", error_trace(_a, ("b", "a", "a")) == (("position-1", "a", "b"),)),
        Witness("detection", "A one-label image outside the repetition codebook is structurally detectable.", detectable((_a, _b), _a, ("b", "a", "a"))),
        Witness("unique-correction", "The registered b/a/a image has exactly source a.", uniquely_correctable(_relation, ("b", "a", "a")) and correction_record(_relation, ("b", "a", "a")) == ("unique-source", _a)),
        Witness("ambiguous-control", "The shared b/a/b image retains both predecessors and refuses unique correction.", not uniquely_correctable(_ambiguous, ("b", "a", "b")) and correction_record(_ambiguous, ("b", "a", "b"))[0] == "closed-source-class"),
    ),
    why=(
        "Coding cannot be derived until the model states exactly what noise changes, what detection observes and why "
        "a correction is unique. Probabilities and metrics are not necessary for these structural boundaries."
    ),
    derivation=(
        "Channels supply source/output relations; dynamics supplies transitions and predecessor loss; entropy supplies "
        "closed classes; graphs supply paths. Ten structural axes force exact action provenance, error traces and "
        "singleton-predecessor correction."
    ),
    check=(
        "Execute all 1,024 noise kernels, verify identity and changed-position traces, detection, unique correction and "
        "an ambiguous predecessor control, run all adverse controls and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes finite structural noise and error. It does not assign a stochastic error frequency, "
        "physical noise mechanism or asymptotic reliability rate."
    ),
    correspondence_terms=("noise", "error pattern", "error detection", "syndrome", "decoding ambiguity"),
)
