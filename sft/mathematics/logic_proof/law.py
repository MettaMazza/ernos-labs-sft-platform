"""Force finite formal logic and proof from distinguished forms and exact traces."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-LOGIC-PROOF-001"


@dataclass(frozen=True)
class Proposition:
    form: str
    orientation: str

    def __post_init__(self) -> None:
        if not self.form or self.orientation not in ("held", "complementary-held"):
            raise ValueError("a proposition requires a canonical form and one held orientation")


@dataclass(frozen=True)
class ProofStep:
    premises: tuple[Proposition, ...]
    conclusion: Proposition
    rule: str

    def __post_init__(self) -> None:
        if not self.premises or not self.rule:
            raise ValueError("a proof step retains its nonempty premises and registered rule")


def denied(proposition: Proposition) -> Proposition:
    orientation = "complementary-held" if proposition.orientation == "held" else "held"
    return Proposition(proposition.form, orientation)


def conjunction(left: Proposition, right: Proposition) -> tuple[str, Proposition, Proposition]:
    return ("joint-complete", left, right)


def disjunction(left: Proposition, right: Proposition, held: Proposition) -> tuple[str, Proposition, tuple[Proposition, Proposition]]:
    if held not in (left, right):
        raise ValueError("a disjunction witness must hold one generated alternative")
    return ("held-alternative", held, (left, right))


def proof_is_valid(
    premises: tuple[Proposition, ...],
    steps: tuple[ProofStep, ...],
    rules: tuple[tuple[str, tuple[Proposition, ...], Proposition], ...],
) -> bool:
    available = list(premises)
    for step in steps:
        if any(premise not in available for premise in step.premises):
            return False
        if (step.rule, step.premises, step.conclusion) not in rules:
            return False
        available.append(step.conclusion)
    return True


def consistent(admitted: tuple[Proposition, ...]) -> bool:
    return all(denied(proposition) not in admitted for proposition in admitted)


def grammar_complete(
    generated: tuple[Proposition, ...],
    decided: tuple[Proposition, ...],
) -> bool:
    return len(set(generated)) == len(generated) and all(
        proposition in decided or denied(proposition) in decided for proposition in generated
    )


_p = Proposition("P", "held")
_q = Proposition("Q", "held")
_rule = ("P-to-Q", (_p,), _q)
_step = ProofStep((_p,), _q, "P-to-Q")


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite logic, inference and proof boundaries",
    statement=(
        "An admitted proposition is a canonical distinguished form with a held orientation; denial is the retained "
        "complementary orientation, not a negative number. Conjunction retains joint proofs, disjunction retains a "
        "chosen generated branch and its alternatives, implication is a registered premise-to-conclusion transition, "
        "and a proof is a complete dependency trace of accepted rules. Consistency, soundness and completeness are "
        "machine-checkable only relative to the exact registered finite grammar and rule set."
    ),
    dependencies=(
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule=(
        "Generate the complete product of proposition identity, denial, conjunction, disjunction, implication, "
        "inference provenance, consistency, soundness, grammar completeness and extra-logical status."
    ),
    grammar_boundary=(
        "All propositions and finite proofs generated from canonical forms, two held orientations, joint and "
        "alternative constructions, registered inference transitions and complete dependency traces."
    ),
    dimensions=(
        binary_dimension("proposition", "What fixes a proposition?", "presentation-sentence", "A sentence presentation can alias or hide the judged form.", "canonical-distinguished-form", "The exact generated form is the proposition identity."),
        binary_dimension("denial", "What fixes denial?", "negative-truth-value", "A negative magnitude is outside the admitted domain.", "complementary-held-orientation", "Denial retains the same form with the other exact fibre orientation."),
        binary_dimension("conjunction", "What proves a conjunction?", "single-side-proof", "One side cannot establish the joint claim.", "joint-complete-proof", "Both constituent proof traces are retained together."),
        binary_dimension("disjunction", "What proves a disjunction?", "unidentified-choice", "An unidentified choice erases which alternative is supported.", "held-alternative-with-support", "The held branch and complete generated alternative family are retained."),
        binary_dimension("implication", "What fixes implication?", "truth-table-import", "A borrowed table installs conventional logical values.", "proof-carrying-transition", "A registered rule maps exact premises to an exact conclusion."),
        binary_dimension("inference", "What fixes a proof?", "conclusion-only", "A bare conclusion erases its premises and rules.", "complete-dependency-trace", "Every step retains available premises, rule identity and conclusion."),
        binary_dimension("consistency", "What fixes consistency?", "assumed-consistent", "An assertion does not search for opposed admitted orientations.", "no-opposed-admission", "No form and its complementary orientation are jointly admitted."),
        binary_dimension("soundness", "What fixes soundness?", "authority-or-name", "Authority cannot replace validation against registered rules.", "rule-and-witness-preservation", "Every accepted step matches a registered source-bound rule and preserves its witnesses."),
        binary_dimension("completeness", "When may completeness be claimed?", "unbounded-global-claim", "A finite proof kernel cannot establish an ungenerated universal domain.", "registered-grammar-exhaustion", "Every proposition in the exact generated grammar has its declared decision evidence."),
        binary_dimension("addition", "Is another logical axiom added?", "extra-logical-axiom", "An extra axiom is not supplied by the canonical form and rule traces.", "no-extra-logical-axiom", "All admitted inference is registered and witnessed."),
    ),
    exact_result=(
        "The logic/proof kernel is canonical distinguished propositions, complementary held denial, joint and held "
        "alternative proof forms, proof-carrying implication, complete inference traces, explicit consistency and "
        "soundness, and completeness only over the exhausted registered grammar."
    ),
    laws=(
        "denial changes held orientation while preserving proposition identity",
        "conjunction and disjunction retain their complete source proof structure",
        "an implication is admitted through a registered proof-carrying transition",
        "a valid proof is replayable step by step from its premises and rule registry",
        "completeness is always indexed by an explicit generated grammar boundary",
    ),
    induction_base="One proposition form and its two orientations provide the first decidable grammar cell.",
    induction_step=(
        "Adding one proposition or rule generates its complementary orientation, joint and alternative combinations, "
        "and all new premise tuples. Consistency and proof replay are rechecked for precisely those new forms and steps."
    ),
    boundary_exclusions=(
        "no imported truth-value arithmetic",
        "no negative truth magnitude",
        "no authority-based proof admission",
        "no global completeness beyond a generated grammar",
    ),
    witnesses=(
        Witness("held-denial", "Denial preserves P while changing only its held orientation.", denied(_p) == Proposition("P", "complementary-held") and denied(denied(_p)) == _p),
        Witness("joint-proof", "Conjunction retains both exact constituent proofs.", conjunction(_p, _q) == ("joint-complete", _p, _q)),
        Witness("held-disjunction", "Disjunction retains the supported branch and both alternatives.", disjunction(_p, _q, _p) == ("held-alternative", _p, (_p, _q))),
        Witness("proof-replay", "The registered P-to-Q step replays from its available premise.", proof_is_valid((_p,), (_step,), (_rule,))),
        Witness("tampered-rule-control", "Changing the rule identity invalidates the same conclusion trace.", not proof_is_valid((_p,), (ProofStep((_p,), _q, "unregistered"),), (_rule,))),
        Witness("consistency", "P and Q are consistent, while P and its held denial are not.", consistent((_p, _q)) and not consistent((_p, denied(_p)))),
        Witness("bounded-completeness", "Both registered proposition forms have explicit held decisions.", grammar_complete((_p, _q), (_p, _q))),
    ),
    why=(
        "Every branch depends on distinguishable valid and invalid derivations. The proof law makes admission "
        "mechanical while preventing conventional logical axioms or institutional authority from entering silently."
    ),
    derivation=(
        "Canonical forms supply proposition identity; held fibres supply opposed orientations; discrete relations "
        "supply rules; order supplies proof-strength relations. Ten choices force the replayable finite proof kernel."
    ),
    check=(
        "Execute all 1,024 kernels, verify held denial, conjunction and disjunction provenance, replay a registered "
        "proof, reject a tampered rule, check consistency and bounded completeness, then regenerate independently."
    ),
    limitations=(
        "This closes finite generated proof theory. Computability, self-reference, undecidability and incompleteness "
        "boundaries require the later formal-computation branch and are not claimed here."
    ),
    correspondence_terms=("proposition", "negation", "conjunction", "disjunction", "implication", "proof", "soundness", "completeness"),
)
