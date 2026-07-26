import unittest
from fractions import Fraction

from sft.physics.stellar_galactic_tidal_terminal_law_v1 import (
    SPEC,
    baryonic_tully_fisher_exponent,
    baryonic_tully_fisher_ratio,
    hydrostatic_balance,
    radial_response_exponents,
    radial_restoration,
    stellar_lifetime_fall_exponents,
    stellar_luminosity_exponents,
    theorem_certificate,
    tidal_terminal,
    visible_asymptote_comparison,
)
from sft.physics.structural_constants import candidate_rows


class StellarGalacticTidalTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)

    def test_hydrostatic_and_radial_restoration(self):
        self.assertEqual(hydrostatic_balance()["outward_share"], Fraction(1, 2))
        self.assertTrue(hydrostatic_balance()["balanced"])
        self.assertEqual(radial_response_exponents(), {"pressure": Fraction(5, 3), "gravity": Fraction(4, 3)})
        for q in (Fraction(3, 2), Fraction(2), Fraction(5, 2)):
            row = radial_restoration(q)
            self.assertTrue(row["compression_pushes_out"])
            self.assertTrue(row["expansion_pulls_in"])
            self.assertFalse(row["irrational_root_evaluated"])

    def test_stellar_and_galaxy_scaling(self):
        self.assertEqual(stellar_luminosity_exponents(), (3, 4))
        self.assertEqual(stellar_lifetime_fall_exponents(), (2, 3))
        self.assertTrue(visible_asymptote_comparison(Fraction(2))["flat_requires_additional_enclosed_support"])
        self.assertEqual(baryonic_tully_fisher_exponent(), 4)
        self.assertEqual(baryonic_tully_fisher_ratio(Fraction(2)), 16)

    def test_finite_tidal_terminal_and_boundary(self):
        for pair in ((2, 1), (3, 1), (3, 2), (5, 3)):
            row = tidal_terminal(*pair)
            self.assertTrue(row["finite"])
            self.assertTrue(row["strictly_dissipative_before_lock"])
            self.assertTrue(row["terminal_one_to_one"])
            self.assertEqual(row["external_forcing_or_eccentric_resonance_boundary"], "separate-generated-boundary")
        self.assertTrue(theorem_certificate()["all_tidal_rows_lock"])


if __name__ == "__main__":
    unittest.main()
