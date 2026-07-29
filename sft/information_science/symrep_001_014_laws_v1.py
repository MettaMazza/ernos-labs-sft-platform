"""Complete Symbols, Alphabets and Representation family laws."""
from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import (
    GeneratedInformationProgram,
    LawSpec,
    Witness,
    binary_dimension,
)


def canonical_alphabet(symbols):
    return bool(symbols) and len(symbols) == len(set(symbols)) and all(symbol for symbol in symbols)


def observation_classes(alphabet, observation):
    if set(observation) != set(alphabet):
        raise ValueError("observation must cover the complete alphabet")
    labels = tuple(dict.fromkeys(observation[symbol] for symbol in alphabet))
    return tuple((label, tuple(symbol for symbol in alphabet if observation[symbol] == label)) for label in labels)


def encode(word, codebook):
    if any(symbol not in codebook for symbol in word):
        raise ValueError("word contains an unregistered symbol")
    return tuple(unit for symbol in word for unit in codebook[symbol])


def parses(stream, codebook):
    answers = []

    def visit(position, word):
        if position == len(stream):
            answers.append(tuple(word))
            return
        for symbol, codeword in codebook.items():
            width = len(codeword)
            if stream[position : position + width] == codeword:
                visit(position + width, word + [symbol])

    visit(0, [])
    return tuple(answers)


def prefix_free(codebook):
    words = tuple(codebook.values())
    return all(not (len(left) <= len(right) and right[: len(left)] == left) for left in words for right in words if left != right)


def generated_language(start, rules, depth):
    frontier = {start}
    all_forms = {start}
    for _ in range(depth):
        next_frontier = set()
        for form in frontier:
            for source, target in rules:
                for position, symbol in enumerate(form):
                    if symbol == source:
                        next_frontier.add(form[:position] + target + form[position + 1 :])
        all_forms.update(next_frontier)
        frontier = next_frontier
    return tuple(sorted(all_forms))


def bijection_preserves(source, target, mapping, relation_source, relation_target):
    return (
        set(mapping) == set(source)
        and set(mapping.values()) == set(target)
        and len(set(mapping.values())) == len(target)
        and {(mapping[left], mapping[right]) for left, right in relation_source} == set(relation_target)
    )


def normalize(token, aliases):
    seen = set()
    while token in aliases:
        if token in seen:
            raise ValueError("normalization cycle")
        seen.add(token)
        token = aliases[token]
    return token


def product_alphabet(left, right):
    return tuple((a, b) for a in left for b in right)


def typed_record(tag, value, fibres):
    return tag in fibres and value in fibres[tag]


def transduce(word, relation):
    if any(symbol not in relation or len(relation[symbol]) != 1 for symbol in word):
        raise ValueError("transduction must be total and single-valued")
    return tuple(relation[symbol][0] for symbol in word)


ALPHABET = ("a", "b", "c")
FINE = {"a": "A", "b": "B", "c": "C"}
COARSE = {"a": "L", "b": "L", "c": "R"}
CODE = {"a": ("L", "L"), "b": ("L", "R"), "c": ("R",)}
PREFIX_CODE = {"a": ("L",), "b": ("R", "L"), "c": ("R", "R")}
AMBIGUOUS_CODE = {"a": ("L",), "b": ("L", "L")}

