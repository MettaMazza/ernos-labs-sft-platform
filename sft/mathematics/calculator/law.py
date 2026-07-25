"""Force the unique SFT-native scientific-calculator semantics."""

from __future__ import annotations

from fractions import Fraction

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension

from .machine import calculate
from .operations import (
    circle_constant_enclosure,
    combination,
    divide,
    exp_enclosure,
    factorial,
    ln_enclosure,
    multiply,
    nth_root,
    sin_enclosure,
)
from .values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    forward,
    parse_exact_number,
)


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-003"


def _halts_division_by_empty() -> bool:
    try:
        divide(forward(1), EMPTY_ONE)
    except CalculatorHalt:
        return True
    return False


_decimal_sum = calculate("0.1+0.2")
_cancelled = calculate("1-1")
_held = calculate("1-3")
_root_two = nth_root(forward(2), 2)
_exp_one = exp_enclosure(forward(1), 12)
_ln_exp_lower = ln_enclosure(_exp_one.lower, 8) if isinstance(_exp_one, CertifiedInterval) else None
_sin_one = sin_enclosure(forward(1), 12)
_pi = circle_constant_enclosure(24)
_orthogonal_square = multiply(ComplexFibre(EMPTY_ONE, forward(1)), ComplexFibre(EMPTY_ONE, forward(1)))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact traced SFT-native scientific calculator",
    statement=(
        "A scientific-calculator interface is admitted in SFT only when every entered decimal is translated "
        "character-by-character to an exact rational part, displayed zero is structural empty-One, subtraction "
        "uses held orientation, all algebraic and transcendental non-rational results remain exact rational "
        "enclosures with replayable bounds, orthogonal values remain typed Fold fibres, every operation is traced, "
        "and every undefined or uncertified operation halts."
    ),
    dependencies=(
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-ALGEBRAIC-BALANCE-002",
        "SFT-MATH-LIMIT-CONTINUUM-002",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-LOGIC-PROOF-001",
        "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    ),
    generation_rule=(
        "Generate the complete product of input-value, empty, orientation, exact-operation, non-rational, "
        "transcendental, orthogonal, domain, trace and extra-rule choices."
    ),
    grammar_boundary=(
        "All calculator semantics formed from the ten declared binary representation and execution choices, "
        "with exact finite rational recurrences and a declared finite resource bound."
    ),
    dimensions=(
        binary_dimension("input", "How are entered numerals represented?", "host-float", "A host float loses the exact entered part before proof begins.", "character-exact-part", "Characters generate the exact counted numerator, denominator and exponent."),
        binary_dimension("empty", "What represents the absence of retained magnitude?", "numeric-zero", "Numerical zero is not an admitted SFT value.", "structural-empty-One", "The empty-One form records complete cancellation or empty magnitude."),
        binary_dimension("orientation", "How is a conventional negative result retained?", "negative-scalar", "A negative scalar imports a forbidden signed field.", "held-fibre-orientation", "One of two generated held labels records orientation with a positive magnitude."),
        binary_dimension("operations", "What executes arithmetic?", "host-arithmetic-oracle", "A host arithmetic oracle erases the generated Fold construction.", "generated-exact-kernels", "Junction, pairing, refinement and recurrence execute the operation exactly."),
        binary_dimension("nonrational", "How are roots without a rational exact value represented?", "irrational-scalar", "An irrational scalar is outside the proof domain.", "rational-balance-enclosure", "An exact rational bracket and polynomial balance certify the result without importing a scalar."),
        binary_dimension("transcendental", "How are exp, logarithmic, circular and trigonometric functions evaluated?", "black-box-library-value", "A black-box value supplies no Fold derivation or remainder certificate.", "finite-rational-recurrence-bound", "A finite exact recurrence and positive tail bound enclose the function value."),
        binary_dimension("orthogonal", "How is conventional imaginary notation represented?", "imaginary-scalar", "An imaginary scalar is not an admitted proof value.", "typed-orthogonal-fibre-pair", "Two exact Fold fibres retain real and orthogonal coordinates compositionally."),
        binary_dimension("domain", "What happens when a proof obligation is undefined or unclosed?", "nan-infinity-continuation", "NaN or infinity silently continues beyond the admitted domain.", "explicit-lawful-halt", "The machine halts before returning an uncertified value."),
        binary_dimension("trace", "What evidence accompanies an answer?", "answer-only", "An answer without provenance cannot be replayed or independently checked.", "complete-proof-resource-trace", "Input translation, operations, result and counted resources are retained."),
        binary_dimension("addition", "May a calculator-specific scale or answer rule be added?", "has-extra-rule", "A fitted constant or answer-selecting rule is not supplied by the dependencies.", "no-extra-rule", "The calculator composes only already-admitted exact structures and proofs."),
    ),
    exact_result=(
        "The unique admitted calculator semantics uses exact character-generated rational parts, structural "
        "empty-One, held orientation, generated exact kernels, certified rational enclosures, finite rational "
        "recurrences with explicit remainder bounds, typed orthogonal fibres, mandatory domain halts, complete "
        "proof/resource traces and no extra rule."
    ),
    laws=(
        "decimal and scientific notation are exact rational boundary encodings, never floating proof values",
        "complete cancellation returns structural empty-One and unmatched remainder retains held orientation",
        "every exact operation composes admitted arithmetic, combinatorial and order structures",
        "every non-rational result is an exact rational enclosure carrying its generating recurrence and bound",
        "an unclosed enclosure, exhausted resource bound or invalid domain halts without a result",
        "orthogonal composition is a typed two-fibre product and introduces no imaginary scalar",
        "decimal output is a downstream display projection and never proof evidence",
    ),
    induction_base=(
        "One entered digit is translated to an exact counted part; the structural empty-One and structural One "
        "supply cancellation and identity bases."
    ),
    induction_step=(
        "Appending a generated digit refines the exact denominator by one counted tenfold composition; appending "
        "an operator composes two already-certified values, and appending one recurrence term retains the previous "
        "exact sum plus one exact part while replacing the remainder by a proven smaller positive bound."
    ),
    boundary_exclusions=(
        "semantic numerical zero, NaN and infinity are not admitted values",
        "negative, irrational and imaginary scalars are replaced by typed Fold structures",
        "binary floating-point and opaque host-library answers are excluded from proof",
        "uncertified roots, series, singularities and exhausted resource bounds halt",
        "decimal projections are correspondence displays only",
    ),
    witnesses=(
        Witness("exact-decimal", "0.1 plus 0.2 is the exact rational part 3/10, not a host floating result.", isinstance(_decimal_sum.value, FoldScalar) and _decimal_sum.value.magnitude == Fraction(3, 10)),
        Witness("empty-cancellation", "One substituted from One yields structural empty-One.", isinstance(_cancelled.value, EmptyOne)),
        Witness("held-remainder", "One substituted by three yields counter-held positive magnitude two.", isinstance(_held.value, FoldScalar) and not _held.value.is_forward and _held.value.magnitude == 2),
        Witness("root-balance", "The exact sqrt(2) bracket has lower square below two and upper square at or above two.", isinstance(_root_two, CertifiedInterval) and _root_two.lower.magnitude ** 2 < 2 <= _root_two.upper.magnitude ** 2),
        Witness("combinatorial-recurrence", "Factorial and selection recurrence reproduce exact finite arrangements.", factorial(forward(5)).magnitude == 120 and combination(forward(10), forward(3)).magnitude == 120),
        Witness("transcendental-enclosure", "exp, ln, sin and circle operations return ordered rational enclosures with certificates.", isinstance(_exp_one, CertifiedInterval) and isinstance(_ln_exp_lower, CertifiedInterval) and isinstance(_sin_one, CertifiedInterval) and isinstance(_pi, CertifiedInterval)),
        Witness("orthogonal-composition", "The square of the unit orthogonal fibre is counter-held real One with empty orthogonal fibre.", isinstance(_orthogonal_square, ComplexFibre) and isinstance(_orthogonal_square.real, FoldScalar) and not _orthogonal_square.real.is_forward and isinstance(_orthogonal_square.orthogonal, EmptyOne)),
        Witness("domain-halt", "Division by structural empty-One halts without returning NaN or infinity.", _halts_division_by_empty()),
        Witness("complete-trace", "A parsed calculation retains boundary translation, operation and terminal records.", _decimal_sum.operations_executed == 1 and len(_decimal_sum.trace) >= 4),
        Witness("scientific-notation", "Scientific notation is translated exactly without a floating intermediate.", isinstance(parse_exact_number("1.25e-2"), FoldScalar) and parse_exact_number("1.25e-2").magnitude == Fraction(1, 80)),
    ),
    why=(
        "A calculator makes the Mathematics laws directly inspectable, but it may not smuggle the conventional "
        "signed real or complex number model back into the proof domain through its user interface."
    ),
    derivation=(
        "Exhausting the ten representation and execution choices leaves one compositional machine: exact entered "
        "parts, empty-One, held orientations, admitted arithmetic recurrences, rational balance enclosures, typed "
        "orthogonal fibres, mandatory halts and complete traces. Each supported scientific function is then a "
        "finite composition of those structures, not a new axiom or fitted parameter."
    ),
    check=(
        "Execute all 1,024 generated semantics, require the sole all-preserving survivor, run exact arithmetic, "
        "root, combinatorial, transcendental, orthogonal, parser, trace and halt witnesses, run four adverse "
        "controls, and independently regenerate both the product and operational examples."
    ),
    limitations=(
        "Closure is for the declared calculator grammar and finite resource bounds. A displayed decimal is not "
        "proof evidence. Enclosures report their exact bounds; requests that cannot close inside the declared "
        "bound halt rather than returning a guess. Additional named functions remain lawful extensions only when "
        "they reduce to admitted exact recurrences and pass the same engine route."
    ),
    correspondence_terms=(
        "scientific calculator",
        "rational arithmetic",
        "signed arithmetic",
        "real functions",
        "complex arithmetic",
        "interval arithmetic",
        "certified numerics",
    ),
)
