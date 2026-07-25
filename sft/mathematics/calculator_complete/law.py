"""Force the complete accessible SFT Mathematics calculator and explorer."""

from __future__ import annotations

import json
from pathlib import Path

from sft.mathematics.calculator.values import CertifiedInterval, EmptyOne, FoldScalar
from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension

from .controller import CalculatorController, FUNCTION_CATALOG, MAIN_BUTTON_ROWS
from .evidence import calculation_evidence
from .machine import calculate


CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-006"
PREDECESSOR_CLAIMS = (
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ALGEBRA-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-PROBABILITY-STATISTICS-001",
    "SFT-MATH-OPTIMIZATION-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-MATH-EXACT-RELATIONS-002",
    "SFT-MATH-ORBIT-NUMBER-THEORY-002",
    "SFT-MATH-LIMIT-CONTINUUM-002",
    "SFT-MATH-ALGEBRAIC-BALANCE-002",
    "SFT-MATH-BOUNDED-N-BODY-002",
    "SFT-MATH-FLOORED-FLUID-REGULARITY-002",
    "SFT-MATH-PRIME-PAIR-CENSUS-002",
    "SFT-MATH-RIEMANN-MIRROR-002",
    "SFT-MATH-COLLATZ-FINITE-CENSUS-002",
    "SFT-MATH-SELF-SIMILAR-CONVERGENCE-002",
    "SFT-MATH-SCIENTIFIC-CALCULATOR-004",
    "SFT-MATH-SCIENTIFIC-CALCULATOR-005",
)


def _dimension(key: str, rejected: str, rejected_reason: str, admitted: str, admitted_reason: str):
    return binary_dimension(
        key,
        key.replace("_", " ") + "?",
        rejected,
        rejected_reason,
        admitted,
        admitted_reason,
    )


