"""Force exact finite codes from word support and disjoint error images."""

from __future__ import annotations

from itertools import product

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-CODING-001"
EMPTY_ONE = ("empty-One",)
Word = tuple[str, ...]


def complete_support(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    if len(labels) < 2 or len(set(labels)) != len(labels) or not positions:
        raise ValueError("code support requires distinct labels and nonempty positions")
    return tuple(tuple(word) for word in product(labels, repeat=len(positions)))


def codebook(support: tuple[Word, ...], held: tuple[Word, ...]) -> tuple[Word, ...]:
    if not held or len(set(held)) != len(held) or any(word not in support for word in held):
        raise ValueError("a codebook is a nonempty duplicate-free held support selection")
    return held


def difference_trace(left: Word, right: Word):
    if len(left) != len(right):
        raise ValueError("codewords require one common position carrier")
    held = tuple(
        (f"position-{position + 1}", a, b)
        for position, (a, b) in enumerate(zip(left, right))
        if a != b
    )
    return held if held else EMPTY_ONE


def single_label_images(word: Word, labels: tuple[str, ...]) -> tuple[Word, ...]:
    images = [word]
    for position, held in enumerate(word):
        for label in labels:
            if label == held:
                continue
            images.append(word[:position] + (label,) + word[position + 1 :])
    return tuple(images)


def error_image_family(codes: tuple[Word, ...], labels: tuple[str, ...]):
    return tuple((word, single_label_images(word, labels)) for word in codes)


def detectable_code(codes: tuple[Word, ...], labels: tuple[str, ...]) -> bool:
    return all(
        image == source or image not in codes
        for source in codes for image in single_label_images(source, labels)
    )


def correctable_code(codes: tuple[Word, ...], labels: tuple[str, ...]) -> bool:
    family = error_image_family(codes, labels)
    return all(
        not set(left_images).intersection(right_images)
        for left_position, (_, left_images) in enumerate(family)
        for _, right_images in family[left_position + 1 :]
    )


def decode_received(codes: tuple[Word, ...], labels: tuple[str, ...], received: Word):
    sources = tuple(source for source, images in error_image_family(codes, labels) if received in images)
    return ("unique-source", sources[0]) if len(sources) == 1 else ("closed-source-class", sources)


def repetition_code(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    if len(labels) < 2 or not positions:
        raise ValueError("repetition code requires a distinction and nonempty positions")
    return tuple(tuple(label for _ in positions) for label in labels)


_labels = ("a", "b")
_positions = ("p1", "p2", "p3")
_support = complete_support(_labels, _positions)
_repetition = repetition_code(_labels, _positions)
_uncoded = (("a",), ("b",))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite coding, detection and correction",
    statement=(
        "A finite code is a nonempty held selection of complete generated equal-position word support plus a total "
        "source/codeword relation. Codeword difference is the exact changed-position trace. A registered error family "
        "is detectable when every nonidentity image lies outside the codebook and correctable when distinct codewords "
        "have disjoint complete error-image supports. Decoding is then the unique source whose image family contains "
        "the received word. Redundancy is admitted only when those retained positions force separation."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-INFO-COMPRESSION-REDUNDANCY-001",
        "SFT-INFO-NOISE-ERROR-001",
    ),
    generation_rule=(
        "Generate the complete product of word support, codebook selection, source encoding, position identity, "
        "difference trace, error-family coverage, detection, correction, redundancy witness, generality and extra-code status."
    ),
    grammar_boundary=(
        "All finite codes generated from complete held-label word support, held codebooks, exact source maps, common "
        "position carriers, registered error actions and complete error-image families."
    ),
    dimensions=(
        binary_dimension("support", "What fixes possible codewords?", "partial-word-support", "Omission hides possible code or error images.", "complete-generated-word-support", "Every held-label word over the registered positions occurs once."),
        binary_dimension("codebook", "What fixes valid words?", "free-valid-list", "A free list lacks a complete source support boundary.", "held-support-selection", "The codebook is an exact nonempty selection of generated words."),
        binary_dimension("encoding", "What links messages to codewords?", "implicit-assignment", "An implicit assignment erases source provenance.", "total-source-code-relation", "Every source message has one retained codeword."),
        binary_dimension("positions", "What makes codewords comparable?", "unequal-or-unlabelled-positions", "Position changes cannot be located on unequal or anonymous carriers.", "common-canonical-position-trace", "Every word uses the same retained ordered position carrier."),
        binary_dimension("difference", "What fixes codeword separation?", "scalar-distance", "A scalar erases which positions and labels differ.", "complete-difference-trace", "Every changed position retains both code labels; equality is empty One."),
        binary_dimension("errors", "What fixes an error family?", "sampled-error-outputs", "Sampling cannot prove image supports disjoint.", "complete-registered-error-images", "Every registered action image of every codeword is generated."),
        binary_dimension("detection", "What forces detection?", "likely-corruption", "Likelihood imports a prior and threshold.", "noncodeword-image", "Every nonidentity registered image lies outside the valid codebook."),
        binary_dimension("correction", "What forces correction?", "nearest-codeword", "A metric can tie and is not structurally supplied.", "disjoint-error-image-support", "Every received image belongs to at most one source codeword family."),
        binary_dimension("redundancy", "When are added positions lawful?", "unaccounted-padding", "Padding without a correction witness is an unforced addition.", "separation-forcing-positions", "Every added position participates in the exact disjoint-image certificate."),
        binary_dimension("generality", "What closes any registered finite error family?", "fixed-mask-example", "One mask does not establish all registered actions.", "error-action-successor", "A fresh action extends every codeword image family and disjointness is rechecked."),
        binary_dimension("addition", "Is another coding theorem imported?", "extra-distance-or-rate-rule", "A borrowed metric or asymptotic rate can select the code.", "no-extra-coding-rule", "Code status follows only from generated support and error images."),
    ),
    exact_result=(
        "The coding kernel is complete word support, held codebook and source map, common positions, exact differences, "
        "complete registered error images, structural detection, disjoint-support correction and witnessed redundancy."
    ),
    laws=(
        "valid codewords are a held selection of complete generated word support",
        "difference retains every changed canonical position and both labels",
        "detection requires all nonidentity registered images outside the codebook",
        "correction is equivalent to pairwise disjoint complete error-image supports",
        "a correctable received form decodes by exact unique source membership without a prior",
    ),
    induction_base="One registered error action generates one image per codeword; detection and support disjointness are exhaustively checked.",
    induction_step=(
        "Adding one error action appends its exact image to every affected codeword family. Detection checks valid-word "
        "membership and correction checks every newly possible intersection with all other source families."
    ),
    boundary_exclusions=(
        "no stochastic error model",
        "no floating distance or likelihood threshold",
        "no unaccounted redundancy",
        "no asymptotic rate imported as a finite proof",
    ),
    witnesses=(
        Witness("support", "Two labels over three positions generate eight unique words.", len(_support) == 8 and len(set(_support)) == 8),
        Witness("difference", "The repetition codewords differ at all three retained positions.", len(difference_trace(*_repetition)) == 3),
        Witness("detection", "Every single-label change of a width-three repetition codeword lies outside the codebook.", detectable_code(_repetition, _labels)),
        Witness("correction", "The two complete single-label error-image supports are disjoint.", correctable_code(_repetition, _labels)),
        Witness("decoding", "A received b/a/a word belongs uniquely to the all-a source family.", decode_received(_repetition, _labels, ("b", "a", "a")) == ("unique-source", ("a", "a", "a"))),
        Witness("unprotected-control", "The one-position uncoded family cannot correct a single label change.", not correctable_code(_uncoded, _labels)),
    ),
    why=(
        "Coding theory must establish correction from complete structural error alternatives. A metric or probability "
        "may summarize a sealed code later but cannot select which received forms decode uniquely."
    ),
    derivation=(
        "Fold assembly supplies word support; noise supplies registered transformations and predecessor classes; "
        "compression supplies lawful redundancy; combinatorics exhausts image families. Eleven axes force finite "
        "detection and correction through exact support separation."
    ),
    check=(
        "Execute all 2,048 coding kernels, exhaust width-three word support and all single-label images, verify detection, "
        "correction and decoding, reject the unprotected code and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes exact finite classical coding for any explicitly registered error family. Quantum codes, "
        "fault tolerance and unbounded error thresholds belong to later branches."
    ),
    correspondence_terms=("block code", "Hamming distance", "error detection", "error correction", "repetition code"),
)
