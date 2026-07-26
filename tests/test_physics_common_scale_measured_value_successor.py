import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.common_scale_measured_value_successor_validation_v1 import authoritative_record, exact_common_scale_analysis
from sft.physics.common_scale_measured_value_successor_v1 import SOURCE_IDS, SPEC
from sft.physics.generated_empirical_law import candidate_rows


class CommonScaleMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_measured_value_vector(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_common_scale_analysis(record["registered_target"])
        self.assertEqual(result["scheme_intervals"]["on-shell"], (Fraction(22333, 100000), Fraction(22351, 100000)))
        self.assertEqual(result["low_transfer_intervals"]["Cesium-atomic-parity-violation"], (Fraction(2331, 10000), Fraction(2367, 10000)))
        self.assertTrue(all(value for key, value in result.items() if key not in {"scheme_intervals", "low_transfer_intervals"}))

    def test_displaced_terminal_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = json.loads(json.dumps(authoritative_record(root)["registered_target"]))
        target["scheme_rows"][0]["center"] = "0.22000"
        self.assertFalse(exact_common_scale_analysis(target)["terminal_inside_on_shell_interval"])

    def test_displaced_APV_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = json.loads(json.dumps(authoritative_record(root)["registered_target"]))
        target["low_transfer_rows"][3]["center"] = "0.2300"
        target["low_transfer_rows"][3]["standard_uncertainty"] = "0.0001"
        self.assertFalse(exact_common_scale_analysis(target)["support_eight_inside_APV_interval"])


if __name__ == "__main__":
    unittest.main()
