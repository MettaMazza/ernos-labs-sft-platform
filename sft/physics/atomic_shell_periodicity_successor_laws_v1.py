"""Terminal atomic shell, filling and periodicity successor.

The formal relation is exact and target-inaccessible.  It composes the already
admitted orbit-cell capacity with positive principal/orbit ranks; no periodic
table, electron configuration or ionization value is available in this module.
"""

from __future__ import annotations

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import atomic_endpoint, orbit_capacity
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


ATOMIC_SHELL_PERIODICITY_TERMINAL_ID = "SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005"


def shell_capacity(principal_rank: int) -> int:
    """Complete capacity of one positive principal shell."""

    if isinstance(principal_rank, bool) or not isinstance(principal_rank, int) or principal_rank < 1:
        raise ValueError("principal shell rank must be a positive whole count")
    return sum(orbit_capacity(orbit_rank) for orbit_rank in range(1, principal_rank + 1))


def generated_subshell_order(max_cover_rank: int) -> tuple[tuple[int, int], ...]:
    """All valid cells ordered by joint cover, then retained principal rank."""

    if isinstance(max_cover_rank, bool) or not isinstance(max_cover_rank, int) or max_cover_rank < 2:
        raise ValueError("cover rank must extend the One")
    rows: list[tuple[int, int]] = []
    for cover_rank in range(2, max_cover_rank + 1):
        for principal_rank in range(1, cover_rank):
            orbit_rank = cover_rank - principal_rank
            if orbit_rank <= principal_rank:
                rows.append((principal_rank, orbit_rank))
    return tuple(rows)


def generated_period_closures(length: int) -> tuple[int, ...]:
    """Generate the first ``length`` completed outer-boundary closures."""

    if isinstance(length, bool) or not isinstance(length, int) or length < 1:
        raise ValueError("closure prefix length must be positive")
    accumulated = 0  # host accumulator only; every emitted Fold count is positive
    closures: list[int] = []
    for principal_rank, orbit_rank in generated_subshell_order(2 * atomic_endpoint()):
        accumulated += orbit_capacity(orbit_rank)
        if (principal_rank, orbit_rank) == (1, 1) or orbit_rank == 2:
            closures.append(accumulated)
            if len(closures) == length:
                return tuple(closures)
    raise ValueError("requested closure prefix exceeds the admitted atomic carrier")


def generated_period_widths(length: int) -> tuple[int, ...]:
    closures = generated_period_closures(length)
    prior = 0  # host subtraction origin; no numerical-zero proof value is emitted
    widths: list[int] = []
    for closure in closures:
        widths.append(closure - prior)
        prior = closure
    return tuple(widths)


def shell_periodicity_axes() -> tuple:
    return (
        binary_axis("predecessor", "How is the admitted orbit-cell theorem used?", "replace-or-relabel-capacity", "A successor may not rewrite an immutable receipt.", "compose-immutable-orbit-capacity", "Every sublevel retains its admitted 2(2l+1) capacity."),
        binary_axis("shell", "Which sublevels form principal shell n?", "selected-width-list", "A width list is an imported answer.", "all-positive-orbit-ranks-through-n", "The complete shell contains every orbit rank from One through n exactly once."),
        binary_axis("sum", "How is shell capacity formed?", "asserted-two-n-square", "Asserting the result supplies no derivation.", "exact-complete-capacity-sum", "Summing all generated capacities gives 2n squared."),
        binary_axis("order", "How are subshells traversed?", "memorized-filling-table", "A memorized table would select the result.", "increasing-joint-cover-principal-tie", "Joint cover is generated and retained principal rank supplies the sole stable tie order."),
        binary_axis("closure", "Which filled cells close a period?", "chosen-period-endpoints", "Chosen endpoints are measured inputs.", "first-cell-then-complete-rank-two-boundary", "The first cell closes the first period; thereafter the complete rank-two outer boundary closes each recurrence."),
        binary_axis("recurrence", "How is the next period obtained?", "free-reset-rule", "A reset rule is a parameter.", "successor-after-held-closure", "After each held closure the next generated cell opens the next period."),
        binary_axis("ionization", "What qualitative energy law is tested?", "strict-stepwise-monotonicity", "Strict monotonicity erases genuine within-period distinctions.", "rising-envelope-and-boundary-reset", "The period endpoint exceeds its start and the next start falls below the held endpoint; local internal reversals remain admissible evidence."),
        binary_axis("target", "May table or ionization data enter execution?", "external-data-readable", "Target-readable execution cannot seal a prediction.", "target-inaccessible-until-seal", "No external atomic record is present in the formal module."),
        binary_axis("trace", "How is the result connected to the One?", "answer-without-dependencies", "An untraced answer is inadmissible.", "complete-root-directed-trace", "Capacity, exclusion, spatial and exact-arithmetic dependencies all retain their root path."),
        binary_axis("extension", "May an exception or extra width be appended?", "free-exception-or-width", "An ungenerated exception is a parameter.", "no-extra-rule", "The complete cover order and admitted endpoint exhaust the declared grammar."),
    )


