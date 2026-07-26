from fractions import Fraction
import unittest

from sft.physics.collective_radiation_response_terminal_law_v1 import (
    SPEC, acoustic_ladder, alfven_squared_carrier, exact_mode_occupation,
    finite_boson_occupations, laser_ledger, occupation_scale_covariant,
    plasma_squared_carriers, radiation_power_ratio, ultraviolet_closed,
)
from sft.physics.structural_constants import candidate_rows


class CollectiveRadiationResponseTerminalTests(unittest.TestCase):
    def test_complete_finite_boson_support(self):
        words = finite_boson_occupations((1, 2, 3, 5, 8), 7)
        self.assertEqual(len(words), 10)
        self.assertTrue(ultraviolet_closed((1, 2, 3, 5, 8), 7))
        self.assertTrue(occupation_scale_covariant((1, 2, 3, 5, 8), 7, 5))
        self.assertEqual(len(exact_mode_occupation((1, 2, 3), 5)), 3)

    def test_radiation_and_acoustic_scaling(self):
        self.assertEqual(radiation_power_ratio(Fraction(2)), 16)
        self.assertEqual(radiation_power_ratio(Fraction(3, 2)), Fraction(81, 16))
        self.assertEqual(acoustic_ladder(Fraction(1, 6), 3), (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)))

    def test_laser_plasma_and_alfven_carriers(self):
        laser = laser_ledger(3, 2, Fraction(4, 3), Fraction(5, 4), 7)
        self.assertTrue(laser["population_inverted"] and laser["above_threshold"])
        self.assertEqual(laser["linewidth_time_product"], 1)
        plasma = plasma_squared_carriers(Fraction(3), Fraction(2), Fraction(5), Fraction(7), Fraction(11))
        self.assertEqual(plasma["plasma_frequency_squared"], Fraction(12, 35))
        self.assertEqual(plasma["debye_length_squared"], Fraction(77, 12))
        self.assertEqual(alfven_squared_carrier(Fraction(3), Fraction(5), Fraction(7)), Fraction(9, 35))

    def test_invalid_inputs_halt(self):
        with self.assertRaises(ValueError): finite_boson_occupations((), 1)
        with self.assertRaises(ValueError): finite_boson_occupations((1, 2), 0)
        with self.assertRaises(ValueError): acoustic_ladder(Fraction(1), 0)
        with self.assertRaises(ValueError): laser_ledger(0, 1, Fraction(1), Fraction(1), 1)
        with self.assertRaises(ValueError): plasma_squared_carriers(Fraction(0), Fraction(1), Fraction(1), Fraction(1), Fraction(1))
        with self.assertRaises(ValueError): alfven_squared_carrier(Fraction(-1), Fraction(1), Fraction(1))

    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__": unittest.main()
