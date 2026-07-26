import unittest
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.spin_statistics_condensation_empirical_v1 import SOURCE_IDS, SPEC
from sft.physics.spin_statistics_condensation_validation_v1 import authoritative_record, exact_spin_statistics_analysis


class SpinStatisticsCondensationEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_vector(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_spin_statistics_analysis(record["registered_target"])
        self.assertEqual(result["bec_interval"], (89, 99))
        self.assertEqual(result["spinor_interval"], (666, 742))
        self.assertTrue(all(value for key, value in result.items() if key not in {"bec_interval", "spinor_interval"}))

    def test_unfavorable_spinor_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["spinor_measured_return_degrees_center"] = 600
        self.assertFalse(exact_spin_statistics_analysis(target)["spinor_interval_contains_forced_return"])

    def test_reversed_cooling_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["bec_ground_share_increases_as_temperature_is_lowered"] = False
        self.assertFalse(exact_spin_statistics_analysis(target)["bec_cooling_direction"])

    def test_invalid_uncertainty_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["spinor_measured_return_degrees_uncertainty"] = -1
        self.assertFalse(exact_spin_statistics_analysis(target)["positive_exact_carriers"])


if __name__ == "__main__":
    unittest.main()
