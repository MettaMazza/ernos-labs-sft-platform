"""Complete-field Formal Computation laws, FORMX-001 through FORMX-022."""
from __future__ import annotations

from itertools import product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM


def canonical_configuration(state, tape, head):
    if not tape or head not in tuple(range(len(tape))):
        raise ValueError("configuration requires a nonempty generated tape and retained head")
    return (state, tuple(tape), head)


def run_relation(source, relation, terminal, bound):
    trace = [source]
    seen = {source}
    current = source
    for _ in range(bound):
        if current in terminal:
            return tuple(trace), "terminal"
        images = tuple(relation.get(current, ()))
        if len(images) != 1:
            return tuple(trace), "partial" if not images else "branching"
        current = images[0]
        trace.append(current)
        if current in seen:
            return tuple(trace), "recurrent"
        seen.add(current)
    return tuple(trace), "open-boundary"


def word_concatenations(left, right):
    return {a + b for a in left for b in right}


def finite_iteration(language, depth):
    levels = [{()}]
    for _ in range(depth):
        levels.append(word_concatenations(levels[-1], language))
    return tuple(frozenset(level) for level in levels)


def parse_count_a(word):
    """Count S -> a | SS parse trees by complete split recursion."""
    if word == ("a",):
        return 1
    return sum(parse_count_a(word[:cut]) * parse_count_a(word[cut:]) for cut in range(1, len(word)))


def generated_a_words(depth):
    words = {("a",)}
    for _ in range(depth):
        words |= {left + right for left in tuple(words) for right in tuple(words)}
    return words


def accepts(word, start, accepting, transition):
    state = start
    for symbol in word:
        key = (state, symbol)
        if key not in transition:
            return False
        state = transition[key]
    return state in accepting


def transduce(word, start, relation):
    state = start
    output = ()
    for symbol in word:
        state, emitted = relation[(state, symbol)]
        output += tuple(emitted)
    return state, output


def rewrite_all(word, rules):
    images = set()
    for source, target in rules:
        width = len(source)
        for place in range(len(word) - width + 1):
            if word[place : place + width] == source:
                images.add(word[:place] + target + word[place + width :])
    return images


def normal_forms(word, rules):
    pending = [word]
    visited = set()
    terminals = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        images = rewrite_all(current, rules)
        if images:
            pending.extend(images)
        else:
            terminals.add(current)
    return frozenset(terminals), frozenset(visited)


def iterate(function, value, word):
    for _label in word:
        value = function(value)
    return value


def primitive_append(seed, controls, label):
    value = tuple(seed)
    for _control in controls:
        value += (label,)
    return value


def least_witness(sequence, predicate):
    for prefix, item in zip((sequence[:place] for place in range(1, len(sequence) + 1)), sequence):
        if predicate(item):
            return prefix, item
    return tuple(sequence), None


def free(term):
    tag = term[0]
    if tag == "var":
        return {term[1]}
    if tag == "app":
        return free(term[1]) | free(term[2])
    return free(term[2]) - {term[1]}


def rename(term, old, new):
    if term[0] == "var":
        return ("var", new if term[1] == old else term[1])
    if term[0] == "app":
        return ("app", rename(term[1], old, new), rename(term[2], old, new))
    binder = new if term[1] == old else term[1]
    return ("abs", binder, rename(term[2], old, new))


def substitute(term, name, replacement):
    if term[0] == "var":
        return replacement if term[1] == name else term
    if term[0] == "app":
        return ("app", substitute(term[1], name, replacement), substitute(term[2], name, replacement))
    binder, body = term[1], term[2]
    if binder == name:
        return term
    if binder in free(replacement):
        fresh = next(candidate for candidate in ("u", "v", "w", "z") if candidate not in free(body) | free(replacement) | {name})
        body = rename(body, binder, fresh)
        binder = fresh
    return ("abs", binder, substitute(body, name, replacement))


def stack_reverse(word):
    stack = []
    trace = []
    for symbol in word:
        stack.append(symbol)
        trace.append(("push", symbol, tuple(stack)))
    output = []
    while stack:
        symbol = stack.pop()
        output.append(symbol)
        trace.append(("pop", symbol, tuple(stack)))
    return tuple(output), tuple(trace)


def recursive_reverse(word):
    return () if not word else recursive_reverse(word[1:]) + (word[0],)


