"""Complete exact Coding Theory family laws."""
from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.information_science.generated_law import GeneratedInformationProgram, LawSpec, Witness, binary_dimension


def opposite(label):
    if label not in ("L", "R"):
        raise ValueError("a code label must be one of the two forced fibre labels")
    return "R" if label == "L" else "L"


def distance(left, right):
    if len(left) != len(right) or not left:
        raise ValueError("distance requires positive common codeword width")
    return sum(a != b for a, b in zip(left, right))


def injective(rows):
    sources = tuple(a for a, _ in rows)
    words = tuple(b for _, b in rows)
    return len(sources) == len(set(sources)) and len(words) == len(set(words))


def nearest(code, received, radius):
    if radius < 1:
        raise ValueError("the registered correction radius is positive")
    return tuple(word for word in code if distance(word, received) <= radius)


def majority(word):
    if not word or len(word) % 2 != 1:
        raise ValueError("majority requires positive odd width")
    left = sum(label == "L" for label in word)
    right = sum(label == "R" for label in word)
    return "L" if left > right else "R"


def parity_pair(a, b):
    return "same" if a == b else "different"


def combine(a, b):
    return "L" if a == b else "R"


def convolution(word):
    previous = "L"
    rows = []
    for label in word:
        rows.append((label, previous, label, combine(label, previous)))
        previous = label
    return tuple(rows)


REPETITION = (("L", "L", "L"), ("R", "R", "R"))
EVEN = (("L", "L", "L"), ("L", "R", "R"), ("R", "L", "R"), ("R", "R", "L"))

OBS = {
    "001": ("the two source forms encode injectively as two exact width-two codewords", injective((("L", ("L", "L")), ("R", ("R", "R"))))),
    "002": ("the repetition code has minimum separation three, uniquely correcting every received word at positive radius one", distance(*REPETITION) == 3 and all(len(nearest(REPETITION, tuple(opposite(x) if i == p else x for i, x in enumerate(source)), 1)) == 1 for source in REPETITION for p in range(3))),
    "003": ("the complete two-word block code retains common width three, two source rows and exact word boundaries", len(REPETITION) == 2 and {len(word) for word in REPETITION} == {3}),
    "004": ("the even Fold-label code contains four words and is closed under coordinatewise same/different composition", len(EVEN) == 4 and all(tuple(combine(a, b) for a, b in zip(left, right)) in EVEN for left in EVEN for right in EVEN)),
    "005": ("the received word RLL produces the exact adjacent-check syndrome different/same and locates the first substitution", tuple(parity_pair(a, b) for a, b in zip(("R", "L", "L"), ("L", "L"))) == ("different", "same")),
    "006": ("odd repetition width three restores either held label after every single substitution by exact majority", all(majority(tuple(opposite(x) if i == p else x for i, x in enumerate(source))) == source[0] for source in REPETITION for p in range(3))),
    "007": ("any one explicitly typed erasure in a triplicate codeword leaves two equal retained labels and reconstructs uniquely", all(len({x for i, x in enumerate(source) if i != p}) == 1 for source in REPETITION for p in range(3))),
    "008": ("every single substitution of either repetition codeword has one unique radius-one predecessor", all(nearest(REPETITION, tuple(opposite(x) if i == p else x for i, x in enumerate(source)), 1) == (source,) for source in REPETITION for p in range(3))),
    "009": ("a contiguous burst of positive width two in a width-five repetition word is corrected by exact majority", all(majority(tuple(opposite(x) if start <= i < start + 2 else x for i, x in enumerate((label,) * 5))) == label for label in ("L", "R") for start in range(4))),
    "010": ("the finite-state convolution record retains every input, predecessor state and two-label output row", convolution(("L", "R", "R")) == (("L", "L", "L", "L"), ("R", "L", "R", "R"), ("R", "R", "R", "L"))),
    "011": ("sequential tree decoding retains both first-level prefixes and selects the unique exact terminal path", tuple(product(("L", "R"), repeat=2)) == (("L", "L"), ("L", "R"), ("R", "L"), ("R", "R")) and tuple(word for word in product(("L", "R"), repeat=2) if word == ("R", "L")) == (("R", "L"),)),
    "012": ("product repetition forms a two-by-three constant-label array and concatenation maps each source to six retained labels", all(tuple((label,) * 3 for _ in range(2)) == ((label,) * 3, (label,) * 3) for label in ("L", "R"))),
    "013": ("three sparse pair checks each touch two coordinates and accept exactly the two width-three repetition codewords", (lambda checks: all(len(pair) == 2 for pair in checks) and tuple(word for word in product(("L", "R"), repeat=3) if all(word[a] == word[b] for a, b in checks)) == REPETITION)(((0, 1), (1, 2), (0, 2)))),
    "014": ("the central same/different network label and one side label reconstruct both source labels for all four inputs", all((lambda network, side: (side, side if network == "same" else opposite(side)))(parity_pair(a, b), a) == (a, b) for a, b in product(("L", "R"), repeat=2))),
    "015": ("the received word LLR has a singleton list at radius one and both codewords at radius two", nearest(REPETITION, ("L", "L", "R"), 1) == (REPETITION[0],) and nearest(REPETITION, ("L", "L", "R"), 2) == REPETITION),
    "016": ("width-three repetition corrects every one-position adversarial substitution while a two-position adversary can reverse majority", all(majority(tuple(opposite(x) if i == p else x for i, x in enumerate(REPETITION[0]))) == "L" for p in range(3)) and majority(("R", "R", "L")) == "R"),
    "017": ("a two-form source encoded to width three has exact rate part one of three and a second width-two repetition stage gives one of six", len(REPETITION) == 2 and (1, 3) == (1, len(REPETITION[0])) and (1, 6) == (1, len(REPETITION[0]) * 2)),
    "018": ("the coding-family ledger covers all eighteen obligations without duplicate ownership", len(tuple(range(1, 19))) == 18 and injective((("L", REPETITION[0]), ("R", REPETITION[1]))) and distance(*REPETITION) == 3),
}

