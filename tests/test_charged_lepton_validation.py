from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.charged_lepton_validation import (
    SOURCE_PATH,
    comparison_record,
    isolate_three_roots,
    koide_source_interval,
    positive_sqrt_interval,
)


ROOT = Path(__file__).resolve().parents[1]


class ChargedLeptonValidationTests(unittest.TestCase):
    def test_cubic_has_three_exact_positive_root_brackets(self) -> None:
        brackets = isolate_three_roots()
        self.assertEqual(len(brackets), 3)
        self.assertTrue(all(Fraction(0, 1) < lower < upper < Fraction(1, 1) for lower, upper in brackets))

    def test_complete_codata_comparison_fails_without_omitting_rows(self) -> None:
        record = comparison_record(ROOT)
        self.assertFalse(record["all_rows_passed"])
        self.assertFalse(record["muon_electron"]["overlap"])
        self.assertFalse(record["muon_tau"]["overlap"])

    def test_external_square_roots_have_exact_outward_enclosures(self) -> None:
        value = Fraction(2, 1)
        lower, upper = positive_sqrt_interval(value)
        self.assertLessEqual(lower * lower, value)
        self.assertGreaterEqual(upper * upper, value)

    def test_exact_koide_value_lies_inside_complete_source_enclosure(self) -> None:
        lower, upper = koide_source_interval(ROOT / SOURCE_PATH)
        self.assertLessEqual(lower, Fraction(2, 3))
        self.assertLessEqual(Fraction(2, 3), upper)


if __name__ == "__main__":
    unittest.main()
