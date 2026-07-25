"""Completion tests for the accessible claim-006 calculator."""

from __future__ import annotations

from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    counter,
    forward,
    scalar_to_fraction_for_projection,
)
from sft.mathematics.calculator_complete import CalculatorController, CalculatorSession, calculate
from sft.mathematics.calculator_complete.controller import FUNCTION_CATALOG, INSERTIONS, MAIN_BUTTON_ROWS
from sft.mathematics.calculator_complete.evidence import calculation_evidence, validate_value, value_form
from sft.mathematics.calculator_complete.expression_census import expression_census_json, expression_families
from sft.mathematics.calculator_complete.explorer import RegisteredMathematicsExplorer
from sft.mathematics.calculator_complete.operations import cos_value, periodic_reduce, sin_value, tan_value
from sft.mathematics.calculator_complete.presentation import friendly


ROOT = Path(__file__).resolve().parents[1]


def bounds(value: CertifiedInterval) -> tuple[Fraction, Fraction]:
    return (
        scalar_to_fraction_for_projection(value.lower),
        scalar_to_fraction_for_projection(value.upper),
    )


def midpoint(value: CertifiedInterval) -> float:
    lower, upper = bounds(value)
    return float((lower + upper) / 2)


class CompleteExpressionTests(unittest.TestCase):
    def test_familiar_arithmetic_and_terminal_equals(self) -> None:
        examples = {
            "1+1=": Fraction(2),
            "0.1+0.2=": Fraction(3, 10),
            "2+3*4": Fraction(14),
            "(2+3)*4": Fraction(20),
            "1-1": Fraction(0),
            "2^3": Fraction(8),
            "5!": Fraction(120),
            "50%": Fraction(1, 2),
            "1e-3": Fraction(1, 1000),
        }
        for expression, expected in examples.items():
            with self.subTest(expression=expression):
                value = calculate(expression).value
                actual = scalar_to_fraction_for_projection(value)
                self.assertEqual(actual, expected)

    def test_complete_declared_function_surface(self) -> None:
        exact = {
            "abs(-2)": Fraction(2), "recip(4)": Fraction(1, 4),
            "pow(2,3)": Fraction(8), "root(8,3)": Fraction(2),
            "ncr(5,2)": Fraction(10), "npr(5,2)": Fraction(20),
            "sum(1,2,3)": Fraction(6), "prod(2,3,4)": Fraction(24),
            "mean(1,2,3,4)": Fraction(5, 2), "variance(1,2,3)": Fraction(2, 3),
            "floor(-1.2)": Fraction(-2), "ceil(-1.2)": Fraction(-1),
            "gcd(48,18)": Fraction(6), "lcm(12,18)": Fraction(36),
            "mod(17,5)": Fraction(2), "hypot(3,4)": Fraction(5),
        }
        for expression, expected in exact.items():
            with self.subTest(expression=expression):
                self.assertEqual(
                    scalar_to_fraction_for_projection(calculate(expression).value), expected
                )
        certified = (
            "sqrt(2)", "cbrt(2)", "2^pi", "exp(1)", "ln(2)", "log(8,2)",
            "log10(2)", "log2(8)", "sin(1)", "cos(1)", "tan(1)",
            "asin(1/2)", "acos(1/2)", "atan(1)", "sinh(1)", "cosh(1)",
            "tanh(1)", "asinh(1)", "acosh(2)", "atanh(1/2)",
            "stddev(1,2,3)", "pi", "tau", "e", "phi",
        )
        for expression in certified:
            with self.subTest(expression=expression):
                self.assertIsInstance(calculate(expression, places=10).value, CertifiedInterval)
        pair = calculate("complex(2,3)").value
        self.assertIsInstance(pair, ComplexFibre)
        self.assertEqual(calculate("conj(complex(2,3))").value.orthogonal, counter(3))

    def test_periodic_reduction_closes_large_angles(self) -> None:
        for expression, conventional in (
            ("sin(1000000)", math.sin(1000000)),
            ("cos(1000000)", math.cos(1000000)),
        ):
            with self.subTest(expression=expression):
                value = calculate(expression, places=12).value
                self.assertIsInstance(value, CertifiedInterval)
                self.assertAlmostEqual(midpoint(value), conventional, places=11)
                self.assertIn("whole-turn-translation", " ".join(value.certificate))
        reduced = periodic_reduce(forward(1000000), 12)
        lower, upper = bounds(reduced)
        self.assertLess(abs(float(lower)), 4)
        self.assertLess(abs(float(upper)), 4)

    def test_angle_modes_and_large_turn_identity(self) -> None:
        half = calculate("sin(30)", angle_mode="deg", places=10).value
        one = calculate("tan(50)", angle_mode="grad", places=10).value
        self.assertLessEqual(bounds(half)[0], Fraction(1, 2))
        self.assertGreaterEqual(bounds(half)[1], Fraction(1, 2))
        self.assertLessEqual(bounds(one)[0], Fraction(1))
        self.assertGreaterEqual(bounds(one)[1], Fraction(1))

    def test_resource_and_domain_boundaries_halt_before_output(self) -> None:
        for expression, limit in (
            ("12345", 4), ("1e99", 10), ("11!", 10), ("2^11", 10),
            ("root(2,11)", 10), ("ncr(11,2)", 10),
        ):
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                calculate(expression, operation_limit=limit)
        for expression in ("1/0", "asin(2)", "ln(0)", "atanh(1)", "tan(90)"):
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                calculate(expression, angle_mode="deg")


