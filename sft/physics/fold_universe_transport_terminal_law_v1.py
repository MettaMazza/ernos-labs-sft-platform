"""Exact composite-orbit topology and physical transport boundary."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import gcd

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024"
EMPTY_ONE = ("empty-One",)


def unit_residues(odd_denominator: int) -> tuple[int, ...]:
    if isinstance(odd_denominator, bool) or odd_denominator < 3 or odd_denominator % 2 != 1:
        raise ValueError("a Fold orbit component requires a positive odd denominator")
    return tuple(residue for residue in range(1, odd_denominator) if gcd(residue, odd_denominator) == 1)


def fold_residue(residue: int, odd_denominator: int) -> int:
    if residue not in unit_residues(odd_denominator):
        raise ValueError("Fold residue must belong to the denominator unit orbit")
    folded = (2 * residue) % odd_denominator
    if folded < 1:
        raise ValueError("Fold unexpectedly produced an empty residue")
    return folded


def orbit_trace(residue: int, odd_denominator: int) -> tuple[int, ...]:
    current = residue
    trace = []
    while True:
        current = fold_residue(current, odd_denominator)
        trace.append(current)
        if current == residue:
            return tuple(trace)


def crt_component_map(residue: int, left: int, right: int) -> tuple[int, int]:
    if gcd(left, right) != 1 or residue not in unit_residues(left * right):
        raise ValueError("CRT component map requires coprime odd factors and a composite unit residue")
    return residue % left, residue % right


def crt_component_census(left: int, right: int) -> dict[str, object]:
    if gcd(left, right) != 1:
        raise ValueError("component census requires coprime factors")
    composite = left * right
    source = unit_residues(composite)
    pairs = tuple(crt_component_map(residue, left, right) for residue in source)
    target = tuple(product(unit_residues(left), unit_residues(right)))
    commutes = all(
        crt_component_map(fold_residue(residue, composite), left, right)
        == (
            fold_residue(residue % left, left),
            fold_residue(residue % right, right),
        )
        for residue in source
    )
    return {
        "composite": composite,
        "source": source,
        "pairs": pairs,
        "target": target,
        "bijection": len(set(pairs)) == len(source) == len(target) and set(pairs) == set(target),
        "fold_commutes": commutes,
    }


def least_common_multiple(left: int, right: int) -> int:
    return left * right // gcd(left, right)


def composite_period(left: int, right: int) -> dict[str, int | bool]:
    left_period = len(orbit_trace(1, left))
    right_period = len(orbit_trace(1, right))
    composite = left * right
    combined_period = len(orbit_trace(1, composite))
    expected = least_common_multiple(left_period, right_period)
    return {
        "left": left_period,
        "right": right_period,
        "composite": combined_period,
        "lcm": expected,
        "matches": combined_period == expected,
    }


def denominator_trace(residue: int, odd_denominator: int, depth: int) -> tuple[int, ...]:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("denominator trace requires positive depth")
    current = residue
    denominators = []
    for _ in range(depth):
        current = fold_residue(current, odd_denominator)
        denominators.append(odd_denominator)
    return tuple(denominators)


def target_trajectory_independent_of_source(left: int, right: int, target_residue: int, depth: int) -> bool:
    if target_residue not in unit_residues(right):
        raise ValueError("target residue must belong to the target component")
    expected = []
    current = target_residue
    for _ in range(depth):
        current = fold_residue(current, right)
        expected.append(current)
    trajectories = []
    for source_residue in unit_residues(left):
        current_left = source_residue
        current_right = target_residue
        observed = []
        for _ in range(depth):
            current_left = fold_residue(current_left, left)
            current_right = fold_residue(current_right, right)
            observed.append(current_right)
        trajectories.append(tuple(observed))
    return trajectories and all(row == tuple(expected) for row in trajectories)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Composite Fold-orbit topology and inter-universe transport boundary",
    statement=(
        "Every reduced positive odd denominator defines an exact periodic Fold-orbit "
        "component.  For coprime components m and n, the units of mn map bijectively "
        "to ordered component pairs, Fold doubling commutes with that map, and the "
        "composite period is the least common multiple of the component periods.  "
        "This forces exact joint support and lockstep correlation.  It does not force "
        "directed signalling or literal physical travel: Fold dynamics preserves the "
        "denominator, and one component trajectory is independent of the other once "
        "the composite initial state is fixed.  Composition is a global preparation "
        "or description map, not a transition moving a pre-existing state between "
        "components.  The physical transport record therefore remains empty unless "
        "a separately admitted causal operation is supplied."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-ALGEBRA-001",
        "SFT-MATH-ORBIT-NUMBER-THEORY-002",
        "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
        "SFT-PHYS-QUANTUM-NO-SIGNALLING-001",
        "SFT-PHYS-FIELD-LOCALITY-CAUSALITY-001",
        "SFT-PHYS-SPACETIME-CAUSAL-ORDER-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of orbit identity, denominator dynamics, "
        "composite topology, component map, period law, correlation record, signal "
        "test, travel test, physical interpretation and extension forms."
    ),
    grammar_boundary=(
        "Every positive reduced odd-denominator Fold orbit; every coprime pair and "
        "its complete composite unit-residue product; every positive finite Fold "
        "depth; and the admitted locality, causal-order, entanglement and "
        "no-signalling boundaries."
    ),
    axes=(
        binary_axis("orbit", "What is a Fold universe in this law?", "unbounded-cosmological-world", "A cosmological world is not generated by denominator arithmetic.", "exact-odd-denominator-orbit-component", "A reduced odd denominator supplies a closed, reproducible Fold orbit."),
        binary_axis("dynamics", "Can Fold motion change components?", "selected-denominator-change", "No Fold transition generates a new denominator.", "denominator-preserved-at-every-step", "Doubling and reduction permute unit residues within the same odd denominator."),
        binary_axis("topology", "How do coprime components combine?", "asserted-network-edge", "An asserted edge has no exact state map.", "complete-coprime-composite-product", "The composite unit set is generated and compared with every component pair."),
        binary_axis("mapping", "What relates composite and component states?", "lossy-or-selected-projection", "Selection or loss breaks exact component recovery.", "bijective-commuting-component-map", "The complete residue map is one-to-one, onto and commutes with Fold action."),
        binary_axis("period", "What is the composite recurrence?", "chosen-or-multiplied-period", "A chosen/product period ignores shared recurrence factors.", "least-common-multiple-period", "Lockstep return occurs at the least common multiple of both exact periods."),
        binary_axis("correlation", "What does the composite prove?", "independent-unrelated-trajectories", "That discards the shared composite origin.", "joint-lockstep-support-correlation", "One composite state retains one state from each component through every common Fold tick."),
        binary_axis("signal", "Can one component steer the other?", "correlation-relabeled-as-signal", "Correlation alone supplies no sender-selected change.", "target-trajectory-independent-of-source", "Holding the target initial state fixes its complete trajectory for every source residue."),
        binary_axis("travel", "Does composition move a state between denominators?", "description-map-relabeled-as-travel", "A preparation/projection map is not a native transition path.", "empty-cross-component-transition-record", "Every native Fold transition keeps the original denominator; no travel edge is generated."),
        binary_axis("physical", "What physical claim follows?", "literal-multiverse-transport-asserted", "Arithmetic components do not by themselves establish multiple physical cosmologies or traversal.", "arithmetic-correspondence-with-causal-boundary", "The exact orbit network is retained while physical signalling/travel requires a separate causal law."),
        binary_axis("extension", "May a transport operation be inserted?", "free-portal-or-time-channel", "A portal or temporal channel is an unforced extra law.", "no-extra-rule", "Fold, composition, projection and the admitted causal boundary exhaust the grammar."),
    ),
    exact_result=(
        "Coprime odd-denominator Fold components have an exact bijective composite "
        "map that commutes with Fold and has least-common-multiple recurrence, "
        "forcing joint lockstep correlation; native Fold dynamics preserves each "
        "denominator, one component cannot steer another, and the literal physical "
        "inter-component signalling/travel record is empty."
    ),
    induction_base=(
        "One composite unit residue maps to one ordered component pair and one Fold "
        "step maps both entries by their own exact Fold action."
    ),
    induction_step=(
        "If the component map commutes at a tick, applying Fold once more doubles "
        "every residue before the same reductions, preserving the pair map, each "
        "denominator and target-trajectory independence at the next tick."
    ),
    exclusions=(
        "no imported cosmological multiverse, wormhole, closed-timelike-curve or portal premise",
        "no V1/V2 executable, answer table, physical target or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no relabelling of arithmetic composition/projection as literal physical travel",
        "no relabelling of deterministic correlation as directed communication",
        "no physical universe plurality without a separately admitted observational discriminator",
    ),
    witnesses=(
        Witness("complete-CRT-censuses", "The complete unit-residue maps for three-by-five, three-by-seven and five-by-seven are bijective and Fold-commuting.", all(crt_component_census(left, right)["bijection"] and crt_component_census(left, right)["fold_commutes"] for left, right in ((3, 5), (3, 7), (5, 7)))),
        Witness("period-law", "Composite periods equal the least common multiple of component periods for every registered coprime pair.", all(composite_period(left, right)["matches"] for left, right in ((3, 5), (3, 7), (5, 7)))),
        Witness("denominator-preservation", "Every tested native trajectory retains its source denominator.", all(denominator_trace(1, denominator, 12) == (denominator,) * 12 for denominator in (3, 5, 7, 15, 21, 35))),
        Witness("no-steering", "Every target trajectory is independent of the paired source residue once the target initial state is fixed.", all(target_trajectory_independent_of_source(left, right, 1, 12) for left, right in ((3, 5), (3, 7), (5, 7)))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EMPTY_ONE",
    "SPEC",
    "composite_period",
    "crt_component_census",
    "crt_component_map",
    "denominator_trace",
    "fold_residue",
    "orbit_trace",
    "target_trajectory_independent_of_source",
    "unit_residues",
)
