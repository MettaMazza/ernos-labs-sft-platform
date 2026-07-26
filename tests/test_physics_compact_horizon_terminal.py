import unittest
from fractions import Fraction

from sft.physics.compact_horizon_terminal_law_v1 import (
    EMPTY_ONE_FORM,
    SPEC,
    THERMAL_MASS_PRODUCT,
    endpoint_census,
    evaporation_certificate,
    exclusion_scaling_certificate,
    horizon_thermodynamics,
    theorem_certificate,
)
from sft.physics.structural_constants import candidate_rows


class CompactHorizonTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)

    def test_exclusion_scaling_is_depth_independent(self):
        for depth in (1, 2, 3, 8, 16, 32):
            row = exclusion_scaling_certificate(depth)
            self.assertTrue(row["base_equal"])
            self.assertTrue(row["gravity_strict_after_base"])
            self.assertTrue(row["perfect_cube_support"])
            self.assertTrue(row["depth_independent_exponent_order"])

    def test_two_family_endpoint_census(self):
        row = endpoint_census()
        self.assertEqual(row["loaded_exclusion_threshold"], Fraction(3, 4))
        self.assertEqual(row["folded_gravity_balance"], Fraction(1, 2))
        self.assertEqual(row["family_count"], 2)
        self.assertEqual(row["third_pre_horizon_family"], EMPTY_ONE_FORM)
        self.assertEqual(row["successor_after_second_family"], "horizon-closure")

    def test_inverse_mass_temperature_and_area(self):
        reference = horizon_thermodynamics(Fraction(1, 4))
        self.assertEqual(reference["radius"], Fraction(1, 2))
        self.assertEqual(reference["temperature"], Fraction(1, 4))
        self.assertEqual(reference["temperature"] * reference["mass"], THERMAL_MASS_PRODUCT)
        for depth in (1, 2, 3, 8, 16):
            row = evaporation_certificate(depth)
            self.assertTrue(row["thermal_mass_invariant"])
            self.assertTrue(row["all_reached_carriers_positive"])
            self.assertTrue(row["finite_floor_retained"])
        theorem = theorem_certificate()
        self.assertTrue(theorem["all_exclusion_scalings_close"])
        self.assertTrue(theorem["two_pre_horizon_families"])
        self.assertTrue(theorem["reference_cross_closes"])
        self.assertTrue(theorem["all_evaporation_traces_close"])


if __name__ == "__main__":
    unittest.main()