class InteractionTests(unittest.TestCase):
    def test_result_chaining_clear_entry_and_all_clear(self) -> None:
        controller = CalculatorController()
        controller.set_expression("1+1")
        self.assertEqual(controller.press("=").result, "2")
        self.assertEqual(controller.press("+").expression, "ans+")
        controller.press("3")
        self.assertEqual(controller.press("=").result, "5")
        controller.set_expression("999")
        controller.press("CE")
        self.assertEqual(controller.view().result, "5")
        controller.press("C")
        self.assertEqual(controller.view().result, "0")
        self.assertIs(controller.session.answer, EMPTY_ONE)

    def test_unary_binary_sign_factorial_and_backspace_controls(self) -> None:
        controller = CalculatorController()
        controller.set_expression("9")
        self.assertEqual(controller.press("√").result, "3")
        self.assertEqual(controller.press("x²").result, "9")
        controller.press("n!")
        self.assertEqual(controller.view().result, "362880")
        controller.set_expression("12")
        self.assertEqual(controller.press("⌫").expression, "1")
        self.assertEqual(controller.press("±").expression, "-(1)")
        self.assertEqual(controller.press("±").expression, "1")
        controller.set_expression("5")
        self.assertEqual(controller.press("nCr").expression, "ncr(5,")

    def test_memory_history_modes_catalog_and_errors(self) -> None:
        controller = CalculatorController()
        controller.set_expression("2")
        controller.evaluate()
        controller.press("MS")
        self.assertTrue(controller.view().memory_active)
        controller.press("M+")
        controller.press("M−")
        controller.press("MR")
        self.assertEqual(controller.view().expression, "mem")
        controller.press("MC")
        self.assertFalse(controller.view().memory_active)
        controller.set_angle_mode("DEG")
        self.assertEqual(controller.view().angle_mode, "DEG")
        controller.insert_catalog("sum")
        self.assertTrue(controller.view().expression.endswith("sum("))
        controller.restore_history(0)
        self.assertEqual(controller.view().expression, "2")
        controller.clear_history()
        self.assertFalse(controller.view().history)
        controller.set_expression("1/0")
        view = controller.evaluate()
        self.assertEqual(view.result, "HALT")
        self.assertTrue(view.error)

    def test_visible_surface_is_unique_familiar_and_complete(self) -> None:
        labels = tuple(label for row in MAIN_BUTTON_ROWS for label in row)
        self.assertEqual(len(labels), len(set(labels)))
        for required in ("0", "1", "+", "−", "×", "÷", "=", "CE", "C", "⌫", "MS", "sin", "√"):
            self.assertIn(required, labels)
        catalog_names = {row[0] for row in FUNCTION_CATALOG}
        self.assertTrue({"sum", "prod", "mean", "variance", "stddev", "complex", "conj"} <= catalog_names)


