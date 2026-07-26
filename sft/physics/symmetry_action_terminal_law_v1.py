"""Finite Fold symmetry/conservation and least-action correspondence.

Conventional Noether and variational equations are not premises.  A symmetry
is generated as a complete bijection preserving transition incidence, exact
step carriers and held fibres.  A descending path carries only exact positive
step magnitudes.  These definitions make the local and global statements
machine-checkable without signed action values or a continuum.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
from math import gcd

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


CLAIM_ID = "SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016"


def fold_part(value: Fraction) -> Fraction:
    """Execute exact double-and-cast on one positive part of the One."""

    if not isinstance(value, Fraction) or value <= 0 or value > 1:
        raise ValueError("Fold requires one exact positive part of the One")
    doubled = value + value
    return doubled if doubled <= 1 else doubled - 1


def reduced_odd_denominator_core(value: Fraction) -> int:
    """Return the positive odd carrier left after complete binary division."""

    if not isinstance(value, Fraction) or value <= 0 or value > 1:
        raise ValueError("odd-core custody requires one exact positive Fold part")
    denominator = value.denominator
    while denominator % 2 == 0:
        denominator //= 2
    return denominator


def odd_core_is_conserved(value: Fraction) -> bool:
    """Check the Fold invariant used as the native symmetry charge."""

    return reduced_odd_denominator_core(value) == reduced_odd_denominator_core(
        fold_part(value)
    )


def dyadic_fold_descent(value: Fraction) -> tuple[Fraction, ...]:
    """Retain the unique Fold trajectory from a dyadic part to the One."""

    if reduced_odd_denominator_core(value) != 1:
        raise ValueError("fixed-point descent is the exact dyadic basin")
    trace = (value,)
    current = value
    while current != 1:
        current = fold_part(current)
        trace += (current,)
    return trace


def dyadic_denominator_rank(value: Fraction) -> int:
    """Count the positive binary divisions retained by a nonterminal part."""

    if value == 1 or reduced_odd_denominator_core(value) != 1:
        raise ValueError("rank requires a nonterminal dyadic Fold part")
    denominator = value.denominator
    rank = 1
    while denominator > 2:
        denominator //= 2
        rank += 1
    return rank


def descent_rank_strictly_falls(trace: tuple[Fraction, ...]) -> bool:
    """Every nonterminal Fold act removes exactly one binary denominator layer."""

    if len(trace) < 2 or trace[-1] != 1:
        return False
    for source, target in zip(trace, trace[1:]):
        if target == 1:
            if source.denominator != 2:
                return False
        elif dyadic_denominator_rank(source) != dyadic_denominator_rank(target) + 1:
            return False
    return True


def oriented_magnitude(
    source: Fraction, target: Fraction
) -> tuple[str, Fraction] | tuple[()]:
    """Represent direction by a label and magnitude by an exact positive part."""

    if (
        not isinstance(source, Fraction)
        or not isinstance(target, Fraction)
        or source <= 0
        or target <= 0
    ):
        raise ValueError("path coordinates must be exact positive carriers")
    if source == target:
        return ()
    if source > target:
        return "toward-lower-carrier", source - target
    return "toward-upper-carrier", target - source


def path_action(path: tuple[Fraction, ...]) -> Fraction:
    """Total positive variation along a finite generated path."""

    if len(path) < 2:
        raise ValueError("an action path requires two generated endpoints")
    first = oriented_magnitude(path[0], path[1])
    if first == ():
        raise ValueError("an empty repeated-state act is not a path transition")
    total = first[1]
    for source, target in zip(path[1:], path[2:]):
        step = oriented_magnitude(source, target)
        if step == ():
            raise ValueError("an empty repeated-state act is not a path transition")
        total += step[1]
    if total <= 0:
        raise ValueError("path action must retain a positive carrier")
    return total


def endpoint_separation(path: tuple[Fraction, ...]) -> Fraction:
    step = oriented_magnitude(path[0], path[-1])
    if step == ():
        raise ValueError("distinct endpoints are required")
    return step[1]


def is_monotone_descent(path: tuple[Fraction, ...]) -> bool:
    return all(
        oriented_magnitude(source, target)[0] == "toward-lower-carrier"
        for source, target in zip(path, path[1:])
    )


def descent_telescopes(path: tuple[Fraction, ...]) -> bool:
    if not is_monotone_descent(path):
        return False
    return path_action(path) == endpoint_separation(path)


def detour_cannot_lower_action(path: tuple[Fraction, ...]) -> bool:
    return path_action(path) >= endpoint_separation(path)


def charge_preserving_bijections(
    charges: tuple[str, ...],
) -> tuple[tuple[int, ...], ...]:
    """Enumerate the complete finite symmetry class of one conserved partition."""

    if not charges:
        raise ValueError("a conserved partition requires generated support")
    indices = tuple(range(len(charges)))
    return tuple(
        permutation
        for permutation in permutations(indices)
        if all(charges[index] == charges[permutation[index]] for index in indices)
    )


def preserves_edges_and_carriers(
    permutation: tuple[int, ...],
    edges: tuple[tuple[int, int, Fraction], ...],
) -> bool:
    edge_set = set(edges)
    return all(
        (permutation[source], permutation[target], carrier) in edge_set
        for source, target, carrier in edges
    )


def complete_symmetry_class(
    charges: tuple[str, ...],
    edges: tuple[tuple[int, int, Fraction], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        permutation
        for permutation in charge_preserving_bijections(charges)
        if preserves_edges_and_carriers(permutation, edges)
    )


def symmetry_preserves_charge(
    permutation: tuple[int, ...], charges: tuple[str, ...]
) -> bool:
    return all(
        charges[index] == charges[permutation[index]]
        for index in range(len(charges))
    )


def all_small_paths_obey_action_boundary() -> bool:
    values = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    for length in (2, 3, 4, 5):
        for path in product(values, repeat=length):
            if path[0] == path[-1] or any(a == b for a, b in zip(path, path[1:])):
                continue
            if not detour_cannot_lower_action(path):
                return False
            if is_monotone_descent(path) and not descent_telescopes(path):
                return False
    return True


def all_reduced_fold_parts_preserve_odd_core(denominator_limit: int) -> bool:
    """Finite control census for the depth-independent denominator proof."""

    if isinstance(denominator_limit, bool) or denominator_limit < 2:
        raise ValueError("control boundary requires a positive denominator extension")
    return all(
        odd_core_is_conserved(Fraction(numerator, denominator))
        for denominator in range(2, denominator_limit + 1)
        for numerator in range(1, denominator + 1)
        if gcd(numerator, denominator) == 1
    )


def all_dyadic_parts_descend(depth_limit: int) -> bool:
    """Finite control census for the arbitrary-depth dyadic induction."""

    if isinstance(depth_limit, bool) or depth_limit < 1:
        raise ValueError("dyadic control boundary requires a positive depth")
    for depth in range(1, depth_limit + 1):
        denominator = 2**depth
        for numerator in range(1, denominator, 2):
            trace = dyadic_fold_descent(Fraction(numerator, denominator))
            if (
                len(trace) != depth + 1
                or not descent_rank_strictly_falls(trace)
                or trace[-1] != 1
            ):
                return False
    return True


_CHARGES = ("left-fibre", "left-fibre", "right-fibre", "right-fibre")
_EDGES = (
    (0, 1, Fraction(1, 4)),
    (1, 0, Fraction(1, 4)),
    (2, 3, Fraction(1, 4)),
    (3, 2, Fraction(1, 4)),
)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Finite Fold symmetry, conservation and least action",
    statement=(
        "Exact Fold double-and-cast preserves the reduced odd denominator core of "
        "every positive rational part, giving a depth-independent native conserved "
        "charge.  In every finite generated transition support, a symmetry is the "
        "complete bijection that preserves transition incidence, exact positive "
        "step carriers and held observation fibres.  Its fibre identity is "
        "therefore conserved.  Conversely, complete enumeration of the bijections "
        "preserving any registered conserved partition generates that partition's "
        "symmetry class.  In the exact dyadic basin, every Fold act removes one "
        "binary denominator layer and the unique trajectory reaches the One, where "
        "the identity act is empty One.  For every finite ranked descent path, action is the "
        "complete sum of exact positive oriented step magnitudes.  Every monotone "
        "descent telescopes exactly to the endpoint separation; any detour retains "
        "an additional positive up/down carrier and cannot lower the action.  Thus "
        "the local dyadic descent and global minimum-variation reading are one exact "
        "Fold structure at the declared boundary."
    ),
    dependencies=(
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ORDER-LATTICE-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORBIT-NUMBER-THEORY-002",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-FOUNDATION-PART-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of support, symmetry, incidence, carrier, "
        "conserved-fibre, converse, action, path and extension forms."
    ),
    grammar_boundary=(
        "Every exact positive rational Fold part; the complete dyadic fixed-point "
        "basin; every finite generated state support; every bijection of that support; "
        "every registered exact transition/carrier relation and held fibre "
        "partition; every finite path of distinct adjacent states with exact "
        "positive ranked coordinates."
    ),
    axes=(
        binary_axis(
            "support",
            "Which state space is examined?",
            "selected-or-continuous-state-sample",
            "A sample or continuum premise is not a complete generated domain.",
            "complete-finite-generated-support",
            "Every generated state is retained once.",
        ),
        binary_axis(
            "symmetry",
            "What is a symmetry?",
            "named-transformation-without-census",
            "A named transformation does not prove bijection or completeness.",
            "complete-bijection-enumeration",
            "Every permutation is generated and decided.",
        ),
        binary_axis(
            "incidence",
            "What must the symmetry preserve?",
            "state-labels-without-transition-law",
            "Ignoring incidence can turn a non-dynamics map into a symmetry.",
            "transition-incidence-preserved",
            "Every source/target transition maps to an admitted transition.",
        ),
        binary_axis(
            "carrier",
            "What happens to physical step carriers?",
            "free-rescaling-under-symmetry",
            "A free rescaling changes the physical law.",
            "exact-positive-carrier-preserved",
            "Every mapped edge retains the same exact carrier.",
        ),
        binary_axis(
            "conserved",
            "Which quantity is conserved?",
            "answer-only-scalar",
            "A scalar detached from support has no conservation trace.",
            "odd-core-and-held-invariant-fibre",
            "Fold preserves the reduced odd denominator core and every enumerated symmetry remains inside its held fibre.",
        ),
        binary_axis(
            "converse",
            "How is the converse closed?",
            "assert-every-conservation-has-unknown-symmetry",
            "An ungenerated symmetry is not evidence.",
            "enumerate-all-fibre-preserving-bijections",
            "The complete permutation census constructs exactly the symmetry class of the conserved partition.",
        ),
        binary_axis(
            "action",
            "How is action represented?",
            "signed-or-imported-action-integral",
            "Signed continuum integration is outside the proof domain.",
            "sum-of-positive-oriented-step-magnitudes",
            "Orientation is held as a label and every magnitude is exact and positive.",
        ),
        binary_axis(
            "path",
            "Which path is extremal?",
            "postulated-stationary-physical-path",
            "Postulating stationarity imports the desired principle.",
            "dyadic-Fold-descent-and-positive-detour-bound",
            "The unique dyadic Fold trace loses one binary layer per act, terminates at identity, and every ranked detour adds retained positive variation.",
        ),
        binary_axis(
            "extension",
            "May another variational rule be added?",
            "free-Lagrangian-or-Euler-equation",
            "An imported functional or equation is an extra premise.",
            "no-extra-rule",
            "Finite bijection, invariant fibre, exact path and positive order exhaust the grammar.",
        ),
    ),
    exact_result=(
        "Fold preserves the reduced odd denominator core of every rational part; "
        "complete finite Fold symmetries preserve their held invariant fibres, "
        "every registered conserved partition generates its complete preserving "
        "symmetry class; every dyadic Fold part follows its unique binary-rank "
        "descent to stationary One; every monotone positive descent path telescopes "
        "to its endpoint carrier; and no finite detour has smaller action."
    ),
    induction_base=(
        "One-half folds to the One while retaining odd core One; a two-state "
        "support has a complete permutation census; a one-edge descent has action "
        "equal to its exact endpoint separation."
    ),
    induction_step=(
        "Writing a reduced denominator as a binary power times an odd core shows "
        "that Fold removes at most one binary factor and cannot alter the odd core. "
        "Adding one dyadic denominator layer adds exactly one preceding Fold act. "
        "Adding one generated state extends the complete permutation census by "
        "placing it in every image position and deciding the same incidence, "
        "carrier and fibre predicates.  Appending one exact path step preserves "
        "telescoping when its orientation continues descent; an opposed step "
        "retains additional positive variation and cannot reduce total action."
    ),
    exclusions=(
        "no imported Noether theorem, Lagrangian, Euler-Lagrange equation or continuum variation",
        "no prior V1/V2 proof artifact, answer table or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no assertion that an arbitrary non-Fold physical system has the registered dyadic ranking",
        "no measured trajectory or target selecting the symmetry, charge or action form",
    ),
    witnesses=(
        Witness(
            "odd-core-invariance",
            "Every reduced rational control part through denominator 128 preserves its exact odd core.",
            all_reduced_fold_parts_preserve_odd_core(128),
        ),
        Witness(
            "dyadic-fixed-point-descent",
            "Every reduced dyadic part through depth eight loses one binary layer per Fold and reaches the One.",
            all_dyadic_parts_descend(8),
        ),
        Witness(
            "complete-charge-symmetry",
            "The two-by-two fibre partition has exactly four preserving bijections.",
            len(charge_preserving_bijections(_CHARGES)) == 4,
        ),
        Witness(
            "incidence-carrier-symmetry",
            "The complete edge-labelled example retains only its exact preserving bijections.",
            len(complete_symmetry_class(_CHARGES, _EDGES)) == 4
            and all(
                symmetry_preserves_charge(permutation, _CHARGES)
                for permutation in complete_symmetry_class(_CHARGES, _EDGES)
            ),
        ),
        Witness(
            "telescoping-descent",
            "A complete exact descent telescopes to endpoint separation.",
            descent_telescopes(
                (Fraction(1, 1), Fraction(3, 4), Fraction(1, 2), Fraction(1, 4))
            ),
        ),
        Witness(
            "detour-bound",
            "Every exhaustively generated small exact path respects the action boundary.",
            all_small_paths_obey_action_boundary(),
        ),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "charge_preserving_bijections",
    "complete_symmetry_class",
    "descent_rank_strictly_falls",
    "descent_telescopes",
    "detour_cannot_lower_action",
    "dyadic_denominator_rank",
    "dyadic_fold_descent",
    "endpoint_separation",
    "fold_part",
    "is_monotone_descent",
    "odd_core_is_conserved",
    "oriented_magnitude",
    "path_action",
    "preserves_edges_and_carriers",
    "reduced_odd_denominator_core",
    "symmetry_preserves_charge",
)
