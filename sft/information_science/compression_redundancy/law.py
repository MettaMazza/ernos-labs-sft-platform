"""Force lossless compression, redundancy and complete resource accounting."""

from __future__ import annotations

from itertools import product

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-COMPRESSION-REDUNDANCY-001"
Word = tuple[str, ...]
Dictionary = tuple[tuple[str, Word], ...]


def prefix_free(codewords: tuple[Word, ...]) -> bool:
    if not codewords or any(not word for word in codewords) or len(set(codewords)) != len(codewords):
        return False
    return all(
        not (len(left) < len(right) and right[: len(left)] == left)
        for left in codewords for right in codewords if left != right
    )


def reconstruct(dictionary: Dictionary, token_trace: tuple[str, ...]) -> Word:
    entries = dict(dictionary)
    if not entries or len(entries) != len(dictionary) or not token_trace or any(token not in entries for token in token_trace):
        raise ValueError("compressed description requires a complete dictionary and nonempty valid token trace")
    return tuple(cell for token in token_trace for cell in entries[token])


def description_resource_trace(dictionary: Dictionary, token_trace: tuple[str, ...]):
    reconstructed = reconstruct(dictionary, token_trace)
    dictionary_trace = tuple(("dictionary", label, *block) for label, block in dictionary)
    token_cells = tuple(("token", token) for token in token_trace)
    return {
        "dictionary": dictionary_trace,
        "tokens": token_cells,
        "reconstructed": reconstructed,
        "complete_resource": dictionary_trace + token_cells,
    }


def is_lossless_description(message: Word, dictionary: Dictionary, token_trace: tuple[str, ...]) -> bool:
    return bool(message) and reconstruct(dictionary, token_trace) == message


def redundant_positions(message: Word, dictionary: Dictionary, token_trace: tuple[str, ...]):
    if not is_lossless_description(message, dictionary, token_trace):
        raise ValueError("redundancy requires exact reconstruction")
    produced: list[tuple[str, str]] = []
    entries = dict(dictionary)
    for token in token_trace:
        produced.extend((token, cell) for cell in entries[token])
    return tuple(produced)


