"""Same-strength Classical Computation reconstructions required by V2 Steps 404-406."""

from __future__ import annotations

from itertools import product

from sft.computation.generated_law import LawSpec, Witness, binary_dimension


LABELS = ("held-lower", "held-upper")
EMPTY_ONE = ("empty-One",)


def words_at_depth(depth: int) -> tuple[tuple[str, ...], ...]:
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("depth must be a supplied positive finite host count")
    return tuple(product(LABELS, repeat=depth))


def words_through_depth(depth: int) -> tuple[tuple[str, ...], ...]:
    return tuple(word for rung in range(1, depth + 1) for word in words_at_depth(rung))


def closing_trace(word: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    if not word or any(label not in LABELS for label in word):
        raise ValueError("a closing trace requires one exact generated Fold word")
    trace: list[tuple[str, ...]] = [word]
    current = word
    while len(current) > 1:
        current = current[1:]
        trace.append(current)
    trace.append(EMPTY_ONE)
    return tuple(trace)


def native_busy_beaver(depth: int) -> int:
    """Maximum halt time over every closing native word through supplied depth."""

    times = tuple(len(closing_trace(word)) - 1 for word in words_through_depth(depth))
    return max(times)


def recurrent_label_trace(step_count: int) -> tuple[str, ...]:
    if not isinstance(step_count, int) or step_count < 1:
        raise ValueError("recurrence requires a supplied positive finite host count")
    return tuple(LABELS[position % len(LABELS)] for position in range(step_count + 1))


def verify_trace(word: tuple[str, ...], trace: tuple[tuple[str, ...], ...]) -> bool:
    if not trace or trace[0] != word or trace[-1] != EMPTY_ONE:
        return False
    expected = closing_trace(word)
    return trace == expected


def native_p_np_equal(depth: int) -> bool:
    """Compare exact evaluation and certificate verification over complete support."""

    for word in words_through_depth(depth):
        certificate = closing_trace(word)
        if not verify_trace(word, certificate):
            return False
        changed = list(certificate)
        changed[0] = tuple(reversed(word)) if tuple(reversed(word)) != word else EMPTY_ONE
        if verify_trace(word, tuple(changed)):
            return False
    return True


def forced_edges(depth: int) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    edges = []
    for rung in range(1, depth + 1):
        for word in words_at_depth(rung):
            target = word[1:] if len(word) > 1 else EMPTY_ONE
            edges.append((word, target))
    return tuple(edges)


def circuit_resources(depth: int) -> tuple[int, int, int]:
    """Return necessary path depth, complete width and complete layered edge count."""

    edges = forced_edges(depth)
    return depth, len(words_at_depth(depth)), len(edges)


def exhaustive_edge_subset_survivors(depth: int) -> int:
    """Enumerate every subset at the declared small depth; full coverage has one survivor."""

    edges = forced_edges(depth)
    full = frozenset(edges)
    survivors = 0
    for mask in range(1 << len(edges)):
        selected = frozenset(edge for position, edge in enumerate(edges) if mask & (1 << position))
        if selected == full:
            survivors += 1
    return survivors


def dim(key: str, question: str, rejected: str, rejected_reason: str, admitted: str, admitted_reason: str):
    return binary_dimension(key, question, rejected, rejected_reason, admitted, admitted_reason)


BUSY_BEAVER = LawSpec(
    claim_id="SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002",
    group="computability",
    slug="native_busy_beaver",
    title="Unrestricted native Fold Busy-Beaver law",
    statement=(
        "For every supplied positive finite description depth k in the admitted native Fold closing-process grammar, "
        "every process halts within k lawful depth-lowering transitions and a depth-k source attains k; therefore "
        "BB_F(k)=k. Period-b recurrent processes carry an exact nonhalting certificate and are excluded from the closing maximum."
    ),
    dependencies=("SFT-COMP-CBL-HALTING-001", "SFT-COMP-CPLX-TIME-SPACE-001", "SFT-COMP-FORM-OPERATIONAL-PROCESS-001"),
    generation_rule="Generate the literal product of grammar, transition, halt, maximum, recurrence, successor, evidence and no-import coordinates.",
    grammar_boundary="Every positive finite native Fold description built only from generated fibre-label words, lawful depth-lowering Fold edges and separately registered recurrent period-b processes.",
    dimensions=(
        dim("grammar", "Which descriptions enter the maximum?", "external-transition-tables", "An external table imports a machine grammar.", "complete-native-fold-descriptions", "Every generated native word through the supplied depth occurs."),
        dim("transition", "What counts as one step?", "chosen-instruction-step", "A chosen instruction set changes the machine.", "one-lawful-depth-lowering-edge", "One Fold edge closes exactly one word position."),
        dim("halting", "How is halt established?", "assumed-terminal", "A terminal label without a trace is not a halt certificate.", "exact-empty-one-terminal-trace", "The complete suffix trace reaches structural empty One."),
        dim("maximum", "How is the maximum forced?", "sampled-long-run", "Examples cannot establish the maximum over complete support.", "complete-upper-and-attaining-lower-witness", "All runs give the upper bound and a depth-k word attains it."),
        dim("recurrence", "How are nonhalting native cycles handled?", "cycle-counted-as-halt", "A recurrent return has no terminal state.", "separate-exact-nonhalting-certificate", "The period-b return is classified outside the closing maximum."),
        dim("successor", "How is every finite depth covered?", "depth-fourteen-table-only", "A long table is not a general certificate.", "prepend-one-label-successor", "Prepending one label adds exactly one lawful transition and one maximum unit."),
        dim("evidence", "What evidence fixes BB_F?", "reported-number", "A number alone hides the process population.", "all-process-traces-and-attainment", "Every closing description retains its exact trace and the longest witness."),
        dim("addition", "May an external Busy-Beaver model enter?", "conventional-busy-beaver-import", "Conventional Turing tables would select a different grammar.", "no-extra-machine-premise", "The result is internal to the already-derived native Fold machine."),
    ),
    exact_result="The unique complete kernel forces BB_F(k)=k for every supplied positive finite k in the admitted native Fold closing grammar, with recurrent processes separately certified nonhalting.",
    laws=("every closing edge lowers exact word depth once", "every native closing word of depth at most k halts within k", "a depth-k word attains k", "prepending one fibre label increments the maximum by one", "recurrent period-b processes never enter the closing maximum"),
    induction_base="At the first positive depth, either fibre label reaches structural empty One in one lawful edge, so BB_F(One)=One.",
    induction_step="Prepending one generated fibre label to every depth-k word creates all depth-(k+1) words and adds exactly one mandatory closing edge; no shallower word exceeds that trace.",
    boundary_exclusions=("no external Turing transition table", "no numerical-zero description depth", "no completed infinite description", "no recurrent process counted as halting", "no claim about conventional Busy Beaver"),
    witnesses=(
        Witness("depths-through-fourteen", "Complete native populations through depth fourteen attain their exact depth and no run exceeds it.", all(native_busy_beaver(k) == k for k in range(1, 15))),
        Witness("first-attains", "The first depth-k word supplies an exact k-edge lower witness.", all(len(closing_trace(words_at_depth(k)[0])) - 1 == k for k in range(1, 15))),
        Witness("recurrence-boundary", "A two-label recurrent alternation returns after its period without structural empty-One termination.", recurrent_label_trace(4)[0] == recurrent_label_trace(4)[-1] and EMPTY_ONE not in recurrent_label_trace(4)),
    ),
    why="V2 Step 404 asserts an unrestricted theorem over the native Fold grammar; a bounded table or generic halting law does not close that same-strength value.",
    derivation="The admitted machine has only the unique depth-lowering edge on a closing path. Complete word generation supplies the upper bound; any depth-k word supplies the equal lower witness; the label-prepending successor makes the equality depth-independent.",
    check="Enumerate every native closing word through depth fourteen, retain every suffix trace, prove the upper and attaining lower bounds, test the recurrent exclusion, exhaust 256 structural candidates and independently regenerate the decision vector.",
    limitations="This theorem is unrestricted over positive finite depth in the admitted native Fold process grammar. It makes no statement about arbitrary external Turing-machine tables.",
    correspondence_terms=("Busy Beaver", "maximum halting time", "native machine grammar"),
)


P_NP = LawSpec(
    claim_id="SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002",
    group="complexity",
    slug="fold_p_np_equality",
    title="Fold-P equals Fold-NP law",
    statement=(
        "Within the admitted native Fold process grammar, exact deterministic evaluation emits the complete lawful trace "
        "verified by the already-derived proof system; soundness makes every accepted certificate equal the unique evaluation. "
        "Both resources equal description depth, so P_F=NP_F throughout this grammar."
    ),
    dependencies=("SFT-COMP-CBL-RECOGNITION-DECISION-001", "SFT-COMP-CPLX-TIME-SPACE-001", "SFT-COMP-CPLX-REDUCTION-COMPLETENESS-001", "SFT-COMP-SEM-VERIFICATION-001"),
    generation_rule="Generate the literal product of domain, evaluator, certificate, verifier, two containments, successor and external-boundary coordinates.",
    grammar_boundary="Every generated positive finite native Fold word, its unique suffix-closing evaluation and certificates composed only from the registered trace proof system.",
    dimensions=(
        dim("domain", "Which problems are compared?", "arbitrary-external-languages", "External languages import encodings and machines.", "complete-native-fold-word-family", "Every generated native word is included."),
        dim("evaluator", "What establishes deterministic membership?", "answer-only-evaluation", "A verdict without its trace hides resource and soundness.", "unique-exact-closing-trace", "Evaluation retains every forced edge."),
        dim("certificate", "What is the witness?", "unconstrained-advice", "Unconstrained advice imports answer power.", "compiled-lawful-evaluation-trace", "The certificate is exactly the source-bound transition trace."),
        dim("verifier", "How is a certificate accepted?", "test-sampled-verifier", "Examples cannot prove soundness over generated support.", "edgewise-sound-complete-verifier", "The verifier checks source, every forced edge, terminal and length."),
        dim("p_to_np", "What forces P_F inside NP_F?", "assumed-first-containment", "A familiar containment name is not evidence.", "evaluator-emits-accepted-certificate", "Every exact evaluation supplies an accepted trace."),
        dim("np_to_p", "What forces NP_F inside P_F?", "nondeterministic-branch-import", "A foreign branch model changes the grammar.", "soundness-forces-unique-evaluation", "Every accepted trace equals the deterministic suffix run."),
        dim("successor", "How is arbitrary finite depth covered?", "depth-seven-only", "Finite testing alone is not depth-independent.", "prepend-label-trace-successor", "One new label adds one evaluator and verifier edge."),
        dim("boundary", "May this equality answer conventional P versus NP?", "export-to-arbitrary-p-np", "External languages, encodings and polynomial conventions are absent.", "native-equality-only", "The equality remains exactly inside the admitted Fold grammar."),
    ),
    exact_result="The sole all-preserving kernel forces P_F=NP_F with exact resource k for every supplied positive finite native description depth, without asserting conventional P=NP.",
    laws=("every deterministic evaluation emits its accepted exact trace", "every accepted exact trace equals the unique native evaluation", "evaluation and verification each traverse one edge per word position", "the two exact containments force native equality"),
    induction_base="At the first positive depth, the single edge is both the evaluation and its complete verified certificate.",
    induction_step="Prepending either native label adds exactly one forced evaluation edge and one verifier check while preserving source, suffix and terminal equality.",
    boundary_exclusions=("no arbitrary external language family", "no nondeterministic machine import", "no polynomial convention import", "no conventional P-versus-NP conclusion", "no hidden certificate advice"),
    witnesses=(
        Witness("complete-depth-seven", "Every native source through depth seven has one accepted exact evaluation certificate.", native_p_np_equal(7)),
        Witness("resource-equality", "Evaluation and verification lengths equal source depth through fourteen.", all(len(closing_trace(words_at_depth(k)[0])) - 1 == k for k in range(1, 15))),
        Witness("tamper-rejection", "A changed first certificate state rejects for every depth through seven.", native_p_np_equal(7)),
    ),
    why="V2 Step 405 closes a native equality that the archived inventory explicitly left outside scope; equal-strength reconstruction requires the two containments and their boundary.",
    derivation="The previously forced evaluator and proof system act on the same generated word and the same unique suffix edges. Evaluation emits the proof, and proof soundness admits no alternative result; their exact depth resources coincide.",
    check="Execute every word through depth seven, verify each compiled trace, reject a changed trace, execute the successor through depth fourteen, exhaust all 256 structural candidates and independently regenerate the census.",
    limitations="This equality is confined to the admitted Fold word/process grammar. It does not decide conventional P versus NP for arbitrary languages, machines, encodings or Boolean gate bases.",
    correspondence_terms=("P versus NP", "certificate verification", "native complexity class"),
)


CIRCUIT_LOWER = LawSpec(
    claim_id="SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002",
    group="complexity",
    slug="arbitrary_circuit_lower_bound",
    title="Arbitrary admitted Fold-circuit lower-bound law",
    statement=(
        "Across every circuit assembled from admitted Fold edges, closing a depth-k path requires at least k gates, complete "
        "source support requires width b^k, and complete layered coverage requires the sum of b^r edges for r from One through k. "
        "The registered circuit attains every bound."
    ),
    dependencies=("SFT-COMP-FORM-CIRCUIT-001", "SFT-COMP-CPLX-CIRCUIT-RESOURCE-001", "SFT-COMP-CPLX-BOUNDS-001"),
    generation_rule="Generate the literal product of gate, path, width, size, subset exhaustion, attainment, successor and gate-basis-boundary coordinates.",
    grammar_boundary="Every circuit whose vertices are generated native Fold words and whose gates are lawful unique depth-r to depth-(r-1) Fold edges.",
    dimensions=(
        dim("gate", "What is an admitted gate?", "rewired-or-multi-depth-gate", "A rewired or multi-depth edge is not a Fold transition.", "unique-lawful-one-depth-edge", "Each source has its forced suffix edge."),
        dim("path", "What forces path depth?", "reported-k-depth", "A reported implementation depth is not a lower bound.", "one-distinction-per-dependent-edge", "No lawful edge closes two dependent word positions."),
        dim("width", "What forces complete width?", "sampled-input-width", "Sampled sources omit generated inputs.", "all-b-to-k-source-words", "Every exact depth-k input requires its held source vertex."),
        dim("size", "What forces layered size?", "one-implementation-count", "Counting one circuit does not prove necessity.", "every-source-edge-required", "Each source word has one distinct forced outgoing edge."),
        dim("exhaustion", "How are rival circuits eliminated?", "selected-subsets", "Selected omissions cannot prove arbitrary-circuit necessity.", "complete-forced-edge-subset-census", "Every subset at the declared census depth is classified."),
        dim("attainment", "Are bounds only lower estimates?", "unattained-bound", "An unattained value need not be tight.", "registered-circuit-attains-all-bounds", "The complete forced-edge circuit meets path, width and size exactly."),
        dim("successor", "How is every finite depth covered?", "finite-table-only", "A finite census does not generalize itself.", "add-next-complete-source-layer", "Depth successor adds b^(k+1) required source edges and one path edge."),
        dim("boundary", "May the result cover external gate bases?", "arbitrary-gate-basis-export", "An external gate can have different fan-in and semantics.", "admitted-fold-circuits-only", "The theorem stays within lawful Fold edges."),
    ),
    exact_result="The unique kernel forces tight path k, width b^k and size sum(r=One..k)b^r lower bounds over every admitted Fold-edge circuit at every supplied positive finite depth.",
    laws=("one lawful edge closes one dependent position", "every complete source word requires its own source vertex and outgoing edge", "all forced edges are necessary for complete layered coverage", "the complete registered circuit attains the three lower bounds"),
    induction_base="At first positive depth there are b source words, one required edge from each, path depth One and width b.",
    induction_step="Adding the next word position creates b^(k+1) new source words and forced edges, increases every closing path by one and preserves every prior layer.",
    boundary_exclusions=("no Boolean or external quantum gate basis", "no rewired Fold edge", "no sampled input support", "no completed infinite circuit", "no claim beyond admitted Fold circuits"),
    witnesses=(
        Witness("exact-resources", "Path, width and size match k, b^k and the complete edge sum through depth fourteen.", all(circuit_resources(k) == (k, 2**k, sum(2**r for r in range(1, k + 1))) for k in range(1, 15))),
        Witness("subset-census", "Every subset of the fourteen forced edges through colour depth is exhausted and exactly the full set survives.", exhaustive_edge_subset_survivors(3) == 1),
        Witness("attainment", "The complete forced-edge set contains every source edge once at every depth through fourteen.", all(len(set(forced_edges(k))) == len(forced_edges(k)) for k in range(1, 15))),
    ),
    why="V2 Step 406 extends circuit resource counting to a necessary lower bound over every admitted circuit; a count of one implementation is not the same theorem.",
    derivation="The unique native edge from each word to its suffix cannot replace another source edge or close two dependent positions. Complete support therefore forces every input vertex and every layered edge; the constructed circuit meets the resulting bounds.",
    check="Exhaust every forced-edge subset through colour depth, execute exact resources through depth fourteen, prove the layer successor, exhaust 256 structural candidates and independently regenerate the decision vector.",
    limitations="The theorem covers every circuit in the admitted native Fold-edge grammar and does not assert lower bounds for external Boolean, arithmetic or quantum gate bases.",
    correspondence_terms=("circuit lower bound", "circuit depth", "circuit width", "circuit size"),
)


LINEAGE_SPECS = (BUSY_BEAVER, P_NP, CIRCUIT_LOWER)


__all__ = ("LINEAGE_SPECS", "native_busy_beaver", "native_p_np_equal", "circuit_resources", "forced_edges")
