"""Force uncertainty and entropy as exact observation-class ledgers."""

from __future__ import annotations

from fractions import Fraction

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-ENTROPY-UNCERTAINTY-001"
EMPTY_ONE = ("empty-One",)


def exact_partition(support: tuple[str, ...], observation: tuple[tuple[str, str], ...]):
    images = dict(observation)
    if not support or len(set(support)) != len(support) or len(images) != len(observation) or set(images) != set(support):
        raise ValueError("uncertainty requires complete support and total observation")
    labels = tuple(dict.fromkeys(images[state] for state in support))
    return tuple((label, tuple(state for state in support if images[state] == label)) for label in labels)


def unresolved_pairs(members: tuple[str, ...]):
    pairs = tuple(
        (left, right)
        for left_position, left in enumerate(members)
        for right in members[left_position + 1 :]
    )
    return pairs if pairs else EMPTY_ONE


def entropy_ledger(support: tuple[str, ...], observation: tuple[tuple[str, str], ...]):
    return tuple(
        {
            "observation": label,
            "exact_support_part": Fraction(len(members), len(support)),
            "microstates": members,
            "unresolved_distinctions": unresolved_pairs(members),
        }
        for label, members in exact_partition(support, observation)
    )


def closed_pairs(support: tuple[str, ...], observation: tuple[tuple[str, str], ...]):
    partition = exact_partition(support, observation)
    return tuple(
        pair
        for _, members in partition
        for pair in (() if unresolved_pairs(members) == EMPTY_ONE else unresolved_pairs(members))
    )


def refines(
    support: tuple[str, ...], fine: tuple[tuple[str, str], ...], coarse: tuple[tuple[str, str], ...]
) -> bool:
    fine_images = dict(fine)
    coarse_images = dict(coarse)
    if set(fine_images) != set(support) or set(coarse_images) != set(support):
        return False
    return all(
        coarse_images[left] == coarse_images[right]
        for left in support for right in support
        if fine_images[left] == fine_images[right]
    )


