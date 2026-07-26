from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.velocity_composition_fizeau_validation_v1 import authoritative_record, exact_fizeau_analysis


ROOT = Path(__file__).resolve().parents[1]


class VelocityCompositionFizeauTests(unittest.TestCase):
    def test_source_hashes_and_rows(self) -> None:
        record = authoritative_record(ROOT)
        self.assertEqual(record["source_id"], "ARXIV-1201.0501-FIZEAU-WATER-AIR")
        self.assertEqual(len(record["registered_target"]["systematic_limitations_retained"]), 4)

    def test_exact_discriminator(self) -> None:
        analysis = exact_fizeau_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertEqual(analysis["measured_interval"], (Fraction(271, 1000), Fraction(277, 1000)))
        self.assertEqual(analysis["best_relativistic_distance"], Fraction(25, 1000))
        self.assertEqual(analysis["ordinary_distance"], Fraction(289, 1000))
        self.assertTrue(analysis["measurement_inside_complete_relativistic_systematics_bracket"])
        self.assertTrue(analysis["relativistic_more_than_ten_times_closer"])
        self.assertTrue(analysis["ordinary_outside_measurement_interval"])
        self.assertTrue(analysis["air_control_retained"])

    def test_tampered_control_fails(self) -> None:
        target = dict(authoritative_record(ROOT)["registered_target"])
        target["ordinary_addition_prediction_rad_s_per_m"] = target["water_measured_slope_rad_s_per_m"]
        self.assertFalse(exact_fizeau_analysis(target)["relativistic_more_than_ten_times_closer"])


if __name__ == "__main__":
    unittest.main()
