"""Expanded calculator-core, session, CLI and desktop-surface checks."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest

from sft.mathematics.calculator import CalculatorSession, calculate
from sft.mathematics.calculator.gui import BUTTON_ROWS, GUIDE_TEXT, INSERTIONS
from sft.mathematics.calculator.law_v3 import SPEC
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    EmptyOne,
    FoldScalar,
    scalar_to_fraction_for_projection,
)
from sft.mathematics.generated_law import candidate_records, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def contains(value: CertifiedInterval, target: Fraction) -> bool:
    return (
        scalar_to_fraction_for_projection(value.lower)
        <= target
        <= scalar_to_fraction_for_projection(value.upper)
    )


class ExpandedCalculatorTests(unittest.TestCase):
    def test_ordinary_expression_and_terminal_equals(self) -> None:
        result = calculate("1+1=")
        self.assertIsInstance(result.value, FoldScalar)
        self.assertEqual(result.value.magnitude, 2)
        self.assertIsInstance(calculate("1-1=").value, EmptyOne)

    def test_general_rational_and_certified_powers(self) -> None:
        square_root = calculate("2^(1/2)").value
        cube_root = calculate("2^(1/3)").value
        nonrational = calculate("2^pi", places=10).value
        pi_root = calculate("sqrt(pi)", places=10).value
        self.assertTrue(all(isinstance(item, CertifiedInterval) for item in (square_root, cube_root, nonrational, pi_root)))
        self.assertLess(
            scalar_to_fraction_for_projection(square_root.lower) ** 2,
            Fraction(2),
        )
        self.assertGreaterEqual(
            scalar_to_fraction_for_projection(square_root.upper) ** 2,
            Fraction(2),
        )

    def test_three_angle_modes_and_inverse_functions(self) -> None:
        self.assertTrue(contains(calculate("sin(30)", angle_mode="deg", places=10).value, Fraction(1, 2)))
        self.assertTrue(contains(calculate("cos(60)", angle_mode="deg", places=10).value, Fraction(1, 2)))
        self.assertTrue(contains(calculate("tan(50)", angle_mode="grad", places=10).value, Fraction(1)))
        self.assertTrue(contains(calculate("asin(1/2)", angle_mode="deg", places=10).value, Fraction(30)))
        self.assertTrue(contains(calculate("acos(1/2)", angle_mode="deg", places=10).value, Fraction(60)))
        self.assertTrue(contains(calculate("atan(1)", angle_mode="deg", places=10).value, Fraction(45)))

    def test_hyperbolic_logarithmic_and_exp_surface(self) -> None:
        self.assertTrue(contains(calculate("cosh(0)", places=10).value, Fraction(1)))
        self.assertTrue(contains(calculate("sinh(0)", places=10).value, Fraction(0)))
        self.assertTrue(contains(calculate("tanh(0)", places=10).value, Fraction(0)))
        self.assertTrue(contains(calculate("log(8,2)", places=10).value, Fraction(3)))
        self.assertTrue(contains(calculate("log2(8)", places=10).value, Fraction(3)))
        self.assertTrue(contains(calculate("ln(e)", places=8).value, Fraction(1)))
        self.assertIsInstance(calculate("asinh(1)", places=10).value, CertifiedInterval)
        self.assertIsInstance(calculate("acosh(2)", places=10).value, CertifiedInterval)
        self.assertIsInstance(calculate("atanh(1/2)", places=10).value, CertifiedInterval)

    def test_exact_statistics_integer_and_combinatorial_surface(self) -> None:
        self.assertEqual(calculate("mean(1,2,3,4)").value.magnitude, Fraction(5, 2))
        self.assertEqual(calculate("variance(1,2,3)").value.magnitude, Fraction(2, 3))
        self.assertIsInstance(calculate("stddev(1,2,3)").value, CertifiedInterval)
        self.assertEqual(calculate("gcd(48,18)").value.magnitude, 6)
        self.assertEqual(calculate("lcm(12,18)").value.magnitude, 36)
        self.assertEqual(calculate("mod(17,5)").value.magnitude, 2)
        self.assertEqual(calculate("ncr(10,3)").value.magnitude, 120)
        self.assertEqual(calculate("npr(5,2)").value.magnitude, 20)
        self.assertEqual(calculate("floor(-1.2)").value.orientation, "counter-held")
        self.assertEqual(calculate("ceil(-1.2)").value.magnitude, 1)

    def test_domain_failures_remain_fail_closed(self) -> None:
        from sft.mathematics.calculator.values import CalculatorHalt
        for expression in ("1/0=", "asin(2)", "acosh(1/2)", "atanh(1)", "log(1,1)"):
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                calculate(expression)


class SessionAndApplicationTests(unittest.TestCase):
    def test_answer_memory_and_history(self) -> None:
        session = CalculatorSession(angle_mode="deg")
        first = session.evaluate("1+1=")
        session.memory_store()
        second = session.evaluate("ans+mem=")
        self.assertEqual(first.value.magnitude, 2)
        self.assertEqual(second.value.magnitude, 4)
        self.assertEqual(len(session.history), 2)
        session.memory_subtract(first.value)
        self.assertIsInstance(session.memory, EmptyOne)
        session.memory_add(first.value)
        self.assertEqual(session.memory.magnitude, 2)
        session.memory_clear()
        self.assertIsInstance(session.memory, EmptyOne)

    def test_desktop_button_surface_is_complete_and_discoverable(self) -> None:
        special = {"MC", "MR", "M+", "M−", "MS", "C", "⌫", "=", "±"}
        labels = tuple(label for row in BUTTON_ROWS for label in row)
        self.assertEqual(len(labels), len(set(labels)))
        self.assertTrue(all(label in INSERTIONS or label in special for label in labels))
        for required in ("=", "sin", "asin", "sinh", "log", "xʸ", "√", "nCr", "mean", "MS", "C"):
            self.assertIn(required, labels)
        self.assertIn("How this calculator follows Smithian Fold Theory", GUIDE_TEXT)
        self.assertIn("Exact details", GUIDE_TEXT)

    def test_expanded_law_is_completely_enumerated(self) -> None:
        records = candidate_records(SPEC)
        self.assertEqual(len(records), 8192)
        self.assertEqual(len({row["candidate_id"] for row in records}), 8192)
        self.assertEqual(sum(row["candidate_id"] == survivor_id(SPEC) for row in records), 1)
        self.assertTrue(all(witness.passed for witness in SPEC.witnesses))

    def test_cli_matches_app_core_and_accepts_equals(self) -> None:
        completed = subprocess.run(
            (sys.executable, "-m", "sft.mathematics.calculator", "1+1=", "--trace"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.startswith("2\n"))
        self.assertIn("resources:", completed.stdout)

    def test_gui_and_cli_modules_compile_on_standard_python(self) -> None:
        completed = subprocess.run(
            (sys.executable, "-m", "py_compile", "sft/mathematics/calculator/gui.py", "sft/mathematics/calculator/__main__.py"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
