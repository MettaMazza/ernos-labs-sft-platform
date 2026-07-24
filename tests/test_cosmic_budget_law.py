from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.cosmic_budget_law import COSMIC_BUDGET_SPEC, cosmic_budget_structure
from sft.physics.cosmic_budget_validation import SOURCE_PATH, planck_budget_intervals
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class CosmicBudgetLawTests(unittest.TestCase):
    def test_refined_budget_is_exact_and_closed(self) -> None:
        result = cosmic_budget_structure()
        self.assertEqual(result["vacuum"], Fraction(11, 16))
        self.assertEqual(result["matter"], Fraction(5, 16))
        self.assertEqual(result["baryon"], Fraction(25, 512))
        self.assertEqual(result["cold_dark"], Fraction(135, 512))
        self.assertEqual(result["vacuum"] + result["matter"], Fraction(1, 1))
        self.assertEqual(result["baryon"] + result["cold_dark"], result["matter"])

    def test_complete_candidate_product(self) -> None:
        self.assertEqual(len(candidate_rows(COSMIC_BUDGET_SPEC)), 2048)

    def test_all_refined_values_pass_all_complete_intervals(self) -> None:
        intervals = planck_budget_intervals(ROOT / SOURCE_PATH)
        result = cosmic_budget_structure()
        for key, (lower, upper) in intervals.items():
            with self.subTest(key=key):
                self.assertLessEqual(lower, result[key])
                self.assertLessEqual(result[key], upper)

    def test_every_leading_value_fails_its_complete_interval(self) -> None:
        intervals = planck_budget_intervals(ROOT / SOURCE_PATH)
        leading = {"vacuum": Fraction(2, 3), "matter": Fraction(1, 3), "baryon": Fraction(5, 96), "cold_dark": Fraction(9, 32)}
        for key, value in leading.items():
            with self.subTest(key=key):
                self.assertFalse(intervals[key][0] <= value <= intervals[key][1])


if __name__ == "__main__":
    unittest.main()
