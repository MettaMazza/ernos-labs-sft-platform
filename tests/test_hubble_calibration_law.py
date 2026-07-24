from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.hubble_calibration_law import (
    HUBBLE_CALIBRATION_SPEC,
    hubble_calibration_structure,
)
from sft.physics.hubble_calibration_validation import SOURCE_PATH, hubble_ratio_interval
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class HubbleCalibrationLawTests(unittest.TestCase):
    def test_formal_structure_reconstructs_full_v2_strength(self) -> None:
        result = hubble_calibration_structure()
        self.assertEqual(result["matter_share"] + result["vacuum_share"], Fraction(1, 1))
        self.assertEqual(result["leading_correction"], Fraction(1, 12))
        self.assertEqual(result["leading_ratio"], Fraction(13, 12))
        self.assertEqual(result["orbit_floor"], 127)
        self.assertEqual(len(result["orbit_trace"]), 7)
        self.assertEqual(result["refined_ratio"], Fraction(3305, 3048))

    def test_complete_candidate_product_has_expected_size(self) -> None:
        self.assertEqual(len(candidate_rows(HUBBLE_CALIBRATION_SPEC)), 2048)

    def test_both_exact_ratios_pass_complete_source_interval(self) -> None:
        lower, upper = hubble_ratio_interval(ROOT / SOURCE_PATH)
        result = hubble_calibration_structure()
        self.assertLessEqual(lower, result["leading_ratio"])
        self.assertLessEqual(result["leading_ratio"], upper)
        self.assertLessEqual(lower, result["refined_ratio"])
        self.assertLessEqual(result["refined_ratio"], upper)

    def test_source_interval_is_exact_and_outward_propagated(self) -> None:
        lower, upper = hubble_ratio_interval(ROOT / SOURCE_PATH)
        self.assertEqual(lower, Fraction(7200, 6790))
        self.assertEqual(upper, Fraction(7408, 6690))


if __name__ == "__main__":
    unittest.main()