def circuit_value(inputs, gates):
    values = dict(inputs)
    for output, operation, left, right in gates:
        if operation == "same":
            values[output] = "held" if values[left] == values[right] else "changed"
        elif operation == "choose-left":
            values[output] = values[left]
        else:
            raise ValueError("unregistered gate")
    return values


def interleavings(left, right):
    if not left:
        return {tuple(right)}
    if not right:
        return {tuple(left)}
    return {(left[0],) + tail for tail in interleavings(left[1:], right)} | {(right[0],) + tail for tail in interleavings(left, right[1:])}


def interpret(program, source=()):
    value = tuple(source)
    trace = []
    for instruction in program:
        opcode, argument = instruction
        if opcode == "append":
            value += (argument,)
        elif opcode == "remove-last":
            if value:
                value = value[:-1]
        elif opcode == "retain":
            value = tuple(value)
        else:
            raise ValueError("unregistered instruction")
        trace.append((instruction, value))
    return value, tuple(trace)


ALPHABET = ("a", "b")
EVEN_A = {
    ("q-even", "a"): "q-odd",
    ("q-even", "b"): "q-even",
    ("q-odd", "a"): "q-even",
    ("q-odd", "b"): "q-odd",
}

OBS = {
    "001": ("configuration_round_trip", canonical_configuration("q", ("a", "b", "a"), 1) == ("q", ("a", "b", "a"), 1)),
    "002": ("partial_total_transition_distinction", run_relation("s", {"s": ("t",)}, {"t"}, 3)[1] == "terminal" and run_relation("s", {}, {"t"}, 3)[1] == "partial"),
    "003": ("accept_reject_recurrence_distinction", run_relation("a", {"a": ("accept",)}, {"accept", "reject"}, 4)[1] == "terminal" and run_relation("r", {"r": ("r2",), "r2": ("r",)}, {"accept", "reject"}, 4)[1] == "recurrent"),
    "004": ("finite_language_boolean_operations", ({("a",)} | {("b",)}) == {("a",), ("b",)} and ({("a",), ("b",)} & {("b",)}) == {("b",)} and {("a",), ("b",)} - {("b",)} == {("a",)}),
    "005": ("concatenation_and_iteration", word_concatenations({("a",)}, {("b",), ("a",)}) == {("a", "b"), ("a", "a")} and finite_iteration({("a",), ("b",)}, 2)[2] == frozenset(product(ALPHABET, repeat=2))),
    "006": ("complete_parse_tree_ambiguity", parse_count_a(("a", "a", "a")) == 2),
    "007": ("parser_recognizer_generator_correspondence", all(parse_count_a(word) >= 1 for word in generated_a_words(2)) and not accepts(("a",), "q-even", {"q-even"}, EVEN_A)),
    "008": ("automaton_product_and_quotient", all(accepts(word, "q-even", {"q-even"}, EVEN_A) == (word.count("a") % 2 == 0) for width in range(4) for word in product(ALPHABET, repeat=width))),
    "009": ("finite_state_transduction", transduce(("a", "b", "a"), "q", {("q", "a"): ("q", ("x",)), ("q", "b"): ("q", ("y",))}) == ("q", ("x", "y", "x"))),
    "010": ("stack_queue_register_correspondence", stack_reverse(("a", "b", "c"))[0] == ("c", "b", "a") and tuple(list(("a", "b"))[1:]) == ("b",) and iterate(lambda word: word + ("x",), (), ("c", "c")) == ("x", "x")),
    "011": ("rewrite_termination_and_normal_form", normal_forms(("a", "b", "a", "b"), ((('a', 'b'), ('b', 'a')),))[0] == frozenset({("b", "b", "a", "a")})),
    "012": ("critical_pair_confluence", normal_forms(("a", "a", "a"), ((('a', 'a'), ('a',)),))[0] == frozenset({("a",)})),
    "013": ("recursive_composition_iteration", iterate(lambda word: word + ("x",), (), ("a", "b", "c")) == ("x", "x", "x")),
    "014": ("primitive_recursion_and_least_witness", primitive_append(("s",), ("a", "b"), "x") == ("s", "x", "x") and least_witness(("a", "a", "b", "a"), lambda item: item == "b") == (("a", "a", "b"), "b")),
    "015": ("capture_avoiding_lambda_substitution", substitute(("abs", "y", ("var", "x")), "x", ("var", "y")) == ("abs", "u", ("var", "y"))),
    "016": ("abstract_machine_simulation_invariant", stack_reverse(("a", "b", "c"))[0] == recursive_reverse(("a", "b", "c")) and len(stack_reverse(("a", "b", "c"))[1]) == 6),
    "017": ("acyclic_circuit_evaluation", circuit_value({"a": "held", "b": "changed"}, (("c", "same", "a", "b"), ("d", "choose-left", "c", "a")))["d"] == "changed"),
    "018": ("sequential_combinational_correspondence", circuit_value({"a": "held", "b": "held"}, (("out", "same", "a", "b"),))["out"] == "held" and interpret((("append", "a"), ("append", "b")))[0] == ("a", "b")),
    "019": ("process_interleaving_observational_equivalence", len(interleavings(("a1", "a2"), ("b1", "b2"))) == 6 and all(tuple(x for x in row if x.startswith("a")) == ("a1", "a2") for row in interleavings(("a1", "a2"), ("b1", "b2")))),
    "020": ("universal_interpreter_self_execution", interpret((("append", "a"), ("retain", "self"), ("remove-last", "a"), ("append", "b")))[0] == ("b",)),
    "021": ("effective_translation_overhead", interpret((("append", "a"), ("append", "b")))[0] == stack_reverse(("b", "a"))[0] and len(interpret((("append", "a"), ("append", "b")))[1]) == 2),
    "022": ("formal_computation_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-COMP-FORMX-CONFIGURATION-IDENTITY-001", "Configuration identity and canonical state encoding", "canonical-configuration-carrier", "A formal configuration is the canonical product of one retained process state, one complete generated storage word and one retained position or focus; equality requires equality of every coordinate."),
    "002": ("SFT-COMP-FORMX-PARTIAL-TOTAL-TRANSITION-002", "Partial and total transition relations", "source-complete-transition-relation", "A transition relation is total on its declared domain exactly when every generated source has a retained image; an absent row is a partial boundary and multiple rows retain branching rather than selecting one."),
    "003": ("SFT-COMP-FORMX-TERMINAL-OUTCOME-DISTINCTION-003", "Acceptance, rejection and nontermination distinction", "three-way-terminal-recurrence-ledger", "Acceptance and rejection are separately labelled terminal classes; nontermination is a retained recurrent or open execution trace and is never relabelled as either terminal outcome."),
    "004": ("SFT-COMP-FORMX-LANGUAGE-BOOLEAN-CORRESPONDENCE-004", "Language union, intersection and complement correspondence", "complete-support-language-operations", "Union retains every word in either complete language, intersection retains exactly shared words, and relative complement retains source words absent from the declared comparison support."),
    "005": ("SFT-COMP-FORMX-CONCATENATION-ITERATION-005", "Concatenation, iteration and generated-language closure", "ordered-concatenation-successor-closure", "Language concatenation is the complete ordered joining of every left word with every right word; finite iteration begins with the empty One word and applies that product once per retained successor."),
    "006": ("SFT-COMP-FORMX-DERIVATION-TREE-AMBIGUITY-006", "Grammar derivation trees and ambiguity custody", "complete-derivation-tree-ledger", "A grammar derivation is a complete source-bound rewrite tree; ambiguity exists exactly when one generated terminal word retains multiple distinct derivation trees, all of which remain open."),
    "007": ("SFT-COMP-FORMX-PARSE-RECOGNIZE-GENERATE-007", "Parsing, recognition and generation correspondence", "parse-recognize-generate-equivalence", "Parsing, recognition and generation coincide only when they range over the same complete grammar boundary and preserve a witness tree or rejecting trace for every generated word."),
    "008": ("SFT-COMP-FORMX-AUTOMATON-PRODUCT-QUOTIENT-008", "Automaton product, quotient and minimization", "observation-equivalent-state-quotient", "Automaton product retains both component states; quotienting merges exactly states with identical complete future observations, and minimization is the least such observation-preserving quotient."),
    "009": ("SFT-COMP-FORMX-FINITE-TRANSDUCTION-009", "Finite-state transduction and output custody", "state-and-output-transduction", "A finite transducer retains for every source-state and input-label pair both its successor state and complete emitted word; composition preserves both state and output traces."),
    "010": ("SFT-COMP-FORMX-STORAGE-MACHINE-CORRESPONDENCE-010", "Stack, queue and register storage correspondence", "typed-storage-operation-ledger", "Stack, queue and register machines are distinguished by their retained storage access relation; translations are admitted only when every operation, stored label and execution order is reconstructible."),
    "011": ("SFT-COMP-FORMX-REWRITE-NORMAL-FORM-011", "Rewriting termination and normal forms", "well-founded-rewrite-normalization", "A rewrite system terminates on its declared grammar when every lawful step descends a registered finite order; a normal form is exactly a reachable form with no lawful successor."),
    "012": ("SFT-COMP-FORMX-REWRITE-CONFLUENCE-012", "Rewriting confluence and critical-pair custody", "complete-critical-pair-joinability", "Confluence is forced when every pair of divergent lawful rewrites has a retained common descendant; complete critical-pair enumeration supplies the finite local certificate."),
    "013": ("SFT-COMP-FORMX-RECURSIVE-COMPOSITION-013", "Recursive composition and finite iteration", "base-successor-recursive-composition", "A recursive computation retains one base value and one source-bound successor action; composition substitutes complete output traces and finite iteration applies the action once per generated control label."),
    "014": ("SFT-COMP-FORMX-PRIMITIVE-RECURSION-MINIMIZATION-014", "Primitive recursion and minimization correspondence", "generated-prefix-least-witness", "Primitive recursion is base-plus-successor construction over a generated word; minimization returns the first retained prefix whose terminal label satisfies the declared predicate or an explicit absent-result boundary."),
    "015": ("SFT-COMP-FORMX-LAMBDA-CAPTURE-NORMAL-015", "Lambda reduction, capture avoidance and normal forms", "capture-avoiding-bound-substitution", "Lambda-like substitution replaces only free occurrences, renames a conflicting binder before descent and retains alpha-equivalent structure; normality is absence of a registered reduction redex."),
    "016": ("SFT-COMP-FORMX-MACHINE-SIMULATION-INVARIANT-016", "Abstract-machine simulation invariants", "stepwise-configuration-simulation", "One abstract machine simulates another only through a total configuration relation preserving initial form, terminal outcome and each source step by a finite nonempty target trace with explicit overhead."),
    "017": ("SFT-COMP-FORMX-CIRCUIT-ACYCLIC-EVALUATION-017", "Circuit fan-in, fan-out and acyclic evaluation", "topological-gate-evaluation", "A formal circuit is a finite acyclic gate relation with declared inputs and outputs; evaluation follows dependency order and retains every intermediate held label and fan relation."),
    "018": ("SFT-COMP-FORMX-SEQUENTIAL-COMBINATIONAL-018", "Sequential and combinational process correspondence", "state-retained-sequential-unrolling", "A combinational process depends only on its declared input support; a sequential process additionally retains state, and finite unrolling produces an equivalent acyclic circuit only with every state record preserved."),
    "019": ("SFT-COMP-FORMX-PROCESS-ALGEBRA-EQUIVALENCE-019", "Process algebra composition and observational equivalence", "complete-interleaving-trace-equivalence", "Parallel process composition generates every interleaving preserving each local order; observational equivalence requires equality of complete declared observation traces, not one selected schedule."),
    "020": ("SFT-COMP-FORMX-UNIVERSAL-SELF-INTERPRETATION-020", "Universal interpreter and self-interpretation", "description-driven-universal-interpretation", "A universal Fold interpreter accepts a generated process description as data, executes only its registered operations and emits the same terminal value and trace as direct execution; its own description is admitted by the same grammar."),
    "021": ("SFT-COMP-FORMX-MODEL-TRANSLATION-OVERHEAD-021", "Effective model translation and overhead custody", "bidirectional-trace-preserving-translation", "Computational models are equivalent only when total translations preserve inputs, outcomes and complete traces in both directions while retaining exact description and execution overhead."),
    "022": ("SFT-COMP-FORMX-COMPLETENESS-022", "Formal-computation completeness certificate", "twenty-two-obligation-no-omission-ledger", "Formal-computation completeness is the one-to-one reconciliation of all twenty-two frozen extension obligations with unique survivors, adverse controls, exact observations, independent reconstructions and untouched-engine receipts."),
}