class EvidenceAndExplorerTests(unittest.TestCase):
    def test_every_current_mathematics_expression_family_has_one_translation(self) -> None:
        families = expression_families()
        self.assertEqual(len(families), 24)
        self.assertEqual(len({item.claim_id for item in families}), 24)
        payload = json.loads(expression_census_json())
        self.assertEqual(payload["family_count"], 24)
        self.assertTrue(all(item.operations for item in families))

    def test_runtime_value_checks_are_computed_for_every_value_form(self) -> None:
        values = (
            EMPTY_ONE, forward(2), counter(2), calculate("sqrt(2)").value,
            calculate("complex(2,3)").value,
        )
        expected = (
            "structural_empty_One", "forward_held_positive_rational",
            "counter_held_positive_rational", "certified_exact_rational_enclosure",
            "typed_real_and_orthogonal_Fold_fibres",
        )
        for value, form in zip(values, expected):
            with self.subTest(form=form):
                self.assertTrue(all(validate_value(value).values()))
                self.assertEqual(value_form(value), form)

    def test_calculation_evidence_is_engine_comparable_but_not_an_admission(self) -> None:
        evidence = calculation_evidence(calculate("sqrt(2)"), ROOT)
        self.assertEqual(evidence["kind"], "SFT_calculator_evaluation_not_engine_admission")
        self.assertFalse(evidence["engine_admission_issued"])
        self.assertTrue(evidence["certificate"])
        self.assertTrue(all(evidence["constraint_checks"].values()))
        self.assertGreater(evidence["resources"]["tokens_read"], 0)

    def test_every_current_mathematics_claim_is_visible_and_replayable(self) -> None:
        explorer = RegisteredMathematicsExplorer(ROOT)
        self.assertEqual(len(explorer.claim_ids()), 25)
        for claim_id in explorer.claim_ids():
            with self.subTest(claim_id=claim_id):
                summary = explorer.summary(claim_id)
                if claim_id != "SFT-MATH-SCIENTIFIC-CALCULATOR-006":
                    self.assertTrue(summary.model_admitted)
                self.assertGreater(summary.candidate_count, 0)
                replay = explorer.replay(claim_id)
                self.assertTrue(replay.locally_replayed)
                self.assertFalse(replay.engine_admission_issued)
                self.assertEqual(replay.candidate_count, replay.eliminated_count + 1)
                self.assertEqual(replay.dependency_chain[0], "SFT-ROOT-THERE-IS-NO-NOTHING")


class PortabilityTests(unittest.TestCase):
    def test_cli_expression_proof_law_and_replay_end_to_end(self) -> None:
        commands = (
            (("1+1=",), "2"),
            (("sqrt(2)", "--proof"), '"engine_admission_issued": false'),
            (("--law", "SFT-MATH-EXACT-ARITHMETIC-001"), '"candidate_count": 256'),
            (("--replay-law", "SFT-MATH-EXACT-ARITHMETIC-001"), '"locally_replayed": true'),
        )
        for arguments, expected in commands:
            with self.subTest(arguments=arguments):
                completed = subprocess.run(
                    (sys.executable, "-m", "sft.mathematics.calculator_complete", *arguments),
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIn(expected, completed.stdout)

    def test_three_operating_system_launchers_and_packaged_command(self) -> None:
        launchers = (
            ROOT / "launchers" / "Launch Smithian Calculator.command",
            ROOT / "launchers" / "Launch Smithian Calculator.bat",
            ROOT / "launchers" / "launch-smithian-calculator.sh",
        )
        for launcher in launchers:
            self.assertTrue(launcher.exists())
            self.assertIn("sft.mathematics.calculator_complete", launcher.read_text(encoding="utf-8"))
        project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("sft-calculator", project)


if __name__ == "__main__":
    unittest.main()
