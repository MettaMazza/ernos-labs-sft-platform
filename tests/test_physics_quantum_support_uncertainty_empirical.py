import unittest
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.quantum_support_uncertainty_empirical_v1 import SOURCE_IDS, SPEC
from sft.physics.quantum_support_uncertainty_validation_v1 import authoritative_record, exact_quantum_support_bell_analysis


class QuantumSupportUncertaintyEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_record(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_quantum_support_bell_analysis(record["registered_target"])
        self.assertEqual(result["bell_interval"], (20714, 20780))
        self.assertTrue(all(value for key, value in result.items() if key != "bell_interval"))

    def test_interval_touching_local_bound_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["bell_parameter_center"] = 20033
        self.assertFalse(exact_quantum_support_bell_analysis(target)["complete_interval_above_local_bound"])

    def test_failed_space_like_timing_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["trial_duration_nanoseconds_center_hundredths"] = 11100
        self.assertFalse(exact_quantum_support_bell_analysis(target)["space_like_interval_separation"])

    def test_missing_assumption_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["measurement_independence_is_a_declared_experimental_assumption"] = False
        self.assertFalse(exact_quantum_support_bell_analysis(target)["measurement_independence_assumption_retained"])


if __name__ == "__main__":
    unittest.main()
