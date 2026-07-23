"""Force symbols, observation classes and exact distinguishability."""

from __future__ import annotations

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-SYMBOL-DISTINCTION-001"
Symbol = tuple[str, str]
Observation = tuple[tuple[Symbol, str], ...]


def canonical_alphabet(*symbols: Symbol) -> tuple[Symbol, ...]:
    if not symbols or len(set(symbols)) != len(symbols):
        raise ValueError("an alphabet requires distinct canonical symbol forms")
    if any(not form or not label for form, label in symbols):
        raise ValueError("each symbol retains a canonical form and held label")
    return symbols


def validate_observation(alphabet: tuple[Symbol, ...], observation: Observation) -> bool:
    sources = tuple(source for source, _ in observation)
    return (
        bool(alphabet)
        and len(observation) == len(alphabet)
        and len(set(sources)) == len(sources)
        and set(sources) == set(alphabet)
        and all(label for _, label in observation)
    )


def observed_label(observation: Observation, symbol: Symbol) -> str:
    matches = tuple(label for source, label in observation if source == symbol)
    if len(matches) != 1:
        raise ValueError("observation must classify the symbol exactly once")
    return matches[0]


def distinguishable(observation: Observation, left: Symbol, right: Symbol) -> bool:
    if left == right:
        return False
    return observed_label(observation, left) != observed_label(observation, right)


def observation_classes(
    alphabet: tuple[Symbol, ...], observation: Observation
) -> tuple[tuple[str, tuple[Symbol, ...]], ...]:
    if not validate_observation(alphabet, observation):
        raise ValueError("observation is not total and source-bound")
    labels = tuple(dict.fromkeys(observed_label(observation, symbol) for symbol in alphabet))
    return tuple(
        (label, tuple(symbol for symbol in alphabet if observed_label(observation, symbol) == label))
        for label in labels
    )


def distinction_ledger(alphabet: tuple[Symbol, ...], observation: Observation):
    pairs = tuple(
        (left, right)
        for left_position, left in enumerate(alphabet)
        for right in alphabet[left_position + 1 :]
    )
    return (
        tuple(pair for pair in pairs if distinguishable(observation, *pair)),
        tuple(pair for pair in pairs if not distinguishable(observation, *pair)),
    )


