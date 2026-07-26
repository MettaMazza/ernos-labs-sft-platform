import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.thermal_history_measured_value_successor_validation_v1 import authoritative_record, exact_thermal_analysis
from sft.physics.thermal_history_measured_value_successor_v1 import SPEC, TARGET_ROWS


class ThermalHistoryMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_and_target_products(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertEqual(len(TARGET_ROWS), 6)

    def test_complete_measured_value_vector(self):
        result = exact_thermal_analysis(authoritative_record(Path(__file__).resolve().parents[1]))
        self.assertEqual(result["physical_helium_exact"], Fraction(59, 240))
        ignored = {"temperature_exponent_interval", "physical_helium_interval", "deuterium_scaled_interval", "physical_helium_exact"}
        self.assertTrue(all(value for key, value in result.items() if key not in ignored))

    def test_displaced_helium_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["original"]["registered_target"].update({"primordial_helium_mass_fraction_central": "0.2300", "primordial_helium_mass_fraction_standard_uncertainty": "0.0001"})
        self.assertFalse(exact_thermal_analysis(target)["physical_helium_59_over_240_passed"])

    def test_incomplete_peak_census_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["original"]["registered_target"]["planck_detected_peak_count"] = 17
        self.assertFalse(exact_thermal_analysis(target)["complete_peak_census_retained"])


if __name__ == "__main__":
    unittest.main()