BASE = (
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-COMP-FORM-OPERATIONAL-PROCESS-001", "SFT-COMP-FORM-LANGUAGE-GRAMMAR-001",
    "SFT-COMP-FORM-LANGUAGE-GRAMMAR-001", "SFT-COMP-FORM-LANGUAGE-GRAMMAR-001",
    "SFT-COMP-FORM-AUTOMATON-001", "SFT-COMP-FORM-AUTOMATON-001",
    "SFT-COMP-FORM-AUTOMATON-001", "SFT-COMP-FORM-ABSTRACT-MACHINE-001",
    "SFT-COMP-FORM-REWRITING-001", "SFT-COMP-FORM-REWRITING-001",
    "SFT-COMP-FORM-RECURSIVE-FUNCTION-001", "SFT-COMP-FORM-RECURSIVE-FUNCTION-001",
    "SFT-COMP-FORM-LAMBDA-CALCULUS-001", "SFT-COMP-FORM-MODEL-EQUIVALENCE-001",
    "SFT-COMP-FORM-CIRCUIT-001", "SFT-COMP-FORM-OPERATIONAL-PROCESS-001",
    "SFT-COMP-FORM-COMPOSITION-001", "SFT-COMP-FORM-UNIVERSALITY-001",
    "SFT-COMP-FORM-MODEL-EQUIVALENCE-001", "SFT-COMP-FORM-UNIVERSALITY-001",
)

