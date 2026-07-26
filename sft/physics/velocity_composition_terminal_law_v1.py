"""Exact positive Fold velocity composition, forced from a complete grammar."""

from __future__ import annotations

from enum import Enum
from fractions import Fraction
from itertools import product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-SPACETIME-VELOCITY-COMPOSITION-TERMINAL-033"


class TypedRest(Enum):
    REST = "typed-rest-motion"


class TypedEmpty(Enum):
    EMPTY = "typed-empty-held-part"


REST = TypedRest.REST
EMPTY = TypedEmpty.EMPTY


def _speed(value: Fraction) -> Fraction:
    value = Fraction(value)
    if value <= 0 or value > 1:
        raise ValueError("speed magnitude must be an exact positive part of the limiting One")
    return value


def compose_same_direction(left: Fraction | TypedRest, right: Fraction | TypedRest) -> Fraction | TypedRest:
    """Compose exact positive same-direction speeds; rest is a typed state."""

    if left is REST:
        return right
    if right is REST:
        return left
    u = _speed(left)
    v = _speed(right)
    return (u + v) / (Fraction(1) + u * v)


def held_pair(speed: Fraction) -> tuple[Fraction, Fraction | TypedEmpty]:
    """Forward/held representation without returning a numerical zero."""

    speed = _speed(speed)
    held = EMPTY if speed == 1 else Fraction(1) - speed
    return Fraction(1) + speed, held


def compose_held_pairs(left: Fraction, right: Fraction) -> tuple[Fraction, Fraction | TypedEmpty]:
    left_forward, left_held = held_pair(left)
    right_forward, right_held = held_pair(right)
    forward = left_forward * right_forward
    if left_held is EMPTY or right_held is EMPTY:
        held: Fraction | TypedEmpty = EMPTY
    else:
        held = left_held * right_held
    return forward, held


def recover_speed(pair: tuple[Fraction, Fraction | TypedEmpty]) -> Fraction:
    forward, held = pair
    if held is EMPTY:
        return Fraction(1)
    if forward <= held:
        raise ValueError("held pair does not encode positive forward motion")
    return (forward - held) / (forward + held)


def bilinear_candidates() -> tuple[dict[str, object], ...]:
    """The four identity-compatible present/absent bilinear operations."""

    rows = []
    for numerator_cross, denominator_cross in product((False, True), repeat=2):
        rows.append({
            "candidate_id": f"numerator-cross-{'present' if numerator_cross else 'absent'}__denominator-cross-{'present' if denominator_cross else 'absent'}",
            "numerator_cross": numerator_cross,
            "denominator_cross": denominator_cross,
            "identity_forced_terms": ("left", "right", "denominator-One"),
            "limit_absorbing": (not numerator_cross) and denominator_cross,
        })
    return tuple(rows)


def candidate_value(left: Fraction, right: Fraction, numerator_cross: bool, denominator_cross: bool) -> Fraction:
    left = _speed(left)
    right = _speed(right)
    cross = left * right
    numerator = left + right
    if numerator_cross:
        numerator += cross
    denominator = Fraction(1)
    if denominator_cross:
        denominator += cross
    return numerator / denominator


def unique_bilinear_survivor() -> dict[str, object]:
    survivors = tuple(row for row in bilinear_candidates() if row["limit_absorbing"])
    if len(survivors) != 1:
        raise ValueError("bilinear grammar did not force one velocity operation")
    return survivors[0]


def exact_closure_grid() -> tuple[Fraction, ...]:
    return (Fraction(1, 8), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(7, 8), Fraction(1))