_support = ("aa", "ab", "ba", "bb")
_fine = tuple((state, state) for state in _support)
_prefix = (("aa", "a"), ("ab", "a"), ("ba", "b"), ("bb", "b"))
_coarse = tuple((state, "unresolved") for state in _support)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact entropy and uncertainty from deterministic observation classes",
    statement=(
        "Uncertainty is the complete ledger of deterministic microstate distinctions closed inside each exact "
        "observation class. Entropy is the provenance-retaining family of those classes, their exact positive "
        "support parts, microstate traces and unresolved-pair ledgers; singleton certainty uses structural empty One. "
        "Refining observation can only remove closed pairs, while coarsening can only add them. No stochastic cause, "
        "logarithm, numerical zero or floating expectation enters the law."
    ),
    dependencies=(
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-INFO-SYMBOL-DISTINCTION-001",
        "SFT-INFO-QUANTITY-001",
    ),
    generation_rule=(
        "Generate the complete product of microstate support, observation partition, class weights, unresolved pairs, "
        "entropy representation, refinement order, deterministic status, generality and extra-entropy status."
    ),
    grammar_boundary=(
        "All finite uncertainty structures generated from complete deterministic microstate support, total observation "
        "partitions, exact class parts, complete within-class pair ledgers and refinement relations."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible microstates?", "partial-microstate-support", "Omission changes observation classes and uncertainty.", "complete-deterministic-support", "Every registered microstate occurs once."),
        binary_dimension("partition", "What fixes observation uncertainty?", "overlapping-or-partial-classes", "Overlap or omission does not partition exact support.", "total-disjoint-observation-classes", "Every microstate belongs to exactly one observed class."),
        binary_dimension("weights", "What fixes class weight?", "floating-probability", "A floating propensity imports precision and stochastic cause.", "exact-class-whole-part", "The class count is retained relative to complete support count."),
        binary_dimension("unresolved", "What fixes uncertainty inside a class?", "scalar-uncertainty-score", "A scalar score erases which distinctions are unavailable.", "complete-within-class-pairs", "Every pair of distinct class microstates is retained once."),
        binary_dimension("entropy", "What represents total entropy?", "logarithmic-expectation", "Logarithms and real expectations import forbidden proof values.", "weighted-class-distinction-ledger", "Every class retains exact part, members and unresolved distinctions."),
        binary_dimension("refinement", "How does resolution order uncertainty?", "assumed-more-information", "A name does not prove one observation separates every fine class.", "class-containment-witness", "Every fine class lies inside one coarse class and its closed-pair set is contained."),
        binary_dimension("cause", "Does entropy require random dynamics?", "ontic-random-source", "A stochastic source is neither generated nor required.", "deterministic-support-observation", "Uncertainty comes from distinctions closed by observation over deterministic support."),
        binary_dimension("generality", "What closes every finite support?", "sampled-distributions", "Examples cannot establish a fresh microstate class update.", "microstate-successor", "A fresh state extends exactly one class and its new within-class pairs."),
        binary_dimension("addition", "Is another entropy convention added?", "extra-log-base-or-prior", "A chosen log base or prior is a free parameter.", "no-extra-entropy-convention", "The exact ledger follows only from support and observation."),
    ),
    exact_result=(
        "The entropy/uncertainty kernel is complete deterministic support, total observation classes, exact class "
        "parts, complete unresolved-pair ledgers, refinement containment, successor closure and no stochastic or log rule."
    ),
    laws=(
        "observation classes form a disjoint complete partition of deterministic support",
        "uncertainty is exactly the set of within-class nonidentity microstate pairs",
        "singleton classes carry empty-One uncertainty rather than numerical zero",
        "fine observation cannot have more closed pairs than a coarser observation it refines",
        "entropy retains class provenance and exact part weights instead of collapsing to a floating scalar",
    ),
    induction_base="One deterministic microstate forms one exact whole class with structural empty-One uncertainty.",
    induction_step=(
        "Adding one fresh microstate assigns it to one retained observation image, updates that class's exact part and "
        "adds exactly one unresolved pair with every prior member of the same class; other classes remain unchanged."
    ),
    boundary_exclusions=(
        "no stochastic source premise",
        "no logarithmic entropy proof value",
        "no numerical zero for singleton uncertainty",
        "no fitted probability distribution",
    ),
    witnesses=(
        Witness("fine-certainty", "Fine observation gives every state a singleton class with empty-One uncertainty.", all(item["unresolved_distinctions"] == EMPTY_ONE for item in entropy_ledger(_support, _fine))),
        Witness("prefix-uncertainty", "Prefix observation has two exact half-support classes and one unresolved pair each.", all(item["exact_support_part"] == Fraction(1, 2) and len(item["unresolved_distinctions"]) == 1 for item in entropy_ledger(_support, _prefix))),
        Witness("coarse-uncertainty", "Complete coarsening retains all six microstate pairs as unresolved.", len(closed_pairs(_support, _coarse)) == 6),
        Witness("refinement-order", "Fine refines prefix, and prefix refines the one-class observation.", refines(_support, _fine, _prefix) and refines(_support, _prefix, _coarse)),
        Witness("closed-pair-monotonicity", "Refinement reduces closed distinctions exactly in the witness chain.", len(closed_pairs(_support, _fine)) < len(closed_pairs(_support, _prefix)) < len(closed_pairs(_support, _coarse))),
    ),
    why=(
        "Entropy and uncertainty must be reconstructed without treating randomness or real logarithms as premises. "
        "Exact observation classes already contain the complete unresolved information."
    ),
    derivation=(
        "Mathematical probability supplies exact support parts; symbol distinction supplies observation classes; "
        "information quantity supplies retained/closed ledgers. Nine axes force an entropy object that preserves every "
        "class, part and unavailable distinction."
    ),
    check=(
        "Execute all 512 entropy kernels, verify fine, prefix and total-coarsening ledgers, exact parts and refinement "
        "monotonicity, run adverse controls and independently regenerate the candidate product."
    ),
    limitations=(
        "This theorem closes exact finite entropy and uncertainty. Conventional scalar Shannon entropies are "
        "post-seal summaries only and require a separately declared correspondence map."
    ),
    correspondence_terms=("entropy", "uncertainty", "partition entropy", "resolution", "deterministic ensemble"),
)
