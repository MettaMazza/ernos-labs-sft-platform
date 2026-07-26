import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.cosmic_transport_measured_value_successor_validation_v1 import authoritative_record, exact_cosmic_analysis
from sft.physics.cosmic_transport_measured_value_successor_v1 import SPEC, TARGET_ROWS
from sft.physics.generated_empirical_law import candidate_rows


class CosmicTransportMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_and_target_products(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertEqual(len(TARGET_ROWS), 39)

    def test_complete_measured_value_vector(self):
        result = exact_cosmic_analysis(authoritative_record(Path(__file__).resolve().parents[1]))
        residual = result["residual_certificate"]
        self.assertEqual(residual["row_count"], 32)
        self.assertEqual(residual["refinements"], 3)
        self.assertLess(residual["mean_squared_residual_upper"], Fraction(1, 1))
        ignored = {"residual_certificate", "planck_ratio_interval", "Haridasu_q_interval", "Haridasu_transition_cube_interval", "static_state_magnitude_interval"}
        self.assertTrue(all(value for key, value in result.items() if key not in ignored))

    def test_tampered_chronometer_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["original"]["cosmic_chronometers"]["rows"][0]["central"] = "1000"
        self.assertFalse(exact_cosmic_analysis(target)["chronometer_unit_residual_passed"])

    def test_tampered_transition_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["record"]["corrected_acceleration_target"].update({"transition_redshift_center": "1.50", "transition_redshift_lower_uncertainty": "0.01", "transition_redshift_upper_uncertainty": "0.01"})
        self.assertFalse(exact_cosmic_analysis(target)["onset_inside_Haridasu_transition_interval"])


if __name__ == "__main__":
    unittest.main()
