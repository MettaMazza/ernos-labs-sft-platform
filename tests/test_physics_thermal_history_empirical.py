from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.thermal_history_empirical_v1 import SPEC
from sft.physics.thermal_history_validation_v1 import authoritative_record, exact_thermal_analysis


ROOT = Path(__file__).resolve().parents[1]


class ThermalHistoryEmpiricalTests(unittest.TestCase):
    def test_complete_source_record(self) -> None:
        record = authoritative_record(ROOT)
        self.assertEqual(len(record["sources"]), 6)
        self.assertEqual(len(record["registered_target"]["planck_tt_peak_multipoles"]), 7)
        self.assertFalse(record["historical_blindness_claimed"])

    def test_temperature_and_freezeout_comparison(self) -> None:
        analysis = exact_thermal_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertEqual(analysis["temperature_exponent_interval"], (Fraction(49, 50), Fraction(517, 500)))
        self.assertTrue(analysis["exact_one_inside_temperature_interval"])
        self.assertTrue(analysis["freezeout_sequence_retained"])

    def test_unfavourable_helium_result_is_not_hidden(self) -> None:
        analysis = exact_thermal_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertEqual(analysis["helium_interval"], (Fraction(489, 2000), Fraction(2471, 10000)))
        self.assertTrue(analysis["exact_quarter_excluded"])
        self.assertEqual(analysis["helium_gap_from_analytic_quarter"], Fraction(21, 5000))
        self.assertTrue(analysis["deuterium_positive_minor_channel"])

    def test_recombination_and_acoustic_controls(self) -> None:
        analysis = exact_thermal_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertTrue(analysis["finite_positive_recombination_support"])
        self.assertTrue(analysis["complete_seven_tt_peaks"])
        self.assertTrue(analysis["finite_eighteen_peak_record"])
        self.assertTrue(analysis["angular_integer_multiple_claim_rejected"])

    def test_tampered_temperature_exponent_fails(self) -> None:
        target = dict(authoritative_record(ROOT)["registered_target"])
        target["cmb_temperature_exponent_central"] = "1.100"
        self.assertFalse(exact_thermal_analysis(target)["exact_one_inside_temperature_interval"])

    def test_complete_empirical_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
