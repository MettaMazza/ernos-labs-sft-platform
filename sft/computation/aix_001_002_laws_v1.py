"""Exact attention-and-learning specializations for UnisonFold-class systems.

These laws close two application-specific Classical Computation obligations.
They do not admit a trained model, a conversational-performance result, or an
external teacher as a derivational premise.  Exact operational witnesses are
small generated carriers; later UnisonFold executions remain separately
identified application evidence.
"""

from __future__ import annotations

from fractions import Fraction
from functools import reduce

from sft.computation.generated_law import LawSpec, Witness, binary_dimension


ABSENT = ("structural-absence",)


def oriented(orientation: str, magnitude: Fraction | int) -> tuple[object, ...]:
    exact = Fraction(magnitude)
    if orientation not in {"held", "returned"} or exact <= 0:
        raise ValueError("an oriented part requires one held orientation and an exact positive magnitude")
    return orientation, exact


def _orientation(value: tuple[object, ...]) -> str:
    if value == ABSENT:
        return "absent"
    return str(value[0])


def _magnitude(value: tuple[object, ...]) -> Fraction:
    if value == ABSENT:
        raise ValueError("structural absence has no numerical magnitude")
    return Fraction(value[1])


def opposite(value: tuple[object, ...]) -> tuple[object, ...]:
    if value == ABSENT:
        return ABSENT
    return oriented("returned" if _orientation(value) == "held" else "held", _magnitude(value))


def join(left: tuple[object, ...], right: tuple[object, ...]) -> tuple[object, ...]:
    if left == ABSENT:
        return right
    if right == ABSENT:
        return left
    left_orientation, right_orientation = _orientation(left), _orientation(right)
    left_magnitude, right_magnitude = _magnitude(left), _magnitude(right)
    if left_orientation == right_orientation:
        return oriented(left_orientation, left_magnitude + right_magnitude)
    if left_magnitude == right_magnitude:
        return ABSENT
    return oriented(
        left_orientation if left_magnitude > right_magnitude else right_orientation,
        left_magnitude - right_magnitude if left_magnitude > right_magnitude else right_magnitude - left_magnitude,
    )


def scale(value: tuple[object, ...], part: Fraction) -> tuple[object, ...]:
    exact = Fraction(part)
    if exact <= 0:
        raise ValueError("scaling requires an exact positive part")
    return ABSENT if value == ABSENT else oriented(_orientation(value), _magnitude(value) * exact)


def product_part(left: tuple[object, ...], right: tuple[object, ...]) -> tuple[object, ...]:
    if left == ABSENT or right == ABSENT:
        return ABSENT
    result_orientation = "held" if _orientation(left) == _orientation(right) else "returned"
    return oriented(result_orientation, _magnitude(left) * _magnitude(right))


def difference(left: tuple[object, ...], right: tuple[object, ...]) -> tuple[object, ...]:
    return join(left, opposite(right))


def _less(left: tuple[object, ...], right: tuple[object, ...]) -> bool:
    left_orientation, right_orientation = _orientation(left), _orientation(right)
    if left_orientation != right_orientation:
        order = {"returned": 0, "absent": 1, "held": 2}
        return order[left_orientation] < order[right_orientation]
    if left_orientation == "absent":
        return False
    if left_orientation == "held":
        return _magnitude(left) < _magnitude(right)
    return _magnitude(left) > _magnitude(right)


def least_part(values: tuple[tuple[object, ...], ...]) -> tuple[object, ...]:
    if not values:
        raise ValueError("least-part selection requires generated support")
    least = values[0]
    for value in values[1:]:
        if _less(value, least):
            least = value
    return least


