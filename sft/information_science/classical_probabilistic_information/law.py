"""Force classical and probabilistic information from one deterministic support."""

from __future__ import annotations

from fractions import Fraction

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-CLASSICAL-PROBABILISTIC-001"
EMPTY_ONE = ("empty-One",)


def canonical_support(support: tuple[str, ...]) -> tuple[str, ...]:
    if not support or len(set(support)) != len(support):
        raise ValueError("information support must be nonempty, complete and duplicate-free")
    return support


def classical_state(support: tuple[str, ...], held: str):
    canonical_support(support)
    if held not in support:
        raise ValueError("a classical state must be one held member of registered support")
    return {"held_state": held, "support_provenance": support}


def probability_ledger(
    support: tuple[str, ...], observation: tuple[tuple[str, str], ...]
):
    canonical_support(support)
    images = dict(observation)
    if len(images) != len(observation) or set(images) != set(support):
        raise ValueError("a probability ledger requires one observation image per microstate")
    labels = tuple(dict.fromkeys(images[state] for state in support))
    return tuple(
        {
            "observed_label": label,
            "microstates": tuple(state for state in support if images[state] == label),
            "exact_support_part": Fraction(
                sum(images[state] == label for state in support), len(support)
            ),
        }
        for label in labels
    )


def resolve_observation(
    support: tuple[str, ...], observation: tuple[tuple[str, str], ...], observed: str
):
    rows = probability_ledger(support, observation)
    matching = tuple(row for row in rows if row["observed_label"] == observed)
    if len(matching) != 1:
        raise ValueError("the observed label is outside registered observation support")
    members = matching[0]["microstates"]
    return ("classical-state", members[0]) if len(members) == 1 else ("unresolved-class", members)


def pushforward_ledger(
    support: tuple[str, ...], transformation: tuple[tuple[str, str], ...]
):
    images = dict(transformation)
    if len(images) != len(transformation) or set(images) != set(canonical_support(support)):
        raise ValueError("pushforward requires a total single-valued deterministic transformation")
    labels = tuple(dict.fromkeys(images[state] for state in support))
    return tuple(
        {
            "image": label,
            "predecessors": tuple(state for state in support if images[state] == label),
            "exact_support_part": Fraction(
                sum(images[state] == label for state in support), len(support)
            ),
        }
        for label in labels
    )


def ledger_is_exact_whole(ledger) -> bool:
    parts = tuple(row["exact_support_part"] for row in ledger)
    return bool(parts) and sum(parts, Fraction()) == Fraction(1, 1)


def deterministic_realization(
    support: tuple[str, ...], observation: tuple[tuple[str, str], ...]
):
    return tuple(
        (
            row["observed_label"],
            tuple((state, "deterministic-member") for state in row["microstates"]),
            row["exact_support_part"],
        )
        for row in probability_ledger(support, observation)
    )


