"""Unit and end-to-end checks for the SFT-native scientific calculator."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest

from sft.mathematics.calculator import Calculator, calculate
from sft.mathematics.calculator.law_v2 import SPEC
from sft.mathematics.calculator.operations import (
    exp_enclosure,
    ln_enclosure,
    multiply,
    nth_root,
)
from sft.mathematics.calculator.operations_v2 import circle_constant_enclosure
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    forward,
    parse_exact_number,
)
from sft.mathematics.generated_law import candidate_records, survivor_id


ROOT = Path(__file__).resolve().parents[1]


class CalculatorValueTests(unittest.TestCase):
    def test_decimal_and_scientific_inputs_are_exact(self) -> None:
        self.assertEqual(parse_exact_number("0.1").magnitude, Fraction(1, 10))
        self.assertEqual(parse_exact_number("1.25e-2").magnitude, Fraction(1, 80))
        self.assertIs(parse_exact_number("0"), EMPTY_ONE)

    def test_exact_arithmetic_empty_and_held_orientation(self) -> None:
        self.assertEqual(calculate("0.1+0.2").value.magnitude, Fraction(3, 10))
        self.assertIsInstance(calculate("3-3").value, EmptyOne)
        held = calculate("1-3").value
        self.assertIsInstance(held, FoldScalar)
        self.assertFalse(held.is_forward)
        self.assertEqual(held.magnitude, 2)
        self.assertEqual(calculate("(2/3)^3").value.magnitude, Fraction(8, 27))
        self.assertEqual(calculate("2^-3").value.magnitude, Fraction(1, 8))

    def test_combinatorics_and_postfix_operations(self) -> None:
        self.assertEqual(calculate("5!").value.magnitude, 120)
        self.assertEqual(calculate("ncr(10,3)").value.magnitude, 120)
        self.assertEqual(calculate("npr(5,2)").value.magnitude, 20)
        self.assertEqual(calculate("25%").value.magnitude, Fraction(1, 4))

    def test_root_is_exact_or_certified(self) -> None:
        self.assertEqual(calculate("sqrt(4)").value.magnitude, 2)
        root = nth_root(forward(2), 2)
        self.assertIsInstance(root, CertifiedInterval)
        self.assertLess(root.lower.magnitude ** 2, 2)
        self.assertGreaterEqual(root.upper.magnitude ** 2, 2)
        orthogonal = calculate("sqrt(-4)").value
        self.assertEqual(orthogonal, ComplexFibre(EMPTY_ONE, forward(2)))

    def test_transcendental_results_are_rational_enclosures(self) -> None:
        for value in (
            exp_enclosure(forward(1), 12),
            ln_enclosure(forward(2), 12),
            calculate("sin(1)").value,
            calculate("cos(1)").value,
            circle_constant_enclosure(24),
        ):
            with self.subTest(value=value):
                self.assertIsInstance(value, CertifiedInterval)
                self.assertTrue(value.certificate)

    def test_circle_enclosure_contains_an_unfavorable_known_prefix(self) -> None:
        circle = circle_constant_enclosure(32)
        known = Fraction(
            314159265358979323846264338327950288419716939937510,
            10 ** 50,
        )
        self.assertLess(circle.lower.magnitude, known)
        self.assertGreater(circle.upper.magnitude, known)
        self.assertIn("parity-checked:v2", circle.certificate)

    def test_orthogonal_fibre_composition(self) -> None:
        unit = ComplexFibre(EMPTY_ONE, forward(1))
        squared = multiply(unit, unit)
        self.assertIsInstance(squared, ComplexFibre)
        self.assertFalse(squared.real.is_forward)
        self.assertEqual(squared.real.magnitude, 1)
        self.assertIsInstance(squared.orthogonal, EmptyOne)
        parsed = calculate("complex(2,3)*complex(2,-3)").value
        self.assertEqual(parsed, ComplexFibre(forward(13), EMPTY_ONE))

    def test_domain_and_resource_violations_halt(self) -> None:
        for expression in ("1/0", "ln(0)", "root(2,0)", "unknown(1)"):
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                calculate(expression)
        with self.assertRaises(CalculatorHalt):
            Calculator(operation_limit=1).calculate("1+2+3")

    def test_every_execution_has_a_complete_trace(self) -> None:
        result = calculate("(1+2)*3")
        self.assertEqual(result.operations_executed, 2)
        self.assertTrue(result.trace[0].startswith("boundary:"))
        self.assertTrue(result.trace[-1].startswith("halt:"))


class CalculatorLawAndE2ETests(unittest.TestCase):
    def test_law_product_is_complete_and_uniquely_forced(self) -> None:
        records = candidate_records(SPEC)
        self.assertEqual(len(records), 1024)
        self.assertEqual(len({row["candidate_id"] for row in records}), 1024)
        self.assertEqual(sum(row["candidate_id"] == survivor_id(SPEC) for row in records), 1)
        self.assertTrue(all(witness.passed for witness in SPEC.witnesses))

    def test_cli_executes_on_standard_python(self) -> None:
        completed = subprocess.run(
            (sys.executable, "-m", "sft.mathematics.calculator", "0.1+0.2", "--trace"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("3/10", completed.stdout)
        self.assertIn("resources:", completed.stdout)

    def test_cli_halts_with_nonzero_status(self) -> None:
        completed = subprocess.run(
            (sys.executable, "-m", "sft.mathematics.calculator", "1/0"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("HALT:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
