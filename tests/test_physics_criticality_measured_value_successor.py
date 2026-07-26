import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.criticality_measured_value_successor_validation_v1 import authoritative_record, exact_criticality_analysis
from sft.physics.criticality_measured_value_successor_v1 import SPEC, TARGET_ROWS
from sft.physics.generated_empirical_law import candidate_rows


class CriticalityMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_and_target_products(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertEqual(len(TARGET_ROWS), 8)

    def test_complete_measured_value_vector(self):
        result = exact_criticality_analysis(authoritative_record(Path(__file__).resolve().parents[1]))
        self.assertEqual(result["complete_fifteen_value_mean_squared_residual"], Fraction(5286961, 10584000))
        ignored = {"material_rows", "complete_fifteen_value_mean_squared_residual", "erbium_intervals", "turbulence_interval"}
        self.assertTrue(all(value for key, value in result.items() if key not in ignored))

    def test_tampered_vector_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["original"]["registered_target"]["manganite_rows"][1]["gamma_center"] = 200
        self.assertFalse(exact_criticality_analysis(target)["complete_manganite_residual_below_One"])

    def test_incomplete_material_key_rejects(self):
        target = json.loads(json.dumps(authoritative_record(Path(__file__).resolve().parents[1])))
        target["record"]["manganite_complete_structural_key"]["Widom_relation_verified_for_reported_exponents"] = False
        self.assertFalse(exact_criticality_analysis(target)["all_five_material_keys_complete"])


if __name__ == "__main__":
    unittest.main()