_one_plus_one = calculate("1+1=")
_empty = calculate("1-1")
_held = calculate("1-2")
_root = calculate("sqrt(2)")
_large_angle = calculate("sin(1000000)", places=10)
_controller = CalculatorController()
_controller.set_expression("1+1")
_controller.press("=")
_controller.press("+")
_controller.press("3")
_chained = _controller.press("=")
_proof = calculation_evidence(_root)
_coverage_path = Path(__file__).resolve().parents[3] / "generated/mathematics/scientific_calculator_coverage_v4.json"
_coverage = json.loads(_coverage_path.read_text(encoding="utf-8"))
_totals = _coverage["totals"]
_labels = tuple(label for row in MAIN_BUTTON_ROWS for label in row)
_functions = {name for name, _, _ in FUNCTION_CATALOG}


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Fully realised SFT scientific calculator and complete Mathematics law explorer",
    statement=(
        "The admitted exact calculator extends uniquely to a familiar, progressively disclosed and cross-platform "
        "application that evaluates the complete declared scientific expression language, exposes every currently "
        "registered predecessor Mathematics family, emits engine-comparable but explicitly non-admission proof output, "
        "halts at every exact value/domain/resource boundary, and is completely statement-and-branch tested."
    ),
    dependencies=PREDECESSOR_CLAIMS,
    generation_rule=(
        "Hold all twenty-four admitted predecessor Mathematics claims fixed, then exhaust the ten independent completion "
        "choices for interaction, value law, scientific surface, branch census, proof output, accessibility, portability, "
        "periodic scale, fail-closed resources and complete testing."
    ),
    grammar_boundary=(
        "The complete ten-coordinate binary product of application completions over the immutable claim-005 calculator "
        "and the exact set of twenty-four registered predecessor Mathematics claims."
    ),
    dimensions=(
        _dimension("interaction", "expression-api-only", "An API alone is not a familiar calculator.", "familiar-keypad-and-result-chaining", "Digits, keypad, terminal equals, Ans chaining, memory, clear-entry, all-clear and backspace are all explicit."),
        _dimension("value_law", "projected-host-scalars", "Host zero, negative, irrational, imaginary or floating proof values violate the admitted Mathematics boundary.", "exact-SFT-runtime-types", "Every answer is empty-One, a held positive rational, a certified rational enclosure or typed Fold fibres."),
        _dimension("scientific_surface", "partial-function-subset", "A partial subset cannot realise the declared scientific calculator.", "complete-declared-expression-language", "Every documented arithmetic, power, root, circular, hyperbolic, logarithmic, combinatorial, statistical and typed-fibre function is routed through an exact kernel."),
        _dimension("mathematics_census", "calculator-only-scalar-view", "A scalar-only view omits registered structured and theorem-level Mathematics families.", "all-current-predecessor-families", "All twenty-four predecessor claims have a one-to-one structured/scalar translation and local enumeration replay."),
        _dimension("proof_output", "opaque-friendly-number", "A projected number without exact evidence hides the calculation law.", "typed-certificate-trace-and-resources", "Exact type, rational parts, certificate, operation trace, resources, dependencies and official receipt reference remain inspectable."),
        _dimension("accessibility", "all-evidence-visible-at-once", "Dumping proof detail onto first-time users makes ordinary calculator use inaccessible.", "familiar-first-progressive-disclosure", "The standard calculator is the default; proof, functions, learning and law exploration open on demand."),
        _dimension("portability", "platform-specific-or-heavy-runtime", "A platform-specific or container-dependent app blocks independent access.", "standard-library-mac-Windows-Linux", "One Python-standard-library application plus installed command and three operating-system launchers provides the same evaluator."),
        _dimension("periodic_scale", "unreduced-direct-series-only", "A direct series alone exhausts resources on ordinary large circular arguments.", "certified-whole-turn-reduction", "Large angles subtract an exact whole count of certified turns before rational recurrence."),
        _dimension("resource_boundary", "unbounded-or-silent-failure", "Unbounded construction or NaN/infinity hides an unclosed computation.", "counted-early-check-and-mandatory-halt", "Digits, exponents and counted operations are checked early and every invalid or unclosed expression halts without a value."),
        _dimension("testing", "passing-examples-with-gaps", "Passing examples do not execute every implementation path.", "complete-statement-and-branch-coverage", "Every statement and branch in the declared active inherited and completion implementation is executed, alongside CLI, GUI, launcher, control and law-replay tests."),
    ),
    exact_result=(
        "The unique completion is the familiar cross-platform app whose ordinary input invokes only exact SFT runtime "
        "types; whose advanced view exposes the complete current Mathematics census and engine-comparable proof; whose "
        "large circular inputs are certified by whole-turn reduction; and whose declared active implementation records "
        "no missing statement or branch."
    ),
    laws=(
        "human boundary notation is translated before evaluation and never becomes a prohibited proof scalar",
        "every button, keyboard action, memory transition and terminal expression uses one exact evaluator",
        "a local Mathematics replay can reproduce a registered census but cannot issue or impersonate an engine admission receipt",
        "progressive disclosure changes presentation only and cannot change the exact retained answer",
        "large circular input is equivalent after subtraction of any generated whole number of complete turns",
        "the current expression census is one-to-one with the registered predecessor catalog and halts if that catalog changes without a translation",
        "complete implementation coverage is necessary but remains distinct from engine forcing and independent validation",
    ),
    induction_base=(
        "Claim 005 supplies one exact scalar calculation and one desktop evidence surface; the twenty-four fixed predecessors "
        "supply the complete current Mathematics catalog."
    ),
    induction_step=(
        "Adding one expression, interaction, platform view or Mathematics family is lawful only when it maps to an admitted "
        "kernel, retains exact typed evidence, adds a generated census coordinate or registered translation, and introduces "
        "no uncovered execution branch."
    ),
    boundary_exclusions=(
        "no numerical zero, negative magnitude, irrational scalar, imaginary scalar or floating proof value",
        "no fitted scientific parameter, host transcendental answer, random oracle, NaN or infinity",
        "no GUI or terminal path may bypass the exact evaluator",
        "no calculator replay is labelled an admission receipt",
        "no claim to future Mathematics families not present in the exact predecessor census",
        "no proprietary calculator-specific surface is claimed beyond the declared expression language",
    ),
    witnesses=(
        Witness("ordinary-use", "1+1= returns exact forward-held two.", isinstance(_one_plus_one.value, FoldScalar) and _one_plus_one.value.magnitude == 2),
        Witness("prohibited-value-translation", "Correspondence zero and negative are empty-One and counter-held positive magnitude.", isinstance(_empty.value, EmptyOne) and isinstance(_held.value, FoldScalar) and not _held.value.is_forward and _held.value.magnitude == 1),
        Witness("nonrational-certificate", "sqrt(2) remains a replayable rational enclosure.", isinstance(_root.value, CertifiedInterval) and bool(_root.value.certificate)),
        Witness("large-angle-closure", "A million-radian sine closes after certified whole-turn reduction.", isinstance(_large_angle.value, CertifiedInterval) and any("whole-turn-translation" in item for item in _large_angle.value.certificate)),
        Witness("familiar-result-chain", "2 followed by +3 returns readable five through retained Ans.", _chained.result == "5"),
        Witness("complete-predecessor-census", "The exact dependency set contains twenty-four unique current Mathematics predecessors.", len(PREDECESSOR_CLAIMS) == 24 and len(set(PREDECESSOR_CLAIMS)) == 24),
        Witness("engine-comparable-not-admission", "Proof output contains exact checks and explicitly denies issuing an engine admission.", bool(_proof["constraint_checks"]) and _proof["engine_admission_issued"] is False),
        Witness("familiar-visible-controls", "Every ordinary calculator control is present once.", len(_labels) == len(set(_labels)) and {"0", "1", "+", "−", "×", "÷", "=", "CE", "C", "⌫", "MS"} <= set(_labels)),
        Witness("advanced-function-discovery", "Aggregate and typed-fibre operations remain discoverable without crowding the keypad.", {"sum", "prod", "mean", "variance", "stddev", "complex", "conj"} <= _functions),
        Witness("complete-coverage", "The declared active implementation has no missing statement or branch.", _totals["percent_covered"] == 100.0 and _totals["missing_lines"] == 0 and _totals["missing_branches"] == 0),
    ),
    why=(
        "Exact Mathematics is most useful when any person can calculate with it without surrendering the derivation chain. "
        "Familiarity, complete current-knowledge reach and machine-inspectable evidence must therefore coexist."
    ),
    derivation=(
        "The twenty-four dependencies fix every current Mathematics law and the corrected exact calculator. Exhausting the "
        "ten completion distinctions eliminates an API-only tool, prohibited host values, partial functions, omitted branches, "
        "opaque output, overwhelming presentation, platform lock-in, unreduced large-angle exhaustion, silent resource failure "
        "and incomplete tests. The only surviving form is the familiar exact app plus its progressively disclosed law explorer."
    ),
    check=(
        "Enumerate all 1,024 completion forms; require one all-admitted survivor; execute ordinary, prohibited-value, certified "
        "nonrational, large-angle, result-chain, current-census, proof-output, visible-control, advanced-discovery and exact "
        "coverage witnesses; pass four adverse controls; independently regenerate the product, replay all twenty-four Mathematics "
        "families and rerun the declared active file coverage gate."
    ),
    limitations=(
        "Closure covers the exact current predecessor catalog, declared scientific expression language and application behavior. "
        "It does not claim that a calculation is a new theorem, that every future Mathematics discovery is already translated, "
        "or that every proprietary calculator button is required. Lawful future additions remain open versioned extensions."
    ),
    correspondence_terms=(
        "scientific calculator",
        "computer algebra interface",
        "interval arithmetic",
        "proof-producing computation",
        "mathematics knowledge explorer",
    ),
)


__all__ = ("CLAIM_ID", "PREDECESSOR_CLAIMS", "SPEC")
