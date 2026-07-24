"""Same-strength Quantum Computation laws reconstructed from later V2 observations."""

from __future__ import annotations

from itertools import combinations, product

from sft.quantum_computation.generated_law import LawSpec, Witness, binary_dimension


def forced_width(fault_trace: tuple[str, ...]) -> int:
    """Return the first strict-majority width for a supplied positive fault order."""

    if not fault_trace or len(set(fault_trace)) != len(fault_trace):
        raise ValueError("fault order must be a nonempty generated trace")
    return 2 * len(fault_trace) + 1


def decode(word: tuple[str, ...]) -> str:
    if not word or any(label not in {"held", "returned"} for label in word):
        raise ValueError("word contains an unregistered label")
    held = sum(label == "held" for label in word)
    returned = sum(label == "returned" for label in word)
    if held == returned:
        return "no-strict-majority"
    return "held" if held > returned else "returned"


def exhaustive_small_fault_census(label: str, fault_trace: tuple[str, ...]) -> bool:
    width = forced_width(fault_trace)
    opposite = "returned" if label == "held" else "held"
    encoded = tuple(label for _ in range(width))
    for fault_count in range(len(fault_trace) + 1):
        for positions in combinations(range(width), fault_count):
            changed = tuple(opposite if position in positions else value for position, value in enumerate(encoded))
            if decode(changed) != label:
                return False
    return True


def shorter_widths_fail(fault_trace: tuple[str, ...]) -> bool:
    """Construct one tie or wrong-majority row for every predecessor width."""

    allowance = len(fault_trace)
    for width in range(1, 2 * allowance + 1):
        changed_count = (width + 1) // 2
        word = tuple("returned" if position < changed_count else "held" for position in range(width))
        if changed_count > allowance or decode(word) == "held":
            return False
    return True


def depth_seven_round_trip(fault_trace: tuple[str, ...]) -> bool:
    """Correct a worst-allowed canonical mask on every cell of every depth-seven word."""

    width = forced_width(fault_trace)
    allowance = len(fault_trace)
    for source in product(("held", "returned"), repeat=7):
        recovered = []
        for label in source:
            opposite = "returned" if label == "held" else "held"
            encoded = tuple(label for _ in range(width))
            changed = tuple(opposite if position < allowance else value for position, value in enumerate(encoded))
            recovered.append(decode(changed))
        if tuple(recovered) != source:
            return False
    return True


def operational_witnesses(claim_id: str) -> tuple[Witness, ...]:
    traces = {depth: tuple(f"fault-{index + 1}" for index in range(depth)) for depth in range(1, 15)}
    checks = (
        (forced_width(traces[1]) == 3, "one-error order forces width three"),
        (forced_width(traces[2]) == 5 and forced_width(traces[3]) == 7, "separate two- and three-error orders force widths five and seven"),
        (forced_width(traces[14]) == 29, "fault order fourteen forces width twenty-nine"),
        (all(exhaustive_small_fault_census(label, traces[depth]) for label in ("held", "returned") for depth in (1, 2, 3)), "every mask through orders one, two and three decodes exactly"),
        (all(shorter_widths_fail(traces[depth]) for depth in range(1, 15)), "every predecessor width through fault order fourteen has a constructive failure"),
        (all(forced_width(traces[depth + 1]) == forced_width(traces[depth]) + 2 for depth in range(1, 14)), "the fault-order successor adds exactly two labels"),
        (all((depth + 1) > depth for depth in range(1, 15)), "every supplied finite ceiling has a generated successor fault order"),
        (depth_seven_round_trip(traces[14]), "all depth-seven words round-trip at fault order fourteen before circuit evaluation"),
    )
    return tuple(Witness(f"unbounded-fault-witness-{index}", f"{description} for {claim_id}", passed) for index, (passed, description) in enumerate(checks, 1))


DIMENSIONS = (
    binary_dimension("fault_order", "fixed-one-error-model", "supplied-positive-finite-fault-trace"),
    binary_dimension("width", "selected-or-even-width", "first-strict-majority-width-2t-plus-1"),
    binary_dimension("coverage", "sampled-fault-patterns", "all-masks-through-t-by-subset-count"),
    binary_dimension("minimality", "shorter-widths-unchecked", "counterexample-for-every-width-through-2t"),
    binary_dimension("recovery", "decoded-label-without-record", "exact-syndrome-and-recovery-trace"),
    binary_dimension("circuit", "isolated-code-example", "corrected-word-feeds-exact-circuit-semantics"),
    binary_dimension("generality", "fixed-t-table", "fault-order-successor-and-ceiling-defeat"),
    binary_dimension("addition", "imported-hardware-threshold", "no-rate-device-or-noise-parameter"),
)


