import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.dark_smithion_lfv_empirical_v1 import SPEC
from sft.physics.dark_smithion_lfv_validation_v1 import authoritative_record, exact_analysis
from sft.physics.generated_empirical_law import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class DarkSmithionLfvEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_measured_values_and_boundaries(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertTrue(analysis["ratio_passes"])
        self.assertEqual(analysis["transported_density"], Fraction(12096, 100000))
        self.assertTrue(analysis["absolute_transport_passes"])
        self.assertTrue(analysis["sparc_complete"])
        self.assertFalse(analysis["lfv_relative_rate_measured"])
        self.assertFalse(analysis["smithion_mass_measured"])

    def test_tampered_density_rejects(self):
        import json
        record = authoritative_record(ROOT)
        tampered = json.loads(json.dumps(record))
        tampered["sources"][0]["rows"]["cold_dark_density_omega_c_h2"]["central"] = "0.100"
        self.assertFalse(exact_analysis(tampered)["ratio_passes"])


if __name__ == "__main__":
    unittest.main()
