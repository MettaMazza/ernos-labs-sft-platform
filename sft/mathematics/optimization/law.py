"""Force exact finite optimization from feasible carriers and witnessed order."""

from __future__ import annotations

from fractions import Fraction

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-OPTIMIZATION-001"


def feasible_carrier(candidates: tuple[str, ...], predicates: tuple[tuple[str, bool], ...]) -> tuple[str, ...]:
    if not candidates or len(set(candidates)) != len(candidates):
        raise ValueError("optimization requires a complete canonical candidate carrier")
    verdicts = dict(predicates)
    if set(verdicts) != set(candidates):
        raise ValueError("every candidate must have one source-bound feasibility verdict")
    return tuple(candidate for candidate in candidates if verdicts[candidate])


def undominated(feasible: tuple[str, ...], preferred: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    if not feasible:
        raise ValueError("an admitted optimization instance requires a nonempty feasible carrier")
    if any(better not in feasible or worse not in feasible or better == worse for better, worse in preferred):
        raise ValueError("preference cells must remain inside the feasible carrier")
    return tuple(
        candidate for candidate in feasible
        if not any(worse == candidate for _, worse in preferred)
    )


def exact_optimum(feasible: tuple[str, ...], preferred: tuple[tuple[str, str], ...]):
    held = undominated(feasible, preferred)
    return held[0] if len(held) == 1 else ("retained-equivalence-class", held)


def respects_constraints(candidate: str, constraints: tuple[tuple[str, tuple[str, ...]], ...]) -> bool:
    return all(candidate in allowed for _, allowed in constraints)


def pareto_frontier(
    feasible: tuple[str, ...],
    criteria: tuple[tuple[str, tuple[tuple[str, str], ...]], ...],
) -> tuple[str, ...]:
    def dominates(left: str, right: str) -> bool:
        never_worse = all((left, right) in relation or left == right for _, relation in criteria)
        strictly_better = any((left, right) in relation for _, relation in criteria)
        return never_worse and strictly_better
    return tuple(candidate for candidate in feasible if not any(
        other != candidate and dominates(other, candidate) for other in feasible
    ))


def exact_approximation(candidate_cells: int, optimum_cells: int) -> Fraction:
    if candidate_cells < optimum_cells or optimum_cells < 1:
        raise ValueError("approximation requires positive generated cell counts and a valid lower optimum")
    return Fraction(optimum_cells, candidate_cells)


_candidates = ("a", "b", "c")
_feasible = feasible_carrier(_candidates, (("a", True), ("b", True), ("c", False)))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite optimization and retained optima",
    statement=(
        "An admitted optimization problem is a complete canonical candidate carrier, a source-bound exact "
        "feasibility relation and a witnessed preference relation. Solutions are the complete undominated held "
        "selection; uniqueness is claimed only for a singleton, while ties and incomparable Pareto alternatives "
        "remain explicit. Constraints, decomposition and approximation are exact trace relations without floating "
        "objectives, negative penalties or free tuning parameters."
    ),
    dependencies=(
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule=(
        "Generate the complete product of candidate coverage, feasibility, preference, optimum selection, tie "
        "retention, constraint provenance, decomposition, approximation and extra-objective status."
    ),
    grammar_boundary=(
        "All finite optimization instances generated from canonical candidates, exact predicates, held preference "
        "relations, complete dominance checks, interface-preserving decomposition and exact positive part bounds."
    ),
    dimensions=(
        binary_dimension("candidates", "What fixes the search domain?", "sampled-candidates", "Sampling cannot prove that a better generated candidate was not omitted.", "complete-canonical-candidates", "Every registered candidate form occurs once."),
        binary_dimension("feasibility", "What fixes feasibility?", "implicit-constraint", "An implicit constraint has no candidate-level check trace.", "source-bound-verdicts", "Every candidate receives one exact verdict from each registered constraint."),
        binary_dimension("preference", "What fixes better-than?", "floating-score", "A floating score imports scale and precision choices.", "witnessed-order-relation", "Every preference is an exact retained candidate pair."),
        binary_dimension("solution", "What fixes an optimum?", "first-found", "First-found depends on traversal presentation.", "complete-undominated-selection", "Every feasible candidate is compared and all undominated forms are retained."),
        binary_dimension("ties", "How are equal or incomparable optima treated?", "silent-tie-break", "A silent tie-break adds a free preference.", "retained-equivalence-class", "All jointly optimal or incomparable surviving forms remain explicit."),
        binary_dimension("constraints", "How are constraints admitted?", "penalty-parameter", "A tunable penalty is a free parameter and can select the answer.", "exact-membership-predicate", "Each constraint is a source-bound exact allowed-form relation."),
        binary_dimension("decomposition", "When may a problem decompose?", "assumed-separability", "Shared constraints can invalidate separate optima.", "exact-interface-factorization", "Subproblems compose only when all shared interface relations are retained."),
        binary_dimension("approximation", "What fixes an approximation guarantee?", "decimal-error", "A decimal error imports rounding and a scale.", "exact-positive-part-bound", "The candidate/optimum relation is a generated exact part certificate."),
        binary_dimension("addition", "Is another objective supplied?", "extra-objective-or-tie-rule", "An added score or tie rule is not forced by the instance.", "no-extra-objective", "Only registered feasibility and preference relations select solutions."),
    ),
    exact_result=(
        "The optimization kernel is complete canonical candidates, source-bound feasibility, exact preference, "
        "complete undominated selection, retained ties, exact constraints and interfaces, and positive-part bounds "
        "without an added objective."
    ),
    laws=(
        "optimization may eliminate a candidate only with a retained feasible dominator witness",
        "all undominated candidates survive and uniqueness is a separately checked singleton property",
        "Pareto comparison retains incomparability across exact criteria",
        "decomposition is lawful only with complete shared-interface factorization",
        "approximation is an exact generated part relation rather than a rounded scalar",
    ),
    induction_base="A One-candidate feasible carrier has that candidate as its unique complete undominated selection.",
    induction_step=(
        "Adding one fresh candidate generates its feasibility verdicts and every preference pair with prior feasible "
        "forms. It is either eliminated by a retained dominator, eliminates witnessed dominated forms, or joins the "
        "retained optimal class; no prior optimum is silently discarded."
    ),
    boundary_exclusions=(
        "no floating objective or tolerance",
        "no negative penalty term",
        "no tunable regularizer or tie-break parameter",
        "no unenumerated candidate domain",
    ),
    witnesses=(
        Witness("feasible-selection", "The complete verdict relation retains exactly a and b.", _feasible == ("a", "b")),
        Witness("unique-optimum", "A witnessed a-over-b relation leaves a as the singleton optimum.", exact_optimum(_feasible, (("a", "b"),)) == "a"),
        Witness("ties-retained", "With no forced preference both feasible forms survive explicitly.", exact_optimum(_feasible, ()) == ("retained-equivalence-class", ("a", "b"))),
        Witness("constraint-membership", "The witness candidate is checked against every exact allowed set.", respects_constraints("a", (("first", ("a", "b")), ("second", ("a", "c"))))),
        Witness("pareto-incomparability", "Opposed exact criteria retain both incomparable forms.", pareto_frontier(("a", "b"), (("left", (("a", "b"),)), ("right", (("b", "a"),)))) == ("a", "b")),
        Witness("exact-bound", "Three generated cells against a two-cell optimum produce exact two-over-three.", exact_approximation(3, 2) == Fraction(2, 3)),
    ),
    why=(
        "Search and decision require lawful selection among alternatives. Exact dominance and tie retention prevent "
        "a familiar score, tolerance or traversal order from selecting the result."
    ),
    derivation=(
        "Orders supply witnessed preference and incomparability; graphs supply search relations and decomposable "
        "interfaces; exact arithmetic supplies part bounds. Nine choices force the complete undominated kernel."
    ),
    check=(
        "Execute all 512 kernels, verify feasibility coverage, unique and tied optima, exact constraints, Pareto "
        "incomparability and exact approximation, then independently regenerate the candidate census."
    ),
    limitations=(
        "This closes exact finite optimization structure. Complexity of finding the complete frontier and laws "
        "for particular objective families belong to the algorithms and complexity branches."
    ),
    correspondence_terms=("feasible set", "objective", "optimum", "Pareto frontier", "constraint", "approximation ratio"),
)
