"""Force mutual and conditional information as exact observation-incidence ledgers."""

from __future__ import annotations

from fractions import Fraction

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-MUTUAL-CONDITIONAL-001"
EMPTY_ONE = ("empty-One",)


def validate_observation(
    support: tuple[str, ...], observation: tuple[tuple[str, str], ...]
) -> dict[str, str]:
    images = dict(observation)
    if not support or len(set(support)) != len(support):
        raise ValueError("information incidence requires complete duplicate-free support")
    if len(images) != len(observation) or set(images) != set(support):
        raise ValueError("an observation must classify every support form exactly once")
    return images


def observation_classes(
    support: tuple[str, ...], observation: tuple[tuple[str, str], ...]
):
    images = validate_observation(support, observation)
    labels = tuple(dict.fromkeys(images[state] for state in support))
    return tuple((label, tuple(state for state in support if images[state] == label)) for label in labels)


def joint_ledger(
    support: tuple[str, ...],
    left: tuple[tuple[str, str], ...],
    right: tuple[tuple[str, str], ...],
):
    left_images = validate_observation(support, left)
    right_images = validate_observation(support, right)
    left_labels = tuple(dict.fromkeys(left_images[state] for state in support))
    right_labels = tuple(dict.fromkeys(right_images[state] for state in support))
    rows = []
    for left_label in left_labels:
        left_members = tuple(state for state in support if left_images[state] == left_label)
        left_part = Fraction(len(left_members), len(support))
        for right_label in right_labels:
            right_members = tuple(state for state in support if right_images[state] == right_label)
            right_part = Fraction(len(right_members), len(support))
            members = tuple(
                state
                for state in support
                if left_images[state] == left_label and right_images[state] == right_label
            )
            joint_part = Fraction(len(members), len(support)) if members else EMPTY_ONE
            product_part = left_part * right_part
            relation = (
                "empty-One-below-product"
                if joint_part == EMPTY_ONE
                else "equal" if joint_part == product_part
                else "joint-below-product" if joint_part < product_part
                else "joint-above-product"
            )
            rows.append(
                {
                    "left": left_label,
                    "right": right_label,
                    "members": members if members else EMPTY_ONE,
                    "joint_part": joint_part,
                    "left_part": left_part,
                    "right_part": right_part,
                    "product_part": product_part,
                    "relation": relation,
                }
            )
    return tuple(rows)


def conditional_ledger(
    support: tuple[str, ...],
    target: tuple[tuple[str, str], ...],
    given: tuple[tuple[str, str], ...],
):
    target_images = validate_observation(support, target)
    given_images = validate_observation(support, given)
    target_labels = tuple(dict.fromkeys(target_images[state] for state in support))
    given_labels = tuple(dict.fromkeys(given_images[state] for state in support))
    rows = []
    for given_label in given_labels:
        given_members = tuple(state for state in support if given_images[state] == given_label)
        for target_label in target_labels:
            members = tuple(state for state in given_members if target_images[state] == target_label)
            rows.append(
                {
                    "given": given_label,
                    "target": target_label,
                    "members": members if members else EMPTY_ONE,
                    "exact_given_part": Fraction(len(members), len(given_members)) if members else EMPTY_ONE,
                }
            )
    return tuple(rows)


def conditionally_resolved(
    support: tuple[str, ...],
    target: tuple[tuple[str, str], ...],
    given: tuple[tuple[str, str], ...],
) -> bool:
    target_images = validate_observation(support, target)
    return all(
        sum(row["members"] != EMPTY_ONE for row in conditional_ledger(support, target, given) if row["given"] == given_label) == 1
        for given_label, _ in observation_classes(support, given)
    ) and bool(target_images)


def factorizes(
    support: tuple[str, ...],
    left: tuple[tuple[str, str], ...],
    right: tuple[tuple[str, str], ...],
) -> bool:
    return all(row["joint_part"] != EMPTY_ONE and row["relation"] == "equal" for row in joint_ledger(support, left, right))


def dependence_ledger(
    support: tuple[str, ...],
    left: tuple[tuple[str, str], ...],
    right: tuple[tuple[str, str], ...],
):
    rows = tuple(row for row in joint_ledger(support, left, right) if row["relation"] != "equal")
    return rows if rows else EMPTY_ONE


