import unittest
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.hadron_regge_measured_value_successor_v1 import SPEC
from sft.physics.hadron_regge_measured_value_successor_validation_v1 import authoritative_record, exact_regge_analysis


ROOT = Path(__file__).resolve().parents[1]


class HadronReggeMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_all_five_exact_carriers_inside_support(self):
        result = exact_regge_analysis(authoritative_record(ROOT))
        self.assertTrue(result["complete_five_rows"])
        self.assertTrue(result["exact_carrier_vector"])
        self.assertTrue(result["all_five_inside_measured_support"])
        self.assertTrue(all(row["inside_measured_resonance_support"] for row in result["row_results"]))

    def test_listing_and_method_custody(self):
        result = exact_regge_analysis(authoritative_record(ROOT))
        self.assertTrue(result["rho5_omission_retained"])
        self.assertTrue(result["no_fit_declared"])
        self.assertTrue(result["no_widening_declared"])


if __name__ == "__main__":
    unittest.main()
