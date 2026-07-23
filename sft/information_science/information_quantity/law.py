"""Force information quantity as exact retained distinction structure."""

from __future__ import annotations

from itertools import product

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-QUANTITY-001"
EMPTY_ONE = ("empty-One",)
Word = tuple[str, ...]


def complete_word_support(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    if len(labels) < 2 or len(set(labels)) != len(labels):
        raise ValueError("information support requires at least one generated distinction")
    if not positions or len(set(positions)) != len(positions):
        raise ValueError("information depth requires a nonempty canonical position trace")
    return tuple(tuple(word) for word in product(labels, repeat=len(positions)))


def distinction_pairs(support: tuple[Word, ...]) -> tuple[tuple[Word, Word], ...]:
    if not support or len(set(support)) != len(support):
        raise ValueError("information support must be complete and duplicate-free")
    return tuple(
        (left, right)
        for left_position, left in enumerate(support)
        for right in support[left_position + 1 :]
        if left != right
    )


def information_profile(
    support: tuple[Word, ...], observation: tuple[tuple[Word, str], ...]
):
    images = dict(observation)
    if len(images) != len(observation) or set(images) != set(support):
        raise ValueError("quantity requires one observation image for every support form")
    pairs = distinction_pairs(support)
    retained = tuple(pair for pair in pairs if images[pair[0]] != images[pair[1]])
    closed = tuple(pair for pair in pairs if images[pair[0]] == images[pair[1]])
    classes = tuple(dict.fromkeys(images[word] for word in support))
    return {
        "support_trace": support,
        "observation_classes": classes,
        "retained_distinctions": retained,
        "closed_distinctions": closed,
    }


def distinction_position_trace(labels: tuple[str, ...], positions: tuple[str, ...]):
    support = complete_word_support(labels, positions)
    for position_index, position in enumerate(positions):
        for prefix in product(labels, repeat=position_index):
            for suffix in product(labels, repeat=len(positions) - position_index - 1):
                varied = tuple(prefix) + (labels[0],) + tuple(suffix)
                mate = tuple(prefix) + (labels[1],) + tuple(suffix)
                if varied not in support or mate not in support:
                    raise ValueError("position does not independently realize the Fold distinction")
    return tuple((position, "one-Fold-distinction") for position in positions)


def compose_support(left: tuple[Word, ...], right: tuple[Word, ...]) -> tuple[Word, ...]:
    if not left or not right:
        raise ValueError("information composition requires nonempty supports")
    return tuple(a + b for a in left for b in right)


_labels = ("held-a", "held-b")
_positions = ("p1", "p2", "p3")
_support = complete_word_support(_labels, _positions)
_fine = tuple((word, "seen:" + ":".join(word)) for word in _support)
_coarse = tuple((word, "seen:" + word[0]) for word in _support)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact information quantity as retained distinction structure",
    statement=(
        "Information quantity is the exact structure of distinguishable alternatives retained from a complete "
        "generated support: the support trace, observation-class trace, retained distinction ledger and closed "
        "distinction ledger. The first Fold supplies one native distinction unit. Complete Fold-word support across "
        "a canonical position trace supplies one independently witnessed unit per position; composition is complete "
        "pair support and concatenated position provenance. No logarithm, real scale or semantic zero is foundational."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-INFO-SYMBOL-DISTINCTION-001",
        "SFT-INFO-ENCODING-DECODING-001",
    ),
    generation_rule=(
        "Generate the complete product of support coverage, distinction ledger, observation classes, native unit, "
        "position independence, quantity representation, composition, generality and extra-scale status."
    ),
    grammar_boundary=(
        "All finite information profiles generated from complete canonical Fold-word support, total observation "
        "classes, exact pair distinctions, independently varied positions and pair-cell composition."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible information states?", "partial-support", "Omitting a generated alternative changes every distinction count.", "complete-canonical-support", "Every registered alternative occurs once."),
        binary_dimension("pairs", "What fixes possible distinctions?", "sampled-pairs", "Sampling cannot prove a distinction ledger complete.", "complete-unordered-pair-ledger", "Every pair of distinct support forms occurs once."),
        binary_dimension("observation", "What fixes retained distinctions?", "assumed-resolution", "An assumed resolution has no source-to-image evidence.", "exact-observation-classes", "Image equality classifies every pair as retained or closed."),
        binary_dimension("unit", "What supplies one native information unit?", "imported-bit", "A conventional binary unit would select the answer.", "first-Fold-distinction", "The minimal Fold's two held labels supply the first exact alternative distinction."),
        binary_dimension("positions", "When do several units compose?", "word-length-only", "Length alone does not show each position can vary independently.", "independent-position-witness", "Every position realizes the Fold distinction with all other positions held."),
        binary_dimension("quantity", "How is information quantity represented?", "real-logarithm", "A logarithm imports irrational and floating proof values.", "exact-support-and-distinction-profile", "The complete exact ledgers retain the quantity without a borrowed scale."),
        binary_dimension("composition", "How do information supports combine?", "count-product-only", "A scalar product erases source-coordinate provenance.", "complete-pair-support", "Every left state pairs once with every right state and retains both word traces."),
        binary_dimension("generality", "What closes every generated word depth?", "depth-table", "A table of small supports does not prove the next position.", "position-successor", "A fresh position appends every held label to every prior word."),
        binary_dimension("addition", "Is another information scale added?", "extra-log-base-or-unit", "A chosen base or physical scale is a free parameter.", "no-extra-information-scale", "All quantity follows from Fold units, support and observation."),
    ),
    exact_result=(
        "The information-quantity kernel is complete support and pair ledgers, exact retained/closed observation "
        "distinctions, first-Fold units, independently witnessed position traces, pair-support composition and no log scale."
    ),
    laws=(
        "retained and closed distinction ledgers are disjoint and exhaust complete support pairs",
        "fine observation retains every nonidentity support distinction",
        "coarsening can only move pair distinctions from retained to closed",
        "one complete Fold position supplies one independently realized distinction unit",
        "composing supports retains both source coordinates and concatenates their unit traces",
    ),
    induction_base="The first Fold position has complete two-label support and one independently realized distinction unit.",
    induction_step=(
        "Appending one fresh position extends every prior word once with every held label. Prior position witnesses "
        "remain, the fresh position varies across its labels for each held prefix, and all new support pairs enter exactly once."
    ),
    boundary_exclusions=(
        "no logarithm as a proof operation",
        "no real-valued or irrational information quantity",
        "no semantic numerical zero for identity information",
        "no incomplete support presented as full quantity",
    ),
    witnesses=(
        Witness("complete-support", "Three independently held Fold positions generate eight unique exact words.", len(_support) == 8 and len(set(_support)) == 8),
        Witness("fine-ledger", "Fine observation retains every distinct support pair and closes none.", len(information_profile(_support, _fine)["retained_distinctions"]) == 28 and not information_profile(_support, _fine)["closed_distinctions"]),
        Witness("coarse-ledger", "First-position observation retains cross-class pairs and closes within-class pairs.", len(information_profile(_support, _coarse)["retained_distinctions"]) == 16 and len(information_profile(_support, _coarse)["closed_distinctions"]) == 12),
        Witness("position-units", "Each of three positions independently realizes the Fold distinction.", distinction_position_trace(_labels, _positions) == (("p1", "one-Fold-distinction"), ("p2", "one-Fold-distinction"), ("p3", "one-Fold-distinction"))),
        Witness("support-composition", "Two two-word supports compose into four coordinate-preserving words.", len(compose_support((("a",), ("b",)), (("x",), ("y",)))) == 4),
    ),
    why=(
        "Information quantity must be derived from exact alternatives and observation before entropy, capacity or "
        "compression. Importing logarithms would install a conventional numerical answer and forbidden proof values."
    ),
    derivation=(
        "Fold assembly supplies complete word support; symbol distinction supplies exact observation ledgers; encoding "
        "supplies representation; combinatorics supplies complete pairs. Nine structural questions force a ledger-valued "
        "quantity and independently witnessed Fold-position unit."
    ),
    check=(
        "Execute all 512 quantity kernels, generate complete three-position support, compare fine and coarse ledgers, "
        "verify independent units and composition, run adverse controls and independently regenerate the product."
    ),
    limitations=(
        "This theorem closes exact finite information quantity. Conventional logarithmic units may be post-seal "
        "correspondence summaries but are not SFT proof values."
    ),
    correspondence_terms=("information content", "bit", "alphabet size", "logarithmic information", "joint information"),
)