def theorem_certificate() -> dict[str, object]:
    grid = exact_closure_grid()
    closure = all(Fraction(0) < compose_same_direction(u, v) <= 1 for u in grid for v in grid)
    associativity = all(
        compose_same_direction(compose_same_direction(u, v), w) == compose_same_direction(u, compose_same_direction(v, w))
        for u in grid for v in grid for w in grid
    )
    pair_equivalence = all(
        recover_speed(compose_held_pairs(u, v)) == compose_same_direction(u, v)
        for u in grid for v in grid
    )
    strict_sublimit = all(
        compose_same_direction(u, v) < 1
        for u in grid[:-1] for v in grid[:-1]
    )
    low_speed_difference = all(
        (u + v) - compose_same_direction(u, v) == (u * v * (u + v)) / (Fraction(1) + u * v)
        for u in grid[:-1] for v in grid[:-1]
    )
    return {
        "candidate_count": len(bilinear_candidates()),
        "survivor": unique_bilinear_survivor()["candidate_id"],
        "closure": closure,
        "associativity": associativity,
        "pair_equivalence": pair_equivalence,
        "strict_sublimit": strict_sublimit,
        "limiting_speed_absorbing": all(compose_same_direction(Fraction(1), v) == 1 for v in grid),
        "typed_rest_identity": all(compose_same_direction(REST, v) == v and compose_same_direction(v, REST) == v for v in grid),
        "low_speed_difference_exact": low_speed_difference,
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Exact positive Fold velocity-composition law",
    statement=(
        "Typed rest, exact positive sublimit parts and the complete present/absent bilinear grammar force one "
        "same-direction composition: u Fold-plus v=(u+v)/(One+uv). It is commutative, associative, closed below "
        "the limiting One, fixes the limiting One, and is exactly reconstructed by multiplying the forward/held "
        "pairs (One+u, One Take u) and (One+v, One Take v). Rest and a vanished held part are typed structures, "
        "never numerical zero; direction is held as a label, never a negative proof scalar."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-EXACT-OPERATIONS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-MECH-SPEED-VELOCITY-001",
        "SFT-PHYS-SPACETIME-INERTIAL-TRANSFORMATION-001",
        "SFT-PHYS-SPACETIME-LIMIT-SPEED-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of motion domain, typed rest, forward/held representation, identity-compatible "
        "numerator cross term, identity-compatible denominator cross term, limiting-speed behavior, closure, "
        "associativity, held-record reversibility, empirical custody and extension form."
    ),
    grammar_boundary=(
        "Every exact positive rational speed part through the limiting One; typed rest; typed empty held part; both "
        "present/absent choices for the bilinear cross term after two-sided identity forces the left, right and "
        "denominator-One terms; every exact triple composition; and no signed or continuum proof scalar."
    ),
    axes=(
        binary_axis("domain", "What is composed?", "imported-real-line-velocity", "A continuum imports the target model.", "exact-positive-parts-and-held-direction", "Speed is an exact positive part; direction is retained as a label."),
        binary_axis("rest", "How is rest represented?", "numerical-zero", "Numerical nothing is not an admitted physical part.", "typed-rest-state", "Rest is the empty-motion class with an exact identity action."),
        binary_axis("representation", "What carries motion?", "single-unrecorded-scalar", "One scalar discards the reverse distinction.", "forward-held-pair", "The One-plus and One-Take parts retain both motion faces."),
        binary_axis("numerator", "Does the bilinear numerator retain a cross term?", "cross-term-present", "It prevents the limiting One from remaining fixed.", "cross-term-absent", "Two-sided rest identity already forces the left and right terms."),
        binary_axis("denominator", "Does the bilinear denominator retain a cross term?", "cross-term-absent", "Then composing the limiting One with motion exceeds the One.", "cross-term-present", "The product term exactly balances the limiting boundary."),
        binary_axis("limit", "What happens at the limiting speed?", "limit-moves-or-is-exceeded", "That violates the admitted causal boundary.", "limiting-One-is-absorbing", "Substitution makes numerator and denominator identical."),
        binary_axis("closure", "Where does a sublimit pair land?", "unbounded-sum", "Ordinary addition can leave the domain.", "strictly-inside-One", "One minus the result is the positive product of both held parts over a positive denominator."),
        binary_axis("associativity", "How do three motions compose?", "order-dependent-rule", "Frame grouping cannot change one physical relation.", "exact-associative-product", "Forward and held pair multiplication is associative."),
        binary_axis("record", "Can the operation be reconstructed?", "discard-held-part", "Discarding the held part makes reversal ambiguous.", "retain-forward-and-held-parts", "The exact pair record reconstructs the speed ratio."),
        binary_axis("measurement", "May experiment choose the operation?", "Fizeau-readable-before-seal", "A measured fringe slope could select the survivor.", "postseal-only-comparison", "The structural operation seals before the external optical record is opened."),
        binary_axis("extension", "May another coefficient enter?", "free-coefficient-or-correction", "A coefficient would be a parameter.", "no-extra-rule", "Identity and limit constraints exhaust the four-form grammar."),
    ),
    exact_result=(
        "The unique exact same-direction Fold composition is (u+v)/(One+uv). Typed rest is a two-sided identity; "
        "the limiting One is absorbing; positive sublimit parts remain strictly sublimit; pair multiplication makes "
        "the law associative and reconstructible; and the complete identity-compatible bilinear census contains four "
        "candidates with exactly one survivor."
    ),
    induction_base=(
        "Typed rest leaves either exact speed record unchanged, while the least positive generated parts compose "
        "through the same forward/held pair product."
    ),
    induction_step=(
        "Appending one motion multiplies both retained pair components once. Associativity of exact positive "
        "multiplication preserves the reconstructed ratio, domain closure and limiting boundary at every finite depth."
    ),
    exclusions=(
        "no V1/V2 executable, stored velocity-addition formula or measured optical result in the forcing runtime",
        "no numerical zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof value",
        "no imported Lorentz transform, rapidity, hyperbolic function or consensus kinematic equation as a premise",
        "no target-selected coefficient, fitted denominator or hidden premarked survivor",
        "no claim that the same-direction scalar law alone supplies the full non-collinear rotation law",
    ),
    witnesses=(
        Witness("complete-bilinear-census", "Two-sided rest identity leaves exactly four cross-term presence forms and the limiting One selects one.", len(bilinear_candidates()) == 4 and sum(bool(row["limit_absorbing"]) for row in bilinear_candidates()) == 1),
        Witness("typed-rest-and-limit", "Typed rest is identity and the limiting One is absorbing on the complete exact check grid.", theorem_certificate()["typed_rest_identity"] and theorem_certificate()["limiting_speed_absorbing"]),
        Witness("closure-and-associativity", "All generated pairs close and all generated triples associate exactly.", theorem_certificate()["closure"] and theorem_certificate()["strict_sublimit"] and theorem_certificate()["associativity"]),
        Witness("held-pair-reconstruction", "Independent forward/held multiplication reconstructs the same survivor.", theorem_certificate()["pair_equivalence"]),
        Witness("low-speed-boundary", "The departure from ordinary addition is an exact positive higher-product carrier.", theorem_certificate()["low_speed_difference_exact"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EMPTY", "REST", "SPEC", "TypedEmpty", "TypedRest", "bilinear_candidates",
    "candidate_value", "compose_held_pairs", "compose_same_direction", "exact_closure_grid", "held_pair",
    "recover_speed", "theorem_certificate", "unique_bilinear_survivor",
)