_support = ("aa", "ab", "ba", "bb")
_fine = tuple((state, state) for state in _support)
_prefix = (("aa", "a"), ("ab", "a"), ("ba", "b"), ("bb", "b"))
_unequal = (("aa", "held"), ("ab", "held"), ("ba", "held"), ("bb", "other"))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact classical and probabilistic information correspondence",
    statement=(
        "Classical information is one held member of a complete deterministic support with its provenance retained. "
        "Probabilistic information is the exact observation-class ledger over that same support: every class retains "
        "its deterministic microstates and exact positive part of the whole. Observation resolves a classical state "
        "only for a singleton class; otherwise it returns the complete unresolved class. Deterministic transformations "
        "push the ledger forward by exact predecessor grouping. Probability therefore describes unavailable distinctions "
        "and does not introduce stochastic dynamics, floating propensities, numerical zero or priors."
    ),
    dependencies=(
        "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
        "SFT-INFO-MUTUAL-CONDITIONAL-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
    ),
    generation_rule=(
        "Generate the complete product of deterministic support, classical state, observation, exact class parts, "
        "probabilistic meaning, resolution, transformation, whole closure, generality and extra-random status."
    ),
    grammar_boundary=(
        "All finite classical/probabilistic information descriptions generated from complete deterministic support, "
        "one held classical state, total observation classes, exact positive support parts and total deterministic maps."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible microstates?", "sampled-or-duplicated-support", "Sampling or duplication changes every exact part.", "complete-canonical-support", "Every deterministic microstate occurs once."),
        binary_dimension("classical", "What fixes classical information?", "unheld-symbol-name", "A name alone does not locate a state in complete support.", "one-held-supported-state", "One exact support member is retained with its provenance."),
        binary_dimension("observation", "What fixes probabilistic alternatives?", "free-weight-list", "Weights without microstates import a distribution.", "total-observation-classes", "Every microstate belongs to exactly one observed class."),
        binary_dimension("parts", "What fixes probability weights?", "floating-propensities", "Floating propensities import precision and causal assumptions.", "exact-class-whole-parts", "Each nonempty class count is retained relative to complete support count."),
        binary_dimension("meaning", "What does probability represent?", "ontic-random-cause", "A random cause is neither generated nor needed.", "unresolved-deterministic-distinction", "Each probabilistic class explicitly retains the deterministic alternatives observation closes."),
        binary_dimension("resolution", "When does observation identify a state?", "likely-state-selection", "Selecting the likely state imports a prior.", "singleton-class-only", "Only one-member classes resolve; larger classes remain complete."),
        binary_dimension("transformation", "How does a distribution transform?", "stochastic-transition-matrix", "A free transition matrix adds parameters and random dynamics.", "deterministic-predecessor-grouping", "A total map groups exact predecessor support into image classes."),
        binary_dimension("normalization", "What closes the whole?", "fitted-normalization", "A fitted factor can conceal omitted states.", "partition-exact-whole", "Disjoint complete class parts reconstruct the exact whole."),
        binary_dimension("generality", "What closes arbitrary finite support?", "finite-examples-only", "Examples do not prove the next microstate update.", "microstate-successor", "A fresh microstate enters one class and every exact part is recomputed from membership."),
        binary_dimension("addition", "Is stochastic structure added?", "extra-seed-prior-or-kernel", "The addition is a free parameter and may select results.", "no-extra-stochastic-law", "All probabilistic information follows from support, observation and deterministic maps."),
    ),
    exact_result=(
        "The classical/probabilistic kernel is complete deterministic support, one held classical state, total observation "
        "classes, exact positive class parts, singleton-only resolution, deterministic pushforward, exact-whole closure, "
        "successor closure and no stochastic law."
    ),
    laws=(
        "a classical information state is one held member of complete support",
        "a probabilistic row is an exact nonempty observation class and positive whole part",
        "the complete class ledger reconstructs the exact whole",
        "observation selects a state only when its retained class is singleton",
        "deterministic pushforward groups predecessors without introducing random transitions",
    ),
    induction_base="One deterministic microstate is one held classical state and one exact whole observation class.",
    induction_step=(
        "Adding one fresh microstate extends complete support and exactly one observation class. The class ledgers and "
        "their exact whole parts update from retained membership, while each individual state remains deterministic."
    ),
    boundary_exclusions=(
        "no ontic stochastic transition premise",
        "no floating or fitted probability",
        "no numerical zero probability row; absence is empty One",
        "no prior-based selection inside a non-singleton class",
    ),
    witnesses=(
        Witness("classical-held-state", "A held aa state retains its complete four-state provenance.", classical_state(_support, "aa") == {"held_state": "aa", "support_provenance": _support}),
        Witness("exact-half-classes", "Prefix observation produces two exact one-over-two deterministic classes.", all(row["exact_support_part"] == Fraction(1, 2) and len(row["microstates"]) == 2 for row in probability_ledger(_support, _prefix))),
        Witness("exact-unequal-parts", "A three-member class and one-member class retain exact three-over-four and one-over-four parts.", tuple(row["exact_support_part"] for row in probability_ledger(_support, _unequal)) == (Fraction(3, 4), Fraction(1, 4))),
        Witness("resolution-boundary", "Fine observation resolves aa while prefix observation retains the unresolved aa/ab class.", resolve_observation(_support, _fine, "aa") == ("classical-state", "aa") and resolve_observation(_support, _prefix, "a") == ("unresolved-class", ("aa", "ab"))),
        Witness("pushforward-whole", "Deterministic prefix pushforward retains both predecessors and reconstructs the exact whole.", ledger_is_exact_whole(pushforward_ledger(_support, _prefix)) and pushforward_ledger(_support, _prefix)[0]["predecessors"] == ("aa", "ab")),
        Witness("deterministic-realization", "Every probabilistic prefix row exposes its deterministic member trace.", all(all(tag == "deterministic-member" for _, tag in row[1]) for row in deterministic_realization(_support, _prefix))),
    ),
    why=(
        "The relation between classical and probabilistic information must be explicit in a deterministic theory. "
        "Observation classes derive exact probability while preserving every underlying state."
    ),
    derivation=(
        "Mathematical probability supplies exact parts, entropy supplies observation classes, mutual information "
        "supplies joint restriction and conservation supplies deterministic pushforward. Ten axes force one shared support account."
    ),
    check=(
        "Execute all 1,024 kernels; verify held classical states, equal and unequal exact class parts, singleton resolution, "
        "unresolved-class retention, deterministic pushforward and independent candidate regeneration."
    ),
    limitations=(
        "This theorem closes finite classical/probabilistic information correspondence. Empirical frequencies require "
        "separately registered blind data protocols and do not alter the formal law."
    ),
    correspondence_terms=("classical state", "ensemble", "probability distribution", "pushforward", "epistemic uncertainty"),
)
