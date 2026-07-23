"""Force exact encodings, decoders and declared loss classes."""

from __future__ import annotations

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-ENCODING-DECODING-001"
Codeword = tuple[str, ...]
Encoding = tuple[tuple[str, Codeword], ...]


def validate_encoding(
    source: tuple[str, ...], code_support: tuple[Codeword, ...], encoding: Encoding
) -> bool:
    origins = tuple(origin for origin, _ in encoding)
    return (
        bool(source)
        and bool(code_support)
        and len(set(source)) == len(source)
        and len(set(code_support)) == len(code_support)
        and len(encoding) == len(source)
        and set(origins) == set(source)
        and len(set(origins)) == len(origins)
        and all(codeword in code_support for _, codeword in encoding)
    )


def source_classes(source: tuple[str, ...], encoding: Encoding):
    codewords = tuple(dict.fromkeys(codeword for _, codeword in encoding))
    return tuple(
        (codeword, tuple(item for item in source if (item, codeword) in encoding))
        for codeword in codewords
    )


def exact_decoder(source: tuple[str, ...], encoding: Encoding):
    classes = source_classes(source, encoding)
    if any(len(members) != 1 for _, members in classes):
        return None
    return tuple((codeword, members[0]) for codeword, members in classes)


def decode(codeword: Codeword, decoder):
    matches = tuple(source for held, source in decoder if held == codeword)
    if len(matches) != 1:
        raise ValueError("decoding requires one retained source image")
    return matches[0]


def closed_distinctions(source: tuple[str, ...], encoding: Encoding):
    return tuple(
        (left, right)
        for left_position, left in enumerate(source)
        for right in source[left_position + 1 :]
        if next(code for item, code in encoding if item == left)
        == next(code for item, code in encoding if item == right)
    )


def compose_encodings(first: Encoding, second: tuple[tuple[Codeword, Codeword], ...]) -> Encoding:
    second_map = dict(second)
    if len(second_map) != len(second) or any(code not in second_map for _, code in first):
        raise ValueError("encoding composition requires a complete exact interface map")
    return tuple((source, second_map[code]) for source, code in first)


