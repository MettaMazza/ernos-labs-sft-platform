"""Force exact finite uncertainty and statistical summaries from observation classes."""

from __future__ import annotations

from fractions import Fraction

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-PROBABILITY-STATISTICS-001"
EMPTY_ONE = ("empty-One",)


def exact_event(support: tuple[str, ...], held: tuple[str, ...]):
    if not support or len(set(support)) != len(support):
        raise ValueError("support must be a complete nonempty canonical trace")
    if len(set(held)) != len(held) or any(state not in support for state in held):
        raise ValueError("event must be a duplicate-free held support selection")
    return held if held else EMPTY_ONE


def exact_weight(support: tuple[str, ...], held: tuple[str, ...]) -> Fraction | tuple[str, ...]:
    event = exact_event(support, held)
    if event == EMPTY_ONE:
        return EMPTY_ONE
    return Fraction(len(held), len(support))


def conditional_weight(support: tuple[str, ...], event: tuple[str, ...], condition: tuple[str, ...]):
    exact_event(support, event)
    condition_form = exact_event(support, condition)
    if condition_form == EMPTY_ONE:
        return EMPTY_ONE
    intersection = tuple(state for state in support if state in event and state in condition)
    if not intersection:
        return EMPTY_ONE
    return Fraction(len(intersection), len(condition))


def independent(
    joint_support: tuple[tuple[str, str], ...],
    left_event: tuple[str, ...],
    right_event: tuple[str, ...],
) -> bool:
    left_support = tuple(dict.fromkeys(left for left, _ in joint_support))
    right_support = tuple(dict.fromkeys(right for _, right in joint_support))
    if not left_event or not right_event:
        raise ValueError("independence weight requires nonempty held events; empty cases remain empty One")
    complete = tuple((left, right) for left in left_support for right in right_support)
    if joint_support != complete:
        return False
    joint_held = tuple(pair for pair in joint_support if pair[0] in left_event and pair[1] in right_event)
    return Fraction(len(joint_held), len(joint_support)) == Fraction(len(left_event), len(left_support)) * Fraction(len(right_event), len(right_support))


def exact_mode(trace: tuple[str, ...]) -> tuple[str, ...]:
    if not trace:
        raise ValueError("a statistical trace must be generated and nonempty")
    labels = tuple(dict.fromkeys(trace))
    counts = tuple((label, sum(item == label for item in trace)) for label in labels)
    greatest = max(count for _, count in counts)
    return tuple(label for label, count in counts if count == greatest)


def observation_classes(support: tuple[str, ...], observation: tuple[tuple[str, str], ...]):
    images = dict(observation)
    if set(images) != set(support):
        raise ValueError("observation must classify every microstate once")
    labels = tuple(dict.fromkeys(images[state] for state in support))
    return tuple((label, tuple(state for state in support if images[state] == label)) for label in labels)