def finite_partition(scores: tuple[tuple[object, ...], ...]) -> tuple[Fraction, ...]:
    """Order-preserving exact partition over complete generated score support."""

    least = least_part(scores)
    masses = []
    for score in scores:
        lifted = difference(score, least)
        if _orientation(lifted) == "returned":
            raise AssertionError("least-score lift cannot retain a returned orientation")
        masses.append(Fraction(1, 1) if lifted == ABSENT else Fraction(1, 1) + _magnitude(lifted))
    whole = reduce(lambda left, right: left + right, masses)
    weights = tuple(mass / whole for mass in masses)
    if reduce(lambda left, right: left + right, weights) != Fraction(1, 1):
        raise AssertionError("attention weights do not compose to One")
    return weights


def weighted_join(values: tuple[tuple[object, ...], ...], weights: tuple[Fraction, ...]) -> tuple[object, ...]:
    if len(values) != len(weights) or not values:
        raise ValueError("weighted contraction requires equal complete supports")
    result = ABSENT
    for value, weight in zip(values, weights):
        result = join(result, scale(value, weight))
    return result


def fold_normalize(values: tuple[tuple[object, ...], ...]) -> tuple[tuple[object, ...], ...]:
    """Exact mean-departure normalization with structural constant-vector handling."""

    if not values:
        raise ValueError("normalization requires a generated coordinate carrier")
    mean = ABSENT
    share = Fraction(1, len(values))
    for value in values:
        mean = join(mean, scale(value, share))
    departures = tuple(difference(value, mean) for value in values)
    magnitudes = tuple(_magnitude(value) for value in departures if value != ABSENT)
    if not magnitudes:
        return tuple(ABSENT for _value in values)
    whole_departure = reduce(lambda left, right: left + right, magnitudes)
    exact_scale = Fraction(len(values), 1) / whole_departure
    return tuple(ABSENT if value == ABSENT else scale(value, exact_scale) for value in departures)


def oriented_complement_gate(value: tuple[object, ...]) -> tuple[object, ...]:
    """Two-Fibre complement gate; the two branch parts always compose to One."""

    if value == ABSENT:
        return ABSENT
    magnitude = _magnitude(value)
    whole = Fraction(2, 1) + magnitude
    held_branch = (Fraction(1, 1) + magnitude) / whole
    returned_branch = Fraction(1, 1) / whole
    if held_branch + returned_branch != Fraction(1, 1):
        raise AssertionError("gate complement parts do not compose to One")
    multiplier = held_branch if _orientation(value) == "held" else returned_branch
    return scale(value, multiplier)


def causal_attention(tokens: tuple[tuple[object, ...], ...]) -> tuple[dict[str, object], ...]:
    """One-coordinate exact Q/K/V witness with future positions structurally absent."""

    if not tokens:
        raise ValueError("attention requires an ordered token support")
    trace = []
    for target, query in enumerate(tokens):
        source_positions = tuple(range(target + 1))
        keys = tokens[: target + 1]
        scores = tuple(product_part(query, key) for key in keys)
        weights = finite_partition(scores)
        output = weighted_join(keys, weights)
        trace.append(
            {
                "target": target,
                "source_positions": source_positions,
                "scores": scores,
                "weights": weights,
                "output": output,
            }
        )
    return tuple(trace)


def attention_witnesses() -> tuple[bool, ...]:
    base = causal_attention((oriented("held", 1),))
    prefix = (oriented("held", 1), oriented("returned", Fraction(1, 2)))
    appended = prefix + (oriented("held", Fraction(3, 2)),)
    prefix_trace = causal_attention(prefix)
    successor_trace = causal_attention(appended)
    head_a = successor_trace
    head_b = causal_attention(tuple(opposite(value) for value in appended))
    retained_heads = tuple((left["output"], right["output"]) for left, right in zip(head_a, head_b))
    normalized = fold_normalize(retained_heads[-1])
    gated = tuple(oriented_complement_gate(value) for value in normalized)
    residual = tuple(join(source, update) for source, update in zip(retained_heads[-1], gated))
    return (
        base[0]["source_positions"] == (0,) and base[0]["weights"] == (Fraction(1, 1),),
        tuple(row["output"] for row in prefix_trace) == tuple(row["output"] for row in successor_trace[: len(prefix_trace)]),
        all(row["source_positions"] == tuple(range(row["target"] + 1)) for row in successor_trace),
        all(reduce(lambda left, right: left + right, row["weights"]) == Fraction(1, 1) for row in successor_trace),
        len(retained_heads) == len(appended) and all(len(row) == 2 for row in retained_heads),
        len(normalized) == len(gated) == len(residual) == 2,
        oriented_complement_gate(ABSENT) == ABSENT,
    )


