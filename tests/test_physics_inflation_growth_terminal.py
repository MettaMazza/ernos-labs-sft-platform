from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.inflation_growth_terminal_law_v1 import (
    SPEC,
    exact_doubling_depth,
    forward_component_transfer,
    generator_cover,
    perturbation_growth_trace,
    scalar_support_share,
    tensor_support_share,
)
from sft.physics.structural_constants import candidate_rows


class InflationGrowthTerminalTests(unittest.TestCase):
    def test_generator_cover_is_exact_and_least(self) -> None:
        self.assertEqual(generator_cover(), (5, 32))
        self.assertEqual(exact_doubling_depth(32), 5)
        with self.assertRaises(ValueError):
            exact_doubling_depth(27)

    def test_primordial_partition_closes_to_one(self) -> None:
        self.assertEqual(scalar_support_share(), Fraction(31, 32))
        self.assertEqual(tensor_support_share(), Fraction(1, 32))
        self.assertEqual(scalar_support_share() + tensor_support_share(), Fraction(1))

    def test_growth_and_component_transport_are_exact(self) -> None:
        self.assertEqual(perturbation_growth_trace(), (Fraction(1, 4), Fraction(1, 2), Fraction(1)))
        row = forward_component_transfer(Fraction(3, 2))
        self.assertEqual(row["matter_retention"], Fraction(8, 27))
        self.assertEqual(row["radiation_retention"], Fraction(16, 81))
        self.assertEqual(row["matter_over_radiation"], Fraction(3, 2))

    def test_invalid_inputs_halt(self) -> None:
        for value in (0, -1, True):
            with self.assertRaises(ValueError):
                exact_doubling_depth(value)
        for value in (Fraction(0), Fraction(-1)):
            with self.assertRaises(ValueError):
                forward_component_transfer(value)

    def test_complete_engine_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