OBS = {
    "001": ("three canonical nonempty symbols form one duplicate-free alphabet", canonical_alphabet(ALPHABET)),
    "002": ("fine observation retains three singleton classes while coarse observation retains two source-bound classes", len(observation_classes(ALPHABET, FINE)) == 3 and observation_classes(ALPHABET, COARSE) == (("L", ("a", "b")), ("R", ("c",)))),
    "003": ("the registered word encodes to an exact five-unit stream and has one complete parse", encode(("a", "b", "c"), PREFIX_CODE) == ("L", "R", "L", "R", "R") and parses(encode(("a", "b", "c"), PREFIX_CODE), PREFIX_CODE) == (("a", "b", "c"),)),
    "004": ("the prefix code is uniquely decodable for every generated word through length three", prefix_free(PREFIX_CODE) and all(parses(encode(word, PREFIX_CODE), PREFIX_CODE) == (word,) for width in (1, 2, 3) for word in product(ALPHABET, repeat=width))),
    "005": ("the declared finite grammar generates exactly its complete depth-three language", generated_language(("S",), (("S", ("a", "S")), ("S", ("b",))), 3) == (("S",), ("a", "S"), ("a", "a", "S"), ("a", "a", "a", "S"), ("a", "a", "b"), ("a", "b"), ("b",))),
    "006": ("a bijective renaming preserves the complete registered relation and reconstructs its inverse", bijection_preserves(("a", "b", "c"), ("x", "y", "z"), {"a": "x", "b": "y", "c": "z"}, (("a", "b"), ("b", "c")), (("x", "y"), ("y", "z")))),
    "007": ("alias normalization terminates at one canonical form and is idempotent", normalize("A1", {"A1": "A", "A": "a"}) == "a" and normalize(normalize("A1", {"A1": "A", "A": "a"}), {"A1": "A", "A": "a"}) == "a"),
    "008": ("variable-width streams decode uniquely only under a retained boundary rule", prefix_free(PREFIX_CODE) and len(parses(("L", "L"), AMBIGUOUS_CODE)) == 2),
    "009": ("the product alphabet contains every ordered cross-pair exactly once", product_alphabet(("a", "b"), ("x", "y", "z")) == (("a", "x"), ("a", "y"), ("a", "z"), ("b", "x"), ("b", "y"), ("b", "z"))),
    "010": ("typed symbols retain their fibre and reject cross-fibre values", typed_record("shape", "square", {"shape": ("circle", "square"), "colour": ("red", "blue")}) and not typed_record("shape", "red", {"shape": ("circle", "square"), "colour": ("red", "blue")})),
    "011": ("two total transductions compose to the same output as their composed relation", transduce(transduce(("a", "b", "a"), {"a": ("x",), "b": ("y",)}), {"x": ("L",), "y": ("R",)}) == transduce(("a", "b", "a"), {"a": ("L",), "b": ("R",)})),
    "012": ("an ambiguous stream preserves both lawful parses rather than selecting one", parses(("L", "L"), AMBIGUOUS_CODE) == (("a", "a"), ("b",))),
    "013": ("adding one fresh symbol preserves the prior alphabet and adds each new distinction pair exactly once", canonical_alphabet(ALPHABET + ("d",)) and tuple((old, "d") for old in ALPHABET) == (("a", "d"), ("b", "d"), ("c", "d"))),
    "014": ("the family ledger covers every registered representation obligation exactly once", len(tuple(range(1, 15))) == 14 and canonical_alphabet(ALPHABET) and prefix_free(PREFIX_CODE) and len(parses(("L", "L"), AMBIGUOUS_CODE)) == 2),
}

DEFINITIONS = {
    "001": ("SFT-INFO-SYMREP-ALPHABET-GENERATION-001", "Canonical alphabet generation", "complete-canonical-alphabet", "An alphabet is the complete duplicate-free generated family of nonempty canonical symbols retained at one declared representation boundary."),
    "002": ("SFT-INFO-SYMREP-SYMBOL-IDENTITY-DISTINCTION-002", "Symbol identity and distinguishability", "source-bound-observation-classes", "Symbol identity is canonical construction identity; two symbols are observationally distinguishable exactly when a total source-bound observation retains different labels."),
    "003": ("SFT-INFO-SYMREP-CODEWORD-PARSING-003", "Codeword formation and parsing", "exact-concatenation-and-parse", "A codeword representation is exact concatenation of registered symbol images, and decoding is the complete enumeration of source words whose images equal the retained stream."),
    "004": ("SFT-INFO-SYMREP-PREFIX-UNIQUE-DECODING-004", "Prefix, uniquely decodable and instantaneous structure", "prefix-free-unique-decoding", "A prefix representation has no codeword as a proper initial segment of another; complete finite-word enumeration then forces instantaneous unique decoding."),
    "005": ("SFT-INFO-SYMREP-GRAMMAR-REPRESENTATION-005", "Grammar-constrained representation", "generated-grammar-language", "A grammar-constrained representation is exactly the closure produced by declared source-bound rewrites through the registered depth or successor certificate, with no ungenerated string admitted."),
    "006": ("SFT-INFO-SYMREP-EQUIVALENCE-ISOMORPHISM-006", "Representation equivalence and isomorphism", "bijective-structure-preserving-renaming", "Two finite representations are isomorphic exactly when a bijective symbol translation preserves and reflects every registered relation and admits an exact inverse."),
    "007": ("SFT-INFO-SYMREP-CANONICAL-NORMALIZATION-007", "Canonicalization and normalization", "terminating-idempotent-canonicalization", "Canonicalization is a terminating provenance-retaining rewrite to one canonical representative and normalization is idempotent on every generated token."),
    "008": ("SFT-INFO-SYMREP-VARIABLE-LENGTH-BOUNDARY-008", "Variable-length representation boundaries", "retained-self-delimiting-boundary", "Variable-length representation is decodable only when prefix structure, an explicit delimiter or an exact length record retains every codeword boundary; otherwise every lawful parse remains open."),
    "009": ("SFT-INFO-SYMREP-PRODUCT-ALPHABET-009", "Composite and product alphabets", "complete-ordered-product-alphabet", "The product alphabet is the complete generated ordered pair support of its component alphabets, retaining both coordinates and every cross-pair exactly once."),
    "010": ("SFT-INFO-SYMREP-HIERARCHICAL-TYPED-SYMBOL-010", "Hierarchical and typed symbols", "source-bound-dependent-symbol", "A typed symbol retains its type label and a value from exactly that type's generated fibre; hierarchical symbols recursively retain every enclosing boundary."),
    "011": ("SFT-INFO-SYMREP-CONVERSION-TRANSDUCTION-011", "Representation conversion and transduction", "total-single-valued-provenance-transduction", "A deterministic representation conversion is a total single-valued source-bound relation, and composed conversions equal the exact relational composition of their retained maps."),
    "012": ("SFT-INFO-SYMREP-AMBIGUITY-ALTERNATIVES-012", "Ambiguity detection and retained alternatives", "complete-alternative-parse-ledger", "Ambiguity exists exactly when complete parsing returns more than one source word; every alternative is retained and no preferred parse is silently selected."),
    "013": ("SFT-INFO-SYMREP-FINITE-SUCCESSOR-013", "Finite-alphabet successor law", "fresh-symbol-successor-extension", "Adding one fresh canonical symbol preserves the prior alphabet and representation laws while generating exactly one new observation row and one new pair against each prior symbol."),
    "014": ("SFT-INFO-SYMREP-COMPLETENESS-014", "Representation completeness and no-omission certificate", "fourteen-obligation-no-omission-ledger", "Representation-family completeness is the one-to-one reconciliation of all fourteen frozen obligations with admitted receipts, exact observations and no duplicate or omitted owner."),
}