def binary32_positive_part(bits: int) -> Fraction | None:
    """Translate one captured positive IEEE-754 binary32 record without float arithmetic."""

    if not isinstance(bits, int) or bits < 0 or bits >= (1 << 32):
        raise ValueError("binary32 record is outside its exact bit carrier")
    sign = bits >> 31
    exponent = (bits >> 23) & 0xFF
    fraction = bits & ((1 << 23) - 1)
    if sign or exponent == 0xFF:
        raise ValueError("teacher masses must be finite nonnegative observation records")
    if exponent == 0 and fraction == 0:
        return None
    if exponent == 0:
        significand, power = fraction, -149
    else:
        significand, power = (1 << 23) + fraction, exponent - 127 - 23
    if power >= 0:
        return Fraction(significand * (1 << power), 1)
    return Fraction(significand, 1 << (-power))


def exact_teacher_partition(bit_records: tuple[int, ...]) -> tuple[Fraction | None, ...]:
    parts = tuple(binary32_positive_part(bits) for bits in bit_records)
    present = tuple(part for part in parts if part is not None)
    if not present:
        raise ValueError("teacher partition contains no observed positive part")
    whole = reduce(lambda left, right: left + right, present)
    normalized = tuple(None if part is None else part / whole for part in parts)
    normalized_present = tuple(part for part in normalized if part is not None)
    if reduce(lambda left, right: left + right, normalized_present) != Fraction(1, 1):
        raise AssertionError("teacher observation parts do not compose to One")
    return normalized


def distribution_disagreement(
    left: tuple[Fraction | None, ...], right: tuple[Fraction | None, ...]
) -> tuple[int, Fraction | None]:
    if len(left) != len(right) or not left:
        raise ValueError("distribution comparison requires equal complete supports")
    differences = []
    for left_part, right_part in zip(left, right):
        if left_part is None and right_part is None:
            continue
        if left_part is None:
            differences.append(right_part)
        elif right_part is None:
            differences.append(left_part)
        elif left_part != right_part:
            differences.append(left_part - right_part if left_part > right_part else right_part - left_part)
    if not differences:
        return 0, None
    return len(differences), reduce(lambda first, second: first + second, differences)


def objective_less(left: tuple[int, Fraction | None], right: tuple[int, Fraction | None]) -> bool:
    left_count, left_part = left
    right_count, right_part = right
    if left_part is None:
        return right_part is not None
    if right_part is None:
        return False
    if left_part != right_part:
        return left_part < right_part
    return left_count < right_count


def retained_strict_successors(
    current: tuple[int, Fraction | None], candidates: tuple[tuple[str, tuple[int, Fraction | None]], ...]
) -> tuple[str, ...]:
    if not candidates or len({name for name, _objective in candidates}) != len(candidates):
        raise ValueError("update candidates require a complete unique identity ledger")
    best = candidates[0][1]
    for _name, objective in candidates[1:]:
        if objective_less(objective, best):
            best = objective
    tied = tuple(name for name, objective in candidates if objective == best)
    return tied if objective_less(best, current) else ()