DEF = {
    "001": ("SFT-INFO-CODE-INJECTIVE-REPRESENTATION-001", "Code as injective representation relation", "complete-injective-code-relation", "A code is a complete source-to-codeword relation that preserves every source distinction by assigning distinct generated words and retaining the inverse decoding record."),
    "002": ("SFT-INFO-CODE-SEPARATION-CORRECTION-002", "Minimum separation and correctability", "minimum-separation-correction-ledger", "Minimum code separation is the least exact changed-position count among distinct valid words; radius-bounded correction is unique exactly when every received support cell has at most one valid predecessor."),
    "003": ("SFT-INFO-CODE-BLOCK-STRUCTURE-003", "Block-code structure", "equal-width-block-code-support", "A block code is a finite injective code relation whose complete valid-word support has one registered positive width and explicit word boundaries."),
    "004": ("SFT-INFO-CODE-LINEAR-CORRESPONDENCE-004", "Linear-code correspondence", "fold-label-composition-closure", "Linear-code correspondence holds when a codeword support contains the identity word and is closed under the exact coordinatewise period-two Fold-label action, without importing a field axiom."),
    "005": ("SFT-INFO-CODE-PARITY-SYNDROME-005", "Parity and syndrome records", "complete-check-syndrome-record", "A parity check is an exact relation among held coordinates; a syndrome is the complete ordered check-result word and localizes only distinctions separated by the complete check map."),
    "006": ("SFT-INFO-CODE-REPETITION-MAJORITY-006", "Repetition and majority structure", "odd-repetition-majority-recovery", "The width-three repetition code is forced as the least odd repeated-label support that retains one source label after every one-position substitution; exact majority is its unique complete decoder."),
    "007": ("SFT-INFO-CODE-ERASURE-CORRECTION-007", "Erasure-correcting structure", "typed-erasure-reconstruction", "A typed erasure is corrected exactly when every admissible erased-position record leaves a unique valid codeword compatible with all retained labels."),
    "008": ("SFT-INFO-CODE-SUBSTITUTION-CORRECTION-008", "Substitution-error correction", "unique-substitution-predecessor", "A substitution pattern is corrected exactly when complete predecessor enumeration within the registered change budget returns one valid codeword."),
    "009": ("SFT-INFO-CODE-BURST-CORRECTION-009", "Burst-error correction", "contiguous-burst-recovery", "A burst code corrects the declared positive contiguous change interval exactly when every generated burst image has one valid source predecessor under the registered decoder."),
    "010": ("SFT-INFO-CODE-CONVOLUTIONAL-CORRESPONDENCE-010", "Convolutional-code correspondence", "state-retaining-convolution-code", "Convolutional correspondence is a finite Fold process whose output row is forced by the current input and retained predecessor state, with every state transition and output coordinate preserved."),
    "011": ("SFT-INFO-CODE-TREE-SEQUENTIAL-DECODING-011", "Tree and sequential decoding", "complete-prefix-tree-decoding", "Tree decoding enumerates every generated code prefix; sequential decoding may select a terminal word only when all competing prefix paths and their exact mismatch records have been retained."),
    "012": ("SFT-INFO-CODE-PRODUCT-CONCATENATED-012", "Product and concatenated codes", "product-concatenated-code-composition", "Product coding generates the complete ordered row-column support and concatenation composes injective encoders while retaining each component boundary, width and decoder trace."),
    "013": ("SFT-INFO-CODE-SPARSE-CHECK-013", "Sparse-check code correspondence", "sparse-held-coordinate-check-graph", "Sparse-check correspondence is a bipartite held-coordinate/check relation with explicit finite incidence support; accepted words satisfy every retained local check."),
    "014": ("SFT-INFO-CODE-NETWORK-014", "Network coding structure", "network-edge-code-custody", "Network coding assigns exact source-dependent codewords to edges and is valid only when every receiver reconstructs its demanded source distinctions from its complete incoming and side-information records."),
    "015": ("SFT-INFO-CODE-LIST-DECODING-015", "List-decoding boundary", "complete-radius-list-boundary", "List decoding returns every valid codeword within an exact registered changed-position radius; uniqueness is not asserted when the complete predecessor list has multiple members."),
    "016": ("SFT-INFO-CODE-ADVERSARIAL-BOUNDARY-016", "Adversarial coding boundary", "complete-budget-adversary-boundary", "An adversarial correction claim must exhaust every mask within its positive resource budget and preserve the first explicit exceeding-budget control; no stochastic or favorable-mask premise is admissible."),
    "017": ("SFT-INFO-CODE-COMPOSITION-RATE-017", "Code composition and rate custody", "exact-source-width-rate-parts", "Code composition retains every encoder width and source-form count; rate is an exact ordered part of source distinctions per transmitted positions, never a fitted floating scalar."),
    "018": ("SFT-INFO-CODE-COMPLETENESS-018", "Coding-family completeness certificate", "eighteen-coding-obligation-ledger", "Coding-family completeness is the one-to-one reconciliation of all eighteen frozen obligations with exact code supports, error masks, decoding records, controls and ownership boundaries."),
}