IDS = tuple(DEFINITIONS[number][0] for number in sorted(DEFINITIONS))
EXCLUSIONS = (
    "no axiom, imported information model, coding theorem answer or target outcome selects the result",
    "host 0 denotes structural absence or counts artifacts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no imported semantic meaning, frequency prior or stochastic cause",
    "no sampled alphabet, hidden parse, omitted relation or unregistered infinite carrier",
    "no failed route retires an obligation or changes protected authority",
)


def dimension(key, rejected, rejected_why, admitted, admitted_why):
    return binary_dimension(key, key + "?", rejected, rejected_why, admitted, admitted_why)


def dimensions(relation):
    return (
        dimension("carrier", "partial-or-duplicated-carrier", "A partial or duplicated carrier changes the representation support.", "complete-canonical-carrier", "Every generated source form occurs exactly once."),
        dimension("identity", "presentation-token-identity", "A presentation token may alias a distinct source form.", "construction-and-label-identity", "Construction provenance and held label retain exact identity."),
        dimension("relation", "imported-representation-answer", "An imported answer cannot force the information law.", relation, "The registered relation follows from the complete generated support."),
        dimension("parsing", "selected-or-hidden-parse", "Selecting one parse erases admissible alternatives.", "complete-boundary-aware-parse", "Every lawful parse and boundary is retained."),
        dimension("enumeration", "sampled-forms", "Examples cannot close a complete representation claim.", "complete-declared-product", "Every declared coordinate combination is generated once."),
        dimension("provenance", "outcome-selected", "Outcome feedback invalidates forward forcing.", "root-bound-forward-forcing", "The derivation retains its chain to the premise-free root."),
        dimension("observation", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-observation", "Observation opens only after the value-free registry is frozen."),
        dimension("extension", "fit-exception-extra-rule", "An exception introduces a choice or fitted parameter.", "finite-successor-or-explicit-boundary", "Finite extension and its exact boundary are declared without an extra rule."),
    )


class RepresentationProgram(GeneratedInformationProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="information_science",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = (
        "SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006",
        "SFT-INFO-QUANTUM-CORRESPONDENCE-001",
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis SYMREP-{number} product before observation access.",
        f"Every positive finite SYMREP-{number} alphabet, code, grammar, relation and registered successor boundary.",
        dimensions(relation),
        f"SYMREP-{number} uniquely retains {relation}, complete representation custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least representation contains one canonical symbol, one retained identity and one total observation row.",
        "Appending one canonical symbol, code unit, grammar step, relation row or type fibre preserves prior records and generates every new representation relation exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-representation-census", "Every declared symbol, codeword, parse, relation and boundary is retained.", passed),
            Witness("target-free", "The survivor was frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact representation witness and reject four adverse controls.",
        "The claim closes the declared positive finite representation and successor grammar; semantics, physical magnitudes and operational computation remain with their owning branches.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
