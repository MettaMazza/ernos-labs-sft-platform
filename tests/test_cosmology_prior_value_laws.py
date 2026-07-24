from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.cosmology_prior_value_laws import DARK_BARYON_SPEC, dark_baryon_structure
from sft.physics.cosmology_prior_value_validation import SOURCE_PATH, density_ratio_interval
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class CosmologyPriorValueLawTests(unittest.TestCase):
    def test_dark_baryon_structure_is_exact_and_complete(self) -> None:
        result = dark_baryon_structure()
        self.assertEqual(result["baryon_share"] + result["dark_share"], Fraction(1, 1))
        self.assertEqual(result["leading_ratio"], Fraction(27, 5))
        self.assertEqual(result["refined_ratio"], Fraction(279, 52))
        self.assertEqual(len(result["orbit_trace"]), 5)

    def test_complete_candidate_product_has_expected_size(self) -> None:
        self.assertEqual(len(candidate_rows(DARK_BARYON_SPEC)), 1024)

    def test_both_exact_ratios_pass_complete_planck_interval(self) -> None:
        lower, upper = density_ratio_interval(ROOT / SOURCE_PATH)
        result = dark_baryon_structure()
        self.assertLessEqual(lower, result["leading_ratio"])
        self.assertLessEqual(result["leading_ratio"], upper)
        self.assertLessEqual(lower, result["refined_ratio"])
        self.assertLessEqual(result["refined_ratio"], upper)


if __name__ == "__main__":
    unittest.main()