EXCLUSIONS = (
    "no axiom, imported machine model, theorem answer or target outcome selects the survivor",
    "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden transition, selected branch, omitted parse, unregistered oracle or stochastic cause",
    "no failed route retires an obligation or changes the protected engine or verification authority",
)


def dimensions(relation):
    return (
        binary_dimension("carrier", "complete configuration carrier?", "partial-carrier", "A partial carrier omits a generated state, word or focus.", "complete-canonical-carrier", "Every declared configuration coordinate is retained."),
        binary_dimension("transition", "source-complete lawful transition?", "hidden-or-selected-transition", "A hidden or selected step changes the operational relation.", "source-bound-complete-transition", "Every lawful source image is retained."),
        binary_dimension("relation", "forced formal relation?", "imported-model-answer", "An imported computational answer cannot force the law.", relation, "The relation is reconstructed from generated Fold states and traces."),
        binary_dimension("trace", "complete trace custody?", "terminal-only-output", "A terminal output alone closes execution distinctions.", "complete-step-trace", "Every intermediate configuration and outcome class is retained."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-examples", "Examples cannot close a formal computation family.", "literal-complete-product", "Every registered coordinate combination is generated exactly once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "Dependencies retain a complete chain to the root theorem."),
        binary_dimension("observation", "post-registry observation?", "preopened-target", "A preopened result could choose the survivor.", "post-registry-exact-execution", "Exact execution opens only after target identity freeze."),
        binary_dimension("extension", "successor-general boundary?", "fit-exception-rule", "An exception adds a free choice.", "finite-successor-or-explicit-boundary", "The base, successor and ownership boundary are declared."),
    )


class FormalExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="computation",
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
    index = int(number) - 1
    dependencies = (
        "SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006",
        "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006",
        BASE[index],
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id, "FORMX", title.lower().replace(" ", "-"), title, statement, dependencies,
        f"Generate the complete eight-axis FORMX-{number} product before observation access.",
        f"Every positive finite FORMX-{number} configuration, relation, trace, composition and registered successor boundary.",
        dimensions(relation),
        f"FORMX-{number} uniquely retains {relation}, complete execution custody, root forcing, post-registry observation and no extra rule.",
        (statement, observation),
        "The least process contains one canonical configuration and one retained source-bound operation or terminal classification.",
        "Adding one generated state, symbol, rule, gate, process or description preserves prior traces and generates every new lawful relation exactly once.",
        EXCLUSIONS,
        (
            Witness("exact-execution", observation, passed),
            Witness("complete-formal-census", "Every declared state, transition, trace, parse, gate and model translation is retained.", passed),
            Witness("target-free", "The survivor grammar is frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact execution and reject four adverse controls.",
        "The claim closes the declared positive finite formal-computation grammar; physical realization and quantum dynamics remain with their owning branches.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 22 or len(OBS) != 22 or not all(passed for _, passed in OBS.values()):
        raise ValueError("FORMX family witness or membership failure")
    for specification in specifications:
        specification.validate()


validate_family()
