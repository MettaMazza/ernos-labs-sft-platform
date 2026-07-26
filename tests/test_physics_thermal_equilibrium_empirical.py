import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.thermal_equilibrium_empirical_v1 import SOURCE_IDS, SPEC
from sft.physics.thermal_equilibrium_validation_v1 import authoritative_record, exact_thermal_analysis


class ThermalEquilibriumEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_exact_external_intervals_and_relations(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_thermal_analysis(record["registered_target"])
        self.assertEqual(result["acoustic_interval"], (13806456, 13806512))
        self.assertEqual(result["electronic_interval"], (13806340, 13806680))
        self.assertTrue(all(value for key, value in result.items() if key not in {"acoustic_interval", "electronic_interval"}))

    def test_unfavorable_interval_rejects(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["electronic_kb_scaled_center"] = 13000000
        self.assertFalse(exact_thermal_analysis(target)["electronic_contains_exact"])

    def test_invalid_negative_uncertainty_cannot_pass(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["acoustic_kb_scaled_standard_uncertainty"] = -1
        self.assertFalse(exact_thermal_analysis(target)["positive_exact_carriers"])


if __name__ == "__main__":
    unittest.main()