_support = ("aa", "ab", "ba", "bb")
_left = (("aa", "a"), ("ab", "a"), ("ba", "b"), ("bb", "b"))
_right = (("aa", "a"), ("ab", "b"), ("ba", "a"), ("bb", "b"))
_same = _left


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact mutual and conditional information from joint observation incidence",
    statement=(
        "Conditional information is the complete exact restriction of one total observation to every class of another. "
        "Mutual dependence is the complete joint-incidence ledger comparing each observed joint support part with the "
        "product of its exact marginal parts; absent cells remain structural empty One and no signed subtraction is used. "
        "Factorization holds exactly when every joint cell is present and its part equals the marginal product. Thus "
        "conditioning and dependence are derived from deterministic support and observation, without priors, logarithms, "
        "stochastic causes or floating values."
    ),
    dependencies=(
        "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
        "SFT-INFO-QUANTITY-001",
    ),
    generation_rule=(
        "Generate the complete product of support, two observations, marginal classes, joint incidence, conditional "
        "restriction, dependence comparison, factorization, deterministic status, generality and extra-measure status."
    ),
    grammar_boundary=(
        "All finite mutual and conditional information structures generated from complete deterministic support, two "
        "total observation maps, their exact marginal classes, complete joint cells and exact positive part relations."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible source forms?", "partial-source-support", "Omission changes marginal, joint and conditional parts.", "complete-deterministic-support", "Every registered source form occurs exactly once."),
        binary_dimension("observations", "What fixes the two information views?", "partial-or-multivalued-views", "An incomplete or multivalued view cannot form exact classes.", "two-total-observation-maps", "Each source form has exactly one image in each view."),
        binary_dimension("marginals", "What fixes the separate information classes?", "named-marginal-scores", "Scores erase which source forms produce each image.", "exact-provenance-classes", "Each image retains its complete source class and exact whole part."),
        binary_dimension("joint", "What fixes combined information?", "sampled-joint-cells", "Sampling can hide absent or repeated combinations.", "complete-joint-incidence-ledger", "Every pair of marginal labels has an explicit member class or empty One."),
        binary_dimension("conditional", "What fixes information under a condition?", "renormalized-prior", "A prior or guessed normalization is not generated.", "exact-class-restriction", "Each target class is intersected with the complete held given class."),
        binary_dimension("mutual", "What fixes mutual dependence?", "scalar-log-ratio", "A log ratio imports real values and erases the cells responsible.", "joint-versus-product-ledger", "Every joint part is compared exactly with its marginal product while retaining provenance."),
        binary_dimension("factorization", "What forces independence?", "uncorrelated-assertion", "A label does not establish every joint cell and weight.", "all-cell-exact-equality", "Every joint cell exists and equals its exact marginal product."),
        binary_dimension("cause", "Does dependence require random generation?", "stochastic-source-premise", "A random cause is neither forced nor required.", "deterministic-observation-incidence", "Dependence is a relation among exact observation classes over deterministic support."),
        binary_dimension("generality", "What closes arbitrary finite support?", "small-table-only", "A table does not establish the next source update.", "source-successor-update", "A fresh source enters one marginal class and one joint cell, updating exact parts."),
        binary_dimension("addition", "Is another information measure added?", "extra-base-prior-or-scalar", "The added choice is a free parameter.", "no-extra-information-measure", "The ledgers follow only from complete support and total observations."),
    ),
    exact_result=(
        "The mutual/conditional kernel is complete deterministic support, two total observations, exact marginal and "
        "joint classes, exact conditional restrictions, provenance-retaining joint/product comparison, all-cell "
        "factorization, successor closure and no stochastic or logarithmic measure."
    ),
    laws=(
        "conditional rows partition every nonempty given class by target observation",
        "every conditional part is exact and positive; absent intersections are empty One",
        "the joint ledger explicitly contains every marginal-label pair cell",
        "factorization holds exactly when every joint cell equals its marginal-part product",
        "dependence retains the responsible joint cells and comparison direction without signed subtraction",
    ),
    induction_base="One source form gives one whole marginal cell, one whole joint cell and one whole conditional cell.",
    induction_step=(
        "Adding one fresh source form places it in exactly one class of each observation and therefore one joint cell; "
        "all marginal, joint and conditional counts and exact parts are recomputed from retained membership."
    ),
    boundary_exclusions=(
        "no logarithmic mutual-information proof value",
        "no signed or floating dependence score",
        "no stochastic cause or prior distribution",
        "no incomplete joint census presented as factorization",
    ),
    witnesses=(
        Witness("conditional-parts", "Conditioning the second coordinate on the first yields two exact half-parts in each given class.", all(row["exact_given_part"] == Fraction(1, 2) for row in conditional_ledger(_support, _right, _left))),
        Witness("factorized-grid", "The complete two-by-two coordinate grid factorizes exactly.", factorizes(_support, _left, _right)),
        Witness("empty-dependence", "A factorized grid has structural empty-One dependence ledger.", dependence_ledger(_support, _left, _right) == EMPTY_ONE),
        Witness("resolved-copy", "An observation is conditionally resolved by an exact copy of itself.", conditionally_resolved(_support, _left, _same)),
        Witness("dependent-copy", "Two identical nontrivial views do not factorize and retain their responsible cells.", not factorizes(_support, _left, _same) and dependence_ledger(_support, _left, _same) != EMPTY_ONE),
    ),
    why=(
        "Conditional and mutual information must preserve the observation cells that create the relation. Collapsing "
        "them into an imported logarithmic scalar would discard the exact structural proof."
    ),
    derivation=(
        "Probability supplies exact support parts, entropy supplies observation classes and quantity supplies retained "
        "distinctions. Ten axes force conditional restriction, joint incidence and exact factorization."
    ),
    check=(
        "Execute all 1,024 kernels; exhaust a two-by-two support grid, verify conditional parts, factorization and its "
        "empty dependence ledger, reject the copied-view control and independently regenerate the product."
    ),
    limitations=(
        "This closes exact finite structural conditional information and dependence. Conventional scalar Shannon "
        "mutual information is a post-seal correspondence summary, not an SFT proof value."
    ),
    correspondence_terms=("conditional information", "mutual information", "joint distribution", "marginal", "independence"),
)
