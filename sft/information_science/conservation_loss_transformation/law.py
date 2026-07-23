"""Force information conservation and loss from exact total transformations."""

from __future__ import annotations

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-CONSERVATION-LOSS-001"
EMPTY_ONE = ("empty-One",)


def validate_transformation(
    source: tuple[str, ...], transformation: tuple[tuple[str, str], ...]
) -> dict[str, str]:
    images = dict(transformation)
    if not source or len(set(source)) != len(source):
        raise ValueError("a transformation requires complete duplicate-free source support")
    if len(images) != len(transformation) or set(images) != set(source):
        raise ValueError("a transformation must map every source form exactly once")
    return images


def source_pairs(source: tuple[str, ...]):
    if not source or len(set(source)) != len(source):
        raise ValueError("distinction accounting requires canonical source support")
    return tuple(
        (left, right)
        for position, left in enumerate(source)
        for right in source[position + 1 :]
    )


def transformation_ledger(
    source: tuple[str, ...], transformation: tuple[tuple[str, str], ...]
):
    images = validate_transformation(source, transformation)
    pairs = source_pairs(source)
    retained = tuple(pair for pair in pairs if images[pair[0]] != images[pair[1]])
    closed = tuple(pair for pair in pairs if images[pair[0]] == images[pair[1]])
    fibres = tuple(
        (image, tuple(state for state in source if images[state] == image))
        for image in dict.fromkeys(images[state] for state in source)
    )
    return {
        "source_support": source,
        "image_support": tuple(image for image, _ in fibres),
        "retained_distinctions": retained if retained else EMPTY_ONE,
        "closed_distinctions": closed if closed else EMPTY_ONE,
        "predecessor_fibres": fibres,
    }


def compose(
    source: tuple[str, ...],
    first: tuple[tuple[str, str], ...],
    second: tuple[tuple[str, str], ...],
):
    first_images = validate_transformation(source, first)
    middle = tuple(dict.fromkeys(first_images[state] for state in source))
    second_images = validate_transformation(middle, second)
    return tuple((state, second_images[first_images[state]]) for state in source)


def is_reversible(source: tuple[str, ...], transformation: tuple[tuple[str, str], ...]) -> bool:
    images = validate_transformation(source, transformation)
    return len(set(images.values())) == len(source)


def reverse_record(source: tuple[str, ...], transformation: tuple[tuple[str, str], ...]):
    ledger = transformation_ledger(source, transformation)
    return tuple(
        (
            image,
            members[0] if len(members) == 1 else ("held-predecessor-labels", members),
        )
        for image, members in ledger["predecessor_fibres"]
    )


def downstream_retention_law(
    source: tuple[str, ...],
    first: tuple[tuple[str, str], ...],
    second: tuple[tuple[str, str], ...],
) -> bool:
    first_ledger = transformation_ledger(source, first)
    composite_ledger = transformation_ledger(source, compose(source, first, second))
    first_retained = set(() if first_ledger["retained_distinctions"] == EMPTY_ONE else first_ledger["retained_distinctions"])
    composite_retained = set(() if composite_ledger["retained_distinctions"] == EMPTY_ONE else composite_ledger["retained_distinctions"])
    return composite_retained.issubset(first_retained)