_a = ("form-a", "held-a")
_b = ("form-b", "held-b")
_c = ("form-c", "held-c")
_alphabet = canonical_alphabet(_a, _b, _c)
_fine = ((_a, "seen-a"), (_b, "seen-b"), (_c, "seen-c"))
_coarse = ((_a, "seen-left"), (_b, "seen-left"), (_c, "seen-right"))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact symbols, observation classes and distinguishability",
    statement=(
        "An admitted symbol is a canonical generated form with a retained held label inside a complete canonical "
        "alphabet. Observation is a total single-valued source-bound classification. Two symbols are distinguishable "
        "exactly when their retained observation labels differ; symbols sharing one observation image remain distinct "
        "microforms but belong to one closed observation class. Every retained and closed distinction is recorded."
    ),
    dependencies=(
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-LOGIC-PROOF-001",
    ),
    generation_rule=(
        "Generate the complete product of alphabet coverage, symbol identity, held label, observation coverage, "
        "observation single-valuedness, distinction rule, closed-class retention, finite generality and extra-symbol status."
    ),
    grammar_boundary=(
        "All finite symbol systems generated from canonical Fold forms, held labels, complete alphabets, total "
        "observation relations and exact retained/closed pair ledgers."
    ),
    dimensions=(
        binary_dimension("alphabet", "What fixes the symbol carrier?", "partial-or-duplicated-alphabet", "Omission or duplication changes the possible symbol family.", "complete-canonical-alphabet", "Every generated symbol form occurs once."),
        binary_dimension("identity", "What fixes symbol identity?", "presentation-token", "A presentation token may alias distinct generated forms.", "canonical-form-identity", "The complete construction trace fixes exact symbol identity."),
        binary_dimension("label", "How is a symbol held apart?", "unlabelled-form", "Without a retained label the selected fibre identity is unavailable.", "retained-held-label", "The symbol carries its exact held fibre label."),
        binary_dimension("observation", "What fixes observation coverage?", "partial-observation", "A missing symbol has no declared observation class.", "total-source-bound-observation", "Every alphabet member has one retained observation row."),
        binary_dimension("image", "How many images may one symbol have?", "multivalued-image", "Multiple unheld images do not identify the observation made.", "single-retained-image", "Each source symbol has exactly one held observation label."),
        binary_dimension("distinction", "What makes two symbols distinguishable?", "assumed-or-visual-difference", "Presentation difference does not establish retained observational separation.", "different-observation-labels", "The observation relation retains distinct images for the two source forms."),
        binary_dimension("closure", "What happens when images merge?", "source-identity-erased", "Erasing sources prevents an exact account of closed distinctions.", "closed-class-with-microforms", "Merged symbols remain as exact source members of one observation class."),
        binary_dimension("generality", "What closes every finite alphabet?", "sampled-alphabets", "Examples do not establish extension to a fresh symbol.", "alphabet-successor", "A fresh canonical symbol adds one row and all new distinction pairs."),
        binary_dimension("addition", "Is another symbol rule added?", "extra-symbol-semantics", "Imported meaning or frequency is not supplied by form and observation.", "no-extra-symbol-semantics", "Identity and distinction use only generated forms, labels and observation."),
    ),
    exact_result=(
        "The symbol kernel is a complete canonical held-labelled alphabet, total single-valued observation, exact "
        "different-image distinguishability, retained closed classes, successor generality and no imported semantics."
    ),
    laws=(
        "symbol identity is canonical construction identity plus retained held label",
        "observation classes partition the complete alphabet without changing microform identity",
        "distinguishability is symmetric and irreflexive on exact symbol pairs",
        "coarsening closes distinctions only by merging observation images",
        "the retained/closed pair ledgers exhaust every generated unordered symbol pair",
    ),
    induction_base="One canonical symbol has one observation row and no nonidentity pair distinction.",
    induction_step=(
        "Adding one fresh canonical symbol adds exactly one source-bound observation row and one pair with every prior "
        "symbol. Each new pair is classified once as retained or closed by equality of its two observation labels."
    ),
    boundary_exclusions=(
        "no imported semantic meaning",
        "no frequency or probability prior",
        "no presentation alias replacing canonical identity",
        "no ungenerated infinite alphabet",
    ),
    witnesses=(
        Witness("total-observation", "The fine observation classifies every symbol exactly once.", validate_observation(_alphabet, _fine)),
        Witness("fine-distinction", "Fine observation retains every nonidentity pair distinction.", len(distinction_ledger(_alphabet, _fine)[0]) == 3 and not distinction_ledger(_alphabet, _fine)[1]),
        Witness("coarse-closure", "Coarse observation closes only the a/b distinction while retaining both microforms.", distinction_ledger(_alphabet, _coarse)[1] == (((_a, _b)),)),
        Witness("symmetry", "Swapping a distinguished pair does not change its status.", distinguishable(_fine, _a, _b) == distinguishable(_fine, _b, _a)),
        Witness("irreflexivity", "A canonical symbol is not distinguished from itself.", not distinguishable(_fine, _a, _a)),
        Witness("class-retention", "The coarse class retains both exact left microforms.", observation_classes(_alphabet, _coarse)[0] == ("seen-left", (_a, _b))),
    ),
    why=(
        "Information cannot be quantified before the model derives what a symbol is and exactly when two possible "
        "forms remain distinguishable to an observation. Imported alphabets or meanings would select that boundary."
    ),
    derivation=(
        "Canonical form enforcement supplies exact identity; discrete relations supply total classification; logic "
        "supplies distinguished held orientations; the measurement boundary fixes one-way observation. Exhausting "
        "nine structural questions forces the symbol/observation-class kernel."
    ),
    check=(
        "Execute all 512 symbol kernels, verify totality, fine and coarse ledgers, symmetry, irreflexivity and retained "
        "microforms, run four adverse controls and independently regenerate the product."
    ),
    limitations=(
        "This theorem closes finite structural symbols and observation-relative distinction. It does not assign "
        "linguistic meaning, occurrence frequency or information quantity; those require downstream laws."
    ),
    correspondence_terms=("symbol", "alphabet", "observation", "equivalence class", "distinguishability"),
)