_source = ("a", "b", "c")
_support = (("held-a",), ("held-b",), ("held-c",))
_lossless = (("a", _support[0]), ("b", _support[1]), ("c", _support[2]))
_lossy = (("a", _support[0]), ("b", _support[0]), ("c", _support[2]))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact encoding, decoding and declared representational loss",
    statement=(
        "An admitted encoding is a total single-valued source-bound map from a complete canonical source alphabet "
        "into generated codeword support, retaining every source-to-code relation. Exact decoding exists exactly "
        "when every used codeword class contains one source and the decoder is the resulting left inverse. A many-to-one "
        "encoding is lawful only as declared lossy representation whose complete closed-source classes remain recorded."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
        "SFT-INFO-SYMBOL-DISTINCTION-001",
    ),
    generation_rule=(
        "Generate the complete product of source coverage, code support, encoding totality, single-valuedness, "
        "provenance, decoder law, exact/lossy status, composition, finite generality and extra-code status."
    ),
    grammar_boundary=(
        "All finite representations generated from complete canonical source alphabets, generated Fold codewords, "
        "total maps, inverse relations, retained source classes and exact interface composition."
    ),
    dimensions=(
        binary_dimension("source", "What fixes the encoded domain?", "partial-source", "An omitted source symbol has no representation row.", "complete-canonical-source", "Every source symbol occurs once in the registered domain."),
        binary_dimension("support", "What fixes possible codewords?", "free-code-token", "A free token has no generated Fold-word provenance.", "generated-code-support", "Every codeword is an exact generated held-label word."),
        binary_dimension("coverage", "How much of the source is encoded?", "partial-map", "A partial map leaves at least one source without a codeword.", "total-source-map", "Every source has one encoding row."),
        binary_dimension("image", "How many held codewords may one source receive?", "unheld-multiple-images", "Multiple images do not identify the codeword actually retained.", "single-retained-codeword", "Each source has exactly one held codeword image."),
        binary_dimension("provenance", "What representation evidence is kept?", "source-code-link-erased", "Erasing links prevents reconstruction of source classes.", "complete-source-code-relation", "Every exact source-to-code pair is retained."),
        binary_dimension("decoder", "What fixes exact decoding?", "guessed-preimage", "A used codeword can have several source predecessors.", "singleton-class-left-inverse", "Every used code class is singleton and the inverse map returns its source."),
        binary_dimension("loss", "How is a many-to-one encoding treated?", "silent-loss", "Silent merging falsely claims unavailable distinctions remain.", "declared-closed-source-classes", "Every merged source family is retained as an explicit loss class."),
        binary_dimension("composition", "When may encodings compose?", "presentation-concatenation", "Concatenation can join unequal code interfaces.", "complete-interface-map", "Every first-stage codeword has exactly one second-stage image."),
        binary_dimension("generality", "What closes arbitrary finite source size?", "sampled-codebooks", "Examples do not establish a fresh source row.", "source-successor", "A fresh source adds one exact encoding row and updates one code class."),
        binary_dimension("addition", "Is an external representation rule added?", "extra-code-convention", "A borrowed numeral or lexical convention can select the code.", "no-extra-code-convention", "Only generated code support and exact relations are used."),
    ),
    exact_result=(
        "The encoding kernel is complete source and generated code support with a total single-valued provenance "
        "relation, singleton-class left-inverse decoding, explicit loss classes, exact composition and no borrowed code."
    ),
    laws=(
        "every source symbol has exactly one retained codeword image",
        "lossless exact decoding exists if and only if used codeword classes are singleton",
        "many-to-one encoding closes exactly the distinctions inside its retained source classes",
        "decoder-after-lossless-encoder returns the original canonical source",
        "encoding composition preserves source provenance when every intermediate codeword is mapped",
    ),
    induction_base="One source symbol maps to one generated codeword and its singleton inverse decodes exactly.",
    induction_step=(
        "Adding one fresh source adds exactly one encoding pair. A fresh codeword preserves singleton decoding; a used "
        "codeword extends its closed source class and changes the representation status to declared lossy."
    ),
    boundary_exclusions=(
        "no imported binary numeral system",
        "no presentation-only token identity",
        "no silent many-to-one loss",
        "no infinite codebook as a completed object",
    ),
    witnesses=(
        Witness("lossless-total", "The witness lossless relation maps every source once into generated support.", validate_encoding(_source, _support, _lossless)),
        Witness("left-inverse", "The exact decoder reconstructs every lossless source.", exact_decoder(_source, _lossless) is not None and all(decode(code, exact_decoder(_source, _lossless)) == source for source, code in _lossless)),
        Witness("loss-detected", "The lossy relation has no exact decoder and retains the merged a/b class.", exact_decoder(_source, _lossy) is None and closed_distinctions(_source, _lossy) == (("a", "b"),)),
        Witness("class-ledger", "Every used lossy codeword retains its exact source members.", source_classes(_source, _lossy)[0] == (_support[0], ("a", "b"))),
        Witness("composition", "Complete code interface composition preserves each source relation.", compose_encodings(_lossless, tuple((word, word + ("next",)) for word in _support))[0] == ("a", ("held-a", "next"))),
    ),
    why=(
        "Information requires lawful representation before quantity, compression or channels can be discussed. "
        "Encoding must expose exactly which distinctions it preserves and which it closes."
    ),
    derivation=(
        "Fold assembly supplies generated codewords; symbol law supplies canonical sources and distinctions; discrete "
        "maps supply totality; compositional mathematics supplies exact interfaces. Ten structural axes force the "
        "total relation, inverse and declared-loss kernel."
    ),
    check=(
        "Execute all 1,024 encoding kernels, verify total lossless mapping, decoder left inverse, lossy-class retention "
        "and interface composition, run adverse controls and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes finite encoding and decoding structure. It does not yet assign code length value, "
        "compression optimality, channel reliability or correction power."
    ),
    correspondence_terms=("alphabet", "codeword", "encoder", "decoder", "injective code", "lossy representation"),
)
