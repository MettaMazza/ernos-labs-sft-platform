"""Depth-independent accumulated separation for the admitted Fold couplings.

WHY
The terminal running law already forces the common binary support and the
exact gap between the binary and generator-three sectors.  V1 B10 and V2 Step
259 additionally require the complete finite accumulation law.

DERIVATION
At positive level ``n`` the support is ``R_n = 2^(n-1)`` by repeated Fold
doubling and the adjacent-sector gap is
``1 / ((R_n + 2)(R_n + 3))``.  The first two terms are 1/12 and 1/20.  From
the second term onward each successor is strictly below half its predecessor.
Every finite tail is therefore bounded by the matching finite geometric
envelope, and every finite partial accumulation lies in ``[1/12, 11/60)``.

CHECK
All proof values are exact positive fractions or generated positive counts.
No completed infinite sum, logarithm, continuum scale, target value or
floating-point operation enters the law.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    value_axis,
)


CLAIM_ID = "SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015"


@lru_cache(maxsize=None)
def binary_support(level: int) -> int:
    """Return the complete support at a generated positive level."""

    if isinstance(level, bool) or level < 1:
        raise ValueError("level must be a generated positive count")
    support = 1
    cursor = 1
    while cursor < level:
        support += support
        cursor += 1
    return support


@lru_cache(maxsize=None)
def adjacent_sector_gap(level: int) -> Fraction:
    """Exact gap between sector counts two and three."""

    support = binary_support(level)
    return Fraction(1, (support + 2) * (support + 3))


@lru_cache(maxsize=None)
def finite_partial_accumulation(level: int) -> Fraction:
    """Sum every generated gap from the One level through ``level``."""

    if isinstance(level, bool) or level < 1:
        raise ValueError("partial accumulation requires a positive level")
    total = adjacent_sector_gap(1)
    cursor = 2
    while cursor <= level:
        total += adjacent_sector_gap(cursor)
        cursor += 1
    return total


def successor_is_below_half(level: int) -> bool:
    """Prove strict half-contraction after the exceptional first step."""

    if isinstance(level, bool) or level < 2:
        raise ValueError("half-contraction begins at the second positive level")
    current = adjacent_sector_gap(level)
    successor = adjacent_sector_gap(level + 1)
    return successor + successor < current


def finite_tail_envelope(start_level: int, end_level: int) -> bool:
    """Bound a finite tail by twice its first term, without an infinite sum."""

    if (
        isinstance(start_level, bool)
        or isinstance(end_level, bool)
        or start_level < 2
        or end_level < start_level
    ):
        raise ValueError("tail bounds require positive ordered levels from two")
    tail = adjacent_sector_gap(start_level)
    cursor = start_level + 1
    while cursor <= end_level:
        tail += adjacent_sector_gap(cursor)
        cursor += 1
    return tail < adjacent_sector_gap(start_level) + adjacent_sector_gap(start_level)


def accumulation_is_bounded(level: int) -> bool:
    """The exact V2 finite-depth bracket."""

    total = finite_partial_accumulation(level)
    return Fraction(1, 12) <= total < Fraction(11, 60)


def tolerance_witness(denominator: int) -> int:
    """Generate a finite level whose remaining envelope is below 1/denominator."""

    if isinstance(denominator, bool) or denominator < 1:
        raise ValueError("tolerance denominator must be a positive count")
    level = 2
    tolerance = Fraction(1, denominator)
    while adjacent_sector_gap(level) + adjacent_sector_gap(level) >= tolerance:
        level += 1
    return level


def tolerance_is_witnessed(denominator: int) -> bool:
    level = tolerance_witness(denominator)
    return adjacent_sector_gap(level) + adjacent_sector_gap(level) < Fraction(
        1, denominator
    )


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Finite accumulated Fold-coupling separation",
    statement=(
        "For the admitted binary and generator-three running sectors on the common "
        "Fold support R, the exact adjacent gap at positive level n is "
        "1/((R_n+2)(R_n+3)), with R_1=One and R_(n+1)=2R_n.  The first gap is "
        "1/12 and the second is 1/20.  Every successor from the second gap onward "
        "is strictly below half its predecessor.  Consequently every positive "
        "finite partial accumulation S_N satisfies 1/12 <= S_N < 11/60, and for "
        "every positive finite tolerance a generated level supplies a smaller "
        "exact remaining-tail envelope.  This is constructive finite convergence, "
        "not a completed infinite sum."
    ),
    dependencies=(
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-MATH-SELF-SIMILAR-CONVERGENCE-002",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-FOUNDATION-COUNT-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of predecessor, gap term, first-step, "
        "contraction, envelope, finite-boundary, tolerance and extension forms."
    ),
    grammar_boundary=(
        "Every positive finite common-support level generated from the One by "
        "binary succession; the exact binary/generator-three pair gap; every "
        "positive finite partial accumulation and every positive rational "
        "tolerance represented by a positive denominator."
    ),
    axes=(
        binary_axis(
            "predecessor",
            "Which running law supplies the terms?",
            "imported-or-selected-coupling-table",
            "A conventional or selected table is not an admitted predecessor.",
            "admitted-common-support-gap-law",
            "The current model-admitted running receipt forces the complete pair-gap family.",
        ),
        binary_axis(
            "term",
            "What is accumulated?",
            "unsigned-or-fitted-difference",
            "A fitted difference can encode a target.",
            "exact-adjacent-sector-gap",
            "The generator difference is the One and the paired denominators force 1/((R+2)(R+3)).",
        ),
        binary_axis(
            "first",
            "How is the exceptional first successor handled?",
            "assert-half-contraction-from-first-gap",
            "The transition 1/12 to 1/20 shrinks but is not below half.",
            "retain-one-twelfth-and-one-twentieth",
            "The complete first two exact gaps are retained before the general contraction.",
        ),
        binary_axis(
            "contraction",
            "What closes every later successor?",
            "visual-or-imported-convergence",
            "Visual approach and an imported series theorem are not Fold proof objects.",
            "exact-strict-half-contraction-after-level-two",
            "For every R at least two, the successor denominator exceeds twice the current denominator.",
        ),
        value_axis(
            "envelope",
            "Which generated upper envelope is forced?",
            (
                ("one-sixth", "Later exact partial sums exceed this candidate."),
                ("eleven-sixtieths", ""),
                ("one-fifth", "This is a weaker nonminimal envelope."),
                ("target-selected-bound", "A target-selected bound violates the direction of proof."),
            ),
            "eleven-sixtieths",
            "The base 1/12 plus twice the first contracting-tail term 1/20 uniquely gives 11/60.",
        ),
        binary_axis(
            "boundary",
            "Is a completed infinite object required?",
            "completed-infinite-sum",
            "Completed infinity is outside the SFT domain.",
            "every-positive-finite-partial-support",
            "The induction bounds every generated finite partial accumulation.",
        ),
        binary_axis(
            "tolerance",
            "How is convergence witnessed?",
            "limit-symbol-without-witness",
            "A limit label alone supplies no finite certificate.",
            "generated-finite-tail-witness",
            "Binary support eventually makes twice one exact gap smaller than any registered positive rational tolerance.",
        ),
        binary_axis(
            "extension",
            "May another correction or bound be selected?",
            "free-tail-correction",
            "A free correction is a parameter.",
            "no-extra-rule",
            "The admitted gap, first two terms, exact contraction and finite induction exhaust the law.",
        ),
    ),
    exact_result=(
        "Every positive finite partial sum of the binary/generator-three Fold "
        "coupling gaps lies in the exact bracket [1/12, 11/60); after the second "
        "level every successor gap is below half its predecessor, and every "
        "positive rational tolerance has a generated finite tail witness."
    ),
    induction_base=(
        "At the One support the gap is 1/12.  At the binary successor support it "
        "is 1/20; both lie below the forced envelope 11/60."
    ),
    induction_step=(
        "For support R at least two, doubling R makes the next paired denominator "
        "strictly greater than twice the current paired denominator.  Appending "
        "the next gap therefore preserves the finite geometric envelope, and "
        "continued binary succession constructs a finite witness below every "
        "positive rational tolerance."
    ),
    exclusions=(
        "no V1/V2 executable, certificate, stored partial-sum table or prior survivor in execution",
        "no imported coupling equation, infinite-series formula, logarithm or continuum limit",
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no measured coupling, target value, fitted coefficient or selected stopping depth",
        "no completed infinity and no claim of an attained terminal sum",
    ),
    witnesses=(
        Witness(
            "first-two-gaps",
            "The complete first two terms are exactly one-twelfth and one-twentieth.",
            adjacent_sector_gap(1) == Fraction(1, 12)
            and adjacent_sector_gap(2) == Fraction(1, 20),
        ),
        Witness(
            "strict-successor-contraction",
            "Every checked generated successor after level two is below half its predecessor.",
            all(successor_is_below_half(level) for level in range(2, 129)),
        ),
        Witness(
            "finite-partial-envelope",
            "Every checked finite partial accumulation remains inside the exact depth-independent bracket.",
            all(accumulation_is_bounded(level) for level in range(1, 129))
            and all(finite_tail_envelope(2, level) for level in range(2, 129)),
        ),
        Witness(
            "constructive-tolerance",
            "Every checked positive rational tolerance receives an exact finite witness.",
            all(tolerance_is_witnessed(value) for value in (1, 2, 3, 5, 7, 11, 127, 1024)),
        ),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "accumulation_is_bounded",
    "adjacent_sector_gap",
    "binary_support",
    "finite_partial_accumulation",
    "finite_tail_envelope",
    "successor_is_below_half",
    "tolerance_is_witnessed",
    "tolerance_witness",
)