_support = ("aa", "ab", "ba", "bb")
_joint = (("a", "a"), ("a", "b"), ("b", "a"), ("b", "b"))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite probability and statistics from Fold observation",
    statement=(
        "Probability is an exact held-support/whole-support part relation over a complete deterministic generated "
        "microstate support; uncertainty records distinctions closed by an observation class and is not a causal "
        "random premise. Conditional weight is exact common-refinement restriction, independence is complete "
        "pair-cell factorization, and statistics are provenance-retaining finite trace summaries. The empty event "
        "is empty One, never numerical zero."
    ),
    dependencies=(
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    generation_rule=(
        "Generate the complete product of support coverage, event formation, weight, uncertainty status, conditioning, "
        "independence, statistics, empirical isolation and extra-random-law status."
    ),
    grammar_boundary=(
        "All exact finite probability spaces and statistical traces generated from complete microstate support, "
        "held selections, observation classes, common refinement, exact parts and sealed empirical measurements."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible microstates?", "sampled-or-partial-support", "A partial support silently changes every derived weight.", "complete-generated-support", "Every registered deterministic microstate occurs once."),
        binary_dimension("event", "What fixes an event?", "named-outcome", "A name without retained membership does not identify support.", "held-support-selection", "An event is a duplicate-free held selection of exact support."),
        binary_dimension("weight", "What fixes probability quantity?", "floating-propensity", "A floating propensity imports precision and a stochastic cause.", "exact-held-whole-part", "Weight is the exact held count over the complete support count."),
        binary_dimension("uncertainty", "What produces uncertainty?", "ontic-random-cause", "A causal random source is neither generated nor required.", "closed-observation-distinction", "Uncertainty records which deterministic microstate distinctions observation does not retain."),
        binary_dimension("conditioning", "What fixes conditional weight?", "renormalized-guess", "A guessed renormalization can omit common support.", "exact-common-refinement", "Restrict to the complete held condition and count its exact event intersection."),
        binary_dimension("independence", "What fixes independence?", "uncorrelated-assertion", "An assertion does not prove factorized joint support.", "pair-cell-factorization", "Complete joint support is the exact product and event weights multiply by bijection."),
        binary_dimension("statistics", "What fixes a statistic?", "opaque-estimator", "An opaque scalar erases source rows and tie structure.", "provenance-retaining-summary", "Every summary is recomputable from the complete finite trace and retains ties."),
        binary_dimension("empirical", "How may measured rows test a law?", "target-informed-fit", "Using target rows during derivation allows them to select the law.", "post-seal-blind-check", "Natural measurements enter only after formal sealing under registered isolation."),
        binary_dimension("addition", "Is a stochastic law added?", "extra-random-parameter", "A seed distribution or prior is a free parameter.", "no-extra-random-parameter", "All weights follow from support and observation without stochastic dynamics."),
    ),
    exact_result=(
        "The probability/statistics kernel is complete deterministic support, held events, exact held/whole weights, "
        "observation-class uncertainty, common-refinement conditioning, pair-cell independence, transparent finite "
        "summaries and post-seal empirical checking without random parameters."
    ),
    laws=(
        "event weight is an exact positive part relation; empty event is empty One",
        "conditional weight is exact restriction to a nonempty held condition",
        "independence is a bijective complete joint-support factorization",
        "uncertainty belongs to an observation partition and does not alter deterministic microstate evolution",
        "statistical summaries retain exact provenance and all tied alternatives",
    ),
    induction_base="A One-state support has whole certainty; its held-empty event is represented by empty One.",
    induction_step=(
        "Adding one fresh microstate extends whole support once and either extends or leaves each held event. Exact "
        "parts, observation classes, intersections and summaries update from that retained membership without a prior."
    ),
    boundary_exclusions=(
        "no ontic stochastic premise",
        "no floating probability in proof evidence",
        "no Bayesian or distributional prior parameter",
        "no target data may select a formal law",
    ),
    witnesses=(
        Witness("exact-weight", "Two held states in four complete states have the exact one-over-two part.", exact_weight(_support, ("aa", "ab")) == Fraction(1, 2)),
        Witness("empty-event", "The empty event is structural empty One rather than numerical zero.", exact_weight(_support, ()) == EMPTY_ONE),
        Witness("conditional", "Conditioning on the two a-prefix states retains one selected state as one-over-two.", conditional_weight(_support, ("aa", "ba"), ("aa", "ab")) == Fraction(1, 2)),
        Witness("independence", "The complete two-by-two pair support factorizes exactly.", independent(_joint, ("a",), ("a",))),
        Witness("ties-retained", "An exact modal summary preserves both equally supported alternatives.", exact_mode(("a", "b", "a", "b")) == ("a", "b")),
        Witness("observation-classes", "A prefix observation retains two exact two-state classes.", observation_classes(_support, (("aa", "a"), ("ab", "a"), ("ba", "b"), ("bb", "b"))) == (("a", ("aa", "ab")), ("b", ("ba", "bb")))),
    ),
    why=(
        "Prediction and experiment require uncertainty and statistics, but a superdeterministic Fold model cannot "
        "import stochastic dynamics. Exact observation classes supply the required epistemic structure."
    ),
    derivation=(
        "Parts supply exact held/whole quantities; combinatorics supplies complete support; the measurement boundary "
        "isolates data. Nine structural choices force the observation-support account without a prior."
    ),
    check=(
        "Execute all 512 kernels, verify exact event and conditional parts, an empty-One control, joint-support "
        "factorization, tied summaries and observation classes, then independently regenerate the census."
    ),
    limitations=(
        "This closes exact finite probability and descriptive statistics. Inferential claims about natural data "
        "remain empirical claims and require preregistered blind validation through the empirical engine."
    ),
    correspondence_terms=("probability space", "conditional probability", "independence", "random variable", "statistic", "sampling"),
)
