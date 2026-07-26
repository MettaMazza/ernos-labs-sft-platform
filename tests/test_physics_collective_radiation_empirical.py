from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.collective_radiation_empirical_v1 import SPEC
from sft.physics.collective_radiation_validation_v1 import authoritative_record, exact_collective_analysis
from sft.physics.generated_empirical_law import candidate_rows

ROOT = Path(__file__).resolve().parents[1]

class CollectiveRadiationEmpiricalTests(unittest.TestCase):
    def test_sources_and_values(self):
        record = authoritative_record(ROOT); self.assertEqual(len(record["sources"]), 5); self.assertFalse(record["historical_blindness_claimed"])
        a = exact_collective_analysis(record["registered_target"])
        self.assertTrue(a["blackbody_exponent_matches"]); self.assertEqual(a["blackbody_double_ratio"], 16)
        self.assertTrue(a["blackbody_coefficient_agreement"] and a["blackbody_shape_agreement"] and a["acoustic_precision_retained"])
        self.assertEqual(a["laser_narrowing_factor_floor"], 20); self.assertTrue(a["laser_feedback_narrows"])
        self.assertTrue(a["plasma_direct_relation"] and a["alfven_record_complete"]); self.assertEqual(a["alfven_year_count"], 8)
    def test_tamper_fails(self):
        target = dict(authoritative_record(ROOT)["registered_target"]); target["blackbody_exponent"] = 3
        self.assertFalse(exact_collective_analysis(target)["blackbody_exponent_matches"])
    def test_candidate_product(self):
        rows = candidate_rows(SPEC); self.assertEqual(len(rows), 256); self.assertEqual(len({x["candidate_id"] for x in rows}), 256); SPEC.validate()

if __name__ == "__main__": unittest.main()