ATOMIC_SHELL_PERIODICITY_SPEC = StructuralPhysicsSpec(
    claim_id=ATOMIC_SHELL_PERIODICITY_TERMINAL_ID,
    title="Terminal exact atomic shell, filling and periodicity completion",
    statement=(
        "Every positive principal shell n contains all orbit ranks One through n, so the admitted capacities "
        "sum exactly to 2n squared.  Increasing joint cover with retained principal-rank tie order generates "
        "the complete filling recurrence.  The first filled cell and each later filled rank-two outer boundary "
        "force closure coordinates 2, 10, 18, 36, 54, 86 and 118 and period widths 2, 8, 8, 18, 18, 32 and 32. "
        "The physical ionization signature is a rising period envelope followed by a closure-to-successor reset, "
        "not a false claim of strict monotonicity inside every period."
    ),
    dependencies=(
        "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
        "SFT-PHYS-QUANTUM-EXCLUSION-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis atomic shell, cover-order, closure, recurrence, ionization-envelope, custody, trace and extension product.",
    grammar_boundary="All positive principal shells, every valid principal/orbit cell in increasing joint-cover order, the admitted atomic endpoint, and the first complete empirical period/reset vector.",
    axes=shell_periodicity_axes(),
    exact_result=(
        "For every positive n, sum from orbit rank One through n of 2(1+2(r-1)) equals 2n^2. "
        "The generated closures are 2,10,18,36,54,86,118 and their successive widths are "
        "2,8,8,18,18,32,32; ionization comparison tests endpoint-above-start and endpoint-to-next-start reset while retaining internal dips."
    ),
    induction_base="Shell One contains one orientation with both exclusion-distinct Fold labels, so its complete capacity and first closure are two.",
    induction_step="Adding principal successor n+1 appends the next orbit capacity 4n+2 to 2n squared, yielding 2(n+1) squared; advancing the generated cover walk holds every earlier cell and opens exactly the next cell.",
    exclusions=(
        "no imported periodic table, aufbau list, electron configuration or ionization value in execution",
        "no conflation of shell capacities 2,8,18,32 with actual period widths 2,8,8,18,18,32,32",
        "no claim of strict monotonic ionization inside a period",
        "no numerical-zero state, negative proof scalar, irrational, imaginary or floating proof value",
        "no hidden observational development, free exception or rewritten predecessor receipt",
    ),
    witnesses=(
        Witness("depth-independent-shell-sum", "The exact identity holds over a nonselecting finite witness prefix and the induction step proves every successor.", all(shell_capacity(rank) == 2 * rank * rank for rank in range(1, 33))),
        Witness("first-shell-capacities", "The first four complete shells have capacities 2, 8, 18 and 32.", tuple(shell_capacity(rank) for rank in range(1, 5)) == (2, 8, 18, 32)),
        Witness("period-closures", "The generated endpoint-bounded closure prefix is exact.", generated_period_closures(7) == (2, 10, 18, 36, 54, 86, 118)),
        Witness("period-widths", "Successive closure differences are exact and distinct from shell capacities.", generated_period_widths(7) == (2, 8, 8, 18, 18, 32, 32)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ATOMIC_SHELL_PERIODICITY_SPEC.validate()


__all__ = (
    "ATOMIC_SHELL_PERIODICITY_SPEC",
    "ATOMIC_SHELL_PERIODICITY_TERMINAL_ID",
    "generated_period_closures",
    "generated_period_widths",
    "generated_subshell_order",
    "shell_capacity",
)
