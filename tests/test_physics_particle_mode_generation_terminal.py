import unittest
from fractions import Fraction

from sft.physics.particle_mode_generation_terminal_law_v1 import (
    EMPTY_ONE,
    colour_binary_dual,
    generation_coordinates,
    interior_fixed_modes,
    least_cover_depth,
    m_fold_fibre,
    mass_pattern_transport,
    mass_ratio_reach,
    place_recurrent_particle_modes,
    theorem_certificate,
    transition_mode_certificate,
)


class ParticleModeGenerationTerminalTests(unittest.TestCase):
    def test_general_fibre_and_fixed_modes(self):
        for multiplicity in range(2, 14):
            result = m_fold_fibre(multiplicity, Fraction(1, 2))
            self.assertEqual(len(result["preimages"]), multiplicity)
            self.assertTrue(result["complete"] and result["all_positive_inside_one"] and result["exact_return"])
            modes = interior_fixed_modes(multiplicity)
            self.assertEqual(modes, EMPTY_ONE if multiplicity == 2 else tuple(Fraction(index, multiplicity - 1) for index in range(1, multiplicity - 1)))

    def test_generation_coordinates_are_order_labels_not_masses(self):
        result = generation_coordinates()
        self.assertTrue(result["all_three"] and result["order_isomorphic"])
        self.assertFalse(result["coordinates_are_mass_values"])
        self.assertEqual(result["half_fibre"], (Fraction(1, 6), Fraction(1, 2), Fraction(5, 6)))

    def test_unique_cover_depths(self):
        self.assertEqual(least_cover_depth(2, 27)["depth"], 5)
        self.assertEqual(least_cover_depth(3, 27)["depth"], 3)
        self.assertTrue(least_cover_depth(2, 27)["minimal"])

    def test_arbitrary_finite_particle_census_placement(self):
        for count in (1, 2, 3, 27, 65):
            result = place_recurrent_particle_modes(tuple(f"trace-{index}" for index in range(1, count + 1)))
            self.assertTrue(result["complete"] and result["injective"] and result["internal_depth_not_spatial_dimension"])
            self.assertGreaterEqual(result["capacity"], count)

    def test_terminal_mass_transport_rejects_old_site_mass_reading(self):
        result = mass_pattern_transport()
        self.assertTrue(result["complete_sector_table"])
        self.assertTrue(result["old_site_fraction_equals_mass_claim_rejected"])
        self.assertTrue(result["site_order_selects_root_order_only"])

    def test_dual_and_reach_identities(self):
        self.assertEqual(colour_binary_dual(5), Fraction(1, 95))
        self.assertEqual(colour_binary_dual(7), Fraction(1, 383))
        for depth in range(1, 10):
            result = mass_ratio_reach(depth)
            self.assertTrue(result["identity"])
            self.assertEqual(result["heavy_to_light"], result["subtraction_reach"])

    def test_transition_is_structural_not_universal_rate(self):
        result = transition_mode_certificate()
        self.assertTrue(result["complete"] and result["terminal_mixing_carriers_required"])
        self.assertFalse(result["separations_are_universal_observed_mixing_rates"])

    def test_theorem_certificate(self):
        self.assertTrue(all(theorem_certificate().values()))

    def test_invalid_forms_halt(self):
        with self.assertRaises(ValueError):
            m_fold_fibre(1, Fraction(1, 2))
        with self.assertRaises(ValueError):
            place_recurrent_particle_modes(("same", "same"))


if __name__ == "__main__":
    unittest.main()
