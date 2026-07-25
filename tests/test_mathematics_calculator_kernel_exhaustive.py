"""Exhaustive branch tests for every inherited exact calculator kernel."""

from __future__ import annotations

from fractions import Fraction
import unittest
from unittest.mock import patch

from sft.mathematics.calculator import machine as machine_v1
from sft.mathematics.calculator import machine_v2
from sft.mathematics.calculator import machine_v3
from sft.mathematics.calculator import operations as op
from sft.mathematics.calculator import operations_v2 as op2
from sft.mathematics.calculator import operations_v3 as op3
from sft.mathematics.calculator import values
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    add_scalar,
    compare_scalar,
    counter,
    forward,
    parse_exact_number,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
)


def interval(lower, upper, reason="test"):
    return CertifiedInterval(lower, upper, (reason,))


class ValueFormExhaustiveTests(unittest.TestCase):
    def test_constructor_invariants_and_boundary_parsing(self) -> None:
        self.assertEqual(str(EMPTY_ONE), "empty-One")
        with self.assertRaises(CalculatorHalt):
            FoldScalar("sideways", Fraction(1))
        for magnitude in (Fraction(0), Fraction(-1), 1):
            with self.subTest(magnitude=magnitude), self.assertRaises(CalculatorHalt):
                FoldScalar("forward-held", magnitude)  # type: ignore[arg-type]
        with self.assertRaises(CalculatorHalt):
            interval(forward(2), forward(1))
        with self.assertRaises(CalculatorHalt):
            CertifiedInterval(forward(1), forward(2), ())
        with self.assertRaises(CalculatorHalt):
            forward(-1)
        self.assertIs(counter(0), EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            counter(-1)

        failures = ("", "+1", "-1", "1e", "1e+", "1.2.3", "x", "1.a")
        for token in failures:
            with self.subTest(token=token), self.assertRaises((CalculatorHalt, ValueError)):
                parse_exact_number(token)
        self.assertEqual(parse_exact_number(".5"), forward(Fraction(1, 2)))
        self.assertEqual(parse_exact_number("2e3"), forward(2000))
        self.assertEqual(parse_exact_number("2e-3"), forward(Fraction(1, 500)))

    def test_scalar_comparison_arithmetic_and_rendering_all_paths(self) -> None:
        forms = (counter(2), counter(1), EMPTY_ONE, forward(1), forward(2))
        for left_index, left in enumerate(forms):
            for right_index, right in enumerate(forms):
                expected = (left_index > right_index) - (left_index < right_index)
                self.assertEqual(compare_scalar(left, right), expected)
        self.assertEqual(add_scalar(EMPTY_ONE, forward(1)), forward(1))
        self.assertEqual(add_scalar(forward(1), EMPTY_ONE), forward(1))
        self.assertEqual(add_scalar(forward(1), forward(2)), forward(3))
        self.assertIs(add_scalar(forward(2), counter(2)), EMPTY_ONE)
        self.assertEqual(add_scalar(forward(3), counter(2)), forward(1))
        self.assertEqual(add_scalar(forward(2), counter(3)), counter(1))
        self.assertIs(op.multiply_scalar(EMPTY_ONE, forward(2)), EMPTY_ONE)
        self.assertEqual(op.multiply_scalar(counter(2), forward(3)), counter(6))
        with self.assertRaises(CalculatorHalt):
            op.reciprocal_scalar(EMPTY_ONE)
        self.assertEqual(scalar_to_fraction_for_projection(EMPTY_ONE), 0)
        self.assertIs(scalar_from_projection(Fraction(0)), EMPTY_ONE)
        self.assertEqual(scalar_from_projection(Fraction(-2)), counter(2))
        self.assertEqual(values.decimal_projection(EMPTY_ONE), "0")
        self.assertTrue(values.decimal_projection(counter(Fraction(1, 2))).startswith("-"))
        self.assertEqual(values.exact_text(EMPTY_ONE), "empty-One")
        self.assertEqual(values.exact_text(counter(2)), "counter:2")
        self.assertEqual(values.exact_text(forward(Fraction(1, 2))), "1/2")
        self.assertEqual(values.value_text(interval(forward(1), forward(1))), "1")
        self.assertIn("fibre", values.value_text(ComplexFibre(forward(1), counter(1))))
        self.assertIn("≈", values.value_text(forward(Fraction(1, 3))))


class OperationKernelExhaustiveTests(unittest.TestCase):
    def test_scalar_interval_and_fibre_arithmetic_paths(self) -> None:
        fibre = ComplexFibre(forward(2), forward(3))
        self.assertIsInstance(op.add(fibre, forward(1)), ComplexFibre)
        self.assertIsInstance(op.add(forward(1), fibre), ComplexFibre)
        self.assertIsInstance(op.negate(fibre), ComplexFibre)
        self.assertIsInstance(op.negate(interval(counter(2), forward(3))), CertifiedInterval)
        self.assertIsInstance(op.multiply(fibre, forward(2)), ComplexFibre)
        self.assertIsInstance(op.multiply(forward(2), fibre), ComplexFibre)
        self.assertIsInstance(op.multiply(interval(counter(1), forward(2)), forward(3)), CertifiedInterval)
        self.assertIsInstance(op.reciprocal(fibre), ComplexFibre)
        self.assertIsInstance(op.reciprocal(interval(forward(1), forward(2))), CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            op.reciprocal(interval(counter(1), forward(1)))
        self.assertIsInstance(op.absolute(fibre), CertifiedInterval)
        crossing = op.absolute(interval(counter(2), forward(3)))
        self.assertEqual(crossing.lower, EMPTY_ONE)
        negative = op.absolute(interval(counter(3), counter(2)))
        self.assertEqual(negative.lower, forward(2))
        positive = interval(forward(2), forward(3))
        self.assertIs(op.absolute(positive), positive)
        self.assertEqual(op.absolute(counter(2)), forward(2))
        self.assertEqual(op.absolute(EMPTY_ONE), EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            op.require_scalar(interval(forward(1), forward(2)))

    def test_whole_count_power_combinatorics_and_roots(self) -> None:
        self.assertEqual(op.require_whole(EMPTY_ONE), 0)
        with self.assertRaises(CalculatorHalt):
            op.require_whole(EMPTY_ONE, allow_empty=False)
        for invalid in (counter(1), forward(Fraction(1, 2))):
            with self.assertRaises(CalculatorHalt):
                op.require_whole(invalid)
        self.assertEqual(op.whole_power(forward(2), EMPTY_ONE), forward(1))
        with self.assertRaises(CalculatorHalt):
            op.whole_power(forward(2), forward(Fraction(1, 2)))
        self.assertEqual(op.whole_power(forward(2), counter(3)), forward(Fraction(1, 8)))
        with self.assertRaises(CalculatorHalt):
            op.permutation(forward(2), forward(3))
        with self.assertRaises(CalculatorHalt):
            op.combination(forward(2), forward(3))
        self.assertEqual(op.permutation(forward(3), EMPTY_ONE), forward(1))
        self.assertEqual(op.combination(forward(3), EMPTY_ONE), forward(1))
        self.assertEqual(op._perfect_root(0, 2), 0)
        self.assertEqual(op._perfect_root(1, 2), 1)
        self.assertEqual(op._perfect_root(9, 2), 3)
        self.assertIsNone(op._perfect_root(8, 2))
        with self.assertRaises(CalculatorHalt):
            op.nth_root(forward(2), 0)
        self.assertIs(op.nth_root(EMPTY_ONE, 2), EMPTY_ONE)
        self.assertEqual(op.nth_root(counter(8), 3), counter(2))
        exact_orthogonal = op.nth_root(counter(4), 2)
        self.assertIsInstance(exact_orthogonal, ComplexFibre)
        with self.assertRaises(CalculatorHalt):
            op.nth_root(counter(2), 2)
        counter_enclosure = op.nth_root(counter(2), 3)
        self.assertIsInstance(counter_enclosure, CertifiedInterval)
        small = op.nth_root(forward(Fraction(1, 2)), 2)
        self.assertIsInstance(small, CertifiedInterval)

    def test_series_success_and_exhaustion_paths(self) -> None:
        for places in (0, 61):
            with self.assertRaises(CalculatorHalt):
                op._tolerance(places)
        self.assertEqual(op.exp_enclosure(EMPTY_ONE).lower, forward(1))
        self.assertIsInstance(op.exp_enclosure(counter(1), places=6), CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            op.exp_enclosure(forward(10), places=18, max_terms=1)
        with self.assertRaises(CalculatorHalt):
            op.ln_enclosure(EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            op.ln_enclosure(counter(1))
        self.assertEqual(op.ln_enclosure(forward(1)).lower, EMPTY_ONE)
        self.assertLess(compare_scalar(op.ln_enclosure(forward(Fraction(1, 2))).upper, EMPTY_ONE), 0)
        with self.assertRaises(CalculatorHalt):
            op.ln_enclosure(forward(100), places=18, max_terms=1)
        self.assertIsInstance(op.log10_enclosure(forward(2), 6), CertifiedInterval)
        self.assertEqual(op.sin_enclosure(EMPTY_ONE).lower, EMPTY_ONE)
        self.assertEqual(op.cos_enclosure(EMPTY_ONE).lower, forward(1))
        self.assertLess(compare_scalar(op.sin_enclosure(counter(1), 6).upper, EMPTY_ONE), 0)
        self.assertIsInstance(op.tan_enclosure(forward(1), 6), CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            op._alternating_trig(forward(10), False, 18, 1)
        odd = op._atan_unit_enclosure(Fraction(1, 5), 1)
        even = op._atan_unit_enclosure(Fraction(1, 5), 2)
        self.assertIsInstance(odd, CertifiedInterval)
        self.assertIsInstance(even, CertifiedInterval)
        with patch("sft.mathematics.calculator.operations.subtract", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op.circle_constant_enclosure()
        self.assertEqual(op.conjugate(forward(1)), forward(1))


class CorrectedAndExpandedOperationTests(unittest.TestCase):
    def test_corrected_circle_private_boundaries_and_failure(self) -> None:
        for x, terms in ((Fraction(0), 1), (Fraction(2), 1), (Fraction(1, 2), 0)):
            with self.subTest(x=x, terms=terms), self.assertRaises(CalculatorHalt):
                op2._atan_unit_enclosure_v2(x, terms)
        self.assertIsInstance(op2._atan_unit_enclosure_v2(Fraction(1, 2), 1), CertifiedInterval)
        self.assertIsInstance(op2._atan_unit_enclosure_v2(Fraction(1, 2), 2), CertifiedInterval)
        with patch("sft.mathematics.calculator.operations_v2.subtract", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op2.circle_constant_enclosure()

    def test_general_power_root_exp_log_and_interval_paths(self) -> None:
        self.assertEqual(op3._ordered_interval(forward(1), forward(2), ("ordered",)).lower, forward(1))
        hull = op3._interval_hull(
            interval(forward(2), forward(3), "a"),
            interval(counter(1), forward(4), "b"),
            certificate="hull",
        )
        self.assertEqual((hull.lower, hull.upper), (counter(1), forward(4)))
        with self.assertRaises(CalculatorHalt):
            op3.rational_power(forward(2), ComplexFibre(forward(1), forward(1)))
        with self.assertRaises(CalculatorHalt):
            op3.rational_power(interval(counter(1), forward(2)), interval(forward(1), forward(2)))
        self.assertEqual(op3.rational_power(forward(2), EMPTY_ONE), forward(1))
        self.assertEqual(op3.rational_power(forward(2), counter(2)), forward(Fraction(1, 4)))
        self.assertIsInstance(op3.rational_power(interval(forward(2), forward(3)), forward(2), 6), CertifiedInterval)
        self.assertEqual(op3.root_value(forward(8), 3), forward(2))
        with self.assertRaises(CalculatorHalt):
            op3.root_value(interval(counter(1), forward(2)), 2)
        rooted = op3.root_value(interval(forward(2), forward(4)), 2)
        self.assertIsInstance(rooted, CertifiedInterval)
        with patch("sft.mathematics.calculator.operations_v3.nth_root", return_value=ComplexFibre(EMPTY_ONE, forward(1))):
            with self.assertRaises(CalculatorHalt):
                op3.root_value(interval(forward(1), forward(2)), 2)
        self.assertIsInstance(op3.exp_value(interval(forward(1), forward(2)), 6), CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            op3.exp_value(ComplexFibre(forward(1), forward(1)))
        with self.assertRaises(CalculatorHalt):
            op3.ln_value(interval(EMPTY_ONE, forward(2)))
        self.assertIsInstance(op3.ln_value(interval(forward(1), forward(2)), 6), CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            op3.ln_value(ComplexFibre(forward(1), forward(1)))
        for base in (EMPTY_ONE, counter(2), forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.log_base(forward(2), base)
        with patch("sft.mathematics.calculator.operations_v3.divide", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.log_base(forward(2), forward(3))

    def test_inverse_trig_angle_and_hyperbolic_remaining_paths(self) -> None:
        self.assertEqual(op3._atan_small(EMPTY_ONE, 6).lower, EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            op3._atan_small(forward(Fraction(3, 4)), 6)
        with self.assertRaises(CalculatorHalt):
            op3._atan_small(forward(Fraction(1, 2)), 60, max_terms=1)
        self.assertIsInstance(op3._atan_small(counter(Fraction(1, 3)), 6), CertifiedInterval)
        self.assertIsInstance(op3.atan_value(interval(counter(1), forward(1)), 6), CertifiedInterval)
        self.assertEqual(op3.atan_value(EMPTY_ONE, 6).lower, EMPTY_ONE)
        self.assertIsInstance(op3.atan_value(counter(2), 6), CertifiedInterval)
        self.assertIsInstance(op3.atan_value(forward(Fraction(3, 4)), 6), CertifiedInterval)
        self.assertIsInstance(op3.atan_value(forward(2), 6), CertifiedInterval)
        with patch("sft.mathematics.calculator.operations_v3.add", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.atan_value(forward(1), 6)
        self.assertEqual(op3.asin_value(EMPTY_ONE, 6).lower, EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            op3.asin_value(forward(2), 6)
        self.assertIsInstance(op3.asin_value(forward(1), 6), CertifiedInterval)
        self.assertIsInstance(op3.asin_value(counter(1), 6), CertifiedInterval)
        with patch("sft.mathematics.calculator.operations_v3.subtract", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.acos_value(forward(Fraction(1, 2)), 6)
        with patch(
            "sft.mathematics.calculator.operations_v3.subtract",
            return_value=ComplexFibre(forward(1), forward(1)),
        ):
            with self.assertRaises(CalculatorHalt):
                op3._trig_interval(interval(forward(1), forward(2)), False, 6)
        with patch("sft.mathematics.calculator.operations_v3.divide", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.tan_value(forward(1), 6)

        for mode in ("rad", "deg", "grad"):
            self.assertIsNotNone(op3.to_radians(forward(1), mode))
            self.assertIsNotNone(op3.from_radians(forward(1), mode))
        with self.assertRaises(CalculatorHalt):
            op3.to_radians(forward(1), "turn")
        with self.assertRaises(CalculatorHalt):
            op3.from_radians(forward(1), "turn")

        with patch("sft.mathematics.calculator.operations_v3.divide", return_value=forward(1)):
            for function in (op3.sinh_value, op3.cosh_value, op3.tanh_value, op3.atanh_value):
                with self.subTest(function=function.__name__), self.assertRaises(CalculatorHalt):
                    function(forward(Fraction(1, 2)), 6)
        with patch("sft.mathematics.calculator.operations_v3.sinh_value", return_value=interval(forward(1), forward(2))), patch(
            "sft.mathematics.calculator.operations_v3.cosh_value", return_value=interval(forward(2), forward(3))
        ), patch("sft.mathematics.calculator.operations_v3.divide", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.tanh_value(forward(1), 6)
        self.assertIsInstance(op3.asinh_value(counter(1), 6), CertifiedInterval)
        for invalid in (EMPTY_ONE, counter(2), forward(Fraction(1, 2))):
            with self.assertRaises(CalculatorHalt):
                op3.acosh_value(invalid, 6)

    def test_aggregates_rounding_integer_and_forced_error_paths(self) -> None:
        with self.assertRaises(CalculatorHalt):
            op3.exact_sum(())
        with self.assertRaises(CalculatorHalt):
            op3.exact_product(())
        exact = interval(forward(Fraction(6, 5)), forward(Fraction(7, 5)))
        self.assertEqual(op3.floor_value(exact), forward(1))
        self.assertEqual(op3.ceil_value(exact), forward(2))
        for function in (op3.floor_value, op3.ceil_value):
            with self.assertRaises(CalculatorHalt):
                function(interval(forward(Fraction(4, 5)), forward(Fraction(6, 5))))
        for function in (op3.gcd_value, op3.lcm_value):
            with self.assertRaises(CalculatorHalt):
                function(forward(Fraction(1, 2)), forward(2))
        self.assertIs(op3.lcm_value(EMPTY_ONE, forward(2)), EMPTY_ONE)
        with self.assertRaises(CalculatorHalt):
            op3.modulo_value(forward(2), EMPTY_ONE)
        with patch("sft.mathematics.calculator.operations_v3.divide", return_value=forward(1)):
            with self.assertRaises(CalculatorHalt):
                op3.golden_ratio_enclosure()


class ParserMachineExhaustiveTests(unittest.TestCase):
    def test_v1_parser_all_success_functions(self) -> None:
        calculator = machine_v1.Calculator(places=6)
        expressions = (
            "+2", "-2", "2+3-1", "2*3/2", "2^3", "5!", "50%", "(2+3)",
            "pi", "e", "empty", "empty_one", "abs(-2)", "recip(2)", "sqrt(4)",
            "exp(1)", "ln(2)", "log10(2)", "sin(1)", "cos(1)", "tan(1)",
            "conj(complex(2,3))", "root(8,3)", "pow(2,3)", "ncr(5,2)", "npr(5,2)",
            "log(8,2)",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assertIsNotNone(calculator.calculate(expression).value)
        self.assertEqual(machine_v1.calculate("1+1").value, forward(2))

    def test_v1_parser_every_halt_boundary(self) -> None:
        for constructor in ((0, 10), (61, 10), (18, 0)):
            places, limit = constructor
            with self.assertRaises(CalculatorHalt):
                machine_v1.Calculator(places=places, operation_limit=limit)
        expressions = (
            "", "1@2", "1 2", "(", "1+", "1)", "unknown", "pi()", "abs()",
            "root(2)", "missing(1)",
        )
        for expression in expressions:
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                machine_v1.Calculator().calculate(expression)
        with self.assertRaises(CalculatorHalt):
            machine_v1.Calculator(operation_limit=1).calculate("1+1+1")
        self.assertEqual(machine_v1.Calculator().calculate("1   ").value, forward(1))
        with self.assertRaises(CalculatorHalt):
            machine_v1.Calculator().calculate("*1")
        self.assertEqual(machine_v1.Calculation("1", forward(1), (), 1, 0).render(), "1")

    def test_v2_and_v3_machine_specific_paths(self) -> None:
        self.assertIsInstance(machine_v2.calculate("pi").value, CertifiedInterval)
        self.assertEqual(machine_v2.calculate("1+1").value, forward(2))
        with self.assertRaises(CalculatorHalt):
            machine_v2.calculate("pi()")
        empty_v2 = machine_v2.Calculator()
        with self.assertRaises(CalculatorHalt):
            empty_v2._primary()
        with self.assertRaises(CalculatorHalt):
            machine_v3.Calculator(angle_mode="turn")
        calculator = machine_v3.Calculator(symbols={"Custom": forward(3)})
        self.assertEqual(calculator.calculate("custom").value, forward(3))
        self.assertIsInstance(calculator.calculate("tau").value, CertifiedInterval)
        self.assertIsInstance(calculator.calculate("golden").value, CertifiedInterval)
        self.assertIsInstance(calculator.calculate("pi").value, CertifiedInterval)
        self.assertIsInstance(calculator.calculate("log(2)").value, CertifiedInterval)
        with self.assertRaises(CalculatorHalt):
            calculator.calculate("1=1")
        self.assertEqual(machine_v3.calculate("1+1=").value, forward(2))
        for expression in ("sum()", "log(1,2,3)", "complex(1)"):
            with self.subTest(expression=expression), self.assertRaises(CalculatorHalt):
                calculator.calculate(expression)
        empty_v3 = machine_v3.Calculator()
        with self.assertRaises(CalculatorHalt):
            empty_v3._primary()


if __name__ == "__main__":
    unittest.main()
