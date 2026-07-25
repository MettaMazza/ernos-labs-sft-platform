"""Force the expanded one-to-one mainstream scientific-calculator surface."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from sft.mathematics.generated_law import Witness, binary_dimension

from .gui import BUTTON_ROWS, GUIDE_TEXT, INSERTIONS
from .law_v2 import SPEC as CORE_SPEC
from .machine_v3 import calculate
from .session import CalculatorSession
from .values import CertifiedInterval, FoldScalar, scalar_to_fraction_for_projection


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-005"


def _contains(interval: CertifiedInterval, value: Fraction) -> bool:
    return (
        scalar_to_fraction_for_projection(interval.lower)
        <= value
        <= scalar_to_fraction_for_projection(interval.upper)
    )


_one_plus_one = calculate("1+1=")
_rational_power = calculate("2^(1/2)")
_nonrational_power = calculate("2^pi", places=10)
_sin_thirty = calculate("sin(30)", places=10, angle_mode="deg")
_atan_one = calculate("atan(1)", places=10, angle_mode="deg")
_cosh_empty = calculate("cosh(0)", places=10)
_statistics = calculate("mean(1,2,3,4)")
_variance = calculate("variance(1,2,3)")
_session = CalculatorSession(angle_mode="deg")
_session_first = _session.evaluate("1+1=")
_session.memory_store()
_session_second = _session.evaluate("ans+mem=")


SPEC = replace(
    CORE_SPEC,
    claim_id=CLAIM_ID,
    title="Complete exact SFT scientific calculator and cross-platform learning app",
    statement=(
        "The admitted exact calculator core extends uniquely to the declared mainstream scientific-calculator "
        "surface: terminal equals execution; editable expressions; exact and certified general powers, roots, "
        "logarithmic, exponential, trigonometric, inverse-trigonometric, hyperbolic, combinatorial and statistical "
        "operations; radian, degree and gradian modes; retained answer, memory and history; and one cross-platform "
        "desktop application exposing decimal projection, exact evidence, proof trace and SFT learning guidance. "
        "No interface action may bypass the same exact fail-closed evaluator."
    ),
    dependencies=CORE_SPEC.dependencies + ("SFT-MATH-SCIENTIFIC-CALCULATOR-004",),
    generation_rule=(
        CORE_SPEC.generation_rule
        + " Extend that complete product by declared scientific-function coverage, stateful interaction, and "
        "cross-platform application/evidence-surface choices."
    ),
    grammar_boundary=(
        "The complete thirteen-coordinate product formed by the ten exact core semantics plus the declared "
        "mainstream scientific function manifest, session interaction law and standard-library desktop evidence surface."
    ),
    dimensions=CORE_SPEC.dimensions
    + (
        binary_dimension(
            "scientific_surface",
            "Does the executable cover the complete declared mainstream scientific function manifest?",
            "partial-basic-function-subset",
            "A basic subset is not the requested scientific calculator.",
            "complete-declared-scientific-surface",
            "Arithmetic, rational/non-rational powers, roots, logs, exponentials, circular/inverse/hyperbolic functions, combinatorics, exact statistics and typed orthogonal operations are all routed through certified kernels.",
        ),
        binary_dimension(
            "session",
            "How does ordinary calculator interaction retain state?",
            "stateless-expression-only",
            "A stateless expression evaluator lacks terminal equals, answer, memory and history behavior.",
            "equals-answer-memory-history",
            "The terminal equals key executes; Ans, memory and ordered history retain explicit typed state without altering laws.",
        ),
        binary_dimension(
            "application",
            "How can a nontechnical user operate and inspect the calculator?",
            "terminal-only-opaque-answer",
            "A terminal-only answer surface is not a clean general-user calculator app and hides evidence.",
            "cross-platform-app-trace-and-guide",
            "One standard-library desktop app provides editable display, keypad, angle selector, memory, history, exact detail, proof trace and embedded SFT guidance.",
        ),
    ),
    exact_result=(
        "The unique expanded calculator is the exact core plus the complete declared scientific-function surface, "
        "terminal equals/Ans/memory/history state, RAD/DEG/GRAD translation, and one cross-platform desktop app whose "
        "buttons and keyboard invoke only the same fail-closed evaluator. Every exact result retains its Fold type; "
        "every non-rational result remains a certified rational enclosure; decimal output is display only."
    ),
    laws=CORE_SPEC.laws
    + (
        "a rational exponent is counted root followed by counted composition; a certified exponent uses exp of the certified product with ln",
        "degree and gradian inputs translate through the independently certified circle enclosure before circular evaluation",
        "inverse circular and hyperbolic operations are exact recurrence compositions with explicit domain halts",
        "memory, answer and history retain values but never mutate operation law or proof certificates",
        "terminal and desktop interfaces are two views of one evaluator and cannot create an untraced answer",
    ),
    induction_step=(
        CORE_SPEC.induction_step
        + " Each additional named function is admitted only when its finite expression tree terminates in already "
        "certified kernels; each session action appends a typed state record; each GUI action maps to exactly one parser token or state transition."
    ),
    boundary_exclusions=CORE_SPEC.boundary_exclusions
    + (
        "no GUI button, memory action, angle mode or display conversion may bypass the exact evaluator",
        "no host random generator, floating transcendental library, silent complex promotion or hidden calculator state",
        "no claim to functions outside the explicit feature manifest without a new versioned extension",
    ),
    witnesses=CORE_SPEC.witnesses
    + (
        Witness(
            "ordinary-equals-calculation",
            "A user may enter 1+1= and receive exact forward-held two.",
            isinstance(_one_plus_one.value, FoldScalar) and _one_plus_one.value.magnitude == 2,
        ),
        Witness(
            "general-power-surface",
            "Rational and certified non-rational exponents both return exact rational enclosures.",
            isinstance(_rational_power.value, CertifiedInterval) and isinstance(_nonrational_power.value, CertifiedInterval),
        ),
        Witness(
            "angle-mode-correspondence",
            "DEG sin(30) encloses exact half-One and DEG atan(One) encloses exact forty-five.",
            isinstance(_sin_thirty.value, CertifiedInterval)
            and isinstance(_atan_one.value, CertifiedInterval)
            and _contains(_sin_thirty.value, Fraction(1, 2))
            and _contains(_atan_one.value, Fraction(45)),
        ),
        Witness(
            "hyperbolic-base",
            "cosh(empty-One) returns an enclosure containing structural One.",
            isinstance(_cosh_empty.value, CertifiedInterval) and _contains(_cosh_empty.value, Fraction(1)),
        ),
        Witness(
            "exact-statistics",
            "Mean and population variance retain exact rational parts.",
            isinstance(_statistics.value, FoldScalar)
            and _statistics.value.magnitude == Fraction(5, 2)
            and isinstance(_variance.value, FoldScalar)
            and _variance.value.magnitude == Fraction(2, 3),
        ),
        Witness(
            "memory-answer-history",
            "Stored answer, recalled memory and ordered history execute as typed session state.",
            _session_first.value.magnitude == 2
            and _session_second.value.magnitude == 4
            and len(_session.history) == 2
            and _session.memory == _session_first.value,
        ),
        Witness(
            "discoverable-desktop-surface",
            "The app exposes the ordinary keypad, scientific functions, equals, memory, history evidence and SFT guide.",
            any("=" in row for row in BUTTON_ROWS)
            and all(label in INSERTIONS or label in {"MC", "MR", "M+", "M−", "MS", "C", "⌫", "=", "±"} for row in BUTTON_ROWS for label in row)
            and "Exact details" in GUIDE_TEXT
            and "Memory" in GUIDE_TEXT,
        ),
    ),
    why=(
        "A 1-to-1 scientific calculator must be usable like the familiar desktop calculator, not merely expose a "
        "narrow proof API. Accessibility cannot weaken the exact SFT value law or hide its certificates."
    ),
    derivation=(
        "Claim 004 supplies the admitted exact core. Exhausting the three extension choices forces complete declared "
        "function coverage, explicit session state and a cross-platform evidence-bearing app. Every new function is "
        "then reduced to exact arithmetic, rational recurrence, certified enclosure, typed fibre composition or a "
        "mandatory domain halt; UI controls map one-for-one to those operations."
    ),
    check=(
        "Execute all 8,192 combined semantics, require one survivor, replay every core witness, exercise ordinary "
        "equals, general powers, all function families, three angle modes, state and memory, terminal execution and "
        "the complete GUI control map; run adverse controls and independently regenerate the product and operational examples."
    ),
    limitations=(
        "Closure covers the explicit feature manifest documented by the app and README, not every proprietary button "
        "ever shipped on every calculator. Additional functions remain open lawful extensions. Physical-unit conversion "
        "tables and random-number generation are excluded because they require separately registered empirical units or "
        "a deterministic Fold-randomness law rather than an opaque host oracle."
    ),
)