_source = ("aa", "ab", "ba", "bb")
_identity = tuple((state, state) for state in _source)
_prefix = (("aa", "a"), ("ab", "a"), ("ba", "b"), ("bb", "b"))
_erase = (("a", "one"), ("b", "one"))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact information conservation, loss and transformation",
    statement=(
        "An information transformation is a total single-valued map over complete source support. Every source "
        "distinction is conserved as an image distinction or closed inside an exact predecessor fibre; these two ledgers "
        "are disjoint and exhaustive. Reversibility is forced exactly by singleton fibres. An irreversible transformation "
        "can be reversed only when a retained predecessor label resolves each non-singleton fibre. Under composition, "
        "downstream retained distinctions are a subset of those retained upstream, so a map creates no unrecorded source distinction."
    ),
    dependencies=(
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-LOGIC-PROOF-001",
        "SFT-INFO-ENCODING-DECODING-001",
        "SFT-INFO-CHANNEL-CAPACITY-001",
        "SFT-INFO-MUTUAL-CONDITIONAL-001",
    ),
    generation_rule=(
        "Generate the complete product of source support, totality, provenance, pair accounting, fibres, loss, "
        "reversibility, composition, generality and extra-source status."
    ),
    grammar_boundary=(
        "All finite deterministic information transformations generated from complete canonical source support, "
        "total single-valued maps, exact image fibres, complete source-pair ledgers and transformation composition."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible inputs?", "partial-input-support", "Omission hides distinctions that may be lost.", "complete-canonical-source", "Every registered source form occurs once."),
        binary_dimension("map", "What fixes transformation?", "partial-or-multivalued-rule", "An incomplete or multivalued rule cannot account for every source.", "total-single-valued-map", "Each source has exactly one held image."),
        binary_dimension("provenance", "What connects images to sources?", "image-only-output", "Image-only output erases which sources entered each result.", "exact-predecessor-fibres", "Every image retains its complete source class."),
        binary_dimension("accounting", "What fixes conserved information?", "output-cardinality-only", "A count erases which distinctions survive.", "complete-source-pair-partition", "Every source pair is classified exactly as retained or closed."),
        binary_dimension("loss", "What constitutes information loss?", "lower-score-assertion", "A score does not identify unavailable predecessors.", "non-singleton-image-fibre", "Loss is the exact source distinctions closed inside an image fibre."),
        binary_dimension("reversal", "What forces reversibility?", "assumed-inverse", "An inverse cannot choose among merged predecessors.", "singleton-fibre-or-held-record", "Singleton fibres reverse directly; merged fibres require retained predecessor labels."),
        binary_dimension("composition", "How does loss propagate?", "fresh-downstream-distinction", "A deterministic image map has no source for a distinction already closed.", "retained-pair-subset", "A downstream map can preserve or close an upstream distinction but cannot reopen it."),
        binary_dimension("conservation", "What is information conservation?", "unchanged-scalar", "An unchanged scalar can hide exchanges among distinctions.", "retained-plus-closed-exhaustion", "The two exact ledgers disjointly exhaust all source distinctions."),
        binary_dimension("generality", "What closes arbitrary finite maps?", "sampled-transformations", "Examples do not prove a fresh source image accounted.", "source-successor-map-cell", "A fresh source adds one held map cell and all new pair comparisons."),
        binary_dimension("addition", "May information appear without a source?", "unrecorded-created-distinction", "A new distinction without source or record violates provenance.", "no-extra-information-source", "All output distinctions trace to separated source images or declared external input."),
    ),
    exact_result=(
        "The transformation kernel is complete source support, a total held map, exact predecessor fibres, exhaustive "
        "retained/closed source distinctions, singleton-fibre reversibility, held reverse records, compositional "
        "retention monotonicity and no unrecorded information source."
    ),
    laws=(
        "retained and closed ledgers are disjoint and exhaust every source distinction",
        "information loss is exactly the source distinctions inside non-singleton image fibres",
        "a transformation is reversible exactly when every predecessor fibre is singleton",
        "a non-singleton fibre requires a retained predecessor label for exact reconstruction",
        "composition cannot restore a distinction already closed by an upstream deterministic map",
    ),
    induction_base="One source maps to one held image, has one singleton fibre and structural empty-One pair ledgers.",
    induction_step=(
        "Adding one fresh source adds one image membership and one pair against each prior source. Image equality "
        "places each new pair exactly in the retained or closed ledger and updates one predecessor fibre."
    ),
    boundary_exclusions=(
        "no image without source provenance",
        "no assumed inverse across merged predecessors",
        "no scalar conservation law replacing distinction ledgers",
        "no downstream reopening without a declared external record",
    ),
    witnesses=(
        Witness("identity-conservation", "Identity retains all six source distinctions and closes none.", len(transformation_ledger(_source, _identity)["retained_distinctions"]) == 6 and transformation_ledger(_source, _identity)["closed_distinctions"] == EMPTY_ONE),
        Witness("prefix-loss", "Prefix projection retains four cross-prefix distinctions and closes two exact predecessor pairs.", len(transformation_ledger(_source, _prefix)["retained_distinctions"]) == 4 and len(transformation_ledger(_source, _prefix)["closed_distinctions"]) == 2),
        Witness("reversibility-boundary", "Identity is reversible while prefix projection is not.", is_reversible(_source, _identity) and not is_reversible(_source, _prefix)),
        Witness("reverse-record", "Each prefix image retains its two possible source labels.", all(item[1][0] == "held-predecessor-labels" and len(item[1][1]) == 2 for item in reverse_record(_source, _prefix))),
        Witness("data-processing", "Erasing the retained prefix cannot reopen either previously closed distinction.", downstream_retention_law(_source, _prefix, _erase) and transformation_ledger(_source, compose(_source, _prefix, _erase))["retained_distinctions"] == EMPTY_ONE),
    ),
    why=(
        "Information conservation and loss require pair-level accounting: image counts alone cannot show which source "
        "alternatives remain recoverable or what record reversal requires."
    ),
    derivation=(
        "Encoding supplies inverse classes, channels supply relations, mutual information supplies joint incidence and "
        "dynamics supplies composition. Ten axes force exhaustive pair accounting and the compositional loss law."
    ),
    check=(
        "Execute all 1,024 kernels; compare identity, prefix projection and total erasure, verify exact pair ledgers, "
        "reverse records and downstream subset law, then independently regenerate the product."
    ),
    limitations=(
        "This theorem closes exact finite deterministic information transformation. Thermodynamic energy costs and "
        "operational quantum measurement belong to later physical and quantum branches."
    ),
    correspondence_terms=("data processing", "information loss", "reversible map", "many-to-one map", "sufficient record"),
)