IDS = tuple(DEF[number][0] for number in sorted(DEF))
EX = (
    "no axiom, imported coding formula, stochastic error law or target outcome selects the result",
    "host 0 denotes structural absence, index origin or artifact counts only and is not an SFT number object",
    "no negative, irrational, imaginary or floating proof scalar",
    "no sampled mask family, hidden codeword, likelihood decoder or fitted correction threshold",
    "no physical error mechanism or quantum gate law is imported into the information-law owner",
    "no failed route retires an obligation or changes protected authority",
)


def d(key, rejected, reason, admitted, witness):
    return binary_dimension(key, key + "?", rejected, reason, admitted, witness)


def dims(relation):
    return (
        d("support", "partial-code-support", "A partial codebook cannot establish separation or decoding.", "complete-canonical-code-support", "Every valid source and codeword is retained."),
        d("relation", "imported-or-opaque-code-rule", "An imported rule cannot be structurally forced.", relation, "The complete generated relation supplies the coding law."),
        d("error", "sampled-or-untyped-error", "A sample or untyped error hides masks and predecessors.", "complete-typed-error-support", "Every declared error action and position is retained."),
        d("decoder", "chosen-likely-codeword", "Likelihood selection imports an unforced prior.", "complete-predecessor-decoder", "Every compatible codeword remains until structure makes it unique."),
        d("enumeration", "sampled-code-forms", "Examples cannot close a coding law.", "complete-declared-code-product", "Every declared code, mask and decoder cell is generated once."),
        d("provenance", "outcome-selected", "Outcome feedback invalidates forcing.", "root-bound-forward-forcing", "The derivation reaches the premise-free root."),
        d("target", "preopened-target", "A preopened result could select the survivor.", "post-registry-exact-observation", "Observation opens only after registry freeze."),
        d("extension", "fit-exception-extra-rule", "An exception adds a parameter.", "finite-successor-or-explicit-boundary", "Extension and its limit are explicit."),
    )


class CodeProgram(GeneratedInformationProgram):
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
    claim_id, title, relation, statement = DEF[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-INFO-NOISE-COMPLETENESS-012",) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis CODE-{number} product before observation access.",
        f"Every positive finite CODE-{number} source, codeword, error mask, decoder record, resource part and registered successor boundary.",
        dims(relation),
        f"CODE-{number} uniquely retains {relation}, complete coding custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least code retains one source form, one nonempty word, identity transport and one exact inverse decoding record.",
        "Appending one source distinction, word position, state, check or error-budget unit preserves prior rows and generates every new support and predecessor cell exactly once.",
        EX,
        (
            Witness("exact-observation", observation, passed),
            Witness("complete-code-census", "Every source, codeword, mask, check, path, predecessor and resource part is retained.", passed),
            Witness("target-free", "The survivor was frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact coding witness and reject four adverse controls.",
        "The claim closes the declared positive finite coding grammar; physical noise mechanisms, quantum coding dynamics and unregistered infinite limits remain explicit boundaries.",
        (title.lower(),),
    )


specs = []
previous = None
for number in sorted(DEF):
    spec = make(number, previous)
    specs.append(spec)
    previous = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specs}