def fixed_support(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    if len(labels) < 2 or not positions:
        raise ValueError("support requires a distinction and nonempty positions")
    return tuple(tuple(word) for word in product(labels, repeat=len(positions)))


def shorter_nonempty_support(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    return tuple(
        tuple(word)
        for held_length in range(1, len(positions))
        for word in product(labels, repeat=held_length)
    )


def universal_shortening_impossible(labels: tuple[str, ...], positions: tuple[str, ...]) -> bool:
    full = fixed_support(labels, positions)
    short = shorter_nonempty_support(labels, positions)
    return len(short) < len(full)


_message = ("a", "b", "a", "b", "a", "b")
_dictionary = (("held-block", ("a", "b")),)
_tokens = ("held-block", "held-block", "held-block")


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact lossless compression and redundancy accounting",
    statement=(
        "Lossless compression is a complete description relation whose retained dictionary and token trace reconstruct "
        "the exact canonical message. Redundancy is a message distinction or occurrence reconstructible from retained "
        "description structure. Variable codewords are uniquely parseable only with a complete delimiter or prefix-free "
        "witness. Every dictionary and token resource is counted; no fixed complete word support can injectively map "
        "all its forms into the strictly shorter nonempty support."
    ),
    dependencies=(
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-OPTIMIZATION-001",
        "SFT-INFO-ENCODING-DECODING-001",
        "SFT-INFO-QUANTITY-001",
    ),
    generation_rule=(
        "Generate the complete product of message coverage, description provenance, exact reconstruction, parsing, "
        "redundancy witness, resource accounting, shortening status, optimization, generality and extra-compressor status."
    ),
    grammar_boundary=(
        "All finite lossless descriptions generated from canonical messages, retained dictionaries, token traces, "
        "exact decoders, unique parsing witnesses and complete positive resource traces."
    ),
    dimensions=(
        binary_dimension("message", "What fixes the source message?", "partial-message", "An omitted occurrence changes the reconstruction target.", "complete-canonical-message", "Every source occurrence remains in exact order."),
        binary_dimension("description", "What representation evidence is retained?", "opaque-short-string", "A short string without dictionary provenance cannot reconstruct the source.", "dictionary-and-token-trace", "Every reusable block and held token occurrence is retained."),
        binary_dimension("reconstruction", "What makes compression lossless?", "similar-output", "Similarity does not establish exact source identity.", "exact-decoder-equality", "Decoding reproduces the complete canonical message trace."),
        binary_dimension("parsing", "What makes variable codewords separable?", "ambiguous-concatenation", "One stream may admit several codeword parses.", "prefix-or-delimiter-witness", "A generated boundary makes the parse unique."),
        binary_dimension("redundancy", "What identifies redundancy?", "frequency-assumption", "Frequency alone does not prove reconstruction.", "reconstructible-occurrence-trace", "Omitted raw occurrences are generated exactly from retained description structure."),
        binary_dimension("resources", "What is counted as compressed size?", "payload-only", "Ignoring a dictionary or decoder hides required information.", "complete-description-resource", "Dictionary, tokens, boundaries and decoder identity are all retained."),
        binary_dimension("shortening", "Can every fixed-width message be shortened?", "universal-shortening-claim", "Strictly shorter support has fewer generated nonempty codewords than complete fixed support.", "pigeonhole-boundary", "At least one full-support message cannot receive a distinct strictly shorter codeword."),
        binary_dimension("optimization", "What selects a best description?", "tuned-score", "A floating objective or tie rule is unforced.", "complete-undominated-descriptions", "All exact descriptions are generated and every minimal resource trace tie is retained."),
        binary_dimension("generality", "What closes arbitrary finite repetition?", "sampled-messages", "Examples do not establish a fresh repeated token.", "token-successor", "Appending one retained token reconstructs exactly its registered dictionary block."),
        binary_dimension("addition", "Is another compression model added?", "extra-statistical-model", "A learned or fitted model can select the representation.", "no-extra-compression-model", "Only exact generated dictionaries, tokens and decoding are used."),
    ),
    exact_result=(
        "The compression kernel is exact message reconstruction from a uniquely parseable dictionary/token description, "
        "complete resource accounting, reconstructible redundancy, pigeonhole-limited shortening and no fitted model."
    ),
    laws=(
        "losslessness is exact equality of reconstructed and source canonical traces",
        "a reusable block is redundancy only when every replaced occurrence is reconstructible",
        "dictionary, parser and decoder resources belong to the complete description",
        "prefix freedom or an explicit delimiter is required for unique variable-word parsing",
        "no injective code can assign every complete fixed-width message a strictly shorter nonempty word",
    ),
    induction_base="One dictionary token reconstructs its one registered nonempty block and retains the complete description.",
    induction_step=(
        "Appending one valid held token appends exactly its dictionary block to the reconstructed message and one token "
        "cell to the resource trace. Exact reconstruction and parsing remain local and replayable."
    ),
    boundary_exclusions=(
        "no hidden learned model or trained weights",
        "no payload-only size claim",
        "no ambiguous variable-word parsing",
        "no universal lossless shortening claim",
    ),
    witnesses=(
        Witness("exact-reconstruction", "Three retained block tokens reconstruct the six-cell message exactly.", is_lossless_description(_message, _dictionary, _tokens)),
        Witness("resource-accounting", "The description retains one dictionary entry and all three token occurrences.", len(description_resource_trace(_dictionary, _tokens)["dictionary"]) == 1 and len(description_resource_trace(_dictionary, _tokens)["tokens"]) == 3),
        Witness("redundancy-provenance", "Every reconstructed raw cell retains the token and dictionary block that supplied it.", len(redundant_positions(_message, _dictionary, _tokens)) == len(_message)),
        Witness("prefix-control", "The witness prefix family parses uniquely while a prefix-containing family fails.", prefix_free((("a",), ("b", "a"), ("b", "b"))) and not prefix_free((("a",), ("a", "b")))),
        Witness("universal-bound", "Complete two-label width-three support cannot inject into all shorter nonempty words.", universal_shortening_impossible(("a", "b"), ("p1", "p2", "p3"))),
    ),
    why=(
        "Compression claims can hide information in a dictionary, parser, model or decoder. The law must force exact "
        "reconstruction and count every retained resource before shortening has scientific meaning."
    ),
    derivation=(
        "Encoding supplies exact decoders; information quantity supplies resource traces; combinatorics supplies full "
        "fixed and shorter supports; optimization retains all minimal descriptions. Ten axes force lossless reconstruction, "
        "complete accounting and the universal-shortening boundary."
    ),
    check=(
        "Execute all 1,024 compression kernels, reconstruct the witness message, account for dictionary and tokens, "
        "reject ambiguous prefixes, exhaust the fixed/short support boundary and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes finite structural compression. It does not assert a universal best compressor, a "
        "probability distribution or an asymptotic real-valued rate."
    ),
    correspondence_terms=("lossless compression", "redundancy", "prefix code", "dictionary coding", "pigeonhole bound"),
)