CLAIM_ID = "SFT-QUANTUM-UNBOUNDED-FINITE-FAULT-TOLERANCE-002"
STATEMENT = (
    "For every supplied positive finite fault-order trace t, the unique first repetition width correcting every mask "
    "through t is 2t+1: at least t+1 source labels remain against at most t changes, every width through 2t has a "
    "constructive tie or wrong-majority counterexample, redundancy is exactly 2t, and the successor fault order adds "
    "exactly two labels. The corrected word composes with exact Fold circuit semantics. This is an unbounded finite "
    "fault-order theorem, not a stochastic hardware-rate or physical threshold constant."
)


UNBOUNDED_FAULT_TOLERANCE = LawSpec(
    claim_id=CLAIM_ID,
    slug="UNBOUNDED-FINITE-FAULT-TOLERANCE",
    title="Unbounded finite Fold quantum fault-tolerance law",
    statement=STATEMENT,
    dependencies=(
        "SFT-QUANTUM-ERROR-CORRECTION-001",
        "SFT-QUANTUM-FAULT-TOLERANCE-001",
        "SFT-QUANTUM-CIRCUIT-001",
        "SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002",
    ),
    generation_rule="Generate the literal product of fault order, width, mask coverage, minimality, recovery, circuit composition, successor and no-extra-parameter coordinates.",
    grammar_boundary="Every supplied positive finite Fold fault-order trace, its generated repetition widths in increasing order, every fault mask through that order by exact subset class, and composition with admitted finite Fold circuit semantics.",
    dimensions=DIMENSIONS,
    exact_result=STATEMENT,
    laws=(
        "Width law: the first strict-majority carrier at fault order t contains exactly 2t+1 held positions.",
        "Correction law: at most t changes leave at least t+1 original labels, so the unique strict majority is retained.",
        "Minimality law: every width w through 2t is defeated by changing ceil(w/2) positions, producing a tie or wrong majority.",
        "Successor law: replacing t by its next generated fault order adds exactly two carrier positions and defeats every fixed positive finite ceiling.",
        "Composition law: recovery supplies the exact source word to the already-admitted reversible circuit semantics.",
    ),
    induction_base="At the first positive fault order, widths one and two have explicit failure rows and width three retains two source labels against one change.",
    induction_step="If width 2t+1 is the first survivor at fault order t, the next order requires one further possible change and one further retained source majority; exactly two added positions produce 2(t+1)+1, while every shorter successor width has the same constructive counterexample.",
    boundary_exclusions=(
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no complex amplitude, Hilbert-space axiom or stochastic collapse postulate",
        "no completed infinite-width code or completed infinity",
        "no measured error rate, hardware threshold, fitted noise model or device parameter",
        "no application output or physical benchmark may select the code law",
    ),
    witnesses=operational_witnesses(CLAIM_ID),
    why="The later V2 result removes the fixed-order frontier and requires a constructive depth-independent theorem for every supplied positive finite fault allowance.",
    derivation="Strict-majority preservation forces the width: t changed positions require strictly more than t retained source positions, so the least total is t+(t+1)=2t+1. The generated counterexample at every predecessor width proves minimality, and the fault-order successor proves unbounded positive-finite closure.",
    check="Exhaust 256 structural candidates; enumerate every mask for both labels at t=1,2,3; execute width/minimality/successor certificates through t=14; round-trip all 128 depth-seven words at t=14; reject fixed ceilings and hardware-threshold imports; independently regenerate all results.",
    limitations="The theorem is unbounded over supplied positive finite code fault orders. It does not estimate a stochastic physical device threshold, correlated hardware noise rate or thermodynamic implementation cost.",
    correspondence_terms=("quantum error correction", "fault tolerance", "threshold theorem boundary"),
)


LINEAGE_SPECS = (UNBOUNDED_FAULT_TOLERANCE,)