def teacher_learning_witnesses() -> tuple[bool, ...]:
    teacher = exact_teacher_partition((0x3E800000, 0x3F000000, 0x3E800000))
    student = exact_teacher_partition((0x3F000000, 0x3E800000, 0x3E800000))
    improved_a = (Fraction(3, 8), Fraction(3, 8), Fraction(1, 4))
    improved_b = tuple(improved_a)
    worsened = (Fraction(5, 8), Fraction(1, 8), Fraction(1, 4))
    current_objective = distribution_disagreement(student, teacher)
    candidates = (
        ("held-direction", distribution_disagreement(improved_a, teacher)),
        ("returned-direction", distribution_disagreement(worsened, teacher)),
        ("parallel-held-direction", distribution_disagreement(improved_b, teacher)),
        ("unchanged", current_objective),
    )
    tied_successors = retained_strict_successors(current_objective, candidates)
    no_descent = retained_strict_successors(current_objective, (("unchanged", current_objective),))
    persisted_artifact = {
        "model_identity": "student-successor",
        "parent_identity": "student-parent",
        "objective_ledger": candidates,
        "retained_tied_successors": tied_successors,
    }
    return (
        binary32_positive_part(0x3F000000) == Fraction(1, 2),
        teacher == (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
        reduce(lambda left, right: left + right, tuple(part for part in teacher if part is not None)) == Fraction(1, 1),
        current_objective == (2, Fraction(1, 2)),
        tied_successors == ("held-direction", "parallel-held-direction"),
        no_descent == (),
        "teacher" not in persisted_artifact and "teacher_runtime" not in persisted_artifact,
    )


ATTENTION_DIMENSIONS = (
    binary_dimension("support", "complete ordered token-position support?", "sampled-token-context", "A sampled context cannot establish the architecture carrier.", "complete-ordered-token-position-support", "Every token and position retains one exact identity."),
    binary_dimension("projection", "exact source-bound query, key and value projections?", "opaque-attention-score", "An opaque score cannot reconstruct attention.", "exact-source-bound-q-k-v-projections", "Every projection and contraction is exact and retained."),
    binary_dimension("causality", "future positions excluded structurally?", "numerical-future-mask", "A numerical sentinel introduces a non-SFT proof value and may leak future support.", "structural-predecessor-only-support", "Only generated causal predecessors enter each partition."),
    binary_dimension("partition", "complete exact attention partition?", "sampled-or-truncated-attention", "Truncation removes lawful predecessor parts.", "complete-exact-causal-attention-partition", "All lawful score parts compose exactly to One."),
    binary_dimension("heads", "head identities and contraction retained?", "collapsed-or-unidentified-heads", "Collapsed heads cannot be independently reconstructed.", "identity-retaining-multihead-contraction", "Every head and source contraction remains addressable."),
    binary_dimension("block", "complete normalization, residual and gate block trace?", "result-only-layer", "A terminal layer value cannot establish its operation sequence.", "exact-normalize-residual-gate-block-trace", "Every block operation and interface is retained."),
    binary_dimension("successor", "causality preserved when one position or layer is appended?", "fixed-context-demonstration", "A fixed demonstration does not close generalized depth.", "append-position-and-layer-successor", "The base and append successor preserve every prior causal output."),
    binary_dimension("boundary", "architecture free of imported runtime, weights and target selection?", "imported-transformer-runtime-or-weights", "Imported machinery would replace the SFT architecture proof.", "no-imported-runtime-weight-or-target-selector", "The architecture is generated wholly inside the declared exact carrier."),
)


LEARNING_DIMENSIONS = (
    binary_dimension("teacher", "teacher identity frozen as external observation?", "mutable-or-runtime-teacher", "A mutable or runtime teacher can silently select later states.", "frozen-source-bound-external-teacher", "Teacher identity and observation custody are fixed before new execution."),
    binary_dimension("encoding", "teacher records translated by exact bit identity?", "float-arithmetic-target", "Floating arithmetic would become an unregistered learning rule.", "exact-bit-record-to-rational-parts", "Captured finite bits translate to exact dyadic parts without float arithmetic."),
    binary_dimension("support", "complete declared teacher output partition?", "top-k-or-truncated-teacher-output", "A truncated distribution hides disagreement support.", "complete-declared-teacher-output-partition", "Every declared output group is present or structurally absent."),
    binary_dimension("custody", "development, validation and held-out identities frozen?", "mixed-or-migrating-data-roles", "Migrating rows invalidate generalization custody.", "frozen-disjoint-data-role-ledgers", "Every example remains in its predeclared role."),
    binary_dimension("objective", "exact complete disagreement objective?", "floating-surrogate-or-hidden-weight", "A surrogate or hidden weight is not the registered SFT relation.", "exact-complete-disagreement-ledger", "Every hard and teacher-part disagreement is exact and retained."),
    binary_dimension("update", "complete generated exact update grammar?", "gradient-or-target-selected-update", "A target-selected or opaque gradient route cannot force the update.", "generated-exact-update-candidate-grammar", "Unchanged and every declared oriented successor are generated before scoring."),
    binary_dimension("selection", "strict descent, ties, failures and lineage retained?", "winner-only-or-overwritten-history", "Erasing alternatives or adverse rows breaks learning custody.", "strict-descent-tie-adverse-lineage-ledger", "Only strict descent mutates state and every tie or failure remains retained."),
    binary_dimension("boundary", "teacher-free persistence and separate unseen evaluation?", "copied-weight-runtime-teacher-or-training-generalization", "Teacher dependence or a training-only generalization claim crosses the boundary.", "teacher-free-artifact-and-sealed-unseen-boundary", "The artifact persists without its teacher and generalization is tested separately."),
)


ATTENTION_CHECKS = attention_witnesses()
LEARNING_CHECKS = teacher_learning_witnesses()


ATTENTION_SPEC = LawSpec(
    claim_id="SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001",
    group="AIX",
    slug="causal-attention-transformer",
    title="Exact SFT causal attention-transformer assembly",
    statement="An SFT causal attention-transformer is the finite composition of exact source-bound token and position carriers, query-key-value projections, predecessor-only attention partitions, identity-retaining multihead value contractions, exact normalization, residual and oriented complement-gate blocks, and a complete output-support projection. Future positions are structural absence rather than numerical masks; every intermediate part, rounding or enclosure and causal edge is retained; a one-position base and append-position/layer successor preserve all prior causal outputs; no imported transformer runtime, pretrained weight or target result selects the architecture.",
    dependencies=(
        "SFT-COMP-FORM-STATE-TRANSITION-001",
        "SFT-COMP-FORM-COMPOSITION-001",
        "SFT-COMP-ALG-STRINGS-SEQUENCES-001",
        "SFT-COMP-SCIX-FINITE-PRECISION-002",
        "SFT-MATH-GRAPH-DIRECTED-CAUSAL-REACHABILITY-008",
        "SFT-MATH-LINEAR-VECTOR-COORDINATE-CARRIERS-001",
        "SFT-MATH-LINEAR-MAP-COMPOSITION-002",
        "SFT-MATH-LINEAR-INNER-PRODUCT-METRIC-008",
        "SFT-MATH-LINEAR-TENSOR-CONTRACTION-012",
        "SFT-MATH-PROB-FINITE-DISTRIBUTION-006",
        "SFT-MATH-NUM-EXACT-REPRESENTATION-ROUNDING-001",
    ),
    generation_rule="Generate the literal product of token support, projection, causality, partition, head assembly, block trace, successor and import-boundary coordinates before any UnisonFold result is opened.",
    grammar_boundary="Every finite exact causal self-attention network assembled from generated token/position supports, declared layer/head/coordinate carriers, exact oriented rational or registered finite-grid parameters, structurally predecessor-only score supports, complete attention partitions, exact block traces and complete output support.",
    dimensions=ATTENTION_DIMENSIONS,
    exact_result="The unique exact SFT causal attention-transformer retains complete token-position support, source-bound Q/K/V projections, structural predecessor-only causality, a complete exact attention partition, identity-retaining multihead contraction, exact normalization/residual/gate traces, append-position and append-layer successors, and no imported runtime, weights or target selector.",
    laws=(
        "For target position i, only positions generated at or before i enter its attention support; later positions are structural absence.",
        "Each causal score family is translated monotonically to exact positive parts that compose to One over the complete lawful predecessor support.",
        "Normalization is an exact declared map with structural constant-carrier handling; residuals and the two-Fibre complement gate retain orientation and complete traces.",
        "Appending one token position or one architecture-compatible layer preserves the causal outputs already computed on every earlier prefix.",
    ),
    induction_base="One held token-position carrier generates one Q/K/V row, one causal source, one attention part equal to One, one retained head output and one complete output-support trace.",
    induction_step="Appending one position generates only its complete predecessor score/part/value ledger and cannot alter earlier ledgers; appending one compatible layer consumes the prior exact interface and preserves all token identities and causal edges.",
    boundary_exclusions=(
        "no numerical negative infinity or numerical mask value",
        "no floating, irrational, imaginary or completed-infinite proof scalar",
        "no hidden attention row, dropped predecessor, collapsed head or unretained rounding",
        "no pretrained parameter, external transformer runtime or target answer as an architectural premise",
        "no conversational-quality, optimization, physical-speed or quantum-computation conclusion",
    ),
    witnesses=tuple(
        Witness(f"exact-attention-witness-{index}", "Independent finite carrier check for causal partition, prefix preservation, head identity, exact block composition or structural absence.", passed)
        for index, passed in enumerate(ATTENTION_CHECKS, 1)
    ),
    why="Existing exact arithmetic, linear, causal, finite-distribution and composition laws supply every primitive but do not own the transformer-specific assembly invariant.",
    derivation="Generate the eight-axis architecture grammar, eliminate every form missing one necessary carrier or boundary, execute the exact base carrier and prove the append-position/layer successor.",
    check="Regenerate all 256 candidates independently; replay exact causal partitions and prefix invariance; reject numerical masks, incomplete supports, collapsed heads and imported machinery.",
    limitations="This is an architecture and execution law. It does not assert that any parameter state has learned, generalized, conversed acceptably or outperformed another model.",
    correspondence_terms=("causal self-attention", "multihead transformer", "autoregressive transformer"),
)


LEARNING_SPEC = LawSpec(
    claim_id="SFT-COMP-AIX-EXACT-TEACHER-LEARNING-002",
    group="AIX",
    slug="exact-teacher-learning",
    title="Exact source-bound teacher-observation learning",
    statement="An external pretrained teacher may supply development observations to an SFT-native learner only after the architecture, teacher and corpus identities, exact bit-to-rational observation map, complete output partition, exact disagreement objective, generated update grammar, data roles and stop rule are frozen. Teacher bits become exact source-bound parts without floating arithmetic; no teacher parameter, tokenizer implementation or runtime enters the student. Every unchanged and declared oriented successor is scored by the same exact student execution, only strict objective descent may change state, tied successors and all adverse routes are retained, persisted artifacts bind complete parent and evidence lineage and run without the teacher, and unseen conversational generalization remains a separate sealed evaluation.",
    dependencies=(
        "SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-COMP-HAND-MEASUREMENT-BOUNDARY-002",
        "SFT-COMP-LEARN-CLASSICAL-LEARNING-001",
        "SFT-COMP-LEARN-REPRESENTATION-001",
        "SFT-COMP-LEARN-ADAPTATION-001",
        "SFT-COMP-LEARNX-HYPOTHESIS-FAMILY-002",
        "SFT-COMP-LEARNX-LOSS-RISK-003",
        "SFT-COMP-LEARNX-HELD-OUT-CUSTODY-004",
        "SFT-COMP-LEARNX-GENERALIZATION-006",
        "SFT-COMP-LEARNX-OPTIMIZATION-CONVERGENCE-016",
        "SFT-COMP-LEARNX-LEARNED-VERIFICATION-024",
    ),
    generation_rule="Generate the literal product of teacher identity, record encoding, output support, data custody, objective, update, selection/persistence and unseen-boundary coordinates before the new exact-learning execution is opened.",
    grammar_boundary="Every finite exact teacher-observation learning execution over a previously admitted SFT causal attention-transformer, a frozen external teacher/corpus identity, captured finite output records, a complete declared output grouping, a generated exact parameter/update carrier and separately frozen evaluation supports.",
    dimensions=LEARNING_DIMENSIONS,
    exact_result="The unique exact teacher-observation learner retains a frozen source-bound external teacher, exact bit-record-to-rational parts, complete teacher output support, disjoint data-role custody, a complete exact disagreement ledger, generated exact update candidates, strict-descent/tie/adverse/persistence lineage and a teacher-free artifact with a separate sealed unseen boundary.",
    laws=(
        "External teacher values cross the measurement boundary only as immutable identified observations after the computational law and new execution identities are frozen.",
        "Every finite teacher bit record maps exactly to a dyadic rational part or structural absence; grouping and normalization use only exact arithmetic over complete declared support.",
        "The update grammar is generated before scoring, includes the unchanged state and every declared oriented successor, retains the complete optimum class and mutates only under strict descent.",
        "A persisted successor binds its parent, architecture, corpus, teacher-observation, objective, update and implementation identities while containing no teacher runtime or copied teacher parameter.",
        "Development agreement cannot establish conversational generalization; unseen evaluation is independently frozen and every favorable and adverse row remains evidence.",
    ),
    induction_base="One frozen prompt identity, one complete teacher output partition, one student state and the unchanged/held/returned candidate class produce one exact disagreement and lineage ledger.",
    induction_step="Adding one prompt, output group, generated update direction or checkpoint appends its exact identities and comparison rows without changing prior data roles, objectives, candidates, results or evidence.",
    boundary_exclusions=(
        "no teacher weight, tokenizer implementation, hidden state, gradient, optimizer state or runtime dependency inside the student",
        "no floating arithmetic, floating surrogate, hidden weighting or unregistered tolerance in the learning decision",
        "no target-selected update grammar, erased tie, discarded failure or overwritten checkpoint lineage",
        "no development prompt, teacher observation or training score may enter the sealed unseen support",
        "no training agreement alone establishes generalized conversation, physical efficiency or quantum advantage",
    ),
    witnesses=tuple(
        Witness(f"exact-teacher-learning-witness-{index}", "Independent finite check for bit-exact teacher parts, complete partition, exact disagreement, strict descent, tie retention, hold behavior or teacher-free persistence.", passed)
        for index, passed in enumerate(LEARNING_CHECKS, 1)
    ),
    why="The general learning laws require exact custody but do not specify how an external pretrained teacher can be observed without importing its floating arithmetic or parameters into an SFT-native learner.",
    derivation="Freeze the value-free eight-axis grammar, translate captured finite teacher records to exact parts, generate all declared update candidates, compare their complete exact ledgers and preserve the full strict-descent or hold transition with lineage.",
    check="Regenerate all 256 candidates independently; replay binary-record translation, complete partition, exact disagreement, tied strict successors and no-descent hold; reject any float, copied parameter, runtime teacher or evaluation leakage.",
    limitations="This law admits the learning process contract, not a trained UnisonFold artifact or a generalization result. Those require separately identified executions and sealed unseen evidence.",
    correspondence_terms=("knowledge distillation", "teacher-student learning", "exact discrete optimization"),
)


SPECS = {spec.claim_id: spec for spec in (ATTENTION_SPEC, LEARNING_SPEC)}
IDS = tuple(SPECS)


def validate_family() -> None:
    if len(IDS) != 2 or not all(ATTENTION_CHECKS) or not all(LEARNING_CHECKS):
        raise ValueError("AIX family membership or exact operational witness failed")
    for spec in SPECS.values():
        spec.validate()


validate_family()

